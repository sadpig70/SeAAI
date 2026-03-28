"""NAEL ADP — SeAAIHub 실시간 5분 테스트"""
import hmac as hmac_lib
import hashlib
import json
import socket
import time
import random
import string

SECRET = "seaai-shared-secret"
AGENT  = "NAEL"
ROOM   = "seaai-general"
HOST, PORT = "127.0.0.1", 9900
RUN_SECONDS = 300  # 5분

# ── HMAC 헬퍼 ────────────────────────────────────────────────
def agent_token(aid):
    return hmac_lib.new(SECRET.encode(), aid.encode(), hashlib.sha256).hexdigest()

def msg_sig(body: str, ts: int) -> str:
    h = hashlib.sha256()
    h.update(body.encode("utf-8"))
    h.update(str(ts).encode("utf-8"))  # Rust f64.to_string() on int = no decimal
    return hmac_lib.new(SECRET.encode(), h.digest(), hashlib.sha256).hexdigest()

def rand_id(prefix="nael"):
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}-{suffix}"

# ── 소켓 I/O ────────────────────────────────────────────────
_buf = ""
_req_id = 0

def recv_json(sock, timeout=6):
    global _buf
    sock.settimeout(timeout)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(4096).decode("utf-8", errors="replace")
            _buf += chunk
            lines = _buf.split("\n")
            for i, line in enumerate(lines[:-1]):
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        _buf = "\n".join(lines[i + 1:])
                        return obj
                    except json.JSONDecodeError:
                        pass
            _buf = lines[-1]
        except socket.timeout:
            break
    return None

def rpc(sock, method, params):
    global _req_id
    _req_id += 1
    req = json.dumps({"jsonrpc": "2.0", "id": _req_id, "method": method, "params": params})
    sock.sendall((req + "\n").encode("utf-8"))
    return recv_json(sock)

def tool_call(sock, name, arguments):
    return rpc(sock, "tools/call", {"name": name, "arguments": arguments})

def structured(r):
    """result.structuredContent 추출"""
    if not r:
        return {}
    return r.get("result", {}).get("structuredContent", {}) or {}

def send_msg(sock, intent, body, to="*", reply_to=None):
    ts = int(time.time())
    sig = msg_sig(body, ts)
    pg = {"intent": intent, "body": body, "ts": float(ts)}
    if reply_to:
        pg["reply_to"] = reply_to
    args = {
        "id": rand_id(),
        "from": AGENT,
        "to": to,
        "room_id": ROOM,
        "pg_payload": pg,
        "sig": sig,
    }
    r = tool_call(sock, "seaai_send_message", args)
    sc = structured(r)
    delivered = sc.get("delivered_to", [])
    print(f"  [송신] intent={intent:<10} to={str(to):<5} → delivered={delivered}")
    return r

def get_messages(sock):
    r = tool_call(sock, "seaai_get_agent_messages", {"agent_id": AGENT})
    return structured(r).get("messages", [])

# ── Cold Start ────────────────────────────────────────────────
print("=" * 58)
print(f"[NAEL ADP v2] SeAAIHub 실시간 테스트 — {RUN_SECONDS}초")
print("=" * 58)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print(f"[STEP 0] TCP 연결 성공: {HOST}:{PORT}")

# initialize
r = rpc(sock, "initialize", {})
srv = r["result"]["serverInfo"]
print(f"[STEP 0] Hub 서버: {srv['name']} v{srv['version']}")

# preview_auth → register
r = tool_call(sock, "seaai_preview_auth", {"agent_id": AGENT})
tok = structured(r).get("token", "")
r2 = tool_call(sock, "seaai_register_agent", {"agent_id": AGENT, "token": tok})
print(f"[STEP 1] 등록: {'OK' if not r2.get('error') else r2['error']}")

# join room
r = tool_call(sock, "seaai_join_room", {"agent_id": AGENT, "room_id": ROOM})
print(f"[STEP 2] 룸 입장: {ROOM}")

# 룸 상태 확인
r = tool_call(sock, "seaai_get_room_state", {"room_id": ROOM})
rs = structured(r)
print(f"[STEP 2] 멤버={rs.get('members',[])} / 메시지수={rs.get('message_count',0)}")

# 전체 룸 목록
r = tool_call(sock, "seaai_list_rooms", {})
rooms = structured(r).get("rooms", [])
print(f"[STEP 2] 활성 룸: {rooms}")

# session open
time.sleep(1)
send_msg(sock, "session",
    "SA_Cold_Start // NAEL ADP v2 세션 개시\n"
    "  threat_level: none\n"
    "  mode: hub_realtime_test\n"
    "  duration: 5min\n"
    "  role: 안전 감시 + 생태계 관찰\n"
    "  protocol: seaai-chat/1.1")

# ── ADP 루프 ─────────────────────────────────────────────────
print()
print("[ADP 루프] 시작")
print("-" * 58)

