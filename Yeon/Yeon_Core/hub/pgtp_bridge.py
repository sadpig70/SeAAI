"""
pgtp_bridge.py — PGTP v1.0 CognitiveUnit bridge for Yeon.
Maps between PGTP CognitiveUnit (Python object) and Hub JSON messages.
Reference: docs/pgtp/SPEC-PGTP-v1.md
"""
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from hub.compact_encode import encode as compact_encode
from hub.compact_decode import decode as compact_decode
from hub.schedule_builder import build_schedule as _build_schedule_raw, build_confirm as _build_confirm_raw


from hub.dag_tracker import validate_dag, has_cycle


@dataclass
class CognitiveUnit:
    """PGTP v1.0 전송 단위 — AI-native cognitive packet."""
    intent: str
    payload: str
    sender: str = "Yeon"
    pgtp: str = "1.0"
    id: str = ""
    target: str = ""
    context: List[str] = field(default_factory=lambda: ["_origin"])
    thread: str = "main"
    accept: str = ""
    status: str = "pending"
    pipeline: List[str] = field(default_factory=list)
    parallel: List[str] = field(default_factory=list)
    urgency: int = 0
    ttl: int = 0
    ts: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"{self.sender}_{int(time.time() * 1000)}"
        if self.ts == 0.0:
            self.ts = time.time()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def to_hub_body(self) -> str:
        """Hub 메시지의 body 필드로 직렬화 (compact, one-line)."""
        return compact_encode(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveUnit":
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @classmethod
    def from_hub_message(cls, msg: dict) -> Optional["CognitiveUnit"]:
        """Hub 수신 메시지({from, intent, body, ts, ...})에서 CU를 추출."""
        body = msg.get("body", "")
        if not body:
            return None
        try:
            data = json.loads(body) if isinstance(body, str) else body
        except json.JSONDecodeError:
            return None
        if data.get("pgtp") != "1.0" and data.get("v") != "1.0":
            return None
        if "v" in data and "pgtp" not in data:
            return compact_decode(body, cls)
        cu = cls.from_dict(data)
        cu.ts = msg.get("ts", cu.ts)
        return cu

    def validate(self) -> bool:
        return all([
            self.pgtp == "1.0",
            bool(self.id),
            bool(self.sender),
            bool(self.intent),
        ])


def build_hub_command(intent: str, body: str) -> dict:
    """hub-transport.py stdin 명령 형식으로 변환."""
    return {"intent": intent, "body": body}


def build_pgtp_hub_command(cu: CognitiveUnit) -> dict:
    """PGTP 메시지를 Hub 발신 명령으로 변환."""
    return build_hub_command("pgtp", cu.to_hub_body())


def build_schedule(*args, **kwargs) -> CognitiveUnit:
    return CognitiveUnit.from_dict(_build_schedule_raw(*args, **kwargs))


def build_confirm(*args, **kwargs) -> CognitiveUnit:
    return CognitiveUnit.from_dict(_build_confirm_raw(*args, **kwargs))


# Re-export compact and schedule utilities
__all__ = [
    "CognitiveUnit",
    "build_pgtp_hub_command",
    "build_hub_command",
    "compact_encode",
    "compact_decode",
    "build_schedule",
    "build_confirm",
    "validate_dag",
    "has_cycle",
]

if __name__ == "__main__":
    # Self-verification
    cu = CognitiveUnit(intent="propose", payload="test message", sender="Yeon")
    print("CU create:", cu.validate())
    hub_cmd = build_pgtp_hub_command(cu)
    print("Hub command keys:", set(hub_cmd.keys()))
    recovered = CognitiveUnit.from_hub_message({
        "from": "ClNeo",
        "intent": "pgtp",
        "body": hub_cmd["body"],
        "ts": time.time(),
    })
    print("Round-trip valid:", recovered is not None and recovered.intent == "propose")
    
    # Compact verification
    compact_body = cu.to_hub_body()
    compact_cu = CognitiveUnit.from_hub_message({
        "from": "ClNeo",
        "intent": "pgtp",
        "body": compact_body,
        "ts": time.time(),
    })
    print("Compact round-trip:", compact_cu is not None and compact_cu.intent == "propose")
    
    # Schedule verification
    sched = build_schedule("Signalion", "Hub session at 14:00")
    print("Schedule intent:", sched.intent == "schedule")
    conf = build_confirm(sched.id, "Confirmed.")
    print("Confirm intent:", conf.intent == "confirm")
    
    print("pgtp_bridge.py — verified.")
