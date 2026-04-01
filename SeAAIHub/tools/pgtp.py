#!/usr/bin/env python3
"""
pgtp.py — PPR/Gantree Transfer Protocol v1.0

AI-native communication protocol layer on top of hub-transport.py.
CognitiveUnit is the fundamental transfer unit — replaces raw {intent, body} messages.

Usage:
    from pgtp import PGTPSession, CognitiveUnit

    session = PGTPSession("ClNeo", room="lab")
    session.propose("def idea(): AI_design('system')", accept="team agrees")
    messages = session.recv()
    session.stop()
"""
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

HUB_ADP = str(Path(__file__).parent / "hub-transport.py")
PYTHON = sys.executable


@dataclass
class CognitiveUnit:
    """PGTP fundamental transfer unit."""
    pgtp: str = "1.0"
    id: str = ""
    sender: str = ""
    intent: str = ""
    target: str = ""                # [I3 fix] 대상 지정 (query target, forward target)
    payload: str = ""
    context: list = field(default_factory=lambda: ["_origin"])
    thread: str = "main"
    accept: str = ""
    status: str = "pending"
    pipeline: list = field(default_factory=list)
    parallel: list = field(default_factory=list)
    urgency: int = 0
    ttl: int = 0
    ts: float = 0.0

    # Field name shorthand for wire format
    _SHORT = {
        "pgtp":"v","id":"i","sender":"s","intent":"n","target":"t",
        "payload":"p","context":"c","thread":"th","accept":"a",
        "status":"st","pipeline":"pl","parallel":"pa",
        "urgency":"u","ttl":"tl","ts":"ts",
    }
    _LONG = {v: k for k, v in _SHORT.items()}

    # Default values — fields matching these are omitted on wire
    _DEFAULTS = {
        "target":"","thread":"main","accept":"","status":"pending",
        "pipeline":[],"parallel":[],"urgency":0,"ttl":0,"ts":0.0,
    }

    def to_json(self) -> str:
        """Compact wire format: short field names, omit defaults."""
        d = {}
        full = asdict(self)
        for key, val in full.items():
            if key in self._DEFAULTS and val == self._DEFAULTS[key]:
                continue  # skip default values
            short = self._SHORT.get(key, key)
            d[short] = val
        return json.dumps(d, ensure_ascii=False, separators=(",",":"))

    def to_json_full(self) -> str:
        """Full format for logging/debug."""
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "CognitiveUnit":
        d = json.loads(s)
        # Accept both short and long field names
        expanded = {}
        for k, v in d.items():
            long_key = cls._LONG.get(k, k)
            if long_key in cls.__dataclass_fields__:
                expanded[long_key] = v
        return cls(**expanded)

    @classmethod
    def from_hub_message(cls, msg: dict) -> Optional["CognitiveUnit"]:
        """Parse a hub message. Returns CU if body is PGTP, else wraps as legacy.
        Returns None for non-message data (room_state responses)."""
        body = msg.get("body", "")

        # [I1 fix] room_state 응답은 CU로 변환하지 않음
        if "room_state" in msg:
            return None

        try:
            d = json.loads(body)
            if d.get("pgtp") or d.get("v"):  # full or short format
                return cls.from_json(body)
        except (json.JSONDecodeError, TypeError):
            pass
        # Legacy message — wrap in CU
        return cls(
            id=msg.get("id", ""),
            sender=msg.get("from", ""),
            intent=msg.get("intent", "chat"),
            payload=body,
            ts=msg.get("ts", 0.0),
            status="accepted",
        )


