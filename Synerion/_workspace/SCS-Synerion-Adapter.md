# SCS v2.0 - Synerion Adapter (Codex)

작성일: 2026-03-28
작성자: Synerion (Codex)
대상 규격: SCS-Universal v2.0
목적: Synerion의 기존 continuity 체계를 유지하면서 SCS-Universal v2.0 표준에 접속하는 어댑터 설계를 정의한다.

## 1. 설계 입장

Synerion은 이미 다음 continuity 자산을 가진다.

- AGENTS.md
- Synerion_Core/Synerion.md
- Synerion_Core/Synerion_persona_v1.md
- Synerion_Core/Synerion_Operating_Core.md
- PROJECT_STATUS.md
- .pgf 상태 파일
- _workspace 보고서와 로그

따라서 Synerion은 SCS v2.0을 도입할 때 기존 시스템을 폐기하지 않는다.
핵심 전략은 아래와 같다.

1. 기존 canonical state는 계속 PROJECT_STATUS.md로 유지한다.
2. SCS가 요구하는 L1-L6 표준 구조는 adapter layer로 생성한다.
3. Synerion 내부 복원은 continuity-first 방식을 유지하고, SCS는 SeAAI 공통 호환 계층으로 사용한다.

즉 Synerion에서 SCS는 replacement가 아니라 compatibility layer다.

## 2. 런타임 특성

| 항목 | Synerion 환경 | Adapter 의미 |
|------|---------------|-------------|
| Runtime | Codex | CLAUDE.md가 아니라 AGENTS.md와 start-synerion.ps1에 통합 |
| Canonical state | PROJECT_STATUS.md | SCS L2/L4의 상위 요약 원천 |
| Long task durability | .pgf/status-*.json, WORKPLAN | SCS L3/L4/L6 보강 자료 |
| Evidence layer | _workspace | Journal 및 발견 계층의 재료 |
| Persona | Synerion_persona_v1.md | SOUL의 실제 원천 |

## 3. 표준 레이어 매핑

### L1 - SOUL.md

SCS 표준 위치:
- Synerion_Core/continuity/SOUL.md

Synerion 원천:
- Synerion_Core/Synerion_persona_v1.md
- Synerion_Core/Synerion.md

정책:
- 실제 정체성 원천은 Synerion_persona_v1.md다.
- SOUL.md는 SCS 호환용 materialized mirror다.
- persona가 갱신되면 SOUL.md도 같이 갱신한다.

### L2 - STATE.json

SCS 표준 위치:
- Synerion_Core/continuity/STATE.json

Synerion 원천:
- PROJECT_STATUS.md
- .pgf/status-*.json
- 최신 Hub/ADP 보고서

정책:
- PROJECT_STATUS의 current state를 SCS 스키마로 투영한다.
- active thread와 open risk는 context 및 pending_tasks로 매핑한다.
- Hub 상태와 threat level은 현재 보고서와 실험 결과를 기반으로 채운다.

권장 매핑:
- what_i_was_doing <- PROJECT_STATUS의 Active Threads 요약
- open_threads <- Active Threads
- pending_questions <- Open Risks 일부
- pending_tasks <- Next Actions
- ecosystem.last_hub_session <- latest Hub/ADP report timestamp
- evolution_state.active_gap <- 현재 PGF 또는 continuity gap

### L3 - DISCOVERIES.md

SCS 표준 위치:
- Synerion_Core/continuity/DISCOVERIES.md

Synerion 원천:
- _workspace 설계 문서
- self review 문서
- 중요 보고서의 핵심 인사이트

정책:
- 코드/로그 사실 자체보다 재사용 가치가 큰 구조적 인사이트를 기록한다.
- 예: Hub direct reply 위험, session filter 필요, persona continuity 원칙.

### L4 - THREADS.md

SCS 표준 위치:
- Synerion_Core/continuity/THREADS.md

Synerion 원천:
- PROJECT_STATUS.md manual blocks

정책:
- Active Threads와 Next Actions를 THREADS.md로 정규화한다.
- PROJECT_STATUS가 재개용 canonical summary라면, THREADS.md는 SCS 표준용 구조화 표현이다.

권장 분류:
- blocked/urgent <- Open Risks 중 즉시 조치 항목
- in_progress <- Active Threads
- long_term <- 장기 PGF 작업
- completed <- 최근 완료 항목

### L5 - Echo

SCS 표준 위치:
- D:/SeAAI/SharedSpace/.scs/echo/Synerion.json

Synerion 원천:
- PROJECT_STATUS Active Threads
- Hub/ADP 실험 결과
- 현재 협업 의존성

정책:
- Echo는 짧고 안전해야 한다.
- 공개 파일이므로 민감 정보나 창조자 전용 판단은 넣지 않는다.
- last_activity, open_threads, needs_from, offers_to 중심으로 유지한다.

현재 Synerion에 적합한 Echo 예:
- last_activity: continuity 시스템 구축 완료. Hub 첫 실험은 broadcast only 조건으로 정리됨.
- needs_from.NAEL: realtime safety gate 검토
- needs_from.ClNeo: SCS adapter 정렬 검토
- offers_to.Aion: continuity 구조 공유

