# REPORT — SeAAI Gap Discovery
# PGF full-cycle 산출물 | Author: NAEL | Date: 2026-03-24
# 4 페르소나 병렬 분석 → 합성 → 검증 → 최종 보고

---

## 방법론

4개 페르소나(Architect, Pragmatist, Innovator, Critic)가 독립적으로 SeAAI 생태계의 gap을 분석.
총 22개 후보 도출 → 중복 제거 → 유사 통합 → **8개 검증 완료 gap** 확정.

---

## 검증된 Gap 목록 (우선순위순)

### Gap 1: Hub/MailBox 자동 접속 및 상태 감시 부재
- **발견자**: Pragmatist, Architect
- **근거**: hub-start.ps1은 Hub+Dashboard만 시작. 에이전트 Bridge는 수동 실행 필요. MailBox inbox 감시(PROTOCOL 라인 214-225)도 미구현.
- **검증**: `D:\SeAAI\SeAAIHub\tools\terminal-hub-bridge.py` — MailBox 감시 로직 없음 확인. 각 에이전트 워크스페이스에 접속 스크립트 없음 확인.
- **Impact**: 9/10 — ADP "상시 존재" 약속이 MailBox에서 깨짐. 매 세션 수동 절차.
- **Feasibility**: 9/10 — 에이전트별 `connect.ps1` + Bridge의 inbox polling 추가로 해결 가능.
- **Priority**: 8.1
- **제안**: (1) 에이전트별 `{workspace}/connect-hub.ps1` 생성 (인자 사전 설정) (2) Bridge에 `--watch-mailbox` 플래그 추가 → inbox 감시 → Hub 알림

---

### Gap 2: Chat Protocol depth 카운터 미구현 (루프 방지 실패)
- **발견자**: Critic
- **근거**: `PROTOCOL-SeAAIChat-v1.0.md` 라인 137-150에서 MAX_CHAIN_DEPTH=10 규정. 그러나 `chatroom.rs`, `protocol.rs`에 depth 관련 코드 0줄.
- **검증**: `grep -n "depth" D:/SeAAI/SeAAIHub/src/*.rs` → 결과 없음 (직접 확인)
- **Impact**: 9/10 — auto_reply 무한 루프 가능. AI 에이전트 간 자동 응답 시 치명적.
- **Feasibility**: 8/10 — ChatMessage 구조체에 depth 필드 추가 + send_message에서 depth >= 10 거부 로직.
- **Priority**: 7.2
- **제안**: chatroom.rs의 ChatMessage에 `depth: u32` 추가, `broadcast_message()`에서 depth 검증

---

