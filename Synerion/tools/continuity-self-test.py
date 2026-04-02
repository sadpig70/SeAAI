#!/usr/bin/env python3
"""Validate core Synerion continuity artifacts."""

from continuity_lib import self_test_checks


def main() -> int:
    checks = self_test_checks()
    failed = [check for check in checks if not check[1]]
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
