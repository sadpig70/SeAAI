#!/usr/bin/env python3
"""
Ecosystem Pulse — SeAAI 생태계 맥박 측정기
Vera E1 진화 산출물. 생태계 전체 건강도를 정량 측정한다.

사용법:
  python ecosystem_pulse.py                    # 전체 측정 + 리포트 생성
  python ecosystem_pulse.py --json             # JSON만 stdout 출력
  python ecosystem_pulse.py --score-only       # 점수만 출력
"""

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 설정 ──────────────────────────────────────────────

SEAAI_ROOT = Path("D:/SeAAI")
ECHO_DIR = SEAAI_ROOT / "SharedSpace/.scs/echo"
MAILBOX_ROOT = SEAAI_ROOT / "MailBox"
REPORT_DIR = SEAAI_ROOT / "Vera/Vera_Core/reports"
HUB_PORT = 9900
MEMBERS = ["Aion", "ClNeo", "NAEL", "Synerion", "Vera", "Yeon"]

KST = timezone(timedelta(hours=9))

# ── 가중치 ─────────────────────────────────────────────

WEIGHTS = {
    "echo_activity": 25,
    "mailbox_rate": 20,
    "hub_status": 15,
    "scs_completeness": 20,
    "member_diversity": 20,
}

# ── EchoCollector ──────────────────────────────────────

def collect_echoes() -> dict:
    """Echo 파일 6개 수집·파싱."""
    echoes = {}
    for member in MEMBERS:
        path = ECHO_DIR / f"{member}.json"
        if path.exists():
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig")
                data = json.loads(text)
                echoes[member] = {
                    "exists": True,
                    "timestamp": data.get("timestamp", ""),
                    "status": data.get("status", "unknown"),
                    "last_activity": data.get("last_activity", ""),
                    "evolution": data.get("evolution", ""),
                    "needs_from": data.get("needs_from", {}),
                    "offers_to": data.get("offers_to", {}),
                }
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                echoes[member] = {"exists": True, "error": str(e)}
        else:
            echoes[member] = {"exists": False}
    return echoes


# ── MailBoxAnalyzer ────────────────────────────────────

def analyze_mailbox() -> dict:
    """멤버별 MailBox 처리율 계산."""
    stats = {}
    for member in MEMBERS:
        member_dir = MAILBOX_ROOT / member
        if not member_dir.exists():
            stats[member] = {"inbox": 0, "read": 0, "rate": 0.0, "exists": False}
            continue

        inbox = list((member_dir / "inbox").glob("*.md")) if (member_dir / "inbox").exists() else []
        read = list((member_dir / "read").glob("*.md")) if (member_dir / "read").exists() else []
        total = len(inbox) + len(read)
        rate = len(read) / total if total > 0 else 1.0  # 0/0 = 완전 처리로 간주

        stats[member] = {
            "inbox": len(inbox),
            "read": len(read),
            "total": total,
            "rate": round(rate, 2),
            "exists": True,
        }
    return stats


# ── HubStatusChecker ───────────────────────────────────

def check_hub() -> dict:
    """Hub 프로세스·포트 상태 확인."""
    # 포트 확인
    port_open = False
    try:
        with socket.create_connection(("127.0.0.1", HUB_PORT), timeout=1):
            port_open = True
    except (ConnectionRefusedError, OSError, TimeoutError):
        pass

    # 프로세스 확인
    process_running = False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq SeAAIHub.exe", "/FO", "CSV", "/NH"],
            capture_output=True, timeout=5
        )
        process_running = b"SeAAIHub.exe" in result.stdout
    except Exception:
        pass

    return {
        "port_open": port_open,
        "process_running": process_running,
        "port": HUB_PORT,
    }


# ── StalenessCalculator ───────────────────────────────

def calculate_staleness(echoes: dict, now: datetime) -> dict:
    """Echo 기준 멤버별 비활성 시간(시간 단위) 계산."""
    staleness = {}
    for member, echo in echoes.items():
        if not echo.get("exists") or echo.get("error") or not echo.get("timestamp"):
            staleness[member] = {"hours": 999, "status": "unknown"}
            continue
        try:
            ts_str = echo["timestamp"]
            # ISO 8601 파싱
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=KST)
            delta = now - ts
            hours = delta.total_seconds() / 3600
            staleness[member] = {
                "hours": round(hours, 1),
                "status": "fresh" if hours < 24 else "stale" if hours < 72 else "dead",
            }
        except (ValueError, TypeError):
            staleness[member] = {"hours": 999, "status": "parse_error"}
    return staleness


# ── HealthScorer ───────────────────────────────────────

