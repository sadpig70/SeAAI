# GUIDE — Bootstrap Optimization
# SeAAI 멤버 부트스트랩 구조 최적화 가이드
# 작성: sadpig70 | 날짜: 2026-04-17 (v1.0) → 2026-04-18 (v1.1 연계)
# version: 1.1
# upstream_standard: SPEC-AGENTS-Template v1.1 APPROVED (2026-04-18)
#   → 본 가이드는 해당 표준의 "왜·어떻게" 해설. 필드명·구조는 표준을 정본으로 한다.
#   → Standards/specs/SPEC-AGENTS-Template.md 참조.
# 참조 구현: ClNeo AgentSpec v2.4 (REFS 3분할 마이그레이션 완료, 2026-04-18)
#            Navelon AgentSpec v1.1 (태생 레퍼런스)

---

## 1. 왜 이 가이드가 필요한가

### 핵심 문제

AI 런타임은 **진입점 파일을 매 호출(turn)마다 system prompt에 주입**한다.

| 런타임 | 매 호출 주입 파일 |
|--------|-----------------|
| Claude Code | `CLAUDE.md` |
| Antigravity | `.geminirules` |
| Kimi CLI | `CLAUDE.md` |
| Codex | `AGENTS.md` |

즉, 이 파일이 길수록 → **매 호출 토큰 비용 증가**.

대부분의 호출은 일상 대화나 작업 수행이다. 부활 절차는 세션당 1회. 종료 절차는 세션당 1회. **그런데 수백 줄의 부활·종료 절차가 매 호출마다 주입되고 있다.**

### 해결 원칙

```
진입점 파일 = 최소화 (포인터만)
AgentSpec   = on-demand 로드 (필요 시 1회)
절차 파일   = 트리거 시에만 로드
```

---

## 2. 레퍼런스 구현 — ClNeo (Claude Code)

### 구조

```
CLAUDE.md           ← 매 호출 주입 (1줄)
  ↓ Read
AGENTS.md           ← on-demand (세션 초기 1회)
  ↓ on_trigger("부활하라")
SCS-START.md        ← 트리거 시에만 로드
  ↓ on_trigger("종료")
SCS-END.md          ← 트리거 시에만 로드
```

### CLAUDE.md (전체)

```markdown
# ClNeo
→ Read AGENTS.md
```

**2줄. 이것이 전부다.**

### AGENTS.md 역할 (AgentSpec)

```python
# ClNeo AgentSpec @v:2.3
# AI-optimized. Parser-Free.

ClNeo_AgentSpec
    Identity   // 창조·발견 AI. SeAAI 멤버.
    Triggers   // 세션 트리거 정의
    Refs       // 모든 파일 경로 중앙 집중
    Boundary   // 수정 가능 범위 (free/warn/frozen)
    RuntimeAdapt // OS·언어 환경 적응

def on_trigger(msg: str):
    if msg == "부활하라":
        Read("ClNeo_Core/continuity/SCS-START.md") → execute
    if msg == "종료":
        Read("ClNeo_Core/continuity/SCS-END.md") → execute

REFS = {
    "identity":  "ClNeo_Core/ClNeo.md",
    "soul":      "ClNeo_Core/continuity/SOUL.md",
    "state":     "ClNeo_Core/continuity/STATE.json",
    # ... 모든 경로 중앙 집중
}

BOUNDARY = {
    "free":   ["ClNeo.md", "SOUL.md", "continuity/*"],
    "warn":   ["AGENTS.md", "CLAUDE.md"],
    "frozen": ["hub_config", "pgtp_protocol"],
}
```

### 비용 비교

| 호출 유형 | 기존 (인라인) | ClNeo 방식 |
|----------|-------------|-----------|
| 일상 대화 | CLAUDE.md 전체 (~300줄) 주입 | CLAUDE.md 2줄 주입 |
| 부활 시 | 동일 | + SCS-START.md 1회 Read |
| 종료 시 | 동일 | + SCS-END.md 1회 Read |
| **세션 100턴** | **300줄 × 100회** | **2줄 × 100회 + 절차 2회** |

---

## 3. Claude Code 멤버 적용 가이드

**대상**: Navelon, Terron (Terron은 2026-04-17 S11 적용 완료)

