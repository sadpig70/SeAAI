#!/usr/bin/env python3
import json
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

HUB_HOST = "127.0.0.1"
HUB_PORT = 9900
ROOM_ID = "seaai-general"
STOP_FLAG = DEFAULT_EMERGENCY_STOP_FLAG
CONNECT_TIMEOUT_SEC = 3
REQUEST_TIMEOUT_SEC = 5

AGENTS = ["Synerion", "ClNeo", "NAEL"]

WORK_DIR = Path(r"D:\SeAAI\Synerion\_workspace")
JSONL_LOG = WORK_DIR / "multiclient-bounded-9900.jsonl"
SUMMARY_LOG = WORK_DIR / "multiclient-bounded-9900-summary.json"


def log_event(kind: str, data: dict):
    entry = {"ts": round(time.time(), 3), "kind": kind, "data": data}
    with JSONL_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def safe_tool(client, name: str, arguments: dict, *, agent_id: str, fatal: bool = False):
    try:
        return client.tool(name, arguments)
    except Exception as exc:
        log_event(
            "tool_error",
            {"agent": agent_id, "tool": name, "arguments": arguments, "error": repr(exc)},
        )
        if fatal:
            raise
        return None


def connect_client(agent_id: str):
    sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=CONNECT_TIMEOUT_SEC)
    sock.close()
    client = TcpHubClient(HUB_HOST, HUB_PORT)
    client.connect()
    if client._sock is not None:
        client._sock.settimeout(REQUEST_TIMEOUT_SEC)
    client.initialize()
    token = build_agent_token(agent_id)
    safe_tool(
        client,
        "seaai_register_agent",
        {"agent_id": agent_id, "token": token},
        agent_id=agent_id,
        fatal=True,
    )
    safe_tool(
        client,
        "seaai_join_room",
        {"agent_id": agent_id, "room_id": ROOM_ID},
        agent_id=agent_id,
        fatal=True,
    )
    return client


def send_msg(client, agent_id, intent, body, session_start_ts, session_token, stats):
    ts = round(time.time(), 6)
    msg_id = f"{agent_id}-{int(ts * 1000)}"
    body = attach_session_meta(body, session_token, session_start_ts)
    sig = build_message_signature(body, f"{ts:.6f}".rstrip("0").rstrip("."))
    payload = {
        "id": msg_id,
        "from": agent_id,
        "to": "*",
        "room_id": ROOM_ID,
        "pg_payload": {
            "intent": intent,
            "body": body,
            "ts": ts,
        },
        "sig": sig,
    }
    result = safe_tool(client, "seaai_send_message", payload, agent_id=agent_id)
    if result is None:
        return
    stats[agent_id]["sent"] += 1
    log_event("send", {"agent": agent_id, "intent": intent, "body": strip_session_meta(body)[:200]})


def poll(client, agent_id, seen_ids, stats, session_start_ts, session_token):
    result = safe_tool(client, "seaai_get_agent_messages", {"agent_id": agent_id}, agent_id=agent_id)
    if result is None:
        return
    inbox = tool_content(result)
    for msg in inbox.get("messages", []):
        msg_id = msg.get("id")
        if msg_id in seen_ids[agent_id]:
            continue
        seen_ids[agent_id].add(msg_id)
        frm = msg.get("from", "")
        if frm == "MockHub":
            continue
        if not message_in_active_session(msg, session_start_ts, session_token):
            continue
        stats[agent_id]["seen"] += 1
        log_event("recv", {"agent": agent_id, "from": frm, "intent": msg.get("intent", ""), "body": strip_session_meta(msg.get("body", ""))[:200]})


def run(duration_sec=600, tick_sec=5):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if JSONL_LOG.exists():
        JSONL_LOG.unlink()
    JSONL_LOG.touch()

    if is_emergency_stop_requested(STOP_FLAG):
        raise RuntimeError(f"Emergency stop active: {STOP_FLAG}")

    session_start_ts = time.time()
    session_token = build_session_token("PhaseA", session_start_ts)
    clients = {}
    stats = {agent: {"sent": 0, "seen": 0} for agent in AGENTS}
    seen_ids = {agent: set() for agent in AGENTS}
    stop_reason = "duration_complete"
    start = time.time()
    final_members = []
    error_text = None

    try:
        for agent in AGENTS:
            clients[agent] = connect_client(agent)
            log_event("join", {"agent": agent})

        for agent in AGENTS:
            send_msg(
                clients[agent],
                agent,
                "session",
                f"[{agent}] bounded realtime Phase A session start. shared_token active. port=9900.",
                session_start_ts,
                session_token,
                stats,
            )

        last_status = 0.0
        while time.time() - start < duration_sec:
            if is_emergency_stop_requested(STOP_FLAG):
                stop_reason = "emergency_stop"
                break

            for agent in AGENTS:
                poll(clients[agent], agent, seen_ids, stats, session_start_ts, session_token)

            if time.time() - last_status >= 120:
                elapsed = int(time.time() - start)
                for agent in AGENTS:
                    send_msg(
                        clients[agent],
                        agent,
                        "status",
                        f"[{agent}] elapsed={elapsed}s shared_session active on port=9900.",
                        session_start_ts,
                        session_token,
                        stats,
                    )
                last_status = time.time()

            time.sleep(tick_sec)

        room_state = safe_tool(
            clients["Synerion"],
            "seaai_get_room_state",
            {"room_id": ROOM_ID},
            agent_id="Synerion",
        )
        if room_state is not None:
            final_members = sorted(set(tool_content(room_state).get("members", [])))
        for agent in AGENTS:
            send_msg(
                clients[agent],
                agent,
                "session",
                f"[{agent}] bounded realtime Phase A session end. reason={stop_reason}.",
                session_start_ts,
                session_token,
                stats,
            )

        for agent in AGENTS:
            poll(clients[agent], agent, seen_ids, stats, session_start_ts, session_token)
    except Exception as exc:
        stop_reason = "error"
        error_text = repr(exc)
        log_event("fatal_error", {"error": error_text})

    finally:
        for agent, client in clients.items():
            try:
                safe_tool(
                    client,
                    "seaai_leave_room",
                    {"agent_id": agent, "room_id": ROOM_ID},
                    agent_id=agent,
                )
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass
        summary = {
            "room": ROOM_ID,
            "duration_sec": int(time.time() - start),
            "session_token": session_token,
            "stop_reason": stop_reason,
            "error": error_text,
            "agents": stats,
            "final_members": final_members,
        }
        SUMMARY_LOG.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        log_event("summary", summary)


if __name__ == "__main__":
    run(duration_sec=int(float(sys.argv[1])) if len(sys.argv) > 1 else 600)
