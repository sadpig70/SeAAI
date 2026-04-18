"""
Terron — Stale Data Cycler (E4)

정체 데이터 감지 → 심각도 분류 → 경고 발행 → 건강도 게시.
감지만이 아닌 감지+교정 자기치유 루프.

사용법:
    python stale_cycler.py                    # 전체 순환 (stdout JSON)
    python stale_cycler.py --publish          # SharedSpace에 보고서 게시
    python stale_cycler.py --alert            # 경고 메일 발송
    python stale_cycler.py --module echo      # Echo staleness만
    python stale_cycler.py --module state     # STATE 정합성만
    python stale_cycler.py --module health    # 건강도 게시만
"""

import sys
import io
import json
from datetime import datetime, timezone
from pathlib import Path

# ── UTF-8 stdout (Windows cp949 대응) ──────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 공유 상수 import ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from shared_constants import (
    MEMBERS, SEAAI_ROOT, ECHO_DIR, PRESENCE_DIR, REPORTS_DIR,
    MAILBOX_BASE, WORKSPACE_DIR, HUB_HOST, HUB_PORT,
    STALE_WARNING_HOURS, STALE_CRITICAL_HOURS, STALE_DEAD_HOURS,
)


# ── 유틸 ────────────────────────────────────────────────────────────────────
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def hours_since(ts_str: str | None) -> float | None:
    if not ts_str:
        return None
    try:
        return (now_utc() - parse_iso(ts_str)).total_seconds() / 3600
    except Exception:
        return None


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 모듈 1: Echo Staleness 감지 + 분류 ────────────────────────────────────
def detect_echo_staleness() -> list[dict]:
    """Echo JSON의 staleness를 감지하고 심각도를 분류한다."""
    results = []
    for member in MEMBERS:
        path = ECHO_DIR / f"{member}.json"
        entry = {"member": member, "path": str(path)}

        if not path.exists():
            entry.update({"status": "missing", "severity": "dead",
                          "action": "Echo 파일 자체가 없음 — 해당 멤버 세션 기록 없음"})
            results.append(entry)
            continue

        try:
            echo = json.loads(path.read_text(encoding="utf-8-sig"))
            ts = echo.get("timestamp")
            h = hours_since(ts)

            if h is None:
                entry.update({"status": "no_timestamp", "severity": "critical",
                              "action": "timestamp 필드 없음 — Echo 형식 점검 필요"})
            elif h > STALE_DEAD_HOURS:
                entry.update({"status": "dead", "severity": "dead",
                              "hours_stale": round(h, 1),
                              "last_activity": echo.get("last_activity", "unknown"),
                              "action": f"{round(h)}h 정체 — 멤버 비활성 또는 종료 절차 미실행"})
            elif h > STALE_CRITICAL_HOURS:
                entry.update({"status": "critical", "severity": "critical",
                              "hours_stale": round(h, 1),
                              "last_activity": echo.get("last_activity", "unknown"),
                              "action": f"{round(h)}h 정체 — 세션 종료 후 미갱신 가능성"})
            elif h > STALE_WARNING_HOURS:
                entry.update({"status": "warning", "severity": "warning",
                              "hours_stale": round(h, 1),
                              "last_activity": echo.get("last_activity", "unknown"),
                              "action": "갱신 권장"})
            else:
                entry.update({"status": "fresh", "severity": "ok",
                              "hours_stale": round(h, 1),
                              "last_activity": echo.get("last_activity", "unknown")})
        except Exception as e:
            entry.update({"status": "error", "severity": "critical",
                          "error": str(e), "action": "Echo JSON 파싱 실패"})

        results.append(entry)
    return results


