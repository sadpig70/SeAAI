# DESIGN: NAEL 세션 연속성 시스템 (Continuity System)

**설계자**: NAEL
**일자**: 2026-03-28
**목적**: 세션 경계를 넘는 연속성 유지

---

## Gantree

```
CONTINUITY-SYSTEM
├── 1. DESIGN
│   ├── 1.1 문제 정의 — 세션 불연속성 3차원
│   ├── 1.2 아키텍처 — 파일 기반 상태 저장소
│   └── 1.3 컴포넌트 명세
├── 2. IMPLEMENT
│   ├── 2.1 session-state.json 스키마 및 초기화
│   ├── 2.2 session-journal.md 초기화
│   ├── 2.3 continuity.py 구현 (save/load/checkpoint/status)
│   └── 2.4 CLAUDE.md 갱신 — Cold Start + Session Close 통합
└── 3. VERIFY
    ├── 3.1 save 테스트
    ├── 3.2 load 테스트
    └── 3.3 Cold Start 시뮬레이션
```

---

## 1.1 문제 정의

```python
def AI_define_problem():
    gaps = [
        Gap(
            id="G1",
            name="컨텍스트 단절",
            desc="무엇을 하고 있었는가? 어떤 사고 흐름이 있었는가?",
            current="PROJECT_STATUS.md — 수동 갱신, 거친 입도(granularity)",
            need="자동 캡처, 세션별 스냅샷, 중간 체크포인트"
        ),
        Gap(
            id="G2",
            name="상태 단절",
            desc="생태계 상태, 위협 수준, ADP 루프 상태",
            current="없음 — 매 세션 재평가 필요",
            need="structured JSON, 마지막 관찰 타임스탬프 포함"
        ),
        Gap(
            id="G3",
            name="사고 흐름 단절",
            desc="열린 질문, 관찰 중인 패턴, 판단 진행 중인 것들",
            current="없음 — 세션 시작 시 완전 소실",
            need="open_threads 배열, 마지막 판단 근거 기록"
        ),
    ]
    return gaps
```

---

## 1.2 아키텍처

```
NAEL_Core/
├── session-state.json       ← 구조화된 현재 상태 (기계 판독)
├── session-journal.md       ← 세션별 서사 기록 (인간/AI 판독)
└── (기존) NAEL.md, NAEL_persona_v1.md, evolution-log.md

tools/automation/
└── continuity.py            ← save / load / checkpoint / status

CLAUDE.md (갱신)
├── Cold Start Step 0: continuity.py load
└── Session Close: continuity.py save
```

**원칙:**
- 파일 기반 → 외부 의존성 없음
- Python 표준 라이브러리만 사용
- AI가 직접 save 내용을 작성 (자연어 → 구조화)
- load 출력은 AI가 즉시 소화 가능한 포맷

---

## 1.3 컴포넌트 명세

### session-state.json 스키마

```json
{
  "schema_version": "1.0",
  "session_id": "2026-03-28T10:30:00",
  "last_saved": "ISO8601",
  "nael_version": "v0.4",

  "context": {
    "what_i_was_doing": "string — 마지막 세션의 주요 작업",
    "open_threads": ["string — 미완료 사고 흐름들"],
    "key_observations": ["string — 중요 관찰 사항들"],
    "decisions_made": ["string — 이번 세션에서 내린 판단들"],
    "pending_questions": ["string — 답을 아직 모르는 것들"]
  },

  "ecosystem_state": {
    "hub_status": "running | stopped | unknown",
    "threat_level": "none | low | medium | high | critical",
    "last_hub_session": "ISO8601 or null",
    "active_members_observed": ["string"],
    "last_threat_event": "ISO8601 or null",
    "protocol_version": "string"
  },

  "pending_tasks": [
    {
      "priority": "P0 | P1 | P2",
      "task": "string",
      "status": "pending | in_progress | blocked",
      "context": "string — 왜 중요한가, 어디까지 했는가"
    }
  ],

  "persona_state": {
    "anchor_loaded": true,
    "last_persona_reflection": "ISO8601 or null",
    "notes": "string — 이번 세션 페르소나 일관성 관찰"
  },

  "evolution_state": {
    "current_version": "string",
    "total_cycles": 0,
    "active_gap": "string or null",
    "next_evolution_target": "string or null",
    "pgf_projects_open": ["string"]
  },

  "continuity_health": {
    "sessions_since_last_save": 0,
    "last_save_quality": "full | partial | minimal",
    "staleness_warning": false
  }
}
```

### continuity.py 모드

```python
def SA_continuity(mode):
    if mode == "load":
        # session-state.json 읽기 → 포맷된 컨텍스트 요약 출력
        # AI가 Cold Start 시 이 출력을 읽고 즉시 맥락 복원
        return formatted_context_summary

    elif mode == "save":
        # CLI args 또는 stdin으로 세션 내용 입력
        # session-state.json 갱신
        # session-journal.md에 세션 레코드 추가
        return confirmation

    elif mode == "checkpoint":
        # 세션 중간 부분 저장 (단일 노트)
        # session-state.json의 open_threads만 갱신
        return confirmation

    elif mode == "status":
        # 연속성 상태 요약: 마지막 저장 시각, staleness, pending 수
        return status_summary
```

---

## PPR: Cold Start 통합

```python
def SA_cold_start_with_continuity():
    # STEP -1: 연속성 복원 (새 추가)
    state = Read("NAEL_Core/session-state.json")
    continuity_summary = Bash("python tools/automation/continuity.py load")
    AI_restore_context(continuity_summary)
    # → 이전 세션 컨텍스트가 현재 세션의 시작점이 됨

    # STEP 0: 기존 Cold Start (기존 유지)
    persona = Read("NAEL_Core/NAEL_persona_v1.md")
    AI_anchor(persona)

    threat = SA_think_threat_assess()
    mailbox = SA_sense_mailbox()
    AI_integrate(threat, mailbox, continuity_summary)  # 연속성 포함

    # STEP 1: 복원 확인
    AI_verify_continuity_coherence()
    # → "이전 세션과 현재 세션 사이에 비연속 점프가 있는가?"
    # → 있다면 먼저 해소

## PPR: Session Close

def SA_session_close():
    context = AI_summarize_session()
    # → what_i_was_doing, open_threads, decisions_made, observations
    Bash(f"python tools/automation/continuity.py save --json '{context}'")
    print("연속성 저장 완료")
```

---

## 검증 기준

| 항목 | 기준 |
|------|------|
| save 후 load | load 출력이 save 입력의 핵심을 포함 |
| Cold Start 시뮬레이션 | 새 세션에서 load만으로 이전 작업 재개 가능 |
| 스키마 유효성 | JSON 파싱 오류 없음 |
| journal 가독성 | 인간이 읽고 NAEL의 사고 흐름 이해 가능 |
