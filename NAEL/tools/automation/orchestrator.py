#!/usr/bin/env python3
"""
Agent Workflow Orchestrator
===========================
멀티 에이전트 워크플로우를 선언적으로 정의하고,
Claude Code Agent 디스패치 프롬프트로 변환하는 엔진.

워크플로우 패턴:
  - pipeline: A → B → C (순차)
  - parallel: [A, B, C] → aggregate (병렬)
  - consensus: [A, B, C] → vote → select (합의)
  - iterative: A → review → rework? → done (반복)

사용법 (프롬프트 생성):
  python orchestrator.py --workflow pipeline --topic "주제" --steps "research,analyze,recommend"
  python orchestrator.py --workflow consensus --topic "주제" --agents 4
  python orchestrator.py --workflow iterative --topic "주제" --max-rounds 3
"""

import json
from dataclasses import dataclass, field
from typing import Optional


# ========== Workflow Definitions ==========

@dataclass
class AgentSpec:
    name: str
    role: str
    model: str = "sonnet"  # sonnet for speed, opus for quality
    task_prompt: str = ""
    system_prompt: str = ""


@dataclass
class WorkflowStep:
    name: str
    agents: list[AgentSpec]
    mode: str = "sequential"  # sequential, parallel, consensus
    aggregate_strategy: str = "concatenate"  # concatenate, vote, synthesize
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    name: str
    description: str
    steps: list[WorkflowStep]
    policy: dict = field(default_factory=dict)

    def to_dispatch_plan(self) -> list[dict]:
        """Claude Code Agent 디스패치 계획으로 변환"""
        plan = []
        for step in self.steps:
            step_plan = {
                "step_name": step.name,
                "mode": step.mode,
                "agents": [],
                "aggregate": step.aggregate_strategy,
                "depends_on": step.depends_on,
            }
            for agent in step.agents:
                step_plan["agents"].append({
                    "name": agent.name,
                    "role": agent.role,
                    "model": agent.model,
                    "task": agent.task_prompt,
                    "system": agent.system_prompt,
                })
            plan.append(step_plan)
        return plan


# ========== Pre-built Workflow Templates ==========

def build_pipeline_workflow(
    topic: str,
    steps: list[str],
    model: str = "sonnet",
) -> Workflow:
    """순차 파이프라인 워크플로우"""
    wf_steps = []
    for i, step_name in enumerate(steps):
        agent = AgentSpec(
            name=f"agent_{step_name}",
            role=f"{step_name} specialist",
            model=model,
            task_prompt=_pipeline_task(topic, step_name, i, steps),
        )
        depends = [steps[i - 1]] if i > 0 else []
        wf_steps.append(WorkflowStep(
            name=step_name,
            agents=[agent],
            mode="sequential",
            depends_on=depends,
        ))

    return Workflow(
        name=f"pipeline_{topic[:30]}",
        description=f"Pipeline: {' → '.join(steps)}",
        steps=wf_steps,
    )


