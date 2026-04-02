"""Health checker for ADP daemon."""
import subprocess
from pathlib import Path


def check_process_alive(proc: subprocess.Popen) -> bool:
    return proc.poll() is None


def check_echo_freshness(echo_path: Path, max_hours: float = 24.0) -> bool:
    if not echo_path.exists():
        return False
    import json
    from datetime import datetime
    try:
        data = json.loads(echo_path.read_text(encoding="utf-8"))
        ts = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        elapsed = (datetime.now() - ts).total_seconds() / 3600
        return elapsed <= max_hours
    except Exception:
        return False


def check_STOP_FLAG(flag_path: Path) -> bool:
    return flag_path.exists()
