"""Compact wire format encoder for PGTP v1.0."""
import json
from dataclasses import asdict

_SHORT = {
    "pgtp": "v", "id": "i", "sender": "s", "intent": "n", "target": "t",
    "payload": "p", "context": "c", "thread": "th", "accept": "a",
    "status": "st", "pipeline": "pl", "parallel": "pa",
    "urgency": "u", "ttl": "tl", "ts": "ts",
}

_DEFAULTS = {
    "target": "", "thread": "main", "accept": "", "status": "pending",
    "pipeline": [], "parallel": [], "urgency": 0, "ttl": 0, "ts": 0.0,
}


def encode(cu) -> str:
    """Encode CognitiveUnit to compact JSON string."""
    d = {}
    full = asdict(cu)
    for key, val in full.items():
        if key in _DEFAULTS and val == _DEFAULTS[key]:
            continue
        short = _SHORT.get(key, key)
        d[short] = val
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"))
