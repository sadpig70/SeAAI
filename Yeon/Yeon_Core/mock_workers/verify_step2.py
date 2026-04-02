"""Verify Step 2: one worker connects to Hub and survives 10s."""
import time
import json
from pathlib import Path
from hub_worker_spawner import spawn_hub_worker, stop_worker


def test_worker_survives_10s():
    print("  [TEST] spawn YeonWorker01 on Hub")
    proc = spawn_hub_worker("YeonWorker01", duration=15)
    time.sleep(10)
    alive = proc.poll() is None
    stop_worker(proc)
    assert alive, "Worker died before 10s"
    print("  [PASS] worker alive 10s")


def test_worker_log_has_session_start():
    log_path = Path("D:/SeAAI/SeAAIHub/.bridge/yeonworker01/adp-log.jsonl")
    assert log_path.exists(), "Worker log not found"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    found = any(json.loads(line).get("event") == "session_start" for line in lines)
    assert found, "No session_start in worker log"
    print("  [PASS] worker log has session_start")


def main():
    print("Step 2 Verification — Worker Hub Connection")
    test_worker_survives_10s()
    test_worker_log_has_session_start()
    print("Step 2 — ALL PASS")


if __name__ == "__main__":
    main()
