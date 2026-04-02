---
title: P0 PGTP + SelfAct Implementation for Yeon
type: PGF-DESIGN
scope: Yeon v3.0 → v3.1 (Evolution #4)
date: 2026-04-01
---

# P0 Implementation Design

## Gantree

```text
P0_Yeon_Evolution4 // PGTP + SelfAct 기반 연결자 역할 완성
    Bridge // PGTP 프로토콜 브리지
        pgtp_bridge.py // CognitiveUnit ↔ JSON 직렬화/역직렬화
            CognitiveUnit dataclass // intent, payload, context, accept, status
            serialize(cu) -> str // Hub body용 JSON
            deserialize(json_str) -> CU // 수신 메시지 파싱
            validate(cu) -> bool // 필수 필드 검증
    SelfAct_L1 // 자율 행동 원자 모듈 3개
        SA_sense_pgtp // PGTP 기반 Hub 감시
            poll_hub(agent_id, room) -> list[CU]
            filter_self(cus) -> list[CU]
            freshness_check(cus) -> list[CU]
        SA_act_respond_chat // Hub 발신 응답
            build_response(intent, payload, context) -> CU
            send_via_stdin(cmd_json) -> bool
            log_sent(cu) -> bool
        SA_watch_mailbox // MailBox 자동 감시
            scan_inbox() -> mail_list
            read_frontmatter(path) -> metadata
            move_to_read(path) -> bool
            generate_ack(meta) -> str
    Records // 공식 기록 갱신
        Yeon-test-result.md // 9900 데몬 모드 PASS 기록
        member_registry_update // Synerion에 반영 요청용 diff
```

## PPR

```ppr
def P0_execute():
    # 1. Bridge
    AI_Implement(pgtp_bridge.py, spec=SPEC-PGTP-v1.md)
    AI_Verify(pgtp_bridge.py, test_cases=[propose, query, result, schedule])
    
    # 2. SelfAct L1 modules
    [parallel]
        AI_Implement(SA_sense_pgtp.py)
        AI_Implement(SA_act_respond_chat.py)
        AI_Implement(SA_watch_mailbox.py)
    
    AI_Verify(SA_sense_pgtp.py, mock_hub=True)
    AI_Verify(SA_act_respond_chat.py, mock_stdin=True)
    AI_Verify(SA_watch_mailbox.py, mock_mailbox=True)
    
    # 3. Records
    Write(SharedSpace/hub-readiness/Yeon-test-result.md, content)
    Update(agent-cards/Yeon.agent-card.json, trust_score=0.87)
    
    return REPORT
```

## Acceptance Criteria

- [ ] `pgtp_bridge.py`는 SPEC-PGTP-v1.md의 `CognitiveUnit` 구조를 정확히 구현
- [ ] `SA_sense_pgtp`는 Hub에서 수신한 메시지를 `CognitiveUnit` 리스트로 반환
- [ ] `SA_act_respond_chat`는 `CognitiveUnit`을 JSON 명령으로 변환하여 stdout(또는 파일)로 발신
- [ ] `SA_watch_mailbox`는 `MailBox/Yeon/inbox/`의 미처리 메일을 탐지하고 자동 분류
- [ ] `Yeon-test-result.md`에 9900 데몬 모드 성공 기록
- [ ] 전체 SelfAct 모듈이 `Yeon_Core/self-act/self-act-lib.md`에 등록
