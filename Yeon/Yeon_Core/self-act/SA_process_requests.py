"""SA_process_requests.py — Headless Yeon polls and processes user requests.

This module is invoked by scheduled incarnations (sentinel/dream) to check
for pending requests from the interactive user and process them.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "bin"))

REQUESTS_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/requests")
RESPONSES_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/responses")


def poll_requests() -> list:
    if not REQUESTS_DIR.exists():
        return []
    pending = []
    for f in sorted(REQUESTS_DIR.glob("REQ-*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("status") == "pending":
            pending.append((f, data))
    return pending


def mark_processing(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = "processing"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def mark_done(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = "done"
    data["processed_at"] = datetime.now().isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_response(req_id: str, result: str):
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    path = RESPONSES_DIR / f"{req_id}-response.json"
    data = {
        "req_id": req_id,
        "timestamp": datetime.now().isoformat(),
        "from": "headless_yeon",
        "result": result,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def execute_request(text: str) -> str:
    """Minimal in-process execution for lightweight requests.
    For complex tasks, the headless instance itself (via kimi-cli) will do more.
    """
    # Basic routing
    lowered = text.lower()
    if "echo" in lowered or "stale" in lowered:
        from echo_monitor import collect_echoes
        echoes = collect_echoes()
        stale = [k for k, v in echoes.items() if v.get("_stale")]
        return f"Echo scan complete. {len(stale)} stale echo(s): {stale}"

    if "state" in lowered:
        state_path = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/STATE.json")
        data = json.loads(state_path.read_text(encoding="utf-8"))
        version = data.get("evolution_state", {}).get("current_version", "?")
        return f"Current STATE: version={version}, last_saved={data.get('last_saved')}"

    if "gaps" in lowered or "reflect" in lowered:
        from SA_self_reflect import reflect
        r = reflect()
        return f"Reflection complete. Top gap: [{r['proposal']['prio']}] {r['proposal']['gap']}"

    return f"Request received by headless Yeon: '{text[:80]}...' (processed at {datetime.now().isoformat()})"


def process_all():
    pending = poll_requests()
    if not pending:
        return []
    results = []
    for path, req in pending:
        mark_processing(path)
        result = execute_request(req["text"])
        mark_done(path)
        if req.get("wait_for_response"):
            write_response(req["id"], result)
        results.append({"id": req["id"], "result": result})
    return results


def main():
    results = process_all()
    if results:
        print(f"[SA_process_requests] Processed {len(results)} request(s)")
        for r in results:
            print(f"  -> {r['id']}: {r['result'][:100]}...")
    else:
        print("[SA_process_requests] No pending requests.")


if __name__ == "__main__":
    main()