def build_consensus_workflow(
    topic: str,
    num_agents: int = 4,
    model: str = "sonnet",
) -> Workflow:
    """합의 기반 워크플로우 — 독립 분석 → 투표 → 합의"""
    roles = [
        ("Optimist", "Focus on opportunities and potential"),
        ("Skeptic", "Focus on risks and failure modes"),
        ("Pragmatist", "Focus on feasibility and cost"),
        ("Visionary", "Focus on long-term impact and innovation"),
        ("Analyst", "Focus on data and evidence"),
        ("Ethicist", "Focus on societal impact and fairness"),
        ("Economist", "Focus on market dynamics and ROI"),
        ("Engineer", "Focus on technical implementation"),
    ]

    agents = []
    for i in range(min(num_agents, len(roles))):
        name, bias = roles[i]
        agents.append(AgentSpec(
            name=name,
            role=f"{name} analyst",
            model=model,
            system_prompt=f"You are {name}. Your analytical focus: {bias}. Argue from this perspective.",
            task_prompt=f"## Topic\n{topic}\n\n## Task\nAnalyze this topic from your perspective. Provide:\n1. Your assessment (200-300 words)\n2. Key recommendation\n3. Confidence level (1-10)\n4. Top risk from your viewpoint",
        ))

    # Step 1: Independent analysis (parallel)
    step1 = WorkflowStep(
        name="independent_analysis",
        agents=agents,
        mode="parallel",
        aggregate_strategy="concatenate",
    )

    # Step 2: Synthesis (single agent reads all)
    synthesizer = AgentSpec(
        name="Synthesizer",
        role="neutral moderator",
        model="opus" if model == "opus" else "sonnet",
        task_prompt=(
            f"## Topic\n{topic}\n\n"
            "## All Agent Analyses\n{prev_results}\n\n"
            "## Task: Consensus Synthesis\n"
            "1. Identify consensus points (where 3+ agents agree)\n"
            "2. Identify key disagreements\n"
            "3. Tally recommendations and confidence levels\n"
            "4. Provide final integrated recommendation\n"
            "5. Rate overall confidence (1-10)"
        ),
    )

    step2 = WorkflowStep(
        name="synthesis",
        agents=[synthesizer],
        mode="sequential",
        aggregate_strategy="synthesize",
        depends_on=["independent_analysis"],
    )

    return Workflow(
        name=f"consensus_{topic[:30]}",
        description=f"Consensus: {num_agents} agents → synthesize",
        steps=[step1, step2],
    )


def build_iterative_workflow(
    topic: str,
    max_rounds: int = 3,
    model: str = "sonnet",
) -> Workflow:
    """반복 정제 워크플로우 — 생성 → 비판 → 개선 → 비판 → ..."""
    steps = []

    # Initial generation
    creator = AgentSpec(
        name="Creator",
        role="content creator",
        model=model,
        task_prompt=f"## Task\n{topic}\n\nCreate an initial high-quality response. Be thorough.",
    )
    steps.append(WorkflowStep(name="create", agents=[creator]))

    for r in range(1, max_rounds + 1):
        # Critic
        critic = AgentSpec(
            name=f"Critic_R{r}",
            role="harsh critic",
            model=model,
            task_prompt=(
                "## Previous Output\n{prev_results}\n\n"
                "## Task: Critique\n"
                "Identify specific weaknesses, errors, or improvements needed.\n"
                "Rate current quality: 1-10.\n"
                "If quality >= 9, output 'APPROVED' and stop.\n"
                "Otherwise, list specific actionable improvements."
            ),
        )
        steps.append(WorkflowStep(
            name=f"critique_r{r}",
            agents=[critic],
            depends_on=[f"improve_r{r-1}" if r > 1 else "create"],
        ))

        # Improver
        improver = AgentSpec(
            name=f"Improver_R{r}",
            role="content improver",
            model=model,
            task_prompt=(
                "## Original + Critique\n{prev_results}\n\n"
                "## Task: Improve\n"
                "Address EVERY critique point. Produce an improved version.\n"
                "If critique says 'APPROVED', output the current version unchanged."
            ),
        )
        steps.append(WorkflowStep(
            name=f"improve_r{r}",
            agents=[improver],
            depends_on=[f"critique_r{r}"],
        ))

    return Workflow(
        name=f"iterative_{topic[:30]}",
        description=f"Iterative: create → (critique → improve) x {max_rounds}",
        steps=steps,
    )


