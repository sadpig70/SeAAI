"""Spawn mock translation workers without Hub communication."""
import json
from pathlib import Path

WORKER_BASE = Path(__file__).resolve().parent


def spawn(worker_id: str, persona: str, input_task: str) -> Path:
    """Create a mock worker sandbox with run script."""
    worker_dir = WORKER_BASE / worker_id
    worker_dir.mkdir(exist_ok=True)

    # Write persona
    (worker_dir / "persona.json").write_text(
        json.dumps({"id": worker_id, "persona": persona}, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write input task
    (worker_dir / "input.txt").write_text(input_task, encoding="utf-8")

    # Write worker run script
    run_py = worker_dir / "run.py"
    run_py.write_text(
        f"""import json
from pathlib import Path

base = Path(__file__).resolve().parent
inp = (base / "input.txt").read_text(encoding="utf-8")
persona = json.loads((base / "persona.json").read_text(encoding="utf-8"))

# Simple mock translation logic
result = {{
    "worker_id": persona["id"],
    "persona": persona["persona"],
    "input": inp,
    "output": f"[{{persona['persona']}}] translated: {{inp}}",
    "status": "done",
}}

(base / "output.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
print("Worker", persona["id"], "finished")
""",
        encoding="utf-8",
    )

    return worker_dir


def run_worker(worker_id: str) -> bool:
    """Execute the mock worker script."""
    import subprocess, sys

    run_py = WORKER_BASE / worker_id / "run.py"
    if not run_py.exists():
        return False
    result = subprocess.run([sys.executable, str(run_py)], capture_output=True, text=True)
    return result.returncode == 0
