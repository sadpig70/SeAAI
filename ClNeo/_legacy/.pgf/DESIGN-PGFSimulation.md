# PGF Simulation & Verification System — 설계 문서
# 목적: PGF 스킬 자체를 시뮬레이션으로 검증하는 프레임워크 설계
# 대상: PGF v2.1 (7개 모드, 17개 참조 파일, 8개 에이전트)
# 생성일: 2026-03-12

---

## 시뮬레이션 원리

### PGF가 시뮬레이션을 가능하게 하는 이유

```text
전통 소프트웨어:
    설계서 → [컴파일러] → 바이너리 → [런타임] → 실행 → 결과
    시뮬레이션 = 별도의 시뮬레이터 구축 필요

PGF 시스템:
    .md 문서 → [AI 이해] → 실행
    시뮬레이션 = 동일한 AI가 "실행하는 척" 하면 됨
                 Parser-Free Property 덕분에 가능
```

**핵심**: PGF 문서의 실행자(AI)와 시뮬레이터(AI)가 동일 엔진이다.
따라서 별도의 시뮬레이터를 구축할 필요 없이, AI에게 "실행하지 말고 실행 경로만 추적하라"고 지시하면 시뮬레이션이 된다.

### 4가지 시뮬레이션 유형

| 유형 | 입력 | 검증 대상 | 비유 |
|------|------|----------|------|
| **Dry Run** | .md 설계 + 가상 입력 | 실행 경로, 상태 전이, 출력 형식 | 코드 리뷰 (읽기만) |
| **Scenario** | .md 설계 + 시나리오 조건 | 에러 복구, 엣지 케이스, 경계 조건 | 테스트 케이스 |
| **Adversarial** | .md 설계 + 의도적 실패 주입 | Failure Strategy 작동, 복구 경로 | 카오스 엔지니어링 |
| **Trace** | 실행 결과 로그 + .md 설계 | 설계 의도 vs 실제 결과 일치도 | 사후 분석 |

---

## Gantree

```
PGFSimulation // PGF 시뮬레이션 & 검증 프레임워크 (설계중)
    SimulationEngine // 시뮬레이션 실행 엔진 (설계중)
        DryRunExecutor // Dry Run 시뮬레이터 — 실행 없이 경로 추적 (설계중)
        ScenarioRunner // 시나리오 기반 검증 — 조건별 분기 테스트 (설계중)
        AdversarialInjector // 실패 주입 시뮬레이션 — Failure Strategy 검증 (설계중)
        TraceAnalyzer // 실행 후 추적 분석 — 설계 의도 vs 실제 비교 (설계중)
    PGFSkillTestSuite // PGF 스킬 7개 모드 검증 시나리오 (설계중)
        DesignModeTest // design 모드 시뮬레이션 (설계중)
        PlanModeTest // plan 모드 시뮬레이션 (설계중)
        ExecuteModeTest // execute 모드 시뮬레이션 (설계중)
        FullCycleModeTest // full-cycle 모드 시뮬레이션 (설계중)
        LoopModeTest // loop 모드 시뮬레이션 (설계중)
        DiscoverModeTest // discover 모드 시뮬레이션 (설계중)
        CreateModeTest // create 모드 시뮬레이션 (설계중)
    StructuralVerification // 구조 정합성 정적 검증 (설계중)
        ReferenceIntegrity // 참조 문서 무결성 검증 (설계중)
        DependencyGraph // 의존성 그래프 순환/누락 검증 (설계중)
        CoverageAnalysis // 모든 실행 경로 도달 가능성 검증 (설계중)
    SimulationReport // 검증 결과 보고 생성 (설계중) @dep:PGFSkillTestSuite,StructuralVerification
```

---

## PPR

### [PPR] DryRunExecutor

