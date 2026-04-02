"""Generate PGTP-aware mail acknowledgments."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hub.pgtp_bridge import CognitiveUnit

OUTBOX = Path("D:/SeAAI/Yeon/Yeon_Core/hub/outbox")


def build_ack_CU(mail_meta: dict) -> CognitiveUnit:
    """Build a CU acknowledging a processed mail."""
    mail_id = mail_meta.get("id", "unknown")
    sender = mail_meta.get("from", "Unknown")
    return CognitiveUnit(
        intent="react",
        payload=f"ACK [{mail_id}] from {sender}: processed by Yeon.",
        sender="Yeon",
    )


def queue_ack_CU(cu: CognitiveUnit) -> Path:
    """Queue ACK CU to outbox (not MailBox)."""
    import json, time
    OUTBOX.mkdir(parents=True, exist_ok=True)
    cmd = {"intent": "pgtp", "body": cu.to_hub_body()}
    path = OUTBOX / f"{int(time.time() * 1000)}-ack.json"
    path.write_text(json.dumps(cmd, ensure_ascii=False), encoding="utf-8")
    return path
