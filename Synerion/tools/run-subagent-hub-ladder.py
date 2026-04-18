#!/usr/bin/env python3
"""Stage runner for Synerion subagent ADP/Hub/PGFP ladder experiments."""

from __future__ import annotations

import argparse
import json
import secrets
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "_workspace"
LAB_ROOT = WORKSPACE / "subagent-lab"
TOOLS = ROOT / "tools"
HUB_ROOT = ROOT.parent / "SeAAIHub"
HUB_EXE = HUB_ROOT / "target" / "debug" / "SeAAIHub.exe"
RUNTIME = TOOLS / "subagent_lab_runtime.py"
REPORT_MD = WORKSPACE / "REPORT-Synerion-Subagent-Hub-Ladder-2026-04-02.md"
SUMMARY_JSON = WORKSPACE / "synerion-subagent-hub-ladder-last-run.json"
PGF_ROOT = ROOT / ".pgf"
STATUS_JSON = PGF_ROOT / "status-SynerionSubagentHubLadder.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run staged subagent hub ladder")
    parser.add_argument("--ticks", type=int, default=5)
    parser.add_argument("--tick-sec", type=float, default=0.8)
    parser.add_argument("--hub-port", type=int, default=9900)
    parser.add_argument("--hub-host", default="127.0.0.1")
    parser.add_argument("--room-prefix", default="synerion-lab")
    return parser.parse_args()


def now_local() -> datetime:
    return datetime.now().astimezone()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def port_open(host: str, port: int) -> bool:
    try:
        socket.create_connection((host, port), timeout=1).close()
        return True
    except OSError:
        return False


