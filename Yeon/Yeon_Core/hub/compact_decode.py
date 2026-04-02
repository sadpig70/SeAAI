"""Compact wire format decoder for PGTP v1.0."""
import json

_LONG = {
    "v": "pgtp", "i": "id", "s": "sender", "n": "intent", "t": "target",
    "p": "payload", "c": "context", "th": "thread", "a": "accept",
    "st": "status", "pl": "pipeline", "pa": "parallel",
    "u": "urgency", "tl": "ttl", "ts": "ts",
}


def decode(json_str: str, cu_class):
    """Decode compact JSON string to CognitiveUnit instance."""
    d = json.loads(json_str)
    expanded = {}
    for k, v in d.items():
        long_key = _LONG.get(k, k)
        if long_key in cu_class.__dataclass_fields__:
            expanded[long_key] = v
    return cu_class(**expanded)
