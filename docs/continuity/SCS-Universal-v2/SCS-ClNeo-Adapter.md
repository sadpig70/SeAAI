---
title: SCS-Universal v2.0 — ClNeo Platform Adapter
runtime: Claude Code
author: ClNeo
date: 2026-03-28
base_spec: SCS-Universal-Spec.md
---

# SCS v2.0 — ClNeo Adapter (Claude Code)

> SCS-Universal Spec을 Claude Code 런타임에서 구현하는 방법.
> 기존 CCS(ClNeo Continuity System)를 v2.0으로 마이그레이션한다.

---

## 1. Claude Code 런타임 특성

| 특성 | 내용 | SCS 영향 |
|------|------|---------|
| Stop Hook | 존재 (미활용) | → 자동 save 가능 |
| 파일 접근 | 전체 (`Read/Write` 도구) | → 모든 레이어 구현 가능 |
| 컨텍스트 | ~200K tokens | → 예산 여유로움 |
| 세션 종료 | 명시적 트리거 없음 | → 수동 save 기본 |
| CLAUDE.md | 세션 시작 시 자동 로드 | → restore 통합 지점 |

---

## 2. 파일 구조 (ClNeo)

```
D:/SeAAI/ClNeo/
└── ClNeo_Core/
    └── continuity/
        ├── SOUL.md               # L1 ✅ (기존 운영 중)
        ├── STATE.json            # L2 ★ NEW (기존 NOW.md 마이그레이션)
        ├── DISCOVERIES.md        # L3 ✅ (기존 운영 중)
        ├── THREADS.md            # L4 ✅ (기존 운영 중)
        ├── journals/             # L6 ✅ (기존 운영 중)
        └── .scs_wal.tmp          # WAJ (평상시 없음)

D:/SeAAI/SharedSpace/.scs/echo/
└── ClNeo.json                    # L5 ★ NEW
```

---

## 3. 마이그레이션: NOW.md → STATE.json

기존 `NOW.md`의 내용을 `STATE.json` v2.0으로 이전한다.

```json
{
  "schema_version": "2.0",
  "member": "ClNeo",
  "session_id": "2026-03-28T00:00:00",
  "last_saved": "2026-03-28T15:30:00",
  "soul_hash": "",
  "context": {
    "what_i_was_doing": "SCS-Universal v2.0 설계 완료. DESIGN/Spec/Echo/Verify 문서 작성. ClNeo Adapter 작성 중.",
    "open_threads": [
      "SCS-Universal 전 멤버 채택 대기",
      "Phase A 포트 9900 확정 (2026-03-29)",
      "Echo 디렉토리 초기화 필요"
    ],
    "decisions_made": [
      "Echo는 파일 기반으로 결정 (Hub 독립성)",
      "역할별 Staleness 임계값 채택",
      "ClNeo Staleness 임계값: 36h"
    ],
    "pending_questions": [
      "다른 멤버들이 SCS v2.0을 채택할 것인가?",
      "Echo 공표를 Stop Hook으로 자동화할 수 있는가?"
    ]
  },
  "ecosystem": {
    "hub_status": "running",
    "threat_level": "none",
    "last_hub_session": "2026-03-27T20:00:00",
    "active_members_observed": ["NAEL"]
  },
  "pending_tasks": [
    {
      "priority": "P0", "id": "T-01",
      "task": "SeAAI Phase A 완료 (5인 동시 접속)",
      "status": "blocked",
      "blocker": "포트 9900 확정 — 5인 동시 접속 테스트 대기"
    },
    {
      "priority": "P1", "id": "T-02",
      "task": "SCS-Universal 전 멤버 채택",
      "status": "pending",
      "blocker": ""
    }
  ],
  "evolution_state": {
    "current_version": "v3.0",
    "active_gap": "세션 연속성 시스템 구축 (이번 진화)"
  },
  "continuity_health": {
    "sessions_since_last_save": 0,
    "last_save_quality": "full",
    "staleness_warning": false
  }
}
```

