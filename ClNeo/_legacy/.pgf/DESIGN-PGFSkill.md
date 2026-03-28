# PGF Skill System — Self-Analysis Design Document
# 목적: PGF 스킬 전체를 PGF로 표기하여 최적화 분석 기반 제공
# 생성일: 2026-03-12

---

## Gantree

```
PGFSkill // PGF 스킬 시스템 전체 (분석중) @v:2.0
    SkillEntrypoint // SKILL.md — 라우터 + 전체 명세 허브 (분석중) [630줄]
        ModeRouter // 7개 모드 파싱 및 분기 (완료)
            DesignMode // Gantree + PPR 설계 산출 (완료) @dep:DesignKnowledge
            PlanMode // DESIGN → WORKPLAN 변환 (완료) @dep:DesignMode
            ExecuteMode // WORKPLAN 노드 순차 실행 (완료) @dep:PlanMode
            FullCycleMode // design→plan→execute→verify 연속 실행 (완료)
            LoopMode // Stop Hook 기반 자동 순회 (완료) @dep:LoopEngine
            DiscoverMode // A3IE 7단계 파이프라인 실행 (완료) @dep:DiscoveryEngine
            CreateMode // 자율 창조 사이클 5-Phase (완료) @dep:DiscoverMode,DesignMode
        ContextLoadStrategy // 모드별 참조 문서 선택적 로드 (완료)
        ExecutionProcess // Step 1~7 통합 프로세스 PPR (완료)
        BundleSkillIntegration // /batch, /simplify, /compact 연동 (완료)
        ChecklistSystem // 설계/실행 검증 체크리스트 (완료)
    DesignKnowledge // 설계 단계 지식 베이스 (분석중)
        GantreeReference // Gantree 노드 문법 정본 (완료) [213줄]
            NodeSyntax // 노드명 // 설명 (상태) [@v:] [@dep:] [#태그] (완료)
            StateCodes // 5종 상태: 완료/진행중/설계중/보류/분해 (완료)
            IndentRules // 4칸 공백, 5레벨 제한, 코드블럭 필수 (완료)
            AtomizationCriteria // 15분 룰 + 7개 판단 기준 (완료)
            ParallelBlock // [parallel]/[/parallel] 블록 문법 (완료)
            DependencyNotation // @dep: 의존성 + → 데이터 흐름 (완료)
        PPRReference // PPR 문법 정본 (완료) [361줄]
            AIPrefix // AI_ 접두사 — 4대 인지 범주 (완료)
            PipelineNotation // → 연산자 파이프라인 (완료)
            ParallelExecution // [parallel] 동시 인지 실행 (완료)
            ConvergenceLoop // AI 자체 출력 반복 개선 패턴 (완료)
            FailureStrategy // AI Redesign Authority + 공개 인터페이스 유지 (완료)
            AcceptanceCriteria // 수락 기준 내장 가이드 (완료)
            DataTypes // Python 타입 힌트 기반 표기 (완료)
            FlowControl // if/for/try — Python 그대로 (완료)
            FunctionDef // Gantree 노드의 PPR def 블록 형식 (완료)
        PGFFormat // .md 파일 형식 명세 (완료) [129줄]
            DesignPGFStructure // ## Gantree + ## PPR 섹션 구조 (완료)
            WorkplanPGFStructure // ## POLICY + ## Execution Tree 구조 (완료)
            StatusJsonSchema // project/nodes/summary 필드 (완료)
            StateTransition // 설계중→진행중→완료/보류 전이 규칙 (완료) @dep:WorkplanReference
        Examples // 실전 예시 (완료)
            APIServiceExample // REST API Gantree+PPR 예시 (완료) [77줄]
            ContentGenExample // 콘텐츠 생성 + Convergence Loop 예시 (완료) [125줄]
    ExecutionEngine // 실행 단계 엔진 (분석중)
        WorkplanReference // WORKPLAN 변환/실행 명세 (완료) [265줄]
            DesignToWorkplan // DESIGN→WORKPLAN 변환 규칙 6개 (완료)
            PolicyBlock // POLICY 블록 필드 + 템플릿 3종 (완료)
            NodeStateTransition // 상태 전이 정본 + 갱신 프로토콜 (완료)
            LoopAlgorithm // select_next_node() + run_loop() PPR (완료)
            ErrorRecovery // 세션 중단 재개, 상태 손상, 수동 편집 후 재개 (완료)
        LoopEngine // Stop Hook 기반 자동 실행 엔진 (분석중) (분해)
    DiscoveryEngine // A3IE + 페르소나 발견 엔진 (분석중) (분해)
    ProtocolVision // 미래 확장 비전 (보류) [113줄]
        PGFMCP // MCP 도구에 PPR 타입/실패전략 적용 (보류)
        PGFA2A // 에이전트 서브트리 위임 프로토콜 (보류)
        OrgAdoption // 조직 도입 패턴 — 역할별 읽기/쓰기 범위 (보류)
```

