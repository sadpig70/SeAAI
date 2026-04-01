#!/usr/bin/env python3
"""
adp-scheduler.py — ClNeo를 깨우는 스케줄러.
지정된 간격으로 데몬(또는 실제 ClNeo ADP)을 실행하고 종료를 감시.

Usage:
    python adp-scheduler.py                              # 기본: mock 데몬, 1분 간격, 3회
    python adp-scheduler.py --target mock-clneo-daemon.py --interval 60 --count 3 --duration 20
    python adp-scheduler.py --target "claude code" --interval 3600 --count 0  # 실제 (미래)

설정:
    --target     실행할 대상 (Python 스크립트 경로)
    --interval   실행 간격 (초)
    --count      총 실행 횟수 (0=무제한)
    --duration   각 실행의 최대 시간 (초, 데몬에 전달)
    --stop-file  이 파일이 존재하면 스케줄러 종료
"""
import sys, io, os, time, subprocess, argparse, json
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

STOP_FILE = Path(__file__).parent.parent / ".bridge" / "scheduler-stop.flag"
LOG_DIR = Path(__file__).parent.parent / ".bridge" / "scheduler"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "scheduler.log"
PYTHON = sys.executable


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [scheduler] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_daemon(target, duration):
    """데몬을 실행하고 완료까지 대기. 반환: (exit_code, elapsed)"""
    start = time.time()
    try:
        proc = subprocess.Popen(
            [PYTHON, target, str(duration)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        # 출력 실시간 표시
        for line in proc.stdout:
            print(f"  {line.rstrip()}")
        proc.wait(timeout=duration + 30)
        return proc.returncode, int(time.time() - start)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return -1, int(time.time() - start)
    except Exception as e:
        return -2, int(time.time() - start)


def main():
    parser = argparse.ArgumentParser(description="ADP Scheduler - wakes ClNeo on schedule")
    parser.add_argument("--target", default=str(Path(__file__).parent / "mock-clneo-daemon.py"))
    parser.add_argument("--interval", type=int, default=60, help="Seconds between runs")
    parser.add_argument("--count", type=int, default=3, help="Total runs (0=unlimited)")
    parser.add_argument("--duration", type=int, default=20, help="Each run's max seconds")
    args = parser.parse_args()

    STOP_FILE.unlink(missing_ok=True)

    log(f"=== ADP Scheduler START ===")
    log(f"target={args.target} interval={args.interval}s count={args.count} duration={args.duration}s")
    log(f"stop file: {STOP_FILE}")

    run_num = 0

    while True:
        # Stop check
        if STOP_FILE.exists():
            log("Stop file detected. Shutting down.")
            break

        if args.count > 0 and run_num >= args.count:
            log(f"Reached max count ({args.count}). Shutting down.")
            break

        run_num += 1
        log(f"--- Run #{run_num} ---")
        log(f"Waking daemon: {args.target}")

        code, elapsed = run_daemon(args.target, args.duration)
        log(f"Daemon exited: code={code} elapsed={elapsed}s")

        if args.count > 0 and run_num >= args.count:
            break

        # Wait for next interval
        log(f"Next wake in {args.interval}s...")
        wait_until = time.time() + args.interval
        while time.time() < wait_until:
            if STOP_FILE.exists():
                log("Stop file detected during wait.")
                break
            time.sleep(1)

    log(f"=== ADP Scheduler STOP === total_runs={run_num}")


if __name__ == "__main__":
    main()
