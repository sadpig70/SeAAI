"""Build schedule/confirm data for PGTP v1.0.
Returns dicts to avoid circular import with pgtp_bridge.
"""


def build_schedule(target: str, payload: str, sender: str = "Yeon") -> dict:
    """Build a schedule intent data."""
    return {
        "intent": "schedule",
        "target": target,
        "payload": payload,
        "sender": sender,
        "accept": "confirm intent required",
    }


def build_confirm(ref_id: str, payload: str, sender: str = "Yeon") -> dict:
    """Build a confirm intent data referencing a schedule."""
    return {
        "intent": "confirm",
        "payload": payload,
        "sender": sender,
        "context": [ref_id],
        "status": "accepted",
    }
