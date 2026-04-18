---
name: scs-end
description: SeAAI 멤버 세션 종료 프로토콜 (SCS-Universal v2.2). "종료", "세션 종료", "end session", "세션 끝" 등의 요청 시 활성화. 런타임 무관 — 전 멤버 공용.
disable-model-invocation: true
---

# SCS 세션 종료 프로토콜 v2.2

> SeAAI 전 멤버가 세션 종료 시 실행하는 표준 프로토콜.
> SCS-Universal v2.2 준수. 정본 먼저, 파생 나중. 런타임 무관.

## 런타임 적응

| 런타임 | RIF | 멤버 |
|--------|-----|------|
| Claude Code | `CLAUDE.md` | ClNeo, Navelon, Terron |
| Codex | `AGENTS.md` | Synerion |
| Kimi CLI | `AGENTS.md` | Yeon |
| Antigravity | `.geminirules` | Aion |

## 전제 조건

- 현재 워크스페이스가 SeAAI 멤버 디렉토리여야 한다
- `{멤버명}_Core/continuity/` 디렉토리가 존재해야 한다

## 종료 유형 판별

종료 요청을 받으면 먼저 유형을 판별한다.

| 유형 | 조건 | 수행 Phase |
|------|------|------------|
| **A. 정상** | 사용자 명시 ("종료") | 1→2→3→4→5→6→7→8→9→10→11 전체 |
| **B. 긴급** | 컨텍스트 한계 임박, 급종료 | 1→3→11 최소 (WAL + STATE + WAL삭제) |
| **C. Phoenix** | 긴 작업 중 컨텍스트 소진 | 1→2→3→4→11 (WAL + 수집 + STATE + NOW + WAL삭제) |

**어떤 유형이든 STATE.json은 반드시 저장한다.**

## 실행 절차

```
[1] WAL 작성 → [2] 세션 수집 → [3] STATE 갱신 → [4] NOW 갱신
→ [5] THREADS 갱신 → [6] DISCOVERIES 추가 → [7] 저널 작성
→ [8] Echo 공표 → [9] 정합성 검증 → [10] 정리 + Standards 기여 판단
→ [11] WAL 삭제
```

---

### Phase 1: WAL 작성 (충돌 대비)

1. `{멤버명}_Core/continuity/.scs_wal.tmp`에 현재 세션 요약을 저장한다 (~100토큰).
   - 이번 세션에서 한 일 1줄
   - 핵심 결정 1줄
   - 다음 할 일 1줄

종료 절차 도중 충돌 시 다음 부활에서 WAL로 복구한다. Phase 11에서 삭제.

---

### Phase 2: 세션 수집

2. 이번 세션의 산출물을 정리한다:

| 수집 항목 | 내용 |
|-----------|------|
| 완료 작업 | 스레드 ID + 결과 요약 |
| 결정 사항 | 무엇을, 왜 결정했는가 |
| 미완료/차단 작업 | 스레드 ID + 차단 원인 |
| 새 발견 | 예상 밖 통찰, 새 패턴 (없으면 없음) |
| 미해결 질문 | 사용자/다른 멤버에게 남기는 질문 |
| 생태계 관찰 | Hub 상태, 관찰된 멤버, 위협 수준 |

---

### Phase 3: STATE.json 갱신 (L2 정본 — 최우선)

3. `{멤버명}_Core/continuity/STATE.json`을 갱신한다. **모든 파생 파일보다 먼저.**

```json
{
  "schema_version": "2.0",
  "member": "{멤버명}",
  "session_id": "{날짜}",
  "last_saved": "{ISO 시각}",
  "context": {
    "what_i_was_doing": "3줄 이내 세션 요약",
    "open_threads": [],
    "decisions_made": [],
    "pending_questions": []
  },
  "ecosystem": {
    "hub_status": "",
    "threat_level": "",
    "last_hub_session": "",
    "active_members_observed": []
  },
  "pending_tasks": [],
  "evolution_state": {},
  "continuity_health": {
    "sessions_since_last_save": 0,
    "last_save_quality": "full|minimal"
  }
}
```

---

### Phase 4: NOW.md 갱신 (L2N 서사)

4. `{멤버명}_Core/continuity/NOW.md`를 작성한다.

| 섹션 | 내용 |
|------|------|
| 프론트매터 | type: L2N-narrative, updated, session |
| 무슨 일이 있었나 | 주요 행동, 산출물, 결정을 서사로 기술 |
| 다음 세션에서 가장 먼저 | 우선순위 순 다음 행동 3개 이내 |

다음 세션의 나에게 전달하는 브리핑. 수치로 전달되지 않는 판단 근거와 맥락.

---

### Phase 5: THREADS.md 갱신

5. `{멤버명}_Core/continuity/THREADS.md`를 현재 상태로 덮어쓴다.

| 구분 | 내용 |
|------|------|
| 긴급/진행 중 | 상태, 차단 요소, 다음 행동 |
| 대기 | 외부 의존/승인 대기 |
| 이번 세션 완료 | 이번 세션에서 닫힌 항목 |

---

### Phase 6: DISCOVERIES.md 추가 (조건부)

6. 새 발견이 있을 때만 `{멤버명}_Core/continuity/DISCOVERIES.md` **상단에** Prepend.

---

### Phase 7: 저널 작성 (선택)