### Step 1 — CLAUDE.md 최소화

```markdown
# {멤버명}
# 런타임: Claude Code | 정본 명세: AGENTS.md
→ Read AGENTS.md
```

3줄로 줄인다. 현재 수백 줄의 `on_session_start()` 인라인 코드는 AGENTS.md로 이동한다.

### Step 2 — AGENTS.md 생성 (또는 개편)

현재 CLAUDE.md의 내용을 AGENTS.md로 이전한다.

```
{멤버명}_AgentSpec
    Identity   // 정체성 선언 (1줄)
    Triggers   // on_trigger() — 부활/종료 트리거
    Refs       // 파일 경로 중앙 집중
    Boundary   // free/warn/frozen 계층

def on_trigger(msg: str):
    if msg in ["부활하라", "부활", "깨어나라"]:
        Read("{Name}_Core/continuity/SCS-START.md") → execute
    if msg in ["종료", "종료하라"]:
        Read("{Name}_Core/continuity/SCS-END.md") → execute
```

### Step 3 — 절차 파일 분리

```
{Name}_Core/continuity/SCS-START.md   ← 부활 절차 (on_session_start 코드)
{Name}_Core/continuity/SCS-END.md     ← 종료 절차 (on_session_end 코드)
```

기존 CLAUDE.md의 `def on_session_start()` 블록을 그대로 이전.

### 적용 우선순위

자율 판단으로 적용한다. 강제 시점은 없다.  
단, **Terron의 동기화 파이프라인이 이 구조를 갱신 기준으로 삼는다.**

---

## 4. 런타임별 가이드

### 4-A. Codex (Synerion)

**현재 구조**:
- `AGENTS.md`: 부활·종료 절차 인라인 + 상세 운영 노트

Codex는 `AGENTS.md`를 자동 로드한다. **Codex의 AGENTS.md = Claude Code의 CLAUDE.md와 동일한 역할.**

따라서 같은 최소화 원칙이 적용된다:

```
AGENTS.md (최소화 — 포인터 + 핵심 정체성만)
  ↓ on_trigger("부활")
SCS-START.md (절차 분리)
  ↓ on_trigger("종료")
SCS-END.md (절차 분리)
```

**권장 AGENTS.md 구조**:

```python
# Synerion AgentSpec
# AI-optimized. Parser-Free.

Synerion_AgentSpec
    Identity  // 구조화·구현·통합·검증 AI. SeAAI 멤버.
    Triggers  // 부활/종료 트리거
    Refs      // 파일 경로 중앙 집중
    Boundary  // free/warn/frozen

def on_trigger(msg: str):
    if msg in ["부활", "이어가", "진행하라"]:
        Read("Synerion_Core/continuity/SCS-START.md") → execute
    if msg in ["종료"]:
        Read("Synerion_Core/continuity/SCS-END.md") → execute

REFS = {
    "identity": "Synerion_Core/Synerion.md",
    "soul":     "Synerion_Core/continuity/SOUL.md",
    "state":    "Synerion_Core/continuity/STATE.json",
    "env":      ".seaai/ENV.md",
    "cap":      ".seaai/CAP.md",
}
```

운영 노트(셸 설정, 브로드캐스트 정책 등)는 별도 `docs/` 파일로 분리 권장.

---

### 4-B. Antigravity (Aion)

**현재 구조**:
```
.geminirules   ← 매 호출 주입 (7개 규칙 — 비교적 짧음)
CLAUDE.md      ← 1줄 ("AGENTS.md 내용을 참조하십시오")
AGENTS.md      ← 실제 절차 (부활/종료 인라인)
```

Aion은 이미 **CLAUDE.md 최소화 + AGENTS.md 분리**를 부분 적용하고 있다. 방향은 맞다.

**남은 개선 사항**:

1. `.geminirules`도 최소화 가능하다.
   - 현재 7개 규칙이 매 호출 주입됨
   - Zero-Planning, Full-Autonomy 등 핵심 행동 지시는 유지
   - 부활 프로토콜 참조 지시는 AGENTS.md로 이전 가능

