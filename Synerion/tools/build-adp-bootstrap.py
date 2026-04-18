#!/usr/bin/env python3
"""Rebuild ADP bootstrap from persona seed and shared registry facts."""

from continuity_lib import ADP_BOOTSTRAP_MD, adp_bootstrap_text, write_text


def main() -> int:
    write_text(ADP_BOOTSTRAP_MD, adp_bootstrap_text())
    print(f"[build-adp-bootstrap] wrote {ADP_BOOTSTRAP_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