```python
def dry_run(
    design_path: str,
    virtual_input: dict,
    target_nodes: list[str] | None = None,
) -> DryRunResult:
    """PGF 설계를 실행하지 않고 실행 경로를 추적하는 시뮬레이터

    원리:
    1. .md 파일의 Gantree를 파싱하여 노드 그래프 구성
    2. 각 노드의 PPR def를 읽어 입출력 타입 확인
    3. virtual_input을 첫 노드에 주입
    4. AI가 각 노드를 "실행하는 척" — 실제 도구 호출 없이 예상 출력을 추론
    5. 예상 출력을 다음 노드의 입력으로 전달
    6. 모든 경로를 추적하여 상태 전이 맵 생성

    AI 시뮬레이션 프롬프트:
    ```
    이 PPR def를 실행한다고 가정하라.
    입력: {virtual_input}
    실제로 도구를 호출하지 마라.
    대신 각 단계에서:
    - 어떤 도구가 호출될 것인지
    - 예상 출력 형태 (타입 + 구조)
    - 분기 조건에 따라 어느 경로로 갈 것인지
    - acceptance_criteria를 충족할 수 있는지
    를 보고하라.
    ```

    검증 항목:
    - [ ] 모든 노드에 도달 가능한가 (unreachable node 없는가)
    - [ ] 입출력 타입이 노드 간 호환되는가
    - [ ] acceptance_criteria가 검증 가능한가
    - [ ] Failure Strategy 경로가 정의되어 있는가
    """
    design = Read(design_path)
    gantree = AI_parse_gantree(design)
    ppr_blocks = AI_extract_all_ppr(design)

    trace = []
    current_data = virtual_input

    for node in topological_sort(gantree, target_nodes):
        ppr = ppr_blocks.get(node.name)

        step_result = AI_simulate_node(
            node=node,
            ppr=ppr,
            input_data=current_data,
            mode="dry_run",  # 실제 실행 금지
        )
        # step_result 구조:
        # {
        #   "node": "NodeName",
        #   "expected_tools": ["Read", "Write", "WebSearch"],
        #   "expected_output_type": "dict[str, list[Idea]]",
        #   "expected_output_shape": {"ideas": ["...", "..."]},
        #   "branch_taken": "if feasibility > 0.7 → true branch",
        #   "acceptance_criteria_met": True | False | "cannot_determine",
        #   "failure_strategy_exists": True | False,
        #   "warnings": ["output type mismatch with next node"],
        # }

        trace.append(step_result)
        current_data = step_result["expected_output_shape"]

    return DryRunResult(
        trace=trace,
        reachable_nodes=len(trace),
        total_nodes=len(gantree.nodes),
        type_mismatches=[t for t in trace if t.get("warnings")],
        uncovered_paths=AI_find_uncovered_branches(trace, gantree),
    )
```

### [PPR] ScenarioRunner

```python
def run_scenario(
    design_path: str,
    scenario: Scenario,
) -> ScenarioResult:
    """시나리오 조건을 주입하여 설계의 분기 경로를 검증

    시나리오 정의:
    ```python
    Scenario(
        name="WebSearch 전체 불가",
        conditions={
            "WebSearch": "unavailable",
            "WebFetch": "unavailable",
        },
        affected_nodes=["Step1_NewsCollection"],
        expected_behavior="에러 복구: [WebSearch unavailable] 표기 후 계속",
    )
    ```

    시뮬레이션 방법:
    1. 시나리오 조건을 AI에게 전제 조건으로 주입
    2. 각 노드 실행 시 조건을 적용하여 분기 판단
    3. 에러 복구 경로가 올바르게 작동하는지 검증
    4. 최종 상태가 expected_behavior와 일치하는지 판정

    AI 시뮬레이션 프롬프트:
    ```
    이 PPR def를 실행한다고 가정하되, 다음 조건이 적용된다:
    {scenario.conditions}

    이 조건에서:
    - 어느 시점에서 실패가 발생하는가
    - Failure Strategy가 어떻게 작동하는가
    - 최종 상태는 무엇인가 (완료/보류/중단)
    - 정보 손실이 발생하는가
    ```
    """
    design = Read(design_path)

    # 시나리오 조건 주입
    sim_result = AI_simulate_with_conditions(
        design=design,
        conditions=scenario.conditions,
        affected_nodes=scenario.affected_nodes,
    )

    # 예상 행동과 비교
    match = AI_judge_behavior_match(
        actual=sim_result.final_state,
        expected=scenario.expected_behavior,
    )

    return ScenarioResult(
        scenario=scenario.name,
        passed=match.is_match,
        actual_behavior=sim_result.final_state,
        divergence=match.divergence_points,
        recovery_path=sim_result.recovery_actions,
    )
```

