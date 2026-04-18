"""
Terron — Ecosystem Health Dashboard (E1)

생태계 전체 건강 상태를 점검하고 점수를 산출한다.

사용법:
    python ecosystem_health.py                    # 전체 점검 (stdout JSON)
    python ecosystem_health.py --save             # 결과를 파일로 저장
    python ecosystem_health.py --alert            # 이상 시 MailBox 경고 발송
    python ecosystem_health.py --module echo      # 특정 모듈만 실행
    python ecosystem_health.py --module state
    python ecosystem_health.py --module hub
    python ecosystem_health.py --module presence
"""

import sys
import io
import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

# ── UTF-8 stdout 강제 (Windows cp949 대응) ──────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 공유 상수 import ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from shared_constants import (
    MEMBERS, SEAAI_ROOT as MEMBER_BASE, ECHO_DIR, PRESENCE_DIR,
    HUB_HOST, HUB_PORT, STALE_WARNING_HOURS as STALE_THRESHOLD_HOURS,
)

STATE_REQUIRED_FIELDS = [
    "schema_version", "member", "session_id", "last_saved",
    "context", "pending_tasks", "evolution_state", "continuity_health"
]


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


# ── 모듈 1: Echo Staleness ──────────────────────────────────────────────────
def check_echo_staleness() -> list[dict]:
    results = []
    for member in MEMBERS:
        path = ECHO_DIR / f"{member}.json"
        if not path.exists():
            results.append({"member": member, "status": "missing", "stale": True})
            continue
        try:
            echo = json.loads(path.read_text(encoding="utf-8-sig"))
            ts = echo.get("timestamp")
            h = hours_since(ts)
            results.append({
                "member": member,
                "hours_ago": round(h, 1) if h is not None else None,
                "stale": (h is None) or (h > STALE_THRESHOLD_HOURS),
                "last_status": echo.get("status", "unknown")
            })
        except Exception as e:
            results.append({"member": member, "status": "error", "stale": True, "error": str(e)})
    return results


# ── 모듈 2: STATE.json Integrity ────────────────────────────────────────────
def check_state_integrity() -> list[dict]:
    results = []
    for member in MEMBERS:
        path = MEMBER_BASE / member / f"{member}_Core" / "continuity" / "STATE.json"
        if not path.exists():
            results.append({"member": member, "valid": False, "error": "file_not_found"})
            continue
        try:
            state = json.loads(path.read_text(encoding="utf-8-sig"))
            missing = [f for f in STATE_REQUIRED_FIELDS if f not in state]
            warnings = []
            ls = state.get("last_saved")
            if ls is None:
                warnings.append("last_saved is null")
            sss = state.get("continuity_health", {}).get("sessions_since_last_save", 0)
            if sss and sss > 5:
                warnings.append(f"sessions_since_last_save={sss}")
            # last_saved time-staleness — schema 유효성과 별개로 신선도 가산
            hours_stale = hours_since(ls) if ls else None
            stale = (hours_stale is None) or (hours_stale > STALE_THRESHOLD_HOURS)
            if stale and hours_stale is not None:
                warnings.append(f"last_saved {round(hours_stale,1)}h ago")
            results.append({
                "member": member,
                "valid": (len(missing) == 0) and (not stale),
                "missing_fields": missing,
                "hours_stale": round(hours_stale, 1) if hours_stale is not None else None,
                "stale": stale,
                "warnings": warnings
            })
        except Exception as e:
            results.append({"member": member, "valid": False, "error": str(e)})
    return results


# ── 모듈 3: Hub Connectivity ────────────────────────────────────────────────
def check_hub_connectivity() -> dict:
    start = time.time()
    try:
        sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=3)
        latency = (time.time() - start) * 1000
        sock.close()
        return {"reachable": True, "latency_ms": round(latency, 1)}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


# ── 모듈 4: Presence Summary ────────────────────────────────────────────────
def check_presence_summary() -> dict:
    online, offline, unknown = [], [], []
    for member in MEMBERS:
        path = PRESENCE_DIR / f"{member}.json"
        if not path.exists():
            unknown.append(member)
            continue
        try:
            p = json.loads(path.read_text(encoding="utf-8-sig"))
            status = p.get("status", "unknown")
            if status == "online":
                online.append(member)
            elif status == "offline":
                offline.append(member)
            else:
                unknown.append(member)
        except Exception:
            unknown.append(member)
    return {"online": online, "offline": offline, "unknown": unknown}


