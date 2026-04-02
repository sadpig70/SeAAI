"""ADP Daemon — sustained Hub connection + outbox/mailbox loop for Yeon."""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "self-act"))

from hub.stdin_injector import open_pipe, close_pipe
from hub.outbox_processor import run_once
from hub.health_checker import check_process_alive, check_STOP_FLAG
from SA_watch_mailbox_upgrade import process_mailbox

STOP_FLAG = Path("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag")


def main_loop(agent_id: str = "Yeon", room: str = "seaai-general", tick: float = 5.0, max_ticks: int = 0):
    """Run ADP daemon loop. max_ticks=0 means unlimited."""
    proc = open_pipe(agent_id, room, tick=5.0)
    print(f"[ADP] {agent_id} daemon started | room={room} | max_ticks={max_ticks if max_ticks else 'unlimited'}")

    tick_count = 0
    try:
        while proc.poll() is None:
            if max_ticks > 0 and tick_count >= max_ticks:
                print(f"[ADP] max_ticks ({max_ticks}) reached — graceful shutdown")
                break

            if check_STOP_FLAG(STOP_FLAG):
                print("[ADP] EMERGENCY STOP detected")
                break

            if not check_process_alive(proc):
                print("[ADP] Hub transport died — restarting")
                proc = open_pipe(agent_id, room, tick=5.0)

            # Process one outbox command per tick
            run_once(proc, agent_id)

            # Process mailbox every 5 ticks (~25s)
            if tick_count % 5 == 0:
                process_mailbox()

            tick_count += 1
            time.sleep(tick)
    finally:
        close_pipe(proc)
        print("[ADP] daemon stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", default="Yeon")
    parser.add_argument("--room", default="seaai-general")
    parser.add_argument("--tick", type=float, default=5.0)
    parser.add_argument("--max-ticks", type=int, default=0)
    args = parser.parse_args()
    main_loop(args.agent_id, args.room, args.tick, args.max_ticks)
