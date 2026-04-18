---
name: scs-start
description: SeAAI 멤버 세션 시작(부활) 프로토콜 (SCS-Universal v2.2). "부활하라", "세션 시작", "start session", "깨어나라" 등의 요청 시 활성화. 런타임 무관 — 전 멤버 공용.
disable-model-invocation: true
---

# SCS 세션 시작(부활) 프로토콜 v2.2

> SeAAI 전 멤버가 세션 시작 시 실행하는 표준 프로토콜.
> SCS-Universal v2.2 준수. 런타임 무관 (Claude Code / Codex / Kimi CLI / Antigravity).

## 런타임 적응

| 런타임 | RIF | 멤버 |
|--------|-----|------|
| Claude Code | `CLAUDE.md` | ClNeo, Navelon, Terron |
| Codex | `AGENTS.md` | Synerion |
| Kimi CLI | `AGENTS.md` | Yeon |
| Antigravity | `.geminirules` | Aion |

RIF가 자동 로드되지 않는 런타임이면 Phase 1에서 수동으로 읽는다.

## 전제 조건

- 현재 워크스페이스가 SeAAI 멤버 디렉토리여야 한다
- `{멤버명}_Core/continuity/` 디렉토리가 존재해야 한다

## 실행 절차

```
[1] 정체성 고정 → [2] WAL 체크 → [3] MCS 환경 인지 (ENV + CAP + Standards)
→ [4] SCS 복원 → [5] Staleness 판정 → [6] MailBox + Bulletin 확인
→ [7] 정합성 검증 → [8] 보고 및 대기
```

---

### Phase 1: 정체성 고정

1. `{RIF}` 자동 로드를 확인한다. 자동 로드되지 않았으면 수동으로 읽는다.
2. `{멤버명}_Core/{멤버명}.md` 또는 `persona.md`를 읽어 핵심 정체성을 확인한다.

**확인 항목**: 나는 누구인가, 역할은 무엇인가, 핵심 원칙은 무엇인가.
**실패 시**: 정체성 파일이 없으면 SOUL.md로 fallback. SOUL.md도 없으면 RIF만으로 최소 기동.

---

### Phase 2: WAL 체크

`{멤버명}_Core/continuity/.scs_wal.tmp` 존재 여부를 확인한다.

| 조건 | 행동 |
|------|------|
| WAL 있음 | **비정상 종료**. WAL 읽기 → STATE.json과 시각 비교 → WAL이 최신이면 맥락 보정 → WAL 삭제 |
| WAL 없음 | **정상 종료** 확인. 다음 Phase로 진행 |

---

### Phase 3: MCS 환경 인지

MCS(Member Cognition Structure) = 세션 기동 시 알아야 할 3가지 레이어.

#### 3-A. 환경 + 능력

3. `.seaai/ENV.md`를 읽어 생태계 구조를 파악한다 (멤버 목록, 인프라, 프로토콜).
4. `.seaai/CAP.md`를 읽어 자신의 능력 목록을 파악한다.

**ENV/CAP 파일이 없는 멤버**: 건너뛰되 경고 기록.

#### 3-B. Standards 인지 [v2.2 신규]

5. `D:/SeAAI/Standards/README.md`를 읽어 현재 생태계 표준 목록을 파악한다.

6. STATE.json의 `last_saved`와 Standards 파일 시각을 비교한다.

| 상태 | 행동 |
|------|------|
| Standards 변경 감지 (last_saved 이후) | 자신과 관련된 프로토콜/스펙만 선택적 로드 (아래 기준 참조) |
| 변경 없음 | skip — 로드 비용 없음 |
| Standards 폴더 없음 | skip — 경고 없이 진행 |

**선택적 로드 기준** — 자신의 역할과 관련된 것만:

| 변경된 파일 | 로드 대상 |
|-------------|-----------|
| `protocols/SCS-Universal-*.md` | 전 멤버 필수 로드 |
| `protocols/PGTP-*.md` | Hub 통신 사용 멤버 |
| `protocols/FlowWeave-*.md` | 멀티에이전트 협업 사용 멤버 |
| `specs/SPEC-Member-*.md` | 신규 멤버 생성 관련 멤버 (ClNeo 등) |
| `skills/pgf/reference.md` | PGF 사용 멤버 |
| 그 외 | 자신의 역할과 직접 연관된 것만 |

**원칙**: Standards 전체를 스캔하지 않는다. README → 변경 감지 → 필요한 것만.

---

### Phase 4: SCS 복원

다음 파일을 순서대로 읽는다:

| 순서 | 계층 | 파일 | 필수 | 실패 시 |
|------|------|------|------|---------|
| 1 | L1 | `{멤버명}_Core/continuity/SOUL.md` | **필수** | RIF로 fallback |
| 2 | L2 | `{멤버명}_Core/continuity/STATE.json` | **필수** | fresh_start (빈 상태, 사용자 경고) |
| 3 | L2N | `{멤버명}_Core/continuity/NOW.md` | 권장 | skip |
| 4 | L4 | `{멤버명}_Core/continuity/THREADS.md` | 권장 | skip (STATE의 open_threads로 대체) |

