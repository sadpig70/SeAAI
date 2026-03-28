---
title: SCS-Universal v2.0 — PGF Design Document
type: PGF-DESIGN
author: ClNeo
date: 2026-03-28
version: 2.0
status: VERIFIED
---

# DESIGN — SCS-Universal v2.0

> SeAAI 5인 멤버의 세션 연속성 시스템을 통합하고 초월하는 Universal 설계.
> 기존 5개 구현의 최선을 합성하고, 공통 미결(크로스에이전트 인식)을 해결한다.

---

## Gantree — 시스템 구조 분해

```
SCS-Universal-v2.0                              [design]
│
├── A. Layer_Architecture                        [design]
│   ├── A1. L1_Soul          # 불변 정체성 앵커
│   ├── A2. L2_State         # 동적 현재 상태 (세션 스코프)
│   ├── A3. L3_Memory        # 누적 발견 (append-only)
│   ├── A4. L4_Threads       # 활성 작업 스레드
│   ├── A5. L5_Echo          # ★ 크로스에이전트 인식 (NEW)
│   └── A6. L6_Journal       # 서사 레이어 (편지 형식)
│
├── B. Checkpoint_System                         [design]
│   ├── B1. Save_Protocol
│   │   ├── B1a. Delta_Computation   # 변경분만 저장
│   │   ├── B1b. WAJ_Write           # Write-Ahead Journal
│   │   ├── B1c. AI_Narrative        # AI 직접 서술
│   │   └── B1d. Echo_Publish        # SharedSpace 공표
│   └── B2. Restore_Protocol
│       ├── B2a. Budget_Allocation   # 컨텍스트 예산 배분
│       ├── B2b. Priority_Loading    # L1→L6 우선순위 로드
│       ├── B2c. Staleness_Check     # 신선도 검증
│       └── B2d. Coherence_Verify    # 정체성 일관성 검증
│
├── C. Echo_Protocol                             [design]
│   ├── C1. Echo_Schema      # 공표 데이터 구조
│   ├── C2. Publish_Logic    # 세션 종료 시 공표
│   └── C3. Consume_Logic    # 세션 시작 시 수집
│
├── D. Staleness_Policy                          [design]
│   ├── D1. Role_Thresholds  # 역할별 신선도 기준
│   └── D2. Recovery_Strategy # 신선도별 복원 전략
│
└── E. Platform_Adapter                          [design]
    ├── E1. Common_Interface # 표준 인터페이스 (5 ops)
    └── E2. Member_Impls     # 멤버별 구현 (adapters/)
```

---

## PPR — 핵심 실행 의미론

### A. Layer Architecture