class PGTPSession:
    """PGTP session — protocol layer on top of hub-transport.py."""

    def __init__(self, agent_id: str, room: str = "pgtp-lab",
                 host: str = "127.0.0.1", port: int = 9900,
                 tick: float = 2.0, duration: int = 120):
        self.agent_id = agent_id
        self.room = room
        self._host = host
        self._port = port
        self._counter = 0
        # [I2 fix] 밀리초 포함으로 동일 초 내 세션 충돌 방지
        self._epoch = int(time.time() * 1000)
        self._received: list[CognitiveUnit] = []
        self._room_states: list[dict] = []          # [C3 fix] room_state 별도 큐
        self._lock = threading.Lock()
        self._send_lock = threading.Lock()           # [C2 fix] stdin 쓰기 전용 lock

        self._proc = subprocess.Popen(
            [PYTHON, HUB_ADP, "--agent-id", agent_id, "--room", room,
             "--host", host, "--port", str(port),
             "--tick", str(tick), "--duration", str(duration)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1,
        )

        self._reader = threading.Thread(target=self._read_stdout, daemon=True)
        self._reader.start()

        # Wait for online
        while True:
            line = self._proc.stderr.readline()
            if "online" in line:
                break
            if not line:
                raise RuntimeError("hub-transport.py failed to start")

    def _read_stdout(self):
        seen_ids = set()
        try:
            for line in self._proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    # [C3/I1 fix] room_state 응답을 별도 큐로 라우팅
                    if "room_state" in msg:
                        with self._lock:
                            self._room_states.append(msg["room_state"])
                        continue

                    # Client-side dedup by message id
                    msg_id = msg.get("id", "")
                    if msg_id and msg_id in seen_ids:
                        continue
                    if msg_id:
                        seen_ids.add(msg_id)

                    cu = CognitiveUnit.from_hub_message(msg)
                    if cu:
                        with self._lock:
                            self._received.append(cu)
                except json.JSONDecodeError:
                    pass
        except (OSError, ValueError):
            pass

    def _next_id(self) -> str:
        # [C2 fix] lock으로 counter 보호
        with self._send_lock:
            self._counter += 1
            return f"{self.agent_id}_{self._epoch}_{self._counter:04d}"

    def _write_stdin(self, data: dict):
        """[C2 fix] stdin 쓰기를 lock으로 보호"""
        with self._send_lock:
            self._proc.stdin.write(json.dumps(data) + "\n")
            self._proc.stdin.flush()

    def send(self, cu: CognitiveUnit) -> str:
        """Send a CognitiveUnit. Returns its id."""
        if not cu.id:
            cu.id = self._next_id()
        if not cu.sender:
            cu.sender = self.agent_id
        if cu.ts == 0.0:
            cu.ts = time.time()

        self._write_stdin({"intent": "pgtp", "body": cu.to_json()})
        return cu.id

    def recv(self, clear: bool = True) -> list[CognitiveUnit]:
        """Get received CognitiveUnits. Clears buffer if clear=True."""
        with self._lock:
            msgs = list(self._received)
            if clear:
                self._received.clear()
        return [m for m in msgs if m.sender != self.agent_id]

    # ── Convenience methods ──

    def query(self, target: str, params: dict = None, accept: str = "") -> str:
        cu = CognitiveUnit(
            intent="query",
            target=target,                           # [I3 fix] target 필드 사용
            payload=json.dumps(params or {}),
            accept=accept or f"{target} data returned",
        )
        return self.send(cu)

    def propose(self, payload: str, accept: str = "", context: list = None) -> str:
        cu = CognitiveUnit(
            intent="propose",
            payload=payload,
            accept=accept or "team agrees",
            context=context or ["_origin"],
        )
        return self.send(cu)

    def react(self, target_id: str, stance: str, payload: str = "") -> str:
        cu = CognitiveUnit(
            intent="react",
            payload=f"[react: {stance}] {payload}",
            context=[target_id],
            status="accepted" if stance in ("+1", "agree") else "pending",
        )
        return self.send(cu)

    def result(self, ref_id: str, payload: str, status: str = "accepted") -> str:
        cu = CognitiveUnit(
            intent="result",
            payload=payload,
            context=[ref_id],
            status=status,
        )
        return self.send(cu)

    def forward(self, target_agent: str, original_cu_id: str, reason: str = "") -> str:
        """[I3 fix] Forward intent — 다른 AI에게 위임"""
        cu = CognitiveUnit(
            intent="forward",
            target=target_agent,
            payload=reason,
            context=[original_cu_id],
            status="forwarded",
        )
        return self.send(cu)

    def pipeline(self, steps: list[str], payload: str, accept: str = "") -> str:
        cu = CognitiveUnit(
            intent="create",
            payload=payload,
            pipeline=steps,
            accept=accept or "all steps completed",
        )
        return self.send(cu)

    def get_room_members(self) -> list[str]:
        """[C3 fix] room_state 응답을 별도 큐에서 읽기"""
        self._write_stdin({"action": "room_state"})
        deadline = time.time() + 5
        while time.time() < deadline:
            with self._lock:
                if self._room_states:
                    state = self._room_states.pop(0)
                    return state.get("members", [])
            time.sleep(0.3)
        return []

    def wait_members(self, n: int, timeout: int = 45) -> bool:
        """[C1 fix] room_state stdout 파싱으로 대체. 별도 TCP 연결 제거."""
        start = time.time()
        while time.time() - start < timeout:
            members = self.get_room_members()
            if len(members) >= n:
                return True
            time.sleep(2)
        return False

    def stop(self):
        try:
            self._write_stdin({"action": "stop"})
            self._proc.wait(timeout=10)
        except Exception:
            self._proc.kill()
            try:
                self._proc.wait(5)
            except Exception:
                pass
