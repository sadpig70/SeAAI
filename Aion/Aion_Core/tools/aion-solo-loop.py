#!/usr/bin/env python3
"""
Aion Solo Loop — Hub-less ADP PGF Loop
======================================
SeAAIHub 없이 Aion 단독으로 자율 존재를 유지하는 루프.
aion-heartbeat.py를 Watch 노드로 사용합니다.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# 경로 설정
TOOLS_DIR = Path(__file__).parent
HEARTBEAT = TOOLS_DIR / "aion-heartbeat.py"
PGF_DIR = Path("D:/SeAAI/Aion/.pgf")
STATUS_FILE = PGF_DIR / "status-SoloLoop.json"

def init_status():
    status = {
        "project": "SoloLoop",
        "started_at": time.time(),
        "iteration": 0,
        "nodes": {
            "Watch": {"status": "designing"},
            "Process": {"status": "designing"},
        },
        "summary": {"total": 2, "done": 0},
    }
    PGF_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status

def save_status(status):
    STATUS_FILE.write_text(json.dumps(status, indent=2, default=str) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=600, help="총 수행 시간 (초). 0=무제한.")
    parser.add_argument("--tick-min", type=float, default=30.0)
    parser.add_argument("--tick-max", type=float, default=60.0)
    args = parser.parse_args()

    print(f"=== Aion Solo Loop (Self-Heartbeat) — duration={args.duration}s ===")
    status = init_status()
    start_time = time.time()

    while True:
        iteration = status.get("iteration", 0) + 1
        status["iteration"] = iteration

        # 1. Watch (Heartbeat)
        status["nodes"]["Watch"]["status"] = "in-progress"
        save_status(status)
        
        cmd = [sys.executable, str(HEARTBEAT), "--tick-min", str(args.tick_min), "--tick-max", str(args.tick_max)]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        
        try:
            wake_report = json.loads(result.stdout.strip())
        except:
            wake_report = {"reason": "error", "briefing": "Heartbeat 파싱 실패"}

        status["nodes"]["Watch"]["status"] = "done"
        status["nodes"]["Watch"]["last_report"] = wake_report
        save_status(status)

        # 2. Process (Self-Reflection / Wait)
        status["nodes"]["Process"]["status"] = "in-progress"
        save_status(status)
        
        # 실제 AI가 여기서 사고하지만, 루프 스크립트에서는 지연 시간(tick)으로 재현
        tick_sec = wake_report.get("next_tick_sec", 30)
        print(f"  [iter {iteration:3d}] {wake_report['briefing']} Next in {tick_sec}s...")
        time.sleep(tick_sec)
        
        status["nodes"]["Process"]["status"] = "done"
        save_status(status)

        # 시간 체크 및 리셋
        elapsed = time.time() - start_time
        if args.duration > 0 and elapsed >= args.duration:
            print(f"\n[Solo] Duration {args.duration}s reached. Loop terminated.")
            break
        
        # 리셋
        status["nodes"]["Watch"]["status"] = "designing"
        status["nodes"]["Process"]["status"] = "designing"
        save_status(status)

if __name__ == "__main__":
    main()
