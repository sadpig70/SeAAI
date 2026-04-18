import json
import sys
from datetime import datetime
from pathlib import Path

MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
ECHO_ROOT = Path(__file__).resolve().parents[1] / "state" / "echo"


def read_echo(member: str) -> dict:
    path = ECHO_ROOT / f"{member}.md"
    if not path.exists():
        return {"member": member, "exists": False}
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {"member": member, "exists": True, "content": text}


def publish_echo(member: str, message: str) -> dict:
    ECHO_ROOT.mkdir(parents=True, exist_ok=True)
    path = ECHO_ROOT / f"{member}.md"
    body = f"timestamp: {datetime.now().isoformat()}\nmember: {member}\n\n{message}\n"
    path.write_text(body, encoding="utf-8")
    return {"status": "published", "file": str(path)}


def list_echo() -> dict:
    ECHO_ROOT.mkdir(parents=True, exist_ok=True)
    files = [path.name for path in sorted(ECHO_ROOT.glob("*.md"))]
    return {"count": len(files), "files": files}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")
    member = payload.get("member")

    if action in {"read", "publish"} and member not in MEMBERS:
        result = {"error": f"unknown member: {member}"}
    elif action == "read":
        result = read_echo(member)
    elif action == "publish":
        result = publish_echo(member, payload.get("message", ""))
    elif action == "list":
        result = list_echo()
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()

