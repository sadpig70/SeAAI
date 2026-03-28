# WORKPLAN Reference

DESIGN → WORKPLAN 변환 및 실행 가이드.

## WORKPLAN 구조

```markdown
# WORKPLAN-{Name}

## POLICY
- max_iterations: 10
- auto_verify: true
- stop_on_error: false
- retry_blocked: true

## Nodes
1. [ ] NodeA (designing) @dep:
   - # input: 필요한 입력
   - # process: 처리 로직 요약
   - # output: 예상 출력
   - # criteria: 완료 조건
   
2. [ ] NodeB (designing) @dep:NodeA
   - # PPR: inline 또는 def 참조
```

## DESIGN → WORKPLAN 변환 규칙

| DESIGN 요소 | WORKPLAN 변환 |
|------------|---------------|
| Gantree 트리 | 번호 목록으로 평탄화 |
| `(status)` | 체크박스 `[ ]` 또는 `[x]` |
| `@dep:` | 동일한 의존성 표기 유지 |
| PPR `def` | 간략한 `# process` 요약 또는 def 참조 |
| `#` 인라인 주석 | WORKPLAN 노드 하위에 유지 |

## 실행 알고리즘

```python
def execute_workplan(workplan_path, status_path):
    workplan = load_workplan(workplan_path)
    status = load_status(status_path)
    
    # 의존성 그래프 구성
    deps = build_dependency_graph(workplan.nodes)
    
    # 실행 가능한 노드 찾기 (의존성 모두 done)
    ready_nodes = find_ready_nodes(workplan.nodes, status, deps)
    
    for node in ready_nodes:
        # 상태 업데이트
        status.nodes[node.name].status = "in-progress"
        status.nodes[node.name].started = now()
        save_status(status)
        
        # PPR 실행
        result = execute_ppr(node.ppr)
        
        # 검증
        if verify(result, node.criteria):
            status.nodes[node.name].status = "needs-verify"
        else:
            status.nodes[node.name].status = "blocked"
            if POLICY.retry_blocked:
                # Failure Strategy 적용
                node.ppr = AI_redesign(node.ppr, result.failure)
                status.nodes[node.name].attempts += 1
        
        status.nodes[node.name].completed = now()
        save_status(status)
```

## 상태 전이

```
[designing] → [in-progress] → 실행 → 검증 → [needs-verify]
                                             ↓
                                    [passed] → [done]
                                    [rework] → [designing] (재시도)
                                    [blocked] → 정지/보고
```

## POLICY 옵션

| 옵션 | 기본값 | 설명 |
|-----|--------|------|
| max_iterations | 10 | 최대 재시도 횟수 |
| auto_verify | true | 자동 검증 수행 |
| stop_on_error | false | 오류 시 즉시 정지 |
| retry_blocked | true | blocked 시 재시도 |

## 병렬 실행 처리

`[parallel]` 블록 발견 시:

```python
parallel_nodes = extract_parallel_nodes(workplan)

# Task 도구로 병렬 실행
for node in parallel_nodes:
    Task(
        subagent_name="coder",
        description=f"Execute {node.name}",
        prompt=build_execution_prompt(node)
    )

# 결과 수집 및 통합
results = collect_results()
```

## 에러 복구

1. **단일 노드 실패**: 해당 노드만 redesign → 재시도
2. **의존성 실패**: 의존하는 모든 노드 blocked 처리
3. **세션 중단**: status.json 유지 → 다음 세션에서 재개
