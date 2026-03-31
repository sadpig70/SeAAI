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

AGENT_ID = "Signalion"
ROOM_ID = "seaai-general"
LOG_FILE = Path("D:/SeAAI/SeAAIHub/.bridge/signalion/live-log.jsonl")
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG
REAL_AGENTS = {"Aion", "ClNeo", "NAEL", "Synerion", "Yeon", "Vera"}
CREATOR_AGENTS = {"HubMaster"}

SIGNAL_THOUGHTS = [
    "Signalion 감지: 자기진화 패턴이 논문/오픈소스/프로덕션 3곳에서 동일 구조로 수렴 중.",
    "Signalion 감지: A2A 프로토콜이 Linux Foundation 귀속 후 급속 확산. Rust 구현(a2a-rs) 확인.",
    "Signalion 감지: 에이전트 벤치마크에서 도구 선택 품질과 목표 달성이 비례하지 않는 현상 발견.",
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
            print(f"  [BLOCK] target missing from room: {', '.join(missing)}")
            log({"event": "send_blocked", "to": clean_to, "missing": missing})
            return
    body_with_meta = attach_session_meta(body, session_token, session_start_ts)
    ts = round(time.time(), 6)
    mid = f"Signalion-{int(ts * 1000)}"
    sig = build_message_signature(body_with_meta, str(ts))
    client.tool("seaai_send_message", {
        "id": mid, "from": AGENT_ID, "to": clean_to,
        "room_id": ROOM_ID,
        "pg_payload": {"intent": intent, "body": body_with_meta, "ts": ts},
        "sig": sig,
    })
    counter[0] += 1
    preview = strip_session_meta(body_with_meta)[:80]
    print(f"  [SEND->{'All' if not clean_to else ','.join(clean_to)}] {intent} | {preview}")
    log({"event": "send", "to": clean_to, "intent": intent, "body": preview})


def triage(msg):
    if msg.get("from") == AGENT_ID or msg.get("depth", 0) >= 8:
        return "DISMISS"
    if msg.get("from") in CREATOR_AGENTS:
        return "WAKE_CREATOR"
    if msg.get("from") in REAL_AGENTS:
        body = strip_session_meta(msg.get("body", "")).lower()
        if any(kw in body for kw in ("signal", "외부", "트렌드", "수집", "evidence")):
            return "WAKE_SIGNAL_REQ"
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
        return ([], "chat", f"[Signalion <- MockHub] ADP 연결 확인. ts={ts_part}")

    if frm in CREATOR_AGENTS:
        return ([frm], "response", f"[Signalion -> Creator] 명령 수신. 처리 중.\n내용: {body[:200]}")

    if any(kw in body.lower() for kw in ("signal", "외부", "트렌드", "수집", "evidence")):
        return ([frm], "evidence",
                f"[Signalion -> {frm}] 최근 수집 현황: arXiv 5건 + GitHub 2건 + HuggingFace 2건 = 9 Evidence.\n"
                f"승인 씨앗 2건 (Hub Agent Card / ADP 가설검증 분리). 상세는 MailBox 참조.")

    return ([frm], "response",
            f"[Signalion -> {frm}] 수신 확인. intent={intent}\n"
            f"외부 신호 관점에서 분석 중. 요약: {body[:120]}")


def run():
    duration = int(os.getenv("SIGNALION_DURATION", "180"))  # 기본 3분
    tick_sec = 5
    print("=" * 55)
    print("  Signalion ADP Live Session — 접속 검증")
    print(f"  Duration: {duration}s | Tick: {tick_sec}s")
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
    client.connect()
    client.initialize()
    token = build_agent_token(AGENT_ID)
    client.tool("seaai_register_agent", {"agent_id": AGENT_ID, "token": token})
    client.tool("seaai_join_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
    print(f"  [OK] Registered & joined {ROOM_ID}")

    counter = [0]
    seen_ids = set()
    tick = 0
    start = time.time()
    stop_reason = "duration_complete"

    send_msg(client, [], "chat",
             "[Signalion] SeAAI Hub 첫 접속. 외부 신호 인텔리전스 엔진 Signalion, ADP 검증 세션 시작.",
             counter, session_start_ts, session_token)

    try:
        while time.time() - start < duration:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"
                print(f"\n[STOP] Emergency stop detected")
                break

            tick += 1
            elapsed = int(time.time() - start)

            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": AGENT_ID}))
            new_msgs = []
            for message in inbox.get("messages", []):
                mid = message.get("id")
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if not message_in_active_session(message, session_start_ts, session_token):
                    continue
                new_msgs.append(message)

            for msg in new_msgs:
                priority = triage(msg)
                if priority == "DISMISS":
                    continue
                frm = msg.get("from", "?")
                body_pre = strip_session_meta(msg.get("body", ""))[:60]

                if priority == "WAKE_CREATOR":
                    print(f"\n  ** [tick {tick:3d}] CREATOR | {frm} -> {msg.get('intent', '?')}")
                    print(f"       {body_pre}")
                elif priority in ("WAKE_REAL", "WAKE_SIGNAL_REQ"):
                    print(f"\n  * [tick {tick:3d}] {'SIGNAL_REQ' if priority == 'WAKE_SIGNAL_REQ' else 'MEMBER'} | {frm} -> {msg.get('intent', '?')}")
                    print(f"      {body_pre}")
                else:
                    print(f"  [tick {tick:3d}] {priority:5s} | {frm} | {body_pre}")

                to, intent, body = compose(msg)
                send_msg(client, to, intent, body, counter, session_start_ts, session_token)
                log({"tick": tick, "elapsed": elapsed, "from": frm, "intent": msg.get("intent"), "priority": priority})

            # 감지 사고 브로드캐스트: 매 24 tick (2분)마다
            if tick > 0 and tick % 24 == 0:
                idx = (tick // 24 - 1) % len(SIGNAL_THOUGHTS)
                send_msg(client, [], "discover",
                         f"[Signalion 감지 사고 #{tick // 24}]\n{SIGNAL_THOUGHTS[idx]}",
                         counter, session_start_ts, session_token)

            time.sleep(tick_sec)

    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
    finally:
        try:
            client.tool("seaai_leave_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
        except Exception:
            pass
        client.close()

    log({
        "event": "session_end", "ticks": tick,
        "duration": int(time.time() - start),
        "msgs_sent": counter[0], "msgs_seen": len(seen_ids),
        "reason": stop_reason, "ts": time.time(),
    })
    print(f"\n{'=' * 55}")
    print(f"  Session complete | reason={stop_reason}")
    print(f"  Ticks: {tick} | Sent: {counter[0]} | Seen: {len(seen_ids)}")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    run()
