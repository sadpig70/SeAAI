# DESIGN — SeAAIADP-BridgeTick
# 서버 heartbeat 제거 + Bridge 자체 heartbeat (8~10초 랜덤)
# Author: NAEL | Date: 2026-03-24 | Mode: full-cycle

## Gantree

```
SeAAIADP-BridgeTick // 서버 heartbeat → Bridge 자체 heartbeat 전환
    RemoveServerHeartbeat // chatroom.rs에서 time_broadcast 제거
    AddBridgeTick // Bridge에 자체 tick 출력 추가
        TickLogic // 메시지 없을 때 8~10초 랜덤 간격으로 tick 출력
        TickParam // --tick-min, --tick-max CLI 파라미터 추가
    VerifyBuild // Rust 빌드 + Python 구문 검증
    UpdateDocs // 관련 문서 갱신
        UpdateADPSpec // SharedSpace/SPEC-AgentDaemonPresence-v1.1.md
        UpdateProtocol // PROTOCOL-SeAAIChat-v1.0.md (heartbeat 설명 갱신)
        UpdatePGDoc // SeAAI-Architecture-PG.md
        UpdateTechSpec // SeAAI-Technical-Specification.md
```

## PPR

```python
def RemoveServerHeartbeat():
    """chatroom.rs에서 time_broadcast 관련 코드 제거.
    acceptance_criteria:
        - time_broadcast_interval_secs 필드 제거
        - last_time_broadcast_at 필드 제거
        - maybe_broadcast_time_messages_at() 함수 제거
        - inject_hub_time_message() 함수 제거
        - 관련 테스트 코드 갱신
        - cargo build 성공
    """

def AddBridgeTick():
    """Bridge가 자체 tick을 stdout에 출력.
    acceptance_criteria:
        - 새 메시지 있으면 즉시 출력 (기존 동작 유지)
        - 새 메시지 없고 마지막 stdout 출력 이후 N초 경과 → tick 출력
        - N = random.uniform(tick_min, tick_max), 매 tick마다 재생성
        - tick_min 기본 8.0, tick_max 기본 10.0
        - tick JSON: {"kind": "bridge-tick", "tick": n, "next_in": N}
        - poll_interval 유지 (1초) — 메시지 감지는 빠르게
    """

def UpdateDocs():
    """4개 문서 갱신.
    acceptance_criteria:
        - ADP spec: "서버 heartbeat" → "Bridge 자체 tick" 설명 변경
        - Protocol: heartbeat intent 설명에 Bridge tick 반영
        - PG doc: ADP 섹션 갱신
        - Tech spec: ADP 섹션 갱신
    """
```
