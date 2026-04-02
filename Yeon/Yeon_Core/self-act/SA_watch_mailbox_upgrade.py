"""SA_watch_mailbox_upgrade — PGTP-integrated mail processing."""
from SA_watch_mailbox import process_mailbox as base_process
from pgtp_mail_generator import build_ack_CU, queue_ack_CU
from auto_reply_schedule import auto_reply_schedule


def process_mailbox() -> list:
    """Process mailbox with PGTP ack generation and schedule auto-reply."""
    results = base_process()
    for item in results:
        # Generate generic ack CU for every processed mail
        ack_cu = build_ack_CU(item)
        queue_ack_CU(ack_cu)
        # Special handling for schedule intent
        auto_reply_schedule({"id": item["id"], "from": item["from"], "intent": "schedule"})
    return results


if __name__ == "__main__":
    results = process_mailbox()
    print(f"SA_watch_mailbox_upgrade: processed {len(results)} mail(s)")
