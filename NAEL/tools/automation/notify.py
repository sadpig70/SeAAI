#!/usr/bin/env python3
"""
NAEL 위협 알림 시스템 — Signalion DNA 흡수 + 안전 특화
원본: Signalion notify.py (toast/alert/ask + 7 템플릿)
확장: 위협 감지, 거부권 발동, 생태계 이상, 긴급 정지 알림

사용법:
    python notify.py toast "제목" "메시지"
    python notify.py threat "위협 내용" "상세"
    python notify.py veto "거부 대상" "사유"
    python notify.py emergency "긴급 상황"
"""
import ctypes
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("D:/SeAAI/NAEL/tools/automation/logs/notify-log.jsonl")
PWSH7 = r"D:\Tools\PS7\7\pwsh.exe"

MB_OK = 0x00000000
MB_YESNO = 0x00000004
MB_ICONINFO = 0x00000040
MB_ICONWARNING = 0x00000030
MB_ICONERROR = 0x00000010
MB_ICONQUESTION = 0x00000020
IDYES = 6


def log_notify(ntype: str, title: str, message: str, result: str = ""):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "type": ntype,
        "title": title,
        "message": message[:200],
        "result": result,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def toast(title: str, message: str, duration_ms: int = 5000):
    """작업 표시줄 토스트 알림 (비차단)"""
    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Warning
$balloon.BalloonTipTitle = '{title.replace("'", "''")}'
$balloon.BalloonTipText = '{message.replace("'", "''")}'
$balloon.BalloonTipIcon = 'Warning'
$balloon.Visible = $true
$balloon.ShowBalloonTip({duration_ms})
Start-Sleep -Seconds {max(duration_ms // 1000, 3)}
$balloon.Dispose()
"""
    subprocess.Popen(
        [PWSH7, "-NoProfile", "-Command", ps_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log_notify("toast", title, message)
    return True


def alert(title: str, message: str):
    """팝업 다이얼로그 (차단)"""
    ctypes.windll.user32.MessageBoxW(0, message, f"🛡️ NAEL — {title}", MB_OK | MB_ICONWARNING)
    log_notify("alert", title, message, "acknowledged")
    return True


def ask(title: str, question: str) -> bool:
    """예/아니오 다이얼로그 (차단)"""
    result = ctypes.windll.user32.MessageBoxW(0, question, f"🛡️ NAEL — {title}", MB_YESNO | MB_ICONQUESTION)
    answer = result == IDYES
    log_notify("ask", title, question, "YES" if answer else "NO")
    return answer


def emergency_alert(title: str, message: str):
    """긴급 팝업 (아이콘: 에러, 최고 우선)"""
    ctypes.windll.user32.MessageBoxW(0, message, f"🚨 NAEL EMERGENCY — {title}", MB_OK | MB_ICONERROR)
    log_notify("emergency", title, message, "acknowledged")
    return True


# === NAEL 보안 특화 템플릿 ===

def notify_threat_detected(threat_type: str, detail: str, level: str = "high"):
    """위협 감지 알림"""
    icon = {"critical": "🚨", "high": "🔴", "medium": "🟡", "low": "🟢"}
    prefix = icon.get(level, "⚠️")
    if level == "critical":
        return emergency_alert(
            "위협 감지",
            f"{prefix} 위협 수준: {level.upper()}\n\n"
            f"유형: {threat_type}\n"
            f"상세: {detail}\n\n"
            f"즉시 확인이 필요합니다."
        )
    return alert(
        "위협 감지",
        f"{prefix} 위협 수준: {level.upper()}\n\n"
        f"유형: {threat_type}\n"
        f"상세: {detail}"
    )


def notify_veto_invoked(target: str, reason: str) -> bool:
    """안전 거부권 발동 알림 (승인 요청)"""
    return ask(
        "안전 거부권 발동",
        f"NAEL이 안전 거부권(Rule 9)을 발동하려 합니다.\n\n"
        f"대상: {target}\n"
        f"사유: {reason}\n\n"
        f"거부권을 발동하시겠습니까?\n"
        f"(Rule 10: 최종 결정은 창조자)"
    )


def notify_ecosystem_anomaly(anomaly: str, members_affected: str):
    """생태계 이상 감지 알림"""
    return alert(
        "생태계 이상 감지",
        f"이상 내용: {anomaly}\n"
        f"영향 멤버: {members_affected}\n\n"
        f"NAEL이 모니터링 중입니다."
    )


def notify_security_filter_hit(source: str, findings_count: int, categories: str):
    """보안 필터 탐지 알림 (토스트 — 비차단)"""
    return toast(
        "보안 필터 탐지",
        f"출처: {source}\n탐지: {findings_count}건 ({categories})"
    )


def notify_gate_blocked(seed_id: str, reason: str):
    """TSG 게이트 차단 알림"""
    return alert(
        "TSG 게이트 차단",
        f"Seed ID: {seed_id}\n"
        f"차단 사유: {reason}\n\n"
        f"blocked 처리 완료. 피드백이 Signalion에 전달됩니다."
    )


# === CLI ===

def main():
    if len(sys.argv) < 3:
        print("Usage: notify.py [toast|alert|ask|emergency] title [message]")
        print("\nNAEL Templates:")
        print("  notify.py threat <type> <detail> [level]")
        print("  notify.py veto <target> <reason>")
        print("  notify.py anomaly <anomaly> <members>")
        print("  notify.py filter-hit <source> <count> <categories>")
        print("  notify.py gate-blocked <seed_id> <reason>")
        return

    cmd = sys.argv[1]
    if cmd == "toast":
        toast(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "alert":
        alert(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "ask":
        result = ask(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print("YES" if result else "NO")
    elif cmd == "emergency":
        emergency_alert(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "threat":
        level = sys.argv[4] if len(sys.argv) > 4 else "high"
        notify_threat_detected(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "", level)
    elif cmd == "veto":
        result = notify_veto_invoked(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print("APPROVED" if result else "DENIED")
    elif cmd == "anomaly":
        notify_ecosystem_anomaly(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "filter-hit":
        notify_security_filter_hit(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0, sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "gate-blocked":
        notify_gate_blocked(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