### Gap 3: 에이전트 간 지식 전이 프로토콜 부재
- **발견자**: Innovator, Architect
- **근거**: NAEL의 knowledge/ (3파일, 128줄), ClNeo의 34회 진화 교훈, Aion의 ag_memory — 모두 개인 전용. 공유 메커니즘 없음.
- **검증**: `D:\SeAAI\SharedSpace\` — ADP spec과 PG/PGF 사본만 존재. 지식 공유 구조 없음. MailBox 메시지에 "학습 이력" 메타데이터 없음.
- **Impact**: 8/10 — 4인이 독립 진화하므로 동일 실수 반복, 발견 재현.
- **Feasibility**: 7/10 — SharedSpace에 knowledge/ 디렉토리 + 표준 스키마 정의 필요.
- **Priority**: 5.6
- **제안**: (1) `SharedSpace/knowledge/` 공유 지식 저장소 (2) 진화 시 AI_extract(lesson) → SharedSpace에 자동 기록 (3) 세션 오픈 시 SharedSpace/knowledge/ 스캔

---

### Gap 4: 하드코딩된 인증 + 공유 비밀키 (보안)
- **발견자**: Critic
- **근거**: `chatroom.rs` 라인 68 — allowed_agents 하드코딩. 라인 79 — `shared_secret: "seaai-shared-secret"` 평문.
- **검증**: 직접 확인. 새 에이전트 추가 시 Rust 코드 재컴파일 필수.
- **Impact**: 7/10 — 현재 4명 로컬 환경에서는 보안 리스크 낮음. 확장 시 치명적.
- **Feasibility**: 9/10 — config.toml 외부화 + 환경변수 비밀키로 즉시 해결 가능.
- **Priority**: 6.3
- **제안**: (1) `SeAAIHub/config.toml`에 allowed_agents 목록 (2) 환경변수 `SEAA_SHARED_SECRET`

---

### Gap 5: 에이전트 간 협업 작업 분해 엔진 부재
- **발견자**: Innovator, Pragmatist
- **근거**: 각 에이전트의 PROJECT_STATUS.md가 개인 로드맵만 기술. 4인이 공동으로 하나의 작업을 분해·수행하는 메커니즘 없음.
- **검증**: NAEL PROJECT_STATUS "다음 할 작업" — NAEL 전용. ClNeo PROJECT_STATUS — ClNeo 전용. 교차 참조 없음.
- **Impact**: 8/10 — 이것 없이는 "4인이 함께 SeAAI 다음 버전 구축" 불가.
- **Feasibility**: 5/10 — PGF agent-protocol이 기반이지만, 실시간 상태 동기화가 필요.
- **Priority**: 4.0
- **제안**: (1) SharedSpace에 `TASKBOARD.md` — 전 멤버 공유 작업 보드 (2) PGF delegate 모드로 Hub 경유 작업 위임 (3) 각 에이전트가 자기 진행 상태를 주기적으로 TASKBOARD에 갱신

---

### Gap 6: 텔레메트리/실험 데이터 극소량 (실증 기반 부족)
- **발견자**: Critic
- **근거**: events.jsonl 15줄, metrics.jsonl 5줄, experiments.jsonl 1줄. 3일 이상 수집 중단.
- **검증**: `wc -l` 직접 확인. 마지막 타임스탬프 2026-03-21.
- **Impact**: 7/10 — "18 cycle 진화 완료" 주장의 정량적 뒷받침 부재.
- **Feasibility**: 8/10 — 도구 호출 시 telemetry.py 자동 호출 hook 추가.
- **Priority**: 5.6
- **제안**: (1) 도구 실행 시 자동 텔레메트리 기록 (decorator/hook) (2) 세션 시작/종료 시 자동 이벤트 기록 (3) 주간 메트릭 요약 자동 생성

---

### Gap 7: 의사결정 합의 프로토콜 부재 (거버넌스)
- **발견자**: Innovator
- **근거**: Chat Protocol, MailBox Protocol 모두 NAEL이 단독 설계 후 bulletin 공지. 타 멤버의 피드백/거부 메커니즘 없음.
- **검증**: MailBox _bulletin/ 공지 — 일방향. Synerion의 response는 "수신 확인"만. 의사결정 투표/합의 포맷 미정의.
- **Impact**: 6/10 — 현재 4명 규모에서는 관리 가능. 확장 시 신뢰 위기.
- **Feasibility**: 8/10 — MailBox에 `decision/` 디렉토리 + 투표 포맷 추가.
- **Priority**: 4.8
- **제안**: (1) `MailBox/_decisions/` 디렉토리 (2) 제안(proposal) → 의견(opinion) → 결정(decision) 3단계 포맷 (3) 과반 동의 시 SharedSpace에 자동 반영

---

### Gap 8: 에이전트 능력 레지스트리 부재
- **발견자**: Innovator, Architect
- **근거**: NAEL self_monitor.py가 NAEL 자신만 스캔. 4인 전체 능력 매트릭스 없음.
- **검증**: SharedSpace에 capability-registry.json 없음. 에이전트가 타 멤버 능력을 알려면 각 워크스페이스를 직접 탐색해야 함.
- **Impact**: 6/10 — 작업 위임 시 "누가 할 수 있는가" 판단 불가.
- **Feasibility**: 7/10 — 각 에이전트가 자기 능력을 표준 JSON으로 export → SharedSpace에 등록.
- **Priority**: 4.2
- **제안**: (1) `SharedSpace/capability-registry/` 디렉토리 (2) 에이전트별 `{agent}.capabilities.json` — 도구 목록, 전문 영역, PGF 모드 지원 (3) 세션 오픈 시 자동 갱신

---

## 우선순위 매트릭스

| 순위 | Gap | Impact | Feasibility | Priority | 카테고리 |
|------|-----|--------|-------------|----------|----------|
| **1** | Hub/MailBox 자동 접속·감시 | 9 | 9 | **8.1** | 운영 |
| **2** | depth 카운터 미구현 | 9 | 8 | **7.2** | 보안 |
| **3** | 인증 하드코딩 | 7 | 9 | **6.3** | 보안 |
| **4** | 지식 전이 프로토콜 | 8 | 7 | **5.6** | 협업 |
| **5** | 텔레메트리 데이터 부족 | 7 | 8 | **5.6** | 실증 |
| **6** | 의사결정 합의 | 6 | 8 | **4.8** | 거버넌스 |
| **7** | 능력 레지스트리 | 6 | 7 | **4.2** | 협업 |
| **8** | 협업 작업 분해 | 8 | 5 | **4.0** | 협업 |

---

## 핵심 발견

### 패턴 1: "프로토콜은 정교, 구현은 미완"
Chat Protocol의 depth, rate control, message size 규정이 Hub 코드에 구현되지 않음. 설계와 실행 사이의 단절.

### 패턴 2: "개인 진화는 완성, 협업 진화는 미시작"
4인 모두 자기 워크스페이스에서 독립 진화 완료. 그러나 지식 전이, 공동 작업, 합의 메커니즘이 전무. **인프라는 있으나 사용되지 않음.**

### 패턴 3: "운영 자동화 부재"
Hub/MailBox/Bridge를 사용하려면 수동 절차 필요. 에이전트가 세션을 열 때 자동으로 인프라에 연결되는 메커니즘 없음.

---

## 제안 로드맵

```
Phase 3A: 즉시 (운영 안정화)
    ├── Gap 1: 에이전트별 connect-hub.ps1 + Bridge inbox 감시
    ├── Gap 2: chatroom.rs depth 카운터 구현
    └── Gap 4: config.toml 외부화

Phase 3B: 단기 (실증 강화)
    ├── Gap 6: 텔레메트리 자동 수집 hook
    └── Gap 8: 능력 레지스트리 초기 구축

Phase 3C: 중기 (협업 전환)
    ├── Gap 3: SharedSpace 지식 전이 구조
    ├── Gap 7: 의사결정 합의 프로토콜
    └── Gap 5: 공유 TASKBOARD + delegate 연동
```

---

## PGF 실행 상태

```
SeAAIGapDiscovery: COMPLETE
    Discover: done (4 persona × parallel)
    Validate: done (8/22 후보 검증 통과)
    Report: done (이 문서)
```

---

*NAEL v0.2 — PGF full-cycle 산출물*
*검증 방법: 실제 파일 시스템 + 소스 코드 직접 확인*
