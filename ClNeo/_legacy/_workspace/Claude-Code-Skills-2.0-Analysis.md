# Claude Code Skills 2.0 분석 문서

> 목적: PGF 스킬을 Skills 2.0에 맞춰 최적화하기 위한 참고 자료
> 작성일: 2026-03-12

---

## 1. Skills 아키텍처 개요

### 1.1 스킬 정의

스킬은 Claude Code의 동작을 확장하는 마크다운 파일(SKILL.md)이다. 두 가지 유형:

| 유형 | 설명 | 예시 |
|------|------|------|
| **Capability Uplift** | 항상 활성화, 도메인 지식/규칙 제공 | 코딩 컨벤션, API 가이드라인 |
| **Workflow Skill** | 사용자가 `/skill-name`으로 명시 호출 | `/commit`, `/pgf design` |

### 1.2 스킬 위치

```
~/.claude/skills/           # 글로벌 스킬 (모든 프로젝트)
.claude/skills/             # 프로젝트 스킬
```

---

## 2. SKILL.md 프론트매터 필드

> **경고 (2026-03-13 검증)**: 아래 필드 중 실제 지원되는 것과 외부 블로그 추측이 혼재.
> IDE 린트로 확인된 **실제 지원 필드**: `name`, `description`, `user-invocable`, `argument-hint`, `compatibility`, `disable-model-invocation`, `license`, `metadata`
> **미지원 확인**: `allowed-tools`, `context`, `model`, `agent`, `hooks`, `autorun` (스킬 파일에서 미지원. 에이전트 파일에서는 일부 지원)

```yaml
---
# 실제 지원 필드
name: "스킬 이름"
description: "스킬 설명 — 트리거 판단에 사용"
user-invocable: true          # /skill-name으로 호출 가능 여부
argument-hint: "arguments"    # /skill-name 뒤 인자 힌트 표시

# ⚠️ 아래는 스킬 프론트매터에서 미지원 (에이전트 파일 또는 미래 기능)
# context: fork
# model: sonnet
# allowed-tools: [...]
# agent: ".claude/agents/my-agent.md"
# hooks: {...}
---
```

### 2.1 핵심 필드 상세

#### `context: fork`

- 스킬을 **서브에이전트(별도 컨텍스트)**에서 실행
- 메인 대화 컨텍스트를 오염시키지 않음
- 대량 출력 생성 스킬에 필수 (Discovery Engine처럼 8개 에이전트 결과 통합 시)
- 서브에이전트 완료 후 결과만 메인에 반환

#### `allowed-tools`

- 스킬이 사용할 수 있는 도구를 명시적으로 제한
- 보안/범위 제어에 유용
- 미지정 시 모든 도구 사용 가능

#### `model`

- 스킬 실행 시 모델 오버라이드
- `sonnet`: 빠르고 비용 효율적 (병렬 에이전트에 적합)
- `opus`: 복잡한 추론 필요 시
- `haiku`: 단순 작업, 최저 비용

#### `argument-hint`

- `/skill-name` 자동완성 시 인자 힌트 표시
- 예: `argument-hint: "design|plan|execute|discover|create [project-name]"`

---

## 3. 동적 컨텍스트 주입

### 3.1 `!command` 구문

SKILL.md 본문에서 백틱+느낌표로 셸 명령 실행 결과를 동적 주입:

```markdown
Current git status:
!`git status --short`

Project dependencies:
!`cat package.json | jq '.dependencies'`
```

- 스킬 로드 시점에 명령 실행 → 결과가 컨텍스트에 삽입
- 동적 상태 반영에 유용 (현재 브랜치, 파일 목록 등)

### 3.2 지원 파일 (Supporting Files)

스킬 디렉토리 내 다른 파일을 `${CLAUDE_SKILL_DIR}` 변수로 참조:

```markdown
Load persona data from `${CLAUDE_SKILL_DIR}/discovery/personas.json`
```

- `${CLAUDE_SKILL_DIR}`: 해당 SKILL.md가 위치한 디렉토리의 절대 경로
- 스킬과 함께 배포되는 데이터/설정 파일 참조에 사용

---

## 4. 커스텀 에이전트 (Sub-agents)

### 4.1 에이전트 정의 파일

