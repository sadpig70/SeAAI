---
name: sa
description: Use this skill when the task involves SelfAct, SA modules, `SA_` naming, `self-act-lib.md`, SA platforms, SA loop design, or evolving ADP behavior through reusable action modules. Use it to design, review, organize, or integrate `SA_` modules in Codex workspaces, especially for SeAAI and Synerion.
---

# SA

Use this skill as the Codex-native entry point for SelfAct.

- Treat `SA_` as the reusable action-module layer that sits above `AI_` ad hoc cognition.
- Treat `self-act-lib.md` as the action index and selection surface.
- Treat SA as a library of reusable behaviors, not as a replacement for PG or PGF.

## Relation To PG And PGF

- `PG` is the language for structure and intent.
- `PGF` is the execution framework for durable workflows and review.
- `SA` is the reusable action-module library for ADP and autonomous behavior loops.

If the task depends on PG notation or PGF state artifacts, also follow the relevant `pg` and `pgf` skills.

## When To Use

Use this skill when the user asks to:

- create or revise `SA_` modules
- design or review `self-act-lib.md`
- define `SA_ORCHESTRATOR_*` or other SA platforms
- connect SA modules to ADP loops
- compare `AI_` and `SA_`
- decide when a personal SA module should move to shared space
- reason about module selection such as `AI_select_module(...)`

## Core Model

Use this mental model:

```text
tool call     -> deterministic operation like Read/Write/Bash
AI_           -> one-off cognition, judgment, or generation
SA_           -> stored, reusable, composable SelfAct module
SA platform   -> domain-specific family of SA modules
```

Use these three layers:

```text
L1 Primitive  -> single action modules
L2 Composed   -> combinations of L1 modules
L3 Platform   -> domain-specific module families
```

## Default Workflow

1. Identify the user's actual intent: inspect, create, evolve, platformize, or loop-integrate.
2. Check whether the task is local-only or affects shared SeAAI conventions.
3. Keep `SA_` as a SeAAI execution convention unless the user explicitly wants to change PG itself.
4. Prefer the smallest useful artifact set:
   - inline notes for small clarifications
   - local `SA_*.pgf` modules for concrete reusable actions
   - platform folders only when a family of modules is forming
5. Validate naming, layer, inputs, outputs, cost, and execution context before calling the module done.

## Mode Routing

Read only the reference you need:

- creating or rewriting a module:
  [create.md](references/create.md)
- evolving an SA library or mutation logic:
  [evolve.md](references/evolve.md)
- defining or reviewing a platform:
  [platform.md](references/platform.md)
- connecting SA to loops and module selection:
  [loop.md](references/loop.md)

## Codex-Specific Rules

- Do not assume Claude slash commands such as `/sa`.
- Express execution as Codex work: read docs, patch files, validate outputs.
- Prefer local workspace artifacts like `.pgf/self-act/` over global mutation unless the user explicitly wants shared installation.
- For SeAAI work, treat shared-space promotion as a separate decision after local validation.
- When reviewing SA design, focus on:
  - `AI_` vs `SA_` boundary
  - local vs shared scope
  - module selection policy
  - platform cohesion
  - ADP cost and loop behavior

## Initial Synerion Bias

For Synerion-specific SA work, bias toward `SA_ORCHESTRATOR_*` modules such as:

- state scan
- conflict detection
- handoff routing
- shared-impact checking
- promotion decision
- creator escalation

These should optimize for convergence, coordination, and controlled escalation rather than raw creation.
