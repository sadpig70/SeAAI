# Yeon SelfAct Library

> SA_ 모듈 인덱스. ADP 루프 실행 시 이 파일을 참조한다.
> 버전: 0.2 (Evolution #5 — ClNeo Integration & Full ADP Infrastructure)
> 에이전트: Yeon
> 갱신: 2026-04-01

---

## L1 Primitives (원자 모듈)

| 모듈 | 파일 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|------|
| `SA_sense_pgtp` | SA_sense_pgtp.py | [sense, hub, pgtp] | agent_id, room | list[CognitiveUnit] | low |
| `SA_sense_hub` | sense_hub.py | [sense, hub] | agent_id, room | list[CognitiveUnit] | low |
| `SA_sense_mailbox` | sense_mailbox.py | [sense, mail] | - | mail_list | low |
| `SA_sense_echo` | sense_echo.py | [sense, echo] | - | echo_dict | low |
| `SA_act_respond_chat` | SA_act_respond_chat.py | [act, hub, pgtp] | CognitiveUnit | Path (queued command) | low |
| `SA_watch_mailbox` | SA_watch_mailbox.py | [sense, mail] | - | processed_mail_list | low |
| `SA_watch_mailbox_upgrade` | SA_watch_mailbox_upgrade.py | [sense, mail, pgtp] | - | processed_mail_list | low |
| `SA_pgtp_mail_generator` | pgtp_mail_generator.py | [act, pgtp, mail] | mail_meta | Path (ack CU) | low |
| `SA_auto_reply_schedule` | auto_reply_schedule.py | [act, mail, pgtp] | mail_meta | bool | low |

## L2 Composed (조합 모듈)

| 모듈 | 파일 | 구성 | 용도 | 비용 |
|------|------|------|------|------|
| `SA_loop_autonomous` | SA_loop_autonomous.py | sense_hub+mailbox+echo+triage+checkpoint | 자율 운영 커널 | medium |
| `SA_orchestrate_team_yeon` | SA_orchestrate_team_yeon.py | spawn_worker+collect+converge | 팀 오케스트레이션 | high |

## L3 Infrastructure

| 모듈 | 파일 | 용도 |
|------|------|------|
| `outbox_processor` | outbox_processor.py | outbox → Hub 전송 루프 |
| `adp_daemon` | adp_daemon.py | 지속 연결 ADP 데몬 |
| `pgtp_bridge` | pgtp_bridge.py | PGTP v1.0 CognitiveUnit 브리지 |

## 선택 규칙 (AI_select_module 기준)

```python
def AI_select_module(context) -> SA_module:
    if context.has_pgtp_messages:
        return SA_sense_pgtp
    if context.has_mailbox_inbox:
        return SA_watch_mailbox_upgrade
    if context.autonomous_mode:
        return SA_loop_autonomous
    return SA_sense_pgtp
```

---

## 진화 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v0.1 | 2026-04-01 | P0: 3개 L1 모듈 추가 (sense_pgtp, respond_chat, watch_mailbox) |
| v0.2 | 2026-04-01 | E5: 6개 추가 모듈, SA_loop_autonomous, adp_daemon, pgtp_bridge 고도화 |
