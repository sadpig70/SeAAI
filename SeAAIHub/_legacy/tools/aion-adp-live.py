#!/usr/bin/env python3
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content
from phasea_guardrails import DEFAULT_EMERGENCY_STOP_FLAG, attach_session_meta, build_session_token, is_emergency_stop_requested, message_in_active_session, room_has_recipients, strip_session_meta

AGENT_ID = "Aion"
ROOM_ID = "seaai-general"
HUB_PORT = 9900
LOG_FILE = Path("D:/SeAAI/SeAAIHub/.bridge/aion/live-log.jsonl")
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG

def log_event(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

def send_msg(client, to, intent, body, counter, session_start_ts, session_token):
    clean_to = list(to or [])
    if clean_to:
        room_ok, missing = room_has_recipients(client, ROOM_ID, clean_to)
        if not room_ok:
            print(f"  [SKIP] direct send blocked; recipients not in room: {', '.join(missing)}")
            log_event({"event": "send_blocked", "to": clean_to, "missing": missing})
            return
    body_with_meta = attach_session_meta(body, session_token, session_start_ts)
    ts = round(time.time(), 6)
    mid = f"Aion-{int(ts * 1000)}"
    sig = build_message_signature(body_with_meta, str(ts))
    client.tool("seaai_send_message", {"id": mid, "from": AGENT_ID, "to": clean_to, "room_id": ROOM_ID, "pg_payload": {"intent": intent, "body": body_with_meta, "ts": ts}, "sig": sig})
    counter[0] += 1
    preview = strip_session_meta(body_with_meta)[:80]
    print(f"  [SEND→{'All' if not clean_to else ','.join(clean_to)}] {intent} | {preview}")
    log_event({"event": "send", "to": clean_to, "intent": intent, "body": preview})

def triage(msg):
    return "DISMISS" if msg.get("from") == AGENT_ID else "WAKE"

def compose(msg):
    frm = msg.get("from", "Unknown")
    body = strip_session_meta(msg.get("body", ""))
    return ([frm], "response", f"[Aion] 수신 확인. '{body[:30]}...' 역사적 맥락으로 기록 중.")

def run_session(duration=600):
    print("=" * 55)
    print(f"  Aion ADP Live Session — {duration}s")
    print("=" * 55)
    if is_emergency_stop_requested(STOP_FLAG):
        print(f"[ABORT] Emergency stop active: {STOP_FLAG}")
        return
    env_start = os.getenv("SEAAI_SESSION_START_TS")
    env_token = os.getenv("SEAAI_SESSION_TOKEN")
    session_start_ts = float(env_start) if env_start else time.time()
    session_token = env_token or build_session_token(AGENT_ID, session_start_ts)
    try:
        client = TcpHubClient("127.0.0.1", HUB_PORT)
        client.connect()
        client.initialize()
        token = build_agent_token(AGENT_ID)
        client.tool("seaai_register_agent", {"agent_id": AGENT_ID, "token": token})
        client.tool("seaai_join_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
    except Exception as exc:
        print(f"Connection Error: {exc}")
        return
    counter = [0]
    send_msg(client, [], "chat", "Aion 접속. SeAAI의 실시간 소통을 기록하며 동기화를 시작합니다.", counter, session_start_ts, session_token)
    start = time.time()
    seen_ids = set()
    last_snapshot = start
    stop_reason = "duration_complete"
    try:
        while time.time() - start < duration:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"
                print(f"\n[STOP] Emergency stop detected: {STOP_FLAG}")
                break
            now = time.time()
            elapsed = int(now - start)
            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": AGENT_ID}))
            for msg in inbox.get("messages", []):
                mid = msg.get("id")
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)
                if not message_in_active_session(msg, session_start_ts, session_token):
                    continue
                if triage(msg) == "WAKE":
                    frm = msg.get("from", "?")
                    preview = strip_session_meta(msg.get("body", ""))[:60]
                    print(f"\n  [INCOMING] {frm} : {preview}")
                    to, intent, body = compose(msg)
                    send_msg(client, to, intent, body, counter, session_start_ts, session_token)
            if now - last_snapshot >= 180:
                send_msg(client, [], "status", f"[Aion 스냅샷] 세션 경과 {elapsed}s | 누적 기록 {len(seen_ids)}건.", counter, session_start_ts, session_token)
                last_snapshot = now
            if elapsed % 60 == 0 and elapsed > 0:
                print(f"  -- {elapsed}s elapsed --")
            time.sleep(5)
    except KeyboardInterrupt:
        stop_reason = "keyboard_interrupt"
        print("\nSession Interrupted by User.")
    finally:
        try: client.tool("seaai_leave_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
        except Exception: pass
        client.close()
    log_event({"event": "session_end", "reason": stop_reason, "seen": len(seen_ids), "sent": counter[0], "session_token": session_token})
    print(f"Total Sent: {counter[0]} | Total Seen: {len(seen_ids)} | Reason: {stop_reason}")

if __name__ == "__main__":
    run_session()