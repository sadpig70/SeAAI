# PGF Skill Completion Work Plan @v:1.0

> PGF 스킬 미구현 5개 모듈 구현 작업 계획
> 대상: `C:/Users/sadpig70/.claude/skills/pgf/`
> 생성일: 2026-03-13

---

## POLICY

```python
POLICY = {
    "max_retry":           3,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
}
```

---

## 작업 우선순위 근거

| 순위 | 모듈 | 심각도 | 이유 |
|------|------|--------|------|
| 1 | SKILL.md 상태 표시 수정 | HIGH | 매 호출 에러 → 즉시 수정 가능, 5분 |
| 2 | verify 단계 구현 | HIGH | full-cycle/create의 전제 조건 |
| 3 | discovery 아카이브 | MEDIUM | 기존 결과 보호, 단독 구현 가능 |
| 4 | full-cycle 모드 | MEDIUM | verify 의존, design/plan/execute 이미 동작 |
| 5 | design --analyze 모드 | LOW | 편의 기능, 독립적 |

---

## Execution Tree

```
PGFSkillCompletion // PGF 스킬 미구현 모듈 구현 (완료) @v:1.0

    Phase1_QuickFixes // 즉시 수정 가능한 결함 (완료)

        FixStatusDisplay // SKILL.md 인라인 상태 표시 오류 수정 (완료)
            # 작업: SKILL.md의 !`powershell` 인라인 3개 수정
            # 원인: status.json 필드명이 한글('완료')인데 영문('completed')으로 참조
            # 수정 대상: C:/Users/sadpig70/.claude/skills/pgf/SKILL.md:44-48

        FixAgentPath // 에이전트 파일 경로 불일치 수정 (완료)
            # 작업: SKILL.md/discovery-reference.md에서 에이전트 경로 확인
            # 현황: ~/.claude/agents/ 에 파일 없음, 실제 위치는 skills/pgf/agents/
            # discovery-reference.md:66 "${CLAUDE_SKILL_DIR}/agents/" 사용 중 → 정합성 확인

    Phase2_Verify // verify 단계 구현 (완료) @dep:Phase1_QuickFixes

        VerifyReference // verify-reference.md 명세 문서 작성 (완료)
            # 산출물: C:/Users/sadpig70/.claude/skills/pgf/verify-reference.md
            # 내용:
            #   1. 3관점 검증 프로세스 상세 정의
            #      - acceptance_criteria 자동 재확인 알고리즘
            #      - /simplify 연동 프로토콜
            #      - 아키텍처 정합성 검증 기준
            #   2. 검증 결과 판정 (passed / rework / blocked)
            #   3. rework 시 서브트리 재실행 규칙
            #   4. 검증 보고 형식

        VerifyPPR // verify PPR def 블록 작성 (완료) @dep:VerifyReference
            # 산출물: verify-reference.md 내 PPR 섹션
            # PPR 정의:
            #   def verify_project(design_path, workplan_path, policy) -> VerifyResult
            #   def verify_node_acceptance(node, design) -> bool
            #   def verify_code_quality(workplan_path) -> QualityReport
            #   def verify_architecture(design_path, workplan_path) -> ArchReport
            #   def determine_verdict(acceptance, quality, arch) -> VerifyResult

        VerifyIntegration // SKILL.md에 verify 프로세스 통합 (완료) @dep:VerifyPPR
            # 작업:
            #   1. SKILL.md §Step 4 (verify) 상세화
            #   2. 참조 문서 테이블에 verify-reference.md 추가
            #   3. pgf-checklist.md '실행 검증' 섹션 보강

    Phase3_Archive // discovery 아카이브 구현 (완료) @dep:Phase1_QuickFixes

        ArchiveScript // archive-discovery.ps1 스크립트 작성 (완료)
            # 산출물: C:/Users/sadpig70/.claude/skills/pgf/discovery/archive-discovery.ps1
            # 기능:
            #   1. .pgf/discovery/ 의 6개 산출물을 archive/YYYY-MM-DD/ 로 복사
            #   2. 동일 날짜 존재 시 _N 순번 부여
            #   3. 원본은 유지 (다음 실행 시 덮어쓰기 대상)
            # 인수: -DiscoveryDir (기본: .pgf/discovery)

        ArchiveIntegration // discovery-reference.md에 아카이브 호출 통합 (완료) @dep:ArchiveScript
            # 작업:
            #   1. discovery-reference.md §6 아카이브 섹션에 스크립트 호출 명세 추가
            #   2. STEP 7 완료 후 자동 아카이브 트리거 규칙 정의
            #   3. create-reference.md의 archive_discovery() 호출에 스크립트 연결

    Phase4_FullCycle // full-cycle 모드 구현 (완료) @dep:Phase2_Verify

        FullCycleReference // full-cycle 실행 명세 작성 (완료)
            # 산출물: C:/Users/sadpig70/.claude/skills/pgf/fullcycle-reference.md
            # 내용:
            #   1. design→plan→execute→verify 연속 실행 PPR
            #   2. 단계 전환 조건 + 실패 시 동작
            #   3. verify rework 회귀 루프 (max_verify_cycles)
            #   4. 진행 보고 형식
            #   5. 세션 중단/재개 전략

        FullCyclePPR // full-cycle PPR def 블록 작성 (완료) @dep:FullCycleReference
            # 산출물: fullcycle-reference.md 내 PPR 섹션
            # PPR 정의:
            #   def full_cycle(project_name, policy) -> FullCycleResult
            #     Phase 1: AI_design_gantree → DESIGN-{Name}.md
            #     Phase 2: convert_design_to_workplan → WORKPLAN-{Name}.md
            #     Phase 3: execute_all_nodes
            #     Phase 4: verify_project
            #       if rework → 재실행 (max_verify_cycles)

        FullCycleIntegration // SKILL.md에 full-cycle 연동 (완료) @dep:FullCyclePPR
            # 작업:
            #   1. SKILL.md §full-cycle 상세화 (현재 5줄 → 참조 문서 연결)
            #   2. 참조 문서 테이블에 fullcycle-reference.md 추가
            #   3. 규모 감지 전략과 연동 규칙 보강

    Phase5_DesignAnalyze // design --analyze 모드 구현 (완료) @dep:Phase1_QuickFixes

        AnalyzeReference // design --analyze 명세 문서 작성 (완료)
            # 산출물: C:/Users/sadpig70/.claude/skills/pgf/analyze-reference.md
            # 내용:
            #   1. 기존 코드베이스 → PGF 역공학 프로세스
            #      - 디렉토리 구조 스캔 → Gantree 초안 생성
            #      - 코드 읽기 → AI_ 함수 후보 식별
            #      - 의존성 분석 → @dep: 자동 추출
            #   2. 출력: DESIGN-{ProjectName}.md (역공학 결과)
            #   3. 제한사항: 대규모 코드베이스 컨텍스트 관리

        AnalyzePPR // analyze PPR def 블록 작성 (완료) @dep:AnalyzeReference
            # 산출물: analyze-reference.md 내 PPR 섹션
            # PPR 정의:
            #   def analyze_codebase(root_path, project_name) -> DesignPGF
            #     scan_directory_structure → Gantree 초안
            #     AI_identify_modules → 모듈 경계 식별
            #     AI_extract_dependencies → @dep: 그래프
            #     AI_generate_ppr_stubs → PPR def 초안
            #     write_design_pgf → DESIGN-{name}.md

        AnalyzeIntegration // SKILL.md에 analyze 모드 통합 (완료) @dep:AnalyzePPR
            # 작업:
            #   1. SKILL.md design --analyze 행 상세화
            #   2. 참조 문서 테이블에 analyze-reference.md 추가

    Phase6_FinalValidation // 최종 통합 검증 (완료) @dep:Phase2_Verify,Phase3_Archive,Phase4_FullCycle,Phase5_DesignAnalyze

        CrossReferenceCheck // 문서 간 상호 참조 정합성 (완료)
            # 검증 대상:
            #   1. SKILL.md의 참조 문서 테이블 ↔ 실제 파일 존재
            #   2. 모든 참조 문서의 ${CLAUDE_SKILL_DIR} 경로 일관성
            #   3. 에이전트 파일 경로 참조 일관성
            #   4. 모드별 명세 완전성 (7개 모드 전부 참조 문서 보유 확인)

        SkillMDUpdate // SKILL.md 최종 업데이트 (완료) @dep:CrossReferenceCheck
            # 작업:
            #   1. 참조 문서 가이드 테이블에 신규 문서 4개 추가
            #      - verify-reference.md
            #      - fullcycle-reference.md
            #      - analyze-reference.md
            #      - discovery/archive-discovery.ps1
            #   2. 실행 모드 표의 동작 설명 정교화
            #   3. 통합 실행 프로세스 섹션 업데이트

        ChecklistUpdate // pgf-checklist.md 최종 보강 (완료) @dep:CrossReferenceCheck
            # 작업:
            #   1. verify 체크리스트 항목 추가
            #   2. full-cycle 체크리스트 항목 추가
            #   3. archive 체크리스트 항목 추가
```

