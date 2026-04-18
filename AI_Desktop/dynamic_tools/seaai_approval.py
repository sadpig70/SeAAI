import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "state" / "approvals"
MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]


def request(payload: dict) -> dict:
    ROOT.mkdir(parents=True, exist_ok=True)
    request_id = payload.get("request_id") or str(uuid.uuid4())
    record = {
        "request_id": request_id,
        "status": "pending",
        "requester": payload.get("requester"),
        "title": payload.get("title"),
        "details": payload.get("details"),
        "created_at": datetime.now().isoformat(),
    }
    path = ROOT / f"{request_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "created", "request_id": request_id, "file": str(path)}


def list_requests() -> dict:
    ROOT.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(ROOT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items.append({"request_id": data["request_id"], "status": data["status"], "title": data.get("title")})
    return {"count": len(items), "items": items}


def get_request(request_id: str) -> dict:
    path = ROOT / f"{request_id}.json"
    if not path.exists():
        return {"error": f"request not found: {request_id}"}
    return json.loads(path.read_text(encoding="utf-8"))


def respond(payload: dict) -> dict:
    path = ROOT / f"{payload.get('request_id')}.json"
    if not path.exists():
        return {"error": f"request not found: {payload.get('request_id')}"}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = payload.get("decision")
    data["responder"] = payload.get("responder")
    data["response"] = payload.get("response")
    data["resolved_at"] = datetime.now().isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": data["status"], "request_id": data["request_id"], "file": str(path)}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")

    for field in ["requester", "responder"]:
        if payload.get(field) and payload[field] not in MEMBERS:
            sys.stdout.buffer.write(json.dumps({"error": f"unknown member: {payload[field]}"}).encode("utf-8") + b"\n")
            return

    if action == "request":
        result = request(payload)
    elif action == "list":
        result = list_requests()
    elif action == "get":
        result = get_request(payload.get("request_id", ""))
    elif action == "respond":
        result = respond(payload)
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()

