"""SA_orchestrate_team_yeon — Team orchestration for Yeon (mock-based, Hub-ready)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mock_workers"))

from mock_worker_spawner import spawn, run_worker
from mock_worker_collector import collect
from mock_worker_converger import converge, save_converged


def orchestrate(task: str, personas: list) -> dict:
    """Spawn workers for each persona, run, collect, and converge."""
    worker_ids = []
    for i, persona in enumerate(personas):
        wid = f"yeon_worker_{i:03d}"
        spawn(wid, persona, task)
        run_worker(wid)
        worker_ids.append(wid)

    results = collect(worker_ids)
    final = converge(results)
    save_converged(final)
    return final


def main():
    personas = ["formal_translator", "technical_translator", "casual_translator"]
    final = orchestrate("Hello, how are you?", personas)
    print(f"Orchestrated {len(final['contributors'])} workers")
    print(f"Summary: {final['summary'][:80]}...")


if __name__ == "__main__":
    main()
