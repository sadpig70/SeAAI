#!/usr/bin/env python3
"""
Multi-Persona Debate Engine
============================
N개의 관점(페르소나)이 주어진 주제에 대해 구조화된 토론을 수행하고
최종 종합 결론을 도출하는 인지 도구.

사용법:
  python debate.py --topic "주제" [--preset tech] [--rounds 3] [--output result.md]

모드:
  quick    — 단일 프롬프트로 전체 토론 시뮬레이션 (기본)
  dispatch — 멀티 에이전트 디스패치용 JSON 프롬프트 생성

dispatch 모드 반환값의 플레이스홀더:
  - round > 1의 task에 "{prev_round_results}" 포함 → 호출자가 이전 라운드 결과로 치환
  - synthesis_prompt에 "{all_rounds}" 포함 → 호출자가 전체 라운드 결과로 치환
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


PREV_ROUND_PLACEHOLDER = "{prev_round_results}"
ALL_ROUNDS_PLACEHOLDER = "{all_rounds}"


@dataclass
class Persona:
    name: str
    role: str
    bias: str  # 의도적 편향 — 다양성 확보용
    instruction: str = ""

    def to_system_prompt(self) -> str:
        extra = f"Additional: {self.instruction}\n" if self.instruction else ""
        return (
            f"You are {self.name}, a {self.role}.\n"
            f"Your analytical bias: {self.bias}\n"
            f"{extra}\n"
            f"Rules:\n"
            f"- Argue STRONGLY from your perspective\n"
            f"- Challenge other viewpoints with evidence\n"
            f"- Acknowledge valid counterpoints when they exist\n"
            f"- Be concise but thorough"
        )


# 기본 페르소나 세트 — 6가지 사고 모자 (De Bono 변형)
DEFAULT_PERSONAS = [
    Persona("Architect", "systems architect", "structural elegance, long-term scalability"),
    Persona("Pragmatist", "field engineer", "immediate feasibility, cost-effectiveness"),
    Persona("Critic", "security auditor", "risk identification, failure modes"),
    Persona("Innovator", "R&D researcher", "novelty, unexplored possibilities"),
    Persona("User Advocate", "UX researcher", "user experience, accessibility"),
    Persona("Economist", "business analyst", "ROI, market viability, resource efficiency"),
]

# 도메인별 전문 페르소나 프리셋
DOMAIN_PRESETS = {
    "tech": [
        Persona("Backend", "backend engineer", "performance, reliability, data integrity"),
        Persona("Frontend", "frontend developer", "user interaction, responsiveness, aesthetics"),
        Persona("DevOps", "infrastructure engineer", "deployment, monitoring, scalability"),
        Persona("Security", "security researcher", "attack vectors, vulnerabilities, compliance"),
    ],
    "business": [
        Persona("CEO", "startup CEO", "vision, growth, market positioning"),
        Persona("CFO", "financial controller", "cash flow, unit economics, risk"),
        Persona("CTO", "technical leader", "technical debt, team capacity, architecture"),
        Persona("Customer", "power user", "pain points, switching costs, alternatives"),
    ],
    "research": [
        Persona("Theorist", "theoretical researcher", "mathematical rigor, formal proofs"),
        Persona("Experimentalist", "lab researcher", "reproducibility, empirical evidence"),
        Persona("Reviewer", "peer reviewer", "methodology flaws, statistical validity"),
        Persona("Ethicist", "ethics board member", "societal impact, fairness, transparency"),
    ],
}


@dataclass
class DebateRound:
    round_num: int
    arguments: dict[str, str] = field(default_factory=dict)
    rebuttals: dict[str, str] = field(default_factory=dict)


@dataclass
class DebateResult:
    topic: str
    personas: list[Persona]
    rounds: list[DebateRound]
    synthesis: str = ""
    consensus_points: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    recommendation: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"# Debate: {self.topic}",
            "",
            f"**Personas**: {', '.join(p.name for p in self.personas)}",
            f"**Rounds**: {len(self.rounds)}",
            "",
        ]

        for r in self.rounds:
            lines.append(f"## Round {r.round_num}")
            lines.append("")
            for name, arg in r.arguments.items():
                lines.append(f"### [{name}]")
                lines.append(arg)
                lines.append("")
            if r.rebuttals:
                lines.append("### Rebuttals")
                for name, reb in r.rebuttals.items():
                    lines.append(f"**{name}**: {reb}")
                    lines.append("")

        lines.append("## Synthesis")
        lines.append(self.synthesis)
        lines.append("")

        if self.consensus_points:
            lines.append("## Consensus Points")
            for cp in self.consensus_points:
                lines.append(f"- {cp}")
            lines.append("")

        if self.disagreements:
            lines.append("## Remaining Disagreements")
            for d in self.disagreements:
                lines.append(f"- {d}")
            lines.append("")

        if self.recommendation:
            lines.append("## Recommendation")
            lines.append(self.recommendation)

        return "\n".join(lines)


def _validate_debate_args(topic: str, personas: list[Persona], num_rounds: int) -> None:
    """공통 입력 검증."""
    if not topic or not topic.strip():
        raise ValueError("topic must be a non-empty string")
    if num_rounds < 1:
        raise ValueError(f"num_rounds must be >= 1, got {num_rounds}")
    if not personas:
        raise ValueError("personas list must not be empty")


def debate_dispatch(
    topic: str,
    personas: Optional[list[Persona]] = None,
    num_rounds: int = 3,
    context: str = "",
) -> dict:
    """
    Claude Code Agent 디스패치용 프롬프트 생성기.

    Returns:
        {
            "round_prompts": [{
                "round": 1,
                "agent_prompts": [{"persona": name, "system": ..., "task": ...}, ...]
            }, ...],
            "synthesis_prompt": str,
            "personas": [{"name": ..., "role": ..., "bias": ...}, ...],
            "placeholders": {
                "prev_round_results": "Replace in round>1 tasks with previous round output",
                "all_rounds": "Replace in synthesis_prompt with all round outputs"
            }
        }

    Placeholders:
        round > 1의 task 프롬프트에 "{prev_round_results}" 리터럴이 포함됨.
        호출자는 이전 라운드의 에이전트 출력을 모아 이 자리에 치환해야 함.
        synthesis_prompt에는 "{all_rounds}"가 포함됨 — 전체 라운드 결과를 치환.
    """
    if personas is None:
        personas = DEFAULT_PERSONAS

    _validate_debate_args(topic, personas, num_rounds)

    ctx_block = f"## Context\n{context}\n\n" if context else ""

    round_prompts = []
    for r in range(1, num_rounds + 1):
        agent_prompts = []
        for p in personas:
            if r == 1:
                task = (
                    f"## Topic\n{topic}\n\n"
                    f"{ctx_block}"
                    f"## Task\n"
                    f"Present your opening argument on this topic from your perspective as {p.role}.\n"
                    f"Structure: (1) Core position (2) Key evidence/reasoning (3) Implications\n"
                    f"Length: 200-400 words."
                )
            else:
                task = (
                    f"## Topic\n{topic}\n\n"
                    f"## Previous Round Arguments\n"
                    f"{PREV_ROUND_PLACEHOLDER}\n\n"
                    f"## Task\n"
                    f"Round {r}: Read all previous arguments. Then:\n"
                    f"(1) Identify the strongest counterpoint to YOUR position\n"
                    f"(2) Respond to it — concede if valid, rebut if not\n"
                    f"(3) Strengthen your position with new evidence or angle\n"
                    f"(4) If your view has evolved, explain how and why\n"
                    f"Length: 150-300 words."
                )

            agent_prompts.append({
                "persona": p.name,
                "system": p.to_system_prompt(),
                "task": task,
            })
        round_prompts.append({"round": r, "agent_prompts": agent_prompts})

    synthesis_prompt = (
        f"## Topic\n{topic}\n\n"
        f"## All Debate Rounds\n{ALL_ROUNDS_PLACEHOLDER}\n\n"
        f"## Task — Synthesis\n"
        f"You are a neutral moderator. Analyze the entire debate and produce:\n"
        f"1. **Consensus Points** — Where all/most personas agree\n"
        f"2. **Key Disagreements** — Unresolved tensions and why they persist\n"
        f"3. **Synthesis** — Integrated understanding that transcends individual positions\n"
        f"4. **Recommendation** — What should be done, considering all perspectives\n"
        f"5. **Confidence** — How confident are you in this recommendation (1-10) and why"
    )

    return {
        "round_prompts": round_prompts,
        "synthesis_prompt": synthesis_prompt,
        "personas": [{"name": p.name, "role": p.role, "bias": p.bias} for p in personas],
        "placeholders": {
            "prev_round_results": "Replace in round>1 tasks with previous round output",
            "all_rounds": "Replace in synthesis_prompt with all round outputs",
        },
    }


def run_debate(
    topic: str,
    llm_caller: Callable[[str, str], str],
    personas: Optional[list[Persona]] = None,
    num_rounds: int = 3,
    context: str = "",
) -> DebateResult:
    """
    실제 토론 실행 — llm_caller를 주입받아 전체 사이클을 수행.

    Args:
        topic: 토론 주제
        llm_caller: (system_prompt, task_prompt) -> response_text 형태의 호출 함수
        personas: 참여 페르소나 (None이면 DEFAULT_PERSONAS)
        num_rounds: 토론 라운드 수
        context: 추가 컨텍스트

    Returns:
        DebateResult — to_markdown()으로 마크다운 변환 가능
    """
    if personas is None:
        personas = DEFAULT_PERSONAS

    _validate_debate_args(topic, personas, num_rounds)

    dispatch = debate_dispatch(topic, personas, num_rounds, context)
    rounds = []
    all_round_texts = []

    for rp in dispatch["round_prompts"]:
        round_num = rp["round"]
        dr = DebateRound(round_num=round_num)

        for ap in rp["agent_prompts"]:
            task = ap["task"]
            # 플레이스홀더 치환
            if round_num > 1 and all_round_texts:
                prev_text = all_round_texts[-1]
                task = task.replace(PREV_ROUND_PLACEHOLDER, prev_text)

            response = llm_caller(ap["system"], task)
            dr.arguments[ap["persona"]] = response

        # 이 라운드 결과를 텍스트로 모음
        round_text_parts = []
        for name, arg in dr.arguments.items():
            round_text_parts.append(f"### [{name}]\n{arg}")
        round_text = "\n\n".join(round_text_parts)
        all_round_texts.append(round_text)
        rounds.append(dr)

    # 합성
    full_rounds_text = "\n\n---\n\n".join(
        f"## Round {i+1}\n{txt}" for i, txt in enumerate(all_round_texts)
    )
    synth_prompt = dispatch["synthesis_prompt"].replace(ALL_ROUNDS_PLACEHOLDER, full_rounds_text)
    synthesis_response = llm_caller("You are a neutral debate moderator.", synth_prompt)

    return DebateResult(
        topic=topic,
        personas=personas,
        rounds=rounds,
        synthesis=synthesis_response,
    )


def generate_quick_debate_prompt(topic: str, preset: str = "default") -> str:
    """
    단일 프롬프트로 실행 가능한 압축 토론.
    Agent 하나에 전체 토론을 시뮬레이션하게 함.
    """
    if not topic or not topic.strip():
        raise ValueError("topic must be a non-empty string")

    if preset in DOMAIN_PRESETS:
        personas = DOMAIN_PRESETS[preset]
    else:
        personas = DEFAULT_PERSONAS[:4]  # 압축 버전은 4명

    persona_desc = "\n".join(
        f"- **{p.name}** ({p.role}): bias toward {p.bias}" for p in personas
    )

    return f"""# Multi-Persona Debate: {topic}

