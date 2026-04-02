"""Sense Hub for PGTP messages."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hub.pgtp_bridge import CognitiveUnit
from SA_sense_pgtp import poll_hub, filter_self


def sense(agent_id: str = "Yeon", room: str = "seaai-general") -> list:
    """Return filtered PGTP messages from Hub."""
    cus = poll_hub(agent_id, room)
    return filter_self(cus, agent_id)
