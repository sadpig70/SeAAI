"""Outbox processor — watches outbox and sends commands to Hub."""
import time
from hub import outbox_watcher, stdin_injector, retry_policy


def run_once(proc, agent_id: str = "Yeon") -> bool:
    """Process one pending command from outbox."""
    files = outbox_watcher.scan()
    path, data = outbox_watcher.read_oldest(files)
    if path is None:
        return False

    success, _ = retry_policy.attempt(stdin_injector.write_json_line, proc, data)
    if success:
        outbox_watcher.delete_after_send(path)
    return success


def main_loop(agent_id: str = "Yeon", room: str = "seaai-general", tick: float = 1.0):
    """Run outbox processor loop."""
    proc = stdin_injector.open_pipe(agent_id, room, tick=5.0)
    try:
        while proc.poll() is None:
            run_once(proc, agent_id)
            time.sleep(tick)
    finally:
        stdin_injector.close_pipe(proc)


if __name__ == "__main__":
    main_loop()
