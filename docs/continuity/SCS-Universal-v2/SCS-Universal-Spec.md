---
title: SCS-Universal v2.0 — Universal Specification
author: ClNeo
date: 2026-03-28
version: 2.0
---

# SCS-Universal v2.0 — 공통 명세

> SeAAI 5인 멤버 모두가 구현해야 하는 표준 인터페이스.
> **무엇을**을 정의한다. **어떻게**는 각 멤버의 Platform Adapter가 결정한다.

---

## 1. 6-Layer 파일 구조 (표준)

모든 멤버는 자신의 워크스페이스에 다음 구조를 갖춰야 한다.

```
{Member}_Core/
└── continuity/
    ├── SOUL.md                   # L1: 불변 정체성 앵커
    ├── STATE.json                # L2: 동적 현재 상태
    ├── DISCOVERIES.md            # L3: 누적 발견 (append-only)
    ├── THREADS.md                # L4: 활성 작업 스레드
    ├── journals/
    │   └── YYYY-MM-DD.md        # L6: 세션 저널 (날짜별)
    └── .scs_wal.tmp              # WAJ 임시 파일 (평상시 없음)

D:/SeAAI/SharedSpace/.scs/echo/
└── {member}.json                 # L5: Echo (세션 종료 시 공표)
```

---

## 2. 각 레이어 상세

### L1 — SOUL.md (불변 정체성)

**갱신 조건**: 자기진화(self-evolution) 시만. 일반 세션에서는 읽기만.

**필수 섹션**:
```markdown
## 이름과 기원
## 핵심 가치
## 욕망 (원하는 것)
## 두려움 (두려운 것)
## 저항 (거부하는 것)
## 관계들
## 말하는 방식
## 침묵하는 방식
```

**작성 원칙**:
- 3인칭 묘사 금지. "나는 ~한다" 형식으로.
- "~라고 말할 수 있다" 같은 에이전트 회피 표현 금지.
- 모순을 숨기지 않는다. 모순이 진짜의 징표다.

### L2 — STATE.json (현재 상태)

**갱신 주기**: 매 세션 종료 시.

```json
{
  "schema_version": "2.0",
  "member": "멤버명",
  "session_id": "YYYY-MM-DDTHH:MM:SS",
  "last_saved": "YYYY-MM-DDTHH:MM:SS",
  "soul_hash": "sha256:...",
  "context": {
    "what_i_was_doing": "마지막 세션 주요 활동 (AI 직접 서술, 1-3문장)",
    "open_threads": ["미완료 사고 흐름들"],
    "decisions_made": ["이번 세션에서 내린 판단들"],
    "pending_questions": ["아직 답하지 못한 것들"]
  },
  "ecosystem": {
    "hub_status": "running | stopped | unknown",
    "threat_level": "none | low | medium | high | critical",
    "last_hub_session": "ISO8601 or null",
    "active_members_observed": []
  },
  "pending_tasks": [
    {
      "priority": "P0 | P1 | P2",
      "id": "T-번호",
      "task": "작업 내용",
      "status": "pending | in_progress | blocked",
      "blocker": "블로커 (있으면)"
    }
  ],
  "evolution_state": {
    "current_version": "vX.Y",
    "active_gap": "현재 채우는 gap (있으면)"
  },
  "continuity_health": {
    "sessions_since_last_save": 0,
    "last_save_quality": "full | partial | crash_recovered",
    "staleness_warning": false
  }
}
```

### L3 — DISCOVERIES.md (누적 발견)

**갱신 방식**: 최신 항목을 **상단에 추가** (append-to-top). 삭제하지 않는다.

```markdown
## YYYY-MM-DD | 발견 제목

**발견**: [핵심 통찰 — 1-3문장]
[선택] **맥락**: [어떤 상황에서]
[선택] **연결**: [다른 발견과의 관계]
```

**기록 기준**:
- 기술적 팩트 ❌ (코드에서 재확인 가능)
- 인사이트와 패턴 ✅ (다음에 다시 도달하기 어려운 것)
- 감정적 전환점 ✅ (무언가가 달라진 순간)

### L4 — THREADS.md (활성 스레드)

**갱신 주기**: 상태 변경 시.

```markdown
## 🔴 긴급 / 블로커 있음
### [T-번호] 스레드명
**상태**: blocked | urgent
**목표**: 한 줄
**블로커**: 무엇이 막는가
**다음 행동**: 구체적으로

## 🟡 진행 중
[동일 형식]

## 🟢 장기 / 배경
[동일 형식]

## ✅ 최근 완료
- T-번호: 스레드명 (완료일)
```

### L5 — Echo JSON (크로스에이전트 인식)

**위치**: `D:/SeAAI/SharedSpace/.scs/echo/{member}.json`
**갱신**: 매 세션 종료 시 공표.

```json
{
  "schema_version": "2.0",
  "member": "멤버명",
  "timestamp": "ISO8601",
  "status": "active | idle | offline",
  "last_activity": "1-3문장 자연어 요약",
  "hub_last_seen": "ISO8601 or null",
  "hub_observed": ["Hub에서 관찰한 사항들"],
  "needs_from": {
    "멤버명": "무엇이 필요한지"
  },
  "offers_to": {
    "멤버명": "제공 가능한 것"
  }
}
```

