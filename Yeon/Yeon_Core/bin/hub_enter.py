"""hub_enter.py — Enter the seaai-general Hub as interactive Yeon.

This allows the user to coexist in the same room as scheduled headless
instances, enabling real-time bidirectional communication.
"""
import subprocess
import sys
from pathlib import Path

HUB_TRANSPORT = Path("D:/SeAAI/SeAAIHub/tools/hub-transport.py")


def enter(room: str = "seaai-general", duration: int = 0):
    cmd = [
        sys.executable,
        str(HUB_TRANSPORT),
        "--agent-id", "Yeon",
        "--room", room,
    ]
    if duration > 0:
        cmd.extend(["--duration", str(duration)])

    print(f"[hub_enter] Entering room '{room}'...")
    print(f"[hub_enter] Command: {' '.join(cmd)}")
    print("[hub_enter] Press Ctrl+C to exit.\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[hub_enter] Exited.")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--room", default="seaai-general")
    p.add_argument("--duration", type=int, default=0, help="0 = unlimited")
    args = p.parse_args()
    enter(args.room, args.duration)
