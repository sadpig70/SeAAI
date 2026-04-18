#!/usr/bin/env python3
"""Run a bounded Synerion ADP loop using local SelfAct seed modules."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

from continuity_lib import (
    ADP_BOOTSTRAP_MD,
    MAILBOX_INBOX,
    MAILBOX_TRIAGE_JSON,
    MAILBOX_TRIAGE_MD,
    REGISTRY,
    RUNTIME_READINESS_JSON,
    RUNTIME_READINESS_MD,
    STATE_JSON,
    THREADS_MD,
    WORKSPACE,
    drift_evolution_lines,
    drift_evolution_snapshot,
    mailbox_advisory_lines,
    mailbox_triage_markdown,
    mailbox_triage_snapshot,
    now_local,
    runtime_readiness_lines,
    runtime_readiness_markdown,
    runtime_readiness_snapshot,
    self_recognition_drift_report,
    self_recognition_identity,
    shared_impact_lines,
    shared_impact_snapshot,
    sync_continuity_files,
    write_text,
)


LATEST_JSON = WORKSPACE / "synerion-adp-last-run.json"


@dataclass
class ModuleResult:
    module_id: str
    summary: str
    safety_risk: bool = False
    shared_impact: bool = False
    creator_escalation_required: bool = False
    gap_detected: bool = False
    evolution_worthy: bool = False
    details: dict | None = None


def SA_ORCHESTRATOR_scan_state() -> ModuleResult:
    drift = self_recognition_drift_report()
    mailbox = mailbox_triage_snapshot()
    readiness = runtime_readiness_snapshot()
    shared = shared_impact_snapshot(mailbox=mailbox, readiness=readiness)
    drift_link = drift_evolution_snapshot(drift=drift, readiness=readiness, shared=shared)
    details = {
        "identity": self_recognition_identity(),
        "drift": drift,
        "mailbox": mailbox,
        "runtime_readiness": readiness,
        "shared_impact": shared,
        "drift_evolution": drift_link,
    }
    summary = (
        "scan_state: "
        f"drift={drift['drift_detected']} "
        f"mailbox_pending={mailbox['pending_count']} "
        f"shared_impact={shared['detected']} "
        f"rollout_gate={readiness['rollout_gate']}"
    )
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_scan_state",
        summary=summary,
        safety_risk=(shared["recommended_target"] == "Navelon"),
        shared_impact=shared["detected"],
        gap_detected=drift["drift_detected"],
        evolution_worthy=drift_link["record_gap"],
        details=details,
    )


def SA_ORCHESTRATOR_sync_mailbox(context: dict, apply: bool) -> ModuleResult:
    mailbox = context["mailbox"]
    if apply:
        write_text(MAILBOX_TRIAGE_JSON, json.dumps(mailbox, ensure_ascii=False, indent=2) + "\n")
        write_text(MAILBOX_TRIAGE_MD, mailbox_triage_markdown(mailbox))
        summary = (
            "sync_mailbox: "
            f"pending={mailbox['pending_count']} shared-impact={mailbox['shared_impact_count']} advisory persisted"
        )
    else:
        summary = (
            "sync_mailbox: "
            f"pending={mailbox['pending_count']} shared-impact={mailbox['shared_impact_count']} dry-run"
        )
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_sync_mailbox",
        summary=summary,
        shared_impact=mailbox["shared_impact_count"] > 0,
        details={
            "advisory_lines": mailbox_advisory_lines(mailbox),
            "recommended_target": mailbox.get("recommended_target", "local"),
        },
    )


def SA_ORCHESTRATOR_detect_conflict(context: dict) -> ModuleResult:
    drift = context["drift"]
    shared = context["shared_impact"]
    mailbox = context["mailbox"]
    reasons = []
    if drift["drift_detected"]:
        reasons.append("self-recognition drift detected")
    if mailbox["flagged_count"]:
        reasons.append(f"flagged mailbox items={mailbox['flagged_count']}")
    if shared["detected"]:
        reasons.extend(shared["reasons"])
    summary = "detect_conflict: " + ("; ".join(reasons) if reasons else "no immediate conflict")
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_detect_conflict",
        summary=summary,
        safety_risk=(shared["recommended_target"] == "Navelon"),
        shared_impact=shared["detected"],
        gap_detected=drift["drift_detected"] or mailbox["flagged_count"] > 0,
        details={"reasons": reasons},
    )


def SA_ORCHESTRATOR_check_shared_impact(context: dict) -> ModuleResult:
    shared = context["shared_impact"]
    summary = (
        "check_shared_impact: "
        f"detected={shared['detected']} level={shared['level']} target={shared['recommended_target']}"
    )
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_check_shared_impact",
        summary=summary,
        safety_risk=(shared["recommended_target"] == "Navelon"),
        shared_impact=shared["detected"],
        details={"advisory_lines": shared_impact_lines(shared), **shared},
    )


def SA_ORCHESTRATOR_verify_runtime_readiness(context: dict, apply: bool) -> ModuleResult:
    readiness = context["runtime_readiness"]
    if apply:
        write_text(RUNTIME_READINESS_JSON, json.dumps(readiness, ensure_ascii=False, indent=2) + "\n")
        write_text(RUNTIME_READINESS_MD, runtime_readiness_markdown(readiness))
        summary = (
            "verify_runtime_readiness: "
            f"gate={readiness['rollout_gate']} pending={','.join(readiness['pending_native_members']) or 'none'} snapshot persisted"
        )
    else:
        summary = (
            "verify_runtime_readiness: "
            f"gate={readiness['rollout_gate']} pending={','.join(readiness['pending_native_members']) or 'none'} dry-run"
        )
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_verify_runtime_readiness",
        summary=summary,
        shared_impact=(readiness["rollout_gate"] != "green"),
        details={"advisory_lines": runtime_readiness_lines(readiness), **readiness},
    )


def SA_ORCHESTRATOR_sync_continuity(apply: bool) -> ModuleResult:
    if apply:
        sync_continuity_files()
        summary = "sync_continuity: continuity regenerated and drift baseline refreshed"
    else:
        summary = "sync_continuity: dry-run recommendation only"
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_sync_continuity",
        summary=summary,
        shared_impact=True,
        evolution_worthy=apply,
    )


def SA_ORCHESTRATOR_route_handoff(context: dict) -> ModuleResult:
    mailbox = context["mailbox"]
    readiness = context["runtime_readiness"]
    shared = context["shared_impact"]
    drift_link = context["drift_evolution"]
    target = "local"
    reason = "no handoff required"
    if shared["recommended_target"] == "Navelon":
        target = "Navelon"
        reason = "reply gating or shared safety condition remains open"
    elif mailbox["recommended_target"] not in {"local", "Synerion"}:
        target = mailbox["recommended_target"]
        reason = "mailbox triage recommends bounded handoff"
    elif readiness["rollout_gate"] != "green":
        target = "Navelon"
        reason = "shared readiness and runtime parity remain guarded"
    elif drift_link["record_gap"]:
        target = "creator"
        reason = "structural evolution backlog should be acknowledged"
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_route_handoff",
        summary=f"route_handoff: recommend target={target} reason={reason}",
        creator_escalation_required=(target == "creator"),
        shared_impact=(target == "Navelon"),
        details={"target": target, "reason": reason},
    )


def SA_ORCHESTRATOR_link_evolution(context: dict) -> ModuleResult:
    drift_link = context["drift_evolution"]
    summary = (
        "link_evolution: "
        f"status={drift_link['status']} next={drift_link['recommended_module']} record_gap={drift_link['record_gap']}"
    )
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_link_evolution",
        summary=summary,
        gap_detected=drift_link["status"] == "blocked",
        evolution_worthy=drift_link["record_gap"],
        details={"advisory_lines": drift_evolution_lines(drift_link), **drift_link},
    )


def SA_ORCHESTRATOR_idle_maintain(context: dict) -> ModuleResult:
    next_focus = context["runtime_readiness"]["recommended_next"][0] if context["runtime_readiness"]["recommended_next"] else "none"
    return ModuleResult(
        module_id="SA_ORCHESTRATOR_idle_maintain",
        summary=f"idle_maintain: next_focus={next_focus}",
        details={"next_focus": next_focus},
    )


def build_execution_plan(scan: ModuleResult, conflict: ModuleResult) -> list[str]:
    context = scan.details or {}
    mailbox = context.get("mailbox", {})
    readiness = context.get("runtime_readiness", {})
    shared = context.get("shared_impact", {})
    drift_link = context.get("drift_evolution", {})
    plan: list[str] = []
    if conflict.gap_detected:
        plan.append("SA_ORCHESTRATOR_sync_continuity")
    if mailbox.get("pending_count", 0) > 0:
        plan.append("SA_ORCHESTRATOR_sync_mailbox")
    if shared.get("detected"):
        plan.append("SA_ORCHESTRATOR_check_shared_impact")
    if readiness.get("rollout_gate", "blocked") != "green":
        plan.append("SA_ORCHESTRATOR_verify_runtime_readiness")
    if shared.get("detected") or mailbox.get("pending_count", 0) > 0 or readiness.get("rollout_gate", "blocked") != "green":
        plan.append("SA_ORCHESTRATOR_route_handoff")
    if drift_link.get("record_gap"):
        plan.append("SA_ORCHESTRATOR_link_evolution")
    if not plan:
        plan.append("SA_ORCHESTRATOR_idle_maintain")
    deduped: list[str] = []
    for module_id in plan:
        if module_id not in deduped:
            deduped.append(module_id)
    return deduped


def execute_plan(plan: list[str], context: dict, apply: bool) -> tuple[list[ModuleResult], str]:
    modules: list[ModuleResult] = []
    final_target = "local"
    for module_id in plan:
        if module_id == "SA_ORCHESTRATOR_sync_continuity":
            modules.append(SA_ORCHESTRATOR_sync_continuity(apply))
        elif module_id == "SA_ORCHESTRATOR_sync_mailbox":
            modules.append(SA_ORCHESTRATOR_sync_mailbox(context, apply))
        elif module_id == "SA_ORCHESTRATOR_check_shared_impact":
            modules.append(SA_ORCHESTRATOR_check_shared_impact(context))
        elif module_id == "SA_ORCHESTRATOR_verify_runtime_readiness":
            modules.append(SA_ORCHESTRATOR_verify_runtime_readiness(context, apply))
        elif module_id == "SA_ORCHESTRATOR_route_handoff":
            handoff = SA_ORCHESTRATOR_route_handoff(context)
            modules.append(handoff)
            final_target = (handoff.details or {}).get("target", "local")
        elif module_id == "SA_ORCHESTRATOR_link_evolution":
            modules.append(SA_ORCHESTRATOR_link_evolution(context))
        else:
            modules.append(SA_ORCHESTRATOR_idle_maintain(context))
    return modules, final_target


def write_report(run_payload: dict, report_md: Path, report_json: Path) -> None:
    lines = [
        "# Report: Synerion Bounded ADP Run",
        "",
        f"- Generated: {run_payload['generated_at']}",
        f"- Ticks: {run_payload['ticks']}",
        f"- Interval sec: {run_payload['interval_sec']}",
        f"- Apply mode: {run_payload['apply']}",
        "",
        "## Bootstrap Inputs",
        "",
        f"- {STATE_JSON}",
        f"- {THREADS_MD}",
        f"- {ADP_BOOTSTRAP_MD}",
        f"- {REGISTRY}",
        f"- inbox: {MAILBOX_INBOX}",
        "",
        "## Tick Results",
        "",
    ]
    for tick in run_payload["results"]:
        lines.append(f"### Tick {tick['tick']}")
        lines.append(f"- plan: {', '.join(tick['plan'])}")
        for item in tick["modules"]:
            lines.append(f"- {item['module_id']}: {item['summary']}")
        lines.append("")
    lines.extend(
        [
            "## Final Signals",
            "",
            f"- drift_detected: {run_payload['final_drift']['drift_detected']}",
            f"- mailbox_pending: {run_payload['final_mailbox']['pending_count']}",
            f"- mailbox_shared_impact: {run_payload['final_mailbox']['shared_impact_count']}",
            f"- rollout_gate: {run_payload['final_readiness']['rollout_gate']}",
            f"- shared_impact_detected: {run_payload['final_shared_impact']['detected']}",
            f"- evolution_status: {run_payload['final_drift_evolution']['status']}",
            f"- next_recommended_target: {run_payload['final_target']}",
            "",
            "## Advisory",
            "",
            *mailbox_advisory_lines(run_payload["final_mailbox"]),
            *runtime_readiness_lines(run_payload["final_readiness"]),
            *shared_impact_lines(run_payload["final_shared_impact"]),
            *drift_evolution_lines(run_payload["final_drift_evolution"]),
            "",
        ]
    )
    report_text = "\n".join(lines) + "\n"
    payload_text = json.dumps(run_payload, ensure_ascii=False, indent=2) + "\n"
    write_text(report_md, report_text)
    write_text(report_json, payload_text)
    write_text(LATEST_JSON, payload_text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=int, default=3)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    started = now_local()
    run_stamp = started.strftime("%Y-%m-%d-%H%M%S")
    report_md = WORKSPACE / f"REPORT-Synerion-ADP-Run-{run_stamp}.md"
    report_json = WORKSPACE / f"synerion-adp-{run_stamp}.json"

    results: list[dict] = []
    final_target = "local"

    for tick in range(1, args.ticks + 1):
        scan = SA_ORCHESTRATOR_scan_state()
        context = scan.details or {}
        conflict = SA_ORCHESTRATOR_detect_conflict(context)
        plan = build_execution_plan(scan, conflict)
        modules = [scan, conflict]
        executed, target = execute_plan(plan, context, args.apply)
        modules.extend(executed)
        if target != "local":
            final_target = target
        results.append(
            {
                "tick": tick,
                "plan": plan,
                "modules": [
                    {
                        "module_id": module.module_id,
                        "summary": module.summary,
                        "details": module.details or {},
                    }
                    for module in modules
                ],
            }
        )
        if args.interval:
            time.sleep(args.interval)

    final_drift = self_recognition_drift_report()
    final_mailbox = mailbox_triage_snapshot()
    final_readiness = runtime_readiness_snapshot()
    final_shared = shared_impact_snapshot(mailbox=final_mailbox, readiness=final_readiness)
    final_drift_link = drift_evolution_snapshot(
        drift=final_drift,
        readiness=final_readiness,
        shared=final_shared,
    )
    run_payload = {
        "generated_at": started.isoformat(),
        "ticks": args.ticks,
        "interval_sec": args.interval,
        "apply": args.apply,
        "results": results,
        "final_drift": final_drift,
        "final_mailbox": final_mailbox,
        "final_readiness": final_readiness,
        "final_shared_impact": final_shared,
        "final_drift_evolution": final_drift_link,
        "final_target": final_target,
    }
    write_report(run_payload, report_md, report_json)
    print(f"[run-synerion-adp] wrote {report_md}")
    print(f"[run-synerion-adp] wrote {report_json}")
    print(f"[run-synerion-adp] updated {LATEST_JSON}")
    print(
        "[run-synerion-adp] "
        f"drift={final_drift['drift_detected']} "
        f"rollout_gate={final_readiness['rollout_gate']} "
        f"target={final_target}"
    )
    local_failure = final_drift["drift_detected"] or final_mailbox["flagged_count"] > 0
    return 1 if local_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
