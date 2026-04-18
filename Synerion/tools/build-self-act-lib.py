#!/usr/bin/env python3
"""Rebuild self-act library from continuity_lib canonical text."""

from continuity_lib import SELF_ACT_LIB_MD, self_act_lib_text, write_text


def main() -> int:
    write_text(SELF_ACT_LIB_MD, self_act_lib_text())
    print(f"[build-self-act-lib] wrote {SELF_ACT_LIB_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