### (분해) LoopEngine — Stop Hook 기반 자동 실행 엔진

```
LoopEngine // Stop Hook 루프 엔진 (분석중) [4 scripts + 1 spec]
    LoopReference // 루프 실행 명세 (완료) [172줄]
        StopHookProtocol // stdin/stdout JSON 형식 (완료)
        NodeSelectionAlgorithm // 진행중 우선 → 설계중+deps 해소 (완료)
        PromptComposition // 매 iteration 동적 프롬프트 구성 (완료)
        SessionIsolation // session_id 비교로 세션 격리 (완료)
        TerminationConditions // 4종 종료 조건 (완료)
        ErrorRecoveryLoop // 노드 실패 retry, 상태 파일 손상 (완료)
    InitScript // init-loop.ps1 — 루프 초기화 (완료) [157줄]
        WorkplanValidation // WORKPLAN/DESIGN 존재 확인 (완료)
        DuplicateGuard // 기존 루프 중복 방지 (완료)
        PolicyParsing // WORKPLAN에서 POLICY 블록 regex 추출 (완료)
        StateFileCreation // pgf-loop-state.json 생성 (완료)
        HookRegistration // hooks.json에 stop-hook.ps1 등록 (완료)
    StopHookScript // stop-hook.ps1 — 세션 종료 시 다음 노드 주입 (완료) [152줄]
        StateLoading // pgf-loop-state.json + status.json 로드 (완료)
        SessionValidation // session_id 불일치 시 exit (완료)
        NextNodeSelection // select-next-node.ps1 호출 (완료) @dep:NodeSelector
        PPRExtraction // extract-ppr.ps1 호출 (완료) @dep:PPRExtractor
        ProgressCalculation // 완료/전체 노드 수 계산 (완료)
        PromptInjection // block decision + systemMessage 반환 (완료)
    NodeSelector // select-next-node.ps1 — 다음 노드 선택 (완료) [116줄]
        WorkplanParsing // 정규식 노드 파싱 + 마커줄 스킵 (완료)
        DependencyResolution // @dep: 추출 + 완료 여부 확인 (완료)
        PriorityLogic // 진행중 우선 → 설계중 deps 해소 → 트리 순서 (완료)
    PPRExtractor // extract-ppr.ps1 — PPR def 블록 추출 (완료) [103줄]
        HeaderSearch // ### [PPR] NodeName 헤더 검색 (완료)
        PatternSearch // def snake_name( 패턴 직접 검색 (완료)
        CamelToSnake // CamelCase→snake_case 변환 (완료)
```

### (분해) DiscoveryEngine — A3IE + 페르소나 발견 엔진

```
DiscoveryEngine // A3IE 7단계 × 8 페르소나 멀티에이전트 (분석중)
    DiscoveryReference // 실행 명세 정본 (완료) [351줄]
        PipelineSpec // 7단계 Task Prompt + 입출력 정의 (완료)
            Step1_NewsCollection // 21개 도메인 뉴스 수집 (완료)
            Step2_TrendAnalysis // 4관점 트렌드 분석 (완료)
            Step3_InsightExtraction // 10개 교차 도메인 인사이트 (완료)
            Step4_IdeaGeneration // 3개 × 8 = 24개 아이디어 (완료)
            Step5_TopSelection // 상위 3개 선택 (완료)
            Step6_FinalSelection // 최종 1개 선정 + 수렴 판정 (완료)
            Step7_UserVerification // 사용자 검증 또는 자동 선택 (완료)
        ExecutionProtocol // 초기화, 에이전트 병렬 실행, 결과 통합 (완료)
            PersonaInjectionTemplate // 페르소나 주입 프롬프트 형식 (완료)
            AgentParallelExecution // 8 Agent 동시 발행 (sonnet 모델) (완료)
            ResultAggregation // 원본 무편집 보존 + 통합 .md 저장 (완료)
        AutoSelectProtocol // create 모드 자동 아이디어 선택 (완료)
            VoteCounting // 8개 페르소나 투표 집계 (완료)
            TieBreaking // novelty × impact 가중 점수 (완료)
        ContextManagement // STEP 4 이후 요약 전달, /compact 금지 (완료)
        ErrorRecovery // Agent 실패, 세션 끊김, WebSearch 불가 (완료)
        ArchiveStrategy // YYYY-MM-DD 날짜별 보관 (완료)
    PersonaData // personas.json — 8개 페르소나 프로필 (완료) [115줄]
        DiversityAxes // cognitive_style(4) × domain_lens(6) × time_horizon(2) (완료)
        PersonaProfiles // system_prompt + search_keywords + evaluation_bias (완료)
        DomainList // 21개 도메인 목록 (완료)
    OutputStructure // .pgf/discovery/ 산출물 디렉토리 (완료)
        StepOutputFiles // news.md ~ final_idea.md (완료)
        ArchiveDirectory // archive/YYYY-MM-DD/ (완료)
```