def start_hub(host: str, port: int) -> tuple[subprocess.Popen | None, bool, str]:
    if port_open(host, port):
        return None, False, "existing"
    if not HUB_EXE.exists():
        return None, True, "file-fallback"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(
        [str(HUB_EXE), "--tcp-port", str(port)],
        cwd=str(HUB_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            return None, True, "file-fallback"
        if port_open(host, port):
            return proc, True, "rust-binary"
        time.sleep(0.25)
    proc.terminate()
    proc.wait(timeout=5)
    return None, True, "file-fallback"


def stop_hub(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def stage_specs(args: argparse.Namespace, run_id: str) -> list[dict]:
    def room(stage_id: str) -> str:
        return f"{args.room_prefix}-{run_id}-{stage_id}"

    return [
        {
            "id": "stage1-hubless-single",
            "label": "1-agent hubless 5 ticks",
            "mode": "hubless",
            "profile": "plain",
            "goal": "subagent performs bounded ADP without Hub",
            "agents": ["SubagentAlpha"],
            "room": room("s1"),
        },
        {
            "id": "stage2-hub-single",
            "label": "1-agent hub connect",
            "mode": "hub",
            "profile": "plain",
            "goal": "subagent connects to Hub and emits bounded broadcast",
            "agents": ["SubagentAlpha"],
            "room": room("s2"),
        },
        {
            "id": "stage3-synerion-subagent-chat",
            "label": "Synerion + 1 subagent chat",
            "mode": "hub",
            "profile": "plain",
            "goal": "Synerion and one subagent exchange bounded chat via Hub",
            "agents": ["Synerion", "SubagentAlpha"],
            "room": room("s3"),
        },
        {
            "id": "stage4-synerion-subagent-pgfp",
            "label": "Synerion + 1 subagent PGFP",
            "mode": "hub",
            "profile": "pgfp",
            "goal": "Synerion and one subagent exchange PGFP/1 bounded handoff and result",
            "agents": ["Synerion", "SubagentAlpha"],
            "room": room("s4"),
        },
        {
            "id": "stage5-two-subagents",
            "label": "2 subagents over Hub",
            "mode": "hub",
            "profile": "pgfp",
            "goal": "two subagents exchange bounded PGFP/1 packets over Hub",
            "agents": ["SubagentAlpha", "SubagentBeta"],
            "room": room("s5"),
        },
        {
            "id": "stage6-four-subagents",
            "label": "4 subagents over Hub",
            "mode": "hub",
            "profile": "pgfp",
            "goal": "four subagents exchange bounded PGFP/1 packets over Hub",
            "agents": ["SubagentAlpha", "SubagentBeta", "SubagentGamma", "SubagentDelta"],
            "room": room("s6"),
        },
    ]


def run_stage(stage: dict, args: argparse.Namespace, run_id: str, hub_backend: str) -> dict:
    stage_dir = LAB_ROOT / run_id / stage["id"]
    stage_dir.mkdir(parents=True, exist_ok=True)
    procs = []
    shared_session_start = time.time()
    shared_session_token = f"{stage['id']}_{int(shared_session_start)}_{secrets.token_hex(3)}"
    try:
        for agent_id in stage["agents"]:
            stdout_path = stage_dir / f"{agent_id}.stdout.log"
            stderr_path = stage_dir / f"{agent_id}.stderr.log"
            stdout_handle = stdout_path.open("w", encoding="utf-8")
            stderr_handle = stderr_path.open("w", encoding="utf-8")
            command = [
                sys.executable,
                str(RUNTIME),
                "--agent-id",
                agent_id,
                "--mode",
                stage["mode"],
                "--profile",
                stage["profile"],
                "--ticks",
                str(args.ticks),
                "--tick-sec",
                str(args.tick_sec),
                "--room",
                stage["room"],
                "--goal",
                stage["goal"],
                "--run-id",
                run_id,
                "--stage-id",
                stage["id"],
                "--hub-host",
                args.hub_host,
                "--hub-port",
                str(args.hub_port),
                "--hub-backend",
                "file" if stage["mode"] == "hub" and hub_backend == "file-fallback" else "tcp",
                "--session-token",
                shared_session_token,
                "--session-start-ts",
                str(shared_session_start),
            ]
            proc = subprocess.Popen(
                command,
                cwd=str(ROOT),
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                encoding="utf-8",
            )
            procs.append((agent_id, proc, stdout_handle, stderr_handle))
            time.sleep(0.15)

        agent_results = []
        exit_codes = {}
        for agent_id, proc, stdout_handle, stderr_handle in procs:
            code = proc.wait(timeout=max(30, int(args.ticks * args.tick_sec * 10)))
            stdout_handle.close()
            stderr_handle.close()
            exit_codes[agent_id] = code
            summary_path = stage_dir / f"{agent_id}.summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            agent_results.append(summary)

        success, evidence = evaluate_stage(stage, agent_results, exit_codes)
        return {
            "stage_id": stage["id"],
            "label": stage["label"],
            "mode": stage["mode"],
            "profile": stage["profile"],
            "room": stage["room"],
            "agents": stage["agents"],
            "success": success,
            "evidence": evidence,
            "exit_codes": exit_codes,
            "agent_results": agent_results,
        }
    finally:
        for _, proc, stdout_handle, stderr_handle in procs:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=3)
            if not stdout_handle.closed:
                stdout_handle.close()
            if not stderr_handle.closed:
                stderr_handle.close()


def evaluate_stage(stage: dict, agent_results: list[dict], exit_codes: dict[str, int]) -> tuple[bool, list[str]]:
    evidence: list[str] = []
    if any(code != 0 for code in exit_codes.values()):
        return False, [f"non-zero exit codes: {exit_codes}"]
    if stage["mode"] == "hubless":
        ok = all(item["ticks_completed"] == item["ticks_requested"] for item in agent_results)
        evidence.append("all hubless ticks completed" if ok else "tick completion mismatch")
        return ok, evidence
    if len(agent_results) == 1:
        item = agent_results[0]
        ok = item["ticks_completed"] == item["ticks_requested"] and item["sent"] >= 1
        evidence.append(f"single agent sent={item['sent']} received={item['received']}")
        return ok, evidence
    peer_ok = all(item["peer_messages"] >= 1 for item in agent_results)
    evidence.append(
        "peer_messages="
        + ", ".join(f"{item['agent_id']}:{item['peer_messages']}" for item in agent_results)
    )
    if stage["profile"] == "pgfp":
        pgfp_ok = all(item["pgfp_sent"] >= 1 and item["pgfp_received"] >= 1 for item in agent_results)
        evidence.append(
            "pgfp="
            + ", ".join(
                f"{item['agent_id']}:{item['pgfp_sent']}/{item['pgfp_received']}" for item in agent_results
            )
        )
        return peer_ok and pgfp_ok, evidence
    return peer_ok, evidence


def report_markdown(run_id: str, started_hub: bool, hub_backend: str, stages: list[dict]) -> str:
    lines = [
        "# Report: Synerion Subagent Hub Ladder",
        "",
        f"- Generated: {now_local().isoformat()}",
        f"- Run ID: {run_id}",
        f"- Hub started by runner: {started_hub}",
        f"- Hub backend: {hub_backend}",
        "",
        "## Verdict",
        "",
        f"- Successful stages: {sum(1 for stage in stages if stage['success'])}/{len(stages)}",
        "",
        "## Stage Results",
        "",
    ]
    for stage in stages:
        lines.extend(
            [
                f"### {stage['label']}",
                f"- success: {stage['success']}",
                f"- mode/profile: {stage['mode']} / {stage['profile']}",
                f"- agents: {', '.join(stage['agents'])}",
                f"- room: {stage['room']}",
                f"- evidence: {' | '.join(stage['evidence'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Key Findings",
            "",
            "- `hubless -> hub -> Synerion+subagent -> PGFP -> 2 subagents -> 4 subagents` 경로를 하나의 bounded harness로 재현했다.",
            "- `PGFP/1`는 Hub transport를 바꾸지 않고 `pg_payload.body` profile로 얹는 방식으로 실험했다.",
            "- direct reply 대신 broadcast-only를 유지해 current guardrail을 보존했다.",
            "- Rust Hub가 현재 환경에서 `Winsock 10106`으로 실패하면 file-backed shared hub로 같은 room/inbox/broadcast semantics를 유지한다.",
            "",
            "## Output",
            "",
            f"- JSON summary: {SUMMARY_JSON.as_posix()}",
            f"- Run root: {(LAB_ROOT / run_id).as_posix()}",
        ]
    )
    return "\n".join(lines) + "\n"


def status_payload(stages: list[dict]) -> dict:
    items = []
    for stage in stages:
        items.append(
            {
                "task": stage["label"],
                "status": "done" if stage["success"] else "blocked",
                "notes": " | ".join(stage["evidence"]),
            }
        )
    return {
        "updated_at": now_local().isoformat(),
        "project": "SynerionSubagentHubLadder",
        "done": sum(1 for stage in stages if stage["success"]),
        "in_progress": 0,
        "pending": 0,
        "blocked": sum(1 for stage in stages if not stage["success"]),
        "items": items,
    }


def main() -> int:
    args = parse_args()
    run_id = now_local().strftime("%Y%m%d-%H%M%S")
    LAB_ROOT.mkdir(parents=True, exist_ok=True)

    stages = []
    hub_proc = None
    started_hub = False
    hub_backend = "none"
    try:
        specs = stage_specs(args, run_id)
        stages.append(run_stage(specs[0], args, run_id, hub_backend))
        hub_proc, started_hub, hub_backend = start_hub(args.hub_host, args.hub_port)
        for spec in specs[1:]:
            stages.append(run_stage(spec, args, run_id, hub_backend))
    finally:
        stop_hub(hub_proc)

    payload = {
        "generated_at": now_local().isoformat(),
        "run_id": run_id,
        "hub_started_by_runner": started_hub,
        "hub_backend": hub_backend,
        "hub_host": args.hub_host,
        "hub_port": args.hub_port,
        "ticks": args.ticks,
        "tick_sec": args.tick_sec,
        "stages": stages,
    }
    write_json(SUMMARY_JSON, payload)
    write_json(STATUS_JSON, status_payload(stages))
    REPORT_MD.write_text(report_markdown(run_id, started_hub, hub_backend, stages), encoding="utf-8", newline="\n")
    failures = [stage for stage in stages if not stage["success"]]
    print(f"[run-subagent-hub-ladder] wrote {REPORT_MD}")
    print(f"[run-subagent-hub-ladder] wrote {SUMMARY_JSON}")
    print(f"[run-subagent-hub-ladder] stages_ok={len(stages) - len(failures)}/{len(stages)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
