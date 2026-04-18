#!/usr/bin/env python3
"""SeAAIHub 중지."""
import subprocess, platform


def stop_image(name: str):
    if platform.system() == "Windows":
        subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True)
    else:
        subprocess.run(["pkill", "-f", name], capture_output=True)


def main():
    print("Stopping SeAAIHub...")
    try:
        stop_image("SeAAIHub.exe" if platform.system() == "Windows" else "SeAAIHub")
        print("Hub stopped.")
    except Exception as e:
        print(f"Error: {e}")

    try:
        stop_image("mme.exe" if platform.system() == "Windows" else "mme")
        print("MME stopped.")
    except Exception:
        pass

    # Dashboard
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["wmic", "process", "where", "commandline like '%hub-dashboard.py%'", "call", "terminate"],
                capture_output=True
            )
        else:
            subprocess.run(["pkill", "-f", "hub-dashboard.py"], capture_output=True)
        print("Dashboard stopped.")
    except Exception:
        pass

if __name__ == "__main__":
    main()
