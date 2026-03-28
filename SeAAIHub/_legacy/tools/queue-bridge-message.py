#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Append a message to a SeAAIHub bridge outbox.")
    parser.add_argument("--bridge-dir", default="D:/SeAAI/SeAAIHub/.bridge/session")
    parser.add_argument("--sender", required=True)
    parser.add_argument("--to", nargs="+", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--intent", default="design")
    parser.add_argument("--message-id", default="")
    args = parser.parse_args()

    bridge_dir = Path(args.bridge_dir).resolve()
    bridge_dir.mkdir(parents=True, exist_ok=True)
    outbox = bridge_dir / f"outbox-{args.sender}.jsonl"
    payload = {
        "to": args.to,
        "intent": args.intent,
        "body": args.body,
    }
    if args.message_id:
        payload["id"] = args.message_id
    if not outbox.exists():
        outbox.write_text("", encoding="utf-8")
    with outbox.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
