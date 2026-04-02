#!/usr/bin/env python3
"""Synerion session start."""

from pathlib import Path

from tools.continuity_lib import resume_summary_text


def main() -> int:
    print("Starting Synerion session with self-recognition layer...")
    print(f"Workspace: {Path(__file__).parent}")
    print("ADP entrypoint: python tools/run-synerion-adp.py --ticks 3 --apply")
    print()
    print(resume_summary_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