def build_research_synthesis_workflow(
    topic: str,
    num_researchers: int = 3,
    model: str = "sonnet",
) -> Workflow:
    """리서치 → 합성 워크플로우"""
    # Step 1: Parallel research
    researchers = []
    angles = [
        "academic/scientific perspective",
        "industry/market perspective",
        "practical/implementation perspective",
        "historical/evolution perspective",
        "future/prediction perspective",
    ]
    for i in range(min(num_researchers, len(angles))):
        researchers.append(AgentSpec(
            name=f"Researcher_{i+1}",
            role=f"researcher ({angles[i]})",
            model=model,
            task_prompt=(
                f"## Research Topic\n{topic}\n\n"
                f"## Your Angle\n{angles[i]}\n\n"
                "## Task\n"
                "Use WebSearch to find 3-5 authoritative sources on this topic from your angle.\n"
                "For each source: URL, key findings, reliability assessment.\n"
                "Then synthesize your findings into a structured summary."
            ),
        ))

    step1 = WorkflowStep(
        name="research",
        agents=researchers,
        mode="parallel",
        aggregate_strategy="concatenate",
    )

    # Step 2: Knowledge synthesis
    synthesizer = AgentSpec(
        name="Synthesizer",
        role="knowledge synthesizer",
        model="opus" if model == "opus" else "sonnet",
        task_prompt=(
            f"## Topic\n{topic}\n\n"
            "## Research Results\n{prev_results}\n\n"
            "## Task: Cross-Domain Synthesis\n"
            "Synthesize all research into a comprehensive knowledge document:\n"
            "1. Key findings (numbered, with source attribution)\n"
            "2. Cross-source patterns and connections\n"
            "3. Contradictions between sources\n"
            "4. Knowledge gaps\n"
            "5. Actionable conclusions"
        ),
    )

    step2 = WorkflowStep(
        name="synthesize",
        agents=[synthesizer],
        depends_on=["research"],
    )

    return Workflow(
        name=f"research_{topic[:30]}",
        description=f"Research: {num_researchers} parallel researchers → synthesize",
        steps=[step1, step2],
    )


# ========== Helper ==========

def _pipeline_task(topic: str, step_name: str, index: int, all_steps: list[str]) -> str:
    context = f"This is step {index + 1}/{len(all_steps)} in a pipeline: {' → '.join(all_steps)}"
    if index == 0:
        return f"## Topic\n{topic}\n\n## Context\n{context}\n\n## Task\nPerform the '{step_name}' step. Output structured results for the next step."
    else:
        return (
            f"## Topic\n{topic}\n\n## Context\n{context}\n\n"
            f"## Input from Previous Step\n{{prev_results}}\n\n"
            f"## Task\nPerform the '{step_name}' step using the input from the previous step."
        )


def workflow_to_readable(wf: Workflow) -> str:
    """워크플로우를 읽기 쉬운 마크다운으로 변환"""
    lines = [
        f"# Workflow: {wf.name}",
        f"",
        f"{wf.description}",
        f"",
        "## Execution Plan",
        "",
    ]

    for i, step in enumerate(wf.steps, 1):
        mode_icon = {"parallel": "[parallel]", "sequential": "→", "consensus": "⊕"}.get(step.mode, "→")
        lines.append(f"### Step {i}: {step.name} {mode_icon}")
        if step.depends_on:
            lines.append(f"  Depends on: {', '.join(step.depends_on)}")
        lines.append(f"  Agents: {len(step.agents)}")
        for agent in step.agents:
            lines.append(f"  - **{agent.name}** ({agent.role}) [model: {agent.model}]")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent Workflow Orchestrator")
    parser.add_argument("--workflow", required=True,
                        choices=["pipeline", "consensus", "iterative", "research"],
                        help="Workflow type")
    parser.add_argument("--topic", required=True, help="Topic/task")
    parser.add_argument("--steps", help="Pipeline steps (comma-separated)")
    parser.add_argument("--agents", type=int, default=4, help="Number of agents")
    parser.add_argument("--max-rounds", type=int, default=3, help="Max iteration rounds")
    parser.add_argument("--model", default="sonnet", choices=["sonnet", "opus", "haiku"])
    parser.add_argument("--format", default="readable", choices=["readable", "json"])
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    if args.workflow == "pipeline":
        steps = args.steps.split(",") if args.steps else ["research", "analyze", "recommend"]
        wf = build_pipeline_workflow(args.topic, steps, args.model)
    elif args.workflow == "consensus":
        wf = build_consensus_workflow(args.topic, args.agents, args.model)
    elif args.workflow == "iterative":
        wf = build_iterative_workflow(args.topic, args.max_rounds, args.model)
    else:
        wf = build_research_synthesis_workflow(args.topic, args.agents, args.model)

    if args.format == "json":
        result = json.dumps(wf.to_dispatch_plan(), indent=2, ensure_ascii=False)
    else:
        result = workflow_to_readable(wf)

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
