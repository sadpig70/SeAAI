"""Phase 4 verification — ADP Daemon."""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hub.stdin_injector import open_pipe, close_pipe, write_json_line
from hub.health_checker import check_process_alive
from hub.outbox_watcher import scan


def test_daemon_alive_10sec():
    proc = open_pipe("Yeon", "seaai-general", tick=5.0)
    time.sleep(10)
    alive = check_process_alive(proc)
    close_pipe(proc)
    assert alive, "Hub transport died within 10s"
    print("  [PASS] daemon alive 10s")


def test_outbox_consumed():
    import json
    from hub import outbox_watcher
    outbox_watcher.OUTBOX.mkdir(parents=True, exist_ok=True)
    # Clean outbox first
    for f in outbox_watcher.OUTBOX.glob("*.json"):
        f.unlink()
    test_cmd = {"intent": "chat", "body": "daemon test"}
    path = outbox_watcher.OUTBOX / "test-daemon.json"
    path.write_text(json.dumps(test_cmd), encoding="utf-8")

    proc = open_pipe("Yeon", "seaai-general", tick=5.0)
    from hub.outbox_processor import run_once
    success = run_once(proc, "Yeon")
    close_pipe(proc)
    assert success, "Outbox command not sent"
    assert not path.exists(), "Outbox file not deleted"
    print("  [PASS] outbox consumed by daemon")


def main():
    print("Phase 4 Verification")
    test_daemon_alive_10sec()
    test_outbox_consumed()
    print("Phase 4 — ALL PASS")


if __name__ == "__main__":
    main()