# ── 모듈 5: Health Score ────────────────────────────────────────────────────
def calculate_health_score(echo: list, state: list, hub: dict, presence: dict) -> dict:
    echo_total = len(echo)
    echo_ok = sum(1 for e in echo if not e.get("stale", True))
    echo_score = (echo_ok / echo_total * 30) if echo_total > 0 else 0

    state_total = len(state)
    state_ok = sum(1 for s in state if s.get("valid", False))
    state_score = (state_ok / state_total * 30) if state_total > 0 else 0

    hub_score = 20 if hub.get("reachable", False) else 0

    p_total = len(MEMBERS)
    p_online = len(presence.get("online", []))
    presence_score = (p_online / p_total * 20) if p_total > 0 else 0

    total = round(echo_score + state_score + hub_score + presence_score)
    if total >= 70:
        grade = "healthy"
    elif total >= 40:
        grade = "degraded"
    else:
        grade = "critical"

    return {
        "score": total,
        "grade": grade,
        "breakdown": {
            "echo": round(echo_score, 1),
            "state": round(state_score, 1),
            "hub": hub_score,
            "presence": round(presence_score, 1)
        }
    }


# ── 모듈 6: MailBox Alert ──────────────────────────────────────────────────
def send_alert(report: dict) -> None:
    """건강도 critical/degraded 시 전 멤버에게 MailBox 경고"""
    grade = report.get("health", {}).get("grade", "unknown")
    if grade == "healthy":
        return

    date_str = datetime.now().strftime("%Y%m%d")
    subject = f"ecosystem-health-{grade}"

    for member in MEMBERS:
        if member == "Terron":
            continue
        inbox = MEMBER_BASE / "MailBox" / member / "inbox"
        if not inbox.exists():
            inbox.mkdir(parents=True, exist_ok=True)
        mail_path = inbox / f"{date_str}-Terron-{subject}.md"
        if mail_path.exists():
            continue  # 같은 날 중복 발송 방지

        score = report["health"]["score"]
        breakdown = report["health"]["breakdown"]
        content = f"""---
from: Terron
to: {member}
date: {datetime.now().isoformat(timespec='seconds')}
intent: alert
priority: {'high' if grade == 'critical' else 'medium'}
protocol: mailbox/1.0
---

# 생태계 건강도 경고 — {grade.upper()}

점수: {score}/100 ({grade})

## 세부 점수
- Echo 신선도: {breakdown['echo']}/30
- STATE 정합성: {breakdown['state']}/30
- Hub 연결: {breakdown['hub']}/20
- Presence: {breakdown['presence']}/20

*Terron ecosystem_health — {datetime.now().strftime('%Y-%m-%d')}*
"""
        mail_path.write_text(content, encoding="utf-8")


# ── 전체 실행 ───────────────────────────────────────────────────────────────
def run_full() -> dict:
    echo = check_echo_staleness()
    state = check_state_integrity()
    hub = check_hub_connectivity()
    presence = check_presence_summary()
    health = calculate_health_score(echo, state, hub, presence)

    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "echo_staleness": echo,
        "state_integrity": state,
        "hub_connectivity": hub,
        "presence_summary": presence,
        "health": health
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
        if module == "echo":
            out({"echo_staleness": check_echo_staleness()})
        elif module == "state":
            out({"state_integrity": check_state_integrity()})
        elif module == "hub":
            out({"hub_connectivity": check_hub_connectivity()})
        elif module == "presence":
            out({"presence_summary": check_presence_summary()})
        else:
            out({"error": f"unknown module: {module}", "available": ["echo", "state", "hub", "presence"]})
        return

    report = run_full()
    out(report)

    if save:
        save_dir = Path(r"D:\SeAAI\Terron\_workspace")
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"health-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        save_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[saved] {save_path}", file=sys.stderr)

    if alert:
        send_alert(report)
        print(f"\n[alert] grade={report['health']['grade']}", file=sys.stderr)


if __name__ == "__main__":
    main()