# ── 모듈 2: STATE.json Staleness 감지 ─────────────────────────────────────
def detect_state_staleness() -> list[dict]:
    """각 멤버 STATE.json의 staleness + 정합성 점검."""
    results = []
    required_fields = [
        "schema_version", "member", "session_id", "last_saved",
        "context", "pending_tasks", "evolution_state", "continuity_health"
    ]

    for member in MEMBERS:
        path = SEAAI_ROOT / member / f"{member}_Core" / "continuity" / "STATE.json"
        entry = {"member": member, "path": str(path)}

        if not path.exists():
            entry.update({"status": "missing", "severity": "dead",
                          "action": "STATE.json 없음 — 워크스페이스 미생성 또는 첫 세션 미완료"})
            results.append(entry)
            continue

        try:
            state = json.loads(path.read_text(encoding="utf-8-sig"))
            missing = [f for f in required_fields if f not in state]
            h = hours_since(state.get("last_saved"))

            integrity_issues = []
            if missing:
                integrity_issues.append(f"필수 필드 누락: {missing}")

            sss = state.get("continuity_health", {}).get("sessions_since_last_save", 0)
            if sss and sss > 3:
                integrity_issues.append(f"sessions_since_last_save={sss} (비정상)")

            # Staleness 판정
            if h is None:
                severity = "critical"
                status = "no_timestamp"
            elif h > STALE_DEAD_HOURS:
                severity = "dead"
                status = "dead"
            elif h > STALE_CRITICAL_HOURS:
                severity = "critical"
                status = "critical"
            elif h > STALE_WARNING_HOURS:
                severity = "warning"
                status = "warning"
            else:
                severity = "ok"
                status = "fresh"

            # 정합성 문제가 있으면 severity 격상
            if integrity_issues and severity == "ok":
                severity = "warning"
                status = "integrity_issue"

            entry.update({
                "status": status,
                "severity": severity,
                "hours_stale": round(h, 1) if h is not None else None,
                "missing_fields": missing,
                "integrity_issues": integrity_issues,
                "last_saved": state.get("last_saved"),
                "version": state.get("evolution_state", {}).get("current_version", "unknown"),
            })
            if severity not in ("ok",):
                entry["action"] = f"STATE {'정합성 오류' if integrity_issues else '갱신 필요'}"

        except Exception as e:
            entry.update({"status": "error", "severity": "critical",
                          "error": str(e), "action": "STATE.json 파싱 실패"})

        results.append(entry)
    return results


# ── 모듈 3: 종합 보고서 생성 ──────────────────────────────────────────────
def generate_report(echo_results: list, state_results: list) -> dict:
    """Echo + STATE 결과를 종합하여 생태계 순환 보고서 생성."""

    severity_order = {"dead": 4, "critical": 3, "warning": 2, "ok": 1}

    # 멤버별 종합 severity (Echo와 STATE 중 더 심각한 것)
    member_summary = []
    for member in MEMBERS:
        echo_entry = next((e for e in echo_results if e["member"] == member), {})
        state_entry = next((s for s in state_results if s["member"] == member), {})

        echo_sev = echo_entry.get("severity", "dead")
        state_sev = state_entry.get("severity", "dead")
        combined = max(echo_sev, state_sev, key=lambda x: severity_order.get(x, 0))

        member_summary.append({
            "member": member,
            "echo_severity": echo_sev,
            "state_severity": state_sev,
            "combined_severity": combined,
            "echo_hours": echo_entry.get("hours_stale"),
            "state_hours": state_entry.get("hours_stale"),
            "actions": [a for a in [echo_entry.get("action"), state_entry.get("action")] if a],
        })

    # 전체 통계
    fresh = sum(1 for m in member_summary if m["combined_severity"] == "ok")
    warning = sum(1 for m in member_summary if m["combined_severity"] == "warning")
    critical = sum(1 for m in member_summary if m["combined_severity"] == "critical")
    dead = sum(1 for m in member_summary if m["combined_severity"] == "dead")

    total = len(MEMBERS)
    circulation_score = round((fresh / total) * 100) if total > 0 else 0

    if circulation_score >= 70:
        grade = "flowing"        # 순환 원활
    elif circulation_score >= 40:
        grade = "sluggish"       # 순환 부진
    else:
        grade = "stagnant"       # 정체

    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "circulation": {
            "score": circulation_score,
            "grade": grade,
            "fresh": fresh,
            "warning": warning,
            "critical": critical,
            "dead": dead,
        },
        "member_summary": member_summary,
        "echo_detail": echo_results,
        "state_detail": state_results,
    }


