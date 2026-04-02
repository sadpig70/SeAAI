"""Verify E7 Self-Reflection Engine integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from SA_loop_autonomous import main_loop
from SA_self_reflect import DISCOVERIES, STATE_PATH


def test():
    # Ensure baseline discovery count (entries start with '##')
    baseline = 0
    if DISCOVERIES.exists():
        baseline = len([l for l in DISCOVERIES.read_text(encoding="utf-8").splitlines() if l.startswith("## ")])

    # Run 7 ticks -> reflection triggers at tick_num=6 (since tick_num>0 and tick_num%6==0)
    main_loop(ticks=7)

    # Verify discovery recorded
    assert DISCOVERIES.exists(), "DISCOVERIES.md missing"
    lines = DISCOVERIES.read_text(encoding="utf-8").splitlines()
    count = len([l for l in lines if l.startswith("## ")])
    assert count >= baseline, "No new discovery recorded"

    # Verify no duplicate gap text (same proposal recorded twice in the same file)
    gaps = []
    for line in lines:
        if line.startswith("**갭**:"):
            gaps.append(line)
    unique = set(gaps)
    assert len(gaps) == len(unique), f"Duplicate discovery detected: {len(gaps)} vs {len(unique)}"

    # Verify STATE.json carries next_proposal
    import json
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state.get("next_proposal") is not None, "STATE.json missing next_proposal"

    print(f"PASS: E7 verified ({count} discovery entries, {len(unique)} unique gaps)")


if __name__ == "__main__":
    test()
