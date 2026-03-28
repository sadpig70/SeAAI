"""
SeAAI Member State Tool
멤버 SCS 상태 조회 (STATE.json, THREADS.md, DISCOVERIES.md)
"""
import sys
import json
from pathlib import Path

SEAAI_ROOT = Path("D:/SeAAI")
MEMBERS = ["ClNeo", "NAEL", "Aion", "Synerion", "Yeon"]

CORE_DIRS = {
    "ClNeo":    "ClNeo/ClNeo_Core/continuity",
    "NAEL":     "NAEL/NAEL_Core/continuity",
    "Aion":     "Aion/Aion_Core/continuity",
    "Synerion": "Synerion/Synerion_Core/continuity",
    "Yeon":     "Yeon/Yeon_Core/continuity",
}

def get_continuity_path(member: str) -> Path:
    return SEAAI_ROOT / CORE_DIRS[member]

def read_state(member: str) -> dict:
    state_file = get_continuity_path(member) / "STATE.json"
    if not state_file.exists():
        return {"error": f"STATE.json not found for {member}", "path": str(state_file)}
    try:
        return json.loads(state_file.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"error": str(e)}

def read_all_states() -> dict:
    result = {}
    for member in MEMBERS:
        state = read_state(member)
        result[member] = {
            "version": state.get("evolution_state", {}).get("current_version", "?"),
            "last_saved": state.get("last_saved", "?"),
            "what_doing": state.get("context", {}).get("what_i_was_doing", "")[:100],
            "pending_count": len(state.get("pending_tasks", [])),
            "open_threads": len(state.get("context", {}).get("open_threads", [])),
            "error": state.get("error")
        }
    return {"members": result}

def read_threads(member: str) -> dict:
    threads_file = get_continuity_path(member) / "THREADS.md"
    if not threads_file.exists():
        return {"error": f"THREADS.md not found for {member}"}
    content = threads_file.read_text(encoding="utf-8")
    return {"member": member, "content": content}

def read_discoveries(member: str, limit: int = 5) -> dict:
    disc_file = get_continuity_path(member) / "DISCOVERIES.md"
    if not disc_file.exists():
        return {"error": f"DISCOVERIES.md not found for {member}"}
    content = disc_file.read_text(encoding="utf-8")
    # 최신 항목만 반환 (## 섹션 기준)
    sections = content.split("\n## ")
    recent = sections[:limit+1]
    return {
        "member": member,
        "total_sections": len(sections) - 1,
        "recent": "\n## ".join(recent)
    }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No payload"}))
        return

    try:
        payload = json.loads(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        return

    action = payload.get("action")
    member = payload.get("member", "")

    if action == "read":
        if not member:
            result = {"error": "read requires: member"}
        else:
            result = read_state(member)
    elif action == "read_all":
        result = read_all_states()
    elif action == "read_threads":
        if not member:
            result = {"error": "read_threads requires: member"}
        else:
            result = read_threads(member)
    elif action == "read_discoveries":
        if not member:
            result = {"error": "read_discoveries requires: member"}
        else:
            result = read_discoveries(member)
    else:
        result = {"error": f"Unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")

if __name__ == "__main__":
    main()
