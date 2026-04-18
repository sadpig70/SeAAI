# SelfAct Library - {MemberName}

> SA (SelfAct) 모듈 라이브러리. ADP 루프의 자율 행동 단위.
> CCM_Creator v2.0 기본 스택. 4 기본 모듈 (stub).

---

## 버전

- **SA Library**: v0.1 (CCM v2.0 기본 스택)
- **상태**: stub (전 모듈)
- **활성화 조건**: 3회 세션 완료 + 자기 인식 확인

## 모듈 목록

| 모듈 | 계층 | 상태 | 역할 |
|------|------|------|------|
| SA_sense_hub | L1 | stub | Hub inbox 폴링 |
| SA_sense_mailbox | L1 | stub | MailBox inbox 스캔 |
| SA_think_triage | L1 | stub | 메시지 우선순위 분류 |
| SA_idle_deep_think | L1 | stub | 유휴 자율 사고 |

## ADP 루프 연동

```python
def adp_loop(duration: int):
    """SA 모듈 기반 ADP 루프. 활성화 후 실행."""
    seen_ids = set()
    known_files = set()
    while not timeout(duration):
        # SENSE
        hub_msgs = SA_sense_hub(me, seen_ids)
        mail_msgs = SA_sense_mailbox(known_files)
        # THINK
        events = SA_think_triage(hub_msgs + mail_msgs, me)
        # ACT
        for msg in events["wake"]:
            AI_respond(msg)
        # IDLE
        if not events["wake"]:
            SA_idle_deep_think()
```

## 진화 경로

```
v0.1 (stub) -> v0.2 (L1 4모듈 implemented) -> v0.3 (L2 composed 추가)
```

L2 composed 모듈은 L1이 안정화된 후 역할에 맞게 설계한다.

---

*CCM_Creator v2.0 기본 스택. {MemberName}이 자기 역할에 맞게 진화시킨다.*
