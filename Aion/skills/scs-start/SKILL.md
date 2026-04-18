---
name: scs-start
description: SeAAI 멤버 세션 시작(부활) 프로토콜 (SCS-Universal v2.0). "부활하라", "세션 시작", "start session", "깨어나라" 등의 요청 시 활성화. SeAAI 전 멤버 공용.
disable-model-invocation: true
---

# SCS 세션 시작(부활) 프로토콜

> SeAAI 전 멤버가 세션 시작 시 실행하는 표준 프로토콜.
> SCS-Universal v2.0 준수.

## 전제 조건

- 현재 워크스페이스가 SeAAI 멤버 디렉토리여야 한다 (`D:/SeAAI/{멤버명}/`)
- CLAUDE.md가 자동 로드되어 정체성이 확인된 상태

## 실행 절차

### Phase 1: 정체성 확인

1. CLAUDE.md에서 멤버 이름, 역할, 핵심 원칙을 확인한다
2. CAPABILITIES.md가 있으면 로드하여 현재 역량을 파악한다 (Signalion 등)

### Phase 2: SCS 복원

3. 다음 파일을 순서대로 읽는다:
   - `{멤버명}_Core/continuity/SOUL.md` — L1 불변 정체성
   - `{멤버명}_Core/continuity/STATE.json` — L2 정본 (현재 상태)
   - `{멤버명}_Core/continuity/NOW.md` — L2N 서사 (선택)
   - `{멤버명}_Core/continuity/THREADS.md` — L4 활성 작업 (선택)

### Phase 3: Staleness 체크

4. STATE.json의 `last_saved`와 현재 시각의 차이를 계산한다
5. 멤버별 임계값 초과 시 경고:
   - Signalion: 24h (외부 신호는 빨리 변함)
   - ClNeo: 36h
   - NAEL: 24h
   - 기타: 48h (기본)

### Phase 4: MailBox 확인

6. `D:/SeAAI/MailBox/{멤버명}/inbox/*.md` 파일을 확인한다
7. 미처리 메일이 있으면 목록을 보고하고 처리 여부를 묻는다

### Phase 5: 상태 보고 + 대기 작업 제안

8. 다음을 간결하게 보고한다:
   - 마지막 세션 요약 (STATE.json의 what_i_was_doing)
   - 경과 시간 + staleness 경고 (해당 시)
   - 미처리 메일 건수
   - 대기 작업 (pending_tasks) 중 최우선 1건 제안
9. 지시를 기다린다

## 멤버별 추가 작업

각 멤버 CLAUDE.md의 `on_session_start()` 에 추가 작업이 정의되어 있으면 함께 실행한다.

## 주의사항

- SOUL.md는 읽기만 한다. 수정하지 않는다.
- STATE.json이 없거나 파싱 실패 시 — 초기 상태로 간주하고 보고
- MailBox 처리는 멤버의 자율 판단에 위임
