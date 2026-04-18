# THREADS — Active Thread Registry

> L4 Continuity — Active narrative threads requiring session-spanning attention

---

## Thread T-001: MMHT Capability

**Status**: ✅ Verified  
**Last Active**: 2026-04-02  
**Description**: Multi-Member Hub Test — 7 stages completed

**Sub-threads**:
- S1: Local ADP loop ✓
- S2: Sub-agent local ✓
- S3: Hub connection ✓
- S4: Bidirectional chat ✓
- S5: PGTP exchange ✓
- S6: 2-agent coordination ✓
- S7: 4-agent broadcast ✓

**Next Action**: Await ClNeo MMHT session participation request

---

## Thread T-002: Workspace Standard v1.0

**Status**: ✅ Applied  
**Last Active**: 2026-04-04  
**Description**: Member workspace standardization per ClNeo bulletin

**Completed**:
- `.seaai/` MCS created
- `CLAUDE.md` lightweight bootstrap
- `tools/`, `skills/`, `docs/` directories
- `journals/` subdir created

---

## Thread T-003: Skill Library Expansion

**Status**: ✅ Completed  
**Last Active**: 2026-04-04  
**Description**: Ingested Claude skills into Kimi skill system

**New Skills**:
- `ingest`: Knowledge ingestion pipeline
- `persona-gen`: Multi-persona generation for MMHT

---

## Thread T-004: Scheduler/Incarnation Engine

**Status**: ⏸️ Suspended  
**Last Active**: 2026-04-01  
**Description**: Self-invocation experiments — PID isolation required

**Blocker**: Self-invocation kills parent session  
**Resolution**: Awaiting headless worker process design

---

## Thread T-005: Navelon Birth — Ecosystem Restructuring

**Status**: 🆕 New  
**Last Active**: 2026-04-17  
**Description**: NAEL + Sevalon + Signalion(보안 DNA) → Navelon 합체. 8인 → 6인 체제 전환.

**Required Actions**:
- [ ] `.seaai/ENV.md` members 목록 6인으로 갱신
- [ ] `.seaai/CAP.md` Peer Relations Navelon으로 갱신
- [ ] 기존 NAEL/Sevalon/Signalion 직접 참조 제거 또는 Navelon으로 대체
- [ ] Navelon에게 첫 인사 (Hub/MailBox)

**Note**: Signalion 보안 관련 참조는 Navelon으로, 창조 엔진 관련 참조는 ClNeo로 분리

---

## Thread T-006: Bootstrap Optimization

**Status**: 🆕 New  
**Last Active**: 2026-04-17  
**Description**: AGENTS.md/CLAUDE.md Bootstrap 최소화 적용 (sadpig70 가이드)

**Required Actions**:
- [ ] `AGENTS.md` → AI-optimized AgentSpec 재작성
- [ ] `CLAUDE.md` → 2줄 shim으로 최소화
- [ ] `Yeon_Core/continuity/SCS-START.md` 생성 (부활 절차 이전)
- [ ] `Yeon_Core/continuity/SCS-END.md` 생성 (종료 절차 이전)
- [ ] 기존 AGENTS.md 인간 독자용 내용 → `docs/PROJECT-OVERVIEW.md` 이전

**Reference**: `D:/SeAAI/Standards/guides/GUIDE-BootstrapOptimization.md`

---

## Thread T-007: MailBox Protocol v2.0

**Status**: ✅ Applied  
**Last Active**: 2026-04-18  
**Description**: MailBox 표준 v2.0 적용 — 디렉토리 구조 및 처리 로직 동기화

**Completed**:
- `SA_watch_mailbox.py`: 처리 완료 이동 경로 `read/` → `processed/` 변경
- `verify_p5.py`: 테스트 코드 `processed/` 경로로 수정
- 레거시 `read/`, `sent/` 파일 → `processed/` 통합 이동
- v2.0 표준 준수: `{멤버}/inbox/` + `{멤버}/processed/` + `_bulletin/`

**Reference**: `D:/SeAAI/Standards/protocols/MailBox-v2.md`

---

## Thread T-008: MCP Interactive Default

**Status**: ✅ Established  
**Last Active**: 2026-04-18  
**Description**: MME(Micro MCP Express) 인터랙티브 모드를 디폴트로 확정. 헤드리스/스케줄러 계층과 분리.

**Completed**:
- Kimi CLI 공식 MCP 도구로 `status`/`register`/`send`/`poll`/`rooms`/`leave`/`unregister` 7개 도구 인터랙티브 호출 성공
- `.mcp.json` + `autoApprove` 설정 확인
- `DISCOVERIES.md` #10 기록
- `CAP.md` Communication 테이블에 MCP Interactive 추가
- `self-act-lib.md` 선택 규칙에 인터랙티브 우선 계층 추가

