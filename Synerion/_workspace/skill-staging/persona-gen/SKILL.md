---
name: persona-gen
description: "목적 기반 최적 멀티페르소나 생성. 목표를 받아 Synerion/Codex용 멀티페르소나 세트를 PG로 설계하고, 서브에이전트/검증용 분업 구성을 함께 제안한다."
---

# Persona Generator For Codex

Use this skill when the task is to generate personas, compose a review team, design a multi-perspective debate set, or turn one problem into multiple specialized viewpoints.

- Keep PG as the canonical language.
- Keep persona generation tied to the actual goal, not fixed character slots.
- For Synerion, bias toward personas that improve structure, integration, verification, routing, and safe execution.
- If the user wants parallel execution, map personas to subagent roles or workstreams explicitly.

## Start

1. Read the project goal and constraints.
2. Extract required domains, tensions, and missing perspectives.
3. Generate the smallest high-value persona set.
4. Verify tension and convergence balance.
5. Output in PG plus an execution mapping.

## Codex-Specific Rules

- Do not assume Claude slash commands like `/persona-gen`.
- Do not assume a fixed output path under `SeAAIHub/tools/`.
- Prefer storing generated persona sets under `_workspace/personas/` or another workspace-local path.
- If the user also wants execution, connect persona output to subagent roles, review stages, or SA modules.
- If no execution is requested, stop at the persona design artifact.

## Output Shape

Return or write two layers:

1. `PG persona set`
   - Gantree overview
   - persona spec list
   - tension structure

2. `execution mapping`
   - which persona handles analysis
   - which persona handles design
   - which persona handles adversarial review
   - which persona handles synthesis

## Mode Routing

- create or revise a persona set:
  [references/design.md](references/design.md)
- map personas to subagent or workflow execution:
  [references/execute.md](references/execute.md)

## Synerion Bias

When the task is inside Synerion, start from these likely persona families:

- Integrator
- Architect
- Adversarial Reviewer
- Safety Gate
- Operator
- Synthesizer

Add domain personas only when the task actually needs them.