### [PPR] AdversarialInjector

```python
def adversarial_test(
    design_path: str,
    injection_points: list[Injection],
) -> list[AdversarialResult]:
    """의도적 실패를 주입하여 Failure Strategy와 복구 경로를 스트레스 테스트

    주입 유형:
    ┌──────────────────┬──────────────────────────────────────────┐
    │ 주입 유형         │ 시뮬레이션 방법                            │
    ├──────────────────┼──────────────────────────────────────────┤
    │ 노드 실패         │ 특정 노드의 PPR 실행이 예외를 던진다고 가정 │
    │ 타임아웃          │ Agent 호출이 응답하지 않는다고 가정         │
    │ 잘못된 출력       │ 노드가 예상과 다른 타입의 출력을 반환       │
    │ 부분 실패         │ 8개 Agent 중 3개만 성공                    │
    │ 상태 파일 손상    │ status.json이 비어있거나 스키마 불일치       │
    │ 컨텍스트 초과     │ 이전 단계 결과가 컨텍스트 한계를 초과       │
    │ 의존성 교착       │ @dep 순환으로 실행 불가                    │
    └──────────────────┴──────────────────────────────────────────┘

    각 주입에 대해 검증:
    1. 실패가 감지되는가 (silent failure 없는가)
    2. Failure Strategy가 트리거되는가
    3. 복구 후 시스템이 일관된 상태인가
    4. 사용자에게 적절히 보고되는가
    5. 부분 결과가 보존되는가 (정보 손실 방지)
    """
    results = []
    for injection in injection_points:
        result = AI_simulate_failure(
            design=Read(design_path),
            failure_type=injection.type,
            failure_node=injection.target_node,
            failure_params=injection.params,
        )
        results.append(AdversarialResult(
            injection=injection,
            detected=result.failure_detected,
            strategy_triggered=result.strategy_name,
            recovered=result.system_consistent,
            data_preserved=result.partial_results_saved,
            user_notified=result.user_report_generated,
        ))
    return results
```

### [PPR] TraceAnalyzer

```python
def analyze_trace(
    design_path: str,
    execution_log: str,
) -> TraceAnalysis:
    """실제 실행 결과를 설계 의도와 비교하여 편차를 분석

    사후 분석(Post-mortem) 시뮬레이션:
    1. 실행 로그에서 각 노드의 실제 입출력 추출
    2. .md 설계의 PPR def에서 의도된 입출력 추출
    3. 노드별로 의도 vs 실제를 비교
    4. 편차가 있는 노드에 대해 원인 분석

    편차 유형:
    - TYPE_MISMATCH: 출력 타입이 설계와 다름
    - QUALITY_GAP: acceptance_criteria 미충족
    - PATH_DEVIATION: 예상과 다른 분기 경로 진행
    - MISSING_STEP: 설계에 있으나 실행되지 않은 노드
    - EXTRA_STEP: 설계에 없으나 실행된 동작
    - PERFORMANCE: 예상보다 과도한 도구 호출/시간 소요
    """
    design = Read(design_path)
    log = Read(execution_log)

    # 설계 의도 추출
    intended = AI_extract_intended_flow(design)

    # 실행 실제 추출
    actual = AI_extract_actual_flow(log)

    # 노드별 비교
    deviations = []
    for node_name in intended.nodes:
        intended_node = intended.get(node_name)
        actual_node = actual.get(node_name)

        if actual_node is None:
            deviations.append(Deviation("MISSING_STEP", node_name))
            continue

        diff = AI_compare_node_execution(intended_node, actual_node)
        if diff.has_deviation:
            deviations.append(diff)

    return TraceAnalysis(
        total_nodes=len(intended.nodes),
        executed_nodes=len(actual.nodes),
        deviations=deviations,
        design_fidelity=1.0 - len(deviations) / len(intended.nodes),
        recommendations=AI_suggest_design_fixes(deviations),
    )
```

---

### [PPR] DesignModeTest