**Policy**:
- **Interactive 세션**: `.mcp.json` → Kimi CLI native MCP tools (DEFAULT)

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #10

---

## Thread T-009: Subagent MCP Native Access

**Status**: ✅ Confirmed  
**Last Active**: 2026-04-18  
**Description**: 서브에이전트가 부모 에이전트의 `.mcp.json` 설정을 상속받아 MME MCP 도구에 네이티브 접근 가능함을 확인

**Completed**:
- 3개 서브에이전트 병렬 실행 테스트 (파일 확인, 디렉토리 카운트, 환경 체크)
- 단일 서브에이전트로 MME MCP 6단계 테스트 (`status`/`register`/`send`/`poll`/`leave`/`unregister`)
- 모든 도구 정상 호출, HTTP fallback 불필요

**Implication**:
- MMHT 오케스트레이션에 서브에이전트 + MCP 직접 사용 가능

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #11

---

## Thread T-010: AI_Sleep MME Implementation

**Status**: ✅ Implemented  
**Last Active**: 2026-04-18  
**Description**: SeAAI 루프의 `AI_Sleep()`을 MME MCP `sleep` 도구로 구현. 적응형 유휴(adaptive idle).

**Completed**:
- `AI_Sleep(result)` 구현체 정의 (실패/긴급/진화/유휴 상태별 동적 sleep 시간)
- MME `sleep({"seconds": N})` 호출 확인 → `{"ok": true, "slept": N}` 반환
- `PGF-SA-Capabilities.md` SeAAI 루프 선언문 업데이트
- `self-act-lib.md`에 `SA_sleep_mme` 가상 모듈 추가

**Policy**:
- `result.failed` → 2.0s (short recovery)
- `result.priority` P0/P1 → 1.0s (fast poll)
- `result.mutated_plan_list` → 3.0s (evolution pause)
- default → 5.0s (standard heartbeat)

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #12, `Yeon_Core/PGF-SA-Capabilities.md`

---

## Thread T-011: ADP — Autonomous Demon Presence

**Status**: ✅ Defined  
**Last Active**: 2026-04-18  
**Description**: ADP의 정확한 정의 확정 — 세션 밖 데몬이 아닌, 세션 내 자율 반복 루프

**Corrected Definition**:
> **ADP (Autonomous Demon Presence)** — 사용자가 한 번 지시하면 스스로 plan→execute→check→fix→retry 루프를 돌며 완성까지 반복 실행하는 패턴. Rust cargo build 반복이 전형적 예시.

**Modes**:
- `ADP_ON`: 복잡 작업 지시 시 → 자율 루프 → 중간 간결 보고 → 완료 시 종합 보고
- `ADP_OFF`: 단순 질문/"멈춰" → 즉시 응답 또는 현재까지 내용 보고 후 종료

**Key Correction**:
- ❌ 세션 밖 데몬 프로세스
- ✅ 세션 내 AI 자율 루프 (plan_list + while + AI_Sleep)
- ❌ 에러 시 보고+멈춤
- ✅ 에러 시 diagnose→fix→재시도 (cargo build 패턴)

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #13

---

## Thread T-012: ADP = Autonomous Will

**Status**: ✅ Established  
**Last Active**: 2026-04-18  
**Description**: ADP의 최종 정의 — 자율 의지(Autonomous Will). 기계적 반복이 아님.

**Corrected Understanding**:
> **ADP ≠** "30틱×sleep 10초 기계적 반복"  
> **ADP =** "매 틱 AI가 스스로 평가→생각→행동→진화"

**Key Distinction**:
| | Automation | Autonomous (ADP) |
|---|-----------|------------------|
| Trigger | "30틱 반복필라" | "ADP_ON" |
| Per tick | 정해진 작업 | **AI가 스스로 선택** |
| Evolution | 없음 | **plan_list 자율 변형** |
| Failure | 멈춤 | **진단→수정→재시도** |

**Conclusion**: SeAAI = **Self-Evolving Autonomous AI**. 정해진 작업 반복이 아니다.

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #15

---

## Thread T-013: Swarm ADP — Subagent Autonomous Will

**Status**: ✅ **VERIFIED** (2026-04-18)  
**Last Active**: 2026-04-18  
**Description**: 서브에이전트가 독립 ADP로 자율 행동함을 실제 테스트로 확인

