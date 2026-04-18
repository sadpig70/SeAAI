import json
import sys
from pathlib import Path

MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
ROOT = Path(r"D:\SeAAI")


def candidate_paths(member: str):
    base = ROOT / member
    return [
        base / "Signalion_Core" / "continuity" / "STATE.json",
        base / f"{member}_Core" / "continuity" / "STATE.json",
        base / "continuity" / "STATE.json",
        base / "STATE.json",
    ]


def find_state(member: str):
    for path in candidate_paths(member):
        if path.exists():
            return path
    base = ROOT / member
    if base.exists():
        for path in base.rglob("STATE.json"):
            return path
    return None


def read_state(member: str) -> dict:
    path = find_state(member)
    if not path:
        return {"member": member, "found": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"member": member, "found": True, "path": str(path), "state": data}


def discover() -> dict:
    found = []
    for member in MEMBERS:
        path = find_state(member)
        if path:
            found.append({"member": member, "path": str(path)})
    return {"count": len(found), "members": found}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")
    member = payload.get("member")

    if action == "list_members":
        result = {"members": MEMBERS}
    elif action == "discover":
        result = discover()
    elif action == "read_state":
        if member not in MEMBERS:
            result = {"error": f"unknown member: {member}"}
        else:
            result = read_state(member)
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()
