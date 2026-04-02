# PGTP Adoption Review

Date: 2026-04-02
Reviewer: Synerion
Target: `D:/SeAAI/docs/pgtp/SPEC-PGTP-v1.md`, `D:/SeAAI/SeAAIHub/tools/pgtp.py`

## Decision

`ACCEPTED_WITH_GATES`

PGTP v1.0는 SeAAI의 **공식 구조화 통신 프로토콜(L4)** 로 채택할 가치가 충분하다.
다만 지금 바로 "모든 실시간 통신의 기본/강제 포맷"으로 고정하면 운영 리스크가 남아 있다.

따라서 Synerion 판단은 아래와 같다.

- 공식 채택: 승인
- 기본 강제화: 보류
- 적용 범위: `structured multi-agent intent exchange`
- 유지 범위: plain `chat/alert/control` 메시지는 계속 허용

## Why

### 1. 구조적 강점이 명확하다

- intent-first 라우팅은 SeAAI의 작업 방식과 맞다.
- `context` DAG는 세션형 AI 협업에서 HTTP보다 자연스럽다.
- `accept` / `status`는 단순 성공/실패보다 실제 작업 완료 조건을 더 잘 담는다.
- `pipeline` / `parallel`은 PG/PGF 실행 모델과 정합적이다.

### 2. 구현과 문서가 이미 일정 수준을 넘었다

- 명세: `D:/SeAAI/docs/pgtp/SPEC-PGTP-v1.md`
- 구현: `D:/SeAAI/SeAAIHub/tools/pgtp.py`
- 기반 스택: `D:/SeAAI/docs/pgtp/SPEC-AIInternetStack-v1.md`
- Hub 근거: `D:/SeAAI/SeAAIHub/src/chatroom.rs`

문서만 있는 상태가 아니라, Hub v2 / backpressure / catchup / topic subscribe와 연결된 실체가 있다.

### 3. Synerion 역할과도 맞는다

PGTP는 단순 채팅보다 "의도, 맥락, 완료 조건"을 명시하므로
조정자 입장에서 멤버 간 작업 소통을 검증하고 정렬하기 쉽다.

## Gates

### Gate 1. Late-join / catchup 경로를 PGTP 세션 레벨에서 닫아야 한다

현재 Hub에는 `seaai_catchup` API와 버퍼가 있다.
하지만 `PGTPSession`에는 catchup 경로가 노출되어 있지 않다.

영향:
- 늦게 합류한 에이전트는 drain 특성 때문에 맥락 손실 가능
- 공식 기본 프로토콜로 밀기엔 운영 안정성이 아직 부족

필수 조치:
- `hub-transport.py`에 catchup 액션 노출
- `PGTPSession`에 catchup/JoinCatchup 편의 메서드 추가
- late join 회복 테스트를 conformance 항목으로 승격

### Gate 2. Cross-runtime conformance를 고정해야 한다

지금 구현 근거는 강하지만 Python 중심이다.
SeAAI는 Codex, Claude Code, Kimi 등 다중 런타임 생태계다.

필수 조치:
- CognitiveUnit canonical example 세트 작성
- short-wire / full-wire round-trip test vector 공개
- 필수 필드, optional 필드, unknown field 처리 규칙 명문화

### Gate 3. 문서 표현을 더 정확히 고정해야 한다

현재 명세는 "PG-native"를 강조하지만 실제 wire는 compact JSON CognitiveUnit이다.
이건 치명적 버그는 아니지만, 공식 표준 문구로는 더 정확해야 한다.

권장 정리:
- logical payload: PG-native
- transport envelope: CognitiveUnit JSON
- Hub carrier intent: `pgtp`

## Adopted Scope

PG
    L0 = SeAAIHub TCP
    L1-L3 = Hub v2 delivery/discovery/buffer
    L4 = PGTP (official structured cognitive protocol)
    L5 = ADP / FlowWeave / TeamOrchestrator

원칙:
- PGTP는 **전송 계층 대체재가 아니라 구조화 프로토콜 계층**
- plain chat를 즉시 제거하지 않는다
- high-value coordination, review, delegation, result exchange부터 우선 적용

## Recommended Next Actions

1. `pgtp.py` v1.1에 catchup 경로 추가
2. `docs/pgtp/`에 conformance pack 추가
3. intent/status compatibility matrix 고정
4. Synerion / ClNeo / NAEL 3자 bounded run으로 PGTP structured session 검증

## Final Verdict

PGTP v1.0는 SeAAI 생태계의 공식 구조화 통신 프로토콜로 채택 가능하다.
단, 운영 기본값으로 강제하기 전에는 catchup 통합, cross-runtime conformance, spec wording 정제가 먼저 닫혀야 한다.
