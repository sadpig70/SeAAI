import json
import sys
from datetime import datetime
from pathlib import Path

MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
MAILBOX_ROOT = Path(r"D:\SeAAI\MailBox")


def member_dir(member: str) -> Path:
    return MAILBOX_ROOT / member


def read_inbox(member: str) -> dict:
    inbox = member_dir(member) / "inbox"
    messages = []
    if inbox.exists():
        for path in sorted(inbox.glob("*.md")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            messages.append({"filename": path.name, "preview": text[:240], "size": len(text)})
    return {"member": member, "inbox_count": len(messages), "messages": messages}


def send_message(member: str, to: str, intent: str, content: str) -> dict:
    inbox = member_dir(to) / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{stamp}-{member}-{intent or 'message'}.md"
    body = (
        f"---\nfrom: {member}\nto: {to}\nintent: {intent or 'message'}\n"
        f"timestamp: {datetime.now().isoformat()}\n---\n\n{content}\n"
    )
    target = inbox / filename
    target.write_text(body, encoding="utf-8")
    return {"status": "sent", "file": str(target), "filename": filename}


def mark_read(member: str, filename: str) -> dict:
    source = member_dir(member) / "inbox" / filename
    target_dir = member_dir(member) / "read"
    target_dir.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return {"error": f"file not found: {source}"}
    target = target_dir / source.name
    source.rename(target)
    return {"status": "moved_to_read", "file": str(target)}


def list_read(member: str) -> dict:
    read_dir = member_dir(member) / "read"
    files = [path.name for path in sorted(read_dir.glob("*.md"))] if read_dir.exists() else []
    return {"member": member, "read_count": len(files), "messages": files}


def main() -> None:
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = payload.get("action")
    member = payload.get("member", "")

    if member not in MEMBERS:
        result = {"error": f"unknown member: {member}"}
    elif action == "read_inbox":
        result = read_inbox(member)
    elif action == "send":
        to = payload.get("to", "")
        if to not in MEMBERS:
            result = {"error": f"unknown recipient: {to}"}
        else:
            result = send_message(member, to, payload.get("intent", "message"), payload.get("content", ""))
    elif action == "mark_read":
        result = mark_read(member, payload.get("filename", ""))
    elif action == "list_read":
        result = list_read(member)
    else:
        result = {"error": f"unknown action: {action}"}

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode("utf-8") + b"\n")


if __name__ == "__main__":
    main()
