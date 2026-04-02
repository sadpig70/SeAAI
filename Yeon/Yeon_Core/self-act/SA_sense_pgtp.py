"""
SA_sense_pgtp — Poll Hub for PGTP CognitiveUnits.
Input: agent_id, room
Output: list[CognitiveUnit]
"""
import json
from pathlib import Path
from typing import List, Optional
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hub.pgtp_bridge import CognitiveUnit

LOG_DIR = Path("D:/SeAAI/SeAAIHub/.bridge")


def poll_hub(agent_id: str = "Yeon", room: str = "seaai-general", last_n: int = 20) -> List[CognitiveUnit]:
    """Read hub-transport log and extract received PGTP messages as CUs."""
    log_path = LOG_DIR / agent_id.lower() / "adp-log.jsonl"
    cus = []
    if not log_path.exists():
        return cus

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    recent = lines[-last_n:] if len(lines) > last_n else lines

    for line in recent:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("event") != "recv":
            continue
        # Build a synthetic hub message from log entry
        hub_msg = {
            "from": entry.get("from", ""),
            "intent": entry.get("intent", ""),
            "body": entry.get("body", ""),
            "ts": entry.get("ts", 0),
            "id": entry.get("id", ""),
        }
        cu = CognitiveUnit.from_hub_message(hub_msg)
        if cu:
            cus.append(cu)
    return cus


def filter_self(cus: List[CognitiveUnit], sender: str = "Yeon") -> List[CognitiveUnit]:
    return [cu for cu in cus if cu.sender != sender]


def freshness_check(cus: List[CognitiveUnit], after_ts: float = 0) -> List[CognitiveUnit]:
    return [cu for cu in cus if cu.ts > after_ts]


def main():
    cus = poll_hub()
    filtered = filter_self(cus)
    print(f"SA_sense_pgtp: total={len(cus)}, filtered={len(filtered)}")
    for cu in filtered:
        print(f"  [{cu.intent}] from={cu.sender}: {cu.payload[:60]}")


if __name__ == "__main__":
    main()
