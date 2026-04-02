"""Phase 1 verification — PGTP ecosystem."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hub.pgtp_bridge import CognitiveUnit, build_pgtp_hub_command, compact_encode, compact_decode, build_schedule, build_confirm
from hub.dag_tracker import validate_dag, has_cycle
from hub import outbox_watcher, stdin_injector, retry_policy


def test_compact_roundtrip():
    cu = CognitiveUnit(intent="query", payload="test", sender="Yeon")
    body = compact_encode(cu)
    recovered = compact_decode(body, CognitiveUnit)
    assert recovered.intent == "query"
    assert recovered.payload == "test"
    print("  [PASS] compact roundtrip")


def test_schedule_confirm():
    s = build_schedule("ClNeo", "14:00 session")
    c = build_confirm(s.id, "OK")
    assert s.intent == "schedule"
    assert c.intent == "confirm"
    assert c.context == [s.id]
    print("  [PASS] schedule/confirm")


def test_dag():
    history = {"cu_001"}
    cu = CognitiveUnit(intent="react", payload="ok", context=["cu_001"])
    assert validate_dag(cu, history)
    print("  [PASS] dag validation")


def test_outbox_flow():
    import json
    outbox_watcher.OUTBOX.mkdir(parents=True, exist_ok=True)
    test_path = outbox_watcher.OUTBOX / "test-cmd.json"
    test_path.write_text(json.dumps({"intent": "chat", "body": "hi"}), encoding="utf-8")
    files = outbox_watcher.scan()
    path, data = outbox_watcher.read_oldest(files)
    assert data["intent"] == "chat"
    outbox_watcher.delete_after_send(path)
    print("  [PASS] outbox flow")


def test_retry():
    fail_count = [0]
    def fail_twice():
        fail_count[0] += 1
        return fail_count[0] >= 3
    success, attempts = retry_policy.attempt(fail_twice)
    assert success and attempts == 3
    print("  [PASS] retry policy")


def main():
    print("Phase 1 Verification")
    test_compact_roundtrip()
    test_schedule_confirm()
    test_dag()
    test_outbox_flow()
    test_retry()
    print("Phase 1 — ALL PASS")


if __name__ == "__main__":
    main()