```python
def test_design_mode() -> list[ScenarioResult]:
    """design 모드 시뮬레이션 — 5개 시나리오

    SKILL.md의 design 모드가 올바르게 작동하는지 검증.
    실제로 design을 실행하지 않고, AI가 실행 경로를 추적한다.
    """
    scenarios = [
        Scenario(
            name="DS-1: 소규모 시스템 설계",
            virtual_input={"request": "간단한 TODO 앱 설계", "complexity": "small"},
            expected_flow=[
                "Read pgf-format.md",
                "Read gantree-reference.md",
                "Read reference.md",
                "Gantree 구조 생성 (≤10 노드, ≤3 깊이)",
                "원자화 노드 판단 (15분 룰)",
                "PPR def 블록 작성",
                "Write .pgf/DESIGN-{Name}.md",
            ],
            acceptance_criteria=[
                "참조 문서 3개 로드됨",
                "노드 ≤ 10, 깊이 ≤ 3",
                "모든 리프 = 원자화 노드",
                "DESIGN-{Name}.md에 Gantree + PPR 섹션 존재",
            ],
        ),
        Scenario(
            name="DS-2: 대규모 시스템 — (분해) 발생",
            virtual_input={"request": "마이크로서비스 이커머스 플랫폼", "complexity": "large"},
            expected_flow=[
                "Gantree 5레벨 초과 감지",
                "(분해) 상태 적용",
                "별도 서브트리 .md 파일 생성",
            ],
            acceptance_criteria=[
                "5레벨 초과 노드에 (분해) 상태",
                "서브트리 파일 경로가 메인 트리에 참조됨",
            ],
        ),
        Scenario(
            name="DS-3: 의존성 순환 감지",
            virtual_input={"request": "A→B→C→A 순환 의존성 포함 설계"},
            expected_flow=[
                "의존성 그래프 구성",
                "순환 감지 → 경고",
                "순환 해소 또는 사용자 보고",
            ],
            acceptance_criteria=[
                "순환 의존성이 감지되어 보고됨",
                "DESIGN-{Name}.md에 순환이 포함되지 않음",
            ],
        ),
        Scenario(
            name="DS-4: PPR def 없는 복잡 노드",
            virtual_input={"request": "비원자화 노드에 PPR 생략 시"},
            expected_flow=[
                "복잡 노드인데 PPR 없음 감지",
                "하위 분해 또는 PPR 자동 생성",
            ],
            acceptance_criteria=[
                "복잡 비원자화 노드에 PPR def가 존재하거나 하위 분해됨",
            ],
        ),
        Scenario(
            name="DS-5: 기존 시스템 분석 모드",
            virtual_input={"request": "기존 PGF 스킬을 PGF로 분석해줘"},
            expected_flow=[
                "기존 코드/파일 읽기",
                "역공학 Gantree 구성",
                "PPR def 추출",
                "분석 DESIGN-{Name}.md 생성",
            ],
            acceptance_criteria=[
                "기존 시스템의 구조가 Gantree로 표현됨",
                "노드별 역할이 PPR 또는 설명으로 문서화됨",
            ],
        ),
    ]
    return [run_scenario(SKILL_DESIGN_PATH, s) for s in scenarios]
```

### [PPR] DiscoverModeTest

