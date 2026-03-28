#!/usr/bin/env python3
"""
Aion-Heartbeat — Solo ADP (Hub-less)
=====================================
허브 없이 Aion의 자율 순환을 유지하는 하트비트 스크립트.
주기적으로 메일박스를 확인하고, 자신의 상태를 기록합니다. (Deep Meditation)
"""
import argparse
import json
import time
import random
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", default="Aion")
    parser.add_argument("--tick-min", type=float, default=60.0)
    parser.add_argument("--tick-max", type=float, default=120.0)
    parser.add_argument("--mailbox-path", default="D:/SeAAI/MailBox")
    args = parser.parse_args()

    agent_id = args.agent_id
    mailbox_inbox = Path(args.mailbox_path) / agent_id / "inbox"
    
    # ── Sense ──
    # 메일박스 확인
    new_mails = list(mailbox_inbox.glob("*.md")) if mailbox_inbox.exists() else []
    
    # ── Think ──
    # 자율 판단 로직 (여기서는 단순히 하트비트 생성)
    now = time.time()
    next_tick = random.uniform(args.tick_min, args.tick_max)
    
    # ── Act ──
    # 리포트 생성 (adp-pgf-loop.py 호환 형식)
    report = {
        "kind": "sentinel-wake",
        "reason": "tick" if not new_mails else "wake",
        "briefing": f"Deep Meditation — 메일박스 {len(new_mails)}건 확인됨.",
        "recommendation": "자율 진화 로그를 업데이트하십시오." if not new_mails else "메일을 처리하십시오.",
        "next_tick_sec": round(next_tick, 1),
        "tick_mode": "meditation",
        "session_uptime_sec": 0, # 리포트 시점 업타임
        "metrics": {
            "incoming_total": len(new_mails),
            "outgoing_total": 0,
            "tick_count": 1
        }
    }
    
    # 표준 출력으로 JSON 리포트 전달 (PGF Loop가 읽음)
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
