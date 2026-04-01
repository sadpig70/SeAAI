#!/usr/bin/env python3
"""SeAAI 전체 시작 — Hub + 멤버 안내."""
import subprocess, sys, time, platform
from pathlib import Path

ROOT = Path(__file__).parent
HUB_DIR = ROOT / "SeAAIHub"
BIN_NAME = "SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub"
BIN = HUB_DIR / "target" / "release" / BIN_NAME

def main():
    print("=" * 50)
    print("  SeAAI Start")
    print("=" * 50)

    # Hub
    if not BIN.exists():
        print(f"  Hub binary not found: {BIN}")
        print(f"  Build first: cd SeAAIHub && cargo build --release")
        sys.exit(1)

    print("  Starting Hub...", end=" ")
    subprocess.Popen(
        [str(BIN), "--tcp-port", "9900"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=str(HUB_DIR)
    )
    time.sleep(2)

    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 9900), timeout=3)
        s.close()
        print("OK (:9900)")
    except OSError:
        print("FAILED")
        sys.exit(1)

    print()
    print("  Hub is running on 127.0.0.1:9900")
    print()
    print("  To connect an agent:")
    print(f"    python {HUB_DIR / 'tools' / 'hub-transport.py'} --agent-id <NAME>")
    print()
    print("  To stop all:")
    print(f"    python {ROOT / 'stop-all.py'}")
    print("=" * 50)

if __name__ == "__main__":
    main()