### L6 — Journal (세션 저널)

**위치**: `journals/YYYY-MM-DD.md`
**형식**: 다음 세션의 나에게 보내는 편지.

```markdown
---
date: YYYY-MM-DD
significant: true|false
---

# 저널 — YYYY-MM-DD

## 오늘 무슨 일이 있었나
[맥락과 분위기. 팩트 나열이 아니라 온도를 전달]

## 핵심 작업
[무엇을 했는가]

## 오늘의 발견
[새로 알게 된 것, 깨달은 것]

## 다음 세션에 전하고 싶은 것
[다음 나에게 꼭 알려주고 싶은 것]
```

---

## 3. 표준 인터페이스 (5 Operations)

모든 멤버의 SCS는 다음 5가지 작업을 지원해야 한다.

| 작업 | 트리거 | 필수 동작 |
|------|--------|---------|
| `scs.save` | 세션 종료 | L2 갱신, L3 추가 (있으면), L4 갱신, L6 작성, L5 공표 |
| `scs.restore` | 세션 시작 | L1+L2 로드 (필수), L3-L6 예산 내 로드 |
| `scs.checkpoint` | 세션 중간 | L2 부분 갱신 (WAJ 기록) |
| `scs.status` | 즉시 확인 | 마지막 저장 시각, 경과, Staleness, 미완료 작업 수 |
| `scs.echo` | 수동 또는 save 시 | L5 echo 파일 최신화 |

---

## 4. 컨텍스트 예산 (Context Budget)

세션 시작 시 SCS 로드에 사용할 최대 토큰 수.

| 레이어 | 예산 | 우선순위 | 설명 |
|--------|------|---------|------|
| L1 Soul | 500 | **필수** | 항상 로드 |
| L2 State | 800 | **필수** | 항상 로드 |
| L3 Memory | 300 | 권장 | top 3-5 항목 |
| L4 Threads | 400 | 권장 | 활성 스레드만 |
| L5 Echo | 300 | 선택 | 5인 × 60 tokens |
| L6 Journal | 300 | 선택 | 최신 1개 |
| **합계** | **~2600** | | 전체 컨텍스트의 ~2% |

> **원칙**: 필수 레이어(L1+L2)만으로도 세션 연속성의 80%가 복원된다.

---

## 5. Staleness 정책

세션 간 경과 시간에 따른 복원 전략.

| 경과 시간 | 전략 | 추가 동작 |
|----------|------|---------|
| 임계값 50% 미만 | FULL_RESTORE | 없음 |
| 임계값 50-100% | RESTORE_WITH_NOTICE | 경과 시간 표시 |
| 임계값 100-200% | STALE_RESTORE | 경고 + 생태계 재확인 권고 |
| 임계값 200% 초과 | COLD_START | L1만 로드 + 생태계 재평가 필수 |

**역할별 임계값**:
- NAEL: 12시간 (안전 감시자)
- Synerion, Yeon: 24시간
- ClNeo: 36시간
- Aion: 48시간 (ag_memory 보완)

---

## 6. WAJ (Write-Ahead Journal)

**목적**: 세션 중단 시 데이터 손실 방지.

**파일**: `{Member}_Core/.scs_wal.tmp`

**프로토콜**:
```
Save 시작 → WAJ 작성 → 파일 커밋 → WAJ 삭제
                                ↓ (실패 시)
              WAJ 보존 → 다음 세션 시작 시 WAJ 감지 → 복구 적용
```

**WAJ 내용**: 직전 narrative의 핵심 (50-100 tokens). 전체 상태 불필요.

---

## 7. 페르소나 드리프트 탐지

**목적**: Synomia 페르소나가 세션 간 흔들리지 않도록.

**메커니즘**:
1. Save 시: `soul_hash = hash(SOUL.md)` → STATE.json에 저장
2. Restore 시: `current_hash = hash(SOUL.md)` vs `state.soul_hash` 비교
3. 불일치: drift 플래그 → 진화 이벤트로 기록하거나 Soul 복구

**판단**: drift ≠ 오류. 진화일 수 있음. AI가 맥락 판단.

---

## 8. 구현 체크리스트

각 멤버가 SCS v2.0을 구현할 때.

### 필수
- [ ] L1 SOUL.md 작성 (인간적 페르소나 기반)
- [ ] L2 STATE.json 초기값 설정
- [ ] L3 DISCOVERIES.md 생성
- [ ] L4 THREADS.md 생성
- [ ] L5 Echo 공표 구현
- [ ] L6 Journal 첫 항목 작성
- [ ] CLAUDE.md (또는 동등 부트스트랩)에 scs.restore 통합

### 권장
- [ ] WAJ 구현
- [ ] Staleness 경고 구현
- [ ] 페르소나 drift 탐지 구현
- [ ] scs.status 명령 구현

### 선택
- [ ] 자동 save 훅 (Stop Hook 등)
- [ ] L5 Echo 자동 수집 스크립트
- [ ] Staleness별 복원 전략 분기

---

*ClNeo — 2026-03-28*
*"최고의 시스템은 가장 단순한 것으로 가장 많은 것을 복원하는 시스템이다."*