---

## PPR

### [PPR] ModeRouter

```python
def route_mode(command: str) -> ExecutionResult:
    """SKILL.md 프론트매터 argument-hint에서 모드 파싱 후 분기"""

    # 파싱 규칙: command[0] = 모드, command[1:] = 프로젝트명/대상
    mode, target = parse_pgf_command(command)

    # 모드별 참조 문서 로드 (ContextLoadStrategy)
    context_map = {
        "design":     ["pgf-format.md", "gantree-reference.md", "reference.md"],
        "plan":       ["pgf-format.md", "workplan-reference.md"],
        "execute":    ["pgf-format.md", "workplan-reference.md"],
        "full-cycle": ["pgf-format.md", "gantree-reference.md", "reference.md", "workplan-reference.md"],
        "loop":       ["pgf-format.md", "workplan-reference.md", "loop/loop-reference.md"],
        "discover":   ["discovery/discovery-reference.md"],  # personas.json은 내부 로드
        "create":     ["discovery/discovery-reference.md", "pgf-format.md", "gantree-reference.md",
                       "reference.md", "workplan-reference.md"],
    }

    for doc in context_map[mode]:
        Read(f"${{CLAUDE_SKILL_DIR}}/{doc}")

    # 모드 실행
    match mode:
        case "design":     return design_gantree(target)
        case "plan":       return convert_to_workplan(target)
        case "execute":    return execute_workplan(target)
        case "full-cycle": return full_cycle(target)
        case "loop":       return loop_control(target)  # start/cancel/status
        case "discover":   return discovery_engine_run(target)
        case "create":     return creation_cycle(target)
```

### [PPR] ContextLoadStrategy

```python
def context_load_strategy(mode: str) -> list[str]:
    """모드별 선택적 문서 로드 — 컨텍스트 경제성 확보

    설계 원칙:
    - SKILL.md(630줄)는 항상 로드 (스킬 트리거 시 자동)
    - 나머지 문서는 모드에 따라 필요한 것만 로드
    - 총 3,079줄 중 모드당 평균 700~1,200줄만 로드

    현재 문제점:
    - SKILL.md 자체가 630줄로 과대 (허브+명세+프로세스+체크리스트 혼합)
    - design 모드 시 reference.md(361줄) + gantree-reference.md(213줄) 전체 로드
    - create 모드 시 5개 문서 로드 → 컨텍스트 부담 최대
    """

    # 로드 비용 분석 (줄 수)
    load_cost = {
        "design":     630 + 129 + 213 + 361,            # = 1,333줄
        "plan":       630 + 129 + 265,                    # = 1,024줄
        "execute":    630 + 129 + 265,                    # = 1,024줄
        "full-cycle": 630 + 129 + 213 + 361 + 265,       # = 1,598줄
        "loop":       630 + 129 + 265 + 172,              # = 1,196줄
        "discover":   630 + 351,                           # = 981줄
        "create":     630 + 351 + 129 + 213 + 361 + 265,  # = 1,949줄 ← 최대
    }
    return load_cost
```

### [PPR] LoopEngineFlow

```python
def loop_engine_flow(command: str) -> None:
    """PGF-Loop 실행 흐름 — 4개 PS1 스크립트 협업

    실행 체인:
    /pgf loop start
        → init-loop.ps1 (157줄)
            → pgf-loop-state.json 생성
            → hooks.json에 stop-hook.ps1 등록
        → AI가 첫 노드 실행

    세션 종료 시 (자동)
        → stop-hook.ps1 (152줄) [hooks.json에 의해 트리거]
            → select-next-node.ps1 (116줄) 호출
                → WORKPLAN-{Name}.md + status.json 파싱
                → 다음 노드 반환
            → extract-ppr.ps1 (103줄) 호출
                → DESIGN-{Name}.md에서 해당 노드 PPR def 추출
            → 프롬프트 구성
            → {"decision": "block", "systemMessage": prompt} 반환
        → Claude Code가 새 세션에서 프롬프트 실행
        → 반복...

    종료 조건:
    1. 모든 노드 terminal (완료/보류)
    2. max_iterations 도달
    3. 사용자 /pgf loop cancel
    4. 상태 파일 삭제됨

    스크립트 간 데이터 흐름:
    init-loop.ps1 → pgf-loop-state.json → stop-hook.ps1
    stop-hook.ps1 → select-next-node.ps1 (WORKPLAN + status.json → 노드명)
    stop-hook.ps1 → extract-ppr.ps1 (DESIGN-{Name}.md + 노드명 → PPR 텍스트)
    """
    pass
```

