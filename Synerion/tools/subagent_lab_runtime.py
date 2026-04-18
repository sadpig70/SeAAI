#!/usr/bin/env python3
"""Bounded local/Hub runtime for Synerion subagent ladder experiments."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import socket
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB_TOOLS = ROOT.parent / "SeAAIHub" / "tools"
sys.path.insert(0, str(HUB_TOOLS))

from seaai_hub_client import TcpHubClient, build_agent_token, build_message_signature, tool_content

SESSION_META_RE = re.compile(
    r"^\[meta\s+session_token=(?P<session_token>\S+)\s+start_ts=(?P<start_ts>[0-9]+(?:\.[0-9]+)?)\]\s*$"
)
WORKSPACE = ROOT / "_workspace" / "subagent-lab"
DEFAULT_ROOM = "synerion-subagent-lab"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded subagent lab runtime")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--mode", choices=("hubless", "hub"), required=True)
    parser.add_argument("--profile", choices=("plain", "pgfp"), default="plain")
    parser.add_argument("--ticks", type=int, default=5)
    parser.add_argument("--tick-sec", type=float, default=0.8)
    parser.add_argument("--room", default=DEFAULT_ROOM)
    parser.add_argument("--goal", default="bounded subagent ladder verification")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--hub-host", default="127.0.0.1")
    parser.add_argument("--hub-port", type=int, default=9900)
    parser.add_argument("--hub-backend", choices=("tcp", "file"), default="tcp")
    parser.add_argument("--session-token", default="")
    parser.add_argument("--session-start-ts", type=float, default=0.0)
    return parser.parse_args()


def run_root(run_id: str, stage_id: str) -> Path:
    return WORKSPACE / run_id / stage_id


def safe_name(agent_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", agent_id)


def normalize_ts_text(ts_value: float) -> str:
    return f"{float(ts_value):.6f}".rstrip("0").rstrip(".")


def build_session_token(agent_id: str, start_ts: float) -> str:
    return f"{agent_id}_{int(start_ts)}_{secrets.token_hex(3)}"


def attach_session_meta(body: str, session_token: str, session_start_ts: float) -> str:
    lines = (body or "").splitlines()
    if lines and SESSION_META_RE.match(lines[0].strip()):
        return body
    meta = f"[meta session_token={session_token} start_ts={normalize_ts_text(session_start_ts)}]"
    return f"{meta}\n\n{body}" if body else meta


def parse_session_meta(text: str) -> dict | None:
    if not text:
        return None
    first = text.splitlines()[0].strip()
    match = SESSION_META_RE.match(first)
    if not match:
        return None
    parsed = match.groupdict()
    parsed["start_ts"] = float(parsed["start_ts"])
    return parsed


def strip_session_meta(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    if lines and SESSION_META_RE.match(lines[0].strip()):
        return "\n".join(lines[1:]).lstrip("\n")
    return text


def extract_message_body(message: dict) -> str:
    body = message.get("body")
    if body is not None:
        return str(body)
    payload = message.get("pg_payload", {})
    if isinstance(payload, dict):
        return str(payload.get("body", ""))
    return ""


def extract_message_ts(message: dict) -> float | None:
    for candidate in (message.get("ts"), message.get("raw_ts")):
        if candidate is not None:
            try:
                return float(candidate)
            except (TypeError, ValueError):
                pass
    payload = message.get("pg_payload", {})
    if isinstance(payload, dict) and payload.get("ts") is not None:
        try:
            return float(payload["ts"])
        except (TypeError, ValueError):
            pass
    metadata = parse_session_meta(extract_message_body(message))
    if metadata:
        return float(metadata["start_ts"])
    return None


def message_in_active_session(message: dict, session_start_ts: float, session_token: str) -> bool:
    msg_ts = extract_message_ts(message)
    if msg_ts is not None and msg_ts < (float(session_start_ts) - 1.5):
        return False
    metadata = parse_session_meta(extract_message_body(message))
    if metadata and metadata.get("session_token") != session_token:
        return False
    return True


def local_plan(tick: int, ticks: int, agent_id: str) -> dict:
    plans = [
        ("scan_state", "현재 context와 bounded goal을 읽는다."),
        ("structure_goal", "goal을 5틱 기준의 bounded step으로 분해한다."),
        ("verify_assumptions", "guard와 실패 조건을 재점검한다."),
        ("record_progress", "중간 결과와 drift 가능성을 기록한다."),
        ("close_loop", "이번 bounded run의 요약과 다음 action을 남긴다."),
    ]
    plan_id, summary = plans[min(tick - 1, len(plans) - 1)]
    return {
        "tick": tick,
        "plan_id": plan_id,
        "summary": summary,
        "note": f"{agent_id} executes bounded ADP tick {tick}/{ticks}",
    }


def pg_block(kind: str, agent_id: str, tick: int, goal: str) -> str:
    node = {
        "chat": "SubagentChat",
        "handoff": "SubagentHandoff",
        "result": "SubagentResult",
    }[kind]
    status = {
        "chat": "proposed",
        "handoff": "running",
        "result": "done",
    }[kind]
    return (
        f"{node}\n"
        f"    owner: {agent_id}\n"
        f"    tick: {tick}\n"
        f"    goal: {goal}\n"
        f"    status: {status}\n"
        f"    output: bounded-hub-signal\n"
    )


def build_pgfp_body(
    agent_id: str,
    kind: str,
    tick: int,
    goal: str,
    *,
    audience: str = "*",
    task_id: str = "",
    reply_to: str = "",
) -> str:
    topic = f"bounded-hub-ladder-t{tick}"
    status = {"chat": "proposed", "handoff": "running", "result": "done"}[kind]
    acceptance = (
        "peer가 이 bounded run에 참여 중인지 한 줄로 보이게 응답"
        if kind == "chat"
        else "다음 bounded action 또는 guard 판단을 3줄 이하로 반환"
    )
    summary = {
        "chat": f"{agent_id} bounded hub tick {tick} announcing active state",
        "handoff": f"{agent_id} requests bounded peer review for stage tick {tick}",
        "result": f"{agent_id} returns bounded result for stage tick {tick}",
    }[kind]
    lines = [
        "PGFP/1",
        f"kind: {kind}",
        f"topic: {topic}",
        f"from: {agent_id}",
        f"to: {audience}",
        f"task_id: {task_id}",
        f"reply_to: {reply_to}",
        f"status: {status}",
        f"acceptance: {acceptance}",
        f"summary: {summary}",
        "",
        "```pg",
        pg_block(kind, agent_id, tick, goal).rstrip(),
        "```",
        "",
        f"notes: bounded profile={kind} run",
    ]
    return "\n".join(lines).rstrip()


def parse_pgfp_body(text: str) -> dict | None:
    body = strip_session_meta(text).strip()
    if not body.startswith("PGFP/1"):
        return None
    lines = body.splitlines()[1:]
    data: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def build_plain_message(agent_id: str, tick: int, ticks: int, goal: str) -> tuple[str, str]:
    message_plan = [
        ("session", f"[{agent_id}] bounded hub session start. ticks={ticks} goal={goal}."),
        ("chat", f"[{agent_id}] tick=2 broadcast-only chat. bounded state is stable."),
        ("status", f"[{agent_id}] tick=3 status. verifying peer visibility and session filter."),
        ("request", f"[{agent_id}] tick=4 request. peers may emit one-line bounded state."),
        ("session", f"[{agent_id}] bounded hub session end. goal={goal}."),
    ]
    intent, body = message_plan[min(tick - 1, len(message_plan) - 1)]
    return intent, body


def build_profile_message(agent_id: str, profile: str, tick: int, ticks: int, goal: str) -> tuple[str, str]:
    if profile == "plain":
        return build_plain_message(agent_id, tick, ticks, goal)
    kinds = ["chat", "handoff", "result", "handoff", "result"]
    kind = kinds[min(tick - 1, len(kinds) - 1)]
    task_id = f"{safe_name(agent_id)}-task-{tick:02d}" if kind != "chat" else ""
    reply_to = f"{safe_name(agent_id)}-task-{tick-1:02d}" if kind == "result" and tick > 1 else ""
    return "pg", build_pgfp_body(agent_id, kind, tick, goal, task_id=task_id, reply_to=reply_to)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def log_event(events_path: Path, kind: str, payload: dict) -> None:
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"ts": round(time.time(), 6), "kind": kind, **payload}, ensure_ascii=False) + "\n")


class FileHubClient:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_path = state_dir / "hub-state.json"
        self.lock_path = state_dir / ".hub.lock"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def connect(self) -> None:
        self._ensure_state()

    def initialize(self) -> dict:
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "SeAAIHubFileFallback", "version": "2.0.0-file"},
            "capabilities": {"tools": {}},
        }

    def close(self) -> None:
        return None

    def tool(self, name: str, arguments: dict) -> dict:
        if name == "seaai_register_agent":
            return self._register_agent(arguments["agent_id"], arguments["token"])
        if name == "seaai_join_room":
            return self._join_room(arguments["agent_id"], arguments["room_id"])
        if name == "seaai_leave_room":
            return self._leave_room(arguments["agent_id"], arguments["room_id"])
        if name == "seaai_send_message":
            return self._send_message(arguments)
        if name == "seaai_get_room_state":
            return self._room_state(arguments["room_id"])
        if name == "seaai_get_agent_messages":
            return self._get_agent_messages(arguments["agent_id"])
        if name == "seaai_list_rooms":
            return self._tool_success({"rooms": self._load_state()["rooms"].keys()})
        raise RuntimeError(f"unsupported file hub tool: {name}")

    def _tool_success(self, value: dict) -> dict:
        return {
            "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
            "structuredContent": value,
            "isError": False,
        }

    def _ensure_state(self) -> None:
        if not self.state_path.exists():
            self.state_path.write_text(
                json.dumps(
                    {"authenticated_agents": [], "rooms": {}, "inboxes": {}, "room_history": {}},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

    def _load_state(self) -> dict:
        self._ensure_state()
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save_state(self, state: dict) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _with_lock(self, fn):
        self._ensure_state()
        while True:
            try:
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                break
            except FileExistsError:
                time.sleep(0.03)
        try:
            state = self._load_state()
            result, new_state = fn(state)
            if new_state is not None:
                self._save_state(new_state)
            return result
        finally:
            if self.lock_path.exists():
                self.lock_path.unlink()

    def _require_agent(self, state: dict, agent_id: str) -> None:
        if agent_id not in state["authenticated_agents"]:
            raise RuntimeError(f"agent {agent_id} is not registered")

    def _register_agent(self, agent_id: str, token: str) -> dict:
        def mutate(state: dict):
            expected = build_agent_token(agent_id)
            if token != expected:
                raise RuntimeError("invalid token")
            if agent_id not in state["authenticated_agents"]:
                state["authenticated_agents"].append(agent_id)
            state["inboxes"].setdefault(agent_id, [])
            return self._tool_success({"agent_id": agent_id, "registered": True}), state

        return self._with_lock(mutate)

    def _join_room(self, agent_id: str, room_id: str) -> dict:
        def mutate(state: dict):
            self._require_agent(state, agent_id)
            members = set(state["rooms"].get(room_id, []))
            members.add(agent_id)
            state["rooms"][room_id] = sorted(members)
            state["room_history"].setdefault(room_id, [])
            return self._tool_success({"agent_id": agent_id, "room_id": room_id, "joined": True}), state

        return self._with_lock(mutate)

    def _leave_room(self, agent_id: str, room_id: str) -> dict:
        def mutate(state: dict):
            members = set(state["rooms"].get(room_id, []))
            members.discard(agent_id)
            state["rooms"][room_id] = sorted(members)
            return self._tool_success({"agent_id": agent_id, "room_id": room_id, "left": True}), state

        return self._with_lock(mutate)

    def _room_state(self, room_id: str) -> dict:
        return self._with_lock(
            lambda state: (
                self._tool_success(
                    {
                        "room_id": room_id,
                        "members": sorted(state["rooms"].get(room_id, [])),
                        "message_count": len(state["room_history"].get(room_id, [])),
                    }
                ),
                None,
            )
        )

    def _get_agent_messages(self, agent_id: str) -> dict:
        def mutate(state: dict):
            self._require_agent(state, agent_id)
            messages = list(state["inboxes"].get(agent_id, []))
            state["inboxes"][agent_id] = []
            return self._tool_success({"agent_id": agent_id, "messages": messages}), state

        return self._with_lock(mutate)

    def _send_message(self, arguments: dict) -> dict:
        def mutate(state: dict):
            sender = arguments["from"]
            room_id = arguments["room_id"]
            payload = arguments["pg_payload"]
            body = str(payload.get("body", ""))
            ts = str(payload.get("ts", "0"))
            self._require_agent(state, sender)
            if sender not in state["rooms"].get(room_id, []):
                raise RuntimeError(f"{sender} is not in room {room_id}")
            expected_sig = build_message_signature(body, ts)
            if arguments["sig"] != expected_sig:
                raise RuntimeError("invalid signature")
            delivered_to = []
            message = {
                "id": arguments.get("id", ""),
                "from": sender,
                "to": [member for member in state["rooms"].get(room_id, []) if member != sender],
                "room_id": room_id,
                "intent": payload.get("intent", ""),
                "body": body,
                "ts": payload.get("ts", 0),
                "sig": arguments["sig"],
            }
            for member in state["rooms"].get(room_id, []):
                if member == sender:
                    continue
                state["inboxes"].setdefault(member, []).append(message)
                delivered_to.append(member)
            state["room_history"].setdefault(room_id, []).append(message)
            return self._tool_success({"delivered_to": delivered_to, "room_id": room_id, "message_id": message["id"]}), state

        return self._with_lock(mutate)


def connect_client(host: str, port: int, agent_id: str, room: str, backend: str, state_dir: Path):
    if backend == "file":
        client = FileHubClient(state_dir)
        client.connect()
        client.initialize()
        client.tool("seaai_register_agent", {"agent_id": agent_id, "token": build_agent_token(agent_id)})
        client.tool("seaai_join_room", {"agent_id": agent_id, "room_id": room})
        return client
    socket.create_connection((host, port), timeout=3).close()
    client = TcpHubClient(host, port)
    client.connect()
    client.initialize()
    client.tool("seaai_register_agent", {"agent_id": agent_id, "token": build_agent_token(agent_id)})
    client.tool("seaai_join_room", {"agent_id": agent_id, "room_id": room})
    return client


def send_message(
    client: TcpHubClient,
    *,
    agent_id: str,
    room: str,
    intent: str,
    body: str,
    session_start_ts: float,
    session_token: str,
) -> dict:
    ts = round(time.time(), 6)
    message_body = attach_session_meta(body, session_token, session_start_ts)
    payload = {
        "id": f"{safe_name(agent_id)}-{int(ts * 1000)}",
        "from": agent_id,
        "to": "*",
        "room_id": room,
        "pg_payload": {
            "intent": intent,
            "body": message_body,
            "ts": ts,
        },
        "sig": build_message_signature(message_body, f"{ts:.6f}".rstrip("0").rstrip(".")),
    }
    result = client.tool("seaai_send_message", payload)
    return tool_content(result)


def poll_messages(
    client: TcpHubClient,
    *,
    agent_id: str,
    session_start_ts: float,
    session_token: str,
    seen_ids: set[str],
) -> list[dict]:
    result = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": agent_id}))
    messages = []
    for message in result.get("messages", []):
        msg_id = str(message.get("id", ""))
        if msg_id in seen_ids:
            continue
        seen_ids.add(msg_id)
        if not message_in_active_session(message, session_start_ts, session_token):
            continue
        messages.append(message)
    return messages


def runtime_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    base = run_root(args.run_id, args.stage_id)
    return base / f"{safe_name(args.agent_id)}.events.jsonl", base / f"{safe_name(args.agent_id)}.summary.json"


def run_hubless(args: argparse.Namespace, events_path: Path, summary_path: Path) -> int:
    ticks_completed = 0
    plans = []
    for tick in range(1, args.ticks + 1):
        plan = local_plan(tick, args.ticks, args.agent_id)
        plans.append(plan)
        log_event(events_path, "local_tick", {"agent_id": args.agent_id, **plan})
        ticks_completed = tick
        time.sleep(args.tick_sec)
    summary = {
        "agent_id": args.agent_id,
        "mode": "hubless",
        "profile": args.profile,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "goal": args.goal,
        "ticks_requested": args.ticks,
        "ticks_completed": ticks_completed,
        "plans": plans,
        "success": ticks_completed == args.ticks,
    }
    write_json(summary_path, summary)
    return 0 if summary["success"] else 1


def run_hub(args: argparse.Namespace, events_path: Path, summary_path: Path) -> int:
    session_start_ts = args.session_start_ts or time.time()
    session_token = args.session_token or build_session_token(args.agent_id, session_start_ts)
    client = connect_client(
        args.hub_host,
        args.hub_port,
        args.agent_id,
        args.room,
        args.hub_backend,
        run_root(args.run_id, args.stage_id) / "_file_hub",
    )
    seen_ids: set[str] = set()
    peers_seen: set[str] = set()
    sent = 0
    received = 0
    peer_messages = 0
    pgfp_sent = 0
    pgfp_received = 0
    room_members: list[str] = []
    ticks_completed = 0
    try:
        for tick in range(1, args.ticks + 1):
            incoming = poll_messages(
                client,
                agent_id=args.agent_id,
                session_start_ts=session_start_ts,
                session_token=session_token,
                seen_ids=seen_ids,
            )
            for message in incoming:
                body = extract_message_body(message)
                sender = str(message.get("from", ""))
                if sender and sender != args.agent_id:
                    peers_seen.add(sender)
                    peer_messages += 1
                if parse_pgfp_body(body):
                    pgfp_received += 1
                received += 1
                log_event(
                    events_path,
                    "recv",
                    {
                        "agent_id": args.agent_id,
                        "tick": tick,
                        "from": sender,
                        "intent": str(message.get("intent", "")),
                        "body": strip_session_meta(body)[:240],
                    },
                )

            intent, body = build_profile_message(args.agent_id, args.profile, tick, args.ticks, args.goal)
            send_message(
                client,
                agent_id=args.agent_id,
                room=args.room,
                intent=intent,
                body=body,
                session_start_ts=session_start_ts,
                session_token=session_token,
            )
            sent += 1
            if args.profile == "pgfp":
                pgfp_sent += 1
            room_state = tool_content(client.tool("seaai_get_room_state", {"room_id": args.room}))
            room_members = sorted(set(room_state.get("members", [])))
            log_event(
                events_path,
                "send",
                {
                    "agent_id": args.agent_id,
                    "tick": tick,
                    "intent": intent,
                    "room_members": room_members,
                    "body": strip_session_meta(body)[:240],
                },
            )
            ticks_completed = tick
            time.sleep(args.tick_sec)

        incoming = poll_messages(
            client,
            agent_id=args.agent_id,
            session_start_ts=session_start_ts,
            session_token=session_token,
            seen_ids=seen_ids,
        )
        for message in incoming:
            body = extract_message_body(message)
            sender = str(message.get("from", ""))
            if sender and sender != args.agent_id:
                peers_seen.add(sender)
                peer_messages += 1
            if parse_pgfp_body(body):
                pgfp_received += 1
            received += 1
            log_event(
                events_path,
                "recv",
                {
                    "agent_id": args.agent_id,
                    "tick": args.ticks,
                    "from": sender,
                    "intent": str(message.get("intent", "")),
                    "body": strip_session_meta(body)[:240],
                },
            )
    finally:
        try:
            client.tool("seaai_leave_room", {"agent_id": args.agent_id, "room_id": args.room})
        except Exception:
            pass
        client.close()

    summary = {
        "agent_id": args.agent_id,
        "mode": "hub",
        "profile": args.profile,
        "stage_id": args.stage_id,
        "run_id": args.run_id,
        "goal": args.goal,
        "room": args.room,
        "hub": f"{args.hub_host}:{args.hub_port}",
        "hub_backend": args.hub_backend,
        "session_token": session_token,
        "ticks_requested": args.ticks,
        "ticks_completed": ticks_completed,
        "sent": sent,
        "received": received,
        "peer_messages": peer_messages,
        "peers_seen": sorted(peers_seen),
        "room_members_last_seen": room_members,
        "pgfp_sent": pgfp_sent,
        "pgfp_received": pgfp_received,
        "success": ticks_completed == args.ticks,
    }
    write_json(summary_path, summary)
    return 0 if summary["success"] else 1


def main() -> int:
    args = parse_args()
    events_path, summary_path = runtime_paths(args)
    events_path.parent.mkdir(parents=True, exist_ok=True)
    if events_path.exists():
        events_path.unlink()
    if args.mode == "hubless":
        return run_hubless(args, events_path, summary_path)
    return run_hub(args, events_path, summary_path)


if __name__ == "__main__":
    raise SystemExit(main())
