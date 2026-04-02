"""Inject JSON commands to hub-transport.py via stdin pipe."""
import json
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable
HUB_TRANSPORT = Path("D:/SeAAI/SeAAIHub/tools/hub-transport.py")


def open_pipe(agent_id: str, room: str, tick: float = 5.0) -> subprocess.Popen:
    """Open a subprocess pipe to hub-transport.py."""
    cmd = [
        PYTHON, str(HUB_TRANSPORT),
        "--agent-id", agent_id,
        "--room", room,
        "--tick", str(tick),
    ]
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )


def write_json_line(proc: subprocess.Popen, data: dict) -> bool:
    """Write a JSON line to the pipe."""
    if proc.stdin is None or proc.poll() is not None:
        return False
    line = json.dumps(data, ensure_ascii=False) + "\n"
    proc.stdin.write(line)
    proc.stdin.flush()
    return True


def close_pipe(proc: subprocess.Popen) -> bool:
    """Send stop and close the pipe gracefully."""
    try:
        if proc.poll() is None:
            write_json_line(proc, {"action": "stop"})
            proc.wait(timeout=5)
    except Exception:
        proc.kill()
    return True
