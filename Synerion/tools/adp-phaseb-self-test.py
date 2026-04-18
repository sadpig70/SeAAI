#!/usr/bin/env python3
"""Exercise mailbox triage and runtime-safe ADP routing with a temporary fixture."""

from __future__ import annotations

import json
import subprocess
import sys

from continuity_lib import MAILBOX_INBOX, ROOT, WORKSPACE, read_text, write_text


FIXTURE = MAILBOX_INBOX / ".adp-phaseb-selftest-shared-impact.md"
REPORT_JSON = WORKSPACE / "synerion-adp-last-run.json"


def main() -> int:
    fixture_text = """---
id: synerion-selftest-20260402-001
from: Navelon
to: [Synerion]
date: 2026-04-02T11:00:00+09:00
intent: sync
priority: urgent
protocol: seaai-mailbox/1.0
---

# Shared readiness advisory

Please review shared-impact rollout readiness for Hub, member_registry, session_token, and parity.
"""
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    write_text(FIXTURE, fixture_text)
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "update-project-status.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "run-synerion-adp.py"), "--ticks", "1"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = json.loads(read_text(REPORT_JSON))
        modules = payload["results"][0]["modules"]
        module_ids = [module["module_id"] for module in modules]
        assert "SA_ORCHESTRATOR_sync_mailbox" in module_ids
        assert "SA_ORCHESTRATOR_check_shared_impact" in module_ids
        assert payload["final_mailbox"]["pending_count"] >= 1
        assert payload["final_mailbox"]["recommended_target"] == "Navelon"
        print(completed.stdout.strip())
        print("[adp-phaseb-self-test] PASS")
        return 0
    finally:
        if FIXTURE.exists():
            FIXTURE.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
