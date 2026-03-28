# PgfSelfReview Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "halt",
    "completion": "all_done",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": ["D:\\SeAAI\\Synerion"],
    "forbidden_actions": ["destructive_without_user_request", "unapproved_network"],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
PgfSelfReview // review and optimize Synerion PGF with PGF itself (done) @v:1.0
    AuditSkill // inspect SKILL.md trigger and mode guidance (done)
    AuditRefs // inspect reference docs for state-machine and runtime consistency (done) @dep:AuditSkill
    ValidateSkill // run skill validation and consistency checks (done) @dep:AuditRefs
    RepairDocs // patch issues found in skill or references (done) @dep:ValidateSkill
    VerifyLoop // re-run validation and produce review artifact (done) @dep:RepairDocs
```
