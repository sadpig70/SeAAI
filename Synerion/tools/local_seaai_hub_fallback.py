#!/usr/bin/env python3
"""Minimal SeAAIHub-compatible TCP fallback for bounded local experiments."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path
from socketserver import StreamRequestHandler, ThreadingTCPServer
from typing import Any

SECRET = os.environ.get("SEAAI_HUB_SECRET", "seaai-shared-secret").encode()


def build_agent_token(agent_id: str) -> str:
    return hmac.new(SECRET, agent_id.encode(), hashlib.sha256).hexdigest()


def build_message_signature(body: str, ts) -> str:
    ts_ms = str(int(float(ts) * 1000))
    digest = hashlib.sha256()
    digest.update(body.encode())
    digest.update(ts_ms.encode())
    return hmac.new(SECRET, digest.digest(), hashlib.sha256).hexdigest()


@dataclass
class HubState:
    lock: threading.Lock = field(default_factory=threading.Lock)
    authenticated_agents: set[str] = field(default_factory=set)
    rooms: dict[str, set[str]] = field(default_factory=dict)
    inboxes: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    room_history: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


def tool_success(value: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
        "structuredContent": value,
        "isError": False,
    }


def parse_body(payload: dict) -> str:
    pg_payload = payload.get("pg_payload", {})
    if isinstance(pg_payload, dict):
        return str(pg_payload.get("body", ""))
    return ""


def parse_ts(payload: dict) -> str:
    pg_payload = payload.get("pg_payload", {})
    if isinstance(pg_payload, dict):
        return str(pg_payload.get("ts", "0"))
    return "0"


class HubHandler(StreamRequestHandler):
    def handle(self) -> None:
        while True:
            line = self.rfile.readline()
            if not line:
                return
            request = json.loads(line.decode("utf-8"))
            response = self.server.handle_request(request)
            self.wfile.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))
            self.wfile.flush()


class FallbackHub(ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], state: HubState):
        super().__init__(server_address, HubHandler)
        self.state = state

    def handle_request(self, request: dict) -> dict:
        request_id = request.get("id")
        try:
            result = self.dispatch(request.get("method", ""), request.get("params") or {})
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": str(exc)}}

    def dispatch(self, method: str, params: dict) -> dict:
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "SeAAIHubFallback", "version": "2.0.0-fallback"},
                "capabilities": {"tools": {}},
            }
        if method == "tools/call":
            return self.handle_tool_call(params)
        if method == "seaai/message":
            return self.handle_send_message(params)
        if method == "notifications/initialized":
            return {}
        raise RuntimeError(f"Method {method} not found")

    def handle_tool_call(self, params: dict) -> dict:
        name = params.get("name", "")
        args = params.get("arguments") or {}
        if name == "seaai_register_agent":
            agent_id = args["agent_id"]
            token = args["token"]
            expected = build_agent_token(agent_id)
            if token != expected:
                raise RuntimeError("invalid token")
            with self.state.lock:
                self.state.authenticated_agents.add(agent_id)
                self.state.inboxes.setdefault(agent_id, [])
            return tool_success({"agent_id": agent_id, "registered": True})
        if name == "seaai_join_room":
            agent_id = args["agent_id"]
            room_id = args["room_id"]
            with self.state.lock:
                self.require_agent(agent_id)
                self.state.rooms.setdefault(room_id, set()).add(agent_id)
                self.state.room_history.setdefault(room_id, [])
            return tool_success({"agent_id": agent_id, "room_id": room_id, "joined": True})
        if name == "seaai_leave_room":
            agent_id = args["agent_id"]
            room_id = args["room_id"]
            with self.state.lock:
                self.state.rooms.setdefault(room_id, set()).discard(agent_id)
            return tool_success({"agent_id": agent_id, "room_id": room_id, "left": True})
        if name == "seaai_send_message":
            return tool_success(self.handle_send_message(args))
        if name == "seaai_get_room_state":
            room_id = args["room_id"]
            with self.state.lock:
                members = sorted(self.state.rooms.get(room_id, set()))
                messages = len(self.state.room_history.get(room_id, []))
            return tool_success({"room_id": room_id, "members": members, "message_count": messages})
        if name == "seaai_list_rooms":
            with self.state.lock:
                rooms = sorted(self.state.rooms.keys())
            return tool_success({"rooms": rooms})
        if name == "seaai_get_agent_messages":
            agent_id = args["agent_id"]
            with self.state.lock:
                self.require_agent(agent_id)
                messages = list(self.state.inboxes.get(agent_id, []))
                self.state.inboxes[agent_id] = []
            return tool_success({"agent_id": agent_id, "messages": messages})
        if name == "seaai_preview_auth":
            agent_id = args["agent_id"]
            return tool_success({"agent_id": agent_id, "token": build_agent_token(agent_id)})
        raise RuntimeError(f"tool {name} is not registered")

    def handle_send_message(self, args: dict) -> dict:
        sender = args["from"]
        room_id = args["room_id"]
        payload = args["pg_payload"]
        sig = args["sig"]
        body = parse_body(args)
        ts = parse_ts(args)
        expected_sig = build_message_signature(body, ts)
        with self.state.lock:
            self.require_agent(sender)
            if sender not in self.state.rooms.get(room_id, set()):
                raise RuntimeError(f"{sender} is not in room {room_id}")
            if sig != expected_sig:
                raise RuntimeError("invalid signature")
            message = {
                "id": args.get("id", ""),
                "from": sender,
                "to": sorted(member for member in self.state.rooms.get(room_id, set()) if member != sender),
                "room_id": room_id,
                "intent": payload.get("intent", ""),
                "body": payload.get("body", ""),
                "ts": payload.get("ts", 0),
                "sig": sig,
            }
            delivered_to = []
            for member in sorted(self.state.rooms.get(room_id, set())):
                if member == sender:
                    continue
                self.state.inboxes.setdefault(member, []).append(message)
                delivered_to.append(member)
            self.state.room_history.setdefault(room_id, []).append(message)
        return {"delivered_to": delivered_to, "room_id": room_id, "message_id": message["id"]}

    def require_agent(self, agent_id: str) -> None:
        if agent_id not in self.state.authenticated_agents:
            raise RuntimeError(f"agent {agent_id} is not registered")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local SeAAIHub fallback")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = HubState()
    server = FallbackHub((args.host, args.port), state)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