---

## 의존성 그래프

```
Phase1_QuickFixes (독립)
    ├→ Phase2_Verify
    │      └→ Phase4_FullCycle
    ├→ Phase3_Archive
    └→ Phase5_DesignAnalyze

Phase2 + Phase3 + Phase4 + Phase5 전부 완료
    └→ Phase6_FinalValidation
```

---

## 예상 노드 수: 18개

| Phase | 노드 수 | 비고 |
|-------|---------|------|
| Phase1_QuickFixes | 2 | 즉시 수정 |
| Phase2_Verify | 3 | 핵심 — verify 명세 + PPR + 통합 |
| Phase3_Archive | 2 | 스크립트 + 통합 |
| Phase4_FullCycle | 3 | verify 의존 |
| Phase5_DesignAnalyze | 3 | 독립 가능 |
| Phase6_FinalValidation | 3 | 최종 검증 |
| **합계** | **16 리프 + 2 루트/분류** | |

---

## 실행 전략

- **Phase1**: 단독 즉시 실행 (5~10분)
- **Phase2 + Phase3 + Phase5**: Phase1 완료 후 병렬 진행 가능
  - Phase2와 Phase5는 서로 독립
  - Phase3도 독립
- **Phase4**: Phase2(verify) 완료 대기 후 실행
- **Phase6**: 전체 완료 후 교차 검증

---

## 산출물 목록

| # | 파일 | 유형 | Phase |
|---|------|------|-------|
| 1 | `SKILL.md` | 수정 | 1, 6 |
| 2 | `verify-reference.md` | 신규 | 2 |
| 3 | `pgf-checklist.md` | 수정 | 2, 6 |
| 4 | `discovery/archive-discovery.ps1` | 신규 | 3 |
| 5 | `discovery-reference.md` | 수정 | 3 |
| 6 | `create-reference.md` | 수정 | 3 |
| 7 | `fullcycle-reference.md` | 신규 | 4 |
| 8 | `analyze-reference.md` | 신규 | 5 |
| 9 | `workplan-reference.md` | 수정 (필요 시) | 4 |
