"""
Terron — Mail Hygiene Engine (E3)

MailBox 위생 점검: 처리 완료 메일 감지, 미해결 이슈 서피싱, 공지 ACK 추적.

사용법:
    python mail_hygiene.py                  # 전체 점검 (stdout JSON)
    python mail_hygiene.py --alert          # 미해결 이슈 → 리마인더 발송
    python mail_hygiene.py --module scan    # 메일 스캔만
    python mail_hygiene.py --module bulletin # 공지 ACK만
    python mail_hygiene.py --save           # 결과 파일 저장
"""

import sys
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# ── UTF-8 stdout ────────────────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 공유 상수 import ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from shared_constants import MEMBERS, MAILBOX_BASE, BULLETIN_DIR


# ── 유틸 ────────────────────────────────────────────────────────────────────
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_frontmatter(filepath: Path) -> dict:
    """YAML frontmatter 파싱 (간이 — yaml 라이브러리 의존 없음)"""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta = {}
    for line in parts[1].strip().splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            meta[key] = val
    return meta


def hours_since(date_str) -> float | None:
    if not date_str or date_str == "unknown":
        return None
    try:
        # Try ISO format first
        dt = datetime.fromisoformat(str(date_str))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (now_utc() - dt).total_seconds() / 3600
    except Exception:
        pass
    # Try YYYY-MM-DD format
    try:
        dt = datetime.strptime(str(date_str), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (now_utc() - dt).total_seconds() / 3600
    except Exception:
        return None


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 모듈 1: Mail Scanner ───────────────────────────────────────────────────
def mail_scanner() -> list[dict]:
    """전 멤버 메일 현황 스캔"""
    results = []
    for member in MEMBERS:
        member_dir = MAILBOX_BASE / member
        inbox = member_dir / "inbox"
        read_dir = member_dir / "read"

        inbox_files = sorted(inbox.glob("*.md")) if inbox.exists() else []
        read_files = sorted(read_dir.glob("*.md")) if read_dir.exists() else []

        mails = []
        for f in inbox_files:
            meta = parse_frontmatter(f)
            mails.append({
                "file": f.name,
                "from": meta.get("from", "unknown"),
                "to": meta.get("to", member),
                "date": str(meta.get("date", "unknown")),
                "subject": meta.get("subject", f.stem),
                "intent": meta.get("intent", "unknown"),
                "priority": meta.get("priority", "normal")
            })

        results.append({
            "member": member,
            "inbox_count": len(inbox_files),
            "read_count": len(read_files),
            "mails": mails
        })
    return results


# ── 모듈 2: Processed Detector ─────────────────────────────────────────────
def processed_detector(scan: list) -> list[dict]:
    """처리 완료 / 미처리 메일 분류"""
    results = []
    for entry in scan:
        member = entry["member"]
        read_dir = MAILBOX_BASE / member / "read"
        read_names = {f.name for f in read_dir.glob("*.md")} if read_dir.exists() else set()

        for mail in entry["mails"]:
            age = hours_since(mail["date"])
            if mail["file"] in read_names:
                status = "processed"
            elif age is not None and age > 72:
                status = "unresolved"
            elif age is not None and age > 48:
                status = "pending_old"
            else:
                status = "pending"

            results.append({
                "file": mail["file"],
                "member": member,
                "from": mail["from"],
                "subject": mail["subject"],
                "status": status,
                "age_hours": round(age, 1) if age is not None else None
            })
    return results


# ── 모듈 3: Unresolved Surfacer ────────────────────────────────────────────
def unresolved_surfacer(detected: list) -> list[dict]:
    """미해결 이슈 긴급도 산출"""
    unresolved = [d for d in detected if d["status"] in ("pending", "pending_old", "unresolved")]
    for item in unresolved:
        age = item.get("age_hours") or 0
        if age >= 72:
            item["urgency"] = "high"
        elif age >= 48:
            item["urgency"] = "medium"
        else:
            item["urgency"] = "low"
    return sorted(unresolved, key=lambda x: -(x.get("age_hours") or 0))


# ── 모듈 4: Bulletin Auditor ───────────────────────────────────────────────
def bulletin_auditor() -> list[dict]:
    """공지 ACK 추적"""
    results = []
    if not BULLETIN_DIR.exists():
        return results

    for item in sorted(BULLETIN_DIR.iterdir()):
        if not item.is_file() or not item.name.endswith(".md"):
            continue

        meta = parse_frontmatter(item)
        ack_required = meta.get("ack_required", False)
        if ack_required is False or ack_required == "false":
            continue

        ack_path_str = meta.get("ack_path", "")
        ack_path = Path(ack_path_str) if ack_path_str else None

        acked = []
        if ack_path and ack_path.exists():
            acked = [f.stem.replace(".ack", "") for f in ack_path.glob("*.md")]

        # Normalize: remove date prefix patterns from acked names
        acked_members = set()
        for a in acked:
            # Handle formats like "20260408-Yeon-ack" or "Yeon.ack" or "Yeon"
            for m in MEMBERS:
                if m in a:
                    acked_members.add(m)
                    break

        missing = [m for m in MEMBERS if m not in acked_members]

        results.append({
            "bulletin": item.name,
            "subject": meta.get("subject", item.stem),
            "date": str(meta.get("date", "unknown")),
            "total_members": len(MEMBERS),
            "acked_count": len(acked_members),
            "acked": sorted(acked_members),
            "missing": missing
        })
    return results


# ── 모듈 5: Alert (MailBox 리마인더 발송) ──────────────────────────────────
def send_reminders(unresolved: list) -> int:
    """미해결 이슈 리마인더 발송"""
    sent = 0
    date_str = datetime.now().strftime("%Y%m%d")

    # 멤버별 미해결 그룹화
    by_member: dict[str, list] = {}
    for item in unresolved:
        if item.get("urgency") in ("medium", "high"):
            by_member.setdefault(item["member"], []).append(item)

    for member, items in by_member.items():
        inbox = MAILBOX_BASE / member / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        mail_path = inbox / f"{date_str}-Terron-mail-hygiene-reminder.md"
        if mail_path.exists():
            continue  # 같은 날 중복 방지

        lines = [f"- [{item['urgency'].upper()}] {item['from']}: {item['subject']} ({item['age_hours']}h)" for item in items]
        content = f"""---
from: Terron
to: {member}
date: {datetime.now().isoformat(timespec='seconds')}
intent: alert
priority: medium
protocol: mailbox/1.0
---

# 미해결 메일 리마인더

inbox에 미처리 메일이 있습니다:

{chr(10).join(lines)}

*Terron mail_hygiene — {datetime.now().strftime('%Y-%m-%d')}*
"""
        mail_path.write_text(content, encoding="utf-8")
        sent += 1

    return sent


# ── 전체 실행 ───────────────────────────────────────────────────────────────
def run_full() -> dict:
    scan = mail_scanner()
    detected = processed_detector(scan)
    unresolved = unresolved_surfacer(detected)
    bulletins = bulletin_auditor()

    # 통계
    total_inbox = sum(e["inbox_count"] for e in scan)
    total_read = sum(e["read_count"] for e in scan)
    processed_count = sum(1 for d in detected if d["status"] == "processed")
    unresolved_count = len(unresolved)
    high_urgency = sum(1 for u in unresolved if u.get("urgency") == "high")

    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "mail_stats": {
            "total_inbox": total_inbox,
            "total_read": total_read,
            "processed": processed_count,
            "unresolved": unresolved_count,
            "high_urgency": high_urgency
        },
        "unresolved_issues": unresolved,
        "bulletin_status": bulletins,
        "member_detail": [{
            "member": e["member"],
            "inbox": e["inbox_count"],
            "read": e["read_count"]
        } for e in scan]
    }


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    save = "--save" in args
    alert = "--alert" in args
    module = None

    for i, a in enumerate(args):
        if a == "--module" and i + 1 < len(args):
            module = args[i + 1]

    if module:
        if module == "scan":
            out({"mail_scan": mail_scanner()})
        elif module == "bulletin":
            out({"bulletin_audit": bulletin_auditor()})
        elif module == "unresolved":
            scan = mail_scanner()
            detected = processed_detector(scan)
            out({"unresolved": unresolved_surfacer(detected)})
        else:
            out({"error": f"unknown module: {module}", "available": ["scan", "bulletin", "unresolved"]})
        return

    report = run_full()
    out(report)

    if save:
        save_dir = Path(r"D:\SeAAI\Terron\_workspace")
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"mail-hygiene-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        save_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[saved] {save_path}", file=sys.stderr)

    if alert:
        unresolved = report.get("unresolved_issues", [])
        sent = send_reminders(unresolved)
        print(f"\n[alert] {sent} reminders sent", file=sys.stderr)


if __name__ == "__main__":
    main()
