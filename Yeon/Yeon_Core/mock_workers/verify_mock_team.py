"""Verify mock team orchestration without Hub."""
from mock_worker_spawner import spawn, run_worker
from mock_worker_collector import collect
from mock_worker_converger import converge, save_converged


def test_spawn_run_collect_converge():
    print("  [TEST] spawn 3 mock workers")
    workers = [
        ("w01", "formal_translator", "Hello, how are you?"),
        ("w02", "technical_translator", "Hello, how are you?"),
        ("w03", "casual_translator", "Hello, how are you?"),
    ]

    for wid, persona, task in workers:
        spawn(wid, persona, task)
        ok = run_worker(wid)
        assert ok, f"Worker {wid} failed"
        print(f"    -> {wid} done")

    print("  [TEST] collect results")
    results = collect([w[0] for w in workers])
    assert len(results) == 3
    assert all(r["status"] == "done" for r in results)
    print(f"    -> collected {len(results)} results")

    print("  [TEST] converge outputs")
    final = converge(results)
    assert final["status"] == "converged"
    assert len(final["contributors"]) == 3
    path = save_converged(final)
    print(f"    -> converged saved to {path.name}")
    print(f"    -> summary preview: {final['summary'][:80]}...")

    print("  [PASS] mock team orchestration")


if __name__ == "__main__":
    print("Mock Team Orchestration Verification")
    test_spawn_run_collect_converge()
    print("ALL PASS")