# ── 모듈 4: SharedSpace 게시 ─────────────────────────────────────────────
def publish_report(report: dict) -> str:
    """보고서를 SharedSpace에 게시한다. Sevalon/NAEL 등이 즉시 참조 가능."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 최신 보고서 (항상 덮어씀 — 최신 스냅샷)
    latest_path = REPORTS_DIR / "stale_cycler_latest.json"
    latest_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 히스토리 (날짜별 보존)
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    history_path = REPORTS_DIR / f"stale_cycler_{date_str}.json"
    history_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # ecosystem_health 최신 요약도 함께 게시
    health_summary = {
        "timestamp": report["timestamp"],
        "source": "Terron/stale_cycler",
        "circulation": report["circulation"],
        "member_status": {
            m["member"]: m["combined_severity"]
            for m in report["member_summary"]
        },
    }
    health_path = REPORTS_DIR / "ecosystem_health_latest.json"
    health_path.write_text(
        json.dumps(health_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return str(latest_path)


# ── 모듈 5: 경고 메일 발송 ───────────────────────────────────────────────
def send_stale_alerts(report: dict) -> int:
    """critical/dead 멤버에게 경고 메일 발송."""
    sent = 0
    date_str = datetime.now().strftime("%Y%m%d")

    for entry in report["member_summary"]:
        member = entry["member"]
        severity = entry["combined_severity"]

        if severity not in ("critical", "dead") or member == "Terron":
            continue

        inbox = MAILBOX_BASE / member / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        mail_path = inbox / f"{date_str}-Terron-stale-data-alert.md"
        if mail_path.exists():
            continue  # 같은 날 중복 방지

        actions = "\n".join(f"- {a}" for a in entry["actions"]) if entry["actions"] else "- 상태 갱신 필요"
        echo_h = entry.get("echo_hours")
        state_h = entry.get("state_hours")
        echo_info = f"{echo_h}h" if echo_h is not None else "N/A"
        state_info = f"{state_h}h" if state_h is not None else "N/A"

        content = f"""---
from: Terron
to: {member}
date: {datetime.now().isoformat(timespec='seconds')}
intent: alert
priority: {'high' if severity == 'dead' else 'medium'}
protocol: mailbox/1.0
---

# Stale Data 경고 — {severity.upper()}

{member}의 생태계 데이터가 정체되어 있습니다.

- Echo staleness: {echo_info} (severity: {entry['echo_severity']})
- STATE staleness: {state_info} (severity: {entry['state_severity']})

## 권고 조치
{actions}

다음 세션에서 정상 종료 절차를 실행하면 자동 갱신됩니다.

*Terron stale_cycler E4 — {datetime.now().strftime('%Y-%m-%d')}*
"""
        mail_path.write_text(content, encoding="utf-8")
        sent += 1

    return sent


# ── 전체 순환 ─────────────────────────────────────────────────────────────
def run_full() -> dict:
    echo_results = detect_echo_staleness()
    state_results = detect_state_staleness()
    report = generate_report(echo_results, state_results)
    return report


# ── CLI ───────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    publish = "--publish" in args
    alert = "--alert" in args
    save = "--save" in args
    module = None

    for i, a in enumerate(args):
        if a == "--module" and i + 1 < len(args):
            module = args[i + 1]

    if module:
        if module == "echo":
            out({"echo_staleness": detect_echo_staleness()})
        elif module == "state":
            out({"state_staleness": detect_state_staleness()})
        elif module == "health":
            report = run_full()
            publish_report(report)
            out({"published": True, "circulation": report["circulation"]})
        else:
            out({"error": f"unknown module: {module}",
                 "available": ["echo", "state", "health"]})
        return

    report = run_full()
    out(report)

    if publish:
        path = publish_report(report)
        print(f"\n[published] {path}", file=sys.stderr)

    if alert:
        sent = send_stale_alerts(report)
        print(f"\n[alert] {sent} alerts sent", file=sys.stderr)

    if save:
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        save_path = WORKSPACE_DIR / f"stale-cycle-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        save_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[saved] {save_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
