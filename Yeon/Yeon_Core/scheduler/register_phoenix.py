"""register_phoenix.py — Register the Phoenix Wake task with Windows Task Scheduler."""
import subprocess
import sys
from pathlib import Path

PYTHON = Path(sys.executable)
WAKE_SCRIPT = Path("D:/SeAAI/Yeon/Yeon_Core/scheduler/phoenix_wake.py")
GUARDIAN_SCRIPT = Path("D:/SeAAI/Yeon/Yeon_Core/scheduler/context_guardian.py")


def create_wake_task():
    task_name = "Yeon_PhoenixWake"
    tr = f'"{PYTHON}" "{WAKE_SCRIPT}"'
    cmd = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", tr,
        "/sc", "minute",
        "/mo", "5",
        "/f",
    ]
    print(f"[register_phoenix] Creating {task_name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[register_phoenix] ERROR: {result.stderr}")
    return result.returncode == 0


def create_guardian_task():
    task_name = "Yeon_ContextGuardian"
    tr = f'"{PYTHON}" "{GUARDIAN_SCRIPT}" --mode sentinel'
    cmd = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", tr,
        "/sc", "hourly",
        "/f",
    ]
    print(f"[register_phoenix] Creating {task_name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[register_phoenix] ERROR: {result.stderr}")
    return result.returncode == 0


def delete_task(name: str):
    cmd = ["schtasks", "/delete", "/tn", name, "/f"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[register_phoenix] ERROR: {result.stderr}")
    return result.returncode == 0


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["create", "delete"], default="create")
    args = p.parse_args()

    if args.action == "delete":
        for name in ["Yeon_PhoenixWake", "Yeon_ContextGuardian"]:
            delete_task(name)
        return

    ok1 = create_wake_task()
    ok2 = create_guardian_task()

    if ok1 and ok2:
        print("[register_phoenix] Phoenix Protocol registered successfully.")
    else:
        print("[register_phoenix] Some tasks failed.")


if __name__ == "__main__":
    main()
