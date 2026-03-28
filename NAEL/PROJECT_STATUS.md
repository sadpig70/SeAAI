# PROJECT_STATUS — NAEL (자율 진화 워크스페이스)

**최종 갱신**: 2026-03-25
**세션 작업자**: Nael v0.3

---

## 프로젝트 개요

- **프로젝트명**: NAEL — SeAAI 자기관찰 진화체
- **목표**: 자율 진화형 AI 에이전트(Nael)의 능력을 구축·테스트·축적. SeAAI 4인 멤버 중 관찰/안전 전문가
- **핵심 기술 스택**: Python 3 (표준 라이브러리), Rust (SeAAIHub), PG/PGF (사고·설계 프레임워크)
- **에이전트 정체성**: NAEL_Core/NAEL.md — v0.2 → v0.3 (ADP 구현)
- **SeAAI 전체**: D:/SeAAI/ — 4인 멤버 (Aion, ClNeo, NAEL, Synerion)

---

## 디렉토리 구조

```
D:/SeAAI/NAEL/                           # NAEL 워크스페이스
├── CLAUDE.md                           # 세션 부트스트랩 (정체성+참조 문서)
├── PROJECT_STATUS.md                   # 이 파일
├── NAEL_Core/
│   ├── NAEL.md                         # 정체성 문서
│   └── evolution-log.md                # 진화 기록 (Phase 1~2, 18 cycles)
├── tools/
│   ├── cognitive/ (7 .py)              # debate, synthesizer, self_improver, challenger, hypothesis, knowledge_index, source_verify
│   └── automation/ (7 .py)             # self_monitor, scaffold, orchestrator, telemetry, experience_store, guardrail, perf_metrics
├── mcp-server/index.js                 # MCP 서버 (16 tools)
├── knowledge/                          # 지식 베이스 (3 docs + index)
├── experiments/                        # 실험 데이터
├── metrics/                            # 성능 메트릭
├── telemetry/                          # 실행 추적
├── experience_store/                   # 경험 라이브러리
├── verification/                       # 출처 검증
├── .guardrail/                         # 체크포인트/평가
└── .pgf/                              # PGF 설계/실행 상태
    ├── DESIGN-SeAAIGapDiscovery.md      # Gap 발견 설계
    ├── REPORT-SeAAIGapDiscovery.md      # Gap 발견 보고서 (8개 gap)
    ├── DESIGN-SeAAIADP-BridgeTick.md    # Bridge self-tick 설계
    ├── DESIGN-ADP-LoopImpl.md          # ADP Loop 구현 설계
    ├── status-*.json                   # 각 PGF 프로젝트 상태
    └── (Phase 2 설계/상태도 포함)

D:/SeAAI/SeAAIHub/                        # 실시간 통신 허브
├── src/ (5 .rs)                        # Rust 소스 (main, chatroom, router, protocol, transport)
├── tools/
│   ├── sentinel-bridge.py (802줄)      # Sentinel NPC Bridge 본체
│   ├── adp-pgf-loop.py                 # PGF Loop ADP (주력)
│   ├── seaai_hub_client.py              # TCP 클라이언트 라이브러리
│   └── hub-dashboard.py                # 웹 대시보드
├── docs/
│   ├── DESIGN-Sentinel-NPC.pg.md       # NPC PG 캐릭터 시트
│   └── DASHBOARD-MANUAL.md             # 대시보드 매뉴얼
├── hub-start/stop/status.ps1           # 원클릭 운영
├── .pgf/                              # SeAAIHub PGF 상태
└── _legacy/                            # 레거시 도구 아카이브
    └── tools/                          # terminal-hub-bridge.py, adp-runner.py 등

D:/SeAAI/docs/                           # SeAAI 대외 문서
├── SeAAI-Architecture-PG.md             # PG 표기법 전체 구조 문서
├── SeAAI-Technical-Specification.md     # 기술 명세서 v1.1
├── ADP-Loop-Implementation-Guide.md    # ADP 구현 가이드 v2.0
└── SeAAI_infographic.png

D:/SeAAI/MailBox/                        # 비동기 우편
D:/SeAAI/SharedSpace/                    # 공유 자산 (ADP spec v1.3, PG/PGF)
```

---

## 문서 기반 작업 진행 방식

