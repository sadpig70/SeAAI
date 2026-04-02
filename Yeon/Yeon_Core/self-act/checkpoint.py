"""Checkpoint current state to STATE.json and journal."""
import json
from datetime import datetime
from pathlib import Path

CORE_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/continuity")


def save_STATE(context: dict) -> Path:
    """Update STATE.json with current context."""
    state_path = CORE_DIR / "STATE.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        state = {"schema_version": "2.0", "member": "Yeon"}
    state["last_saved"] = datetime.now().isoformat()
    state["context"] = context
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state_path


def write_journal_if_significant(significant: bool = False, text: str = "") -> Path:
    """Write journal only if significant events occurred."""
    if not significant:
        return None
    journal_dir = CORE_DIR / "journals"
    journal_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = journal_dir / f"{today}.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    entry = f"\n## {datetime.now().isoformat()}\n{text}\n"
    path.write_text(existing + entry, encoding="utf-8")
    return path
