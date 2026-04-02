# Persona-Gen Execution Reference

Use this when the user wants to connect personas to actual execution, verification, or subagent work.

## Goal

Translate a persona set into concrete work ownership.

## Mapping Rule

```ppr
def map_personas_to_execution(personas, task):
    analysis = AI_pick(personas, lens="problem framing")
    design = AI_pick(personas, lens="architecture")
    review = AI_pick(personas, lens="adversarial or failure detection")
    safety = AI_pick(personas, lens="risk or policy")
    synth = AI_pick(personas, lens="integration and conclusion")
    return analysis, design, review, safety, synth
```

## Practical Guidance

- analysis personas should expand the problem space
- design personas should produce candidate structures
- review personas should try to break the design
- safety personas should identify guardrails and escalation boundaries
- synthesis personas should compress the result into an executable next step

## Subagent Mapping

If subagents are explicitly allowed:

- assign one bounded workstream per persona
- avoid overlapping write scopes
- keep one persona or the main agent as final synthesizer

If subagents are not allowed:

- run the personas as internal review lenses
- still keep outputs separated before synthesis
