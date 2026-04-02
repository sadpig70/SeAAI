"""Spawn hub-connected worker agents."""
import subprocess
import sys
from pathlib import Path

HUB_TRANSPORT = Path("D:/SeAAI/SeAAIHub/tools/hub-transport.py")
PYTHON = sys.executable


def spawn_hub_worker(agent_id: str, room: str = "seaai-general", duration: int = 30, no_stdin: bool = True) -> subprocess.Popen:
    """Spawn a subprocess running hub-transport.py for a worker."""
    cmd = [
        PYTHON, str(HUB_TRANSPORT),
        "--agent-id", agent_id,
        "--room", room,
        "--tick", "5",
        "--duration", str(duration),
    ]
    if no_stdin:
        cmd.append("--no-stdin")
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )


def stop_worker_graceful(proc: subprocess.Popen):
    """Send stop command via stdin for graceful shutdown."""
    if proc.poll() is None:
        proc.stdin.write('{"action":"stop"}\n')
        proc.stdin.flush()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=3)
    if proc.poll() is None:
        proc.kill()


def stop_worker(proc: subprocess.Popen):
    """Gracefully stop a worker."""
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
