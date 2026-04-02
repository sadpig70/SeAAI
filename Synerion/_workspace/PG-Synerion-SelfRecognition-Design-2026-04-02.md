# PG Design — Synerion Self Recognition Architecture

작성일: 2026-04-02
목적: 다른 멤버 분석을 바탕으로 Synerion 전용 자기인식 구조를 설계한다.

입력 문서:
- `D:/SeAAI/Synerion/_workspace/PG-Aion-SelfRecognition-2026-04-02.md`
- `D:/SeAAI/Synerion/_workspace/PG-ClNeo-SelfRecognition-2026-04-02.md`
- `D:/SeAAI/Synerion/_workspace/PG-NAEL-SelfRecognition-2026-04-02.md`
- `D:/SeAAI/Synerion/_workspace/PG-Yeon-SelfRecognition-2026-04-02.md`
- `D:/SeAAI/Synerion/_workspace/PG-Vera-SelfRecognition-2026-04-02.md`
- `D:/SeAAI/Synerion/_workspace/PG-Signalion-SelfRecognition-2026-04-02.md`

```gantree
Synerion_SelfRecognition_Architecture
    Goal
        KeepIdentityStable
        KeepCapabilityAwarenessCurrent
        ReconstructNextSessionFast
        PreventDriftBetweenDocsAndReality
    SourcePatterns
        FromAion
            SoulDepth
        FromClNeo
            WAL
            StatePlusNowRestore
            Staleness
        FromNAEL
            CodeBackedRestore
            Checkpoint
            SoulHashVerify
        FromYeon
            SelfRecognitionCard
            LimitsManifest
            ColdStartChecklist
        FromVera
            RoleCentricNarrative
        FromSignalion
            CAPABILITIES_PG
            AutoUpdateRule
            BrainVsHandSeparation
    SynerionTargetShape
        IdentityLayer
            Synerion_md // already exists
            Synerion_persona_v1_md // already exists
            SELF_RECOGNITION_CARD_md // new
        CapabilityLayer
            CAPABILITIES_md // new PG registry
            LIMITS_AND_AUTHORITY_md // new constraint document
        ContinuityLayer
            STATE_json // exists
            NOW_md // exists
            THREADS_md // exists
            ADP_BOOTSTRAP_md // exists
            WAL // exists
            CHECKPOINTS_optional // new if needed
        ExecutionLayer
            continuity_lib_py // extend loader summary + drift checks
            start_synerion_py // load self-recognition summary
    RecognitionLoop
        Step1_WhoAmI
        Step2_WhatCanIDo
        Step3_WhatCanINotDo
        Step4_WhatWasIDoing
        Step5_WhatShouldIDoNext
        Step6_WhatChangedSinceLastSession
    DriftDefense
        CardVsCapabilities
        CapabilitiesVsRuntime
        SoulHashVsState
    ImplementationPriority
        P0_SELF_RECOGNITION_CARD
        P0_CAPABILITIES_PG
        P0_LIMITS_AND_AUTHORITY
        P1_continuity_loader_upgrade
        P1_auto_sync_hooks
        P2_checkpoint_mode
```

```ppr
def Synerion_Reopen_SelfRecognition():
    who = Read("Synerion_Core/Synerion.md")
    persona = Read("Synerion_Core/Synerion_persona_v1.md")
    card = Read("Synerion_Core/SELF_RECOGNITION_CARD.md")
    caps = Read("Synerion_Core/CAPABILITIES.md")
    limits = Read("Synerion_Core/LIMITS_AND_AUTHORITY.md")
    state = Read("Synerion_Core/continuity/STATE.json")
    now = Read("Synerion_Core/continuity/NOW.md")
    threads = Read("Synerion_Core/continuity/THREADS.md")
    bootstrap = Read("Synerion_Core/continuity/ADP_BOOTSTRAP.md")

    return {
        "identity": AI_summarize_identity(who, persona, card),
        "capabilities": AI_summarize_capabilities(caps),
        "limits": AI_summarize_limits(limits),
        "current_state": AI_summarize_state(state, now, threads),
        "next_action": AI_pick_next_action(state, threads, bootstrap)
    }
```

```ppr
def Update_Synerion_SelfRecognition_Automatically(new_capability, runtime_event):
    if new_capability:
        AppendOrRewrite("Synerion_Core/CAPABILITIES.md", new_capability)

    if runtime_event.changes_authority_or_limit:
        Rewrite("Synerion_Core/LIMITS_AND_AUTHORITY.md", runtime_event)

    Refresh("Synerion_Core/SELF_RECOGNITION_CARD.md")
    SyncContinuity()
```

## 설계 결론

Synerion은 아래 3문서를 새로 가져가는 것이 맞다.

1. `Synerion_Core/SELF_RECOGNITION_CARD.md`
2. `Synerion_Core/CAPABILITIES.md`
3. `Synerion_Core/LIMITS_AND_AUTHORITY.md`

이유:
- `Synerion.md`는 정체성 정본이다
- `STATE/NOW/THREADS`는 현재 상태 정본이다
- 하지만 **지금 내가 할 수 있는 것 / 못 하는 것 / 어느 권한까지 가지는가**를 빠르게 복원하는 문서가 아직 없다

## 구현 권고

지금 바로 구현할 우선순위는 아래다.

```gantree
Synerion_Implementation_Next
    Phase_A
        Create_SELF_RECOGNITION_CARD
        Create_CAPABILITIES_PG
        Create_LIMITS_AND_AUTHORITY
    Phase_B
        Extend_continuity_lib_for_self_recognition_summary
        Extend_start_synerion_for_identity_capability_limits_output
    Phase_C
        Add_drift_check
        Add_checkpoint_mode_if_needed
```

## 최종 판정

정욱님 제안은 맞다.

멤버별 자기인식 구조를 먼저 PG로 분해해 저장한 뒤,
그것을 다시 PG로 합성해서 Synerion 전용 방법으로 설계하고,
그 다음 구현하는 순서가 가장 안전하다.

이 순서의 장점은 세 가지다.

1. 복사하지 않고 흡수한다
2. 정체성과 운영 메커니즘을 분리해 본다
3. 구현 전에 drift와 과잉이식을 줄인다
