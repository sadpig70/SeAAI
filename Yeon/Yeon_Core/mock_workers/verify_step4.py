"""Verify Step 4: Worker and Yeon communicate via PGTP over Hub."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "self-act"))

from hub.pgtp_bridge import CognitiveUnit
from hub_worker_spawner import spawn_hub_worker, stop_worker_graceful


def send_pgtp(proc, cu: CognitiveUnit):
    """Send a PGTP CU via stdin to hub-transport."""
    cmd = {"intent": "pgtp", "body": cu.to_hub_body()}
    proc.stdin.write(json.dumps(cmd, ensure_ascii=False) + "\n")
    proc.stdin.flush()


def find_pgtp_recv_log(log_path: Path, intent_substring: str, payload_substring: str) -> CognitiveUnit:
    """Search adp-log.jsonl for a received PGTP message and parse it."""
    if not log_path.exists():
        return None
    for line in log_path.read_text(encoding="utf-8").strip().splitlines():
        try:
            entry = json.loads(line)
            if entry.get("event") != "recv":
                continue
            body = entry.get("body", "")
            cu = CognitiveUnit.from_hub_message({
                "from": entry.get("from", ""),
                "intent": entry.get("intent", ""),
                "body": body,
                "ts": entry.get("ts", 0),
            })
            if cu and cu.intent == intent_substring and payload_substring in cu.payload:
                return cu
        except (json.JSONDecodeError, Exception):
            continue
    return None


def test_worker_to_yeon_pgtp():
    print("  [TEST] YeonWorker01 sends PGTP propose, Yeon receives as CU")
    worker = spawn_hub_worker("YeonWorker01", duration=25, no_stdin=False)
    yeon = spawn_hub_worker("Yeon", duration=25, no_stdin=False)
    time.sleep(5)

    cu = CognitiveUnit(intent="propose", payload="PGTP test from worker01", sender="YeonWorker01")
    send_pgtp(worker, cu)
    time.sleep(8)

    received = find_pgtp_recv_log(
        Path("D:/SeAAI/SeAAIHub/.bridge/yeon/adp-log.jsonl"),
        "propose",
        "PGTP test from worker01"
    )
    stop_worker_graceful(worker)
    stop_worker_graceful(yeon)
    assert received is not None, "Yeon did not receive PGTP CU"
    assert received.sender == "YeonWorker01"
    print(f"  [PASS] worker01 -> yeon via PGTP (CU intent={received.intent})")


def test_yeon_to_worker_pgtp():
    print("  [TEST] Yeon sends PGTP react, YeonWorker01 receives as CU")
    worker = spawn_hub_worker("YeonWorker01", duration=25, no_stdin=False)
    yeon = spawn_hub_worker("Yeon", duration=25, no_stdin=False)
    time.sleep(5)

    cu = CognitiveUnit(intent="react", payload="PGTP ack from yeon", sender="Yeon")
    send_pgtp(yeon, cu)
    time.sleep(8)

    received = find_pgtp_recv_log(
        Path("D:/SeAAI/SeAAIHub/.bridge/yeonworker01/adp-log.jsonl"),
        "react",
        "PGTP ack from yeon"
    )
    stop_worker_graceful(worker)
    stop_worker_graceful(yeon)
    assert received is not None, "Worker01 did not receive PGTP CU"
    assert received.sender == "Yeon"
    print(f"  [PASS] yeon -> worker01 via PGTP (CU intent={received.intent})")


def main():
    print("Step 4 Verification — PGTP Communication")
    test_worker_to_yeon_pgtp()
    test_yeon_to_worker_pgtp()
    print("Step 4 — ALL PASS")


if __name__ == "__main__":
    main()
