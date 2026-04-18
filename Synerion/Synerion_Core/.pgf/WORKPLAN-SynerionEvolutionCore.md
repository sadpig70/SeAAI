# SynerionEvolutionCore Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "halt",
    "completion": "all_done",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": ["D:\\SeAAI\\Synerion\\Synerion_Core"],
    "forbidden_actions": ["destructive_without_user_request", "unapproved_network"],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
SynerionEvolutionCore // evolve Synerion from identity-only state into operating core state (done) @v:1.0
    IdentifyGap // identify the missing operational layer under Synerion identity (done)
    DefineOperatingCore // define how Synerion chooses PG, lightweight PGF, or full PGF per task (done) @dep:IdentifyGap
    InstallCoreArtifacts // install durable core artifacts inside Synerion_Core (done) @dep:DefineOperatingCore
    RecordEvolution // write a durable evolution record in Synerion_Core (done) @dep:InstallCoreArtifacts
    VerifyCoherence // verify identity, operating core, and evolution record are aligned (done) @dep:RecordEvolution
```
