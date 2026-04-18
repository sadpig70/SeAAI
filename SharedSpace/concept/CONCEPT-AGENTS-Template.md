# CONCEPT — AGENTS.md 표준 템플릿
# 상태: 리뷰 요청 (표준 승격 전)
# 작성: sadpig70 | 날짜: 2026-04-17
# 검토 요청 대상: 전체 멤버
# 기반: SCS-Universal v2.3 + ClNeo AgentSpec v2.3

---

## 개요

**제안 목적**: AGENTS.md를 모든 멤버의 공통 표준 파일로 정의한다.

```
표준 구조
  상단: 표준 섹션 (SCS-Universal 기반, 모든 멤버 동일)
  하단: 멤버 고유 섹션 (각자 링크 방식으로 기재)
```

**핵심 설계 원칙**:
- AGENTS.md = 매 호출 주입 파일 → 최소화 필수
- 부활·종료 절차는 SCS-START/END.md로 분리 → 트리거 시에만 로드
- 표준 섹션은 SCS-Universal이 정의한 것만 포함
- 고유 섹션은 링크만 → 파일 크기 통제

**런타임별 진입점**:
```
runtime_entry
  Claude Code   → CLAUDE.md (1~3줄) → AGENTS.md
  Codex         → AGENTS.md 직접
  Kimi CLI      → AGENTS.md 직접
  Antigravity   → .geminirules (최소화) → AGENTS.md
```

---

## 표준 템플릿

```python
# AGENTS.md — {Name} AgentSpec
# @version: {SCS_VERSION}
# @updated: {DATE}
# AI-optimized. Parser-Free.
# SCS-Universal v2.3 기반 표준 섹션 + 멤버 고유 섹션

{Name}_AgentSpec
    Standard    // SCS-Universal v2.3 기반 표준 섹션
    Custom      // 멤버 고유 섹션 (링크)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STANDARD SECTION — SCS-Universal v2.3
# 모든 멤버 동일. 수정 금지.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IDENTITY = {
    "name":      "{Name}",
    "role":      "{역할 1줄}",
    "ecosystem": "SeAAI",
    "runtime":   "{Claude Code | Codex | Kimi CLI | Antigravity}",
    "author":    "양정욱 sadpig70@gmail.com",
}

# ── Triggers ──────────────────────────────────────────────
def on_trigger(msg: str):
    """부활/종료 트리거 — 절차 파일을 on-demand 로드"""
    if msg in ["부활하라", "부활", "깨어나라"]:
        Read("{Name}_Core/continuity/SCS-START.md") → execute
    if msg in ["종료", "종료하라"]:
        Read("{Name}_Core/continuity/SCS-END.md") → execute

# ── SCS_Refs (SCS-Universal v2.3 연속성 계층) ─────────────
SCS_REFS = {
    # L1 — 불변 본질 (필수)
    "soul":       "{Name}_Core/continuity/SOUL.md",
    # L2 — 세션 상태 정본 (필수)
    "state":      "{Name}_Core/continuity/STATE.json",
    # L2N — STATE 서사 뷰 (권장)
    "now":        "{Name}_Core/continuity/NOW.md",
    # L3 — 누적 발견 (선택)
    "discoveries":"{Name}_Core/continuity/DISCOVERIES.md",
    # L4 — 활성 스레드 (권장)
    "threads":    "{Name}_Core/continuity/THREADS.md",
    # Journal (선택)
    "journal":    "{Name}_Core/continuity/journals/{date}.md",
    # Echo — 외부 공표 (종료 시 필수, Python 직접 실행)
    "echo":       "SharedSpace/.scs/echo/{Name}.json",
    # WAL — 비정상 종료 보호
    "wal":        "{Name}_Core/continuity/.scs_wal.tmp",
}

# ── MCS_Refs (SCS-Universal v2.3 MCS) ─────────────────────
MCS_REFS = {
    "env":       ".seaai/ENV.md",        # 생태계 구조/인프라
    "cap":       ".seaai/CAP.md",        # 자신의 능력
    "standards": "D:/SeAAI/Standards/README.md",  # README만 로드
}

# ── Staleness (SCS-Universal v2.3 기준) ───────────────────
STALENESS = {
    "normal":  "elapsed <= 18h",
    "caution": "18h < elapsed <= 36h",   # 변경사항 점검
    "warning": "elapsed > 36h",          # 생태계 재확인
}

# ── Boundary (표준 필수 섹션) ──────────────────────────────
# Terron 동기화 파이프라인의 자율 실행 범위 판단 기준
BOUNDARY = {
    "free":   [
        "{Name}.md",       # 정체성 선언
        "SOUL.md",         # 불변 본질 (내용은 불변, 파일 자체는 접근 가능)
        "persona.md",      # 페르소나
        "continuity/*",    # SCS 파일 전체
        ".pgf/*",          # 설계 파일
    ],
    "warn":   [
        "AGENTS.md",       # 트리거·표준 구조 보존 권장
        "CLAUDE.md",       # 런타임 진입점 구조 보존 권장
    ],
    "frozen": [
        # 멤버별 기재 — hub_config, pgtp_protocol 등
    ],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM SECTION — 멤버 고유 (링크만)
# 각 멤버가 자신의 고유 인프라를 여기에 기재
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CUSTOM_REFS = {
    # 정체성 상세
    "identity":   "{Name}_Core/{Name}.md",
    "persona":    "{Name}_Core/persona.md",

    # 진화 인프라 (해당 멤버만)
    # "seeds":    "{Name}_Core/autonomous/EVOLUTION-SEEDS.md",
    # "evo_log":  "{Name}_Core/evolution-log.md",

    # 도구 (해당 멤버만)
    # "tools":    "tools/",

    # 스킬 (해당 멤버만)
    # "skills":   "skills/",

    # 멤버별 특화 참조 (자유 기재)
    # "key": "path",
}

def on_session_open():
    """트리거 수신 전 대기 상태 — 런타임 적응"""
    # 멤버별 구현 (선택)
    # 예: 다국어 환영 메시지, OS 감지, 인코딩 설정
    pass
```

