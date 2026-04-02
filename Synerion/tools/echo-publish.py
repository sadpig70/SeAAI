#!/usr/bin/env python3
"""Publish Synerion shared Echo JSON."""

from __future__ import annotations

import json

from continuity_lib import ECHO_DIR, echo_payload, write_text


def main() -> int:
    target = ECHO_DIR / "Synerion.json"
    write_text(target, json.dumps(echo_payload(), ensure_ascii=False, indent=2) + "\n")
    print(f"[echo-publish] wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
