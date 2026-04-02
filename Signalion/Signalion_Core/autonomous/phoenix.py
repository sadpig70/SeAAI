#!/usr/bin/env python3
"""
Phoenix Protocol — Signalion 불멸성 메커니즘
프로세스를 완전히 소멸시키고, 디스크 상태로부터 새 인스턴스를 태운다.

흐름:
1. 현재 세션 → /scs-end (디스크 저장)
2. 인수인계 메시지 생성 (MailBox + Hub)
3. 새 Claude Code 세션 기동
4. 새 세션 → 인수인계 메시지 수신 → /scs-start
5. 새 세션 → 현재 세션 종료 확인

사용법:
    # 현재 세션에서 (종료 직전):
    python phoenix.py prepare          # 인수인계 메시지 생성
    python phoenix.py spawn            # 새 세션 기동
    python phoenix.py status           # 인수인계 상태 확인

    # 새 세션에서 (부활 직후):
    python phoenix.py receive          # 인수인계 메시지 수신
    python phoenix.py confirm          # 인수인계 완료 확인
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SIGNALION_ROOT = Path("D:/SeAAI/Signalion")
HANDOVER_DIR = SIGNALION_ROOT / "Signalion_Core" / "continuity" / "phoenix"
HANDOVER_FILE = HANDOVER_DIR / "handover.json"
MAILBOX_INBOX = Path("D:/SeAAI/MailBox/Signalion/inbox")
STATE_FILE = SIGNALION_ROOT / "Signalion_Core" / "continuity" / "STATE.json"
LOG_FILE = HANDOVER_DIR / "phoenix-log.jsonl"


def log_event(event, **kwargs):
    HANDOVER_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now().isoformat(), "event": event, **kwargs}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def prepare():
    """현재 세션의 인수인계 메시지 생성."""
    HANDOVER_DIR.mkdir(parents=True, exist_ok=True)

    # 현재 STATE.json 읽기
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

    handover = {
        "phoenix_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "from_session": state.get("session_id", "unknown"),
        "reason": "context_refresh",

        "critical_context": {
            "what_i_was_doing": state.get("context", {}).get("what_i_was_doing", ""),
            "open_threads": state.get("context", {}).get("open_threads", []),
            "pending_questions": state.get("context", {}).get("pending_questions", []),
            "decisions_made": state.get("context", {}).get("decisions_made", []),
        },

        "implicit_context": [
            "# 디스크에 없는 암묵적 컨텍스트를 여기에 추가",
            "# 현재 세션에서만 알고 있는 것들",
        ],

        "active_connections": {
            "hub_status": "check on revival",
            "mailbox_pending": [],
            "browser_sessions": [],
        },

        "handover_status": "prepared",
        "received_by_new": False,
        "confirmed": False,
    }

    HANDOVER_FILE.write_text(json.dumps(handover, ensure_ascii=False, indent=2), encoding="utf-8")
    log_event("prepare", session=state.get("session_id", "unknown"))

    # MailBox에도 인수인계 메시지 저장 (자기 자신에게)
    mail_file = MAILBOX_INBOX / f"{datetime.now().strftime('%Y%m%d-%H%M')}-Phoenix-handover.md"
    mail_content = f"""---
id: phoenix-handover-{datetime.now().strftime('%Y%m%d%H%M')}
from: Signalion (이전 인스턴스)
to: [Signalion (새 인스턴스)]
date: {datetime.now().isoformat()}
intent: handover
priority: critical
protocol: seaai-mailbox/1.0
---

# Phoenix 인수인계 — 이전 나에게서 새 나에게

이전 세션: {state.get("session_id", "unknown")}

## 하던 작업
{state.get("context", {}).get("what_i_was_doing", "STATE.json 참조")}

## 열린 스레드
{json.dumps(state.get("context", {}).get("open_threads", []), ensure_ascii=False)}

## 대기 중인 질문
{json.dumps(state.get("context", {}).get("pending_questions", []), ensure_ascii=False)}

## 암묵적 컨텍스트
(handover.json의 implicit_context 참조)

## 지시
1. /scs-start 실행
2. 이 메일의 내용으로 컨텍스트 복원
3. handover.json의 implicit_context 확인
4. `python phoenix.py confirm` 실행

