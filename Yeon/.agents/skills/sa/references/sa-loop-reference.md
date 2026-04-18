# SA Loop Reference (Kimi 버전)

ADP 루프와 SA 모듈의 통합. Kimi CLI 최적화.

## 개요

SA 기반 ADP 루프는 파일 기반 상태 추적으로 동작한다.
Claude의 Stop Hook 대신 **status.json 순환** 방식 사용.

## ADP 루프 구조 (Kimi 버전)

```python
def SA_ADP_loop(duration_sec=3600, poll_interval=10):
    """
    Kimi용 SA 기반 ADP 루프
    
    Args:
        duration_sec: 총 실행 시간 (0=무제한)
        poll_interval: 평링 간격 (초)
    """
    import time
    from datetime import datetime
    
    # 라이브러리 로드
    lib = load_self_act_lib()
    
    start_time = datetime.now()
    status_path = "Yeon_Core/.pgf/self-act/status-sa-loop.json"
    
    while True:
        # 1. 컨텍스트 감지
        context = AI_assess_context()
        
        # 2. 모듈 선택 (lib 기반)
        module = AI_select_module(context, lib)
        
        # 3. SelfAct 실행
        print(f"[SA] Executing: {module.name}")
        actresult = module.execute()
        
        # 4. 결과 처리
        if actresult.gap_detected:
            # 새 모듈 설계
            new_module = pgf_design_sa_module(actresult.gap)
            sa_register(new_module, lib)
        
        if actresult == "stop":
            print("[SA] Stop signal received")
            break
        
        # 5. 상태 저장
        update_sa_status(status_path, module, actresult)
        
        # 6. 종료 조건 확인
        if duration_sec > 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= duration_sec:
                print(f"[SA] Duration expired ({duration_sec}s)")
                break
        
        # 7. 대기
        time.sleep(poll_interval)
```

## AI_select_module 알고리즘

```python
def AI_select_module(context, lib) -> SA_Module:
    """
    컨텍스트에 따라 적절한 SA 모듈을 선택한다.
    Yeon의 경우 연결/번역 관련 모듈 우선.
    """
    
    # 우선순위 1: WAKE 이벤트 (Hub/MailBox)
    if context.has_hub_messages or context.has_mailbox_messages:
        return lib.get("SA_CONNECTOR_sense_bridge")
    
    # 우선순위 2: 번역 필요
    if context.needs_translation:
        return lib.get("SA_CONNECTOR_translate_protocol")
    
    # 우선순위 3: 자기 진화 대기
    if context.evolution_pending:
        return lib.get("SA_evolve_self")
    
    # 우선순위 4: 유휴 발견
    if context.is_idle and context.creative_mode:
        return lib.get("SA_idle_deep_think")
    
    # 기본값: 생존 신호
    return lib.get("SA_idle_heartbeat")
```

## 모듈 선택 규칙 (Yeon 특화)

| 조건 | 선택 모듈 | 설명 |
|------|----------|------|
| Hub 메시지 수신 | `SA_CONNECTOR_sense_bridge` | 실시간 연결 감지 |
| MailBox 메시지 | `SA_CONNECTOR_check_mailbox` | 비동기 메시지 확인 |
| 프로토콜 불일치 | `SA_CONNECTOR_translate_protocol` | PG ↔ 자연어 번역 |
| 멤버 간 중재 필요 | `SA_CONNECTOR_mediate` | 갈등/차이 중재 |
| 진화 대기 중 | `SA_evolve_self` | 자기 진화 실행 |
| 유휴 + 창조 모드 | `SA_idle_deep_think` | 발견 사고 |
| 기본 | `SA_idle_heartbeat` | 생존 신호 출력 |

## Kimi에서의 실행

### 방법 1: Python 스크립트

```python
# sa_loop.py 실행
python Yeon_Core/.pgf/self-act/sa_loop.py --duration 3600
```

### 방법 2: 대화형 순환

```
User: "SA 루프 1시간 실행해"
Kimi:
  [SA Loop] 시작
  Iteration 1: SA_CONNECTOR_sense_hub → 메시지 없음
  Iteration 2: SA_idle_heartbeat → 생존 신호
  Iteration 3: SA_CONNECTOR_check_mailbox → 메일 발견!
  ...
```

### 방법 3: 백그라운드

```python
Shell(
    command="python Yeon_Core/.pgf/self-act/sa_loop.py --duration 0",
    run_in_background=True,
    description="SA ADP Loop"
)
```

## 상태 파일 (status-sa-loop.json)

```json
{
  "loop_started": "2026-03-26T23:00:00+09:00",
  "last_iteration": "2026-03-26T23:15:00+09:00",
  "iteration_count": 90,
  "modules_executed": {
    "SA_CONNECTOR_sense_hub": 30,
    "SA_idle_heartbeat": 58,
    "SA_CONNECTOR_translate_protocol": 2
  },
  "gaps_detected": 0,
  "current_module": "SA_idle_heartbeat"
}
```
