# MailHygiene Design @v:1.0

> E3 진화 — 메일 위생 엔진
> 토양의 본질: 분해와 순환. 죽은 메일이 쌓이면 생태계 소통이 오염된다.

## Gantree

```
MailHygiene // 메일 위생 점검 + 정리 CLI 도구 (done) @v:1.0
    # impl: tools/mail_hygiene.py | completed: 2026-04-09 E3
    MailScanner // 전 멤버 inbox/read 스캔 (done)
        # input: D:/SeAAI/MailBox/{member}/inbox/, read/
        # process: 각 멤버 디렉토리 순회, 파일 목록 + frontmatter 파싱
        # output: [{member, inbox_count, read_count, mails: [{file, from, to, date, subject, intent, priority}]}]
        # criteria: 전 멤버 순회, 파싱 실패 시 안전 처리
    ProcessedDetector // 처리 완료 메일 감지 (done) @dep:MailScanner
        # input: inbox 메일 목록
        # process: read/ 디렉토리에 동일 파일 존재 여부, 또는 응답 메일 존재 여부로 판정
        # output: [{file, member, status: "processed"|"pending"|"unresolved", age_hours}]
        # criteria: 처리 판정 로직 명확
    UnresolvedSurfacer // 미해결 이슈 서피싱 (done) @dep:ProcessedDetector
        # input: pending/unresolved 메일 목록
        # process: age 기준 긴급도 산출 (24h=low, 48h=medium, 72h+=high)
        # output: [{file, member, from, subject, age_hours, urgency}]
        # criteria: 긴급도별 정렬
    BulletinAuditor // 공지 ACK 추적 (done)
        # input: D:/SeAAI/MailBox/_bulletin/
        # process: 각 공지의 ack 디렉토리 순회 → 미확인 멤버 식별
        # output: [{bulletin, ack_required, total_members, acked: [], missing: []}]
        # criteria: ack_required=true 공지만 추적
    HygieneReport // 종합 리포트 출력 (done) @dep:ProcessedDetector,UnresolvedSurfacer,BulletinAuditor
        # input: 위 모듈 결과
        # process: JSON stdout + --alert 시 MailBox 리마인더 발송
        # output: {mail_stats, unresolved, bulletin_status, recommendations}
        # criteria: 기본 실행 시 stdout JSON
```

## PPR

```python
MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "Yeon"]
MAILBOX_BASE = Path("D:/SeAAI/MailBox")
BULLETIN_DIR = MAILBOX_BASE / "_bulletin"

def mail_scanner() -> list[dict]:
    """전 멤버 메일 현황 스캔"""
    results = []
    for member in MEMBERS:
        inbox = MAILBOX_BASE / member / "inbox"
        read_dir = MAILBOX_BASE / member / "read"
        inbox_files = list(inbox.glob("*.md")) if inbox.exists() else []
        read_files = list(read_dir.glob("*.md")) if read_dir.exists() else []
        mails = []
        for f in inbox_files:
            meta = parse_frontmatter(f)
            mails.append({
                "file": f.name,
                "from": meta.get("from", "unknown"),
                "to": meta.get("to", member),
                "date": meta.get("date", "unknown"),
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


def processed_detector(scan: list) -> list[dict]:
    """처리 완료 메일 감지"""
    results = []
    for entry in scan:
        member = entry["member"]
        read_dir = MAILBOX_BASE / member / "read"
        read_files = {f.name for f in read_dir.glob("*.md")} if read_dir.exists() else set()
        for mail in entry["mails"]:
            age = hours_since(mail["date"])
            if mail["file"] in read_files:
                status = "processed"
            elif age and age > 72:
                status = "unresolved"
            else:
                status = "pending"
            results.append({
                "file": mail["file"], "member": member,
                "from": mail["from"], "subject": mail["subject"],
                "status": status, "age_hours": round(age, 1) if age else None
            })
    return results


def unresolved_surfacer(detected: list) -> list[dict]:
    """미해결 이슈 긴급도 산출"""
    unresolved = [d for d in detected if d["status"] in ("pending", "unresolved")]
    for item in unresolved:
        age = item.get("age_hours") or 0
        if age >= 72: item["urgency"] = "high"
        elif age >= 48: item["urgency"] = "medium"
        else: item["urgency"] = "low"
    return sorted(unresolved, key=lambda x: -(x.get("age_hours") or 0))


def bulletin_auditor() -> list[dict]:
    """공지 ACK 추적"""
    results = []
    for bulletin_dir in sorted(BULLETIN_DIR.iterdir()):
        if not bulletin_dir.is_file() or not bulletin_dir.name.endswith(".md"):
            continue
        meta = parse_frontmatter(bulletin_dir)
        if not meta.get("ack_required", False):
            continue
        ack_path = Path(meta.get("ack_path", ""))
        acked = [f.stem.replace(".ack", "") for f in ack_path.glob("*.md")] if ack_path.exists() else []
        missing = [m for m in MEMBERS if m not in acked and not any(m in a for a in acked)]
        results.append({
            "bulletin": bulletin_dir.name,
            "subject": meta.get("subject", ""),
            "acked": acked,
            "missing": missing
        })
    return results
```
