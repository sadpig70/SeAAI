"""Sense MailBox for pending mails."""
from SA_watch_mailbox import scan_inbox


def sense() -> list:
    """Return list of pending inbox mail paths."""
    return scan_inbox()