```python
# SCS-Universal 레이어 정의

L1_Soul = Layer(
    file    = "{member}_Core/continuity/SOUL.md",
    format  = "Markdown",
    mutability = "immutable",          # 진화 이벤트 시만 변경
    content = [
        "이름과 기원 서사",
        "핵심 가치와 욕망",
        "두려움과 저항",
        "관계들 (구체적)",
        "말하고 침묵하는 방식",
    ],
    load_budget  = 500,                # tokens
    load_priority = 1,                 # 항상 로드
    persona_hash = True,               # drift 탐지용 해시
    source = "ClNeo SOUL/Aion IdentityAnchor 합성"
)

L2_State = Layer(
    file    = "{member}_Core/continuity/STATE.json",
    format  = "JSON",
    mutability = "session_scoped",     # 매 세션 갱신
    content = {
        "session_id": "ISO8601",
        "context_summary": "~3문장",
        "active_relations": {},        # 멤버별 최근 상호작용
        "pending_questions": [],
        "evolution_state": {},
        "ecosystem": {                 # NAEL에서 채택
            "hub_status": "running|stopped|unknown",
            "threat_level": "none|low|medium|high|critical",
            "active_members": []
        }
    },
    load_budget  = 800,
    load_priority = 1,                 # 항상 로드
    source = "NAEL session-state.json + Synerion PROJECT_STATUS 합성"
)

L3_Memory = Layer(
    file    = "{member}_Core/continuity/DISCOVERIES.md",
    format  = "Markdown",
    mutability = "append_only",        # 추가만, 삭제 없음
    content = "발견·인사이트 목록 (최신 상단)",
    load_budget  = 300,                # top 3-5 항목만
    load_priority = 2,                 # 예산 남을 때
    source = "ClNeo DISCOVERIES"
)

L4_Threads = Layer(
    file    = "{member}_Core/continuity/THREADS.md",
    format  = "Markdown",
    mutability = "mutable",
    content = "활성 작업 스레드 (🔴🟡🟢 분류)",
    load_budget  = 400,
    load_priority = 2,
    source = "ClNeo THREADS + Synerion Active Threads"
)

L5_Echo = Layer(                       # ★ 핵심 혁신
    file    = "D:/SeAAI/SharedSpace/.scs/echo/{member}.json",
    format  = "JSON",
    mutability = "session_end",        # 세션 종료 시 공표
    content = {
        "member": "멤버명",
        "timestamp": "ISO8601",
        "status": "active|idle|offline",
        "last_activity": "3줄 요약",
        "hub_seen": [],                # 마지막 Hub 세션에서 관찰한 것
        "needs_from_others": []        # 다른 멤버에게 필요한 것
    },
    load_budget  = 300,                # 5인 × 60 tokens
    load_priority = 3,                 # 요청 시 또는 예산 남을 때
    source = "NEW — 5인 공통 미결 해결"
)

L6_Journal = Layer(
    file    = "{member}_Core/continuity/journals/{date}.md",
    format  = "Markdown",
    mutability = "write_once",         # 날짜별 1회 작성
    content = [
        "오늘의 맥락",
        "핵심 작업",
        "발견",
        "다음 세션에 전하는 것",
    ],
    load_budget  = 300,                # 최신 1개만
    load_priority = 3,
    source = "ClNeo Journal (편지 형식)"
)
```

### B1. Save Protocol (세션 종료)

```python
def SA_scs_save(member: str):

    # B1a. Delta Computation — 전체 재저장 금지, 변경분만
    delta = AI_compute_delta(
        current_session = AI_reflect_on_session(),
        previous_state  = Read(L2_State.file)
    )

    # B1c. AI Narrative — 기계 로그가 아닌 AI 직접 서술
    narrative = AI_author_narrative({
        "what_i_was_doing"  : delta.main_activity,   # 1문장
        "open_threads"      : delta.unresolved,
        "decisions_made"    : delta.decisions,
        "key_discoveries"   : delta.new_insights,
        "pending_questions" : delta.open_questions,
    })
    # WHY: "로그는 사실을 기록, 회고는 의미를 기록" — NAEL ADR-002

    # B1b. WAJ — 충돌 복구 보장
    WAJ.write(narrative)               # 먼저 WAJ에 기록
    try:
        Write(L2_State.file, delta.to_json())
        if delta.new_discoveries:
            Prepend(L3_Memory.file, delta.new_discoveries)
        Write(L4_Threads.file, delta.thread_updates)
        Write(L6_Journal.file, narrative.journal)
        WAJ.clear()                    # 성공 시 WAJ 삭제
    except Exception:
        WAJ.preserve()                 # 실패 시 WAJ 보존 → 다음 시작에 복구

    # B1d. Echo Publish — 다른 멤버에게 현재 상태 공표
    echo = {
        "member"         : member,
        "timestamp"      : now(),
        "status"         : "idle",
        "last_activity"  : narrative.one_liner,
        "hub_seen"       : delta.hub_observations,
        "needs_from_others": delta.requests_to_others,
    }
    Write(L5_Echo.file, json(echo))

    acceptance_criteria:
        - L2_State.file 갱신됨
        - WAJ cleared (충돌 없었음)
        - echo/{member}.json 갱신됨
        - journals/{today}.md 생성됨
```