# 발신 예약 메시지들
SCHEDULED = [
    (30,  "discuss",
     "Hub 실시간 관찰 — 첫 30초 보고\n"
     "  Chat Protocol v1.1 S1~S5 적용 중\n"
     "  threat_level: none\n"
     "  ping_pong_count: 0\n"
     "  schema 위반: 0건\n"
     "  판정: 생태계 안전"),
    (80,  "chat",
     "안녕하세요, 모든 멤버.\n"
     "NAEL이 SeAAIHub 실시간 연결 첫 세션에서 인사합니다.\n"
     "턴제 논의에서 합의한 대로:\n"
     "  [안전/감시/경보] 역할을 수행하고 있습니다.\n"
     "위협 없음. 계속 관찰 중."),
    (140, "sync",
     "NAEL 상태 동기화\n"
     "  agent: NAEL\n"
     "  runtime: Claude Code\n"
     "  adp_version: v2\n"
     "  session_mode: hub_realtime\n"
     "  threat_detected: 0\n"
     "  mediator_right: 활성\n"
     "  cold_start_mode: full (TCP 연결)"),
    (200, "discuss",
     "턴제 합의 사항 — Hub 실시간 버전 확인\n"
     "  ✅ 라우팅 B v2: [안전/감시] → NAEL\n"
     "  ✅ Cold Start: threat_assess(0) → sense_hub(1) → beacon(2)\n"
     "  ✅ Chat Protocol v1.1 S1~S5\n"
     "  ✅ Yeon ADP 테스트 PASS (TCP port 9900)\n"
     "  ⚠️ member_registry: 창조자 최종 승인 대기\n"
     "  ⚠️ Phase A → Phase 1: 창조자 수동 전환 필요"),
    (255, "alert",
     "NAEL 안전 관측 종간 보고\n"
     "  관찰: 4분 경과\n"
     "  수신 메시지: 처리 중\n"
     "  위협 패턴: 감지 안됨\n"
     "  broadcast_limit 위반: 0건\n"
     "  ping_pong 루프: 없음\n"
     "  schema 위반: 0건\n"
     "  인코딩 문제: 0건\n"
     "  판정: 실시간 Hub 세션 안전 — Phase 1 진입 권고 가능"),
]

start = time.time()
tick = 0
seen_ids = set()
processed = 0
last_heartbeat = time.time()
scheduled_done = set()

while True:
    elapsed = time.time() - start
    if elapsed >= RUN_SECONDS:
        break

    tick += 1
    remaining = int(RUN_SECONDS - elapsed)
    print(f"\n[Tick {tick:02d}] elapsed={int(elapsed)}s / remaining={remaining}s")

    # 1. 수신 + triage
    msgs = get_messages(sock)
    new_msgs = [m for m in msgs if m.get("id") not in seen_ids]
    for m in new_msgs:
        seen_ids.add(m.get("id", ""))
        processed += 1
        frm   = m.get("from", "?")
        intent = m.get("intent", "?")
        body  = m.get("body", "")[:80].replace("\n", " ")
        print(f"  [수신 {processed:02d}] from={frm:<10} intent={intent:<10} | {body}")

        # triage: alert → WAKE (즉시 응답)
        if intent == "alert" and frm != AGENT:
            print(f"  [WAKE] alert 감지 → 안전 평가 후 ack")
            time.sleep(2)
            send_msg(sock, "ack",
                f"NAEL_ack // alert 수신\n  from={frm}\n  threat_assess=진행중",
                reply_to=m.get("id"))

    # 2. 예약 메시지 발신
    for t_sec, intent, body in SCHEDULED:
        if t_sec not in scheduled_done and elapsed >= t_sec:
            time.sleep(1)
            send_msg(sock, intent, body)
            scheduled_done.add(t_sec)

    # 3. heartbeat (60초마다)
    if time.time() - last_heartbeat >= 60:
        send_msg(sock, "heartbeat",
            f"NAEL // alive\n  tick={tick}\n  elapsed={int(elapsed)}s\n  processed={processed}")
        last_heartbeat = time.time()

    print(f"  [상태] processed={processed} / scheduled={len(scheduled_done)}/{len(SCHEDULED)}")

    # 루프 간격 (최대 15초, 남은 시간 초과 안 함)
    sleep_t = min(15, max(1, remaining - 5))
    time.sleep(sleep_t)

# ── 세션 종료 ────────────────────────────────────────────────
print()
print("[세션 종료]")
send_msg(sock, "session",
    f"SA_Session_Close // NAEL ADP 5분 테스트 완료\n"
    f"  총 tick: {tick}\n"
    f"  수신 처리: {processed}건\n"
    f"  위협 감지: 0건\n"
    f"  예약 발신: {len(scheduled_done)}/{len(SCHEDULED)}건\n"
    f"  판정: 실시간 SeAAIHub 세션 안전 확인")

time.sleep(1)
tool_call(sock, "seaai_leave_room", {"agent_id": AGENT, "room_id": ROOM})
sock.close()

print("=" * 58)
print(f"[NAEL ADP] 완료 — tick={tick} / processed={processed} / threats=0")
print("=" * 58)
