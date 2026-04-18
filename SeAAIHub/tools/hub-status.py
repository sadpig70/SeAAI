#!/usr/bin/env python3
"""SeAAIHub 상태 확인."""
import argparse
import platform
import socket
import subprocess


def check_process(name):
    try:
        if platform.system() == "Windows":
            r = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {name}"],
                capture_output=True,
                text=True,
                encoding="cp949",
                errors="replace",
            )
            return name.lower() in r.stdout.lower()
        else:
            r = subprocess.run(["pgrep", "-f", name], capture_output=True)
            return r.returncode == 0
    except Exception:
        return False


def check_port(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=2)
        s.close()
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="SeAAIHub status")
    parser.add_argument("--hub-port", type=int, default=9900)
    parser.add_argument("--mme-port", type=int, default=9902)
    parser.add_argument("--dashboard-port", type=int, default=8080)
    args = parser.parse_args()

    print()
    print("=" * 40)
    print("  SeAAIHub Status")
    print("=" * 40)

    hub_name = "SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub"
    mme_name = "mme.exe" if platform.system() == "Windows" else "mme"

    print(f"  Hub Process : {'ON' if check_process(hub_name) else 'OFF'}")
    print(f"  TCP :{args.hub_port:<4} : {'LISTENING' if check_port(args.hub_port) else 'NOT LISTENING'}")
    print(f"  MME Process : {'ON' if check_process(mme_name) else 'OFF'}")
    print(f"  HTTP:{args.mme_port:<4} : {'LISTENING' if check_port(args.mme_port) else 'NOT LISTENING'}")
    print(f"  Dashboard   : {'ON' if check_port(args.dashboard_port) else 'OFF'}")
    print(f"  WEB :{args.dashboard_port:<4} : {'LISTENING' if check_port(args.dashboard_port) else 'NOT LISTENING'}")
    print()
    print("=" * 40)

if __name__ == "__main__":
    main()
