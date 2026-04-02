# DESIGN: Synerion Creative Engine Multipersona Integration

작성일: 2026-04-02
목적: Synerion creative cycle을 persona profile 생성기에서 execution mapping 생성기로 올린다.

## Goal

- persona-gen 스테이징 규격 흡수
- runtime-safe signal policy 적용
- persona set + execution mapping + creative report 동시 생성

## Constraints

- raw mailbox/hub event는 canonical state로 승격하지 않는다.
- creative cycle은 ADP normalized snapshot만 advisory 입력으로 읽는다.
- artifacts는 `_workspace/personas/`와 timestamped report로 남긴다.

## Structure

```gantree
CreativeEngine_Multipersona
    RuntimeSignals
        ManualSections
        BoundedADPSummary
        RegistrySnapshot
        MailboxPendingCount
        SelfRecognitionDrift
    PersonaLayer
        BasePersonas
        DomainPersonas
        BalanceVerification
    ExecutionLayer
        LaneMap
        AssignmentRecords
        SAHints
        HandoffTriggers
    RecordLayer
        PersonaArtifacts
        TimestampedCreativeReport
        ContinuitySync
```

## PPR

```ppr
def install_multipersona_creative_cycle(goal):
    runtime = AI_read_normalized_runtime_snapshot()
    personas = AI_compose_persona_set(goal)
    AI_verify_persona_balance(personas)
    mapping = AI_map_personas_to_execution(personas, runtime)
    report = AI_run_creative_cycle(goal, personas, mapping, runtime)
    AI_record_persona_artifacts(report, mapping)
    AI_sync_continuity()
```
