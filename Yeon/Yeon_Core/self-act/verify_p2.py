"""Phase 2 verification — SelfAct expansion."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sense_hub import sense
from sense_mailbox import sense as sense_mb
from sense_echo import sense as sense_echo
from triage_priority import triage, decide_next_action
from checkpoint import save_STATE
from SA_loop_autonomous import tick
from pgtp_mail_generator import build_ack_CU, queue_ack_CU
from auto_reply_schedule import detect_schedule_intent, auto_reply_schedule
from SA_watch_mailbox_upgrade import process_mailbox


def test_sense_and_triage():
    hub = sense()
    mb = sense_mb()
    echo = sense_echo()
    triaged = triage(hub, mb, echo)
    action = decide_next_action(triaged)
    assert "priority" in action
    print(f"  [PASS] sense+triage (priority={action['priority']})")


def test_checkpoint():
    path = save_STATE({"what_i_was_doing": "test", "open_threads": []})
    assert path.exists()
    print("  [PASS] checkpoint save")


def test_loop_autonomous_tick():
    action = tick()
    assert "priority" in action
    print(f"  [PASS] autonomous tick (priority={action['priority']})")


def test_pgtp_ack():
    cu = build_ack_CU({"id": "test-001", "from": "ClNeo"})
    assert cu.intent == "react"
    path = queue_ack_CU(cu)
    assert path.exists()
    path.unlink()
    print("  [PASS] PGTP ack CU")


def test_auto_reply_schedule():
    meta = {"id": "sched-001", "from": "ClNeo", "intent": "schedule"}
    assert detect_schedule_intent(meta)
    result = auto_reply_schedule(meta)
    assert result
    print("  [PASS] auto reply schedule")


def test_mailbox_upgrade():
    results = process_mailbox()
    assert isinstance(results, list)
    print(f"  [PASS] mailbox upgrade (processed={len(results)})")


def main():
    print("Phase 2 Verification")
    test_sense_and_triage()
    test_checkpoint()
    test_loop_autonomous_tick()
    test_pgtp_ack()
    test_auto_reply_schedule()
    test_mailbox_upgrade()
    print("Phase 2 — ALL PASS")


if __name__ == "__main__":
    main()
