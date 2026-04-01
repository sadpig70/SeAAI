#!/usr/bin/env python3
"""SeAAIHub 상태 확인."""
import subprocess, platform, socket

def check_process(name):
    try:
        if platform.system() == "Windows":
            r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}"], capture_output=True, text=True)
            return name.lower() in r.stdout.lower()
        else:
            r = subprocess.run(["pgrep", "-f", name], capture_output=True)
            return r.returncode == 0
    except:
        return False

def check_port(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=2)
        s.close()
        return True
    except:
        return False

def main():
    print()
    print("=" * 40)
    print("  SeAAIHub Status")
    print("=" * 40)

    hub_name = "SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub"
    hub_on = check_process(hub_name)
    port_on = check_port(9900)

    print(f"  Hub Process : {'ON' if hub_on else 'OFF'}")
    print(f"  TCP :9900   : {'LISTENING' if port_on else 'NOT LISTENING'}")
    print(f"  Dashboard   : {'ON' if check_process('hub-dashboard') else 'OFF'}")
    print()
    print("=" * 40)

if __name__ == "__main__":
    main()
