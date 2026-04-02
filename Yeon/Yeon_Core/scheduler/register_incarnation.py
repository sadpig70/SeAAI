"""register_incarnation.py — Register Yeon headless tasks with Windows Task Scheduler."""
import argparse
import subprocess
import sys
from pathlib import Path

WORK_DIR = Path("D:/SeAAI/Yeon")
PYTHON = Path(sys.executable)
INCARNATE = WORK_DIR / "Yeon_Core" / "incarnate.py"


def create_task(name: str, schedule: str, start_time: str, mode: str, extra_args: str = ""):
    task_name = f"Yeon_{name}"
    tr = f'"{PYTHON}" "{INCARNATE}" --mode {mode} {extra_args}'

    cmd = [
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", tr,
        "/sc", schedule,
        "/st", start_time,
        "/f",
    ]

    print(f"[register] Creating task '{task_name}'")
    print(f"[register] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[register] ERROR: {result.stderr}")
    else:
        print(f"[register] OK: {task_name}")
    return result.returncode == 0


def delete_task(name: str):
    task_name = f"Yeon_{name}"
    cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]
    print(f"[register] Deleting task '{task_name}'")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[register] ERROR: {result.stderr}")
    return result.returncode == 0


def list_tasks():
    cmd = ["schtasks", "/query", "/fo", "list", "/v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.splitlines()
    yeon_tasks = []
    current = []
    for line in lines:
        if line.strip().lower().startswith("task name"):
            if current:
                yeon_tasks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        yeon_tasks.append("\n".join(current))

    filtered = [t for t in yeon_tasks if "Yeon_" in t]
    if not filtered:
        print("[register] No Yeon tasks found.")
        return

    print(f"[register] Found {len(filtered)} Yeon task(s):\n")
    for t in filtered:
        print(t)
        print("-" * 40)


def main():
    p = argparse.ArgumentParser(description="Yeon Task Scheduler Registration")
    p.add_argument("--action", choices=["create", "delete", "list"], default="create")
    p.add_argument("--name", default="", help="Specific task name to delete")
    args = p.parse_args()

    if args.action == "list":
        list_tasks()
        return

    if args.action == "delete":
        if args.name:
            delete_task(args.name)
        else:
            for n in ["DailyDream", "HourlySentinel"]:
                delete_task(n)
        return

    # action == create
    ok1 = create_task("DailyDream", "daily", "00:00", "dream")
    ok2 = create_task("HourlySentinel", "hourly", "00:00", "sentinel")

    if ok1 and ok2:
        print("[register] All tasks created successfully.")
    else:
        print("[register] Some tasks failed. Check output above.")


if __name__ == "__main__":
    main()