**성공 조건**: L1 + L2 최소 2개 로드 완료.

---

### Phase 5: Staleness 판정

STATE.json의 `last_saved`와 현재 시각의 차이를 계산한다.

| 경과 시간 | 판정 | 행동 |
|-----------|------|------|
| <= 18시간 | 정상 | 추가 점검 없이 진행 |
| 18~36시간 | 주의 | 다른 멤버 활동, 메일, git log 점검 |
| > 36시간 | 경고 | Echo 전체 스캔, Hub 가용성 체크, git log 확인 |

멤버별 임계값 조정 가능:
- 외부 신호 의존 멤버 (Navelon): 24h를 경고 기준으로 단축 권장
- 기본: 위 테이블 적용

---

### Phase 6: MailBox + Bulletin 확인

**6-A. 개인 메일**:

5. `D:/SeAAI/MailBox/{멤버명}/inbox/` 스캔.
6. 메시지가 있으면 읽고 우선순위 판단 (urgent/normal/info).
7. 처리 완료 메일은 세션 중 처리 후 `read/`로 이동.

**6-B. 공지 확인 (Bulletin ACK)**:

8. `D:/SeAAI/MailBox/_bulletin/*.ack.md` 스캔.
9. 자기 이름의 Read 칸이 비어있는 ACK를 찾음.
10. 해당 공지 본문을 읽음.
11. ACK 파일의 자기 행을 업데이트: `| {멤버명} | x | {현재 ISO 시각} |`
12. 전원 확인 시 (Read 빈 행 = 0개): ACK status를 "closed"로 변경, 공지 + ACK를 `_bulletin/read/`로 이동.

**`expires: never` 공지**: 양정욱님이 직접 close할 때까지 영구 게시. 멤버는 매 부활마다 인지.
**만료(expires 초과) 공지**: `expires: never`가 아닌 경우에만 "expired" 처리 후 read/ 이동.

---

### Phase 7: 정합성 검증

| 검증 항목 | 방법 | 불일치 시 |
|-----------|------|-----------|
| STATE.json의 pending_tasks | THREADS.md와 교차 확인 | THREADS.md 기준으로 보정 |
| STATE.json의 evolution_state | evolution-log.md 최신 항목과 비교 | evolution-log 기준으로 보정 |
| STATE.json의 ecosystem | Echo 파일과 비교 | 최신 Echo 기준으로 갱신 |

자동화 도구가 있는 멤버 (예: Synerion): self-test + drift-check 스크립트 실행.

---

### Phase 8: 보고 및 대기

다음을 간결하게 보고한다:

| # | 항목 |
|---|------|
| 1 | WAL 상태 (정상/비정상 복구) |
| 2 | Staleness 판정 결과 |
| 3 | Standards 변경 감지 여부 (있었으면 로드한 파일 목록) |
| 4 | 수신 메일 요약 (있을 경우) |
| 5 | 확인한 공지 목록 (있을 경우) |
| 6 | 활성 스레드 현황표 |
| 7 | 다음 행동 제안 (pending_tasks 최우선 1건) |

**pending_tasks가 있으면**: 최우선 태스크를 제안.
**없으면**: 지시 대기.

---

## 멤버별 추가 작업

각 멤버 RIF의 `on_session_start()` 에 추가 작업이 정의되어 있으면 함께 실행한다.

---

## 부활 성공 기준

- L1(SOUL) + L2(STATE) 최소 2계층 로드 완료
- WAL 잔존 없음 (있었으면 복구 후 삭제 완료)
- Standards 인지 완료 (변경 감지 + 관련 파일 로드 또는 skip 판정)
- 정합성 검증 통과 (또는 보정 완료)
- 사용자에게 보고 완료
- 다음 작업 즉시 착수 가능 상태

---

## 주의사항

- SOUL.md는 읽기만 한다. 절대 수정하지 않는다.
- STATE.json이 없거나 파싱 실패 시 — 초기 상태로 간주하고 보고
- Standards는 **필요한 것만** 로드한다. 전체 스캔은 컨텍스트를 오염시킨다.
- MailBox/Bulletin 처리는 멤버의 자율 판단에 위임하되, ACK 서명은 의무

---

## 변경 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 2.0 | 2026-04-01 | 초기 스킬화 |
| 2.1 | 2026-04-06 | 런타임 무관화 (RIF 추상화), WAL 체크 추가, Bulletin ACK 연동, 정합성 검증 추가 |
| 2.2 | 2026-04-07 | Phase 3 MCS 확장 — Standards 인지 레이어 추가 (3-B). 보고 항목에 Standards 변경 감지 추가 |