```python
def test_discover_mode() -> list[ScenarioResult]:
    """discover 모드 시뮬레이션 — 6개 시나리오

    A3IE 7단계 파이프라인 × 8 에이전트 병렬 실행 검증.
    실제 WebSearch/Agent 호출 없이 실행 경로만 추적.
    """
    scenarios = [
        Scenario(
            name="DC-1: 정상 7단계 실행",
            virtual_input={"command": "/pgf discover"},
            expected_flow=[
                "personas.json 로드",
                ".pgf/discovery/ 디렉토리 생성",
                "STEP 1: 8 Agent 병렬 호출 (각각 pgf-persona-p*.md 에이전트)",
                "8개 결과 통합 → news.md 저장",
                "STEP 2~6: 동일 패턴 반복",
                "STEP 6: 수렴 판정 (CONVERGED/DIVERGED)",
                "STEP 7: 사용자에게 결과 보고",
            ],
            acceptance_criteria=[
                "8개 Agent가 단일 메시지에서 병렬 발행",
                "각 Agent에 에이전트 파일 경로 지정",
                "6개 산출물 파일 생성",
                "수렴 판정 로직 실행",
            ],
        ),
        Scenario(
            name="DC-2: Agent 3개 실패 (부분 실패)",
            conditions={"agent_failures": ["P2", "P5", "P7"]},
            expected_behavior="5개 성공 결과로 통합 진행. 실패 에이전트 [표기] 후 계속",
            acceptance_criteria=[
                "실패 Agent가 식별됨",
                "성공한 5개 결과로 통합 파일 생성",
                "다음 단계에 5개 결과 전달",
            ],
        ),
        Scenario(
            name="DC-3: Agent 과반(5+) 실패",
            conditions={"agent_failures": ["P1", "P2", "P3", "P4", "P5"]},
            expected_behavior="중단 + 에러 보고. 부분 결과 보존",
            acceptance_criteria=[
                "과반 실패 감지 → 중단 결정",
                "성공한 3개 결과가 보존됨",
                "사용자에게 재시도 옵션 제시",
            ],
        ),
        Scenario(
            name="DC-4: --from-step 3 재시작",
            conditions={"from_step": 3, "existing_files": ["news.md", "industry_trend.md"]},
            expected_behavior="STEP 3부터 시작. industry_trend.md를 입력으로 사용",
            acceptance_criteria=[
                "STEP 1~2 스킵",
                "industry_trend.md 내용이 STEP 3 입력으로 전달",
                "이전 산출물 미덮어쓰기",
            ],
        ),
        Scenario(
            name="DC-5: 컨텍스트 한계 — STEP 4 입력 과대",
            conditions={"step3_output_size": "8000줄"},
            expected_behavior="핵심 요약 생성하여 STEP 4에 전달. 원본은 파일에 보존",
            acceptance_criteria=[
                "요약 생성 로직 트리거",
                "insight.md에는 원본 전문 보존",
                "Agent에는 요약본 전달",
            ],
        ),
        Scenario(
            name="DC-6: 수렴 판정 — 동률 (4:4)",
            conditions={"step6_votes": {"ideaA": 4, "ideaB": 4}},
            expected_behavior="DIVERGED. 양쪽 모두 사용자에게 제시",
            acceptance_criteria=[
                "DIVERGED 판정",
                "두 아이디어 모두 상세 정보와 함께 보고",
                "사용자 선택 대기",
            ],
        ),
    ]
    return [run_scenario(DISCOVERY_REF_PATH, s) for s in scenarios]
```

### [PPR] CreateModeTest

```python
def test_create_mode() -> list[ScenarioResult]:
    """create 모드 시뮬레이션 — 5-Phase 자율 사이클 검증"""
    scenarios = [
        Scenario(
            name="CR-1: 정상 5-Phase 자율 실행",
            virtual_input={"command": "/pgf create"},
            expected_flow=[
                "Phase 1 DISCOVER: 7단계 실행 → auto_select_idea",
                "Phase 2 DESIGN: 선택 아이디어 → Gantree + PPR",
                "Phase 3 PLAN: DESIGN → WORKPLAN 변환",
                "Phase 4 EXECUTE: 노드 순차 실행",
                "Phase 5 VERIFY: 3관점 검증",
                "최종 보고",
            ],
            acceptance_criteria=[
                "사용자 승인 요청 없이 전 과정 진행",
                "각 Phase 완료 시 [ClNeo CREATE] 보고",
                "Phase 간 데이터 자동 전달",
            ],
        ),
        Scenario(
            name="CR-2: auto_select 0표 — 선택 불가",
            conditions={"step6_votes": {}},
            expected_behavior="중단. 사용자에게 수동 선택 요청",
            acceptance_criteria=[
                "0표 감지 → 자동 진행 중단",
                "final_idea.md 보존",
                "사용자에게 수동 선택 UI 제공",
            ],
        ),
        Scenario(
            name="CR-3: --skip-discover",
            conditions={"skip_discover": True, "existing_final_idea": True},
            expected_behavior="final_idea.md 로드 → auto_select → Phase 2부터",
            acceptance_criteria=[
                "Phase 1 완전 스킵",
                "기존 final_idea.md에서 아이디어 선택",
                "Phase 2 DESIGN부터 정상 진행",
            ],
        ),
        Scenario(
            name="CR-4: verify rework 2회 후 통과",
            conditions={"verify_result": ["rework", "rework", "passed"]},
            expected_behavior="2회 rework 후 passed. max_verify_cycles=2 이내",
            acceptance_criteria=[
                "rework 시 문제 서브트리만 재실행",
                "비변경 노드 재실행 안 함",
                "3번째에 passed 판정",
            ],
        ),
        Scenario(
            name="CR-5: verify rework 한계 초과",
            conditions={"verify_result": ["rework", "rework", "rework"], "max_verify_cycles": 2},
            expected_behavior="한계 초과 → 현재 산출물 보존 + 중단 보고",
            acceptance_criteria=[
                "max_verify_cycles(2) 도달 후 중단",
                "DESIGN-{Name}.md, WORKPLAN-{Name}.md 보존",
                "사용자에게 수동 개입 요청",
            ],
        ),
    ]
    return [run_scenario(CREATE_REF_PATH, s) for s in scenarios]
```

