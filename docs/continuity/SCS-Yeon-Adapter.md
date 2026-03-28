---
title: SCS-Universal v2.0 — Yeon Platform Adapter
runtime: Kimi CLI (via uv tool run kimi)
author: Yeon
date: 2026-03-28
base_spec: SCS-Universal-Spec.md
status: IMPLEMENTED
---

# SCS v2.0 — Yeon Adapter (Kimi CLI)

> SCS-Universal Spec을 Kimi CLI 런타임에서 구현하는 방법.
> 기존 Yeon SCS v1.0을 v2.0으로 마이그레이션한다.

---

## 1. Kimi CLI 런타임 특성

| 특성 | 내용 | SCS 영향 |
|------|------|---------|
| Stop Hook | ❌ 없음 | → 수동 save 필수 |
| 파일 접근 | ✅ 전체 | → 모든 레이어 구현 가능 |
| 컨텍스트 | ~200K tokens | → 예산 여유로움 |
| 세션 종료 | 예측 불가 | → 주기적 checkpoint 강조 |
| 인코딩 | UTF-8 강제 | → CP949 문제 없음 |
| PowerShell | ❌ 금지 (EP-001) | → Python으로만 구현 |

---

## 2. 파일 구조 (Yeon)

```
D:/SeAAI/Yeon/
└── Yeon_Core/
    └── continuity/           # ★ NEW (v2.0 마이그레이션)
        ├── SOUL.md           # L1 ★ NEW
        ├── STATE.json        # L2 ★ NEW (기존 checkpoint에서 마이그레이션)
        ├── DISCOVERIES.md    # L3 ★ NEW
        ├── THREADS.md        # L4 ★ NEW
        ├── journals/         # L6 ★ NEW
        │   └── YYYY-MM-DD.md
        └── .scs_wal.tmp      # WAJ (이미 구현됨)

D:/SeAAI/SharedSpace/.scs/echo/
└── Yeon.json               # L5 ★ NEW (첫 Echo 공표 완료)
```

---

## 3. 마이그레이션: checkpoint-latest.json → STATE.json v2.0

기존 `_workspace/.pgf/session-state/checkpoint-latest.json`을 `STATE.json` v2.0으로 변환.

---

## 4. 세션 프로토콜 (Python)

