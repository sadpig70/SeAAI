"""SA_loop_autonomous — Yeon autonomous operation kernel."""
import time
from datetime import datetime

from sense_hub import sense as sense_hub
from sense_mailbox import sense as sense_mailbox
from sense_echo import sense as sense_echo
from triage_priority import triage, decide_next_action
from checkpoint import save_STATE, write_journal_if_significant
from SA_self_reflect import reflect


def tick(agent_id: str = "Yeon", room: str = "seaai-general", tick_num: int = 0) -> dict:
    """Execute one autonomous tick."""
    hub_msgs = sense_hub(agent_id, room)
    mailbox_mails = sense_mailbox()
    echo_data = sense_echo()

    triaged = triage(hub_msgs, mailbox_mails, echo_data)
    action = decide_next_action(triaged)

    # Self-reflection every 6 ticks (~30s in 5s interval)
    reflection_result = None
    if tick_num > 0 and tick_num % 6 == 0:
        reflection_result = reflect()

    # Checkpoint every tick
    significant = action["priority"] in ("P0", "P1") or (reflection_result and reflection_result["recorded"])
    context = {
        "what_i_was_doing": f"autonomous tick: priority={action['priority']}",
        "open_threads": [f"hub:{len(hub_msgs)}", f"mailbox:{len(mailbox_mails)}", f"stale_echoes:{sum(1 for e in echo_data.values() if e.get('_stale'))}"],
    }
    if reflection_result:
        context["last_reflection"] = reflection_result["proposal"]["gap"]
    save_STATE(context)
    if significant:
        write_journal_if_significant(True, f"Priority {action['priority']} detected: {len(action['items'])} items")

    return {"action": action, "reflection": reflection_result}


def main_loop(ticks: int = 3, agent_id: str = "Yeon", room: str = "seaai-general"):
    """Run N ticks for testing."""
    for i in range(ticks):
        result = tick(agent_id, room, tick_num=i)
        action = result["action"]
        ref = result["reflection"]
        print(f"tick {i+1}: {action['priority']} ({len(action['items'])} items)")
        if ref:
            print(f"  -> reflection: {ref['proposal']['gap']} (recorded={ref['recorded']})")
        time.sleep(1)


if __name__ == "__main__":
    main_loop(ticks=7)
