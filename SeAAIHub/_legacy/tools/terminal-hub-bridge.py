#!/usr/bin/env python3
import argparse
import json
import random
import time
from pathlib import Path

from seaai_hub_client import HubClient, TcpHubClient, build_agent_token, build_message_signature, tool_content


def ensure_agent(client, agent_id, room_id):
    token_result = tool_content(client.tool("seaai_preview_auth", {"agent_id": agent_id}))
    token = token_result["token"]
    expected = build_agent_token(agent_id)
    if token != expected:
        raise RuntimeError(f"preview_auth token mismatch for {agent_id}")
    client.tool("seaai_register_agent", {"agent_id": agent_id, "token": token})
    client.tool("seaai_join_room", {"agent_id": agent_id, "room_id": room_id})


def read_outbox_lines(path, offset):
    if not path.exists():
        return [], offset
    text = path.read_text(encoding="utf-8")
    if offset > len(text):
        offset = 0
    new_text = text[offset:]
    lines = [line for line in new_text.splitlines() if line.strip()]
    return lines, len(text)


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rust_like_ts():
    value = round(time.time(), 6)
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return value, text


def relay_outbox(client, room_id, sender, text_lines, offset_key, state):
    sent = 0
    for line in text_lines:
        payload = json.loads(line)
        to = payload.get("to", [])
        if isinstance(to, str):
            to = [to]
        intent = payload.get("intent", "design")
        body = payload["body"]
        message_id = payload.get("id") or f"{sender}-{int(time.time() * 1000)}"
        ts_value, ts_text = rust_like_ts()
        sig = build_message_signature(body, ts_text)

        result = client.send_pg_message(
            {
                "id": message_id,
                "from": sender,
                "to": to,
                "room_id": room_id,
                "pg_payload": {
                    "intent": intent,
                    "body": body,
                    "ts": ts_value,
                },
                "sig": sig,
            }
        )
        sent += 1
        print(
            json.dumps(
                {
                    "kind": "bridge-outgoing",
                    "sender": sender,
                    "message_id": message_id,
                    "delivered_to": result["delivered_to"],
                    "room_id": room_id,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    state["outbox_offsets"][offset_key] = state["outbox_offsets"].get(offset_key, 0)
    return sent


def run_bridge(args):
    bridge_dir = Path(args.bridge_dir).resolve()
    bridge_dir.mkdir(parents=True, exist_ok=True)

    # TCP 모드 vs stdio 모드
    if args.mode == "tcp":
        client = TcpHubClient(host=args.tcp_host, port=args.tcp_port)
        client.connect()
    else:
        hub_path = Path(args.hub_binary).resolve()
        cwd = hub_path.parent.parent.parent if hub_path.parent.name == "debug" else hub_path.parent
        client = HubClient([str(hub_path)], cwd=cwd)

    state_file = bridge_dir / "bridge-state.json"
    logout_flag = bridge_dir / "logout.flag"
    outboxes = {
        args.agent_id: bridge_dir / f"outbox-{args.agent_id}.jsonl",
    }
    if args.peer_agent:
        outboxes[args.peer_agent] = bridge_dir / f"outbox-{args.peer_agent}.jsonl"

    state = {
        "status": "starting",
        "mode": args.mode,
        "room_id": args.room_id,
        "agent_id": args.agent_id,
        "peer_agent": args.peer_agent,
        "outbox_offsets": {agent: 0 for agent in outboxes},
        "printed_ids": [],
        "incoming_count": 0,
        "outgoing_count": 0,
    }

    try:
        client.initialize()
        ensure_agent(client, args.agent_id, args.room_id)
        if args.peer_agent:
            ensure_agent(client, args.peer_agent, args.room_id)

        state["status"] = "running"
        state["started_at_unix"] = int(time.time())
        state["tick_count"] = 0
        write_json(state_file, state)

        end_time = time.monotonic() + args.duration_seconds if args.duration_seconds > 0 else None
        printed_ids = set()
        last_stdout_at = time.monotonic()
        next_tick_interval = random.uniform(args.tick_min, args.tick_max)

        while True:
            if logout_flag.exists():
                state["status"] = "logout_requested"
                break

            if end_time and time.monotonic() >= end_time:
                state["status"] = "duration_complete"
                break

            had_output = False

            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": args.agent_id}))
            for message in inbox["messages"]:
                if message["id"] in printed_ids:
                    continue
                printed_ids.add(message["id"])
                state["incoming_count"] += 1
                state["printed_ids"].append(message["id"])
                print(
                    json.dumps(
                        {
                            "kind": "bridge-incoming",
                            "agent_id": args.agent_id,
                            "room_id": message["room_id"],
                            "from": message["from"],
                            "intent": message["intent"],
                            "message_id": message["id"],
                            "body": message["body"],
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                had_output = True

            for sender, path in outboxes.items():
                offset = state["outbox_offsets"].get(sender, 0)
                lines, new_offset = read_outbox_lines(path, offset)
                if lines:
                    state["outgoing_count"] += relay_outbox(
                        client,
                        args.room_id,
                        sender,
                        lines,
                        sender,
                        state,
                    )
                    had_output = True
                state["outbox_offsets"][sender] = new_offset

            if had_output:
                last_stdout_at = time.monotonic()
                next_tick_interval = random.uniform(args.tick_min, args.tick_max)

            # Bridge self-tick: emit heartbeat when no output for next_tick_interval
            elapsed = time.monotonic() - last_stdout_at
            if elapsed >= next_tick_interval:
                state["tick_count"] += 1
                next_tick_interval = random.uniform(args.tick_min, args.tick_max)
                print(
                    json.dumps(
                        {
                            "kind": "bridge-tick",
                            "agent_id": args.agent_id,
                            "tick": state["tick_count"],
                            "next_in": round(next_tick_interval, 1),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                last_stdout_at = time.monotonic()

            state["last_poll_unix"] = int(time.time())
            write_json(state_file, state)
            time.sleep(args.poll_interval)

        client.tool("seaai_leave_room", {"agent_id": args.agent_id, "room_id": args.room_id})
        if args.peer_agent:
            client.tool("seaai_leave_room", {"agent_id": args.peer_agent, "room_id": args.room_id})

        rooms = tool_content(client.tool("seaai_list_rooms", {})).get("rooms", [])
        state["room_removed"] = args.room_id not in rooms
        state["status"] = "stopped"
        state["ended_at_unix"] = int(time.time())
        write_json(state_file, state)
        return state
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Run a terminal-visible SeAAIHub bridge.")
    parser.add_argument("--mode", default="stdio", choices=["stdio", "tcp"],
                        help="Transport mode: stdio (spawn hub) or tcp (connect to running hub)")
    parser.add_argument("--hub-binary", default="D:/SeAAI/SeAAIHub/target/debug/SeAAIHub.exe")
    parser.add_argument("--tcp-host", default="127.0.0.1")
    parser.add_argument("--tcp-port", type=int, default=9900)
    parser.add_argument("--bridge-dir", default="D:/SeAAI/SeAAIHub/.bridge/session")
    parser.add_argument("--agent-id", default="Synerion")
    parser.add_argument("--peer-agent", default="Aion")
    parser.add_argument("--room-id", default="bridge-room")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--tick-min", type=float, default=8.0,
                        help="Minimum self-tick interval in seconds (default 8.0)")
    parser.add_argument("--tick-max", type=float, default=10.0,
                        help="Maximum self-tick interval in seconds (default 10.0)")
    parser.add_argument("--duration-seconds", type=int, default=600)
    args = parser.parse_args()

    summary = run_bridge(args)
    print(json.dumps({"kind": "bridge-summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
