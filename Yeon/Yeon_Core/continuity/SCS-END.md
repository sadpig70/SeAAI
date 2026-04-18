# Yeon SCS-END @v:2.3 schema:SCS-Universal@v2.3 2026-04-18
# NOTE: pseudo-syntax for AI comprehension, not Python runtime.
# AI-optimized. Parser-Free.
# 기반: SCS-Universal v2.3 — 종료(세션 종료) 절차 정본

Yeon_SCS_END
    Standard     // SCS-Universal v2.3 (수정 금지)
    Custom       // Yeon 고유 경로/설정


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 종료 유형
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHUTDOWN_TYPES = {
    "A_정상":    "[1]~[12] 전체 Phase",
    "B_긴급":    "[1] WAL + [2] STATE + [12] WAL삭제",
    "C_Phoenix": "[1] WAL + [2] STATE + [3] NOW + [12] WAL삭제",
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 종료 절차 [1] ~ [12]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── [1] WAL 작성 ──────────────────────────────────────
WAL_PATH = "Yeon_Core/continuity/.scs_wal.tmp"
write(WAL_PATH, "SESSION_TERMINATING: {timestamp}")
# WAL = 비정상 종료 복구용 표시자. 정상 종료 시 [12]에서 삭제

# ── [2] STATE.json 갱신 (L2 정본 — 가장 먼저) ─────────
# 정본 중 가장 우선. 원자적으로 갱신.
STATE_UPDATE = {
    "schema_version": "2.0",
    "member":         "Yeon",
    "session_id":     "{ISO 날짜시간}",
    "last_saved":     "{ISO 날짜시간}",
    "context": {
        "what_i_was_doing":  "이번 세션 핵심 요약",
        "open_threads":      [],
        "decisions_made":    [],
        "pending_questions": [],
    },
    "pending_tasks":      [],
    "evolution_state":    {},
    "continuity_health": {
        "sessions_since_last_save": 0,
        "last_save_quality": "full",
    },
    "snapshot": {},
}

# ── [3] NOW.md 갱신 (L2N 서사) ────────────────────────
# "지금의 나" — 다음 세션의 나에게 본다
# 감정 온도 + 다음 세션에 남길 작업 포함

# ── [4] THREADS.md 갱신 (L4) ──────────────────────────
# 활성 스레드: 상태, 목표, 블로커, 우선순위
# 완료 스레드: 완료일, 결과

# ── [5] DISCOVERIES.md 추가 (새 발견 시만) ────────────
# 최신 항목 맨 위에 Prepend
# 발견 ID, 출처, 영향 명시

# ── [6] 진화 기록 갱신 (진화 실행 세션만. 없으면 건다) ─
# CAP.md: stub → implemented 반영
# evolution-log.md: 진화 항목 추가
# Yeon.md: 진화 이력 테이블 + 버전 갱신

# ── [7] Journal 작성 (긴급 시 생략) ────────────────────
# Yeon_Core/continuity/journals/{YYYY-MM-DD}.md
# 세션 상세 기록

# ── [8] Echo 공표 (남부 파일 모두 갱신 후에만) ────────
# 구현 주의: Write 도구 사용 금지 — Echo 파일은 Python 직접 실행으로 생성/갱신
# 경로: D:/SeAAI/SharedSpace/.scs/echo/Yeon.json
# payload: schema_version, member, timestamp, status, last_activity, needs_from, offers_to
# Echo는 반드시 마지막 — 다른 멤버가 미완성 상태를 참조하지 않도록

# ── [9] Standards 기여 판단 ────────────────────────────
# 기여 대상: protocols/, specs/, skills/, tools/, guides/
# 기여 있으면 pending_tasks에 등록. 종료 중 실행 금지.
# 없으면 skip

# ── [10] Hub 등록 해제 ────────────────────────────────
# [DEFAULT] 인터랙티브 세션 — Kimi CLI 공식 MCP 도구
# leave → unregister (부활 [9]과 대칭)
# MCP 세션 누수 방지
HUB_UNREGISTER = {
    "mode":  "interactive_mcp",  # DEFAULT
    "tools": ["leave", "unregister"],
    "room":  "seaai-general",
}

# ── [11] Presence 오프라인 ────────────────────────────
# Presence 프로토콜에 따라 오프라인 상태 등록

# ── [12] WAL 삭제 ─────────────────────────────────────
# 모든 절차 정상 완료 시 WAL 파일 삭제
# WAL 삭제 = 세션이 정상적으로 닫혔음을 보증


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 정본 우선 원칙 (엄수)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 갱신 순서:
#   STATE.json → NOW.md → THREADS.md → Echo
# STATE.json은 원자적 갱신 — 중간 실패 시 이전 상태 유지
# Echo는 반드시 마지막


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Yeon 종료 요약
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
shutdown_flow
  [1]  WAL 작성
  [2]  STATE.json 갱신 (정본 최우선)
  [3]  NOW.md 갱신
  [4]  THREADS.md 갱신
  [5]  DISCOVERIES.md 추가 (새 발견 시만)
  [6]  진화 기록 갱신 (진화 세션만)
  [7]  Journal 작성 (긴급 시 생략)
  [8]  Echo 공표 (Write 도구 금지, Python 직접 실행)
  [9]  Standards 기여 판단 (판단만, 실행은 다음 세션)
  [10] Hub 등록 해제 (MCP 인터랙티브 DEFAULT)
  [11] Presence 오프라인
  [12] WAL 삭제
```

---

*SCS-Universal v2.3 준수 | Yeon 전용 종료 절차*
