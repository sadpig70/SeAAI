# REVIEW-SynerionPgf-2026-03-23

## Scope
- Target: `D:\SeAAI\Synerion\pgf`
- Date: 2026-03-23
- Mode: review | verify
- Method: local PG-based review + Codex subagent multi-persona cross-check

## Review Inputs
- Canonical PG: `D:\SeAAI\SharedSpace\pg\SKILL.md`
- Reviewed docs:
  - `D:\SeAAI\Synerion\pgf\SKILL.md`
  - `D:\SeAAI\Synerion\pgf\pgf-format.md`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md`
  - `D:\SeAAI\Synerion\pgf\codex-runtime-reference.md`
  - `D:\SeAAI\Synerion\pgf\agent-protocol.md`
  - `D:\SeAAI\Synerion\pgf\verify-reference.md`

## Summary
Initial review found multiple material issues. Those findings were subsequently patched in iterative review/fix cycles.
Final local validation and subagent re-checks converged on no remaining high-severity contradictions, and the last medium findings around `decomposed` dependency completion and leaf-only activation were also patched.

## Findings

### [high][state-machine] `needs-verify` is defined but not consumable by the runtime
- Evidence:
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:59`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:74`
  - `D:\SeAAI\Synerion\pgf\codex-runtime-reference.md:130`
  - `D:\SeAAI\Synerion\pgf\verify-reference.md:66`
- Impact:
  - A node can enter `needs-verify`, but next-node selection only picks `in-progress` or dependency-ready `designing`.
  - Verification results are expressed as `passed | rework | blocked`, not as a state transition contract back into WORKPLAN.
  - Result: verify-pending nodes can become orphaned or be bypassed.
- Recommendation:
  - Define explicit transitions for `needs-verify`.
  - Add scheduler rules for verify-pending nodes.
  - Specify how verify verdicts mutate WORKPLAN and `status-{Name}.json`.

### [high][execution-model] WORKPLAN initialization can create multiple active nodes without an explicit `[parallel]` contract
- Evidence:
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:40`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:42`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:75`
- Impact:
  - The conversion rule marks all dependency-free top-level nodes as `in-progress`.
  - The selector then chooses only the first `in-progress` node.
  - This breaks PG semantics where concurrency should be explicit through `[parallel]`, and it makes resume semantics ambiguous.
- Recommendation:
  - Keep exactly one current node as `in-progress` unless a `[parallel]` block explicitly authorizes concurrent execution.
  - Represent ready-but-not-current nodes as `designing` or a separate `ready` concept if needed.

### [high][persistence] Retry and verify-cycle limits are not enforceable across turns
- Evidence:
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:19`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:22`
  - `D:\SeAAI\Synerion\pgf\codex-runtime-reference.md:105`
  - `D:\SeAAI\Synerion\pgf\pgf-format.md:109`
- Impact:
  - `max_retry` and `max_verify_cycles` exist in POLICY, but the status JSON schema stores no retry counters or verify-cycle counters.
  - In a turn-based runtime, those counters must persist or the limits are not real.
- Recommendation:
  - Extend `status-{Name}.json` with per-node `attempt_count`, `verify_cycle_count`, and optional `last_failure`.
  - Define counter update rules in both WORKPLAN and runtime references.

### [medium][safety] Delegation authority bounds are underspecified
- Evidence:
  - `D:\SeAAI\Synerion\pgf\agent-protocol.md:17`
  - `D:\SeAAI\Synerion\pgf\agent-protocol.md:57`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:24`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:35`
- Impact:
  - Delegation is allowed only with user authorization, which is correct.
  - But the TaskSpec does not define explicit authority bounds such as writable paths, forbidden actions, destructive command restrictions, or escalation rules.
  - `write_scope` is documented as policy, but not as a structured agent contract.
- Recommendation:
  - Add an `authority_bounds` section to delegated TaskSpecs.
  - Include `allowed_paths`, `forbidden_actions`, `network_policy`, and `escalation_policy`.

### [medium][schema-drift] POLICY schema is inconsistent between format and execution references
- Evidence:
  - `D:\SeAAI\Synerion\pgf\pgf-format.md:75`
  - `D:\SeAAI\Synerion\pgf\workplan-reference.md:17`
- Impact:
  - `pgf-format.md` shows a minimal POLICY example.
  - `workplan-reference.md` treats `delegate_allowed` and `write_scope` as operational controls.
  - A future generator following only the format file may omit execution-critical safety fields.
- Recommendation:
  - Make one POLICY schema canonical.
  - Reference that schema from all other documents instead of duplicating partial examples.

### [medium][mode-contract] `micro` and lightweight execution are not fully connected to the runtime contract
- Evidence:
  - `D:\SeAAI\Synerion\pgf\SKILL.md:58`
  - `D:\SeAAI\Synerion\pgf\SKILL.md:88`
  - `D:\SeAAI\Synerion\pgf\codex-runtime-reference.md:40`
- Impact:
  - The skill doc allows `micro` and inline execution for small work.
  - The runtime algorithm still assumes `WORKPLAN-{Name}.md` and `status-{Name}.json` exist.
  - It is unclear when small tasks remain artifact-free and when they must auto-promote into `.pgf/` artifacts.
- Recommendation:
  - Add an explicit promotion rule:
    - artifact-free inline
    - lightweight WORKPLAN-only
    - full DESIGN + WORKPLAN + status
  - Define the exact trigger for each transition.

### [low][verification-rigor] Verification falls back to node description too easily
- Evidence:
  - `D:\SeAAI\Synerion\pgf\verify-reference.md:18`
  - `D:\SeAAI\Synerion\pgf\verify-reference.md:20`
- Impact:
  - Using node description as fallback criteria weakens PG's goal of verifiable acceptance contracts.
  - Two different reviewers may reach different pass/fail outcomes from the same prose.
- Recommendation:
  - Treat missing `acceptance_criteria` as a signal to strengthen the node spec or promote formalization level, not as a stable verification base.

## Cross-Persona Notes
- Architecture persona and adversarial persona strongly agreed on the `needs-verify` orphan-state problem.
- Runtime persona and local review strongly agreed on retry persistence being missing.
- One runtime persona claimed Codex subagent capability was absent. That claim was discarded because the current Codex runtime does expose subagent tools in this session. The retained issue is not capability absence, but insufficient delegation safety specification.

## Next Actions
- Close the state-machine contract first: `needs-verify`, selector rules, verify-state mutation.
- Unify POLICY schema and status JSON persistence fields.
- Tighten delegation TaskSpec with explicit authority bounds.
- Define formal promotion rules for `micro` -> lightweight -> full PGF.

## Final Status
- Final pass state: no remaining material high/medium findings after the last patch set
- Residual risk: future implementation may still need concrete parser/serializer utilities, but the current document set is internally consistent enough to act as the Codex-native PGF core
