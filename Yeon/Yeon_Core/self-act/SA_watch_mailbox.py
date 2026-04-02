"""
SA_watch_mailbox — Auto-scan and process Yeon's MailBox inbox.
Input: None
Output: list of processed mail metadata
"""
import re
from pathlib import Path
from typing import List, Dict, Optional

MAILBOX_INBOX = Path("D:/SeAAI/MailBox/Yeon/inbox")
MAILBOX_READ = Path("D:/SeAAI/MailBox/Yeon/read")


def parse_frontmatter(content: str) -> Optional[Dict]:
    """Parse YAML-like frontmatter from MailBox markdown."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    fm_text = parts[1].strip()
    meta = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta


def scan_inbox() -> List[Path]:
    MAILBOX_INBOX.mkdir(parents=True, exist_ok=True)
    return sorted(MAILBOX_INBOX.glob("*.md"))


def move_to_read(path: Path) -> Path:
    MAILBOX_READ.mkdir(parents=True, exist_ok=True)
    dest = MAILBOX_READ / path.name
    path.replace(dest)
    return dest


def generate_ack(meta: Dict) -> str:
    sender = meta.get("from", "Unknown")
    mail_id = meta.get("id", "unknown")
    return f"ACK: {mail_id} from {sender} received and processed by Yeon."


def process_mailbox() -> List[Dict]:
    """Scan, read, move, and acknowledge all pending mails."""
    mails = scan_inbox()
    processed = []
    for path in mails:
        content = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        if meta:
            ack = generate_ack(meta)
            dest = move_to_read(path)
            processed.append({
                "original": path.name,
                "moved_to": str(dest),
                "from": meta.get("from", "Unknown"),
                "id": meta.get("id", ""),
                "ack": ack,
            })
        else:
            # No frontmatter — move anyway to avoid loop
            dest = move_to_read(path)
            processed.append({
                "original": path.name,
                "moved_to": str(dest),
                "from": "Unknown",
                "id": "",
                "ack": "ACK: non-formatted mail received.",
            })
    return processed


def main():
    results = process_mailbox()
    print(f"SA_watch_mailbox: processed {len(results)} mail(s)")
    for r in results:
        print(f"  [{r['from']}] {r['original']} -> read/")


if __name__ == "__main__":
    main()
