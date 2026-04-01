#!/usr/bin/env python3
"""
hub-transport.py — SeAAIHub ADP (Agent Daemon Presence) loop.

Pure transport layer: connect, poll, forward, send, log.
All triage/response logic belongs to the AI session, not here.

Communication:
    stdout ← received messages ONLY (one JSON per line)
             {"from":"NAEL", "intent":"chat", "body":"hello", "id":"...", "ts":...}
    stderr ← status/errors/logs  [hub-transport] ...
    stdin  → send commands        {"intent":"chat", "body":"hello"}
    stdin  → stop command          {"action":"stop"}

Usage:
    python hub-transport.py --agent-id ClNeo
    python hub-transport.py --agent-id NAEL --room ops-room --tick 3 --duration 300
"""
import argparse
import io
import json
import queue
import sys
import threading
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content

STOP_FLAG = Path(__file__).parent.parent.parent / "SharedSpace" / "hub-readiness" / "EMERGENCY_STOP.flag"
LOG_DIR = Path(__file__).parent.parent / ".bridge"


def parse_args():
    p = argparse.ArgumentParser(description="SeAAIHub ADP loop")
    p.add_argument("--agent-id", required=True, help="Agent identity (e.g. ClNeo)")
    p.add_argument("--room", default="seaai-general", help="Room to join")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9900)
    p.add_argument("--tick", type=float, default=5.0, help="Poll interval seconds")
    p.add_argument("--duration", type=int, default=600, help="Max seconds (0=unlimited)")
    return p.parse_args()


def info(msg):
    print(f"[hub-transport] {msg}", file=sys.stderr, flush=True)


def setup_log(agent_id):
    log_dir = LOG_DIR / agent_id.lower()
    log_dir.mkdir(parents=True, exist_ok=True)
    return open(log_dir / "adp-log.jsonl", "a", encoding="utf-8")


def log_event(fh, event, **kw):
    fh.write(json.dumps({"ts": time.time(), "event": event, **kw}, ensure_ascii=False) + "\n")
    fh.flush()


def hub_send(client, agent_id, room, intent, body):
    ts = time.time()
    sig = build_message_signature(body, ts)
    return client.send_pg_message({
        "from": agent_id,
        "room_id": room,
        "pg_payload": {"intent": intent, "body": body, "ts": ts},
        "sig": sig,
    })


def hub_poll(client, agent_id):
    result = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": agent_id}))
    return result.get("messages", [])


def stdin_reader(cmd_queue, stop_event):
    """Read stdin lines in a dedicated thread. Works with both pipe and console."""
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                cmd_queue.put(json.loads(line))
            except json.JSONDecodeError:
                pass
            if stop_event.is_set():
                break
    except (EOFError, OSError):
        pass
    stop_event.set()


def main():
    args = parse_args()
    agent_id = args.agent_id
    log_fh = setup_log(agent_id)

    # Connect
    client = TcpHubClient(args.host, args.port)
    try:
        client.connect()
    except OSError as e:
        info(f"ABORT: {args.host}:{args.port} - {e}")
        sys.exit(1)

    client.initialize()
    client.tool("seaai_register_agent", {"agent_id": agent_id, "token": build_agent_token(agent_id)})
    client.tool("seaai_join_room", {"agent_id": agent_id, "room_id": args.room})

    info(f"{agent_id} online | room={args.room} tick={args.tick}s")
    log_event(log_fh, "session_start", agent_id=agent_id, room=args.room)

    # Stdin reader thread
    cmd_queue = queue.Queue()
    stop_event = threading.Event()
    reader = threading.Thread(target=stdin_reader, args=(cmd_queue, stop_event), daemon=True)
    reader.start()

    start = time.time()
    tick_count = 0
    msgs_received = 0
    msgs_sent = 0

    try:
        while not stop_event.is_set():
            if args.duration > 0 and (time.time() - start) >= args.duration:
                info("duration limit reached")
                break

            if STOP_FLAG.exists():
                info("EMERGENCY STOP")
                break

            # Process stdin commands
            while not cmd_queue.empty():
                cmd = cmd_queue.get_nowait()
                if cmd.get("action") == "stop":
                    stop_event.set()
                    break
                if cmd.get("action") == "room_state":
                    state = tool_content(client.tool("seaai_get_room_state", {"room_id": args.room}))
                    print(json.dumps({"room_state": state}, ensure_ascii=False), flush=True)
                    continue
                intent = cmd.get("intent", "chat")
                body = cmd.get("body", "")
                if body:
                    try:
                        result = hub_send(client, agent_id, args.room, intent, body)
                        delivered = result.get("delivered_to", [])
                        msgs_sent += 1
                        log_event(log_fh, "send", intent=intent, body=body[:80], delivered_to=delivered)
                        info(f"sent [{intent}] -> {delivered}")
                    except RuntimeError as e:
                        log_event(log_fh, "send_error", intent=intent, body=body[:80], error=str(e))
                        info(f"send error: {e}")

            if stop_event.is_set():
                break

            # Poll hub — stdout gets ONLY received messages
            messages = hub_poll(client, agent_id)
            tick_count += 1

            for m in messages:
                msgs_received += 1
                out = {
                    "id": m.get("id", ""),
                    "from": m.get("from", ""),
                    "intent": m.get("intent", ""),
                    "body": m.get("body", ""),
                    "ts": m.get("ts", 0),
                }
                print(json.dumps(out, ensure_ascii=False), flush=True)
                log_event(log_fh, "recv", **out)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        info(f"ERROR: {e}")
        log_event(log_fh, "error", message=str(e))
    finally:
        stop_event.set()
        try:
            client.tool("seaai_leave_room", {"agent_id": agent_id, "room_id": args.room})
        except Exception:
            pass
        client.close()
        log_event(log_fh, "session_end", ticks=tick_count, received=msgs_received, sent=msgs_sent)
        log_fh.close()
        info(f"{agent_id} offline | ticks={tick_count} recv={msgs_received} sent={msgs_sent}")


if __name__ == "__main__":
    main()
