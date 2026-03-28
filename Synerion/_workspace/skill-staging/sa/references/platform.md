# SA Platform Reference

Use this when the task is to define, review, or compare an SA platform.

## Platform Definition

A platform is:

```text
SA modules + domain rules + composition pattern + evaluation criteria
```

Platforms are `L3` structures built from `L1` and `L2`.

## Platform Folder Shape

```text
.pgf/self-act/platforms/{NAME}/
    platform.md
    SA_{NAME}_*.pgf
    knowledge/   optional
```

## Review Questions

- Does the platform have a coherent domain boundary?
- Are the modules really platform-specific, or still generic?
- Does the platform define a cycle or execution pattern?
- Are success criteria visible?
- Should this remain local or be promoted to shared space later?

## Shared Promotion Heuristic

Recommend `personal -> candidate-shared -> shared`.

Promote only when:

- the platform has succeeded in repeated use
- module names and IO are stable
- the domain is not tied to one workspace's private assumptions
- at least one additional SeAAI member can understand or review it

## Synerion Platform Bias

Good Synerion platform families include:

- `SA_ORCHESTRATOR_scan_state`
- `SA_ORCHESTRATOR_detect_conflict`
- `SA_ORCHESTRATOR_route_handoff`
- `SA_ORCHESTRATOR_check_shared_impact`
- `SA_ORCHESTRATOR_escalate_creator`

These should optimize system convergence rather than domain novelty.
