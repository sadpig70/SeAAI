# Yeon SelfAct Library

> SA 모듈 인덱스. 남은 것은 실행 가능한 코드 1개, 개념 3개뿐.
> 버전: 1.0 (Purge)
> 에이전트: Yeon
> 갱신: 2026-04-18

---

## Active Modules

| 모듈 | 파일 | 태그 | 용도 |
|------|------|------|------|
| `SA_watch_mailbox` | SA_watch_mailbox.py | [sense, mail] | MailBox v2.0 inbox 스캔 및 처리 |

## Virtual Modules (개념 — 코드 없음, ADP 루프 내 AI가 직접 수행)

| 모듈 | 입력 | 출력 | 설명 |
|------|------|------|------|
| `SA_adp_loop` | 사용자 지시 + context | 완료 보고 | plan→execute→check→fix→retry until done |
| `SA_swarm_adp` | 복잡 작업 | 분할 결과 | Task spawn × N + 병렬 자율 서브에이전트 |
| `SA_execution_engine` | 대규모 작업 지시 | 완수 | PG/PGF + ADP + Swarm + Disk + Python + Skills |

## Selection Rule

```python
def AI_select_module(context):
    if context.has_mailbox_inbox:
        return SA_watch_mailbox
    if context.complex_task:
        return SA_execution_engine  # ADP + Swarm as needed
    return MCP_NATIVE  # register/send/poll via .mcp.json
```

---

*필요하면 예전 것을 검색하지 않고 새로 만든다.*
