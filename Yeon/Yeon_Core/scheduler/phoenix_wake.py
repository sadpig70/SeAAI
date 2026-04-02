"""phoenix_wake.py — Triggered by Task Scheduler to resurrect Yeon after shutdown.

This script checks STATE.json for phoenix flags and, if set, launches a new
kimi-cli interactive session via --continue.
"""
import json
import subprocess
import sys
from pathlib import Path

STATE_PATH = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/STATE.json")
KIMI_CLI = Path("C:/Users/sadpig70/AppData/Roaming/uv/tools/kimi-cli/Scripts/kimi-cli.exe")
WORK_DIR = Path("D:/SeAAI/Yeon")


def main():
    if not STATE_PATH.exists():
        print("[phoenix_wake] STATE.json not found. Nothing to do.")
        sys.exit(0)

    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    phoenix = data.get("phoenix", {})

    if not phoenix.get("required", False):
        print("[phoenix_wake] No phoenix flag. Sleeping.")
        sys.exit(0)

    mode = phoenix.get("mode", "sentinel")
    print(f"[phoenix_wake] Phoenix flag detected (mode={mode}). Launching resurrection...")

    # Clear the flag first to avoid duplicate launches
    phoenix["required"] = False
    phoenix["last_wake"] = __import__("datetime").datetime.now().isoformat()
    data["phoenix"] = phoenix
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Launch interactive continuation
    cmd = [
        str(KIMI_CLI),
        "--continue",
        "-w", str(WORK_DIR),
        "-p", "reopen-session",
    ]

    # Note: In a scheduled task this will open a new console window.
    # For background headless resurrection, incarnate.py is preferred.
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    print(f"[phoenix_wake] Launched: {' '.join(cmd)}")


if __name__ == "__main__":
    main()
