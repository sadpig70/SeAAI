# PgfSelfReview Design @v:1.0

## Gantree

```text
PgfSelfReview // review and optimize Synerion PGF with PGF itself (in-progress) @v:1.0
    AuditSkill // inspect SKILL.md trigger and mode guidance (designing)
    AuditRefs // inspect reference docs for state-machine and runtime consistency (designing) @dep:AuditSkill
    ValidateSkill // run skill validation and consistency checks (designing) @dep:AuditRefs
    RepairDocs // patch issues found in skill or references (designing) @dep:ValidateSkill
    VerifyLoop // re-run validation and produce review artifact (designing) @dep:RepairDocs
```

## PPR

```python
def audit_refs(pgf_root: Path) -> ReviewFindings:
    # acceptance_criteria:
    #   - contradictions across SKILL, runtime, workplan, and verify docs are identified
    #   - guidance that could cause divergent agent behavior is called out
    ...
```

```python
def repair_docs(findings: ReviewFindings) -> PatchResult:
    # acceptance_criteria:
    #   - fixes preserve PG semantics
    #   - fixes improve Codex execution clarity
    #   - state and review artifacts remain synchronized
    ...
```