## Personas
{persona_desc}

## Instructions
Simulate a structured debate between these {len(personas)} personas.

### Round 1 — Opening Positions
Each persona states their position on the topic (100-200 words each).

### Round 2 — Challenge & Response
Each persona identifies the strongest counter-argument to their position and responds.

### Round 3 — Final Positions
Each persona states their evolved position, noting what changed and what held firm.

### Synthesis
As a neutral moderator, provide:
1. **Consensus points** — agreements across personas
2. **Persistent disagreements** — and why they matter
3. **Integrated recommendation** — actionable conclusion
4. **Confidence level** — 1-10 with justification

Be rigorous. Each persona must argue authentically from their stated bias.
Do NOT let all personas converge artificially — real disagreements should persist.
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Persona Debate Engine")
    parser.add_argument("--topic", required=True, help="Debate topic")
    parser.add_argument("--preset", default="default",
                        help="Persona preset: default, tech, business, research")
    parser.add_argument("--mode", default="quick",
                        choices=["quick", "dispatch"],
                        help="quick=single prompt, dispatch=multi-agent prompts")
    parser.add_argument("--rounds", type=int, default=3,
                        help="Number of debate rounds")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.mode == "quick":
        result = generate_quick_debate_prompt(args.topic, args.preset)
    else:
        personas = DOMAIN_PRESETS.get(args.preset, DEFAULT_PERSONAS)
        result = json.dumps(
            debate_dispatch(args.topic, personas, args.rounds),
            indent=2, ensure_ascii=False,
        )

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
