#!/usr/bin/env python3
"""Export Synerion runtime readiness advisory artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from continuity_lib import (
    RUNTIME_READINESS_JSON,
    runtime_readiness_markdown,
    runtime_readiness_snapshot,
    write_text,
)


def main() -> int:
    readiness = runtime_readiness_snapshot()
    stamp = Path(RUNTIME_READINESS_JSON).stem
    write_text(RUNTIME_READINESS_JSON, json.dumps(readiness, ensure_ascii=False, indent=2) + "\n")
    report_md = RUNTIME_READINESS_JSON.parent / f"REPORT-Synerion-Runtime-Readiness-{readiness['checked_at'][0:10]}.md"
    write_text(report_md, runtime_readiness_markdown(readiness))
    print(f"[assess-runtime-readiness] wrote {RUNTIME_READINESS_JSON}")
    print(f"[assess-runtime-readiness] wrote {report_md}")
    print(f"[assess-runtime-readiness] rollout_gate={readiness['rollout_gate']}")
    return 0 if readiness["common_port_confirmed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
