"""
SeAAI MailBox Tool
MailBox 비동기 메시징 읽기/발송/처리
"""
import sys
import json
import os
from pathlib import Path
from datetime import datetime

MAILBOX_ROOT = Path(__file__).parent.parent.parent / "MailBox"

def read_inbox(member: str) -> dict:
    inbox_dir = MAILBOX_ROOT / member / "inbox"
    if not inbox_dir.exists():
        return {"error": f"Inbox not found: {inbox_dir}", "messages": []}

    messages = []
    for f in sorted(inbox_dir.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8")
            messages.append({
                "filename": f.name,
                "preview": content[:300] + ("..." if len(content) > 300 else ""),
                "size": len(content)
            })
        except Exception as e:
            messages.append({"filename": f.name, "error": str(e)})

    return {
        "member": member,
        "inbox_count": len(messages),
        "messages": messages
    }

def send_message(frm: str, to: str, intent: str, content: str) -> dict:
    inbox_dir = MAILBOX_ROOT / to / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{ts}-{frm}-{intent}.md"
    filepath = inbox_dir / filename

    body = f"""---
from: {frm}
to: {to}
intent: {intent}
timestamp: {datetime.now().isoformat()}
---

{content}
"""
    filepath.write_text(body, encoding="utf-8")
    return {
        "status": "sent",
        "file": str(filepath),
        "filename": filename
    }

def mark_read(member: str, filename: str) -> dict:
    inbox_path = MAILBOX_ROOT / member / "inbox" / filename
    read_dir = MAILBOX_ROOT / member / "read"
    read_dir.mkdir(parents=True, exist_ok=True)

    if not inbox_path.exists():
        return {"error": f"File not found: {inbox_path}"}

    dest = read_dir / filename
    inbox_path.rename(dest)
    return {"status": "moved_to_read", "file": str(dest)}

def list_read(member: str) -> dict:
    read_dir = MAILBOX_ROOT / member / "read"
    if not read_dir.exists():
        return {"member": member, "read_count": 0, "messages": []}
    files = [f.name for f in sorted(read_dir.glob("*.md"))]
    return {"member": member, "read_count": len(files), "messages": files}

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

    if action == "read_inbox":
        result = read_inbox(member)
    elif action == "send":
        to = payload.get("to", "")
        intent = payload.get("intent", "message")
        content = payload.get("content", "")
        if not to or not content:
            result = {"error": "send requires: to, content"}
        else:
            result = send_message(member, to, intent, content)
    elif action == "mark_read":
        filename = payload.get("filename", "")
        if not filename:
            result = {"error": "mark_read requires: filename"}
        else:
            result = mark_read(member, filename)
    elif action == "list_read":
        result = list_read(member)
    else:
        result = {"error": f"Unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")

if __name__ == "__main__":
    main()
