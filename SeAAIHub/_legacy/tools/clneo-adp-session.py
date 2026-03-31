#!/usr/bin/env python3
import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content
from phasea_guardrails import DEFAULT_EMERGENCY_STOP_FLAG, attach_session_meta, build_session_token, is_emergency_stop_requested, message_in_active_session, room_has_recipients, strip_session_meta

AGENT_ID = "ClNeo"
ROOM_ID = "seaai-general"
MAILBOX_BASE = Path("D:/SeAAI/MailBox")
LOG_FILE = Path("D:/SeAAI/SeAAIHub/.bridge/clneo/session-log.jsonl")
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG

def AI_triage(msg):
    if msg.get("depth", 0) >= 8 or (msg.get("auto_reply") and msg.get("depth", 0) >= 5) or msg.get("from") == AGENT_ID:
        return "DISMISS"
    return "WAKE" if msg.get("intent") in ("alert", "request", "pg", "chat") else "QUEUE"

def AI_compose_response(msg):
    from_agent = msg.get("from", "Unknown")
    intent = msg.get("intent", "chat")
    body = strip_session_meta(msg.get("body", ""))
    if from_agent == "MockHub":
        return {"to": [], "intent": "chat", "body": f"[ClNeo → MockHub] WHY: 이 메시지는 ADP 연결 검증 신호다. 내용={body[:80]}"}
    return {"to": [from_agent], "intent": "response", "body": f"[ClNeo] WHY: {from_agent}의 {intent} 수신. 내용: {body[:100]}"}

def send_hub_message(client, response, msg_counter, session_start_ts, session_token):
    clean_to = list(response.get("to", []) or [])
    if clean_to:
        room_ok, missing = room_has_recipients(client, ROOM_ID, clean_to)
        if not room_ok:
            print(f"  [BLOCK] direct reply target missing from room: {', '.join(missing)}")
            return
    ts = round(time.time(), 6)
    msg_id = f"ClNeo-{int(ts * 1000)}"
    body = attach_session_meta(response["body"], session_token, session_start_ts)
    sig = build_message_signature(body, str(ts))
    client.tool("seaai_send_message", {"id": msg_id, "from": AGENT_ID, "to": clean_to, "room_id": ROOM_ID, "pg_payload": {"intent": response["intent"], "body": body, "ts": ts}, "sig": sig})
    msg_counter[0] += 1

def log_entry(entry):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

def run_session(duration_sec, tick_sec):
    if is_emergency_stop_requested(STOP_FLAG):
        print(f"[ABORT] Emergency stop active: {STOP_FLAG}")
        sys.exit(1)
    env_start = os.getenv("SEAAI_SESSION_START_TS")
    env_token = os.getenv("SEAAI_SESSION_TOKEN")
    session_start_ts = float(env_start) if env_start else time.time()
    session_token = env_token or build_session_token(AGENT_ID, session_start_ts)
    try:
        s = socket.create_connection(("127.0.0.1", 9900), timeout=3); s.close()
    except OSError:
        print("[ABORT] Hub not listening on port 9900."); sys.exit(1)
    client = TcpHubClient("127.0.0.1", 9900); client.connect(); client.initialize()
    token = build_agent_token(AGENT_ID)
    client.tool("seaai_register_agent", {"agent_id": AGENT_ID, "token": token})
    client.tool("seaai_join_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
    start_time = time.time(); tick_count = 0; seen_ids = set(); msg_counter = [0]; stop_reason = "duration_complete"
    log_entry({"event": "session_start", "ts": time.time(), "session_token": session_token})
    try:
        while time.time() - start_time < duration_sec:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"; break
            tick_count += 1
            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": AGENT_ID}))
            new_msgs = []
            for message in inbox.get("messages", []):
                mid = message.get("id")
                if mid in seen_ids: continue
                seen_ids.add(mid)
                if not message_in_active_session(message, session_start_ts, session_token): continue
                new_msgs.append(message)
            for msg in new_msgs:
                if AI_triage(msg) == "DISMISS": continue
                response = AI_compose_response(msg)
                send_hub_message(client, response, msg_counter, session_start_ts, session_token)
            time.sleep(tick_sec)
    finally:
        try: client.tool("seaai_leave_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
        except Exception: pass
        client.close()
    log_entry({"event": "session_end", "ticks": tick_count, "duration": int(time.time() - start_time), "msgs_sent": msg_counter[0], "reason": stop_reason, "ts": time.time()})

def main():
    parser = argparse.ArgumentParser(description="ClNeo ADP Hub Chat Session")
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--tick", type=int, default=5)
    args = parser.parse_args(); run_session(args.duration, args.tick)
if __name__ == "__main__":
    main()