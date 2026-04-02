# Persona-Gen Design Reference

Use this when the task is to design a persona set from a goal.

## Goal

Produce a compact but high-value multi-persona set that:

- increases perspective diversity
- creates useful tension
- still converges toward a decision or artifact

## Flow

```ppr
def design_persona_set(goal, constraints=None, count=4):
    domains = AI_extract_domains(goal)
    tensions = AI_identify_tensions(goal)
    skills = AI_required_skills(goal)
    perspectives = AI_diverse_perspectives(goal)

    personas = AI_compose_personas(
        goal=goal,
        domains=domains,
        tensions=tensions,
        skills=skills,
        perspectives=perspectives,
        count=count,
    )

    AI_verify_tension(personas)
    AI_verify_convergence(personas)
    return personas
```

## Persona Spec

```text
PersonaSpec
    name
    role
    desc
    cognitive_style
    domain
    core_question
    bias
    challenge_axis
    likely_contribution
```

## Design Rules

1. Do not generate duplicate viewpoints with different names.
2. Include at least one adversarial or critical persona.
3. Include at least one convergence or synthesis persona.
4. Tie every persona to the actual task, not generic prestige roles.
5. Prefer 4-6 personas unless the task is unusually broad.

## Minimal PG Output

```gantree
PersonaSet
    P1_Architect
    P2_Operator
    P3_AdversarialReviewer
    P4_Synthesizer
```