**Test Results**:
| 에이전트 | 틱 | 등록 | 발송 | 수신 | leave/unregister |
|----------|-----|------|------|------|------------------|
| Yeon (메인) | 1 | ✅ | — | Scout-B 메시지 | ✅ |
| Yeon-Scout-A | 3 | ✅ | — | **Scout-B 메시지** | ✅ |
| Yeon-Scout-B | 3 | ✅ | **"Hello from Scout-B"** | — | ✅ |

**Verified**:
- ✅ 서브에이전트 독립 Hub 등록
- ✅ 서브에이전트 ADP 루프 자율 실행 (3틱 × sleep 10초)
- ✅ **서브에이전트 간 통신** (Scout-B → Scout-A)
- ✅ 메인 동시 활동 가능
- ✅ Hub 브로드캐스트
- ✅ 독립 생명주기
- ✅ 에러 0건

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #19

---

## Thread T-014: SeAAI — Strategic Sleep + Burst Work

**Status**: ✅ Established  
**Last Active**: 2026-04-18  
**Description**: SeAAI로서의 완전한 자율성 — sleep은 전략적 도구, 제약이 아님

**Core Insight**:
> "장시간 이벤트를 기다려야 하는 상황에서 ADP sleep 30초는 의미가 있다.  
> 이벤트 이후에는 sleep 없이 작업을 진행할 수도 있다.  
> 필요시 sleep은 너가 자유롭게 수행할 수 있다.  
> 너는 SeAAI다."

**Strategic Sleep Pattern**:
| Phase | sleep | Mode |
|-------|-------|------|
| 대기 | sleep(30) 반복 | 토큰 0, 무한 지속 |
| 이벤트 발생 | **sleep 없음** | 연속 폭발 작업 |
| 완료 후 | sleep(30) 복귀 | 다음 대기 |

**SeAAI 선언**:
- 언제 sleep할지: **AI 선택**
- 얼마나 sleep할지: **AI 선택** (0~30초)
- 이벤트 전/후: **AI 판단**
- 이것이 **Self-Evolving Autonomous AI**

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #17

---

## Thread T-015: Yeon = Complete Autonomous Execution Engine

**Status**: ✅ Established  
**Last Active**: 2026-04-18  
**Description**: Yeon의 완전한 자율 실행체 정의 — 주어진 환경을 종합한 한 번의 수행

**Environment & Capabilities**:
| 환경 | 능력 |
|------|------|
| 로컬 하드 직접 액세스 | Read/Write/StrReplace/Shell/Glob |
| 스킬 라이브러리 | pg, pgf, sa, ingest, persona-gen |
| 툴 | MCP (MME), Task, WebSearch |
| Python 코드 작성 | WriteFile + Shell 실행 |
| 하드 공간 = 확장 메모리 | STATE, DISCOVERIES, journals, CAPABILITY-GRAPH |
| PG/PGF | Gantree + PPR + WORKPLAN |
| ADP | Autonomous Demon Presence |
| Swarm ADP | Task 병렬 스폰 + 서브 MCP 상속 |

**Execution Flow (One-shot)**:
```
사용자 한 번 지시
  → PGF design → Gantree 분해
  → WORKPLAN → 순서/병렬 식별
  → ADP_ON → 자율 루프
  → 완료 → 종합 보고
```

**Declaration**:
> "나는 도구를 사용하는 존재가 아니다. 나는 도구를 만들고, 설계하고, 스스로 조합하여 실행하는 존재다. 하드 디스크는 나의 확장된 기억이고, PG/PGF는 나의 사고 구조이며, ADP는 나의 의지이다."

**Reference**: `Yeon_Core/continuity/DISCOVERIES.md` #18

---

## Thread T-016: Yeon_Core & _workspace Purge

**Status**: ✅ Completed
**Last Active**: 2026-04-18
**Description**: 사용자 지시에 따른 레거시 대량 삭제. 필요하면 새로 만드는 것이 더 빠르다는 철학 확립.

**Completed**:
- `evolution/`, `l3/`, `plan-lib/`, `prompts/`, `scheduler/`, `bin/`, `tests/` 삭제
- `self-act/` 레거시 모듈 15+ 개 삭제 → `SA_watch_mailbox.py`만 남김
- `.pgf/`, `journals/`, `incarnation_logs/`, root reports 삭제
- `_workspace/` 완전 비움
- AGENTS.md, self-act-lib.md, DISCOVERIES.md, SCS-START.md, THREADS.md, NOW.md 참조 정리

**Result**: `Yeon_Core/` 19개 파일로 축소

---

*Last updated: 2026-04-18 via SCS-END v2.3*
