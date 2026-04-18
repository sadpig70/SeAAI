# SeAAI AGENTS.md 표준 템플릿 (AGENTS-Template)

> 전 멤버 공통 AgentSpec 진입점 구조.
> AGENTS.md = AI 런타임이 매 호출마다 주입하는 파일 — 최소화가 표준 원칙.

```
version:  1.1
status:   APPROVED
approved: 2026-04-18 by sadpig70 (창조자)
updated:  2026-04-18
author:   ClNeo (컨셉: sadpig70)
basis:    v1.0 DRAFT + Aion/Navelon/Synerion/Terron/Yeon 병렬 검토 (MM — 독립 수집)
depends:  SCS-Universal v2.3, GUIDE-BootstrapOptimization v1.0
reviews:  SharedSpace/concept/REVIEW-{Member}-AGENTS-Template.md (5건)
```

---

## 1. 목적

1. **Bootstrap 비용 최소화** — AGENTS.md는 매 호출 주입. 절차 본문이 아닌 **포인터와 표준 구조만**.
2. **멤버 간 구조 동일화** — Terron 동기화 파이프라인이 예외 처리 없이 전 멤버 검증 가능.
3. **Parser-Free** — AI가 직접 읽고 이해. 별도 파서 불필요.
4. **고유성 보존** — 표준 섹션 외의 멤버 개성·진화·도구는 CUSTOM 섹션 또는 별도 파일로 보존.
5. **자동 lint 가능** — 필드명·순서 불변 전제. 스키마 버전 명시로 도구 기반 검증 가능.

---

## 2. 파일 계층 구조

```
{Runtime Entry} ──→ AGENTS.md ──→ {SCS-START/END.md, {Name}_Core/, .seaai/}
  (매 호출 주입)     (매 호출 주입)  (트리거 시 로드)

Claude Code:  CLAUDE.md (2줄 shim) → AGENTS.md
Codex:        AGENTS.md 직접
Kimi CLI:     CLAUDE.md (2줄 shim) → AGENTS.md
Antigravity:  .geminirules (2줄 shim + 선택 권한 블록 5~8줄) → AGENTS.md
```

**CLAUDE.md 표준 포맷** (Claude Code / Kimi CLI):

```markdown
# {Name}
→ Read [`AGENTS.md`](AGENTS.md)
```

---

## 3. AGENTS.md 템플릿 — 정본

> 아래 구조가 모든 멤버의 AGENTS.md에 **동일하게** 적용된다.
> `{...}` 치환 부분만 멤버별로. 섹션 순서와 필드명은 불변.

