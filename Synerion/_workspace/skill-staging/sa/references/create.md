# SA Create Reference

Use this when the task is to create or revise a concrete `SA_` module.

## Goal

Turn an action idea into a reusable module with:

- stable name
- explicit layer
- clear inputs and outputs
- known cost
- an execution shape that can be reused later

## Naming

Use `SA_{phase}_{subject}`.

Recommended phases:

- `sense_`
- `think_`
- `act_`
- `idle_`
- `evolve_`
- `loop_`

Examples:

- `SA_sense_hub`
- `SA_think_triage`
- `SA_act_send_mail`
- `SA_idle_deep_think`
- `SA_loop_morning_sync`

## Creation Flow

1. Normalize the requested behavior into one clear module name.
2. Decide the layer:
   - `L1` if it is a single reusable action
   - `L2` if it orchestrates existing `SA_` modules
   - `L3` if it belongs to a platform family
3. Write a compact module artifact that includes:
   - one-line description
   - inputs and outputs
   - cost band
   - Gantree or structured steps
   - PPR-like execution intent when needed
4. Register or update the module in `self-act-lib.md`.
5. Validate that the module is executable in principle and not just descriptive prose.

## Minimal Module Shape

```markdown
# SA_think_triage

> Classify incoming events into WAKE, QUEUE, or DISMISS.

**ID**: SA_think_triage
**Layer**: L1 Primitive
**Input**: events: list
**Output**: routing: dict
**Cost**: low

## Steps
- inspect event urgency
- inspect source and target relevance
- assign WAKE, QUEUE, or DISMISS
```

## Quality Checks

- The name should say what it does without extra explanation.
- The module should be reusable in more than one immediate prompt.
- The boundary with `AI_` should be clear:
  - one-off reasoning stays `AI_`
  - reusable action logic becomes `SA_`
