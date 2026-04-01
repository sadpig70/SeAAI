#!/usr/bin/env python3
"""SeAAIHub 중지."""
import subprocess, platform

def main():
    print("Stopping SeAAIHub...")
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "SeAAIHub.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "SeAAIHub"], capture_output=True)
        print("Hub stopped.")
    except Exception as e:
        print(f"Error: {e}")

    # Dashboard
    try:
        if platform.system() == "Windows":
            r = subprocess.run(["tasklist"], capture_output=True, text=True)
            # Kill python processes running hub-dashboard
            subprocess.run(
                ["wmic", "process", "where", "commandline like '%hub-dashboard%'", "call", "terminate"],
                capture_output=True
            )
        else:
            subprocess.run(["pkill", "-f", "hub-dashboard"], capture_output=True)
        print("Dashboard stopped.")
    except:
        pass

if __name__ == "__main__":
    main()
