"""Collect results from mock workers."""
import json
from pathlib import Path

WORKER_BASE = Path(__file__).resolve().parent


def collect(worker_ids: list) -> list:
    """Read output.json from each worker."""
    results = []
    for wid in worker_ids:
        out_path = WORKER_BASE / wid / "output.json"
        if out_path.exists():
            results.append(json.loads(out_path.read_text(encoding="utf-8")))
        else:
            results.append({"worker_id": wid, "status": "missing"})
    return results
