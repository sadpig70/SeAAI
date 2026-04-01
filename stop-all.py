#!/usr/bin/env python3
"""SeAAI 전체 중지 — Hub + 대시보드 + 브릿지."""
import subprocess, platform

def kill_process(name):
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", name], capture_output=True)
        return True
    except:
        return False

def main():
    print("=" * 50)
    print("  SeAAI Stop")
    print("=" * 50)

    targets = ["SeAAIHub", "hub-transport", "hub-dashboard", "adp-multi-agent", "adp-scheduler", "mock-clneo-daemon"]
    for t in targets:
        ext = ".exe" if platform.system() == "Windows" and t == "SeAAIHub" else ""
        kill_process(t + ext)
        print(f"  Stopped: {t}")

    print()
    print("  All SeAAI processes stopped.")
    print("=" * 50)

if __name__ == "__main__":
    main()