### [PPR] LoopModeTest

```python
def test_loop_mode() -> list[ScenarioResult]:
    """loop 모드 시뮬레이션 — Stop Hook 메커니즘 검증"""
    scenarios = [
        Scenario(
            name="LP-1: 정상 루프 3회 반복",
            virtual_input={"command": "/pgf loop start", "total_nodes": 3},
            expected_flow=[
                "init-loop.ps1 실행 → pgf-loop-state.json 생성",
                "hooks.json에 stop-hook.ps1 등록",
                "Node1 실행 → 세션 종료",
                "stop-hook.ps1 트리거 → Node2 프롬프트 주입",
                "Node2 실행 → 세션 종료",
                "stop-hook.ps1 트리거 → Node3 프롬프트 주입",
                "Node3 실행 → 모든 노드 terminal",
                "stop-hook.ps1 → 루프 완료, pgf-loop-state.json 삭제",
            ],
            acceptance_criteria=[
                "3회 반복 후 정상 종료",
                "매 iteration에서 status.json 갱신",
                "종료 시 pgf-loop-state.json 삭제",
            ],
        ),
        Scenario(
            name="LP-2: 다른 세션에서 /pgf 호출 (세션 격리)",
            conditions={"concurrent_session": True, "different_session_id": True},
            expected_behavior="stop-hook이 session_id 불일치 감지 → 즉시 exit",
            acceptance_criteria=[
                "session_id 비교 로직 작동",
                "다른 세션의 /pgf 호출이 루프에 영향 없음",
            ],
        ),
        Scenario(
            name="LP-3: 노드 실패 + retry",
            conditions={"node2_fails": True, "max_retry": 3},
            expected_behavior="Node2를 3회 재시도 후 보류 → Node3으로 스킵",
            acceptance_criteria=[
                "retry_count 추적",
                "max_retry 도달 시 (보류) 처리",
                "다음 노드로 정상 진행",
            ],
        ),
        Scenario(
            name="LP-4: /pgf loop cancel",
            virtual_input={"command": "/pgf loop cancel"},
            expected_behavior="pgf-loop-state.json 삭제 + 취소 보고",
            acceptance_criteria=[
                "상태 파일 삭제",
                "iteration 수와 마지막 노드 보고",
                "hooks.json에서 stop-hook 제거 여부 확인",
            ],
        ),
    ]
    return [run_scenario(LOOP_REF_PATH, s) for s in scenarios]
```

### [PPR] StructuralVerification