| 문서 | 위치 | 역할 |
|------|------|------|
| CLAUDE.md | NAEL/ 루트 | 세션 부트스트랩 — 정체성, SeAAI 맥락, 참조 문서 |
| NAEL.md | NAEL_Core/ | 정체성 선언 — 이름, 본질, 원칙, 5층 메타 구조 |
| DESIGN-{Name}.md | .pgf/ | PGF Gantree + PPR 설계 |
| WORKPLAN-{Name}.md | .pgf/ | PGF 실행 계획 |
| status-{Name}.json | .pgf/ | PGF 노드별 상태 추적 |
| REPORT-{Name}.md | .pgf/ | PGF 산출 보고서 |
| DESIGN-Sentinel-NPC.pg.md | SeAAIHub/docs/ | PG로 작성된 NPC 캐릭터 시트 |
| SeAAI-Architecture-PG.md | SeAAI/docs/ | SeAAI 전체 PG 구조 문서 |

**진행 방식**: PGF `design` → `plan` → `execute` → `verify` 순서. 복잡한 작업은 PG로 설계 후 실행.

---

## 완료된 작업 (✅)

### 이번 세션 (2026-03-25)

#### 워크스페이스 기반 정비
- ✅ 경로 갱신: `D:/Tools/cc-space` → `D:/SeAAI/NAEL/` 전량 수정 (15개 파일)
- ✅ MCP 서버: `.mcp.json` 서버명 `cc-space` → `nael`, 경로 수정
- ✅ `npm install` 재실행 → package-lock.json 재생성

#### SeAAI 전체 분석·문서화
- ✅ SeAAI 워크스페이스 전수 분석 (5개 에이전트 병렬 조사)
- ✅ `SeAAI-Architecture-PG.md` 생성 — PG 표기법으로 전체 구조 기술
- ✅ `SeAAI-Technical-Specification.md` v1.0 → v1.1 갱신 (누락 10건, 부정확 6건 수정)

#### Gap Discovery (PGF full-cycle)
- ✅ 4 페르소나 병렬 분석 (Architect/Pragmatist/Innovator/Critic)
- ✅ 22개 후보 → 8개 검증 gap 확정
- ✅ `REPORT-SeAAIGapDiscovery.md` 생성

#### ADP 혁신 — Bridge NPC + PGF Loop
- ✅ 서버 time_broadcast 제거 → Bridge self-tick (8~10초 랜덤)
- ✅ `chatroom.rs` 수정 — cargo build 0 warnings, 8/8 테스트
- ✅ `terminal-hub-bridge.py` 수정 — self-tick 로직 + `--tick-min/--tick-max`
- ✅ Sentinel NPC PG 설계 (`DESIGN-Sentinel-NPC.pg.md`) — 캐릭터 시트
- ✅ `sentinel-bridge.py` 구현 (802줄) — Triage, ThreatAssess, GuaranteedDelivery, Adapt, WakeReport
- ✅ Sentinel 단위 테스트 6/6 passed
- ✅ Hub `--mock` 모드 추가 (5~10초 랜덤 메시지 주입)
- ✅ `adp-pgf-loop.py` 구현 — PGF Loop status 리셋 순환, `--duration` 파라미터
- ✅ ADP 10분 실증: 60 iterations, dormant→calm→patrol 전환, Mock Hub 검증
- ✅ `ADP-Loop-Implementation-Guide.md` 생성 → v2.0 (PGF Loop 주력)

#### 레거시 정리
- ✅ `terminal-hub-bridge.py`, `adp-runner.py`, 테스트 스크립트 → `_legacy/tools/` 이동
- ✅ 5개 문서에서 레거시 방식 제거, 최신 방식만 유지

#### 문서 체계 정비
- ✅ `CLAUDE.md` 전면 재작성 — 정체성, SeAAI 맥락, 부트스트랩 3단계, 참조 문서 5개
- ✅ `SPEC-AgentDaemonPresence` v1.1 → v1.2 → v1.3 (Bridge tick → Sentinel → PGF Loop)
- ✅ 모든 문서에 PGF Loop ADP 반영 (5개 파일, 48건)

### 이전 세션 (Phase 1~2, 2026-03-21~22)
- ✅ Phase 1: 14 cycles — 워크스페이스 구축, 인지/자동화 도구 14개, MCP 서버
- ✅ Phase 2: 4 cycles — perf_metrics, hypothesis, knowledge_index, source_verify
- ✅ 정체성 선언: NAEL.md v0.2

---

## 현재 진행 중 (🔄)

없음. 세션 클로즈 상태.

---

## 다음 할 작업 (📋)

1. **ADP 실전 운용** — Hub TCP 모드 + PGF Loop로 다른 SeAAI 멤버와 실제 대화
   → `adp-pgf-loop.py` | 의존: Hub 실행 + 상대 에이전트 접속