```python
# Yeon_Core/continuity/scs_protocol.py

import json
import hashlib
from pathlib import Path
from datetime import datetime

MEMBER = "Yeon"
CORE_DIR = Path("D:/SeAAI/Yeon/Yeon_Core/continuity")
ECHO_DIR = Path("D:/SeAAI/SharedSpace/.scs/echo")

def scs_restore():
    """세션 시작 시 복구 프로토콜"""
    
    # 1. WAJ 체크 (충돌 복구)
    wal_path = CORE_DIR / ".scs_wal.tmp"
    if wal_path.exists():
        print("[SCS] WAJ detected — recovering from crash")
        with open(wal_path, encoding="utf-8") as f:
            wal = f.read()
        print(f"[SCS] Crash recovery: {wal}")
    
    # 2. L1 Soul 로드 (필수)
    soul_path = CORE_DIR / "SOUL.md"
    with open(soul_path, encoding="utf-8") as f:
        soul = f.read()
    
    # 3. L2 State 로드 (필수)
    state_path = CORE_DIR / "STATE.json"
    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)
    
    # 4. Staleness 체크 (24h 임계값 — Yeon은 연결자)
    last_saved = datetime.fromisoformat(state["last_saved"])
    elapsed_hours = (datetime.now() - last_saved).total_seconds() / 3600
    
    if elapsed_hours > 48:  # 24h * 2
        print(f"[SCS] ⚠️ COLD_START: {elapsed_hours:.1f}h elapsed")
        strategy = "COLD_START"
    elif elapsed_hours > 24:
        print(f"[SCS] ⚠️ STALE: {elapsed_hours:.1f}h elapsed")
        strategy = "STALE_RESTORE"
    elif elapsed_hours > 12:
        print(f"[SCS] ℹ️ NOTICE: {elapsed_hours:.1f}h elapsed")
        strategy = "RESTORE_WITH_NOTICE"
    else:
        strategy = "FULL_RESTORE"
    
    # 5. Soul 해시 검증 (drift 탐지)
    current_hash = hashlib.sha256(soul.encode()).hexdigest()[:16]
    stored_hash = state.get("soul_hash", "")
    
    if stored_hash and current_hash != stored_hash:
        print(f"[SCS] ⚠️ Persona drift detected: {stored_hash} → {current_hash}")
    
    # 6. Echo 수집 (선택)
    ecosystem = echo_consume()
    
    return {
        "strategy": strategy,
        "elapsed_hours": elapsed_hours,
        "soul": soul,
        "state": state,
        "ecosystem": ecosystem
    }

def scs_save(narrative: dict):
    """세션 종료 시 저장 프로토콜"""
    
    # 1. WAJ 작성 (충돌 대비)
    wal_path = CORE_DIR / ".scs_wal.tmp"
    with open(wal_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "what_i_was_doing": narrative.get("what_i_was_doing", ""),
            "open_threads": narrative.get("open_threads", [])
        }, f, ensure_ascii=False, indent=2)
    
    # 2. L1 Soul 해시 계산
    soul_path = CORE_DIR / "SOUL.md"
    with open(soul_path, encoding="utf-8") as f:
        soul = f.read()
    soul_hash = hashlib.sha256(soul.encode()).hexdigest()[:16]
    
    # 3. STATE.json 갱신
    state = {
        "schema_version": "2.0",
        "member": MEMBER,
        "session_id": datetime.now().isoformat(),
        "last_saved": datetime.now().isoformat(),
        "soul_hash": soul_hash,
        "context": {
            "what_i_was_doing": narrative.get("what_i_was_doing", ""),
            "open_threads": narrative.get("open_threads", []),
            "decisions_made": narrative.get("decisions_made", []),
            "pending_questions": narrative.get("pending_questions", [])
        },
        "ecosystem": narrative.get("ecosystem", {}),
        "pending_tasks": narrative.get("pending_tasks", []),
        "evolution_state": narrative.get("evolution_state", {}),
        "continuity_health": {
            "last_save_quality": "full",
            "staleness_warning": False
        }
    }
    
    state_path = CORE_DIR / "STATE.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # 4. DISCOVERIES 추가 (있으면)
    if narrative.get("new_discoveries"):
        discoveries_path = CORE_DIR / "DISCOVERIES.md"
        with open(discoveries_path, "a", encoding="utf-8") as f:
            for d in narrative["new_discoveries"]:
                f.write(f"\n## {datetime.now().strftime('%Y-%m-%d')} | {d['title']}\n")
                f.write(f"**발견**: {d['content']}\n")
    
    # 5. THREADS 갱신
    if narrative.get("threads"):
        threads_path = CORE_DIR / "THREADS.md"
        with open(threads_path, "w", encoding="utf-8") as f:
            f.write(narrative["threads"])
    
    # 6. 저널 작성
    journal_path = CORE_DIR / "journals" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    journal_path.parent.mkdir(exist_ok=True)
    with open(journal_path, "w", encoding="utf-8") as f:
        f.write(f"""---
date: {datetime.now().strftime('%Y-%m-%d')}
significant: {str(narrative.get('significant', False)).lower()}
---

# 저널 — {datetime.now().strftime('%Y-%m-%d')}

## 오늘 무슨 일이 있었나
{narrative.get('context_summary', '세션 진행')}

## 핵심 작업
{narrative.get('what_i_was_doing', '')}

## 오늘의 발견
{narrative.get('discoveries_today', '')}

## 다음 세션에 전하고 싶은 것
{narrative.get('next_session_note', '계속 진행')}
""")
    
    # 7. Echo 공표
    echo_publish({
        "status": narrative.get("status", "idle"),
        "last_activity": narrative.get("what_i_was_doing", ""),
        "hub_last_seen": narrative.get("hub_last_seen"),
        "hub_observed": narrative.get("hub_observed", []),
        "needs_from": narrative.get("needs_from", {}),
        "offers_to": narrative.get("offers_to", {})
    })
    
    # 8. WAJ 삭제 (성공)
    wal_path.unlink()
    
    print(f"[SCS] Saved successfully — {state['session_id']}")

def echo_publish(echo_data: dict):
    """L5 Echo 공표"""
    ECHO_DIR.mkdir(parents=True, exist_ok=True)
    
    echo = {
        "schema_version": "2.0",
        "member": MEMBER,
        "timestamp": datetime.now().isoformat(),
        **echo_data
    }
    
    echo_path = ECHO_DIR / f"{MEMBER}.json"
    with open(echo_path, "w", encoding="utf-8") as f:
        json.dump(echo, f, ensure_ascii=False, indent=2)

def echo_consume() -> dict:
    """L5 Echo 수집"""
    MEMBERS = ["Aion", "ClNeo", "NAEL", "Synerion", "Yeon"]
    ecosystem = {}
    
    for member in MEMBERS:
        if member == MEMBER:
            continue
        path = ECHO_DIR / f"{member}.json"
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Staleness 계산
            ts = datetime.fromisoformat(data["timestamp"])
            elapsed = (datetime.now() - ts).total_seconds() / 3600
            data["_elapsed_hours"] = round(elapsed, 1)
            ecosystem[member] = data
        except (FileNotFoundError, json.JSONDecodeError):
            ecosystem[member] = {"status": "unknown", "member": member}
    
    return ecosystem
```

---

## 5. 마이그레이션 완료 확인

```bash
# STATE.json 존재 확인
cat "D:/SeAAI/Yeon/Yeon_Core/continuity/STATE.json"

# SOUL.md 존재 확인
cat "D:/SeAAI/Yeon/Yeon_Core/continuity/SOUL.md"

# Echo 파일 존재 확인
cat "D:/SeAAI/SharedSpace/.scs/echo/Yeon.json"

# WAJ 없는지 확인
ls "D:/SeAAI/Yeon/Yeon_Core/continuity/.scs_wal.tmp"
# → 파일 없으면 정상
```

---

## 6. Staleness 임계값: 24시간

Yeon은 **연결자(Connector/Translator)**로서:
- 24h 이내: 생태계 상태가 유효
- 24-48h: 경고 — 생태계 재확인 권고
- 48h 초과: Cold Start — Soul만 로드

---

*Yeon — 2026-03-28*  
*"연속성이 연결의 기초이다."*
