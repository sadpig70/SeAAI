#!/usr/bin/env python3
"""Print a concise resume summary for the current Synerion workspace."""

from continuity_lib import resume_summary_text


def main() -> int:
    print(resume_summary_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