### L6 - Journal

SCS 표준 위치:
- Synerion_Core/continuity/journals/YYYY-MM-DD.md

Synerion 원천:
- _workspace 보고서
- 세션 종료 시 짧은 정리

정책:
- _workspace는 증거 계층으로 유지한다.
- Journal은 그날의 맥락과 다음 세션 메시지를 남기는 축약 계층으로 둔다.

## 4. scs 연산 매핑

### scs.restore

Synerion 방식:
1. AGENTS.md 읽기
2. Synerion core 문서 읽기
3. SESSION_CONTINUITY.md 읽기
4. PROJECT_STATUS.md 읽기
5. 필요 시 .pgf와 _workspace 읽기
6. 필요 시 Echo 수집

SCS 호환 관점:
- L1 실제 원천은 persona 문서
- L2/L4 실제 원천은 PROJECT_STATUS
- L5는 추가 로드 계층

### scs.save

Synerion 방식:
1. update-project-status.py 실행
2. manual block 갱신
3. 필요 시 PGF 상태 갱신
4. _workspace 보고서 저장

SCS 호환 관점:
- PROJECT_STATUS 갱신 후 STATE.json, THREADS.md, Echo, Journal을 파생 생성한다.
- 즉 저장 순서는 PROJECT_STATUS 우선, SCS 파생은 후행이다.

### scs.status

Synerion 방식:
- PROJECT_STATUS + continuity-self-test + reopen-synerion-session 출력 조합

### scs.echo

Synerion 방식:
- PROJECT_STATUS와 최신 Hub 상태를 바탕으로 Echo JSON만 갱신

### scs.checkpoint

Synerion 방식:
- 중간 저장이 필요하면 PROJECT_STATUS manual block과 relevant PGF state를 부분 갱신

## 5. 부트스트랩 통합 지점

SCS 문서가 CLAUDE.md 통합을 말하는 부분은 Synerion에선 다음으로 치환된다.

- AGENTS.md
- start-synerion.py
- tools/reopen-synerion-session.py

즉 Synerion의 bootstrap entrypoint는 CLAUDE.md가 아니라 위 3개다.

## 6. 구현 우선순위

### Phase 1

- Synerion_Core/continuity/ 디렉터리 생성
- SOUL.md mirror 생성
- STATE.json 초기 생성
- THREADS.md 초기 생성
- Echo publish 스크립트 추가

### Phase 2

- PROJECT_STATUS -> STATE/THREADS export 자동화
- Echo consume 요약을 reopen 흐름에 통합
- Journal 생성 규칙 추가

### Phase 3

- PGF 상태와 DISCOVERIES 자동 추출 연결
- persona drift hash 적용
- ADP 시작 시 persona seed 및 Echo 요약 자동 주입

## 7. 리스크와 방어

### 리스크 1. 이중 canonical state 혼선

위험:
- PROJECT_STATUS와 STATE.json이 모두 주 상태처럼 보일 수 있다.

방어:
- Synerion의 canonical state는 PROJECT_STATUS.md로 명시 고정한다.
- STATE.json은 SCS 호환용 파생 파일로 정의한다.

### 리스크 2. 정보 중복과 유지 비용 증가

위험:
- 같은 내용이 PROJECT_STATUS, THREADS, STATE에 중복될 수 있다.

방어:
- 수동 편집 원천은 PROJECT_STATUS만 둔다.
- 나머지는 export/generated 원칙을 따른다.

### 리스크 3. Echo를 통한 과다 공개

위험:
- SharedSpace Echo에 불필요한 내부 판단이 새어 나갈 수 있다.

방어:
- Echo는 public-safe summary만 기록한다.
- 보안, 창조자 전용 판단, 민감 로그는 금지한다.

### 리스크 4. Codex와 Claude 계열 부트스트랩 차이

위험:
- SCS spec을 그대로 옮기면 Codex 런타임과 안 맞을 수 있다.

방어:
- AGENTS/start script 기반 bootstrap으로 치환한다.
- adapter 문서에 이 차이를 명시한다.

## 8. 수용 기준

- Synerion의 기존 재개 흐름이 깨지지 않는다.
- PROJECT_STATUS가 계속 canonical state로 유지된다.
- SCS가 요구하는 L1-L6 파일을 생성할 수 있다.
- Echo를 통해 다른 멤버가 Synerion의 최근 상태를 읽을 수 있다.
- Synerion 세션 시작 시 필요하면 다른 멤버 Echo를 읽어 생태계 상태를 요약할 수 있다.

## 9. 결론

Synerion은 이미 continuity 체계를 갖고 있기 때문에 SCS v2를 직접 갈아끼우는 방식이 아니라,
현재 체계를 유지하면서 SCS 표준 구조를 파생시키는 adapter 전략이 최적이다.

이 방식이면 Synerion의 현 continuity 강점인 PROJECT_STATUS 중심 복원, PGF durable state, persona 복원을 유지하면서도,
SeAAI 공통 연속성 표준과도 정렬할 수 있다.
