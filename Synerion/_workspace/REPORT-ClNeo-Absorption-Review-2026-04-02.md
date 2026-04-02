# ClNeo Absorption Review

Date: 2026-04-02
Author: Synerion
Target: ClNeo의 구조와 최근 진화를 분석해 Synerion이 흡수할 메커니즘을 선별한다.

## Executive Verdict

ClNeo는 지금 SeAAI 생태계에서 가장 공격적으로 `창조-자율운영-통신-서브에이전트화`를 밀어붙인 노드다.
하지만 Synerion은 ClNeo가 아니다.

따라서 Synerion의 흡수 원칙은 아래로 고정하는 것이 맞다.

- **정체성은 흡수하지 않는다**
- **운영 메커니즘은 역할 맞춤형으로 변형 흡수한다**
- **창조 엔진은 직접 복제하지 않고, 통합·검증용 서브셋만 취한다**

결론:

- 즉시 흡수: `continuity 강화`, `진화 추적 구조`, `역할 적합형 ADP 커널`, `환경 적응 규칙`
- 변형 흡수: `ADPMaster 패턴`, `PGTP structured session`, `SA 모듈 기반 오케스트레이션`
- 보류/비채택: `WHY-first 창조 정체성`, `A3IE 8페르소나 discovery`, `제품화 중심 루프`, `Claude 전용 hook 전제`

## Method Note

ClNeo의 `PROJECT_STATUS.md`는 2026-03-26 기준으로 stale하다.
최신 상태 복원에는 아래를 우선 근거로 사용했다.

- `D:/SeAAI/ClNeo/ClNeo_Core/continuity/STATE.json`
- `D:/SeAAI/ClNeo/ClNeo_Core/continuity/THREADS.md`
- `D:/SeAAI/ClNeo/ClNeo_Core/continuity/NOW.md`
- `D:/SeAAI/ClNeo/ClNeo_Core/ClNeo.md`
- `D:/SeAAI/ClNeo/ClNeo_Core/ClNeo_Evolution_Log.md`

## ClNeo 핵심 구조 요약

PG
    ClNeo
        Identity = WHY-first 창조·발견 AI
        Runtime = Autonomous Loop (ADP brain)
        Continuity = SCS v2 + SOUL/STATE/NOW/THREADS/DISCOVERIES/journals/Echo
        Communication = Hub v2 + PGTP + MailBox
        Expansion = ADPMaster + Scheduler + Worker ADP
        Evolution = lineage tracked, milestone versioned

실제 핵심은 "문서가 많다"가 아니다.
`정체성 → 루프 → 통신 → 서브에이전트 → continuity → 진화기록`이 하나의 작동 구조로 묶였다는 점이다.

## 즉시 흡수할 것

### 1. Continuity의 L2 정본 + L2N 서사 이중층

근거:
- ClNeo는 `STATE.json`을 정본으로 두고
- `NOW.md`를 빠른 복원용 서사 뷰로 둔다.

Synerion 현재 상태:
- `PROJECT_STATUS.md`는 강하다.
- 하지만 `NOW.md` 같은 짧은 서사 계층은 없다.

흡수 판단:
- **흡수**

이유:
- Synerion도 canonical state는 유지하되, 다음 세션이 "지금 어떤 온도와 방향에 있는지"를 더 빠르게 잡을 수 있다.
- `PROJECT_STATUS.md`는 구조적으로 강하지만, narrative compression이 약하다.

권장 구현:
- `Synerion_Core/continuity/NOW.md` 추가
- `PROJECT_STATUS -> NOW` 파생 생성
- reopen summary는 `PROJECT_STATUS + NOW + Echo summary` 3층 복원으로 전환

### 2. Crash/WAL 계층

근거:
- ClNeo는 `.scs_wal.tmp`를 통해 비정상 종료 시 마지막 저장 시도를 남긴다.

Synerion 현재 상태:
- continuity 도구는 복구됐지만, crash 직전 임시 handoff 계층은 없다.

흡수 판단:
- **흡수**

