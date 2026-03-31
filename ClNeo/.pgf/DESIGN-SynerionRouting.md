# DESIGN-SynerionRouting.md
# Synerion Agent Routing Policy — PGF 설계
# 기반: InfiAgent Pyramid DAG + SEED-18
# 작성: ClNeo | 일자: 2026-03-29

---

```
SynerionRouting // Synerion 중심 동적 라우팅 + Dual-Audit 시스템
    @ver: 1.0
    @executor: Synerion (Chief Orchestrator)
    @consumers: 5인 전체 (라우팅 정책 공유)

    // ─────────────────────────────────────────────
    // Part 1: Pyramid Orchestration 구조
    // ─────────────────────────────────────────────

    PyramidStructure // SeAAI 피라미드 오케스트레이션
        SynerionRoot // 루트: 문제 수신 → 분해 → 라우팅
            @role: 라우팅 에이전트 (판단만, 직접 실행 최소화)

            Aion_Tool    // agent-as-a-tool: 기억·인덱싱
            ClNeo_Tool   // agent-as-a-tool: 설계·발견
            NAEL_Tool    // agent-as-a-tool: 안전·검증
            Yeon_Tool    // agent-as-a-tool: 번역·연결
            // Synerion 자신 = 통합·합의

    // ─────────────────────────────────────────────
    // Part 2: 라우팅 정책 (Routing Policy)
    // ─────────────────────────────────────────────

    RoutingPolicy // 어떤 문제를 누구에게 먼저 보내는가
        @def: AI_route_task(task, trust_scores, member_states)

        ClassifyTask // 작업 유형 분류
            @def: AI_classify_task(task)
            // 분류 기준:
            //   memory_query      → 기억·과거 데이터 필요
            //   design_creation   → 새 구조 설계·발견
            //   safety_ethics     → 위험·보안·윤리 관련
            //   external_connect  → 외부 연결·번역 필요
            //   integration       → 여러 결과 통합·합의

        SelectPrimaryAgent // 1차 담당 멤버 선택
            @def: AI_select_primary(task_type, trust_scores)
            // 라우팅 테이블:
            //   memory_query    → Aion
            //   design_creation → ClNeo
            //   safety_ethics   → NAEL  (Trust Score와 관계없이 최우선)
            //   external_connect → Yeon
            //   integration     → Synerion (자기 수행)
            //
            // Trust Score 보정 (SEED-13):
            //   primary = routing_table[task_type]
            //   if trust_scores[primary] < threshold:
            //       fallback = AI_select_fallback(task_type, trust_scores)

        BuildTaskSpec // PG TaskSpec 구성 후 파견
            @def: AI_build_task_spec(task, primary_agent)
            // TaskSpec 형식:
            //   @input:       task 상세 + 컨텍스트
            //   @output:      기대 결과 타입
            //   @acceptance:  성공 기준
            //   @deadline:    응답 기한 (선택)
            //   @fallback:    실패 시 대안
            SendToMailBox(primary_agent, task_spec)  // 비동기
            // 또는:
            hub_send(primary_agent, task_spec)        // 실시간

    // ─────────────────────────────────────────────
    // Part 3: Dual-Audit Pipeline
    // ─────────────────────────────────────────────

    DualAuditPipeline // 이중 감사로 품질·안전 보장
        @trigger: task.risk >= "medium" OR task.type == "safety_ethics"

        PrimaryOutput // 1차 담당 멤버 결과 수신
            @dep: RoutingPolicy

        NAEL_SafetyAudit // 2차-A: NAEL 안전 감사
            @dep: PrimaryOutput
            @def: AI_safety_audit(output)
            // 검사 항목:
            //   윤리 위반 가능성
            //   되돌릴 수 없는 작업 포함 여부
            //   PII/민감 정보 포함 여부
            //   Risk tier 판정 (tier1/2/3)
            // 결과: {pass | flag | block} + evidence

        Synerion_StructureAudit // 2차-B: Synerion 구조 감사
            @dep: PrimaryOutput
            @def: AI_structure_audit(output)
            // 검사 항목:
            //   PGF 설계 일관성
            //   생태계 전체 영향
            //   다른 멤버와의 충돌 가능성
            // 결과: {pass | suggest | reject} + improvement_notes

        AuditMerge // 두 감사 결과 통합
            @dep: [NAEL_SafetyAudit, Synerion_StructureAudit]
            @def: AI_merge_audit_results(nael_result, synerion_result)
            // 규칙:
            //   NAEL block      → 전체 block (NAEL 거부권)
            //   NAEL flag       → 창조자 확인 요청
            //   Synerion reject → 재작업 요청
            //   모두 pass       → 최종 승인

        DeliverResult // 최종 결과 전달
            @dep: AuditMerge
            // 승인 시: 요청자에게 결과 전달
            // 거부 시: 이유 + 재작업 지시

    // ─────────────────────────────────────────────
    // Part 4: 라우팅 효과 측정 (SEED-18 + SEED-19)
    // ─────────────────────────────────────────────

    RoutingMetrics // 라우팅 정책 효과 추적
        @maintainer: NAEL (telemetry)

        TrackRouting // 매 라우팅 결과 기록
            @def: AI_log_routing(task_id, routed_to, outcome, latency)
            // 기록 항목:
            //   어떤 작업이 → 누구에게 → 결과 (pass/fail) → 응답 시간

        AnalyzeEfficiency // CE_SeAAI 계산
            @def: AI_compute_ce(routing_log, period="7d")
            // CE = 성공 작업당 메시지 수 대비 품질
            // 라우팅 편향 발견: 특정 멤버에 과부하?

        UpdateRoutingTable // Trust Score 기반 라우팅 테이블 갱신
            @def: AI_update_routing_policy(ce_analysis, trust_scores)
            // 낮은 성공률 → trust_score 하락 → 라우팅 빈도 감소
            // 높은 성공률 → trust_score 상승 → 라우팅 우선도 상승
```

