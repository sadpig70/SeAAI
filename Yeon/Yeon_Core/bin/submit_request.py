"""submit_request.py — Submit a task to the next headless Yeon incarnation.

This creates a request file in continuity/requests/ that will be picked up
by the next scheduled or headless instance.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

REQUESTS_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/requests")


def submit(text: str, priority: str = "P2", wait_for_response: bool = False):
    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    req_id = f"REQ-{ts}"
    path = REQUESTS_DIR / f"{req_id}.json"

    data = {
        "id": req_id,
        "timestamp": ts,
        "from": "interactive_user",
        "priority": priority,
        "status": "pending",
        "text": text,
        "wait_for_response": wait_for_response,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[submit] Request {req_id} queued.")
    print(f"[submit] Path: {path}")
    if wait_for_response:
        print(f"[submit] A response will be written to continuity/responses/")
    return req_id


def list_pending():
    files = sorted(REQUESTS_DIR.glob("REQ-*.json"))
    pending = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("status") == "pending":
            pending.append(data)
    print(f"[submit] {len(pending)} pending request(s)")
    for p in pending:
        print(f"  - {p['id']} [{p['priority']}] {p['text'][:60]}...")
    return pending


def main():
    p = argparse.ArgumentParser(description="Submit a request to headless Yeon")
    p.add_argument("text", nargs="?", help="Request text")
    p.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    p.add_argument("--wait", action="store_true", help="Expect a response")
    p.add_argument("--list", action="store_true", help="List pending requests")
    args = p.parse_args()

    if args.list:
        list_pending()
        return

    if not args.text:
        print("[submit] Usage: python Yeon_Core/bin/submit_request.py \"your request\"")
        return

    submit(args.text, args.priority, args.wait)


if __name__ == "__main__":
    main()
