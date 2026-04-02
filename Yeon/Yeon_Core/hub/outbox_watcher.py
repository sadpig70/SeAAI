"""Watch outbox directory for pending Hub commands."""
import json
from pathlib import Path

OUTBOX = Path("D:/SeAAI/Yeon/Yeon_Core/hub/outbox")


def scan() -> list:
    """Return sorted list of pending command files."""
    OUTBOX.mkdir(parents=True, exist_ok=True)
    return sorted(OUTBOX.glob("*.json"))


def read_oldest(files: list) -> tuple:
    """Read and return (Path, dict) of the oldest command."""
    if not files:
        return None, None
    path = files[0]
    data = json.loads(path.read_text(encoding="utf-8"))
    return path, data


def delete_after_send(path: Path) -> bool:
    """Remove command file after successful send."""
    if path and path.exists():
        path.unlink()
        return True
    return False