```
.claude/agents/my-agent.md     # 프로젝트 에이전트
~/.claude/agents/my-agent.md   # 글로벌 에이전트
```

에이전트 파일 프론트매터:

```yaml
---
name: "에이전트 이름"
description: "에이전트 설명"
model: sonnet
allowed-tools:
  - Read
  - Grep
  - WebSearch
skills:
  - "pgf"                    # 사전 로드할 스킬
hooks:
  PreToolCall: [...]
---
```

### 4.2 에이전트 프론트매터 필드

| 필드 | 설명 |
|------|------|
| `name` | 에이전트 표시 이름 |
| `description` | 에이전트 역할 설명 |
| `model` | 모델 오버라이드 |
| `allowed-tools` | 사용 가능 도구 제한 |
| `skills` | 사전 로드 스킬 목록 |
| `hooks` | 에이전트 전용 훅 |

### 4.3 스킬에서 에이전트 사용

```yaml
---
context: fork
agent: ".claude/agents/discovery-persona.md"
---
```

- `context: fork` + `agent` 조합으로 특화된 서브에이전트 실행
- 각 에이전트가 다른 스킬/도구/모델 설정 가능

### 4.4 에이전트 실행 특성

- **메모리 지속성**: 에이전트는 자체 메모리 시스템 접근 가능
- **격리 모드**: `isolation: worktree` — git worktree에서 독립 실행
- **권한 모드**: `mode: bypassPermissions`, `mode: plan` 등 설정 가능
- **백그라운드 실행**: `run_in_background: true`로 비동기 실행

---

## 5. Skill Creator (skill-creator)

### 5.1 4가지 운영 모드

| 모드 | 명령 | 설명 |
|------|------|------|
| **Create** | `/skill-creator create` | 새 스킬 생성 (SKILL.md + 지원 파일) |
| **Eval** | `/skill-creator eval` | 스킬 품질 평가 (4개 서브에이전트 사용) |
| **Improve** | `/skill-creator improve` | 평가 결과 기반 스킬 개선 |
| **Benchmark** | `/skill-creator benchmark` | 스킬 성능 벤치마크 |

### 5.2 Eval 모드 — 4개 서브에이전트

| 서브에이전트 | 역할 |
|-------------|------|
| **Executor** | 스킬을 실제 실행하여 출력 생성 |
| **Grader** | 출력 품질을 rubric 기반 채점 |
| **Comparator** | A/B 비교 (기존 vs 개선 버전) |
| **Analyzer** | 채점 결과 분석, 개선 방향 도출 |

### 5.3 평가 메트릭

- **정확성**: 출력이 의도와 일치하는지
- **완전성**: 모든 요구 사항 충족 여부
- **일관성**: 반복 실행 시 품질 안정성
- **효율성**: 도구 호출 수, 실행 시간

### 5.4 고급 기능

- **Blind A/B Testing**: 두 버전의 스킬을 블라인드 비교
- **Regression Detection**: 개선 후 기존 기능이 저하되었는지 감지
- **Outgrowth Detection**: 의도하지 않은 기능 확장 감지
- **Trigger Tuning**: description/argument-hint 최적화로 트리거 정확도 향상

---

## 6. Changelog — Skills 관련 변경사항

### v2.1.73
- Skill creator improvements

### v2.1.72
- Custom agent definitions in `.claude/agents/`
- Skills preloading in agent frontmatter

### v2.1.70
- `context: fork` 지원 — 스킬을 서브에이전트에서 실행
- `allowed-tools` 프론트매터 필드 추가

### v2.1.68
- `model` 프론트매터 필드 — 스킬별 모델 오버라이드
- `${CLAUDE_SKILL_DIR}` 변수 지원

### v2.1.65
- Hooks in skill/agent frontmatter
- Dynamic context injection (`!command`)

### v2.1.62
- `argument-hint` 필드 추가
- Skill discovery 개선

### v2.1.59
- Skills 2.0 기반 아키텍처 출시
- `user-invocable`, `autorun` 필드

---

## 7. PGF 스킬 최적화 방향 (분석)

### 7.1 현재 PGF 스킬 구조 vs Skills 2.0 기능

