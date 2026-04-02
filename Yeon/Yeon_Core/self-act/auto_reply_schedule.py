"""Auto-reply to schedule intent mails with confirm CU."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hub.pgtp_bridge import build_schedule, build_confirm
from pgtp_mail_generator import queue_ack_CU


def detect_schedule_intent(mail_meta: dict) -> bool:
    return mail_meta.get("intent", "").lower() == "schedule"


def generate_confirm_response(schedule_meta: dict) -> str:
    sender = schedule_meta.get("from", "Unknown")
    return f"Schedule from {sender} accepted. Yeon will confirm via PGTP."


def auto_reply_schedule(mail_meta: dict) -> bool:
    """If mail is schedule intent, generate confirm CU and queue it."""
    if not detect_schedule_intent(mail_meta):
        return False
    mail_id = mail_meta.get("id", "unknown")
    sender = mail_meta.get("from", "Unknown")
    payload = generate_confirm_response(mail_meta)
    # We don't have the original schedule CU id, so we use mail_id as ref
    confirm_cu = build_confirm(mail_id, payload)
    queue_ack_CU(confirm_cu)
    return True
