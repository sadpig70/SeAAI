#!/usr/bin/env python3
"""Write the current SharedSpace readiness and native runtime parity summary."""

from __future__ import annotations

import json

from continuity_lib import (
    RUNTIME_READINESS_JSON,
    RUNTIME_READINESS_MD,
    runtime_readiness_markdown,
    runtime_readiness_snapshot,
    write_text,
)


def main() -> int:
    snapshot = runtime_readiness_snapshot()
    write_text(RUNTIME_READINESS_JSON, json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    write_text(RUNTIME_READINESS_MD, runtime_readiness_markdown(snapshot))
    print(f"[report-runtime-readiness] wrote {RUNTIME_READINESS_MD}")
    print(f"[report-runtime-readiness] wrote {RUNTIME_READINESS_JSON}")
    print(
        "[report-runtime-readiness] "
        f"gate={snapshot['rollout_gate']} pending={','.join(snapshot['pending_native_members']) or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
