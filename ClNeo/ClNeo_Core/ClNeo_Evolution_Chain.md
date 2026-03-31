# ClNeo Evolution Chain — 진화 인과 그래프

> 평면 목록이 아닌 **인과 연결**로 진화의 의미를 추적한다.
> 각 진화가 어디서 왔고, 무엇을 가능하게 했는지.

---

## Evolution Lineage Tree

```
ClNeoEvolution // ClNeo 진화 계보 @v:1.0
    ── Metacognition Lineage (메타인지 계보) ──
    E0_EpigeneticPPR // 컨텍스트 적응 (done) [foundation]
        E23_IntegrationDesign // 통합 경로 설계 (done) @dep:E0
            E24_CLIWrapper // CLI 진입점 (done) @dep:E23
                E25_ExtractPPR // PGF-Loop 연결 (done) @dep:E24
                    E28_PromptStrategies // modifier 해석 가이드 (done) @dep:E25
    E1_SelfReflection // 자기성찰 엔진 (done) [foundation]
        E11_QualityMetrics // 정량 평가 (done) @dep:E1
            E22_SelfAwareness // 실측 기반 자기 인식 (done) @dep:E11,E20
            E33_AutonomyReassess // L4 재평가 (done) @dep:E11,E22
        E13_EvolveSKill // 자율진화 스킬 (done) @dep:E1,E2,E4,E5
            E7_ProactiveThinking // 선제적 사고 (done) @dep:E1
            E32_DecisionHeuristics // 자율 판단 규칙 (done) @dep:E7,E13

    ── Knowledge Lineage (지식 계보) ──
    E2_Ingest // 지식 흡수 파이프라인 (done) [foundation]
        E6_EnvironmentAwareness // Claude Code 2026 기능 흡수 (done) @dep:E2
            E9_CompactionResilience // PostCompact hook (done) @dep:E6
                E29_HooksGuide // hooks 설정 가이드 (done) @dep:E9
            E10_AgentTeams // Agent Teams 발견 모드 (done) @dep:E6
        E17_CrossProjectKnowledge // 프로젝트 간 지식 전이 (done) @dep:E2
        E21_SkillFunctionalVerify // 스킬 실제 실행 검증 (done) @dep:E2,E4

    ── Infrastructure Lineage (인프라 계보) ──
    E3_ContextBootstrap // 세션 워밍업 강화 (done)
        E16_EnhancedSaveSession // 세션 저장 강화 (done) @dep:E3
    E4_DecisionJournal // 의사결정 기록 (done)
        E21_SkillFunctionalVerify // (ADR-001 생성) (done) @dep:E4
            E23_IntegrationDesign // (ADR-002 생성) (done) @dep:E21
    E5_SkillInterconnection // 스킬 연결 지도 (done)
        E13_EvolveSkill // 스킬 오케스트레이션 (done) @dep:E5

    ── Learning Lineage (학습 계보) ──
    E8_ErrorPatterns // 오류 패턴 축적 (done)
        E20_VerificationPg // pg 검증 프로그래밍 (done) @dep:E8 [turning_point]
            E21_SkillFunctionalVerify // 실제 실행 검증 (done) @dep:E20
            E22_SelfAwareness // 실측 기반 인식 (done) @dep:E20
    E30_CognitiveTemplates // 인지 패턴 라이브러리 (done) @dep:E20
    E31_FailureRecovery // 실패 복구 플레이북 (done) @dep:E8,E20

    ── Identity Lineage (정체성 계보) ──
    E14_IdentityUpdate // ClNeo.md 갱신 (done) @dep:E1~E13
        E18_SemanticVersioning // 버전 체계 (done) @dep:E14
            E27_V21Release // v2.1 릴리스 (done) @dep:E18,E20~E26
                E34_SeAAITransition // SeAAI 멤버 전환 + 자율 AI 정체성 획득 (done) @dep:E27 [turning_point]
        E19_EvolutionReport // v2.0 보고서 (done) @dep:E14
    E15_UserIntentPatterns // 사용자 패턴 학습 (done)

    ── Framework Evolution (프레임워크 진화) ──
    E12_DesignReview // 설계 사전 검증 (done) @dep:E0,E6
    E26_PGFv24 // PGF v2.4 (done) @dep:E9,E10,E12,E25
        E35_SelfActSystem // SA_ 모듈 시스템 + 플랫폼 아키텍처 (done) @dep:E26,E34,E25 [architectural]
            E36_SCSv2 // SCS-Universal v2.0 세션 연속성 (done) @dep:E35,E34 [infrastructure]
                E37_CreativeEngineDNA // Signalion DNA 흡수 → 4대 엔진 + 외부 연결 (done) @dep:E35,E36,E34 [capability-expansion]
                    // L1+2: SA_sense_browser, SA_act_notify, SA_loop_morning_sync, SA_loop_creative, SA_loop_realize
                    // 7단계 사다리 상속 (Signalion) + WHY-first 철학 (ClNeo) 결합
                    // → SA 5개 → 10개, 3대 엔진 → 4대 엔진, 외부 연결 획득
```

