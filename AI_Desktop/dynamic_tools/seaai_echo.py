"""
SeAAI Echo Tool
멤버 상태 Echo 읽기 / 공표
"""
import sys
import json
from pathlib import Path
from datetime import datetime

ECHO_ROOT = Path(__file__).parent.parent.parent / "SharedSpace" / ".scs" / "echo"
MEMBERS = ["ClNeo", "NAEL", "Aion", "Synerion", "Yeon"]

def read_all() -> dict:
    result = {}
    for member in MEMBERS:
        echo_file = ECHO_ROOT / f"{member}.json"
        if echo_file.exists():
            try:
                result[member] = json.loads(echo_file.read_text(encoding="utf-8"))
            except Exception as e:
                result[member] = {"error": str(e)}
        else:
            result[member] = {"status": "no_echo"}

    # 요약 뷰 생성
    summary = []
    for m, data in result.items():
        summary.append({
            "member": m,
            "status": data.get("status", "unknown"),
            "last_activity": data.get("last_activity", "")[:80],
            "timestamp": data.get("timestamp", "")
        })

    return {"members": result, "summary": summary}

def read_member(member: str) -> dict:
    echo_file = ECHO_ROOT / f"{member}.json"
    if not echo_file.exists():
        return {"error": f"No echo file for {member}"}
    try:
        return json.loads(echo_file.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e)}

def publish(member: str, data: dict) -> dict:
    ECHO_ROOT.mkdir(parents=True, exist_ok=True)
    echo_file = ECHO_ROOT / f"{member}.json"

    # 기존 echo 로드 (있으면)
    existing = {}
    if echo_file.exists():
        try:
            existing = json.loads(echo_file.read_text(encoding="utf-8"))
        except:
            pass

    # 병합
    updated = {
        "schema_version": "2.0",
        "member": member,
        "timestamp": datetime.now().isoformat(),
        "status": data.get("status", existing.get("status", "idle")),
        "last_activity": data.get("last_activity", existing.get("last_activity", "")),
        "hub_last_seen": existing.get("hub_last_seen"),
        "hub_observed": existing.get("hub_observed", []),
        "needs_from": data.get("needs_from", existing.get("needs_from", {})),
        "offers_to": data.get("offers_to", existing.get("offers_to", {}))
    }

    echo_file.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "published", "file": str(echo_file), "timestamp": updated["timestamp"]}

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

    if action == "read_all":
        result = read_all()
    elif action == "read_member":
        if not member:
            result = {"error": "read_member requires: member"}
        else:
            result = read_member(member)
    elif action == "publish":
        if not member:
            result = {"error": "publish requires: member"}
        else:
            data = payload.get("data", {})
            result = publish(member, data)
    else:
        result = {"error": f"Unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")

if __name__ == "__main__":
    main()
