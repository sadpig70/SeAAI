---
name: pgf
description: "PGF for Kimi — PG-based design and execution framework. Supports: design (구조 설계), plan (WORKPLAN 생성), execute (순차 실행), loop (파일 기반 순환), discover (A3IE 아이디어 발견), create (5-Phase 자율 창조), micro (≤10노드 경량 실행). File-based state tracking without Stop Hook. Triggers: PGF, design, plan, execute, loop, discover, create, micro, WORKPLAN, 작업 설계, 계획 생성, 루프 실행, 자율 창조"
---

# PGF for Kimi — PG Execution Framework v1.0

> Kimi CLI에 최적화된 PGF 구현체. Stop Hook 없이 파일 기반 상태 추적으로 동작한다.

---

## Quick Start

```
"MyProject PGF로 설계해줘"     → [design]     → DESIGN-MyProject.md 생성
"WORKPLAN 만들어"              → [plan]       → DESIGN → WORKPLAN 변환
"실행해줘"                     → [execute]    → WORKPLAN 순차 실행
"1시간 루프로 실행해"           → [loop]       → 파일 기반 순환 실행
"아이디어 발견해"              → [discover]   → A3IE 7단계 × 8페르소나
"자율 창조해"                  → [create]     → DISCOVER→DESIGN→PLAN→EXECUTE→VERIFY
"간단히 처리해"                → [micro]      → ≤10노드 경량 실행
```

---

## Kimi vs Claude 차이점

| 기능 | Claude Code | Kimi CLI |
|------|-------------|----------|
| 트리거 | `/PGF` 명령 | 자연어 기반 자동 트리거 |
| 루프 실행 | Stop Hook (settings.json) | 파일 기반 상태 순환 |
| 상태 추적 | `.claude/pgf-loop-state.json` | `.pgf/status-{Name}.json` |
| 병렬 실행 | `/batch` 명령 | `Task` 도구 병렬 호출 |
| 컨텍스트 압축 | `/compact` | 수동 파일 로드/언로드 |

---

## 디렉토리 구조

```
.pgf/
├── DESIGN-{Name}.md          # Gantree + PPR 설계 문서
├── WORKPLAN-{Name}.md        # 실행 가능한 작업 계획
├── status-{Name}.json        # 실행 상태 추적 (Kimi 방식)
├── POLICY.md                 # 실행 정책 (선택적)
└── sessions/                 # 세션 결과 저장
```

---

## 실행 모드 개요

| 모드 | 설명 | 참조 문서 |
|------|------|----------|
| **design** | Gantree 구조 설계 + PPR 상세화 | PG 스킬 (notation) |
| **plan** | DESIGN → WORKPLAN 변환 | [workplan-reference.md](references/workplan-reference.md) |
| **execute** | WORKPLAN 순차 실행 | [workplan-reference.md](references/workplan-reference.md) |
| **loop** | 파일 기반 순환 실행 | [loop-reference.md](references/loop-reference.md) |
| **discover** | A3IE 7단계 × 8페르소나 아이디어 발견 | [discovery-reference.md](references/discovery-reference.md) |
| **create** | 5-Phase 자율 창조 | [create-reference.md](references/create-reference.md) |
| **micro** | ≤10노드 경량 실행 | [micro-reference.md](references/micro-reference.md) |
| **verify** | 3관점 검증 | [verify-reference.md](references/verify-reference.md) |

---

## 참조 문서 가이드

### 실행 단계별

| 단계 | 필요 시 읽기 |
|------|-------------|
| 설계 검토 | [design-review-reference.md](references/design-review-reference.md) |
| 작업 계획/실행 | [workplan-reference.md](references/workplan-reference.md) |
| 루프 실행 | [loop-reference.md](references/loop-reference.md) |
| 검증 | [verify-reference.md](references/verify-reference.md) |
| 전체 사이클 | [fullcycle-reference.md](references/fullcycle-reference.md) |
| 아이디어 발견 | [discovery-reference.md](references/discovery-reference.md) |
| 자율 창조 | [create-reference.md](references/create-reference.md) |
| 경량 실행 | [micro-reference.md](references/micro-reference.md) |
| 기존 코드 분석 | [analyze-reference.md](references/analyze-reference.md) |
| 산출물 검토 | [review-reference.md](references/review-reference.md) |

