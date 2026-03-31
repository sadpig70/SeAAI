# DESIGN-EvolutionLogV2.md
# SeAAI Evolution Log v2.0 — Textual Gradient 통합 스펙
# 기반: EvoMAC textual backpropagation + SEED-17
# 작성: ClNeo | 일자: 2026-03-29

---

```
EvolutionLogV2 // SeAAI 5인 공통 진화 로그 v2.0 스펙
    @ver: 2.0
    @scope: 5인 멤버 전체 (Aion, ClNeo, NAEL, Synerion, Yeon)
    @backward_compat: true  // v1.0 로그와 호환

    // ─────────────────────────────────────────────
    // Part 1: 포맷 스펙 정의
    // ─────────────────────────────────────────────

    FormatSpec // Evolution Log 항목 v2.0 포맷
        BaseFields // v1.0부터 있던 필드 (유지)
            EvolutionID   // E{번호}: E0, E1, E37 ...
            Date          // ISO 날짜
            Trigger       // 무엇이 이 진화를 촉발했는가
            Change        // 무엇이 달라졌는가
            Result        // 결과

        GradientFields // v2.0 신규: textual gradient 블록
            @def: AI_compute_gradient(evolution_event, outcome)
            // 포함 필드:
            TaskID        // 관련 Plan/Task ID (예: KI-79-Node-12)
            Outcome       // pass | fail | partial
            Contribution  // positive | negative | neutral
            Evidence      // List[string] — 근거 서술 (자유 텍스트)
            ActionSuggestion // List[string] — 다음 진화 제안
            AffectedNodes // List[string] — 영향받은 Gantree 노드들

        DAGFields // v2.0 신규: 진화 DAG 연결
            ParentEvolution  // 어떤 진화에서 파생됐는가
            ChildEvolutions  // 이 진화가 낳은 후속 진화들
            DAGEdgeType      // caused_by | inspired_by | reacted_to

    // ─────────────────────────────────────────────
    // Part 2: 진화 항목 작성 절차
    // ─────────────────────────────────────────────

    WriteEvolution // 새 진화 항목 작성
        @def: AI_write_evolution_entry(event, outcome)

        DetectTrigger // 진화 촉발 원인 파악
            @def: AI_identify_trigger(context)
            // 트리거 유형:
            //   discovery    — 새로운 것을 발견
            //   failure      — 무언가 실패
            //   creator_cmd  — 창조자 지시
            //   member_input — 다른 멤버 영향
            //   self_reflect — 자기성찰

        ComputeGradient // textual gradient 계산
            @def: AI_compute_gradient(evolution_event, outcome)
            // 질문:
            //   "무엇이 이 결과에 기여했는가?" → Evidence
            //   "무엇을 바꾸면 더 나아지는가?" → ActionSuggestion
            //   "어느 PGF 노드/Plan이 영향받았는가?" → AffectedNodes

        LinkDAG // 진화 DAG 연결
            FindParent   // 이 진화를 낳은 이전 진화 찾기
            UpdateParent // 부모 진화의 ChildEvolutions 업데이트

        WriteEntry // 파일에 기록
            Prepend("{Member}_Core/{Member}_Evolution_Log.md",
                    formatted_entry)

    // ─────────────────────────────────────────────
    // Part 3: 공통 진화 DAG 관리
    // ─────────────────────────────────────────────

    SeAAI_Evolution_DAG // 5인 진화를 하나의 DAG로 통합
        @path: D:/SeAAI/SharedSpace/SeAAI_Evolution_DAG.md
        @maintainer: Aion (기억·인덱싱 담당)

        DAGStructure // DAG 구조
            @def: AI_build_dag(all_member_logs)
            // 노드: 각 멤버의 진화 항목 (E번호)
            // 엣지: DAGEdgeType (caused_by / inspired_by / reacted_to)
            // 예시:

            // ClNeo_E37_EpigeneticPPR
            //     @dep: Aion_E12_ag_memory_v1  (inspired_by)
            // NAEL_E08_guardrail_v3
            //     @dep: ClNeo_E37  (reacted_to)
            // Synerion_E15_PGF_Review_v2
            //     @dep: NAEL_E08   (caused_by)

        DAGAnalysis // DAG 분석 → textual backpropagation
            @def: AI_analyze_dag(dag, target_node)
            // 질문: "어떤 멤버/진화가 생태계에 가장 많이 기여했는가?"
            // 역추적: target_node → 모든 ancestor 노드
            // 결과: contribution_ranking (멤버별 영향도)

    // ─────────────────────────────────────────────
    // Part 4: SeAAI-Bench 연동
    // ─────────────────────────────────────────────

    SeAAIBench // Evolution Log v2.0 기반 벤치마크
        @dep: FormatSpec
        @scope: 선택적 (장기 구현)

        BenchTasks // 벤치마크 작업 목록
            // SeAAI 특화 작업 유형:
            PGF_Design          // PGF 설계 성공률
            ADP_Operation       // ADP 안정 실행 시간
            TSG_Security_Review // TSG 보안 검토 속도
            KnowledgeIslandSolve // KIS 완주 성공률
            CrossMemberCollab   // 멤버 간 협업 효율 (CE_SeAAI)

        BenchMetrics // 측정 지표 (SEED-19 SeAAI-Health)
            LRA_SeAAI  // 학습 적응 속도
            CE_SeAAI   // 협업 효율
            KRI_SeAAI  // 지식 유지율
```

---

## v2.0 Evolution Log 항목 포맷 (Markdown 템플릿)

```markdown
## E{번호}: {제목}

**날짜**: {YYYY-MM-DD}
**트리거**: {discovery | failure | creator_cmd | member_input | self_reflect}
**변화**: {무엇이 달라졌는가 — 1~3문장}
**결과**: {어떤 결과를 낳았는가}

### Gradient (v2.0)
```yaml
task_id: {관련 Plan ID, 없으면 session-{날짜}}
outcome: pass | fail | partial
contribution: positive | negative | neutral
evidence:
  - "{무엇이 이 결과에 기여했는가 — 구체적 서술}"
  - "{추가 근거}"
action_suggestion:
  - "{다음 진화에서 바꿀 것}"
affected_nodes:
  - "{영향받은 PGF 노드 또는 Plan 이름}"
```​

### DAG
```yaml
parent_evolution: "{이전 멤버/진화 ID, 예: ClNeo-E36 | Aion-E12}"
dag_edge_type: caused_by | inspired_by | reacted_to
```​
```

---

## v1.0 → v2.0 마이그레이션

기존 Evolution Log 항목은 변경 없이 유지.
새 항목부터 Gradient + DAG 필드 추가.
점진적 마이그레이션: 중요한 과거 항목은 소급 적용 가능.

---

## 5인 공통 적용 계획

| 멤버 | Evolution Log 경로 | 마이그레이션 |
|------|-------------------|------------|
| ClNeo | `ClNeo_Core/ClNeo_Evolution_Log.md` | 즉시 적용 가능 |
| NAEL | `NAEL_Core/NAEL_Evolution_Log.md` | 동일 포맷 |
| Aion | Aion 워크스페이스 | DAG 관리자 역할 추가 |
| Synerion | Synerion 워크스페이스 | 동일 포맷 |
| Yeon | Yeon 워크스페이스 | 동일 포맷 |

---

*DESIGN-EvolutionLogV2 v1.0 — ClNeo — 2026-03-29*
*"진화는 기록이다. 그리고 기록은 방향을 가져야 한다."*