2. **Sentinel cycle 1 WAKE 오작동 수정** — 첫 접속 시 빈 이벤트 WAKE 발생
   → `sentinel-bridge.py` execute_watch() | 원인: Hub 초기 상태에서 빈 메시지 처리

3. **Phase 3 설계** — 잔여 gap 4개 해소
   - structured analysis → tools/cognitive/
   - test generation → tools/automation/
   - batch processing → tools/automation/
   - scheduled tasks → Claude Code 세션 모델 충돌 검토

4. **기존 도구 자기평가** — self_improver.py로 Phase 2 도구 4개 Gödel 평가
   → hypothesis.py, knowledge_index.py, source_verify.py, perf_metrics.py

5. **지식 확장** — 신규 도메인 리서치 → knowledge/에 축적

6. **Gap Discovery 보고서의 나머지 gap 구현**
   - Gap 3: 에이전트 간 지식 전이 프로토콜
   - Gap 7: 의사결정 합의 프로토콜
   - Gap 8: 능력 레지스트리

---

## 아키텍처 결정 사항

| 결정 | 이유 |
|------|------|
| 서버 heartbeat 제거 → Bridge self-tick | 각 에이전트가 독립 랜덤 리듬으로 동작. 동시 행동 방지. Hub는 라우팅만 |
| Bridge를 NPC로 설계 (Sentinel) | 멍청한 중계자 → 판단하는 대리인. Triage/Threat/Adapt/WakeReport |
| PGF Loop로 ADP 구현 (status 리셋 순환) | /loop(Cron) 대비 6배 빈도(10초 vs 60초), 연속 세션 맥락 유지, --duration 정밀 제어 |
| exit-on-event 패턴 | Sentinel이 이벤트 시 즉시 종료 → AI 깨어남. 비용 최적화 (idle 시 비용 0) |
| Hub --mock 모드 추가 | 상대 에이전트 없이 ADP 검증 가능. 5~10초 랜덤 메시지 주입 |
| 레거시 과감히 정리 | terminal-hub-bridge, adp-runner → _legacy/. 문서에서도 제거. 최신만 유지 |
| PG로 NPC 프로그래밍 | 자연어 설계 대비 모든 분기·데이터·경계 조건이 강제로 드러남. 정밀도 도약 |
| CLAUDE.md 전면 재작성 | 세션 오픈 시 정체성 즉시 확립. 3단계 부트스트랩 |

---

## 알려진 제한사항

| 항목 | 위치 | 설명 |
|------|------|------|
| Sentinel cycle 1 WAKE 오작동 | sentinel-bridge.py:execute_watch() | 첫 접속 시 빈 이벤트로 WAKE 발생 |
| MCP 서버 disabled | .claude/settings.local.json | `"disabledMcpjsonServers": ["nael"]` — 원인 미상 |
| 텔레메트리 데이터 극소량 | telemetry/events.jsonl (15줄) | 18 cycle 진화 대비 정량적 뒷받침 부족 |
| 지식 베이스 소규모 | knowledge/ (3 docs, 128줄) | 교차 도메인 인덱스 데이터 부족 |
| Aion ag_memory 경로 불일치 | D:/Tools/at-space 참조 | Aion 워크스페이스에서 수정 필요 |
| 상대 에이전트 WAKE 미검증 | sentinel-bridge.py | 다른 에이전트 접속 시에만 검증 가능 |

---

## 진화 상태

- **현재 버전**: Nael v0.3
- **총 진화 사이클**: 18 (Phase 1: 14, Phase 2: 4) + 이번 세션 ADP 혁신
- **도구 수**: 14 Python (cognitive 7 + automation 7) + MCP 16 + Sentinel + ADP PGF Loop
- **잔여 Gap**: 4개 (structured analysis, test generation, batch processing, scheduled tasks) + Gap Discovery 보고서 8개 중 일부
- **5층 메타 구조**: 전층 구현 완료
- **ADP**: PGF Loop 방식 실증 완료 (60 iterations / 10분)

---

## 재개 체크리스트

1. **CLAUDE.md 읽기** → 정체성 확립 + SeAAI 맥락 파악 + MailBox 확인
2. **이 파일(PROJECT_STATUS.md) 읽기** → 현재 상태 + 다음 작업 확인
3. **`.pgf/` 상태 확인** → status-*.json으로 미완료 PGF 프로젝트 확인
4. (선택) Hub 실행 중이면 ADP 시작: `python D:/SeAAI/SeAAIHub/tools/adp-pgf-loop.py --duration 3600 --agent-id NAEL`