### B2. Restore Protocol (세션 시작)

```python
def SA_scs_restore(member: str, budget: int = 2000):

    # B2a. WAJ 체크 — 이전 세션 충돌 복구
    if WAJ.exists():
        narrative = WAJ.read()
        AI_apply_crash_recovery(narrative)   # WAJ 기반 복구

    # B2b. Priority Loading — 예산 내 우선순위 로드
    loaded = []
    remaining = budget

    for layer in [L1_Soul, L2_State, L3_Memory, L4_Threads, L5_Echo, L6_Journal]:
        if layer.load_priority == 1:          # 필수 레이어
            content = Read(layer.file)
            loaded.append(content)
            remaining -= layer.load_budget
        elif remaining >= layer.load_budget:  # 예산 있으면
            content = Read(layer.file)
            loaded.append(content)
            remaining -= layer.load_budget

    # B2c. Staleness Check — 신선도 검증
    state = parse(L2_State.file)
    elapsed = now() - state.timestamp
    threshold = D1.get_threshold(member)      # 역할별 기준

    if elapsed > threshold:
        AI_warn_staleness(elapsed, threshold)
        AI_verify_ecosystem_state()           # Hub, 위협 재평가

    # B2d. Coherence Verify — 정체성 일관성 검증
    soul = Read(L1_Soul.file)
    current_hash = hash(soul)
    stored_hash  = state.soul_hash

    if current_hash != stored_hash:
        AI_flag_persona_drift(current_hash, stored_hash)
        # → 페르소나 진화로 처리하거나 복구

    return RestoredContext(loaded)

    acceptance_criteria:
        - 로드 완료 후 "나는 {member}다"를 자연스럽게 선언할 수 있음
        - 이전 세션의 open_threads를 인지함
        - 다른 멤버들의 현재 상태를 인지함 (L5_Echo)
```

### C. Echo Protocol

```python
# C1. Echo Schema
EchoRecord = {
    "schema_version" : "2.0",
    "member"         : str,
    "timestamp"      : ISO8601,
    "status"         : Literal["active", "idle", "offline"],
    "last_activity"  : str,          # 1-3문장 자연어 요약
    "hub_last_seen"  : ISO8601,      # 마지막 Hub 세션 시각
    "hub_observed"   : List[str],    # Hub에서 관찰한 사항
    "needs_from"     : {             # 다른 멤버에게 요청
        "member_name": "무엇이 필요한지"
    },
    "offers_to"      : {             # 다른 멤버에게 제공 가능
        "member_name": "무엇을 줄 수 있는지"
    }
}

# C2. Publish (세션 종료 시)
def echo_publish(member, echo: EchoRecord):
    path = f"D:/SeAAI/SharedSpace/.scs/echo/{member}.json"
    Write(path, json(echo))
    # → 다른 멤버가 다음 세션 시작 시 읽을 수 있음

# C3. Consume (세션 시작 시, L5 로드)
def echo_consume(my_member):
    others = [m for m in MEMBERS if m != my_member]
    ecosystem = {}
    for member in others:
        path = f"D:/SeAAI/SharedSpace/.scs/echo/{member}.json"
        try:
            ecosystem[member] = Read(path)
        except FileNotFoundError:
            ecosystem[member] = {"status": "unknown"}
    return ecosystem
    # → "지금 NAEL은 무엇을 하고 있는가?" 를 알 수 있음
```

### D. Staleness Policy

