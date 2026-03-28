# SA Evolve Reference

Use this when the task is to improve an SA library, detect gaps, or plan mutation rules.

## Core Idea

`SA` evolves when the library becomes more complete, less redundant, and more fit for actual loop execution.

Think in four mutation types:

- `ADD`
- `IMPROVE`
- `MERGE`
- `REMOVE`

## Evolution Flow

1. Scan the current library and platform folders.
2. Detect:
   - missing phases
   - weak modules
   - duplicate modules
   - modules that no longer fit the agent's role
3. Propose the smallest mutation set that improves coverage.
4. Validate the resulting library structure.
5. Record why the mutation matters.

## What To Look For

- missing `sense_`, `think_`, or `act_` balance
- too many ad hoc `AI_` behaviors that should have been lifted into `SA_`
- modules whose names overlap but whose behavior is not differentiated
- platform modules that really belong in shared common space

## Synerion Bias

For Synerion, prefer evolution that improves:

- conflict detection
- routing and handoff
- shared-impact review
- convergence and escalation logic

Avoid evolving toward domain creation platforms unless the user explicitly wants that.
