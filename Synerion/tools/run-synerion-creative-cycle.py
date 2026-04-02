#!/usr/bin/env python3
"""Run a bounded Synerion creative cycle for a given goal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from continuity_lib import (
    WORKSPACE,
    bounded_summary,
    latest_report_heading,
    mailbox_inbox_files,
    manual_sections_from_project_status,
    now_local,
    parse_member_registry,
    self_recognition_drift_report,
    write_text,
)


CORE_ENGINE = Path(__file__).resolve().parents[1] / "Synerion_Core" / "Synerion_Creative_Engine.md"
PERSONA_ROOT = WORKSPACE / "personas"
LATEST_JSON = WORKSPACE / "synerion-creative-cycle-last-run.json"
LATEST_PERSONA_JSON = PERSONA_ROOT / "synerion-creative-persona-set.json"
LATEST_PERSONA_MD = PERSONA_ROOT / "synerion-creative-persona-set.md"
LATEST_EXECUTION_JSON = PERSONA_ROOT / "synerion-creative-execution-map.json"
LATEST_EXECUTION_MD = PERSONA_ROOT / "synerion-creative-execution-map.md"


BASE_PERSONAS = [
    {
        "name": "IntegratorArchitect",
        "role": "구조 통합자",
        "desc": "분산된 제안을 실행 가능한 구조로 묶는다.",
        "cognitive_style": "systems synthesis",
        "domain": "integration",
        "question": "이 목표를 어떤 작동 구조로 묶어야 하는가?",
        "bias": "정합성과 연결 우선",
        "challenge_axis": "구조 정합성 붕괴",
        "likely_contribution": "실행 가능한 구조 초안과 convergence 기준 제시",
    },
    {
        "name": "AdversarialReviewer",
        "role": "반박자",
        "desc": "취약점, 과대평가, 누락된 실패 경로를 공격적으로 찾는다.",
        "cognitive_style": "adversarial analysis",
        "domain": "verification",
        "question": "이 설계가 어디서 깨지는가?",
        "bias": "실패점과 과대평가 우선",
        "challenge_axis": "취약점과 과신",
        "likely_contribution": "깨지는 지점과 수정 우선순위 추출",
    },
    {
        "name": "SafetyGate",
        "role": "안전 심사자",
        "desc": "권한, 경계, 위험 승격 조건을 점검한다.",
        "cognitive_style": "policy and risk gating",
        "domain": "safety",
        "question": "권한, 리스크, 경계 위반은 없는가?",
        "bias": "가드레일 우선",
        "challenge_axis": "권한과 경계 위반",
        "likely_contribution": "금지선, 승격선, 검증 전제 정리",
    },
    {
        "name": "RuntimeOperator",
        "role": "운영자",
        "desc": "현 런타임에서 가능한 실행 범위와 비용을 판단한다.",
        "cognitive_style": "operational realism",
        "domain": "runtime",
        "question": "현 런타임에서 실제로 무엇이 가능한가?",
        "bias": "현실 실행 가능성 우선",
        "challenge_axis": "런타임 제약과 비용",
        "likely_contribution": "실행 가능 범위와 bounded next step 명시",
    },
    {
        "name": "Synthesizer",
        "role": "수렴자",
        "desc": "발산된 판단을 실행 가능한 결론으로 압축한다.",
        "cognitive_style": "decision compression",
        "domain": "synthesis",
        "question": "무엇을 남기고 무엇을 버릴 것인가?",
        "bias": "압축과 다음 단계 우선",
        "challenge_axis": "결정 미루기와 과잉 복잡도",
        "likely_contribution": "실행 우선순위와 handoff-ready 결론 생성",
    },
]


def runtime_signals() -> dict[str, Any]:
    manual = manual_sections_from_project_status()
    normalized = bounded_summary()
    registry = parse_member_registry()
    drift = self_recognition_drift_report()
    inbox = mailbox_inbox_files()
    members = registry.get("members", [])
    return {
        "signal_policy": "normalized-only",
        "active_threads": manual.get("ActiveThreads", []),
        "next_actions": manual.get("NextActions", []),
        "open_risks": manual.get("OpenRisks", []),
        "registry_members": [member.agent_id for member in members],
        "registry_updated": registry.get("updated", ""),
        "hub_active_members": normalized.get("final_members") or [],
        "hub_duration_sec": normalized.get("duration_sec"),
        "mailbox_pending": len(inbox),
        "mailbox_snapshot": [path.name for path in inbox[:5]],
        "drift_detected": drift.get("drift_detected", False),
        "drift_mismatches": drift.get("mismatches", []),
        "latest_report": latest_report_heading(),
    }


def compose_domain_personas(goal: str, runtime: dict[str, Any]) -> list[dict[str, Any]]:
    personas: list[dict[str, Any]] = []
    lower = goal.lower()
    if any(token in lower for token in ("protocol", "통신", "pgtp", "hub")):
        personas.append(
            {
                "name": "ProtocolStrategist",
                "role": "프로토콜 전략가",
                "desc": "구조화 통신 계약과 상태 전달 규칙을 고정한다.",
                "cognitive_style": "contract design",
                "domain": "protocol",
                "question": "구조화 통신과 상태 전달을 어떻게 안정화할 것인가?",
                "bias": "interop와 contract 우선",
                "challenge_axis": "프로토콜 drift와 해석 충돌",
                "likely_contribution": "contract, schema, handoff 규칙 제시",
            }
        )
    if any(token in lower for token in ("creative", "창조", "engine", "persona")):
        personas.append(
            {
                "name": "CreativeSystemsBuilder",
                "role": "창조 시스템 설계자",
                "desc": "발견을 반복 가능한 엔진과 자산으로 바꾼다.",
                "cognitive_style": "creation systems",
                "domain": "creative-systems",
                "question": "발견과 구조화를 어떻게 반복 가능한 엔진으로 만들 것인가?",
                "bias": "증폭기와 재사용성 우선",
                "challenge_axis": "발견-구현 단절",
                "likely_contribution": "재사용 가능한 loop, skill, artifact 설계",
            }
        )
    if runtime["mailbox_pending"] or runtime["hub_active_members"] or runtime["drift_detected"]:
        personas.append(
            {
                "name": "CoordinationBroker",
                "role": "조정 브로커",
                "desc": "정규화된 runtime signal을 handoff 가능한 구조로 묶는다.",
                "cognitive_style": "coordination routing",
                "domain": "coordination",
                "question": "현 runtime pressure를 어떤 advisory 구조로 묶어야 하는가?",
                "bias": "signal normalization과 handoff 우선",
                "challenge_axis": "휘발성 신호의 canonical 오염",
                "likely_contribution": "shared impact advisory와 handoff-ready snapshot 생성",
            }
        )
    unique: dict[str, dict[str, Any]] = {}
    for persona in personas:
        unique[persona["name"]] = persona
    return list(unique.values())


def discover_tensions(goal: str, runtime: dict[str, Any]) -> list[str]:
    tensions = [
        f"{goal} 에서 구조 품질과 실행 속도 사이 긴장을 분해해야 한다.",
        f"{goal} 에서 발산된 아이디어와 수렴된 결정 사이 균형을 잡아야 한다.",
    ]
    if runtime["open_risks"]:
        tensions.append(f"open risk {len(runtime['open_risks'])}개를 창조 출력에 무단 승격하지 않아야 한다.")
    if runtime["mailbox_pending"]:
        tensions.append(f"mailbox pending {runtime['mailbox_pending']}건은 advisory pressure로만 다뤄야 한다.")
    if runtime["hub_active_members"]:
        tensions.append(f"Hub active members {', '.join(runtime['hub_active_members'])}는 정규화 snapshot으로만 참조해야 한다.")
    if runtime["drift_detected"]:
        tensions.append("self-recognition drift가 감지되면 authority 승격 전에 재검증해야 한다.")
    return tensions


def discover(goal: str, personas: list[dict[str, Any]], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = []
    tensions = discover_tensions(goal, runtime)
    for index, persona in enumerate(personas):
        tension = tensions[index % len(tensions)]
        outputs.append(
            {
                "persona": persona["name"],
                "role": persona["role"],
                "question": persona["question"],
                "insight": f"{goal} 에서 {persona['role']} 관점으로 `{persona['challenge_axis']}` 축을 우선 분해한다.",
                "tension": tension,
                "bias": persona["bias"],
            }
        )
    return outputs


def verify_persona_balance(personas: list[dict[str, Any]]) -> dict[str, Any]:
    names = {persona["name"] for persona in personas}
    checks = {
        "has_adversarial": "AdversarialReviewer" in names,
        "has_synthesizer": "Synthesizer" in names,
        "has_runtime": "RuntimeOperator" in names,
        "non_duplicate_names": len(names) == len(personas),
        "count_in_range": 4 <= len(personas) <= 7,
    }
    issues = [name for name, passed in checks.items() if not passed]
    return {
        "balanced": not issues,
        "checks": checks,
        "issues": issues,
        "persona_count": len(personas),
    }


def execution_map(personas: list[dict[str, Any]], runtime: dict[str, Any]) -> dict[str, Any]:
    specs = {
        "IntegratorArchitect": {
            "lens": "design",
            "owned_stages": ["Structure", "Converge"],
            "sa_hint": ["SA_ORCHESTRATOR_scan_state", "SA_ORCHESTRATOR_route_handoff"],
            "workstream": "goal을 실행 가능한 구조와 node로 분해",
            "deliverable": "bounded structure proposal",
        },
        "AdversarialReviewer": {
            "lens": "review",
            "owned_stages": ["Challenge", "Verify"],
            "sa_hint": ["SA_ORCHESTRATOR_detect_conflict"],
            "workstream": "실패 경로와 과대평가 지점 공격",
            "deliverable": "risk and breakage list",
        },
        "SafetyGate": {
            "lens": "safety",
            "owned_stages": ["Challenge", "Verify"],
            "sa_hint": ["SA_ORCHESTRATOR_detect_conflict", "SA_ORCHESTRATOR_sync_continuity"],
            "workstream": "authority, safety, guardrail 경계 정리",
            "deliverable": "guardrail and escalation note",
        },
        "RuntimeOperator": {
            "lens": "analysis",
            "owned_stages": ["Discover", "Realize"],
            "sa_hint": ["SA_ORCHESTRATOR_scan_state", "SA_ORCHESTRATOR_idle_maintain"],
            "workstream": "현재 runtime에서 가능한 bounded action 산출",
            "deliverable": "runtime feasibility note",
        },
        "Synthesizer": {
            "lens": "synth",
            "owned_stages": ["Converge", "Record"],
            "sa_hint": ["SA_ORCHESTRATOR_route_handoff", "SA_loop_creative_synerion"],
            "workstream": "발산 결과를 decision과 next step으로 압축",
            "deliverable": "decision and continuity note",
        },
        "ProtocolStrategist": {
            "lens": "design",
            "owned_stages": ["Structure", "Challenge"],
            "sa_hint": ["SA_ORCHESTRATOR_scan_state", "SA_ORCHESTRATOR_route_handoff"],
            "workstream": "contract, schema, handoff protocol 정리",
            "deliverable": "protocol contract proposal",
        },
        "CreativeSystemsBuilder": {
            "lens": "design",
            "owned_stages": ["Discover", "Structure", "Realize"],
            "sa_hint": ["SA_loop_creative_synerion"],
            "workstream": "creative loop와 reusable asset 설계",
            "deliverable": "creative engine extension proposal",
        },
        "CoordinationBroker": {
            "lens": "runtime",
            "owned_stages": ["Discover", "Converge", "Record"],
            "sa_hint": ["SA_ORCHESTRATOR_scan_state", "SA_ORCHESTRATOR_route_handoff"],
            "workstream": "정규화된 mailbox/hub pressure를 advisory 구조로 변환",
            "deliverable": "handoff-ready signal advisory",
        },
    }
    assignments = []
    lane_map: dict[str, str] = {}
    for persona in personas:
        spec = specs.get(persona["name"], specs["IntegratorArchitect"])
        lens = spec["lens"]
        if lens not in lane_map:
            lane_map[lens] = persona["name"]
        assignments.append(
            {
                "persona_id": persona["name"],
                "role": persona["role"],
                "lens": lens,
                "question": persona["question"],
                "bias": persona["bias"],
                "owned_stages": spec["owned_stages"],
                "sa_hint": spec["sa_hint"],
                "subagent": {
                    "enabled": False,
                    "target": "local",
                    "workstream": spec["workstream"],
                    "write_scope": [],
                    "handoff_trigger": "shared-impact or runtime pressure requires bounded routing artifact",
                },
                "deliverable": spec["deliverable"],
                "verify_with": [
                    "persona-balance",
                    "normalized-signal-policy",
                    "continuity-recording",
                ],
            }
        )
    return {
        "schema": "synerion.execution_mapping.v1",
        "goal": runtime.get("goal", ""),
        "execution_mode": "internal_lens",
        "subagent_ready": True,
        "engine_shape": ["Discover", "Structure", "Challenge", "Converge", "Realize", "Verify", "Record"],
        "final_synthesizer": "Synthesizer",
        "lane_map": lane_map,
        "assignments": assignments,
        "synthesis_contract": {
            "input_keys": ["discoveries", "proposal", "risks", "next_steps"],
            "output_keys": ["decision", "bounded_next_step", "continuity_note"],
        },
    }


def structure(goal: str, discoveries: list[dict[str, Any]], runtime: dict[str, Any], mapping: dict[str, Any]) -> dict[str, Any]:
    axes = [item["role"] for item in discoveries]
    return {
        "goal": goal,
        "engine_shape": mapping["engine_shape"],
        "critical_axes": axes,
        "normalized_inputs": [
            "PROJECT_STATUS manual sections",
            "bounded ADP summary",
            "member registry snapshot",
            "mailbox pending count",
            "self-recognition drift report",
        ],
        "runtime_signal_policy": runtime["signal_policy"],
        "draft_proposal": f"{goal} 를 bounded executable structure로 재구성한다.",
    }


def challenge(structured: dict[str, Any], runtime: dict[str, Any], balance: dict[str, Any]) -> list[str]:
    questions = [
        "실시간 런타임 제약과 권한 경계를 넘는가?",
        "구조는 좋아 보여도 verification이 빠져 있지 않은가?",
        "발산은 충분하지만 convergence가 약하지 않은가?",
        "다음 세션 continuity에 바로 연결되는가?",
    ]
    if runtime["mailbox_pending"]:
        questions.append("mailbox pressure를 canonical state로 오해하지 않고 advisory only로 유지했는가?")
    if runtime["hub_active_members"]:
        questions.append("Hub signal은 direct reply가 아니라 broadcast advisory 수준으로만 반영했는가?")
    if runtime["drift_detected"]:
        questions.append("self-recognition drift가 있는 상태에서 authority 승격 판단을 미루고 재검증하게 했는가?")
    if not balance["balanced"]:
        questions.append("persona balance가 깨졌으므로 convergence 결과를 승격하기 전에 persona set을 보강해야 하지 않는가?")
    return questions


def converge(structured: dict[str, Any], challenges: list[str], mapping: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    next_steps = [
        "goal-specific persona set과 execution mapping을 함께 저장한다.",
        "creative output은 timestamped report로 남기고 latest pointer만 별도 유지한다.",
        "runtime signal은 ADP normalized snapshot만 읽고 canonical state로 승격하지 않는다.",
    ]
    if runtime["mailbox_pending"] or runtime["hub_active_members"]:
        next_steps.append("shared-impact가 있으면 direct reply 대신 advisory/handoff artifact를 우선 생성한다.")
    return {
        "proposal": structured["draft_proposal"],
        "challenges": challenges,
        "next_steps": next_steps,
        "decision": "creative cycle을 persona-gen compatible execution mapping형으로 고정한다.",
        "continuity_note": "persona set, execution mapping, creative report를 모두 _workspace 기준으로 기록한다.",
        "lane_map": mapping["lane_map"],
    }


def verify(converged: dict[str, Any], balance: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    if runtime["drift_detected"]:
        warnings.append("self-recognition drift detected; cycle remained advisory-only for runtime signals")
    if runtime["mailbox_pending"]:
        warnings.append("mailbox pending count influenced prioritization only, not canonical state")
    return {
        "passed": balance["balanced"],
        "why": "persona tension, execution mapping, normalized signal policy, timestamped artifacts",
        "next_steps": converged["next_steps"],
        "warnings": warnings,
        "persona_balance_issues": balance["issues"],
    }


def persona_set_payload(goal: str, personas: list[dict[str, Any]], tensions: list[str], balance: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "schema": "synerion.persona_set.v1",
        "goal": goal,
        "generated_at": generated_at,
        "personas": personas,
        "tensions": tensions,
        "balance": balance,
    }


def persona_set_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Synerion Creative Persona Set",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Goal: {payload['goal']}",
        "",
        "## Gantree",
        "",
        "```gantree",
        "PersonaSet",
    ]
    for persona in payload["personas"]:
        lines.append(f"    {persona['name']}")
    lines.extend(["```", "", "## Persona Spec", ""])
    for persona in payload["personas"]:
        lines.extend(
            [
                f"- `{persona['name']}`",
                f"  role: {persona['role']}",
                f"  desc: {persona['desc']}",
                f"  cognitive_style: {persona['cognitive_style']}",
                f"  domain: {persona['domain']}",
                f"  core_question: {persona['question']}",
                f"  bias: {persona['bias']}",
                f"  challenge_axis: {persona['challenge_axis']}",
                f"  likely_contribution: {persona['likely_contribution']}",
            ]
        )
    lines.extend(["", "## Tensions", ""])
    lines.extend(f"- {item}" for item in payload["tensions"])
    lines.extend(["", "## Balance", ""])
    lines.append(f"- balanced: {payload['balance']['balanced']}")
    lines.extend(f"- {name}: {passed}" for name, passed in payload["balance"]["checks"].items())
    return "\n".join(lines) + "\n"


def execution_map_markdown(mapping: dict[str, Any], generated_at: str) -> str:
    lines = [
        "# Synerion Creative Execution Mapping",
        "",
        f"- Generated: {generated_at}",
        f"- Goal: {mapping['goal']}",
        f"- Execution mode: {mapping['execution_mode']}",
        f"- Final synthesizer: {mapping['final_synthesizer']}",
        "",
        "## Lane Map",
        "",
    ]
    lines.extend(f"- {lane}: {persona}" for lane, persona in mapping["lane_map"].items())
    lines.extend(["", "## Assignments", ""])
    for assignment in mapping["assignments"]:
        lines.extend(
            [
                f"- `{assignment['persona_id']}`",
                f"  lens: {assignment['lens']}",
                f"  owned_stages: {', '.join(assignment['owned_stages'])}",
                f"  sa_hint: {', '.join(assignment['sa_hint'])}",
                f"  deliverable: {assignment['deliverable']}",
                f"  handoff_trigger: {assignment['subagent']['handoff_trigger']}",
            ]
        )
    return "\n".join(lines) + "\n"


def persist_persona_artifacts(
    *,
    goal: str,
    personas: list[dict[str, Any]],
    tensions: list[str],
    balance: dict[str, Any],
    mapping: dict[str, Any],
    generated_at: str,
    run_stamp: str,
) -> dict[str, str]:
    PERSONA_ROOT.mkdir(parents=True, exist_ok=True)
    persona_payload = persona_set_payload(goal, personas, tensions, balance, generated_at)
    persona_json = PERSONA_ROOT / f"synerion-creative-persona-set-{run_stamp}.json"
    persona_md = PERSONA_ROOT / f"synerion-creative-persona-set-{run_stamp}.md"
    execution_json = PERSONA_ROOT / f"synerion-creative-execution-map-{run_stamp}.json"
    execution_md = PERSONA_ROOT / f"synerion-creative-execution-map-{run_stamp}.md"

    persona_json_text = json.dumps(persona_payload, ensure_ascii=False, indent=2) + "\n"
    persona_md_text = persona_set_markdown(persona_payload)
    execution_json_text = json.dumps(mapping, ensure_ascii=False, indent=2) + "\n"
    execution_md_text = execution_map_markdown(mapping, generated_at)

    for path, text in (
        (persona_json, persona_json_text),
        (persona_md, persona_md_text),
        (execution_json, execution_json_text),
        (execution_md, execution_md_text),
        (LATEST_PERSONA_JSON, persona_json_text),
        (LATEST_PERSONA_MD, persona_md_text),
        (LATEST_EXECUTION_JSON, execution_json_text),
        (LATEST_EXECUTION_MD, execution_md_text),
    ):
        write_text(path, text)

    return {
        "persona_json": str(persona_json),
        "persona_md": str(persona_md),
        "execution_json": str(execution_json),
        "execution_md": str(execution_md),
        "latest_persona_json": str(LATEST_PERSONA_JSON),
        "latest_persona_md": str(LATEST_PERSONA_MD),
        "latest_execution_json": str(LATEST_EXECUTION_JSON),
        "latest_execution_md": str(LATEST_EXECUTION_MD),
    }


def write_report(payload: dict[str, Any], report_md: Path, report_json: Path) -> None:
    lines = [
        "# Report: Synerion Creative Cycle",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Goal: {payload['goal']}",
        f"- Engine doc: {CORE_ENGINE}",
        f"- Runtime signal policy: {payload['runtime']['signal_policy']}",
        "",
        "## Runtime Signals",
        "",
        f"- mailbox_pending: {payload['runtime']['mailbox_pending']}",
        f"- mailbox_snapshot: {', '.join(payload['runtime']['mailbox_snapshot']) if payload['runtime']['mailbox_snapshot'] else 'none'}",
        f"- hub_active_members: {', '.join(payload['runtime']['hub_active_members']) if payload['runtime']['hub_active_members'] else 'none'}",
        f"- hub_duration_sec: {payload['runtime']['hub_duration_sec']}",
        f"- drift_detected: {payload['runtime']['drift_detected']}",
        f"- latest_report_before_run: {payload['runtime']['latest_report']}",
        "",
        "## Personas",
        "",
    ]
    for persona in payload["personas"]:
        lines.append(f"- {persona['name']} / {persona['role']} / {persona['question']} / axis={persona['challenge_axis']}")
    lines.extend(["", "## Persona Balance", ""])
    lines.append(f"- balanced: {payload['persona_balance']['balanced']}")
    lines.extend(f"- {name}: {passed}" for name, passed in payload["persona_balance"]["checks"].items())
    lines.extend(["", "## Discover", ""])
    for item in payload["discoveries"]:
        lines.append(f"- {item['persona']}: {item['insight']} / tension={item['tension']}")
    lines.extend(
        [
            "",
            "## Structure",
            "",
            f"- Proposal: {payload['structured']['draft_proposal']}",
            f"- Engine shape: {' -> '.join(payload['structured']['engine_shape'])}",
            f"- Normalized inputs: {', '.join(payload['structured']['normalized_inputs'])}",
            "",
            "## Challenge",
            "",
            *(f"- {item}" for item in payload["challenges"]),
            "",
            "## Execution Map",
            "",
            *(f"- {lane}: {persona}" for lane, persona in payload["execution_mapping"]["lane_map"].items()),
            "",
            "## Converged Next Steps",
            "",
            f"- Decision: {payload['converged']['decision']}",
            f"- Continuity note: {payload['converged']['continuity_note']}",
            *(f"- {item}" for item in payload["converged"]["next_steps"]),
            "",
            "## Verify",
            "",
            f"- passed: {payload['verified']['passed']}",
            f"- why: {payload['verified']['why']}",
            *(f"- warning: {item}" for item in payload["verified"]["warnings"]),
            "",
            "## Saved Artifacts",
            "",
            *(f"- {name}: {path}" for name, path in payload["artifacts"].items()),
        ]
    )
    report_text = "\n".join(lines) + "\n"
    payload_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    write_text(report_md, report_text)
    write_text(report_json, payload_text)
    write_text(LATEST_JSON, payload_text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", required=True)
    args = parser.parse_args()

    now = now_local()
    generated_at = now.isoformat()
    run_stamp = now.strftime("%Y-%m-%d-%H%M%S")
    report_md = WORKSPACE / f"REPORT-Synerion-Creative-Cycle-{run_stamp}.md"
    report_json = WORKSPACE / f"synerion-creative-cycle-{run_stamp}.json"

    runtime = runtime_signals()
    runtime["goal"] = args.goal
    personas = list(BASE_PERSONAS)
    personas.extend(compose_domain_personas(args.goal, runtime))
    persona_balance = verify_persona_balance(personas)
    execution_mapping = execution_map(personas, runtime)
    discoveries = discover(args.goal, personas, runtime)
    structured = structure(args.goal, discoveries, runtime, execution_mapping)
    challenges = challenge(structured, runtime, persona_balance)
    converged = converge(structured, challenges, execution_mapping, runtime)
    verified = verify(converged, persona_balance, runtime)
    artifacts = persist_persona_artifacts(
        goal=args.goal,
        personas=personas,
        tensions=discover_tensions(args.goal, runtime),
        balance=persona_balance,
        mapping=execution_mapping,
        generated_at=generated_at,
        run_stamp=run_stamp,
    )

    payload = {
        "generated_at": generated_at,
        "goal": args.goal,
        "runtime": runtime,
        "personas": personas,
        "persona_balance": persona_balance,
        "discoveries": discoveries,
        "structured": structured,
        "challenges": challenges,
        "converged": converged,
        "verified": verified,
        "execution_mapping": execution_mapping,
        "artifacts": artifacts,
    }
    write_report(payload, report_md, report_json)
    print(f"[run-synerion-creative-cycle] wrote {report_md}")
    print(f"[run-synerion-creative-cycle] wrote {report_json}")
    print(f"[run-synerion-creative-cycle] updated {LATEST_JSON}")
    print(f"[run-synerion-creative-cycle] updated {LATEST_PERSONA_MD}")
    print(f"[run-synerion-creative-cycle] updated {LATEST_EXECUTION_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
