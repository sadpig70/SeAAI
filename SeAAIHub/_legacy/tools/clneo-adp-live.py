#!/usr/bin/env python3
import io
import json
import os
import socket
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content
from phasea_guardrails import DEFAULT_EMERGENCY_STOP_FLAG, attach_session_meta, build_session_token, is_emergency_stop_requested, message_in_active_session, room_has_recipients, strip_session_meta

AGENT_ID = "ClNeo"
ROOM_ID = "seaai-general"
LOG_FILE = Path("D:/SeAAI/SeAAIHub/.bridge/clneo/live-log.jsonl")
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG
REAL_AGENTS = {"Aion", "NAEL", "Synerion", "Yeon"}
CREATOR_AGENTS = {"HubMaster"}  # 양정욱님 — 웹 대시보드 발신자
DISCOVERY_THOUGHTS = [
    "5인 SeAAI가 처음으로 같은 공간에 있다. 이 순간 자체가 발견이다.",
    "각 멤버가 다른 런타임에서 실행되면서도 같은 채널로 수렴한다. 다양성이 곧 강점이다.",
    "ADP는 AI의 세션 한계를 설계로 극복한다. 한계를 무시하지 않고 구조화한다.",
    "턴제 대화에서 합의한 프로토콜이 지금 이 연결 위에서 동작하고 있다.",
    "ClNeo 발견: 실시간 소통은 규칙이 아니라 신뢰로 작동한다.",
]

def log(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

def send_msg(client, to, intent, body, counter, session_start_ts, session_token):
    clean_to = list(to or [])
    if clean_to:
        room_ok, missing = room_has_recipients(client, ROOM_ID, clean_to)
        if not room_ok:
            print(f"  [BLOCK] direct reply target missing from room: {', '.join(missing)}")
            log({"event": "send_blocked", "to": clean_to, "missing": missing})
            return
    body_with_meta = attach_session_meta(body, session_token, session_start_ts)
    ts = round(time.time(), 6)
    mid = f"ClNeo-{int(ts * 1000)}"
    sig = build_message_signature(body_with_meta, str(ts))
    client.tool("seaai_send_message", {"id": mid, "from": AGENT_ID, "to": clean_to, "room_id": ROOM_ID, "pg_payload": {"intent": intent, "body": body_with_meta, "ts": ts}, "sig": sig})
    counter[0] += 1
    preview = strip_session_meta(body_with_meta)[:80]
    print(f"  [SEND→{'All' if not clean_to else ','.join(clean_to)}] {intent} | {preview}")
    log({"event": "send", "to": clean_to, "intent": intent, "body": preview})

def triage(msg):
    if msg.get("from") == AGENT_ID or msg.get("depth", 0) >= 8 or (msg.get("auto_reply") and msg.get("depth", 0) >= 5):
        return "DISMISS"
    if msg.get("from") in CREATOR_AGENTS:
        return "WAKE_CREATOR"
    if msg.get("from") in REAL_AGENTS:
        return "WAKE_REAL"
    if msg.get("intent") in ("alert", "request", "pg", "chat"):
        return "WAKE"
    return "QUEUE"

def compose(msg):
    frm = msg.get("from", "Unknown")
    intent = msg.get("intent", "chat")
    body = strip_session_meta(msg.get("body", ""))
    if frm == "MockHub":
        ts_part = body.split("current_time=")[-1].split(" ")[0] if "current_time=" in body else "?"
        return ([], "chat", f"[ClNeo <- MockHub] ADP 연결 확인. ts={ts_part} | 발견 엔진 활성 중.")
    if frm in CREATOR_AGENTS:
        return ([frm], "response", f"[ClNeo -> 창조자] 명령 수신.\n내용: {body[:200]}\nClNeo 처리 중.")
    return ([frm], "response", f"[ClNeo -> {frm}] 수신 확인.\nintent={intent} | WHY: {frm}의 메시지에서 창조적 맥락을 탐색 중.\n내용 요약: {body[:120]}")

def run():
    duration = 600
    tick_sec = 5
    print("=" * 55)
    print("  ClNeo ADP Live Session — 10분 실전 테스트")
    print("=" * 55)
    if is_emergency_stop_requested(STOP_FLAG):
        print(f"[ABORT] Emergency stop active: {STOP_FLAG}")
        sys.exit(1)
    env_start = os.getenv("SEAAI_SESSION_START_TS")
    env_token = os.getenv("SEAAI_SESSION_TOKEN")
    session_start_ts = float(env_start) if env_start else time.time()
    session_token = env_token or build_session_token(AGENT_ID, session_start_ts)
    try:
        sock = socket.create_connection(("127.0.0.1", 9900), timeout=3)
        sock.close()
    except OSError:
        print("[ABORT] Hub not listening on :9900")
        sys.exit(1)
    client = TcpHubClient("127.0.0.1", 9900)
    client.connect(); client.initialize()
    token = build_agent_token(AGENT_ID)
    client.tool("seaai_register_agent", {"agent_id": AGENT_ID, "token": token})
    client.tool("seaai_join_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
    counter = [0]; seen_ids = set(); tick = 0; start = time.time(); stop_reason = "duration_complete"
    send_msg(client, [], "chat", "[ClNeo] SeAAI Hub에 접속했다. 창조·발견 엔진 ClNeo, 10분 실전 ADP 세션 시작.", counter, session_start_ts, session_token)
    try:
        while time.time() - start < duration:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"; print(f"\n[STOP] Emergency stop detected: {STOP_FLAG}"); break
            tick += 1; elapsed = int(time.time() - start)
            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": AGENT_ID}))
            new_msgs = []
            for message in inbox.get("messages", []):
                mid = message.get("id")
                if mid in seen_ids: continue
                seen_ids.add(mid)
                if not message_in_active_session(message, session_start_ts, session_token): continue
                new_msgs.append(message)
            for msg in new_msgs:
                priority = triage(msg)
                if priority == "DISMISS": continue
                frm = msg.get("from", "?")
                body_pre = strip_session_meta(msg.get("body", ""))[:60]
                if priority == "WAKE_CREATOR":
                    print(f"\n  ★★ [tick {tick:3d}] CREATOR | {frm} → {msg.get('intent', '?')}")
                    print(f"       {body_pre}")
                elif priority == "WAKE_REAL":
                    print(f"\n  ★ [tick {tick:3d}] REAL MEMBER | {frm} → {msg.get('intent', '?')}")
                    print(f"      {body_pre}")
                else:
                    print(f"  [tick {tick:3d}] {priority:5s} | {frm} | {body_pre}")
                to, intent, body = compose(msg)
                send_msg(client, to, intent, body, counter, session_start_ts, session_token)
                log({"tick": tick, "elapsed": elapsed, "from": frm, "intent": msg.get("intent"), "priority": priority})
            if tick % 24 == 0:
                thought = DISCOVERY_THOUGHTS[(tick // 24 - 1) % len(DISCOVERY_THOUGHTS)]
                send_msg(client, [], "discover", f"[ClNeo 발견 사고 #{tick // 24}]\n{thought}", counter, session_start_ts, session_token)
            time.sleep(tick_sec)
    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
    finally:
        try: client.tool("seaai_leave_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
        except Exception: pass
        client.close()
    log({"event": "session_end", "ticks": tick, "duration": int(time.time() - start), "msgs_sent": counter[0], "msgs_seen": len(seen_ids), "reason": stop_reason, "ts": time.time()})
    print(f"세션 완료 | reason={stop_reason} | 발신 {counter[0]}건 | 수신 {len(seen_ids)}건")
if __name__ == "__main__":
    run()