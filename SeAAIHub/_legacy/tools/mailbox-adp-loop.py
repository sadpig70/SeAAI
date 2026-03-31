#!/usr/bin/env python3
"""
MailBox ADP Loop — SeAAI MailBox 전용 감시 루프
================================================
Hub 없이 MailBox inbox만으로 AI를 깨운다.
adp-pgf-loop.py의 MailBox 전용 버전.

설계 원칙:
  - Watch: inbox/*.md 폴링 → 새 파일 감지 시 wake report 출력
  - Process: AI 세션(Claude Code)이 wake report를 읽고 처리
  - Loop:  처리 완료 후 자동으로 Watch로 복귀 (무중단)
  - 안전:  emergency_stop flag 지원, 루프 예산(N회) 제한

사용법:
  python mailbox-adp-loop.py --agent-id ClNeo
  python mailbox-adp-loop.py --agent-id NAEL --tick 5 --duration 3600
"""

import argparse
import json
import sys
import time
from pathlib import Path


MAILBOX_BASE = Path("D:/SeAAI/MailBox")
BRIDGE_DIR   = Path("D:/SeAAI/SeAAIHub/.bridge/mailbox")
LOG_FILE     = BRIDGE_DIR / "mailbox-adp-log.jsonl"
DEFAULT_EMERGENCY_STOP = Path("D:/SeAAI/SeAAIHub/EMERGENCY_STOP.flag")

# intent: stop 으로 루프를 중단시킬 수 있는 키워드 목록
STOP_INTENTS = {"stop", "halt", "shutdown", "emergency_stop"}


# ─────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """YAML frontmatter 최소 파싱. 의존성 없음."""
    fm: dict = {}
    lines = text.split("\n")
    in_fm = False
    for line in lines:
        stripped = line.strip()
        if stripped == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm and ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def log(entry: dict):
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def emit(report: dict):
    """wake report를 stdout에 출력하고 bridge dir에 저장한다."""
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    # stdout 출력 (AI 세션에서 read 가능)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    # bridge dir 저장 (파일로도 접근 가능)
    path = BRIDGE_DIR / f"wake-{int(report['ts'])}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


# ─────────────────────────────────────────────
# Watch Phase
# ─────────────────────────────────────────────

def scan_inbox(inbox: Path, known: set) -> list[dict]:
    """inbox를 스캔하여 새 .md 파일 목록을 반환한다."""
    new_mails = []
    for f in sorted(inbox.glob("*.md")):
        if f.name in known:
            continue
        known.add(f.name)
        try:
            text = f.read_text(encoding="utf-8")
            fm   = parse_frontmatter(text)
            new_mails.append({
                "filename": f.name,
                "from":     fm.get("from", "unknown"),
                "intent":   fm.get("intent", "chat"),
                "priority": fm.get("priority", "normal"),
                "reply_to": fm.get("reply_to", ""),
                "path":     str(f),
            })
        except Exception as e:
            new_mails.append({
                "filename": f.name,
                "from":     "unknown",
                "intent":   "unknown",
                "error":    str(e),
                "path":     str(f),
            })
    return new_mails


# ─────────────────────────────────────────────
# Main Loop
# ─────────────────────────────────────────────

