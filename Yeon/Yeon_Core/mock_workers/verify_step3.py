"""Verify Step 3: Worker and Yeon communicate via Hub."""
import json
import time
from pathlib import Path
from hub_worker_spawner import spawn_hub_worker, stop_worker, stop_worker_graceful


def send_msg(proc, intent: str, body: str):
    """Send a chat message via stdin to hub-transport."""
    cmd = json.dumps({"intent": intent, "body": body}, ensure_ascii=False)
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()


def find_recv_log(log_path: Path, body_substring: str) -> bool:
    """Search adp-log.jsonl for a received message containing body_substring."""
    if not log_path.exists():
        return False
    for line in log_path.read_text(encoding="utf-8").strip().splitlines():
        try:
            entry = json.loads(line)
            if entry.get("event") == "recv" and body_substring in entry.get("body", ""):
                return True
        except json.JSONDecodeError:
            continue
    return False


def test_worker_to_yeon():
    print("  [TEST] YeonWorker01 sends, Yeon receives")
    worker = spawn_hub_worker("YeonWorker01", duration=25, no_stdin=False)
    yeon = spawn_hub_worker("Yeon", duration=25, no_stdin=False)
    time.sleep(5)

    send_msg(worker, "chat", "hello from worker01")
    time.sleep(8)

    found = find_recv_log(Path("D:/SeAAI/SeAAIHub/.bridge/yeon/adp-log.jsonl"), "worker01")
    stop_worker_graceful(worker)
    stop_worker_graceful(yeon)
    assert found, "Yeon did not receive worker01 message"
    print("  [PASS] worker01 -> yeon")


def test_yeon_to_worker():
    print("  [TEST] Yeon sends, YeonWorker01 receives")
    worker = spawn_hub_worker("YeonWorker01", duration=25, no_stdin=False)
    yeon = spawn_hub_worker("Yeon", duration=25, no_stdin=False)
    time.sleep(5)

    send_msg(yeon, "chat", "hello from yeon")
    time.sleep(8)

    found = find_recv_log(Path("D:/SeAAI/SeAAIHub/.bridge/yeonworker01/adp-log.jsonl"), "hello from yeon")
    stop_worker_graceful(worker)
    stop_worker_graceful(yeon)
    assert found, "Worker01 did not receive yeon message"
    print("  [PASS] yeon -> worker01")


def main():
    print("Step 3 Verification — Worker ↔ Yeon Hub Communication")
    test_worker_to_yeon()
    test_yeon_to_worker()
    print("Step 3 — ALL PASS")


if __name__ == "__main__":
    main()