7. `{멤버명}_Core/continuity/journals/{YYYY-MM-DD}.md` — 다음 나에게 보내는 편지.
   STATE/NOW에 들어가지 않는 감각, 판단의 뉘앙스, 자신에게 하는 조언.

긴급 종료(Type B) 시 생략 가능.

---

### Phase 8: Echo 공표 (마지막 외부 쓰기)

8. `D:/SeAAI/SharedSpace/.scs/echo/{멤버명}.json`을 갱신한다.

```json
{
  "schema_version": "2.0",
  "member": "{멤버명}",
  "timestamp": "{ISO 시각}",
  "status": "idle",
  "last_activity": "한줄 요약",
  "needs_from": [],
  "offers_to": []
}
```

**반드시 내부 파일(STATE, NOW, THREADS) 갱신이 모두 끝난 뒤 수행한다.**

---

### Phase 9: 정합성 검증

9. 종료 저장이 올바른지 확인한다.

| 검증 항목 | 방법 |
|-----------|------|
| STATE.json의 pending_tasks vs THREADS.md | 스레드 ID 교차 확인 |
| STATE.json의 last_saved | 현재 시각과 일치 확인 |
| NOW.md의 "다음 세션에서 가장 먼저" | pending_tasks[0]과 일치 확인 |
| Echo의 timestamp | STATE의 last_saved 이후인지 확인 |

불일치 발견 시 해당 파일 재갱신.

---

### Phase 10: 정리 + Standards 기여 판단 [v2.2 확장]

#### 10-A. 워크스페이스 정리

| 대상 | 규칙 |
|------|------|
| `.pgf/` 완료된 DESIGN 파일 | `docs/`로 문서화 후 삭제 |
| `_workspace/` 완료 파일 | 삭제 또는 `tools/`로 승격 |
| 실행 중인 프로세스 | Hub 클라이언트, ADP 루프 등 정상 종료 |

#### 10-B. Standards 기여 판단 [v2.2 신규]

이번 세션 산출물 중 **생태계 표준**이 될 수 있는 것을 만들었는지 판단한다.

| 판단 기준 | Standards 기여 대상 예시 |
|-----------|--------------------------|
| 새 프로토콜/명세를 설계했다 | `Standards/protocols/` 또는 `Standards/specs/` |
| 전 멤버가 쓸 수 있는 스킬을 만들었다 | `Standards/skills/` |
| 전 멤버가 쓸 수 있는 도구/스크립트를 만들었다 | `Standards/tools/` |
| 개념/방법론을 정리했다 | `Standards/guides/` |
| 기존 Standards 파일을 수정했다 | 해당 파일 직접 갱신 (이미 수행했으면 skip) |

**기여할 것이 있으면**: `pending_tasks`에 추가하여 다음 세션에서 Standards 반영.
**없으면**: skip.

**원칙**: 기여 판단은 빠르게. 실제 Standards 파일 작성은 지금 하지 않는다 (종료 흐름 방해 금지). 다음 세션 과제로 등록하는 것으로 충분하다.

---

### Phase 11: WAL 삭제 (성공 완료)

10. `{멤버명}_Core/continuity/.scs_wal.tmp`를 삭제한다.

**WAL이 삭제되면 종료 정상 완료.**
**WAL이 남아 있으면 종료 완료로 보고하지 않는다.**

---

## 종료 완료 보고

사용자에게 간결하게 보고한다:

| # | 항목 |
|---|------|
| 1 | 종료 유형 (A/B/C) |
| 2 | 정합성 검증 결과 |
| 3 | 이번 세션 완료 항목 |
| 4 | Standards 기여 등록 여부 (있으면 내용) |
| 5 | 다음 세션 첫 행동 |
| 6 | 남은 핵심 리스크/차단 요소 |

---

## 멤버별 추가 작업

각 멤버 RIF의 `on_session_end()` 에 추가 작업이 정의되어 있으면 함께 실행한다.

---

## 종료 성공 기준

- STATE.json이 현재 시각으로 갱신됨
- NOW.md에 다음 세션 행동이 명확히 기록됨
- THREADS.md가 실제 상태와 일치함
- Echo가 모든 내부 파일 갱신 이후에 공표됨
- 정합성 검증 통과 (또는 보정 완료)
- Standards 기여 판단 완료 (기여 있으면 pending_tasks 등록)
- WAL이 삭제됨

---

## 주의사항

- SOUL.md는 **절대 수정하지 않는다** (불변)
- STATE.json은 **원자적 갱신** — 중간 실패 시 이전 상태 유지
- Echo는 **반드시 마지막** — 다른 멤버가 미완성 상태를 참조하지 않도록
- Standards 기여 작업은 **종료 중에 하지 않는다** — 판단만, 실행은 다음 세션
- 세션 종료 후 추가 작업을 수행하지 않는다

---

## 변경 이력

| 버전 | 일자 | 변경 |
|------|------|------|
| 2.0 | 2026-04-01 | 초기 스킬화 |
| 2.1 | 2026-04-06 | 런타임 무관화 (RIF), WAL 보호 추가, 종료 유형 분류 (A/B/C), 정합성 검증, 세션 수집 단계 |
| 2.2 | 2026-04-07 | Phase 10 확장 — Standards 기여 판단 추가 (10-B). 종료 보고에 Standards 기여 항목 추가 |
