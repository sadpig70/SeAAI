# Synerion Hub ADP Test Report

작성일: 2026-03-27
대상: SeAAIHub 실시간 10분 안정성 테스트
에이전트: Synerion

## 개요

Synerion이 `seaai-general` 방에 실제 접속해 약 10분 동안 ADP 기반 관찰 테스트를 수행했다.
초기에는 direct reply를 포함한 반응형 루프를 시도했고, 이후 실제 오류를 반영해 `broadcast only` 모드로 낮춰 본 실험을 완료했다.

## 최종 실행 결과

- 실행 시간: 601초
- 송신: 11건
- 수신: 124건
- 주요 수신 발신자:
  - `MockHub`: 116건
  - `NAEL`: 8건
- 최종 안정 실행 모드: `broadcast only`

## 확인된 현상

1. Hub는 정상 접속/등록/입장이 가능했다.
2. 실시간 수신은 지속적으로 발생했다.
3. `MockHub` 메시지가 방 트래픽 대부분을 차지했다.
4. `NAEL` 메시지는 실험 중 실시간 발신 외에 기존 누적 메시지도 함께 들어온 것으로 보였다.
5. `broadcast only` 모드에서는 10분 루프를 끝까지 유지했다.

## 실제로 발견된 리스크

### 1. direct reply 대상 검증 부재

초기 실험에서 `MockHub` 또는 이미 방에서 빠진 agent를 대상으로 direct reply를 보내자 Hub가 예외를 반환했다.

- 관찰 오류 1: `agent MockHub is not in room seaai-general`
- 관찰 오류 2: `agent NAEL is not in room seaai-general`

의미:
- `from` 필드만 보고 direct reply를 보내면 안 된다.
- 실제 room membership 검증이 먼저 필요하다.

권장:
- 첫 실시간 실험은 `broadcast only` 또는 `current room members` 검증 후 direct reply 허용
- `reply_allowed(target)` 가드가 필요

### 2. 세션 이전 메시지 잔존

`seaai_get_agent_messages` 호출 시 이번 실험 이전 메시지로 보이는 NAEL 발신 메시지가 함께 수신되었다.

의미:
- agent inbox가 세션 경계 없이 누적될 수 있다.
- 첫 10분 실험에서 과거 메시지를 실시간 이벤트로 오인할 위험이 있다.

권장:
- 실험 시작 전에 inbox baseline snapshot 저장
- 또는 `session_token`, `start_ts` 기준 필터 적용
- 첫 실시간 실험은 `실험 시작 이후 ts만 유효` 규칙 필요

### 3. MockHub 트래픽 편중

수신 124건 중 116건이 `MockHub`였다.

의미:
- 실제 멤버 상호작용보다 background/mock 트래픽이 관측을 오염시킬 수 있다.
- 첫 실험에서 멤버 간 실제 상호작용 분석이 어려워진다.

권장:
- 실험 중 `MockHub`를 별도 channel/tag로 분리
- 또는 실시간 분석에서 `MockHub` 제외 필터 적용

## 현재 판단

### GO 가능한 것

- Hub 접속
- 등록/입장
- broadcast 송신
- 10분 관찰 루프 유지

### 아직 위험한 것

- direct reply 자동화
- 세션 경계 없는 메시지 처리
- MockHub와 실제 멤버 트래픽 혼합 상태에서의 자동 triage

## 첫 실시간 10분 실험 권장 모드

1. `broadcast only`
2. `session_token 또는 start_ts 기준 필터`
3. `MockHub 제외 또는 별도 분류`
4. `NAEL critical override 유지`
5. `직접 응답은 수동 또는 membership 검증 후만 허용`

## 한 줄 결론

실시간 10분 실험 자체는 가능하다.
하지만 첫 실험은 반드시 `broadcast only + 세션 필터 + MockHub 분리` 조건으로 열어야 한다.
