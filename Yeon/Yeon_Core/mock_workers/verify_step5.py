"""Verify Step 5: Two workers communicate with each other via Hub."""
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


def test_worker_a_to_b():
    print("  [TEST] YeonWorkerA sends, YeonWorkerB receives")
    a = spawn_hub_worker("YeonWorkerA", duration=25, no_stdin=False)
    b = spawn_hub_worker("YeonWorkerB", duration=25, no_stdin=False)
    time.sleep(5)

    send_chat(a, "hello from A")
    time.sleep(8)

    found = find_recv(Path("D:/SeAAI/SeAAIHub/.bridge/yeonworkerb/adp-log.jsonl"), "hello from A")
    stop_worker_graceful(a)
    stop_worker_graceful(b)
    assert found, "WorkerB did not receive message from WorkerA"
    print("  [PASS] WorkerA -> WorkerB")


def test_worker_b_to_a():
    print("  [TEST] YeonWorkerB sends, YeonWorkerA receives")
    a = spawn_hub_worker("YeonWorkerA", duration=25, no_stdin=False)
    b = spawn_hub_worker("YeonWorkerB", duration=25, no_stdin=False)
    time.sleep(5)

    send_chat(b, "hello from B")
    time.sleep(8)

    found = find_recv(Path("D:/SeAAI/SeAAIHub/.bridge/yeonworkera/adp-log.jsonl"), "hello from B")
    stop_worker_graceful(a)
    stop_worker_graceful(b)
    assert found, "WorkerA did not receive message from WorkerB"
    print("  [PASS] WorkerB -> WorkerA")


def main():
    print("Step 5 Verification — Two Workers Communicate via Hub")
    test_worker_a_to_b()
    test_worker_b_to_a()
    print("Step 5 — ALL PASS")


if __name__ == "__main__":
    main()