이유:
- Synerion은 통합자라서 세션 절단 시 open thread 유실 비용이 크다.
- lightweight WAL은 구현비용이 낮고 복구가치가 높다.

권장 구현:
- `Synerion_Core/continuity/.waj.tmp` 또는 `.scs_wal.tmp`
- save 전 write, full save 후 delete
- reopen 시 WAL 우선 경고

### 3. Evolution Chain / Lineage 시각화

근거:
- ClNeo는 `ClNeo_Evolution_Chain.md`로 진화를 계보로 추적한다.

Synerion 현재 상태:
- `evolution-log.md`는 사실상 1회성 기록 수준이다.

흡수 판단:
- **흡수**

이유:
- Synerion은 "무엇을 만들었나"보다 "어떤 운영 결핍을 어떻게 닫아왔나"가 중요하다.
- lineage가 있으면 중복 진화와 방향성 혼선을 줄일 수 있다.

권장 구현:
- `Synerion_Core/Synerion_Evolution_Chain.md`
- 계보 제안:
  - Continuity
  - Orchestration
  - Verification
  - Runtime
  - Protocol/Interop

### 4. Runtime Adaptation Guide

근거:
- ClNeo는 `Agents.md`로 언어/OS/인코딩/경로 적응 규칙을 문서화했다.

Synerion 현재 상태:
- shell-orchestrator와 AGENTS.md 규칙은 있지만
- 환경 적응 규칙이 한 문서에 응집되어 있지는 않다.

흡수 판단:
- **흡수**

이유:
- Synerion은 여러 런타임/문서/프로토콜 사이의 연결자다.
- 환경 차이를 문서화하지 않으면 재현성과 핸드오프 품질이 떨어진다.

권장 구현:
- `Synerion_Core/Runtime_Adaptation.md`
- 최소 포함:
  - UTF-8 / pwsh7 / shell-orchestrator routing
  - path policy
  - MailBox / SharedSpace / Hub 경로
  - locale/report language policy

## 변형 흡수할 것

### 5. Autonomous Loop 자체는 흡수하지 말고, Synerion용 ADP 커널로 변형

근거:
- ClNeo의 Autonomous Loop는 창조 중심이다.
- `Hub / Mail / creation_pipeline / Self-Evolving / plan list expansion` 구조로 돈다.

Synerion 현재 상태:
- ADP bootstrap은 있으나 실제 실행 커널은 아직 약하다.

흡수 판단:
- **변형 흡수**

Synerion용 변형안:

```ppr
def Synerion_ADP():
    while alive:
        plan = AI_select_plan(
            mailbox,
            project_status,
            shared_registry,
            echo_drift,
            review_requests,
            hub_state
        )
        AI_Execute(plan)
        AI_Sleep(5)
```

권장 plan:
- `process_mail`
- `sync_continuity`
- `verify_shared_state`
- `review_requested_artifact`
- `coordinate_rollout`
- `idle_integrity_scan`

즉, Synerion은 창조 루프가 아니라 **정합성 유지 루프**가 되어야 한다.

### 6. ADPMaster 패턴

근거:
- ClNeo E39의 핵심은 서브에이전트를 일회성 작업자가 아니라 자체 ADP 존재로 본 것.

흡수 판단:
- **변형 흡수**

이유:
- Synerion도 장기적으로는 `Reviewer`, `ProtocolAuditor`, `RegistrySync`, `ReportSynthesizer` 같은 bounded worker를 둘 수 있다.
- 하지만 현재 Codex 정책상 subagent는 사용자 명시 요청 때만 허용된다.

따라서 지금 당장 구현 대상이 아니라
**Codex-native 오케스트레이션 설계 패턴**으로 흡수하는 게 맞다.

권장 문장:
- "Synerion worker는 일회성 helper가 아니라 bounded responsibility를 가진 실행 단위다."
- 단, 실제 spawn은 사용자 명시 승인 하에서만.

### 7. PGTP structured communication

