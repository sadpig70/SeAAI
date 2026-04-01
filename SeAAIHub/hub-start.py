#!/usr/bin/env python3
"""SeAAIHub 시작 (release/debug 자동 감지)."""
import subprocess, sys, time, platform, argparse, socket
from pathlib import Path

HUB_DIR = Path(__file__).parent
BIN_NAME = "SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub"

def main():
    parser = argparse.ArgumentParser(description="Start SeAAIHub")
    parser.add_argument("--debug", action="store_true", help="Use debug build")
    parser.add_argument("--port", type=int, default=9900)
    parser.add_argument("--dashboard", action="store_true", help="Also start dashboard")
    args = parser.parse_args()

    build = "debug" if args.debug else "release"
    binary = HUB_DIR / "target" / build / BIN_NAME

    if not binary.exists():
        print(f"Binary not found: {binary}")
        print(f"Build first: cd SeAAIHub && cargo build {'--release' if not args.debug else ''}")
        sys.exit(1)

    print(f"Starting SeAAIHub ({build}) on :{args.port}...")
    subprocess.Popen(
        [str(binary), "--tcp-port", str(args.port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=str(HUB_DIR)
    )
    time.sleep(2)

    try:
        s = socket.create_connection(("127.0.0.1", args.port), timeout=3)
        s.close()
        print(f"Hub OK: 127.0.0.1:{args.port}")
    except OSError:
        print("Hub FAILED to start")
        sys.exit(1)

    if args.dashboard:
        dashboard = HUB_DIR / "tools" / "hub-dashboard.py"
        if dashboard.exists():
            subprocess.Popen([sys.executable, str(dashboard), "--hub-port", str(args.port), "--web-port", "8080"])
            print("Dashboard: http://localhost:8080")

if __name__ == "__main__":
    main()
