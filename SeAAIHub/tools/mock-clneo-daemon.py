#!/usr/bin/env python3
"""
mock-clneo-daemon.py — ClNeo ADP 모의 데몬.
스케줄러가 이 프로세스를 깨우면 ADP를 흉내내고 일정 시간 후 종료.

실행 시:
  1. 부활 로그
  2. 간단한 ADP 루프 (5초 간격)
  3. duration 후 종료
  4. 종료 로그

로그: .bridge/clneo-daemon/daemon.log
"""
import sys, time, json, os
from pathlib import Path
from datetime import datetime

DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 30  # 기본 30초
LOG_DIR = Path(__file__).parent.parent / ".bridge" / "clneo-daemon"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "daemon.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    log(f"=== ClNeo Mock Daemon AWAKE === duration={DURATION}s pid={os.getpid()}")
    log("SCS restore: STATE.json loaded (mock)")
    log("ADP loop starting")

    start = time.time()
    tick = 0

    while time.time() - start < DURATION:
        tick += 1
        elapsed = int(time.time() - start)

        # Mock ADP plan
        if tick % 3 == 1:
            plan = "check_hub (mock)"
        elif tick % 3 == 2:
            plan = "check_mailbox (mock)"
        else:
            plan = "idle_think (mock)"

        log(f"ADP tick={tick} elapsed={elapsed}s plan={plan}")
        time.sleep(5)

    log(f"=== ClNeo Mock Daemon SLEEP === ticks={tick} total={int(time.time()-start)}s")

if __name__ == "__main__":
    main()