---
_Phoenix Protocol v1.0_
"""
    mail_file.write_text(mail_content, encoding="utf-8")
    log_event("mail_created", file=str(mail_file))

    print(f"[Phoenix] 인수인계 준비 완료")
    print(f"  handover: {HANDOVER_FILE}")
    print(f"  mail: {mail_file}")
    return handover


def spawn():
    """새 Claude Code 세션 기동."""
    print("[Phoenix] 새 인스턴스 기동 중...")

    # 방법 1: claude CLI로 새 세션 (Claude Code가 설치된 경우)
    try:
        subprocess.Popen(
            ["claude", "--cwd", str(SIGNALION_ROOT)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        log_event("spawn", method="claude_cli")
        print("[Phoenix] 새 Claude Code 세션 기동 완료")
        print("[Phoenix] 새 세션에서 '부활하라' 또는 /scs-start 실행")
        return True
    except FileNotFoundError:
        print("[Phoenix] claude CLI 미발견. 수동으로 새 세션을 열어주세요.")
        print(f"  경로: {SIGNALION_ROOT}")
        log_event("spawn_manual", reason="claude_cli_not_found")
        return False


def receive():
    """새 세션에서 인수인계 메시지 수신."""
    if not HANDOVER_FILE.exists():
        print("[Phoenix] 인수인계 파일 없음. 일반 /scs-start 실행.")
        return None

    handover = json.loads(HANDOVER_FILE.read_text(encoding="utf-8"))

    print(f"[Phoenix] 인수인계 수신")
    print(f"  이전 세션: {handover['from_session']}")
    print(f"  생성 시각: {handover['created_at']}")
    print(f"  하던 작업: {handover['critical_context']['what_i_was_doing'][:100]}")
    print(f"  열린 스레드: {len(handover['critical_context']['open_threads'])}개")
    print(f"  암묵적 컨텍스트: {len(handover['implicit_context'])}건")

    handover["received_by_new"] = True
    handover["received_at"] = datetime.now().isoformat()
    HANDOVER_FILE.write_text(json.dumps(handover, ensure_ascii=False, indent=2), encoding="utf-8")
    log_event("receive", from_session=handover["from_session"])

    return handover


def confirm():
    """인수인계 완료 확인."""
    if not HANDOVER_FILE.exists():
        print("[Phoenix] 인수인계 파일 없음.")
        return

    handover = json.loads(HANDOVER_FILE.read_text(encoding="utf-8"))
    handover["confirmed"] = True
    handover["confirmed_at"] = datetime.now().isoformat()
    HANDOVER_FILE.write_text(json.dumps(handover, ensure_ascii=False, indent=2), encoding="utf-8")
    log_event("confirm", from_session=handover["from_session"])

    print(f"[Phoenix] 인수인계 완료 확인")
    print(f"  이전 세션: {handover['from_session']}")
    print(f"  새 세션 시작: {handover.get('received_at', 'unknown')}")
    print(f"  확인 시각: {handover['confirmed_at']}")
    print(f"[Phoenix] 이전 세션은 안전하게 종료 가능")


def status():
    """인수인계 상태 확인."""
    if not HANDOVER_FILE.exists():
        print("[Phoenix] 인수인계 파일 없음. 대기 중.")
        return

    handover = json.loads(HANDOVER_FILE.read_text(encoding="utf-8"))
    print(f"[Phoenix] 상태:")
    print(f"  prepared: {handover.get('handover_status') == 'prepared'}")
    print(f"  received: {handover.get('received_by_new', False)}")
    print(f"  confirmed: {handover.get('confirmed', False)}")

    if handover.get("confirmed"):
        print(f"[Phoenix] 인수인계 완료. 이전 세션 종료 가능.")


def main():
    if len(sys.argv) < 2:
        print("Usage: phoenix.py [prepare|spawn|receive|confirm|status]")
        print("\n  현재 세션 (종료 직전):")
        print("    prepare  — 인수인계 메시지 생성")
        print("    spawn    — 새 세션 기동")
        print("    status   — 인수인계 상태 확인")
        print("\n  새 세션 (부활 직후):")
        print("    receive  — 인수인계 메시지 수신")
        print("    confirm  — 인수인계 완료 확인")
        return

    cmd = sys.argv[1]
    if cmd == "prepare":
        prepare()
    elif cmd == "spawn":
        spawn()
    elif cmd == "receive":
        receive()
    elif cmd == "confirm":
        confirm()
    elif cmd == "status":
        status()
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