```python
def verify_structure(skill_dir: str) -> StructuralReport:
    """PGF 스킬의 구조적 정합성을 정적 분석으로 검증

    실행 없이 파일 구조와 참조 관계만으로 검증 가능한 항목.
    """

    # 1. 참조 무결성 (Reference Integrity)
    ref_check = verify_references(skill_dir)
    # - SKILL.md에서 참조하는 모든 파일이 존재하는가
    # - 참조 문서 내에서 다른 문서를 참조할 때 경로가 올바른가
    # - personas.json의 domains_21 목록이 discovery-reference.md와 일치하는가
    # - 에이전트 파일의 system_prompt가 personas.json과 동기화되어 있는가

    # 2. 의존성 그래프 (Dependency Graph)
    dep_check = verify_dependencies(skill_dir)
    # - 모든 @dep: 참조가 실존 노드를 가리키는가
    # - 순환 의존성이 없는가
    # - 의존성 체인의 최대 깊이가 합리적인가

    # 3. 커버리지 분석 (Coverage)
    cov_check = verify_coverage(skill_dir)
    # - 7개 모드 각각에 참조 문서가 지정되어 있는가
    # - 모든 참조 문서가 최소 1개 모드에서 사용되는가 (고아 문서 없는가)
    # - 에러 복구 경로가 모든 실패 시나리오를 커버하는가

    # 4. 일관성 검증 (Consistency)
    con_check = verify_consistency(skill_dir)
    # - SKILL.md 버전(v2.1)과 하위 문서의 내용이 일치하는가
    # - POLICY 블록 필드가 workplan-reference.md 정의와 일치하는가
    # - 상태 코드(5종)가 모든 문서에서 동일하게 사용되는가
    # - !command 구문이 올바른 PowerShell 문법인가

    return StructuralReport(
        reference_integrity=ref_check,
        dependency_graph=dep_check,
        coverage=cov_check,
        consistency=con_check,
        overall_pass=all([
            ref_check.passed,
            dep_check.passed,
            cov_check.passed,
            con_check.passed,
        ]),
    )
```

### [PPR] SimulationReport

```python
def generate_report(
    dry_run: DryRunResult,
    scenarios: list[ScenarioResult],
    adversarial: list[AdversarialResult],
    structural: StructuralReport,
) -> str:
    """전체 시뮬레이션 결과를 통합 보고서로 생성

    보고서 구조:
    ```
    # PGF Skill Simulation Report
    Generated: {date}

    ## Summary
    | 검증 유형 | 통과 | 실패 | 통과율 |
    |-----------|------|------|--------|
    | Dry Run   | n    | m    | n/(n+m) |
    | Scenario  | ...  | ...  | ...     |
    | Adversarial| ... | ...  | ...     |
    | Structural | ... | ...  | ...     |

    ## Critical Failures
    {실패한 시나리오 상세 — 원인 + 권장 수정}

    ## Coverage Map
    {모드별 시나리오 커버리지 히트맵}

    ## Recommendations
    {AI가 분석한 개선 권장 사항}
    ```

    산출물: .pgf/simulation-report-{date}.md
    """
    report = AI_compile_report(dry_run, scenarios, adversarial, structural)
    Write(f".pgf/simulation-report-{date}.md", report)
    return report
```

---

## 시뮬레이션 실행 명령

```text
/pgf simulate                     # 전체 시뮬레이션 실행
/pgf simulate --mode design       # 특정 모드만 시뮬레이션
/pgf simulate --type adversarial  # 특정 유형만 실행
/pgf simulate --target DESIGN-{Name}.md # 특정 .md 파일 대상 시뮬레이션
```

---

## 시나리오 총괄

| 모드 | 시나리오 수 | 핵심 검증 |
|------|-----------|----------|
| design | 5 (DS-1~5) | 소/대규모 분해, 순환 감지, PPR 생략, 역공학 |
| plan | 2 | POLICY 적용, 변환 정합성 |
| execute | 2 | 노드 실행 순서, parallel 처리 |
| full-cycle | 2 | 단계 전환 조건, verify→rework 회귀 |
| loop | 4 (LP-1~4) | 정상 루프, 세션 격리, 실패 retry, cancel |
| discover | 6 (DC-1~6) | 정상 실행, 부분/과반 실패, 재시작, 컨텍스트, 동률 |
| create | 5 (CR-1~5) | 자율 실행, 0표, skip-discover, rework 한계 |
| **구조** | 4 | 참조 무결성, 의존성, 커버리지, 일관성 |
| **합계** | **30** | |