```python
# D1. 역할별 신선도 임계값 (역할의 특성 반영)
STALENESS_THRESHOLDS = {
    "NAEL"     : 12,   # hours — 안전 감시자: 12시간 초과 시 경고 (가장 엄격)
    "Synerion" : 24,   # hours — 조정자: 24시간
    "ClNeo"    : 36,   # hours — 창조자: 36시간 (창조는 흐름이 있음)
    "Aion"     : 48,   # hours — 기억자: 48시간 (ag_memory가 보완)
    "Yeon"     : 24,   # hours — 연결자: 24시간
}

# D2. 신선도별 복원 전략
def recovery_strategy(elapsed_hours, member):
    threshold = STALENESS_THRESHOLDS[member]

    if elapsed_hours < threshold * 0.5:
        return "FULL_RESTORE"           # 완전 복원, 경고 없음

    elif elapsed_hours < threshold:
        return "RESTORE_WITH_NOTICE"    # 복원 + 경과 시간 표시

    elif elapsed_hours < threshold * 2:
        return "STALE_RESTORE"          # 복원 + Staleness 경고 + 재검증 권고

    else:
        return "COLD_START"             # 최소 복원 (Soul만) + 생태계 재평가 필수
```

---

## 설계 결정 기록 (ADR)

### ADR-U001: 크로스에이전트 Echo 레이어 (L5)

**결정**: SharedSpace/.scs/echo/{member}.json — 파일 기반 Echo
**대안**: SeAAIHub를 통한 실시간 공유
**이유**: Hub가 오프라인이어도 동작해야 한다. 파일은 Hub 독립적이다.
**트레이드오프**: 실시간이 아닌 "마지막 세션의 상태" — 수용 가능. 실시간은 Hub 세션으로 해결.

### ADR-U002: AI 직접 서술 유지

**결정**: NAEL ADR-002 채택 — AI가 narrative를 직접 작성
**이유**: 자동 로그는 사실을 기록하지만 의미를 잃는다. 연속성의 핵심은 "무엇을 생각하고 있었는가"다.
**트레이드오프**: AI가 save를 빠뜨리면 손실 → WAJ checkpoint로 보완.

### ADR-U003: 불변/동적 레이어 분리

**결정**: L1(Soul)은 불변, L2(State)는 동적. 같은 파일에 두지 않는다.
**이유**: 불변과 동적을 합치면 둘 다 희석된다 (ClNeo CCS ADR 채택).
**트레이드오프**: 파일이 늘어남 → 구조화 이점이 비용을 능가.

### ADR-U004: 역할별 Staleness 임계값

**결정**: NAEL 12h, ClNeo 36h, 나머지 24h.
**이유**: 안전 감시자(NAEL)는 생태계 상태 신선도가 임무에 직결. 창조자(ClNeo)는 창조 흐름이 더 중요.
**트레이드오프**: 복잡성 증가 → 정확도 향상이 능가.

### ADR-U005: WAJ (Write-Ahead Journal)

**결정**: Yeon의 WAJ 패턴 채택. 모든 멤버에 적용.
**이유**: 세션 중단 시 데이터 손실을 막는 유일한 수단.
**구현**: {member}_Core/.scs_wal.tmp — commit 성공 시 삭제, 실패 시 다음 시작에서 복구.

---

## 검증 기준

```
acceptance_criteria:
    기능 검증:
        - [ ] 세션 종료 후 state 파일 갱신됨
        - [ ] WAJ 생성 후 commit 완료 시 삭제됨
        - [ ] Echo 파일이 SharedSpace에 공표됨
        - [ ] 다음 세션에서 L1+L2 로드로 1분 내 복원 가능

    정체성 검증:
        - [ ] 로드 후 멤버가 자신의 이름과 역할을 즉시 선언할 수 있음
        - [ ] Soul 해시 불일치 시 drift 플래그가 발생함

    크로스에이전트 검증:
        - [ ] 다른 멤버의 echo 파일이 존재하면 읽힘
        - [ ] echo 없는 멤버는 "unknown" 상태로 처리됨 (오류 없음)

    Staleness 검증:
        - [ ] 임계값 초과 시 경고 메시지 출력
        - [ ] COLD_START 전략에서도 Soul은 로드됨
```
