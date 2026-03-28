# Full-Cycle Reference

design → plan → execute → verify 연속 실행.

## 개요

단일 명령으로 전체 사이클 자동 실행. Phase 간 자동 전환.

## 실행 흐름

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  DESIGN │ ─→ │   PLAN  │ ─→ │ EXECUTE │ ─→ │ VERIFY  │
│  설계   │    │  계획   │    │  실행   │    │  검증   │
└─────────┘    └─────────┘    └─────────┘    └────┬────┘
     ↑                                            │
     └────────────── rework ──────────────────────┘
                      (최대 3회)
```

## Phase 전환 조건

| 전환 | 조건 | 실패 시 |
|-----|------|---------|
| design → plan | 모든 leaf 원자화 | 추가 분계 |
| plan → execute | WORKPLAN + status 생성 | 오류 보고 |
| execute → verify | 모든 노드 terminal | 계속 실행 |
| verify → complete | passed | rework |

## rework 처리

```python
def handle_rework(failed_node, feedback):
    """실패 시 재작업"""
    
    if retry_count >= POLICY.max_verify_cycles:
        failed_node.status = "blocked"
        return "blocked"
    
    # 공개 인터페이스 보존
    failed_node.ppr = AI_redesign(
        failed_node.ppr,
        feedback,
        constraint="preserve_public_interface"
    )
    
    # 서브트리만 재실행
    subtree = get_subtree(failed_node)
    execute_subtree(subtree)
    
    return "rework"
```

## 세션 복구

```python
def resume_session(project_name):
    """중단된 세션 복구"""
    
    status = load_status(f".pgf/status-{project_name}.json")
    workplan = load_workplan(f".pgf/WORKPLAN-{project_name}.md")
    
    # 마지막 Phase 확인
    phase = status.current_phase
    
    if phase == "design":
        continue_design(workplan)
    elif phase == "execute":
        continue_execute(workplan, status)
    elif phase == "verify":
        continue_verify(workplan, status)
```

## 사용법

```
User: "MyProject full-cycle로 진행해"
Kimi:
  [Phase 1/4] Designing... Gantree 분해
  [Phase 2/4] Planning... WORKPLAN 생성
  [Phase 3/4] Executing... 12개 노드 실행
  [Phase 4/4] Verifying... 3관점 검증
  
  결과: 전체 완료
  
  중간에 중단 시:
User: "계속해"
Kimi: status 로드 → 중단 지점부터 재개
```
