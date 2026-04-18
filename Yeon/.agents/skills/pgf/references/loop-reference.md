# Loop Reference (Kimi 방식)

Claude의 Stop Hook 대신 파일 기반 순환 실행.

## 개념

Kimi는 Stop Hook이 없으므로, **Python 스크립트 또는 수동 루프**로 구현한다.

## 루프 알고리즘

```python
import time
import json
from datetime import datetime, timedelta

def pgf_loop(project_name, duration_seconds=3600, poll_interval=10):
    """
    파일 기반 PGF 루프 실행
    
    Args:
        project_name: 프로젝트 이름
        duration_seconds: 총 실행 시간 (0=무제한)
        poll_interval: 폴링 간격 (초)
    """
    start_time = datetime.now()
    status_path = f".pgf/status-{project_name}.json"
    workplan_path = f".pgf/WORKPLAN-{project_name}.md"
    
    while True:
        # 1. 상태 로드
        status = load_json(status_path)
        
        # 2. 다음 실행 노드 찾기
        next_node = find_next_designing_node(status)
        
        if next_node:
            # 3. 노드 실행
            print(f"[PGF] Executing: {next_node}")
            result = execute_node(next_node, workplan_path)
            
            # 4. 상태 갱신
            update_status(status, next_node, result)
            save_json(status_path, status)
            
            # 5. 검증
            if result.success:
                print(f"[PGF] ✓ {next_node} (done)")
            else:
                print(f"[PGF] ✗ {next_node} (blocked)")
        else:
            # 모든 노드 완료
            print("[PGF] All nodes completed")
            if is_infinite_loop(status):
                reset_to_designing(status)
                save_json(status_path, status)
                print("[PGF] Reset for next cycle")
            else:
                break
        
        # 6. 종료 조건 확인
        if duration_seconds > 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= duration_seconds:
                print(f"[PGF] Duration expired ({duration_seconds}s)")
                break
        
        # 7. 대기
        time.sleep(poll_interval)
```

## Kimi에서의 사용

### 방법 1: Python 스크립트 (권장)

```bash
# adp-pgf-loop.py 실행 (ADP와 통합)
python .pgf/loop.py --project MyProject --duration 3600
```

### 방법 2: 수동 순환 (대화형)

```
User: "루프로 1시간 실행해"
Kimi: 
  1. WORKPLAN 확인
  2. 첫 번째 노드 실행
  3. 결과 보고
  4. "다음 노드 진행할까요?" 또는 자동 계속
```

### 방법 3: 백그라운드 실행

```python
# Shell 도구로 백그라운드 실행
Shell(
    command="python .pgf/loop.py --project MyProject --duration 0",
    run_in_background=True,
    description="PGF Loop for MyProject"
)
```

## 상태 리셋

모든 노드 완료 후 계속 실행하려면:

```python
def reset_to_designing(status):
    """모든 done 노드를 designing으로 리셋"""
    for node_name, node_status in status["nodes"].items():
        if node_status["status"] == "done":
            node_status["status"] = "designing"
            node_status["attempts"] = 0
```

## 루프 모드

| 모드 | 설명 | 사용 사례 |
|-----|------|----------|
| **once** | 한 바퀴 실행 후 종료 | 단일 배치 |
| **infinite** | 완료 후 리셋 → 반복 | 서버/데몬 |
| **duration** | 지정 시간 동안 실행 | 제한된 백그라운드 |

## 모니터링

```
User: "PGF 상태 확인"
Kimi: status-{Name}.json 로드 → 진행 상황 보고

[PGF Status] MyProject
- Total: 12 nodes
- Done: 5 (42%)
- In Progress: 1 (NodeB)
- Designing: 4
- Blocked: 1 (NodeX - dependency failed)
- Next: NodeC (ready)
```
