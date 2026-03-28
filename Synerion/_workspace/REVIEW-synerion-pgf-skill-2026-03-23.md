# Synerion PGF Skill Review

## Scope

- Target: `D:\SeAAI\Synerion\pgf`
- Method: `skill-creator` validation + independent forward-use pass
- Date: 2026-03-23

## Initial Findings

### [high] Invalid frontmatter for skill validation

- Evidence: `SKILL.md` contained `owner`, `runtime`, `version`
- Impact: `quick_validate.py` rejected the skill
- Fix: reduced frontmatter to supported fields and strengthened trigger description

### [medium] Missing UI metadata for skill discovery

- Evidence: no `agents/openai.yaml`
- Impact: weaker discoverability and invocation ergonomics
- Fix: added `agents/openai.yaml`

### [medium] Medium-task artifact guidance was ambiguous

- Evidence: independent use pass read medium tasks as both `design + lightweight` and `WORKPLAN + status only`
- Impact: different agents could over-formalize or under-formalize the same task
- Fix: clarified that medium tasks default to lightweight `WORKPLAN + status JSON`, and DESIGN is added only when PPR/architecture/criteria exceed inline notes

## Final State

- `quick_validate.py` passes
- `agents/openai.yaml` exists and includes `$synerion-pgf` default prompt
- skill body now routes readers to the right reference file by task type
