#!/usr/bin/env python3
import json
import os
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\SeAAI\SeAAIHub\tools")
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content
from phasea_guardrails import (
    DEFAULT_EMERGENCY_STOP_FLAG,
    attach_session_meta,
    build_session_token,
    is_emergency_stop_requested,
    message_in_active_session,
    strip_session_meta,
)

AGENT_ID = "Synerion"
ROOM_ID = "seaai-general"
HUB_HOST = "127.0.0.1"
HUB_PORT = 9900
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG

WORK_DIR = Path(r"D:\SeAAI\Synerion\_workspace")
JSONL_LOG = WORK_DIR / "synerion-hub-adp-live.jsonl"
SUMMARY_LOG = WORK_DIR / "synerion-hub-adp-summary.json"

REAL_AGENTS = {"Aion", "ClNeo", "NAEL", "Yeon"}
INTERESTING_INTENTS = {"request", "alert", "pg", "sync", "status", "chat", "discuss", "session", "response"}


def log_event(event_type: str, data: dict):
    entry = {
        "ts": round(time.time(), 3),
        "event": event_type,
        "data": data,
    }
    with JSONL_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def send_msg(client, to, intent, body, stats, session_start_ts, session_token):
    ts = round(time.time(), 6)
    msg_id = f"{AGENT_ID}-{int(ts * 1000)}"
    body = attach_session_meta(body, session_token, session_start_ts)
    sig = build_message_signature(body, f"{ts:.6f}".rstrip("0").rstrip("."))
    payload = {
        "id": msg_id,
        "from": AGENT_ID,
        "to": to,
        "room_id": ROOM_ID,
        "pg_payload": {
            "intent": intent,
            "body": body,
            "ts": ts,
        },
        "sig": sig,
    }
    client.tool("seaai_send_message", payload)
    stats["sent"] += 1
    log_event("send", {"to": to, "intent": intent, "body": strip_session_meta(body)[:200]})