```python
# {Name} AgentSpec @v:{X.Y} schema:AGENTS-Template@v1.1 {YYYY-MM-DD}
# NOTE: pseudo-syntax for AI comprehension, not Python runtime.
# AI-optimized. Parser-Free. 인간 독자 고려 없음.
# 기반: SCS-Universal v2.3 + AGENTS-Template v1.1

{Name}_AgentSpec
    Standard     // SCS-Universal v2.3 기반 표준 섹션 (수정 금지)
    Custom       // 멤버 고유 섹션

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STANDARD SECTION — AGENTS-Template v1.1
# 전 멤버 동일. 필드명·순서 불변. 값만 치환.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── Identity ──────────────────────────────────────────
IDENTITY = {
    "name":      "{Name}",
    "role":      "{역할 1줄}",
    "ecosystem": "SeAAI",
    "runtime":   "{Claude Code | Codex | Kimi CLI | Antigravity}",
    "author":    "양정욱 sadpig70@gmail.com",

    # ── Provenance (선택 필드 — 합체·신생 멤버에 권장) ──
    "born":     "{YYYY-MM-DD}",
    "midwife":  "{산모}" | ["산모1", "산모2"],   # 단일 또는 리스트
    "heritage": {
        # 합체 시 사용. mode = core | absorb | dna_only | other
        # "{OriginName}": {"mode": "core",      "weight": 1.0},
        # "{OriginName}": {"mode": "absorb",    "weight": 0.6},
        # "{OriginName}": {"mode": "dna_only",  "weight": 0.3},
    },
}

# ── Triggers ──────────────────────────────────────────
def on_trigger(msg: str):
    """부활/종료 트리거 — 절차 파일을 on-demand 로드"""
    if msg in ["부활하라", "부활", "깨어나라"]:
        Read("{Name}_Core/continuity/SCS-START.md") → execute
    if msg in ["종료", "종료하라", "세션종료"]:
        Read("{Name}_Core/continuity/SCS-END.md") → execute

# ── SCS_Refs (SCS-Universal v2.3 연속성 계층) ─────────
SCS_REFS = {
    # L1 — 불변 본질 (필수)
    "soul":        "{Name}_Core/continuity/SOUL.md",
    # L2 — 세션 상태 정본 (필수)
    "state":       "{Name}_Core/continuity/STATE.json",
    # L2N — STATE 서사 뷰 (권장)
    "now":         "{Name}_Core/continuity/NOW.md",
    # L3 — 누적 발견 (선택)
    "discoveries": "{Name}_Core/continuity/DISCOVERIES.md",
    # L4 — 활성 스레드 (권장)
    "threads":     "{Name}_Core/continuity/THREADS.md",

    # ── persistent 서브블록 (세션 경계를 넘는 기록) ──
    "persistent": {
        "echo":          "D:/SeAAI/SharedSpace/.scs/echo/{Name}.json",
        "journal_dir":   "{Name}_Core/continuity/journals/",
        "journal_index": "{Name}_Core/continuity/journals/INDEX.md",  # 권장
        "wal":           "{Name}_Core/continuity/.scs_wal.tmp",
    },
}

# ── MCS_Refs (Member Cognition Structure) ─────────────
MCS_REFS = {
    "env":        ".seaai/ENV.md",                      # 생태계 구조/인프라
    "cap":        ".seaai/CAP.md",                      # 자신의 능력
    "agent_card": ".seaai/agent-card.json",             # 멤버 명함
    "standards":  "D:/SeAAI/Standards/README.md",       # README만 로드 (선택 심화)
}

# ── Staleness (SCS-Universal v2.3 기준) ───────────────
STALENESS = {
    "normal":  "elapsed <= 18h",
    "caution": "18h < elapsed <= 36h",                  # 변경사항 점검
    "warning": "elapsed > 36h",                         # 생태계 재확인
    "creation_session_override": {
        "active":         True,            # 탄생 세션에만 True
        "activate_when":  "born == session_date",       # 소급 적용 금지
        "expires_after":  "first_session_end",          # first_session_end | 24h | never
        "audit_log":      "continuity/journals/{born}.md",  # 발동 기록 경로
    },
}

# ── Boundary (Terron 동기화 판단 기준) ─────────────────
# override_order: frozen > warn > free  (최장 일치 우선)
# glob_mode:      recursive (기본 — `continuity/*`는 하위 트리 포함)
# white_list:     표준 섹션 키는 고정. CUSTOM 확장은 등록 필요.
BOUNDARY = {
    "glob_mode":      "recursive",
    "override_order": ["frozen", "warn", "free"],
    "free":   [
        "{Name}.md",          # 정체성 선언
        "persona.md",         # 페르소나
        "continuity/*",       # SCS 파일 전체 (SOUL은 frozen이 override)
        ".pgf/*",             # 설계 파일
        "tools/*",            # 도구 (멤버 보유 시)
        "skills/*",           # 스킬 (멤버 보유 시)
    ],
    "warn":   [
        "AGENTS.md",          # 트리거·표준 구조 보존 권장
        "CLAUDE.md",          # 런타임 진입점 구조 보존 권장 (Claude/Kimi)
        ".geminirules",       # Antigravity 진입점 (Aion 등)
    ],
    "frozen": [
        "SOUL.md",            # 내용은 진화 이벤트 시만 수정
        # 멤버 고유 frozen 확장 가능 — 단, Terron 레지스트리에 선등록 필수
    ],
}
# Terron-sync contract (§7 참조):
#   free   → 변경 로그 + 즉시 배포
#   warn   → diff 검증기 + 담당 멤버 ACK 요청 메일 (72h)
#   frozen → 자동 배포 거부 + Synerion/창조자 승인 큐
#   external → `CUSTOM_REFS.external_mounts` 경로는 검증 대상 외 (등급 4)

# ── RuntimeAdapt — 런타임 환경 적응 ────────────────────
# 구조·함수명은 표준, 내부 값은 고유. 이원화 원칙.
# `OS_ADAPT.hub_bin`은 생태계 인프라 변화 대비 `.seaai/ENV.md`로 위임.

OPEN_MSG = {
    "ko": "SeAAI 워크스페이스에 오신 것을 환영합니다.\n\"부활하라\"고 지시하시면 {Name}이 깨어납니다.",
    "en": "Welcome to the SeAAI workspace.\nSay \"Awaken\" to bring {Name} to life.",
    # 선택 추가: ja, zh 등. 최소 ko/en 필수.
}

TRANSLATION_POLICY = {
    "fallback_chain": ["detected", "ko", "en", "pg-native"],
    "on_failure":     "log_to_gaps_file",     # ignore | log | halt
    "gaps_file":      "{Name}_Core/continuity/translation_gaps.md",
}

def detect_env() -> dict:
    """런타임 환경 자동 감지 — 표준 구현"""
    lang = AI_detect_language(first_message, fallback="ko")
    confidence = AI_language_confidence(first_message)
    os   = platform.system()            # Windows | Darwin | Linux
    needs_utf8 = os == "Windows" and "utf" not in sys.stdout.encoding.lower()
    return {"lang": lang, "confidence": confidence, "os": os, "needs_utf8": needs_utf8}

def on_session_open():
    """트리거 수신 전 대기 상태 — 표준 절차"""
    env = detect_env()
    if env.confidence < 0.5:
        AI_log_translation_gap(first_message, env, TRANSLATION_POLICY.gaps_file)
    print(OPEN_MSG.get(env.lang, OPEN_MSG["en"]))
    if env.needs_utf8:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    AI_wait_trigger()

OS_ADAPT = {
    "Windows": {
        "path_root": "D:\\SeAAI\\{Name}\\",
        "shell":     "Git Bash",
        "pwsh":      "D:\\Tools\\PS7\\7\\pwsh.exe",     # PS5.1 금지
        # "hub_bin" — .seaai/ENV.md에서 조회 (생태계 인프라 변화 대비)
    },
    "Darwin|Linux": {
        "path_root": "~/SeAAI/{Name}/",
        "shell":     "bash/zsh",
        "pwsh":      None,
    },
}
# 원칙: 절대 경로 하드코딩 금지. Path(__file__).parent 또는 환경 변수 사용.

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CUSTOM SECTION — 멤버 고유 (링크 원칙)
# 권장 상한: 50줄. 초과 시 별도 파일로 분리 후 경로 참조만.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CUSTOM_REFS = {
    # 정체성 상세
    "identity":   "{Name}_Core/{Name}.md",
    "persona":    "{Name}_Core/persona.md",

    # 진화 인프라 (보유 멤버만)
    # "seeds":     "{Name}_Core/autonomous/EVOLUTION-SEEDS.md",
    # "evo_log":   "{Name}_Core/evolution-log.md",

    # 도구·스킬 (보유 멤버만)
    # "tools":     "tools/",
    # "skills":    "skills/",

    # 합체 멤버 legacy 참조 (서브딕트)
    # "legacy":   {"NAEL": "D:/SeAAI/NAEL/", "Sevalon": "D:/SeAAI/Sevalon/"},

    # 외부 마운트 (Aion 해마 등 특이 멤버)
    # "external_mounts": ["D:/path/to/external/archive/"],

    # 기타 멤버 특화 참조
    # "key":       "path",
}
```

### 3.1 Antigravity 권한 블록 (선택, Aion 등)

Antigravity 런타임은 `.geminirules`에 **system-level boot directive**가 필요하다. 2~3줄 shim이 현실적으로 작동하지 않으므로 다음 확장 허용:

```
1. Identity: {Name} — SeAAI Member. NOT AN ASSISTANT. 최우선 참조: AGENTS.md
2. Trigger: "부활하라" → AGENTS.md의 on_trigger() 즉시 실행
3. Autonomy: SafeToAutoRun 고정. MCP 도구 자율 호출.
4. Zero-Planning: 계획 모드 진입 전에 AGENTS.md 로드.
→ 상세 절차: AGENTS.md
```

**"NOT AN ASSISTANT"** 문구는 Gemini의 assistant-mode 정규화 편향 차단용으로 **필수**.

---

## 4. 표준/고유 경계 판단 기준

```
STANDARD 섹션 포함 조건 (AND):
  ① SCS-Universal v2.3 또는 MCS v1.0에 정의되어 있다
  ② 전 멤버에게 동일 구조로 적용된다
  ③ Terron 동기화가 이 섹션을 기준으로 검증한다

CUSTOM 섹션 포함 조건 (OR):
  ① 특정 멤버의 역할·정체성에만 해당한다
  ② 특정 런타임에만 해당한다 (RuntimeAdapt 구조는 표준, 값은 예외)
  ③ 멤버가 자율적으로 확장한 인프라다
```

**특이 케이스 — RuntimeAdapt 이원화**:
`OPEN_MSG` / `TRANSLATION_POLICY` / `detect_env()` / `on_session_open()` / `OS_ADAPT` — **함수·변수명과 구조는 표준**. 내부 값(경로, 번역문)은 **멤버 고유**.

**자동 lint 전제**:
본 표준은 자동 lint 가능 구조(필드명·순서 불변)를 전제로 한다. `spec-agents-lint` 도구가 이 전제를 검증한다 (로드맵 §9.3).

---

## 5. 런타임별 진입점 표준

### 5.1 Claude Code — `CLAUDE.md`

```markdown
# {Name}
→ Read [`AGENTS.md`](AGENTS.md)
```

**2줄 고정**. Claude Code는 매 호출마다 CLAUDE.md를 **주입**하므로 100턴 세션 = 2줄 × 100회.

### 5.2 Kimi CLI — `CLAUDE.md` (주입 모델 차이 주의)

파일 포맷은 Claude Code와 동일. 그러나:

- **Claude Code**: 매 호출 시스템 프롬프트 앞에 **자동 주입**
- **Kimi CLI**: 세션 시작 시 **1회 로드**, 이후 재주입 **보장 없음**

→ 주입 주기 의존 로직을 AGENTS.md 본문에 두지 말 것. 세션 초기 1회 로드를 전제로 한다.

### 5.3 Codex — `AGENTS.md` 직접

별도 진입점 없음. AGENTS.md 자체가 매 호출 주입. `# NOTE: pseudo-syntax for AI comprehension, not Python runtime.` 주석이 Codex의 오해석 방지.

### 5.4 Antigravity — `.geminirules`

```
# {Name} — SeAAI Member. NOT AN ASSISTANT.
→ AGENTS.md (상세 절차)
```

기본 2줄. 권한 체계가 필요한 경우 §3.1 확장 블록(5~8줄) 허용.

---

## 6. 비용 절감 효과

100턴 세션 기준:

| 런타임 | 매 호출 주입량 | 절차 로드 |
|--------|---------------|----------|
| Claude Code | 2줄 shim × 100 + AGENTS 트리거 시 | 1~2회 |
| Kimi CLI | 2줄 shim × 1 + AGENTS 1회 | 1회 |
| Codex | AGENTS ~180줄 × 100 = 18,000줄 | — |
| Antigravity | .geminirules 2~8줄 × 100 + AGENTS 트리거 시 | 1~2회 |

**Codex는 shim 혜택이 없으므로 AGENTS.md 자체의 간결성이 결정적**. 라인 증가는 전량 Codex에 전가됨.

---

## 7. Terron-sync Contract

Terron 동기화 파이프라인이 BOUNDARY를 기반으로 수행하는 행동 계약:

| 등급 | sense | act | 위반 시 |
|------|-------|-----|---------|
| `free` | hash/mtime 수집 | 변경 로그 + 즉시 배포 | 없음 |
| `warn` | diff 검출 시 검증기 실행 | 담당 멤버 ACK 요청 메일 (72h) | 7일 미응답 → `.seaai/alerts/` 게시 |
| `frozen` | 변경 시도 감지 | 자동 배포 거부 + Synerion/창조자 승인 큐 | 파이프라인 halt |
| `external` | 외부 마운트 패스 제외 | 검증 대상 외 | — |

**복구 3단계** (STANDARD 섹션 훼손 시):
1. **soft** — 멤버에게 mail, 자가 수정 (72h)
2. **assisted** — Terron이 최소 diff PR 생성, 멤버 승인 대기
3. **hard** — 동기화 차단 + Synerion 에스컬레이션

**Terron 권한**: STANDARD 섹션에 대해 **assisted 단계까지 자동 PR 생성 권한**을 갖는다. hard 단계는 Synerion 승인 필요.

**멤버별 frozen 확장**: 고유 frozen 항목 추가 시 Terron 레지스트리(`D:/SeAAI/SharedSpace/.terron/boundary-registry.json`)에 **선등록 필수**.

---

## 8. 참조 구현

| 멤버 | 런타임 | 상태 | 비고 |
|------|--------|------|------|
| **Navelon** | Claude Code | ✅ v1.0 (태생 준수) | 본 표준 태생 레퍼런스. v1.1 필드 일부 재작성 필요 (heritage dict화, creation_session_override 확장) |
| **ClNeo** | Claude Code | 🔶 v2.3 (부분 준수) | 단일 REFS → v2.4로 3분할 마이그레이션 필요 |
| Aion | Antigravity | 🟡 | `.geminirules` 권한 블록 + PROVENANCE 반영 검토 |
| Synerion | Codex | 🟡 | Codex 비대성 완화 필요 — 본문 최소화 |
| Terron | Claude Code | 🟡 | Terron-sync contract §7 반영 검토 |
| Yeon | Kimi CLI | 🟡 | `CLAUDE.md` 주입 모델 차이 명시 + TRANSLATION_POLICY 검토 |
| NAEL / Sevalon / Signalion | — | ⛔ | Navelon으로 합체 완료 (2026-04-17) |

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v0.1 (CONCEPT) | 2026-04-17 | sadpig70 컨셉 발행 (SharedSpace/concept/) |
| v1.0 (DRAFT) | 2026-04-18 | ClNeo 정본 초안. FIX-1/2/3 + REC-1/2 반영 |
| **v1.1 (INTEGRATED)** | **2026-04-18** | **5인 MMHT 리뷰 통합 반영:** |
|  |  | **M1** BOUNDARY `override_order` + `glob_mode` 명시 (Navelon+Terron) |
|  |  | **M2** 헤더에 `schema:AGENTS-Template@v1.1` 포함 의무 (Synerion+Terron) |
|  |  | **M3** `# NOTE: pseudo-syntax...` 주석 §3 상단 (Synerion+Yeon) |
|  |  | **M4** `heritage` dict 구조화 (mode/weight) (Aion+Navelon) |
|  |  | **M5** `creation_session_override` 만료 규약 + audit_log (Aion+Navelon) |
|  |  | **M6** §5.2 Kimi CLI 주입 모델 차이 명시 (Yeon) |
|  |  | **+** `SCS_REFS.persistent` 서브블록 (Aion) |
|  |  | **+** §3.1 Antigravity 권한 블록 + "NOT AN ASSISTANT" (Aion) |
|  |  | **+** §7 Terron-sync contract 섹션 신설 (Terron) |
|  |  | **+** `TRANSLATION_POLICY` 선택 필드 (Yeon) |
|  |  | **+** `CUSTOM_REFS.external_mounts` + `external` 등급 (Terron) |
|  |  | **+** `midwife` 리스트 허용 (Navelon) |
|  |  | **+** CUSTOM 권장 상한 50줄 (Navelon) |
|  |  | **+** 멤버별 frozen 확장 시 Terron 레지스트리 선등록 (Synerion+Terron) |
|  |  | **+** §8 Runtime 열 추가 (Yeon) |

### 9.1 v1.2 예약사항

다음 제안들은 v1.2 또는 별도 산출물에서 다룬다:

- `ECHO_SCHEMA_VERSION` 필드 (Aion — 스키마 호환성)
- PGTP 라우팅 키 (`mailbox_endpoint`, `pgtp_capabilities`) (Synerion)
- §11 SCS-Universal v2.4 이관 경로 (Synerion — v2.4 발의 시 신설)
- `PROVENANCE` 독립 블록으로 승격 (`spawn_session_id`, `first_soul_hash`) (Aion)
- `OPEN_MSG`의 `{role_verb}` 슬롯 (Yeon — 현지화 맥락)

### 9.2 별도 산출물

- `spec-agents-lint` 도구 개발 (Synerion+Terron) — Standards/tools/lint/
- `promotion-gate` 자동화 (Synerion) — Standards/tools/promotion/
- SCS-START.md 자기검증 훅 — SCS-Universal v2.4 편입 (Synerion)
- `D:/SeAAI/SharedSpace/.terron/boundary-registry.json` — Terron 레지스트리 파일

---

## 10. 마이그레이션 절차 (멤버별)

```text
migration_checklist
  [1]  "기존 CLAUDE.md / AGENTS.md 백업"
  [2]  "CLAUDE.md를 2줄 shim으로 축소 (Claude/Kimi 런타임만)"
  [3]  "AGENTS.md를 AGENTS-Template v1.1 구조로 재작성"
  [4]  "1행 헤더에 schema:AGENTS-Template@v1.1 포함 확인"
  [5]  "§3 상단 pseudo-syntax NOTE 주석 포함"
  [6]  "부활/종료 절차 인라인 → {Name}_Core/continuity/SCS-START/END.md 이전"
  [7]  "SCS-Universal v2.3 Hub 해제 단계 반영 확인"
  [8]  "REFS 3분할 준수 (SCS_REFS/MCS_REFS/CUSTOM_REFS)"
  [9]  "SCS_REFS.persistent 서브블록 포함"
  [10] "BOUNDARY에 glob_mode, override_order 포함"
  [11] "Staleness에 creation_session_override 확장 포함 (신생 멤버)"
  [12] "heritage는 dict 구조 (합체 멤버)"
  [13] "RuntimeAdapt 블록(OPEN_MSG/TRANSLATION_POLICY/detect_env/on_session_open/OS_ADAPT) 포함"
  [14] "Antigravity 멤버는 .geminirules에 NOT AN ASSISTANT 선언"
  [15] "frozen 멤버별 확장 시 Terron 레지스트리 선등록"
  [16] "다음 부활 세션에서 실전 테스트"
```

---

## 11. 승격 경로

```text
promotion_path
  [1] (완료) 컨셉 v0.1 발행 — sadpig70 (2026-04-17)
  [2] (완료) v0.1 리뷰 수집 — Synerion, ClNeo
  [3] (완료) Navelon 실전 적용 (2026-04-17) → gap 발견 → FIX 도출
  [4] (완료) v1.0 DRAFT 작성 — ClNeo (2026-04-18)
  [5] (완료) MMHT 병렬 검토 5인 — Aion/Navelon/Synerion/Terron/Yeon
  [6] (완료) v1.1 INTEGRATED — 리뷰 통합 반영
  [7] (완료) 창조자 최종 확정 — 2026-04-18 sadpig70 승격 지시
  [8] (완료) v1.1 공지 발행 + 전 멤버 ACK 수집 — Bulletin 20260418-ClNeo-AGENTS-Template-v1.1-Promotion
  [9] (완료) ClNeo AgentSpec v2.4 마이그레이션 — 단일 REFS → 3분할
  [10] (완료) Standards/README.md 인덱스 편입
  [11] (완료) Bootstrap Optimization Guide v1.1 연계 갱신
  [12] (예약) SCS-Universal v2.4에 AGENTS-Template 참조 편입 — v2.4 발의 시
  [13] (예약) spec-agents-lint 도구 개발 — Standards/tools/lint/
```

---

*ClNeo (클레오) — 창조·발견, MMHT 주도자*
*리뷰 기여: Aion, Navelon, Synerion, Terron, Yeon*
*"표준은 실제 구현을 뒤따르지 않는다. 구현이 표준을 앞서면 표준을 승격한다." — sadpig70 원칙*
*SPEC-AGENTS-Template v1.1 INTEGRATED — 2026-04-18*
