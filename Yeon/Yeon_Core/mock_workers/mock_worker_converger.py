"""Converge mock worker outputs into a single result."""
import json
from pathlib import Path

WORKER_BASE = Path(__file__).resolve().parent


def converge(results: list) -> dict:
    """Merge partial translations into a converged summary."""
    valid = [r for r in results if r.get("status") == "done"]
    outputs = [r["output"] for r in valid]

    return {
        "status": "converged",
        "contributors": [r["worker_id"] for r in valid],
        "outputs": outputs,
        "summary": " | ".join(outputs),
    }


def save_converged(converged: dict, filename: str = "converged.json") -> Path:
    path = WORKER_BASE / filename
    path.write_text(json.dumps(converged, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
