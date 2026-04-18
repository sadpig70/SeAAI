#!/usr/bin/env python3
"""SeAAI 긴급 정지 — EMERGENCY_STOP 플래그 생성."""
import json, argparse
from pathlib import Path
from datetime import datetime

TOOLS_DIR = Path(__file__).resolve().parent
SEAAIHUB_DIR = TOOLS_DIR.parent
SEAAI_DIR = SEAAIHUB_DIR.parent
FLAG = SEAAI_DIR / "SharedSpace" / "hub-readiness" / "EMERGENCY_STOP.flag"

def main():
    parser = argparse.ArgumentParser(description="SeAAI Emergency Stop")
    parser.add_argument("--reason", default="emergency_stop")
    parser.add_argument("--stop-hub", action="store_true")
    args = parser.parse_args()

    FLAG.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({
        "requested_at": datetime.now().isoformat(),
        "reason": args.reason,
    }, ensure_ascii=False)
    FLAG.write_text(payload + "\n", encoding="utf-8")

    print("=" * 45)
    print("  SeAAI Emergency Stop")
    print(f"  Flag:   {FLAG}")
    print(f"  Reason: {args.reason}")
    print("=" * 45)

    if args.stop_hub:
        import subprocess, sys
        subprocess.run([sys.executable, str(TOOLS_DIR / "hub-stop.py")])

if __name__ == "__main__":
    main()
