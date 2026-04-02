"""Verify Step 6: Four workers broadcast and receive via Hub."""
import json
import time
from pathlib import Path
from hub_worker_spawner import spawn_hub_worker, stop_worker_graceful


def send_chat(proc, body: str):
    cmd = json.dumps({"intent": "chat", "body": body}, ensure_ascii=False)
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()


def find_recv(log_path: Path, substring: str) -> bool:
    if not log_path.exists():
        return False
    for line in log_path.read_text(encoding="utf-8").strip().splitlines():
        try:
            entry = json.loads(line)
            if entry.get("event") == "recv" and substring in entry.get("body", ""):
                return True
        except json.JSONDecodeError:
            continue
    return False


def test_4_worker_broadcast():
    print("  [TEST] spawn 4 workers on Hub")
    workers = [
        spawn_hub_worker(f"YeonWorker0{i}", duration=30, no_stdin=False)
        for i in range(1, 5)
    ]
    time.sleep(5)

    sender = workers[0]
    send_chat(sender, "broadcast from worker01 to all")
    print("    -> sent broadcast")
    time.sleep(10)

    # Verify all 3 other workers received
    received_count = 0
    for i in range(2, 5):
        log = Path(f"D:/SeAAI/SeAAIHub/.bridge/yeonworker0{i}/adp-log.jsonl")
        if find_recv(log, "broadcast from worker01 to all"):
            received_count += 1
            print(f"    -> YeonWorker0{i} received")

    for w in workers:
        stop_worker_graceful(w)

    assert received_count == 3, f"Only {received_count}/3 workers received broadcast"
    print("  [PASS] 4-worker broadcast (3/3 receivers)")


def main():
    print("Step 6 Verification — Four Workers Hub Broadcast")
    test_4_worker_broadcast()
    print("Step 6 — ALL PASS")


if __name__ == "__main__":
    main()
