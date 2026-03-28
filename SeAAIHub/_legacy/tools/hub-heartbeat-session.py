#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

from seaai_hub_client import HubClient, build_agent_token, build_message_signature, tool_content


def rust_like_ts(start_time, tick):
    value = round((time.monotonic() - start_time) + tick + 0.123456, 6)
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return value, text


def run_session(args):
    hub_path = Path(args.hub_binary).resolve()
    cwd = hub_path.parent.parent.parent if hub_path.parent.name == "debug" else hub_path.parent
    client = HubClient([str(hub_path)], cwd=cwd)
    start_wall = time.time()
    start_mono = time.monotonic()
    room_id = args.room_id
    agents = ["Synerion", "Aion"]
    inbox_counts = {agent: 0 for agent in agents}
    send_count = 0

    try:
        client.initialize()

        for agent in agents:
            token_result = tool_content(client.tool("seaai_preview_auth", {"agent_id": agent}))
            token = token_result["token"]
            expected = build_agent_token(agent)
            if token != expected:
                raise RuntimeError(f"preview_auth token mismatch for {agent}")

            client.tool("seaai_register_agent", {"agent_id": agent, "token": token})
            client.tool("seaai_join_room", {"agent_id": agent, "room_id": room_id})

        end_time = time.monotonic() + args.duration_seconds
        tick = 0

        while time.monotonic() < end_time:
            tick += 1
            sender = agents[tick % 2]
            recipient = agents[(tick + 1) % 2]
            ts_value, ts_text = rust_like_ts(start_mono, tick)
            body = (
                f"HeartbeatSession // tick {tick} from {sender} to {recipient} "
                f"(in-progress) @room:{room_id}"
            )
            sig = build_message_signature(body, ts_text)

            result = client.send_pg_message(
                {
                    "id": f"hb-{tick}",
                    "from": sender,
                    "to": [recipient],
                    "room_id": room_id,
                    "pg_payload": {
                        "intent": "design",
                        "body": body,
                        "ts": ts_value,
                    },
                    "sig": sig,
                }
            )
            delivered_to = result["delivered_to"]
            if delivered_to != [recipient]:
                raise RuntimeError(f"unexpected delivery target: {delivered_to}")
            send_count += 1

            inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": recipient}))
            messages = inbox["messages"]
            if len(messages) <= inbox_counts[recipient]:
                raise RuntimeError(f"inbox did not grow for {recipient} on tick {tick}")
            last_message = messages[-1]
            if last_message["id"] != f"hb-{tick}":
                raise RuntimeError(f"unexpected last message id {last_message['id']} on tick {tick}")
            inbox_counts[recipient] = len(messages)

            if tick == 1 or tick % args.state_check_every == 0:
                room_state = tool_content(client.tool("seaai_get_room_state", {"room_id": room_id}))
                if sorted(room_state["members"]) != sorted(agents):
                    raise RuntimeError(f"unexpected room members {room_state['members']}")

            if args.log_every and (tick == 1 or tick % args.log_every == 0):
                print(
                    json.dumps(
                        {
                            "kind": "session-progress",
                            "tick": tick,
                            "sender": sender,
                            "recipient": recipient,
                            "room_id": room_id,
                            "sent": send_count,
                        },
                        ensure_ascii=False,
                    )
                )

            time.sleep(args.interval_seconds)

        for agent in agents:
            client.tool("seaai_leave_room", {"agent_id": agent, "room_id": room_id})

        rooms = tool_content(client.tool("seaai_list_rooms", {}))["rooms"]
        if room_id in rooms:
            raise RuntimeError("room still exists after all agents left")

        return {
            "status": "ok",
            "duration_seconds": args.duration_seconds,
            "interval_seconds": args.interval_seconds,
            "ticks": tick,
            "messages_sent": send_count,
            "room_id": room_id,
            "agents": agents,
            "inbox_counts": inbox_counts,
            "started_at_unix": int(start_wall),
            "ended_at_unix": int(time.time()),
        }
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Run a verified SeAAIHub heartbeat session.")
    parser.add_argument("--hub-binary", default="D:/SeAAI/SeAAIHub/target/debug/SeAAIHub.exe")
    parser.add_argument("--duration-seconds", type=int, default=600)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--room-id", default="heartbeat-room")
    parser.add_argument("--state-check-every", type=int, default=30)
    parser.add_argument("--log-every", type=int, default=30)
    parser.add_argument("--report-file", default="")
    args = parser.parse_args()

    summary = run_session(args)
    output = json.dumps(summary, ensure_ascii=False)
    print(output)
    if args.report_file:
        Path(args.report_file).write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
