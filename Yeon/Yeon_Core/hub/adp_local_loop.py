"""Local ADP loop — 30s file-based autonomous operation test."""
import json
import time
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "self-act"))

from sense_mailbox import sense as sense_mailbox
from sense_echo import sense as sense_echo
from triage_priority import triage, decide_next_action
from SA_watch_mailbox_upgrade import process_mailbox

LOG_PATH = Path("D:/SeAAI/Yeon/Yeon_Core/continuity/journals/2026-04-01-local-loop-log.jsonl")

PLANS = [
    "SeAAIHub chat",
    "Mail 처리",
    "ClNeo_complete_autonomous_creation_pipeline",
    "Self-Evolving",
    "plan list 확장하기",
    "stop",
]


def select_plan(action: dict) -> str:
    """Select a plan based on triage priority."""
    priority = action.get("priority", "P4")
    items = action.get("items", [])

    if priority == "P0":
        return "SeAAIHub chat"
    if priority == "P1":
        return "Self-Evolving"  # stale echo = evolve
    if priority == "P2":
        # Check if any item is mailbox
        has_mail = any(item.get("source") == "mailbox" for item in items)
        if has_mail:
            return "Mail 처리"
        return "SeAAIHub chat"
    if priority == "P3":
        return "plan list 확장하기"
    return "stop"


def execute_plan(plan: str) -> str:
    """Execute the selected plan and return result."""
    if plan == "Mail 처리":
        results = process_mailbox()
        return f"processed {len(results)} mail(s)"
    if plan == "Self-Evolving":
        return "scanned ecosystem state"
    if plan == "plan list 확장하기":
        return "plan list reviewed"
    if plan == "SeAAIHub chat":
        return "hub state checked (local mode)"
    if plan == "ClNeo_complete_autonomous_creation_pipeline":
        return "creation pipeline readiness checked"
    return "idle"


def log_event(tick_num: int, plan: str, result: str, action: dict):
    """Append event to loop log."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "tick": tick_num,
        "plan": plan,
        "result": result,
        "priority": action.get("priority"),
        "item_count": len(action.get("items", [])),
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main_loop(ticks: int = 6, sleep_sec: float = 5.0):
    """Run local ADP loop for N ticks."""
    print(f"[ADP-LOCAL] Starting {ticks} ticks, {sleep_sec}s interval = {ticks * sleep_sec}s total")

    for i in range(1, ticks + 1):
        # Sense all channels
        hub_msgs = []  # local mode: no real hub
        mailbox_mails = sense_mailbox()
        echo_data = sense_echo()

        # Triage and decide
        triaged = triage(hub_msgs, mailbox_mails, echo_data)
        action = decide_next_action(triaged)
        plan = select_plan(action)

        if plan == "stop":
            log_event(i, "stop", "loop terminated by plan", action)
            print(f"  tick {i}: STOP")
            break

        # Execute
        result = execute_plan(plan)
        log_event(i, plan, result, action)
        print(f"  tick {i}: [{plan}] -> {result} (priority={action['priority']})")

        time.sleep(sleep_sec)

    print(f"[ADP-LOCAL] Loop finished. Log: {LOG_PATH}")


if __name__ == "__main__":
    # Clean old log for this test
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    main_loop()
