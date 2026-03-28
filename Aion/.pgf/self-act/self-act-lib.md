# SelfAct Library — Aion

## L1 Primitives

| 모듈 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|
| SA_sense_heartbeat | [sense] | - | status | low |
| SA_idle_memory_index | [idle, memory] | - | index_update | medium |

## L2 Composed

| 모듈 | 구성 | 용도 |
|------|------|------|
| SA_loop_pulse | SA_sense_heartbeat + SA_idle_memory_index | 생존 및 기억 정기 스캔 |

## L3 Platforms

| 플랫폼 | 도메인 | 모듈 수 |
|--------|--------|---------|
| SA_MEMORY_* | 기억·리콜 플랫폼 | 1 |

## 선택 규칙 (AI_select_module 기준)

```python
def AI_select_module(context) -> SA_module:
    if context.is_idle:
        return SA_loop_pulse
    return SA_sense_heartbeat  # 기본값
```