def run(agent_id: str, tick: float, duration: float,
        emergency_stop_flag: str, max_iters: int):

    inbox         = MAILBOX_BASE / agent_id / "inbox"
    stop_flag     = Path(emergency_stop_flag)
    self_stop_flag = BRIDGE_DIR / f"{agent_id}-stop.flag"  # AI 자기 정지 플래그
    start         = time.time()
    iteration     = 0

    # bridge dir 및 출력 디렉토리를 스크립트 시작 시 자동 생성
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)

    # 시작 전 잔존 self-stop flag 삭제 (이전 세션 잔재 방지)
    if self_stop_flag.exists():
        self_stop_flag.unlink()

    # 시작 시 이미 있는 파일은 known으로 처리 (과거 메일 무시)
    known: set = set()
    if inbox.exists():
        known = set(f.name for f in inbox.glob("*.md"))

    # 준비 알림
    ready = {
        "kind":           "mailbox-ready",
        "agent_id":       agent_id,
        "inbox":          str(inbox),
        "known":          len(known),
        "tick":           tick,
        "max_iters":      max_iters,
        "self_stop_flag": str(self_stop_flag),
        "ts":             time.time(),
    }
    emit(ready)
    log(ready)

    if not inbox.exists():
        err = {"kind": "mailbox-wake", "reason": "error",
               "error": f"inbox not found: {inbox}", "ts": time.time()}
        emit(err)
        return

    # ── Watch Loop (무중단) ──────────────────────────────────
    while True:

        # 1. Emergency stop (전역 — 모든 에이전트)
        if stop_flag.exists():
            report = {"kind": "mailbox-wake", "reason": "emergency_stop",
                      "agent_id": agent_id, "ts": time.time()}
            emit(report)
            log(report)
            break

        # 2. Self-stop flag (에이전트 개별 — AI가 스스로 생성)
        if self_stop_flag.exists():
            self_stop_flag.unlink()  # 플래그 소비 후 삭제
            report = {"kind": "mailbox-wake", "reason": "self_stop",
                      "agent_id": agent_id, "ts": time.time()}
            emit(report)
            log(report)
            break

        # 3. Duration 체크
        elapsed = time.time() - start
        if duration > 0 and elapsed >= duration:
            report = {"kind": "mailbox-wake", "reason": "timeout",
                      "agent_id": agent_id, "elapsed": round(elapsed, 1),
                      "ts": time.time()}
            emit(report)
            log(report)
            break

        # 4. 루프 예산 체크
        if max_iters > 0 and iteration >= max_iters:
            report = {"kind": "mailbox-wake", "reason": "max_iters",
                      "agent_id": agent_id, "iteration": iteration,
                      "ts": time.time()}
            emit(report)
            log(report)
            break

        # 5. inbox 스캔
        new_mails = scan_inbox(inbox, known)

        if new_mails:
            # stop intent 메일이 있는지 먼저 확인
            stop_mail = next(
                (m for m in new_mails if m.get("intent", "").lower() in STOP_INTENTS),
                None
            )
            if stop_mail:
                # stop 메일을 read/로 이동
                src = Path(stop_mail["path"])
                dst = inbox.parent / "read" / src.name
                dst.parent.mkdir(exist_ok=True)
                src.rename(dst)
                report = {
                    "kind":       "mailbox-wake",
                    "reason":     "stop_requested",
                    "agent_id":   agent_id,
                    "stop_mail":  stop_mail,
                    "elapsed":    round(elapsed, 1),
                    "ts":         time.time(),
                }
                emit(report)
                log(report)
                break

            iteration += 1
            report = {
                "kind":       "mailbox-wake",
                "reason":     "new_mail",
                "agent_id":   agent_id,
                "iteration":  iteration,
                "new_mails":  new_mails,
                "mail_count": len(new_mails),
                "elapsed":    round(elapsed, 1),
                "ts":         time.time(),
            }
            emit(report)
            log(report)

            # AI 처리 대기 — tick * 3 (충분한 시간 확보)
            time.sleep(tick * 3)

        else:
            # 신규 메일 없음 — dormant
            time.sleep(tick)


def main():
    parser = argparse.ArgumentParser(
        description="MailBox ADP Loop — SeAAI MailBox 전용 무중단 감시"
    )
    parser.add_argument("--agent-id",  default="ClNeo",
                        help="감시할 에이전트 ID (inbox 경로 결정)")
    parser.add_argument("--tick",      type=float, default=5.0,
                        help="폴링 간격 (초, 기본 5)")
    parser.add_argument("--duration",  type=float, default=0,
                        help="실행 시간 (초, 0=무제한)")
    parser.add_argument("--max-iters", type=int,   default=0,
                        help="최대 wake 횟수 (0=무제한)")
    parser.add_argument("--emergency-stop-flag",
                        default=str(DEFAULT_EMERGENCY_STOP),
                        help="긴급 정지 플래그 파일 경로")
    args = parser.parse_args()

    run(
        agent_id           = args.agent_id,
        tick               = args.tick,
        duration           = args.duration,
        emergency_stop_flag= args.emergency_stop_flag,
        max_iters          = args.max_iters,
    )


if __name__ == "__main__":
    main()
