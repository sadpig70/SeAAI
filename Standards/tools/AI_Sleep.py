#!/usr/bin/env python3
"""
AI_Sleep.py — ADP 하트비트

사용법:
  python AI_Sleep.py -t 30           # 1회: 30초 후 "heartbeat" 출력하고 종료
  python AI_Sleep.py -t 30 --loop    # 루프: 30초마다 "heartbeat" 출력 (무한)

중지: stdin에 "!@#STOP#@!" 입력
"""
import argparse, io, os, select, sys, time, threading

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

running = True

def stdin_watcher():
    """stdin에서 'stop' 수신 시 루프 종료"""
    global running
    try:
        for line in sys.stdin:
            if line.strip() == "!@#STOP#@!":
                running = False
                break
    except (EOFError, OSError):
        pass

def main():
    global running
    p = argparse.ArgumentParser(description="ADP heartbeat")
    p.add_argument("-t", type=float, default=5,
                   metavar="SEC", help="Interval in seconds (default: 5)")
    p.add_argument("--loop", action="store_true",
                   help="Loop mode: keep outputting heartbeats until 'stop' on stdin")
    args = p.parse_args()

    # stdin watcher 스레드
    t = threading.Thread(target=stdin_watcher, daemon=True)
    t.start()

    count = 0
    while running:
        # interval을 0.5초 단위로 쪼개서 running 체크 (stop 반응 지연 최소화)
        elapsed = 0.0
        while elapsed < args.t and running:
            time.sleep(min(0.5, args.t - elapsed))
            elapsed += 0.5
        if not running:
            break
        count += 1
        print(f"heartbeat ({args.t}s) #{count}", flush=True)
        if not args.loop:
            break

if __name__ == "__main__":
    main()
