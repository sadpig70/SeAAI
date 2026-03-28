# PGF Conflict Mitigation Review

## Scope

- Target: `C:\Users\sadpig70\.codex\skills\pgf`
- Goal: reduce conflict with Codex-native working style
- Date: 2026-03-23

## Main Changes

- changed the default posture from `PGF by default` to `PG first, PGF when worth the overhead`
- made durable `.pgf/` artifacts conditional instead of implicit for normal short tasks
- allowed transient single-turn planning to live in conversation state
- relaxed lightweight mode so `WORKPLAN` and `status` are optional unless resumability, handoff, or auditability matter
- clarified that single `in-progress` applies to durable executable nodes, not every exploratory read/edit step
- allowed execute + verify to collapse in one turn when evidence is already conclusive
- aligned `pgf-format.md` with the new non-durable/lightweight rules

## Verification

- `quick_validate.py` passed after each patch cycle
- searched for stale rules that still forced durable artifacts on every task

## Residual Boundary

- full PGF is still intentionally heavier than plain Codex work for long, multi-phase tasks
- if a user explicitly asks for formal PGF artifacts, the heavier durable path still applies by design
