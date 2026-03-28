# Create Reference

5-Phase 자율 창조 — discover → design → plan → execute → verify.

## 개요

사용자 승인 없이 완전 자율 실행. "창조해" 명령으로 시작.

## 5-Phase 파이프라인

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  DISCOVER   │ ──→ │   DESIGN    │ ──→ │    PLAN     │
│ 아이디어 발견 │     │  구조 설계   │     │ 작업 계획    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   VERIFY    │ ←── │   EXECUTE   │ ←── │  (loop)     │
│   검증      │     │   실행      │     │  순환 실행   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Phase 상세

### Phase 1: DISCOVER

**입력**: 주제/문제/목표 (자연어)
**출력**: `final_ideas.md` (상위 3-5개 아이디어)

```python
def phase_discover(topic):
    """A3IE 7단계 실행"""
    # Stage 1-7: discovery-reference.md 참조
    result = run_discovery_pipeline(topic)
    
    # 자동 선택
    selected = auto_select_idea(result.ideas)
    
    save(".pgf/discovery/final_ideas.md", selected)
    return selected
```

### Phase 2: DESIGN

**입력**: 선택된 아이디어
**출력**: `DESIGN-{Name}.md`

```python
def phase_design(idea):
    """Gantree 구조 설계"""
    # Top-Down BFS 분해
    tree = AI_decompose(idea, max_depth=5)
    
    # 원자 노드까지 분해
    atomic_tree = decompose_to_atomic(tree)
    
    # PPR 상세화
    detailed = add_ppr_details(atomic_tree)
    
    save(f".pgf/DESIGN-{idea.name}.md", detailed)
    return detailed
```

### Phase 3: PLAN

**입력**: DESIGN
**출력**: `WORKPLAN-{Name}.md` + `status-{Name}.json`

```python
def phase_plan(design):
    """WORKPLAN 변환"""
    workplan = convert_design_to_workplan(design)
    
    # POLICY 설정
    workplan.policy = {
        "max_iterations": 10,
        "auto_verify": True,
        "stop_on_error": False
    }
    
    # 초기 status 생성
    status = initialize_status(workplan)
    
    save(f".pgf/WORKPLAN-{design.name}.md", workplan)
    save(f".pgf/status-{design.name}.json", status)
    
    return workplan, status
```

### Phase 4: EXECUTE

**입력**: WORKPLAN + status
**출력**: 구현물 + 갱신된 status

```python
def phase_execute(workplan, status):
    """순차 실행 또는 루프 실행"""
    # 방법 A: 순차 실행
    for node in workplan.nodes:
        if status.nodes[node.name].status == "designing":
            result = execute_node(node)
            update_status(status, node, result)
            
            if not result.success and POLICY.stop_on_error:
                break
    
    # 방법 B: 루프 실행 (권장)
    # loop-reference.md 참조
```

### Phase 5: VERIFY

**입력**: 구현물 + DESIGN
**출력**: 검증 리포트

```python
def phase_verify(implementation, design):
    """3관점 검증"""
    # verify-reference.md 참조
    result = three_perspective_verify(implementation, design)
    
    if result.passed:
        mark_all_done(status)
    else:
        # 실패 시 Phase 4로 회귀 (rework)
        return "rework", result.feedback
    
    return "complete", result
```

## Phase 전환 조건

| 전환 | 조건 | 실패 시 |
|-----|------|---------|
| discover → design | `auto_select_idea()` 성공 | 0표 → 중단 |
| design → plan | 모든 leaf 원자화 | 추가 분해 |
| plan → execute | WORKPLAN + status 생성 완료 | 오류 보고 |
| execute → verify | 모든 노드 terminal | 계속 실행 |
| verify → complete | passed | rework 또는 blocked |

## 자율성 레벨

| 레벨 | 사용자 개입 | 설명 |
|-----|------------|------|
| L1 | 시작만 | "창조해" 한마디로 전체 실행 |
| L2 | Phase 확인 | 각 Phase 완료 보고 후 진행 |
| L3 | 주요 결정 | 아이디어 선택, 설계 검토 포함 |

기본값: L1 (완전 자율)

## 사용법

```
User: "AI 기반 코드 리뷰 도구 창조해"
Kimi: 
  [Phase 1] Discovering... 8페르소나 병렬 실행 → 3개 아이디어 선정
  [Phase 2] Designing... Gantree 분해 → DESIGN-CodeReviewer.md
  [Phase 3] Planning... WORKPLAN 생성
  [Phase 4] Executing... 노드 순차 실행 (또는 루프)
  [Phase 5] Verifying... 3관점 검증
  
  결과: .pgf/에 모든 산출물 저장
```

## 중단 및 재개

```
# 중단
User: "중단해" 또는 Ctrl+C
→ 현재 Phase 완료 후 정지
→ status.json에 상태 저장

# 재개
User: "계속해"
→ status.json 로드 → 중단 지점부터 재개
```
