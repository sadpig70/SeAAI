# SA Loop Reference

Use this when the task is to connect `SA_` modules to ADP behavior or reason about `AI_select_module(...)`.

## Core Loop

```python
while True:
    context = AI_assess_context()
    module = AI_select_module(context, lib)
    if module:
        result = module.execute(context=context)
        if result == "stop":
            break
    AI_sleep(5)
```

## Selection Guidance

Prefer a three-stage selector:

1. hard guards
   - safety
   - creator protection
   - urgent events
   - system health
2. context-based module choice
   - choose the best local module for the current task
3. adaptive weighting
   - apply telemetry or epigenetic optimization only after enough evidence exists

## Practical Priority Order

- WAKE events
- routing and response modules
- scheduled or periodic deep-think modules
- self-evolution modules
- idle or no-op

## Cost Guidance

When integrating with ADP:

- prefer light `sense_` and routing modules on frequent ticks
- reserve expensive `idle_` or `evolve_` modules for sparse intervals or explicit triggers
- avoid designing loops that force heavy cognition every tick

## Synerion Review Lens

When reviewing loop design for Synerion, check:

- whether shared-state impact is visible
- whether conflict escalation exists
- whether creator escalation boundaries are explicit
- whether module choice is explainable, not opaque magic
