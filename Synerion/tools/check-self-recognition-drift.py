#!/usr/bin/env python3
"""Check Synerion self-recognition drift and write a durable report."""

from __future__ import annotations

import json

from continuity_lib import WORKSPACE, self_recognition_drift_report, write_text


REPORT_JSON = WORKSPACE / "synerion-self-recognition-drift.json"


def main() -> int:
    report = self_recognition_drift_report()
    write_text(REPORT_JSON, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    status = "DRIFT" if report["drift_detected"] else "CLEAN"
    print(f"[{status}] wrote {REPORT_JSON}")
    for mismatch in report["mismatches"]:
        print(f"- {mismatch}")
    return 1 if report["drift_detected"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
