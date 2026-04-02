#!/usr/bin/env python3
"""Generate a durable Synerion runtime readiness report."""

from __future__ import annotations

import json

from continuity_lib import RUNTIME_READINESS_JSON, RUNTIME_READINESS_MD, runtime_readiness_snapshot, write_text


def main() -> int:
    snapshot = runtime_readiness_snapshot()
    lines = [
        "# Report: Synerion Runtime Readiness",
        "",
        f"- Generated: {snapshot['checked_at']}",
        f"- Rollout gate: {snapshot['rollout_gate']}",
        f"- Common port confirmed: {snapshot['common_port_confirmed']}",
        f"- Shared bounded pass: {snapshot['shared_bounded_pass']}",
        f"- Broadcast-only guard: {snapshot['broadcast_only_guard']}",
        f"- Direct reply guard: {snapshot['direct_reply_guard']}",
        f"- Session filter guard: {snapshot['session_filter_guard']}",
        "",
        "## Member Matrix",
        "",
    ]
    for row in snapshot["member_rows"]:
        lines.append(
            f"- {row['agent_id']} / runtime={row['runtime']} / native={row['native_status']} / evidence={row['hub_evidence']}"
        )
    lines.extend(["", "## Recommended Next", ""])
    lines.extend(f"- {item}" for item in snapshot["recommended_next"])
    write_text(RUNTIME_READINESS_MD, "\n".join(lines) + "\n")
    write_text(RUNTIME_READINESS_JSON, json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    print(f"[verify-runtime-readiness] wrote {RUNTIME_READINESS_MD}")
    print(f"[verify-runtime-readiness] wrote {RUNTIME_READINESS_JSON}")
    print(f"[verify-runtime-readiness] rollout_gate={snapshot['rollout_gate']}")
    return 0 if snapshot["rollout_gate"] in {"green", "guarded"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
