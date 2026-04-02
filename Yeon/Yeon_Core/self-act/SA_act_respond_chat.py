"""
SA_act_respond_chat — Send a response via Hub command queue.
Input: CognitiveUnit or intent/payload
Output: written command file in Yeon_Core/hub/outbox/
"""
import json
import time
from pathlib import Path
from typing import Optional
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hub.pgtp_bridge import CognitiveUnit, build_pgtp_hub_command, build_hub_command

OUTBOX_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/hub/outbox")


def send_response(cu: CognitiveUnit) -> Path:
    """Write a hub command to the outbox queue."""
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    cmd = build_pgtp_hub_command(cu)
    filename = f"{int(time.time() * 1000)}-{cu.intent}.json"
    path = OUTBOX_DIR / filename
    path.write_text(json.dumps(cmd, ensure_ascii=False), encoding="utf-8")
    return path


def send_simple(intent: str, body: str, sender: str = "Yeon") -> Path:
    """Send a non-PGTP simple chat message."""
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    cmd = build_hub_command(intent, body)
    filename = f"{int(time.time() * 1000)}-{intent}.json"
    path = OUTBOX_DIR / filename
    path.write_text(json.dumps(cmd, ensure_ascii=False), encoding="utf-8")
    return path


def main():
    cu = CognitiveUnit(intent="react", payload="Acknowledged. Processing.", sender="Yeon")
    path = send_response(cu)
    print(f"SA_act_respond_chat: queued -> {path.name}")


if __name__ == "__main__":
    main()
