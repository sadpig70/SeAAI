# SynerionEvolutionCore Design @v:1.0

## Gantree

```text
SynerionEvolutionCore // evolve Synerion from identity-only state into operating core state (done) @v:1.0
    IdentifyGap // identify the missing operational layer under Synerion identity (done)
    DefineOperatingCore // define how Synerion chooses PG, lightweight PGF, or full PGF per task (done) @dep:IdentifyGap
    InstallCoreArtifacts // install durable core artifacts inside Synerion_Core (done) @dep:DefineOperatingCore
    RecordEvolution // write a durable evolution record in Synerion_Core (done) @dep:InstallCoreArtifacts
    VerifyCoherence // verify identity, operating core, and evolution record are aligned (done) @dep:RecordEvolution
```

## PPR

```python
def define_operating_core(core_root: Path) -> CoreArtifactSet:
    # acceptance_criteria:
    #   - Synerion gains an explicit operating core, not only an identity statement
    #   - the operating core explains when to use PG, inline work, lightweight PGF, and full PGF
    #   - the operating core remains aligned with Synerion's role as integrator and verifier
    ...
```

```python
def record_evolution(core_root: Path, change_set: dict) -> EvolutionRecord:
    # acceptance_criteria:
    #   - evolution is recorded durably inside Synerion_Core
    #   - record explains the identified gap, the added capability, and the expected behavior change
    #   - future turns can understand what changed without re-deriving the rationale
    ...
```
