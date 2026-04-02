"""
P0 Verification Script — PGTP Bridge + SelfAct L1 modules.
"""
import json
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hub.pgtp_bridge import CognitiveUnit, build_pgtp_hub_command
from SA_sense_pgtp import poll_hub, filter_self, freshness_check
from SA_act_respond_chat import send_response, send_simple
from SA_watch_mailbox import scan_inbox, parse_frontmatter, process_mailbox


def verify_bridge():
    print("[V] Bridge verification")
    cu = CognitiveUnit(intent="propose", payload="Hello PGTP", sender="Yeon")
    assert cu.validate(), "CU validation failed"
    cmd = build_pgtp_hub_command(cu)
    assert cmd["intent"] == "pgtp", "Hub command intent wrong"
    body = json.loads(cmd["body"])
    assert body["pgtp"] == "1.0", "PGTP version wrong"
    assert body["intent"] == "propose", "CU intent round-trip failed"
    print("  -> PASS")


def verify_sense():
    print("[V] SA_sense_pgtp verification")
    cus = poll_hub()
    filtered = filter_self(cus)
    assert isinstance(cus, list), "poll_hub must return list"
    assert isinstance(filtered, list), "filter_self must return list"
    print(f"  -> PASS (cus={len(cus)}, filtered={len(filtered)})")


def verify_act():
    print("[V] SA_act_respond_chat verification")
    cu = CognitiveUnit(intent="react", payload="Roger that.", sender="Yeon")
    path = send_response(cu)
    assert path.exists(), "Queued file not created"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["intent"] == "pgtp", "Queued command intent wrong"
    # cleanup
    path.unlink()
    print(f"  -> PASS (queued={path.name})")


def verify_mailbox():
    print("[V] SA_watch_mailbox verification")
    mails = scan_inbox()
    assert isinstance(mails, list), "scan_inbox must return list"
    sample_fm = parse_frontmatter("---\nfrom: ClNeo\nid: test-001\n---\n# body")
    assert sample_fm.get("from") == "ClNeo", "Frontmatter parse failed"
    results = process_mailbox()
    assert isinstance(results, list), "process_mailbox must return list"
    print(f"  -> PASS (inbox={len(mails)}, processed={len(results)})")


def main():
    print("=" * 50)
    print("P0 SelfAct Verification")
    print("=" * 50)
    verify_bridge()
    verify_sense()
    verify_act()
    verify_mailbox()
    print("=" * 50)
    print("ALL P0 VERIFICATIONS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()