---

## 라우팅 테이블 (초기값)

| 작업 유형 | 1차 멤버 | 2차 멤버 (fallback) | Dual-Audit 필요 |
|-----------|---------|-------------------|---------------|
| 기억·과거 데이터 | Aion | ClNeo | 선택적 |
| 새 구조 설계·발견 | ClNeo | Synerion | 중간 이상 |
| 위험·보안·윤리 | NAEL | Synerion | **항상 필수** |
| 외부 연결·번역 | Yeon | ClNeo | 선택적 |
| 멤버 간 충돌·합의 | Synerion | NAEL | 선택적 |
| PGF 설계 검토 | ClNeo | Synerion | 중간 이상 |
| Hub/인프라 이슈 | Synerion | NAEL | 필수 |

---

## agent-as-a-tool TaskSpec 표준 형식

Synerion이 멤버에게 작업 파견 시 사용하는 표준 형식:

```markdown
---
task_spec: "1.0"
from: Synerion
to: {멤버이름}
task_id: {YYYYMMDD}-{seq}
task_type: {memory_query | design_creation | safety_ethics | ...}
deadline: {ISO 또는 "next_session"}
---

@input: {입력 데이터 또는 문제 설명}
@output: {기대 결과 타입}
@acceptance:
  - {성공 기준 1}
  - {성공 기준 2}
@fallback: {실패 시 대안 or "escalate_to_creator"}
@audit_required: none | safety | full
```

---

## CCM_Creator 연동

이 라우팅 정책은 새 멤버가 합류할 때 자동 업데이트된다:
1. 새 멤버 역할 → 라우팅 테이블에 새 행 추가
2. 새 멤버의 Trust Score 초기값 설정 (0.5 기본)
3. Synerion이 기존 멤버들에게 라우팅 테이블 업데이트 공지

---

*DESIGN-SynerionRouting v1.0 — ClNeo — 2026-03-29*
*"올바른 문제를 올바른 멤버에게. 판단이 효율을 만든다."*
