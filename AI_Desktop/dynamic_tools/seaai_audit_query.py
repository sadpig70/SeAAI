import json
import sys
from pathlib import Path

AUDIT_PATH = Path(__file__).resolve().parents[1] / "logs" / "audit.ndjson"


def load_entries():
    if not AUDIT_PATH.exists():
        return []
    entries = []
    for line in AUDIT_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")
    limit = int(payload.get("limit", 20))
    entries = load_entries()

    if action == "list_recent":
        result = {"count": min(limit, len(entries)), "entries": entries[-limit:]}
    elif action == "by_actor":
        actor = payload.get("actor", "")
        filtered = [entry for entry in entries if entry.get("actor") == actor]
        result = {"count": min(limit, len(filtered)), "entries": filtered[-limit:]}
    elif action == "by_tool":
        tool = payload.get("tool", "")
        filtered = [entry for entry in entries if entry.get("tool") == tool]
        result = {"count": min(limit, len(filtered)), "entries": filtered[-limit:]}
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()