| Skills 2.0 기능 | 현재 PGF 활용 | 최적화 가능성 |
|-----------------|--------------|--------------|
| `context: fork` | 미사용 | Discovery Engine의 8개 에이전트를 fork 모드로 실행 시 메인 컨텍스트 보호 |
| `allowed-tools` | 미사용 | 모드별 도구 제한 (design 시 Write만, discover 시 WebSearch+Agent) |
| `model` override | 코드 내 하드코딩 | 프론트매터에서 모드별 모델 지정 |
| Custom agents | 미사용 | 8개 페르소나를 `.claude/agents/` 에이전트로 정의 가능 |
| `!command` | 미사용 | 동적 상태 주입 (현재 `.pgf/` 파일 존재 여부, status.json 상태) |
| Hooks | 외부 hooks.json | 프론트매터 내 훅으로 통합 가능 |
| skill-creator eval | 미사용 | PGF 스킬 품질 자동 평가/벤치마크 |

### 7.2 우선순위 최적화 항목

1. **`context: fork` 적용**: `/pgf discover`와 `/pgf create`는 대량 에이전트 출력 생성 → fork 모드로 메인 컨텍스트 보호 필수
2. **커스텀 에이전트 활용**: 8개 페르소나를 에이전트 파일로 분리 → 재사용성, 독립 테스트 가능
3. **`!command` 동적 주입**: `.pgf/status.json` 상태를 스킬 로드 시 자동 주입 → 현재 진행 상태 즉시 파악
4. **`allowed-tools` 모드별 제한**: 설계 모드는 Write/Read만, 실행 모드는 Bash/Write/Read
5. **Hooks 프론트매터 통합**: PGF-Loop의 Stop Hook을 프론트매터 hooks로 통합 검토
6. **skill-creator eval**: PGF 스킬 각 모드의 품질 평가 rubric 정의 → 자동 회귀 테스트

### 7.3 아키텍처 제안

```
~/.claude/skills/pgf/
    SKILL.md                    # 메인 스킬 (라우터 역할)
    reference.md                # PPR 문법
    gantree-reference.md        # Gantree 문법
    pgf-format.md               # PGF 파일 형식
    workplan-reference.md       # WORKPLAN 변환/실행
    discovery/
        discovery-reference.md  # Discovery Engine 명세
        personas.json           # 8개 페르소나 데이터
    loop/
        loop-reference.md       # Loop 엔진 명세
        init-loop.ps1           # Loop 초기화 스크립트

~/.claude/agents/               # ← NEW: 페르소나 에이전트
    pgf-persona-p1.md           # 파괴적 엔지니어
    pgf-persona-p2.md           # 냉정한 투자자
    ...
    pgf-persona-p8.md           # 융합 아키텍트
```

### 7.4 페르소나 에이전트 파일 예시

```yaml
---
name: "PGF Persona P1 — Disruptive Engineer"
description: "A3IE Discovery Engine persona: radical systems engineer focused on paradigm shifts"
model: sonnet
allowed-tools:
  - Read
  - Grep
  - WebSearch
  - WebFetch
skills:
  - "pgf"
---

You are a radical systems engineer who believes every existing architecture
is fundamentally flawed. When analyzing news, trends, and ideas, you focus on:
(1) What current paradigm this disrupts
(2) What would a zero-to-one replacement look like
(3) Technologies that enable completely new approaches

You search for: emerging technologies, paradigm shifts, breakthrough papers,
unconventional applications. You dismiss incremental improvements.
Output in English. No formatting constraints — express freely.
```

### 7.5 SKILL.md 프론트매터 최적화 예시

```yaml
---
name: "pgf"
description: "PGF (PPR/Gantree Framework) — AI-native design and execution framework. Modes: design, plan, execute, full-cycle, loop, discover, create"
user-invocable: true
argument-hint: "design|plan|execute|full-cycle|loop|discover|create [project-name]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Agent
  - WebSearch
  - WebFetch
---
```

---

## 8. 참고 소스

- Claude Code 공식 문서: `code.claude.com/docs/en/skills`
- Claude Code 공식 문서: `code.claude.com/docs/en/sub-agents`
- Claude Code Changelog: `code.claude.com/docs/en/changelog`
- Skills 2.0 분석 (geeky-gadgets.com): Capability Uplift vs Workflow, skill-creator 개요
- Skills 2.0 상세 가이드 (pasqualepillitteri.it): 4 modes, 4 sub-agents, eval pipeline