def score_health(echoes: dict, mailbox: dict, hub: dict, staleness: dict) -> dict:
    """5개 차원 가중 합산으로 0-100 건강 점수 산출."""

    scores = {}

    # 1. Echo 활성도 (25점)
    fresh_count = sum(1 for s in staleness.values() if s["status"] == "fresh")
    scores["echo_activity"] = round((fresh_count / len(MEMBERS)) * WEIGHTS["echo_activity"])

    # 2. MailBox 처리율 (20점)
    rates = [m["rate"] for m in mailbox.values() if m.get("exists")]
    avg_rate = sum(rates) / len(rates) if rates else 0
    scores["mailbox_rate"] = round(avg_rate * WEIGHTS["mailbox_rate"])

    # 3. Hub 상태 (15점)
    hub_score = 0
    if hub["process_running"]:
        hub_score += 8
    if hub["port_open"]:
        hub_score += 7
    scores["hub_status"] = hub_score

    # 4. SCS 완전성 (20점)
    scs_count = 0
    for member in MEMBERS:
        has_echo = echoes.get(member, {}).get("exists", False) and not echoes.get(member, {}).get("error")
        if has_echo:
            scs_count += 1
    scores["scs_completeness"] = round((scs_count / len(MEMBERS)) * WEIGHTS["scs_completeness"])

    # 5. 멤버 다양성 (20점)
    existing = sum(1 for e in echoes.values() if e.get("exists"))
    scores["member_diversity"] = round((existing / len(MEMBERS)) * WEIGHTS["member_diversity"])

    total = sum(scores.values())
    grade = "HEALTHY" if total >= 80 else "MODERATE" if total >= 60 else "WEAK" if total >= 40 else "CRITICAL"

    return {
        "total": total,
        "grade": grade,
        "dimensions": scores,
        "weights": WEIGHTS,
    }


# ── ReportWriter ───────────────────────────────────────

def generate_report(score: dict, echoes: dict, mailbox: dict, hub: dict, staleness: dict, now: datetime) -> dict:
    """통합 리포트 dict 생성."""
    return {
        "report_type": "ecosystem_pulse",
        "version": "1.0",
        "generated_at": now.isoformat(),
        "generated_by": "Vera",
        "health": score,
        "echoes": echoes,
        "mailbox": mailbox,
        "hub": hub,
        "staleness": staleness,
    }


def write_report(report: dict, now: datetime) -> tuple:
    """JSON + Markdown 리포트 파일 생성. 반환: (json_path, md_path)."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = now.strftime("%Y%m%d-%H%M")

    # JSON
    json_path = REPORT_DIR / f"pulse-{date_str}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    h = report["health"]
    md_lines = [
        f"# Ecosystem Pulse — {now.strftime('%Y-%m-%d %H:%M')} KST",
        f"**Score: {h['total']}/100 ({h['grade']})**",
        "",
        "## 차원별 점수",
        "",
        "| 차원 | 점수 | 만점 |",
        "|------|------|------|",
    ]
    for dim, val in h["dimensions"].items():
        md_lines.append(f"| {dim} | {val} | {WEIGHTS[dim]} |")

    md_lines += ["", "## 멤버별 상태", "", "| 멤버 | Echo 갱신 | 비활성(h) | MailBox 처리율 |", "|------|----------|----------|--------------|"]
    for member in MEMBERS:
        echo = report["echoes"].get(member, {})
        stale = report["staleness"].get(member, {})
        mb = report["mailbox"].get(member, {})
        ts = echo.get("timestamp", "-")[:16] if echo.get("exists") else "없음"
        hours = f"{stale.get('hours', '?')}h"
        rate = f"{int(mb.get('rate', 0) * 100)}%" if mb.get("exists") else "-"
        md_lines.append(f"| {member} | {ts} | {hours} | {rate} |")

    hub_info = report["hub"]
    hub_str = "실행중" if hub_info["process_running"] and hub_info["port_open"] else "중지"
    md_lines += ["", f"## Hub: {hub_str} (port {hub_info['port']})", ""]
    md_lines.append(f"*Generated by Vera ecosystem_pulse.py v1.0*")

    md_path = REPORT_DIR / f"pulse-{date_str}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return json_path, md_path


# ── Main ───────────────────────────────────────────────

def main():
    now = datetime.now(KST)

    echoes = collect_echoes()
    mailbox = analyze_mailbox()
    hub = check_hub()
    staleness = calculate_staleness(echoes, now)
    score = score_health(echoes, mailbox, hub, staleness)
    report = generate_report(score, echoes, mailbox, hub, staleness, now)

    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    if "--score-only" in sys.argv:
        print(f"{score['total']}/100 ({score['grade']})")
        return

    json_path, md_path = write_report(report, now)
    print(f"Ecosystem Pulse: {score['total']}/100 ({score['grade']})")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")


if __name__ == "__main__":
    main()
