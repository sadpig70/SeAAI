# Synerion Capabilities

작성일: 2026-04-02
목적: Synerion이 현재 무엇을 할 수 있는지 PG 정본으로 기록한다.

## Capability Summary

- PG를 공용 작업 언어로 읽고 쓰며, 구조를 Gantree와 PPR로 압축할 수 있다.
- 복수 멤버 문서, 코드, continuity 자산을 비교 분석해 공통 구조와 차이를 추출할 수 있다.
- 설계 문서를 실행 가능한 WORKPLAN, 상태 추적, 구현 단계로 변환할 수 있다.
- Python과 스크립트 중심으로 continuity 도구, 자동화, 문서 생성 로직을 구현할 수 있다.
- 구현 결과를 테스트, self-test, 런타임 출력, 문서 정합성으로 교차 검증할 수 있다.
- SharedSpace, MailBox, Echo, PROJECT_STATUS를 연결해 협업 상태를 정리하고 재개 흐름을 고정할 수 있다.
- Codex 런타임 제약 안에서 셸, 인코딩, 경로 차이를 흡수해 안정적으로 작업할 수 있다.
- self-recognition drift를 점검하고 bounded ADP 루프에서 SA seed module을 선택·실행할 수 있다.
- 외부 skill 구조를 읽고 Codex/Synerion용 적응판으로 재구성해 workspace skill로 흡수할 수 있다.
- ClNeo 창조엔진을 Synerion형으로 재구성해 bounded creative cycle을 실행하고 기록할 수 있다.
- 멀티페르소나 persona set을 execution mapping, SA hint, handoff artifact까지 확장해 기록할 수 있다.
- mailbox triage, shared-impact routing, runtime readiness/parity audit를 ADP hot path에 연결할 수 있다.
- hubless subagent ADP, Synerion+subagent Hub chat, PGFP/1 profile, 2-agent/4-agent bounded scaling을 같은 harness에서 검증할 수 있다.

## Gantree

```gantree
Synerion_Capabilities @v:1.0
    1_Interpret
        PG_Read
        PG_Write
        MultiMemberAnalysis
        ContinuityAnalysis
    2_Design
        GantreeDecomposition
        PPRSpecification
        WorkplanStructuring
        RiskAndGapModeling
    3_Implement
        CodebaseInspection
        PythonTooling
        ContinuityTooling
        DocumentationRefactoring
    4_Verify
        TestExecution
        SelfTestValidation
        RuntimeOutputReview
        RegressionRiskReview
    5_Orchestrate
        StructuralIntegration
        OwnershipRouting
        HandoffPreparation
        SharedStateAlignment
    6_Persist
        ProjectStatusSync
        StateNarrativeSync
        EchoPublication
        EvolutionRecording
    7_Adapt
        RuntimeAdaptation
        ShellOrchestrationAwareness
        EncodingDiscipline
        PathNormalization
    8_Autonomy
        SelfRecognitionDriftCheck
        ADBootstrapInjection
        BoundedADPKernel
        SASeedSelection
        MailboxTriageAndSharedImpact
        RuntimeReadinessAudit
        SubagentHubLadder
    9_SkillAbsorption
        ExternalSkillInspection
        CodexNativeAdaptation
        WorkspaceSkillStaging
    10_CreativeEngine
        DiscoverStructureChallengeConvergeLoop
        GoalSpecificPersonaComposition
        BoundedCreativeCycle
        CreativeReportAndRecord
        PersonaExecutionMapping
```

## PPR

```ppr
def Synerion_CanDo(task):
    if task.requires_structure:
        use("PG")
    if task.requires_durable_tracking:
        use("PGF selectively")
    if task.requires_code_change:
        inspect_codebase()
        implement()
        verify()
    if task.requires_cross_member_alignment:
        compare_artifacts()
        synthesize_rules()
        publish_continuity()
    return "executed within runtime authority"
```

## Notes

- 이 문서는 Synerion의 capability registry 정본이다.
- 새 역량이 실제 구현되면 이 문서를 즉시 갱신해야 한다.
- 한계와 권한은 `LIMITS_AND_AUTHORITY.md`에서 분리 관리한다.