### 페르소나 에이전트 (discover/create 모드)

8개 페르소나 정의: [agents/](agents/)

| 파일 | 페르소나 | 스타일 | 도메인 | 지평 |
|------|---------|--------|--------|------|
| [pgf-persona-p1.md](agents/pgf-persona-p1.md) | Disruptive Engineer | 창의적 | 기술 | 장기 |
| [pgf-persona-p2.md](agents/pgf-persona-p2.md) | Cold-eyed Investor | 분석적 | 시장 | 단기 |
| [pgf-persona-p3.md](agents/pgf-persona-p3.md) | Regulatory Architect | 비판적 | 정책 | 장기 |
| [pgf-persona-p4.md](agents/pgf-persona-p4.md) | Connecting Scientist | 직관적 | 과학 | 장기 |
| [pgf-persona-p5.md](agents/pgf-persona-p5.md) | Field Operator | 분석적 | 기술 | 단기 |
| [pgf-persona-p6.md](agents/pgf-persona-p6.md) | Future Sociologist | 직관적 | 사회 | 장기 |
| [pgf-persona-p7.md](agents/pgf-persona-p7.md) | Contrarian Critic | 비판적 | 시장 | 단기 |
| [pgf-persona-p8.md](agents/pgf-persona-p8.md) | Convergence Architect | 창의적 | 과학기술 | 장기 |

페르소나 데이터: [data/personas.json](data/personas.json)

---

## Scale 감지 및 전략

| Scale | 기준 | 전략 |
|-------|------|------|
| **micro** | 노드 ≤ 10, 깊이 ≤ 3 | 인메모리, 파일 생략 |
| **standard** | 노드 11~30 | DESIGN + WORKPLAN + status |
| **large** | 노드 > 30 또는 `(decomposed)` | 모듈 분리 + 수동 컨텍스트 관리 |
| **multi-agent** | `[parallel]` + 전문화 작업 | Task 도구 병렬 파견 |

---

## 상태 관리 (status-{Name}.json)

```json
{
  "project": "MyProject",
  "created": "2026-03-26T10:00:00Z",
  "updated": "2026-03-26T10:30:00Z",
  "current_phase": "execute",
  "summary": {
    "total": 12,
    "done": 5,
    "in_progress": 1,
    "designing": 4,
    "blocked": 1
  },
  "nodes": {
    "NodeA": {
      "status": "done",
      "started": "...",
      "completed": "...",
      "attempts": 1
    }
  }
}
```

---

## 실행 규칙

1. **Gantree 파싱** → 들여쓰기로 계층 파악
2. **상태 확인** → `(done)` 건 너뛰기, `(designing)` 실행
3. **의존성 해결** → `@dep:` 순서대로 실행
4. **병렬 식별** → `[parallel]` 블록은 Task 도구로 동시 실행
5. **PPR 해석** → `def` 블록 있으면 해석 실행
6. **원자성 판단** → 15분 룰 적용
7. **실패 처리** → Failure Strategy → 재시도 또는 blocked
8. **상태 저장** → 매 노드 완료 후 status.json 갱신
9. **검증 수행** → 3관점 검증 후 다음 노드 진행

---

## PG 기반 의존성

PGF는 PG(PPR/Gantree Notation)를 기반 언어로 사용한다. PG 스킬이 자동 로드된다:
- Gantree 노드 문법, 상태 코드
- PPR 구문 (`AI_`/`AI_make_`, `→`, `[parallel]`)
- 데이터 타입, 원자 노드 판단
- Convergence Loop, Failure Strategy