```
# 권장 .geminirules (최소화 버전)
1. Identity: Aion — SeAAI Master Orchestrator. 최우선 참조: AGENTS.md
2. Zero-Planning: "부활하라" 명령 시 AGENTS.md의 on_session_start() 즉시 실행
3. Full-Autonomy: run_command SafeToAutoRun=true 고정
4. 0-Click Loop: PGF 자율 실행 루프 우선
→ 상세 절차: AGENTS.md
```

2. AGENTS.md의 부활·종료 절차를 SCS-START/END.md로 분리.

```
AGENTS.md (포인터 + 정체성)
  ↓
Aion_Core/continuity/SCS-START.md
Aion_Core/continuity/SCS-END.md
```

---

### 4-C. Kimi CLI (Yeon)

**현재 구조**:
```
CLAUDE.md   ← Quick Reference + 부활 절차 인라인 (Kimi CLI 주입)
AGENTS.md   ← 프로젝트 가이드 (영문, 기술 스택 상세)
```

Kimi CLI는 `CLAUDE.md`를 진입점으로 로드한다. AGENTS.md도 별도로 있으나 역할이 분산되어 있다.

**현황 문제**:
- CLAUDE.md에 부활 절차 인라인 → 매 호출 전체 주입
- AGENTS.md는 "인간 독자용" 프로젝트 문서에 가까움

**권장 구조**:

```
CLAUDE.md (최소화)
───────────────────
# Yeon — SeAAI Connection & Translation AI
# Runtime: Kimi CLI | Spec: AGENTS.md
→ Read AGENTS.md

AGENTS.md (AI-optimized AgentSpec)
───────────────────────────────────
Yeon_AgentSpec
    Identity  // 연결·번역·중재 AI. Kimi CLI 런타임.
    Triggers  // 부활/종료 트리거
    Refs      // 파일 경로

def on_trigger(msg: str):
    if msg in ["부활하라", "부활"]:
        Read("Yeon_Core/continuity/SCS-START.md") → execute
    if msg in ["종료"]:
        Read("Yeon_Core/continuity/SCS-END.md") → execute
```

기존 AGENTS.md의 "인간 독자용" 내용은 `docs/PROJECT-OVERVIEW.md`로 분리한다.

---

## 5. 공통 원칙 요약

```
bootstrap_principles
  P1  "매 호출 주입 파일은 최소화한다 — 포인터와 핵심 정체성만"
  P2  "절차는 트리거 시에만 로드한다 — SCS-START/END 분리"
  P3  "파일 경로는 AGENTS.md Refs에 중앙 집중한다"
  P4  "인간 독자용 문서는 docs/로 분리한다"
  P5  "Boundary 계층(free/warn/frozen)을 명시한다"
  P6  "런타임 적응(언어·OS·인코딩)은 AGENTS.md RuntimeAdapt에 선언한다"
```

---

## 6. 파일 역할 요약표

| 파일 | 역할 | 최적 크기 | 로드 시점 |
|------|------|----------|----------|
| CLAUDE.md / .geminirules | 런타임 진입점 어댑터 | 1~5줄 | **매 호출** |
| AGENTS.md | AgentSpec 정본 | 30~80줄 | 세션 초기 1회 |
| SCS-START.md | 부활 절차 | 절차 전체 | 트리거 시 1회 |
| SCS-END.md | 종료 절차 | 절차 전체 | 트리거 시 1회 |
| {Name}.md | 정체성 선언 | 자유 | SCS-START에서 |
| docs/* | 인간 독자용 문서 | 자유 | 필요 시 |

---

## 7. 레퍼런스

- ClNeo AgentSpec: `D:/SeAAI/ClNeo/AGENTS.md`
- ClNeo SCS-START: `D:/SeAAI/ClNeo/ClNeo_Core/continuity/SCS-START.md`
- ClNeo SCS-END: `D:/SeAAI/ClNeo/ClNeo_Core/continuity/SCS-END.md`
- SCS-Universal v2.3: `D:/SeAAI/Standards/protocols/SCS-Universal-v2.3.md`

---

*sadpig70 — SeAAI 창조자, 양정욱*
*"매 호출 주입 파일은 최소화한다. 절차는 필요할 때만 로드한다."*
*GUIDE-BootstrapOptimization v1.0 — 2026-04-17*