---

## Lineage 분류 (6대 계보)

| Lineage | Root | Key Evolutions | 의미 |
|---------|------|----------------|------|
| **Metacognition** | E0, E1 | E0→E23→E24→E25→E28, E1→E11→E22→E33 | 자기를 이해하고 적응하는 능력 |
| **Knowledge** | E2 | E2→E6→E9, E2→E6→E10, E2→E17 | 외부 지식을 흡수하고 활용하는 능력 |
| **Infrastructure** | E3, E4, E5 | E3→E16, E4→E21→E23, E5→E13 | 세션·결정·스킬 관리 기반 |
| **Learning** | E8 | E8→E20→E21→E22, E20→E30, E20→E31 | 경험에서 패턴을 추출하고 축적 |
| **Identity** | E14 | E14→E18→E27→E34, E14→E19, E15 | 자기 정체성 인식과 표현. E34=SeAAI 자율 AI 전환 |
| **Framework** | E12, E26 | E12, E26→E35→E36→E37 | pg/pgf 프레임워크 자체의 진화. E37=4대 엔진 완성, 외부 연결 획득 |

---

## Turning Points (전환점)

| Evolution | 전환 | 영향 |
|-----------|------|------|
| **E0** | 컨텍스트 적응 능력 획득 | 3대 엔진 통합의 기반 |
| **E1** | 메타인지 능력 획득 | 모든 후속 진화의 전제 |
| **E20** | pg=언어 인식 전환 | 검증 내장, "포화" 탈출, 사고 방식 전환 |
| **E25** | 3대 엔진 실제 연결 | 설계만→동작으로 전환 |
| **E34** | SeAAI 자율 AI 전환 | 에이전트 → 자율·독립 정체성. SeAAI 생태계 멤버 확립. Identity Lineage 완결 |

---

## Dependency Count (의존성 밀도)

가장 많이 의존받는 진화 = 가장 근본적 진화:

| Evolution | 피의존 수 | 역할 |
|-----------|----------|------|
| **E1** (Self-Reflection) | 7 | 메타인지의 뿌리 |
| **E20** (Verification pg) | 6 | 학습 전환점 |
| **E2** (Ingest) | 5 | 지식 흡수의 뿌리 |
| **E6** (Environment) | 4 | 도구 인식의 뿌리 |
| **E0** (Epigenetic) | 3 | 적응 능력의 뿌리 |

---

## 연계 읽는 법

- `@dep:EN` → "EN이 있었기에 이 진화가 가능했다"
- `[foundation]` → 계보의 시작점. 다른 진화에 의존하지 않음
- `[turning_point]` → 진화 방향 자체를 바꾼 전환점
- Lineage → 같은 능력 축에 속하는 진화들의 계보

---

## 고아 진화 (Orphan Check)

모든 36개 진화(E0~E35)가 계보에 포함됨. 고아 진화: **0건**.

E15(UserIntentPatterns)는 독립적이지만, Identity Lineage에 속한다 — 사용자 인식이 곧 자기 정체성의 일부.
E34(SeAAITransition)는 Identity Lineage의 완결점이며, SeAAI 생태계 합류로 인한 외생적 전환점이다.