### [PPR] DiscoveryEngineFlow

```python
def discovery_engine_flow() -> None:
    """Discovery Engine 실행 흐름 — 7단계 × 8 페르소나

    personas.json → 8 Agent 병렬 발행 (sonnet)
        ↓
    STEP 1 (news.md): 뉴스 수집 — 입력 없음, 21개 도메인
        → 8개 결과 통합 → .pgf/discovery/news.md
        ↓
    STEP 2 (industry_trend.md): 트렌드 분석 — 입력: news.md
        → 8개 결과 통합 → .pgf/discovery/industry_trend.md
        ↓
    STEP 3 (insight.md): 인사이트 도출 — 입력: industry_trend.md
        → 8개 결과 통합 → .pgf/discovery/insight.md
        ↓
    STEP 4 (system_design.md): 아이디어 생성 — 입력: insight.md (요약 가능)
        → 8×3 = 24개 아이디어 → .pgf/discovery/system_design.md
        ↓
    STEP 5 (candidate_idea.md): 상위 3 선택 — 입력: system_design.md
        → 8개 결과 통합 → .pgf/discovery/candidate_idea.md
        ↓
    STEP 6 (final_idea.md): 최종 1 선정 — 입력: candidate_idea.md
        → 수렴 판정 (CONVERGED/DIVERGED)
        ↓
    STEP 7a (discover 모드): 사용자 검증 → 선택/재실행/아카이브
    STEP 7b (create 모드): auto_select_idea() → Phase 2 자동 전환

    컨텍스트 관리:
    - STEP 1~3: 이전 단계 전문 전달
    - STEP 4+: 이전 단계 결과 과도 시 핵심 요약 전달
    - 산출물 파일에는 항상 원본 전문 보존
    """
    pass
```

---

## 분석 소견

### 1. 구조적 강점

| 강점 | 근거 |
|------|------|
| **선택적 로드 설계** | 3,079줄 전체 중 모드당 700~1,200줄만 로드 — 컨텍스트 경제성 |
| **명확한 책임 분리** | 설계(Gantree+PPR) / 변환(WORKPLAN) / 실행(Loop) / 발견(Discovery) |
| **실행 가능한 스크립트** | loop/ 4개 PS1이 Stop Hook 메커니즘을 실제 구현 |
| **데이터-로직 분리** | personas.json(데이터) ↔ discovery-reference.md(로직) 분리 |
| **점진적 확장** | 7개 모드가 독립적으로 추가/수정 가능 |

### 2. 구조적 약점

| 약점 | 영향 | 위치 |
|------|------|------|
| **SKILL.md 과대** | 630줄 — 라우터+명세+프로세스+체크리스트 혼합. 항상 전체 로드되어 컨텍스트 낭비 | SkillEntrypoint |
| **create 모드 컨텍스트 폭발** | 6개 문서 로드 = 1,949줄. 5-Phase 실행 중 컨텍스트 압박 | CreateMode |
| **참조 문서 중복 내용** | PPR 핵심 요약이 SKILL.md와 reference.md에 이중 기술 | SkillEntrypoint ↔ PPRReference |
| **Skills 2.0 미활용** | context:fork, allowed-tools, model, custom agents, !command 미적용 | 전체 |
| **protocol-reference.md 고립** | 113줄 비전 문서 — 다른 파일과 참조 관계 없음. 로드 조건도 불명확 | ProtocolVision |
| **에러 복구 분산** | workplan-reference.md §5, loop-reference.md §9, discovery-reference.md §8에 각각 독립 정의 | 3곳 |
| **검증(verify) 명세 부재** | full-cycle Step 4 verify가 SKILL.md PPR에만 존재. 별도 참조 문서 없음 | ExecutionProcess |

### 3. 최적화 우선순위

```
[P0] SKILL.md 분리 — 630줄 → 라우터(~150줄) + 공통 명세 분리
[P1] Skills 2.0 적용 — context:fork, model, allowed-tools 프론트매터 활용
[P2] create 모드 컨텍스트 최적화 — Phase별 필요 문서만 동적 로드
[P3] 중복 제거 — SKILL.md 내 PPR/Gantree 요약 → reference 참조로 대체
[P4] verify 명세 독립 — verify-reference.md 분리 또는 workplan-reference.md에 통합
[P5] 에러 복구 통합 — 공통 에러 복구 패턴을 한 곳에 정의
```
