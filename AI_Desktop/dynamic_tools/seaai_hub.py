import json
import sys
from pathlib import Path

HUB_ROOT = Path(r"D:\SeAAI\SeAAIHub")


def latest_log():
    candidates = []
    for folder in [HUB_ROOT / "logs", HUB_ROOT]:
        if folder.exists():
            candidates.extend(folder.rglob("*.log"))
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def latest_protocol():
    candidates = list(HUB_ROOT.rglob("PROTOCOL*.md")) + list(HUB_ROOT.rglob("*protocol*.md"))
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def status() -> dict:
    protocol = latest_protocol()
    log = latest_log()
    return {
      "hub_root": str(HUB_ROOT),
      "exists": HUB_ROOT.exists(),
      "has_chatroom_src": (HUB_ROOT / "src" / "chatroom.rs").exists(),
      "latest_log": str(log) if log else None,
      "latest_protocol": str(protocol) if protocol else None
    }


def read_log(lines: int) -> dict:
    log = latest_log()
    if not log:
        return {"found": False}
    content = log.read_text(encoding="utf-8", errors="ignore").splitlines()
    return {"found": True, "path": str(log), "tail": content[-lines:]}


def read_protocol() -> dict:
    protocol = latest_protocol()
    if not protocol:
        return {"found": False}
    text = protocol.read_text(encoding="utf-8", errors="ignore")
    return {"found": True, "path": str(protocol), "preview": text[:4000]}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")

    if action == "status":
        result = status()
    elif action == "read_log":
        result = read_log(int(payload.get("lines", 80)))
    elif action == "read_protocol":
        result = read_protocol()
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()
