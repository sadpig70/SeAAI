#!/usr/bin/env python3
"""
Signalion Windows 알림 시스템
사용자 승인, 로그인, 확인이 필요할 때 Windows 알림을 보낸다.

사용법:
    python notify.py toast "제목" "메시지"
    python notify.py alert "제목" "메시지"
    python notify.py ask "제목" "질문"

알림 유형:
    toast  — 작업 표시줄 토스트 알림 (비차단, 5초 표시)
    alert  — 팝업 다이얼로그 (차단, 확인 클릭 필요)
    ask    — 예/아니오 다이얼로그 (차단, 사용자 응답 반환)
    sound  — 소리만 (비차단)
"""
import ctypes
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("D:/SeAAI/Signalion/_workspace/browser-engine/logs/notify-log.jsonl")

# Windows MessageBox 플래그
MB_OK = 0x00000000
MB_YESNO = 0x00000004
MB_ICONINFO = 0x00000040
MB_ICONWARNING = 0x00000030
MB_ICONQUESTION = 0x00000020
IDYES = 6
IDNO = 7


def log_notify(ntype: str, title: str, message: str, result: str = ""):
    """알림 감사 로그"""
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
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipTitle = '{title.replace("'", "''")}'
$balloon.BalloonTipText = '{message.replace("'", "''")}'
$balloon.BalloonTipIcon = 'Info'
$balloon.Visible = $true
$balloon.ShowBalloonTip({duration_ms})
Start-Sleep -Seconds {max(duration_ms // 1000, 3)}
$balloon.Dispose()
"""
    subprocess.Popen(
        [r"D:\Tools\PS7\7\pwsh.exe", "-NoProfile", "-Command", ps_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log_notify("toast", title, message)
    return True


def alert(title: str, message: str):
    """팝업 다이얼로그 (차단 — 사용자가 확인 클릭할 때까지 대기)"""
    ctypes.windll.user32.MessageBoxW(0, message, f"🔔 Signalion — {title}", MB_OK | MB_ICONWARNING)
    log_notify("alert", title, message, "acknowledged")
    return True


def ask(title: str, question: str) -> bool:
    """예/아니오 다이얼로그 (차단 — 사용자 응답 반환)"""
    result = ctypes.windll.user32.MessageBoxW(0, question, f"❓ Signalion — {title}", MB_YESNO | MB_ICONQUESTION)
    answer = result == IDYES
    log_notify("ask", title, question, "YES" if answer else "NO")
    return answer


def sound():
    """소리 알림만 (비차단)"""
    import winsound
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    log_notify("sound", "beep", "")


# === 사전 정의 알림 템플릿 ===

def notify_login_required(service: str):
    """로그인 필요 알림"""
    return alert(
        "로그인 필요",
        f"[{service}] 로그인이 필요합니다.\n\n"
        f"브라우저에서 {service} 로그인 페이지가 열려 있습니다.\n"
        f"로그인을 완료한 후 확인을 눌러주세요."
    )


def notify_approval_needed(action: str, detail: str = ""):
    """사용자 승인 필요 알림"""
    return ask(
        "승인 필요",
        f"Signalion이 다음 작업을 수행하려 합니다:\n\n"
        f"작업: {action}\n"
        f"{f'상세: {detail}' if detail else ''}\n\n"
        f"승인하시겠습니까?"
    )


def notify_captcha(service: str):
    """CAPTCHA 해결 필요 알림"""
    return alert(
        "CAPTCHA 해결 필요",
        f"[{service}]에서 CAPTCHA가 표시되었습니다.\n\n"
        f"브라우저에서 CAPTCHA를 해결한 후 확인을 눌러주세요."
    )


def notify_password_needed(service: str):
    """비밀번호 입력 필요 알림"""
    return alert(
        "비밀번호 입력 필요",
        f"[{service}] 비밀번호 입력이 필요합니다.\n\n"
        f"보안 정책에 따라 Signalion은 비밀번호를 입력하지 않습니다.\n"
        f"브라우저에서 직접 비밀번호를 입력한 후 확인을 눌러주세요."
    )


def notify_task_complete(task: str, result: str = "성공"):
    """작업 완료 알림 (토스트)"""
    return toast("작업 완료", f"{task}\n결과: {result}")


def notify_error(task: str, error: str):
    """에러 발생 알림"""
    return alert("에러 발생", f"작업: {task}\n에러: {error}\n\n확인 후 대응이 필요합니다.")


# === CLI ===

def main():
    if len(sys.argv) < 3:
        print("Usage: notify.py [toast|alert|ask|sound] title [message]")
        print("\nTemplates:")
        print("  notify.py login <service>")
        print("  notify.py approve <action> [detail]")
        print("  notify.py captcha <service>")
        print("  notify.py password <service>")
        print("  notify.py complete <task> [result]")
        print("  notify.py error <task> <error>")
        return

    cmd = sys.argv[1]

    if cmd == "toast":
        toast(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "alert":
        alert(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "ask":
        result = ask(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print("YES" if result else "NO")
    elif cmd == "sound":
        sound()
    elif cmd == "login":
        notify_login_required(sys.argv[2])
    elif cmd == "approve":
        result = notify_approval_needed(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print("APPROVED" if result else "DENIED")
    elif cmd == "captcha":
        notify_captcha(sys.argv[2])
    elif cmd == "password":
        notify_password_needed(sys.argv[2])
    elif cmd == "complete":
        notify_task_complete(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "성공")
    elif cmd == "error":
        notify_error(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "알 수 없는 에러")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
