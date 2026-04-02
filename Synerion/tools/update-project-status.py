#!/usr/bin/env python3
"""Regenerate Synerion continuity artifacts with WAL-protected sync."""

from continuity_lib import PROJECT_STATUS, sync_continuity_files


def main() -> int:
    sync_continuity_files()
    print(f"[update-project-status] synced continuity via {PROJECT_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