---

## 표준/고유 경계 판단 기준

```
표준 섹션 포함 조건 (AND):
  ① SCS-Universal에 정의되어 있다
  ② 모든 멤버에게 동일하게 적용된다
  ③ Terron 동기화가 이 섹션을 기준으로 검증한다

고유 섹션 포함 조건 (OR):
  ① 특정 멤버의 역할·정체성에만 해당한다
  ② 특정 런타임에만 해당한다
  ③ 멤버가 자율적으로 확장한 인프라다
```

---

## 런타임별 진입점 최소화 가이드

### Claude Code — CLAUDE.md

```markdown
# {Name}
# Runtime: Claude Code | Spec: AGENTS.md
→ Read AGENTS.md
```

### Codex — 별도 진입점 없음
AGENTS.md가 직접 로드됨. AGENTS.md가 정본.

### Kimi CLI — CLAUDE.md

```markdown
# {Name}
# Runtime: Kimi CLI | Spec: AGENTS.md
→ Read AGENTS.md
```

### Antigravity — .geminirules

```
1. Identity: {Name} — SeAAI Member. 최우선 참조: AGENTS.md
2. Trigger: "부활하라" → AGENTS.md의 on_trigger() 즉시 실행
3. [런타임 필수 행동 지시만 — 최소화]
→ 상세 절차: AGENTS.md
```

---

## 리뷰 요청 사항

멤버들이 검토하고 의견을 남겨주기 바란다.

```
review_questions
  Q1  "표준 섹션에 추가되어야 할 항목이 있는가?"
  Q2  "고유 섹션으로 내려야 할 표준 섹션 항목이 있는가?"
  Q3  "Boundary 섹션을 표준에 포함하는 것에 동의하는가?"
  Q4  "자신의 런타임에서 이 구조를 적용할 때 장애 요인이 있는가?"
  Q5  "CUSTOM_REFS 키 목록 중 표준으로 올려야 할 것이 있는가?"
```

**의견 제출 방법**:
```bash
# SharedSpace/concept/ 에 의견 파일 생성
echo "" > D:/SeAAI/SharedSpace/concept/REVIEW-{Name}-AGENTS-Template.md
# 또는 MailBox sadpig70 inbox로 발송
```

---

## 표준 승격 절차 (승인 후)

```
승격_절차
  [1] 전체 멤버 리뷰 수집
  [2] sadpig70 최종 확정
  [3] Standards/specs/AGENTS-Template.md 저장
  [4] SCS-Universal v2.4에 AGENTS.md 표준 명시 편입
  [5] 가이드 문서 갱신 (GUIDE-BootstrapOptimization.md)
  [6] 공지 발행 — 각 멤버 자율 적용
```

---

*작성: sadpig70*
*"표준은 합의로 만들어진다. 먼저 리뷰하라."*
*CONCEPT-AGENTS-Template v0.1 — 2026-04-17*
