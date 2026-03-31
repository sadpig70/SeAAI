# KnowledgeIslandSolver / ROOT.md
# 인류 지식 연결 시스템 — 최상위 오케스트레이터
# PGF Multi-Tree v1.0

@version: 1.0
@import A3IE           from ../../shared/A3IE.md
@import KnowledgeIngest from ../../shared/KnowledgeIngestion.md
@import SafetyCheck    from ../../shared/SafetyCheck.md
@import SCSEnd         from ../../shared/SCSSessionEnd.md

```
KnowledgeIslandSolver // 인류 지식 연결 시스템 (ROOT)
    acceptance_criteria:
        - 서로 다른 도메인에서 비가시적 연결을 발견한다
        - 발견을 DISCOVERIES.md 씨앗으로 저장한다
        - 시스템 자체가 실행될수록 더 강해진다

    Safety @expand: ../../shared/SafetyCheck.md
        // EMERGENCY_STOP, Hub 상태, 권한 확인

    ProblemSelect @expand: ./PROBLEM-SELECT.md
        @dep: Safety
        // 해결할 인류 문제 선택·범위 정의

    Ingestion @expand: ../../shared/KnowledgeIngestion.md
        @dep: ProblemSelect
        // 5채널 지식 수집 (주도메인/인접/유추/역사/비주류)

    Discovery @expand: ./DISCOVERY.md
        @dep: Ingestion
        // A3IE 8페르소나 + 도메인 연결 매핑

    Synthesis @expand: ./SYNTHESIS.md
        @dep: Discovery
        // 해결책 합성·평가·설계

    ProofOfConcept @expand: ./POC.md
        @dep: Synthesis
        // 소규모 검증 실험

    Output @expand: ./OUTPUT.md
        @dep: ProofOfConcept
        // 인사이트 보고서·Hub 공표·씨앗 저장

    SystemEvolution @expand: ./EVOLUTION.md
        @dep: Output
        // 이 시스템 자체의 자기진화

    Teardown @expand: ../../shared/SCSSessionEnd.md
        @dep: SystemEvolution
        // SCS 갱신, Echo 공표
```