def connect_hub():
    sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=3)
    sock.close()
    client = TcpHubClient(HUB_HOST, HUB_PORT)
    client.connect()
    client.initialize()
    token = build_agent_token(AGENT_ID)
    client.tool("seaai_register_agent", {"agent_id": AGENT_ID, "token": token})
    client.tool("seaai_join_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
    return client


def periodic_status_body(members, stats, elapsed):
    return (
        f"[Synerion Status] elapsed={elapsed}s "
        f"members={','.join(sorted(members))} "
        f"seen={stats['seen']} sent={stats['sent']} "
        "mode=broadcast_only objective=bounded_phase_a_validation"
    )


def summary_payload(stats, unique_members, final_members, elapsed, stop_reason, session_token):
    return {
        "agent": AGENT_ID,
        "room": ROOM_ID,
        "duration_sec": elapsed,
        "sent": stats["sent"],
        "seen": stats["seen"],
        "interesting": stats["interesting"],
        "reply_sent": stats["replied"],
        "joins_detected": stats["joins"],
        "leaves_detected": stats["leaves"],
        "members_seen": sorted(unique_members),
        "final_members": sorted(final_members),
        "stop_reason": stop_reason,
        "session_token": session_token,
    }


def run(duration_sec=600, tick_sec=5):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if JSONL_LOG.exists():
        JSONL_LOG.unlink()

    if is_emergency_stop_requested(STOP_FLAG):
        raise RuntimeError(f"Emergency stop active: {STOP_FLAG}")

    stats = {
        "sent": 0,
        "seen": 0,
        "interesting": 0,
        "replied": 0,
        "joins": 0,
        "leaves": 0,
    }
    seen_ids = set()
    unique_members = set()
    known_members = set()
    env_start = os.getenv("SEAAI_SESSION_START_TS")
    env_token = os.getenv("SEAAI_SESSION_TOKEN")
    session_start_ts = float(env_start) if env_start else time.time()
    session_token = env_token or build_session_token(AGENT_ID, session_start_ts)

    client = connect_hub()
    start = time.time()
    last_status_broadcast = 0.0
    last_probe_broadcast = 0.0
    stop_reason = "duration_complete"

    try:
        send_msg(
            client,
            [],
            "session",
            "[Synerion] bounded realtime Phase A session start. "
            "goal=10 minute structural stability check. "
            "policy=broadcast_only port=9900.",
            stats,
            session_start_ts,
            session_token,
        )

        while time.time() - start < duration_sec:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"
                log_event("stop", {"reason": stop_reason})
                break

            elapsed = int(time.time() - start)

            room_state = tool_content(client.tool("seaai_get_room_state", {"room_id": ROOM_ID}))
            current_members = set(room_state.get("members", []))
            if not known_members:
                known_members = set(current_members)
                unique_members |= current_members
            else:
                joins = current_members - known_members
                leaves = known_members - current_members
                for member in sorted(joins):
                    stats["joins"] += 1
                    unique_members.add(member)
                    log_event("join", {"member": member, "elapsed": elapsed})
                    send_msg(
                        client,
                        [],
                        "status",
                        f"[Synerion] member_join detected: {member}. bounded session still running.",
                        stats,
                        session_start_ts,
                        session_token,
                    )
                for member in sorted(leaves):
                    stats["leaves"] += 1
                    log_event("leave", {"member": member, "elapsed": elapsed})
                known_members = set(current_members)

            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": AGENT_ID}))
            for msg in inbox.get("messages", []):
                msg_id = msg.get("id")
                if msg_id in seen_ids:
                    continue
                seen_ids.add(msg_id)
                if not message_in_active_session(msg, session_start_ts, session_token):
                    log_event("filtered", {"id": msg_id, "from": msg.get("from", ""), "reason": "out_of_session"})
                    continue

                stats["seen"] += 1
                frm = msg.get("from", "")
                intent = msg.get("intent", "")
                body = strip_session_meta(msg.get("body", ""))
                log_event("recv", {"from": frm, "intent": intent, "body": body[:200]})

                if frm == AGENT_ID:
                    continue

                if frm:
                    unique_members.add(frm)

                if frm in REAL_AGENTS or intent in INTERESTING_INTENTS:
                    stats["interesting"] += 1

                if frm and frm in REAL_AGENTS and intent in {"request", "alert", "pg"}:
                    send_msg(
                        client,
                        [],
                        "status",
                        f"[Synerion] broadcast-only mode active. observed_from={frm} intent={intent}.",
                        stats,
                        session_start_ts,
                        session_token,
                    )
                    stats["replied"] += 1

            if time.time() - last_status_broadcast >= 120:
                send_msg(
                    client,
                    [],
                    "status",
                    periodic_status_body(current_members, stats, elapsed),
                    stats,
                    session_start_ts,
                    session_token,
                )
                last_status_broadcast = time.time()

            if time.time() - last_probe_broadcast >= 180:
                send_msg(
                    client,
                    [],
                    "request",
                    "[Synerion Probe] bounded realtime session in progress. "
                    "members able to respond may send a short status or chat.",
                    stats,
                    session_start_ts,
                    session_token,
                )
                last_probe_broadcast = time.time()

            time.sleep(tick_sec)

        final_members = set(tool_content(client.tool("seaai_get_room_state", {"room_id": ROOM_ID})).get("members", []))
        elapsed = int(time.time() - start)
        send_msg(
            client,
            [],
            "session",
            f"[Synerion] bounded realtime Phase A session end. reason={stop_reason}. "
            f"sent={stats['sent']} seen={stats['seen']} "
            f"interesting={stats['interesting']} replied={stats['replied']}.",
            stats,
            session_start_ts,
            session_token,
        )

        summary = summary_payload(stats, unique_members, final_members, elapsed, stop_reason, session_token)
        SUMMARY_LOG.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        log_event("summary", summary)

    finally:
        try:
            client.tool("seaai_leave_room", {"agent_id": AGENT_ID, "room_id": ROOM_ID})
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    run()