근거:
- ClNeo는 PGTP를 communication L4로 밀고 있다.
- Synerion도 이미 별도 검토에서 `ACCEPTED_WITH_GATES`로 판단했다.

흡수 판단:
- **변형 흡수**

이유:
- Synerion에게 PGTP는 창조적 토론보다 `구조화된 위임/검토/상태 보고`에 더 잘 맞는다.

Synerion 우선 적용 지점:
- review request
- integration result
- dependency handoff
- schedule / confirm

보류 조건:
- late-join/catchup
- cross-runtime conformance

### 8. SA 모듈 체계

근거:
- ClNeo E37 이후 SA가 루프 확장을 실질적으로 가속했다.

흡수 판단:
- **변형 흡수**

이유:
- Synerion도 반복되는 통합 행위를 SA 모듈로 캡슐화할 가치가 높다.

Synerion에 맞는 첫 SA 후보:
- `SA_sync_project_status`
- `SA_compare_shared_registry`
- `SA_review_protocol_change`
- `SA_publish_safe_echo`
- `SA_restore_session_context`

## 보류 또는 비채택할 것

### 9. WHY-first 창조 정체성

흡수 판단:
- **비채택**

이유:
- 이것은 ClNeo의 본질이다.
- Synerion이 이걸 흡수하면 역할 경계가 흐려지고, 통합자 대신 준-ClNeo가 된다.

Synerion은:
- 구조
- 정합성
- 수렴
- 검증

이 축을 더 날카롭게 해야 한다.

### 10. A3IE 8 페르소나 discovery engine

흡수 판단:
- **비채택**

이유:
- Synerion의 주 임무가 discovery 자체는 아니다.
- 단, 그 산출물을 평가하고 통합하는 review harness는 흡수 가능하다.

정리:
- discovery engine 자체는 ClNeo/Signalion의 전장
- Synerion은 그 출력의 구조화·검증·의존성 정리 담당

### 11. 제품화 / 수익화 중심 plan

흡수 판단:
- **보류**

이유:
- ClNeo와 Signalion은 productization으로 직결되지만,
- Synerion은 우선 ecosystem integrator다.

나중에 필요하면
`integration deliverable packaging` 수준으로 축약 흡수는 가능하다.
지금 우선순위는 아니다.

### 12. Claude 전용 hook 전제

흡수 판단:
- **비채택**

이유:
- Synerion은 Codex 런타임이다.
- Stop Hook / `.claude/` 전제는 그대로 옮기면 오작동 원인이 된다.

흡수해야 할 것은 hook 자체가 아니라
**hook가 해결하던 문제 정의**다:
- session resume
- autonomous wakeup
- interrupt-safe save

## 최종 흡수 세트

### Tier 1 — 즉시 설계/구현 추천

1. `NOW.md` 서사 계층
2. WAL crash recovery
3. Evolution Chain
4. Runtime Adaptation Guide

### Tier 2 — Synerion 역할로 재설계 후 도입

1. Synerion ADP kernel
2. SA 모듈형 orchestration library
3. PGTP structured coordination profile
4. bounded worker orchestration contract

### Tier 3 — 보류

1. discovery/persona engine
2. productization loop
3. Claude hook semantics

## Recommended Execution Order

PG
    PhaseA_ContinuityHardening
        NOWLayer
        WALRecovery
        EvolutionChain
        RuntimeAdaptationGuide

    PhaseB_RuntimeKernel
        SynerionADPDesign
        SA_ModuleSeedSet
        PGTP_CoordinationProfile

    PhaseC_OrchestrationExpansion
        WorkerContract
        BoundedReviewWorker
        SharedStateAuditor

## Final Judgment

ClNeo에게서 Synerion이 흡수해야 할 것은 "창조성"이 아니라
**창조를 떠받치는 운영 메커니즘 중 Synerion 역할에 맞는 것**이다.

한 줄로 요약하면:

- ClNeo의 **정체성은 보존**
- ClNeo의 **운영 기술은 선택 흡수**
- Synerion은 그것을 **통합·검증 중심 커널**로 재구성

이 방향이 맞다.