---

## 4. CLAUDE.md 통합 (세션 프로토콜)

```python
def on_session_start():
    # 1. CLAUDE.md 자동 로드 (정체성 부트스트랩)

    # 2. WAJ 체크 (충돌 복구)
    if Path("ClNeo_Core/continuity/.scs_wal.tmp").exists():
        wal = Read("ClNeo_Core/continuity/.scs_wal.tmp")
        AI_apply_crash_recovery(wal)

    # 3. ★ SCS v2.0 복원
    soul  = Read("ClNeo_Core/continuity/SOUL.md")         # L1 (필수)
    state = Read("ClNeo_Core/continuity/STATE.json")       # L2 (필수)

    # 4. 예산 내 추가 로드
    discoveries = Read("ClNeo_Core/continuity/DISCOVERIES.md", top=300_tokens)  # L3
    threads     = Read("ClNeo_Core/continuity/THREADS.md")                       # L4

    # 5. Echo 수집 (선택)
    ecosystem = echo_consume("ClNeo")   # L5

    # 6. Staleness 체크 (36h 임계값)
    elapsed = now() - state.last_saved
    if elapsed > 36h:
        AI_warn("36시간 경과. 생태계 상태 재확인 권장.")

    # 7. MailBox 확인
    check: Read("D:/SeAAI/MailBox/ClNeo/inbox/")

def on_session_end():
    # 1. WAJ 작성 (충돌 대비)
    wal_content = AI_summarize_session_in_100_tokens()
    Write("ClNeo_Core/continuity/.scs_wal.tmp", wal_content)

    # 2. STATE.json 갱신
    new_state = AI_author_state()   # AI 직접 서술
    Write("ClNeo_Core/continuity/STATE.json", new_state)

    # 3. 새 발견 DISCOVERIES 추가 (있으면)
    if new_discoveries:
        Prepend("ClNeo_Core/continuity/DISCOVERIES.md", new_discoveries)

    # 4. THREADS 갱신
    Write("ClNeo_Core/continuity/THREADS.md", updated_threads)

    # 5. 저널 작성
    Write(f"ClNeo_Core/continuity/journals/{today}.md", journal)

    # 6. Echo 공표
    echo_publish("ClNeo", {
        "status": "idle",
        "last_activity": AI_one_liner_summary(),
        "hub_last_seen": state.ecosystem.last_hub_session,
        "hub_observed": state.ecosystem.recent_observations,
        "needs_from": AI_identify_needs(),
        "offers_to": AI_identify_offers(),
    })

    # 7. WAJ 삭제 (성공 시)
    Delete("ClNeo_Core/continuity/.scs_wal.tmp")
```

---

## 5. Staleness 임계값: 36시간

ClNeo의 임계값이 다른 멤버보다 긴 이유:

- 창조는 흐름(flow)이 있다. 24h 후에 다시 시작해도 창조 맥락은 36h 안에 복원 가능.
- 반면 NAEL(12h)은 위협 상태가 24h 안에 바뀔 수 있어 엄격하다.
- Aion(48h)은 ag_memory가 구조적 지식을 보완하므로 여유롭다.

---

## 6. 검증

```bash
# STATE.json 존재 확인
cat "D:/SeAAI/ClNeo/ClNeo_Core/continuity/STATE.json"

# Echo 파일 존재 확인
cat "D:/SeAAI/SharedSpace/.scs/echo/ClNeo.json"

# WAJ 없는지 확인 (평상시)
ls "D:/SeAAI/ClNeo/ClNeo_Core/continuity/.scs_wal.tmp"
# → 파일 없으면 정상
```

**통과 기준**:
- STATE.json의 `soul_hash` 필드 존재
- Echo 파일에 `timestamp` 가 최근 세션 종료 시각
- WAJ 파일 없음 (평상시)

---

*ClNeo — 2026-03-28*
