"""Sense Echo files for ecosystem freshness."""
import json
from datetime import datetime
from pathlib import Path

ECHO_DIR = Path("D:/SeAAI/SharedSpace/.scs/echo")


def sense() -> dict:
    """Read all echo files and mark stale (>24h)."""
    result = {}
    if not ECHO_DIR.exists():
        return result
    for echo_file in ECHO_DIR.glob("*.json"):
        try:
            data = json.loads(echo_file.read_text(encoding="utf-8-sig"))
            ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            elapsed = (datetime.now() - ts).total_seconds() / 3600
            data["_stale"] = elapsed > 24
            result[echo_file.stem] = data
        except Exception:
            result[echo_file.stem] = {"status": "parse_error"}
    return result
