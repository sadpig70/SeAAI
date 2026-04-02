"""Triage incoming events into P0~P4 priorities."""


def triage(hub_msgs: list, mailbox_mails: list, echo_data: dict) -> dict:
    """Classify all channels into priority buckets."""
    result = {"P0": [], "P1": [], "P2": [], "P3": [], "P4": []}

    for cu in hub_msgs:
        if cu.urgency >= 3 or cu.intent == "interrupt":
            result["P0"].append({"source": "hub", "cu": cu})
        elif cu.intent in ("schedule", "confirm", "propose"):
            result["P2"].append({"source": "hub", "cu": cu})
        else:
            result["P3"].append({"source": "hub", "cu": cu})

    for mail in mailbox_mails:
        result["P2"].append({"source": "mailbox", "mail": mail})

    for member, data in echo_data.items():
        if data.get("_stale"):
            result["P1"].append({"source": "echo", "member": member, "reason": "stale"})
        else:
            result["P3"].append({"source": "echo", "member": member})

    return result


def decide_next_action(triage_result: dict) -> dict:
    """Pick highest priority non-empty bucket."""
    for pri in ("P0", "P1", "P2", "P3", "P4"):
        if triage_result[pri]:
            return {"priority": pri, "items": triage_result[pri]}
    return {"priority": "P4", "items": []}
