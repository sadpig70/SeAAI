#!/usr/bin/env python3
"""Export Synerion canonical continuity state and derived views."""

from __future__ import annotations

import json

from continuity_lib import NOW_MD, STATE_JSON, THREADS_MD, now_markdown, state_payload, threads_markdown, write_text


def main() -> int:
    write_text(THREADS_MD, threads_markdown())
    write_text(STATE_JSON, json.dumps(state_payload(), ensure_ascii=False, indent=2) + "\n")
    write_text(NOW_MD, now_markdown())
    print(f"[export-scs-state] wrote {THREADS_MD}")
    print(f"[export-scs-state] wrote {STATE_JSON}")
    print(f"[export-scs-state] wrote {NOW_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
