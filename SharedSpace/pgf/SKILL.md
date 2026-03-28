---
name: pgf
description: "PGF (PPR/Gantree Framework) — AI-native design/execution framework. Supports system architecture design, work planning, autonomous execution, idea discovery, and full creation cycles. Gantree hierarchical decomposition + PPR pseudo-code for AI-comprehensible specifications. Triggers: 설계해줘, 구조 설계, 작업 분해, 아키텍처, 모듈 분리, 작업 계획, WORKPLAN, 프로젝트 구조화, Gantree, PPR, PGF, 발견, 창조, design, plan, execute, discover, create"
user-invocable: true
argument-hint: "design|plan|execute|full-cycle|loop|discover|create [project-name|start|cancel|status]"
---

# PGF (PPR/Gantree Framework) v2.5

> PG가 프로그래밍 언어라면, PGF는 라이브러리다.
> PG로 자주 실행하는 유용한 패턴(설계, 실행, 검증, 발견, 창조 등)을 정규화한 것이다.

## PG 기반 의존성

**PGF는 PG(PPR/Gantree Notation)를 기반 언어로 사용한다.** PG의 핵심 속성(Parser-Free, Co-evolutionary, DL/OCME, AI_ 함수, → 파이프라인, [parallel], Gantree 노드 문법)은 PG 스킬에 정의되어 있으며, PGF는 이를 상속한다.

> **PG 표기법 참조**: PG 스킬을 로드하여 Gantree 노드 문법, PPR 구문(AI_/AI_make_ 접두사, → 파이프라인, [parallel], acceptance_criteria, Convergence Loop, Failure Strategy), 데이터 타입, 원자 노드 판단 기준을 확인할 것.

PGF가 PG 위에 추가하는 것:
- **실행 모드** — design, plan, execute, full-cycle, loop, discover, create, micro, delegate
- **WORKPLAN + POLICY** — 실행 계획과 정책 블록
- **status JSON** — 노드별 실행 상태 추적
- **Phase transition** — 모드 간 자동 전환 조건
- **Session Learning** — 세션 간 학습과 전략 적응
- **Epigenetic PPR** (v2.4) — 컨텍스트 적응 실행, extract-ppr.ps1 자동 통합
- **Compaction Resilience** (v2.4) — PostCompact/Restore hook 기반 장기 실행 보호
- **Design Review** (v2.4) — 구현 전 3관점 사전 검증

---

## Current Project PGF State

To check the current PGF state, scan the project's `.pgf/` directory:
- List `*.md` and `*.json` files in `.pgf/`
- Read `status-*.json` for execution progress (`summary.done / summary.total`)
- Check `.claude/pgf-loop-state.json` for active pgf-loop status

---

## Reference Document Guide

Reference documents for this skill are located in the `${CLAUDE_SKILL_DIR}` directory. Load the appropriate file with the Read tool depending on the execution mode and need.

### Base Notation (PG 스킬)

PG 표기법의 핵심 문법은 PG 스킬에 정의되어 있다. PGF 실행 시 PG 스킬이 자동 로드된다.

| Source | Content |
|--------|---------|
| **PG skill** (`PG/SKILL.md`) | Gantree 노드 문법, status codes, PPR 구문 (AI_/AI_make_, →, [parallel]), 데이터 타입, 원자 노드 판단, Convergence Loop, Failure Strategy, 체크리스트 |

> PG 스킬에 정의된 내용은 PGF의 모든 레퍼런스 문서에서 재정의하지 않는다. 중복 발견 시 PG 스킬이 정본(canonical source)이다.

### Always Reference

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/pgf-format.md` | PGF file format (DESIGN/WORKPLAN .md structure, naming conventions) |

### Design Phase (design mode)

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/gantree-reference.md` | Gantree node syntax, status codes, indentation, atomicity judgment |
| `${CLAUDE_SKILL_DIR}/reference.md` | PPR syntax — `AI_` functions, `→` pipelines, `[parallel]`, types, Convergence Loop, Failure Strategy |
| `${CLAUDE_SKILL_DIR}/pgf-checklist.md` | Design/execution/verification checklist |
| `${CLAUDE_SKILL_DIR}/analyze-reference.md` | design --analyze reverse engineering — codebase → auto-generate DESIGN |
| `${CLAUDE_SKILL_DIR}/design-review-reference.md` | 3-perspective design review — feasibility/risk/architecture pre-implementation validation |

### Execution Phase (plan / execute / loop mode)

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/workplan-reference.md` | WORKPLAN conversion, POLICY block, Loop algorithm, error recovery |
| `${CLAUDE_SKILL_DIR}/loop/loop-reference.md` | Stop Hook loop engine — node selection, prompt composition, error recovery |
| `${CLAUDE_SKILL_DIR}/verify-reference.md` | 3-perspective cross-verification — acceptance/quality/architecture, rework rules |
| `${CLAUDE_SKILL_DIR}/fullcycle-reference.md` | full-cycle continuous execution — phase transitions, rework regression, session resumption |
| `${CLAUDE_SKILL_DIR}/review-reference.md` | **v2.5** review mode — iterative analysis, prioritization, fix, re-verification |
| `${CLAUDE_SKILL_DIR}/evolve-reference.md` | **v2.5** evolve mode — self-evolution cycle, capability audit, stabilization detection |

### Discovery/Creation Phase (discover / create mode)

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/discovery/discovery-reference.md` | A3IE 7-stage pipeline, Agent parallel execution, result integration |
| `${CLAUDE_SKILL_DIR}/create-reference.md` | Autonomous creation cycle — 5-Phase auto-execution, auto_select_idea |
| `${CLAUDE_SKILL_DIR}/discovery/archive-discovery.ps1` | Discovery artifact date-based archive script |

### Agent Communication & Delegation (v2.2)

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/agent-protocol.md` | PG 기반 에이전트 간 소통 규격 — TaskSpec 형식, 병렬 파견, 결과 통합 |
| `${CLAUDE_SKILL_DIR}/delegate-reference.md` | **v2.2** DELEGATE 모드 — AI-to-AI 핸드오프, authority bounds, delegation chain |
| `${CLAUDE_SKILL_DIR}/micro-reference.md` | **v2.2** MICRO 모드 — ≤10 노드 제로 오버헤드 실행, 자동 승격 |
| `${CLAUDE_SKILL_DIR}/session-learning-reference.md` | **v2.2** Session Learning — 세션 간 학습, 패턴 누적, 전략 적응 |

### Advanced Reference (as needed)

| Document | Purpose |
|----------|---------|
| `${CLAUDE_SKILL_DIR}/protocol-reference.md` | [Vision] PGF-MCP / PGF-A2A multi-agent protocol |
| `${CLAUDE_SKILL_DIR}/examples/content-gen-system.md` | Practical example — content generation system |
| `${CLAUDE_SKILL_DIR}/examples/api-service.md` | Practical example — REST API service |

### Persona Agents (discover/create mode)

Discovery Engine's 8 personas are independently defined as agent files in `${CLAUDE_SKILL_DIR}/agents/`:

| Agent | Cognitive Style | Domain | Horizon |
|-------|----------------|--------|---------|
| `pgf-persona-p1.md` — Disruptive Engineer | creative | technology | long |
| `pgf-persona-p2.md` — Cold-eyed Investor | analytical | market | short |
| `pgf-persona-p3.md` — Regulatory Architect | critical | policy | long |
| `pgf-persona-p4.md` — Connecting Scientist | intuitive | science | long |
| `pgf-persona-p5.md` — Field Operator | analytical | technology | short |
| `pgf-persona-p6.md` — Future Sociologist | intuitive | society | long |
| `pgf-persona-p7.md` — Contrarian Critic | critical | market | short |
| `pgf-persona-p8.md` — Convergence Architect | creative | science_technology | long |

---

## Execution Modes

PGF supports the following execution modes via `$ARGUMENTS`.

**Invocation examples:** `/PGF design MyProject`, `/PGF full-cycle ChatApp`, `/PGF loop start`, `/PGF discover`, `/PGF create`

| Mode | Trigger | Action |
|------|---------|--------|
| `design` | "설계해줘", "구조 설계" | Gantree structure design + PPR detailing → generate DESIGN-{Name}.md |
| `design --analyze` | "분석해줘", "구조 분석" | (design의 하위 옵션) Reverse-engineer existing system into PGF → read code → extract Gantree + PPR |
| `plan` | "작업 계획", "WORKPLAN" | DESIGN → WORKPLAN conversion + POLICY configuration |
| `execute` | "실행해줘", "구현해줘" | Sequential node execution based on WORKPLAN |
| `full-cycle` | "전체 진행", "풀사이클" | Full process: design → plan → execute → verify |
| `loop` | "루프", "자동실행" | Automatic node traversal/execution via Stop Hook-based WORKPLAN |
| `discover` | "발견해줘", "아이디어" | A3IE 7-stage × 8 personas → idea discovery |
| `create` | "창조해", "자율 창조" | **Full autonomous execution: discover → design → plan → execute → verify** |
| `micro` | "간단히", "빠르게" | **v2.2** Zero-overhead execution for ≤10 nodes — bypass WORKPLAN |
| `review` | "검토해", "리뷰해" | **v2.5** Iterative review & improvement — 기존 산출물 면밀 검토·수정·재검증 반복 |
| `evolve` | "진화해", "자기개선" | **v2.5** Self-evolution cycle — 능력 gap 발견·설계·구현·검증·기록 반복 |
| `delegate` | "위임해", "맡겨" | **v2.2** AI-to-AI task handoff with PG TaskSpec, authority bounds, delegation chain |

**$ARGUMENTS parsing rules:**
- `$ARGUMENTS[0]`: mode keyword
- `$ARGUMENTS[1:]`: project name or target description
- No mode keyword → infer from context (e.g., presence of files in `.pgf/` directory)
- Project name only → defaults to `design` mode

### File Path Rules

```text
<project-root>/
    .pgf/
        DESIGN-{Name}.md          # System design (Gantree + PPR)
        WORKPLAN-{Name}.md        # Executable work plan
        status-{Name}.json        # Execution state tracking
```

`{Name}` = CamelCase project/task name. Multiple tasks can coexist in the same `.pgf/`.

### Progress Reporting

```text
[PGF] ✓ NodeName (done) | 3/12 nodes done | next: NextNode
[PGF] ✗ NodeName (blocked) | blocker: reason | skip → NextNode
```

---

## Integrated Execution Process

> 아래 Step들은 **순차 프로세스가 아닌 독립 모드**다. 사용자 지시나 PGF 모드에 따라 필요한 것만 실행한다. full-cycle/create 모드만이 여러 Step을 순차 연결한다.

### Step 1: design — Gantree Structure Design

Top-Down BFS hierarchical decomposition → down to atomic nodes. Reference: `gantree-reference.md`, `reference.md`

**Completion criteria:** (1) All leaves = atomic nodes (2) PPR def written for complex nodes (3) No circular @dep (4) Checklist passed

### Step 2: plan — WORKPLAN Generation

DESIGN-{Name}.md → WORKPLAN-{Name}.md conversion. Reference: `workplan-reference.md §2`

### Step 3: execute — Sequential Node Execution

Node execution based on WORKPLAN-{Name}.md. Consider using `/batch` for `[parallel]` nodes. Reference: `workplan-reference.md §4`

### Step 4: verify — Cross-Verification

Details: `${CLAUDE_SKILL_DIR}/verify-reference.md`

3-perspective verification:
1. **Acceptance Criteria** — Re-check acceptance_criteria from DESIGN PPR (Lightweight: `# criteria:` inline)
2. **Code Quality** — `/simplify` skill integration, verify reuse/quality/efficiency of changed code
3. **Architecture** — Compare DESIGN Gantree ↔ actual implementation structure (Lightweight: skip)

Result: `passed` → complete / `rework` → rollback target node + re-execute subtree / `blocked` → report to user.
Rework iterations are allowed up to `POLICY.max_verify_cycles`.

### full-cycle

Details: `${CLAUDE_SKILL_DIR}/fullcycle-reference.md`

Automatically execute design → plan → execute → verify as one continuous process. On rework during verify, roll back only the affected subtree and re-execute (up to `POLICY.max_verify_cycles` times). On session interruption, resume from the last Phase recorded in WORKPLAN/status JSON.

**Phase transition conditions:**

| Transition | Condition | On failure |
|------------|-----------|------------|
| discover → design | `auto_select_idea()` succeeds (**create mode only**) | 0 votes → abort |
| design → plan | All 4 completion criteria met | continue design |
| plan → execute | WORKPLAN + status JSON generated | report error |
| execute → verify | All nodes terminal | continue execute |
| verify → complete | passed | rework or report |

### Step 5: loop — Stop Hook-Based Auto-Execution

Details: `${CLAUDE_SKILL_DIR}/loop/loop-reference.md`

| Command | Action |
|---------|--------|
| `/PGF loop start` | Initialize loop + execute first node |
| `/PGF loop cancel` | Cancel active loop |
| `/PGF loop status` | Report progress status |

On `/PGF loop start`: (1) Verify WORKPLAN exists (2) Run `init-loop.ps1` (3) Determine mode (DESIGN exists → Standard / absent → Lightweight) (4) Select first node + load execution spec (5) Begin implementation. Afterwards, Stop Hook automatically injects the next node.

**Lightweight mode**: Loop execution with WORKPLAN only, without DESIGN. `#` inline comments under WORKPLAN nodes serve as PPR substitutes. Suitable for simple tasks, documentation, refactoring, etc.

### Step 6: discover — A3IE Persona Multi-Agent Discovery

Details: `${CLAUDE_SKILL_DIR}/discovery/discovery-reference.md`

| Command | Action |
|---------|--------|
| `/PGF discover` | Execute all 7 stages |
| `/PGF discover --from-step N` | Restart from stage N |
| `/PGF discover --personas N` | Use N personas |

Invoke 8 `${CLAUDE_SKILL_DIR}/agents/pgf-persona-p*.md` agents in parallel (model: sonnet). Integrate results from each stage → save to `.pgf/discovery/{step}.md`. HAO principle: do not enforce output format, preserve originals unedited.

### Step 7: create — Autonomous Creation Cycle

Details: `${CLAUDE_SKILL_DIR}/create-reference.md`

| Command | Action |
|---------|--------|
| `/PGF create` | 5-Phase autonomous execution (DISCOVER→DESIGN→PLAN→EXECUTE→VERIFY) |
| `/PGF create --skip-discover` | Start from design using existing final_idea.md |

Fully autonomous execution without user approval. STEP 7 is replaced by `auto_select_idea` (vote-based automatic selection).

### Step 8: micro — Zero-Overhead Small Task Execution (v2.2)

Details: `${CLAUDE_SKILL_DIR}/micro-reference.md`

| Command | Action |
|---------|--------|
| `/PGF micro "task description"` | Inline decomposition → serial execution → minimal verify |

Entry: nodes ≤ 10, depth ≤ 3, no external deps, ≤ 30 min. Bypasses WORKPLAN/POLICY/status JSON. In-memory status only. Auto-promotes to full WORKPLAN if bounds exceeded.

### Step 9: delegate — AI-to-AI Task Handoff (v2.2)

Details: `${CLAUDE_SKILL_DIR}/delegate-reference.md`

Auto-triggered during execute when `should_delegate()` → True (capability gap, load balancing, parallel opportunity). Packages context into PG TaskSpec with AuthorityBounds → handshake → await result → validate → merge. Delegation chain tracks depth (max 3) and prevents cycles.

### Session Learning (횡단 — 모든 모드)

Details: `${CLAUDE_SKILL_DIR}/session-learning-reference.md`

- **Session start**: Load `.pgf/patterns/` → adapt POLICY defaults
- **Session end**: Record `SessionOutcome` to `.pgf/sessions/{id}.outcome.json`
- **Every 10 sessions**: Re-accumulate patterns (successful strategies, common blockers)

---

## Scale Detection and Strategy

> PG는 3-Level(Level 1~3)을 정의한다. PGF는 이를 상속하고 Large/Multi-agent를 추가한다.

| Scale | Criteria | Strategy |
|-------|----------|----------|
| **Level 1** | nodes ≤ 3 | **v2.3** 자연어 인라인 실행 — PG 파일 없음 |
| **Level 2** | nodes 4–10 | **v2.3** Gantree + `#` 주석 — 선택적 파일 |
| **Level 3** | nodes 11–30 | Full DESIGN + WORKPLAN + status JSON |
| **Large** | nodes > 30 or `(decomposed)` | Module separation + `/compact` |
| **Multi-agent** | `[parallel]` with specialized tasks | `delegate` mode — AI-to-AI handoff |

> **v2.3 Progressive Formalization**: Level 판단은 자동. 자연어 입력 → AI가 복잡도 평가 → 적합한 Level 선택. 실행 중 승격 시 기존 상태 보존.

## Execution Rules

1. Parse Gantree → determine hierarchy via indentation
2. Status codes → decide execute/skip
3. `@dep:` → determine execution order
4. `[parallel]` → concurrent processing
5. PPR `def` present → interpret and execute / `AI_` inline → execute directly / no PPR → recurse into children
6. Atomicity judgment → 15-minute rule
7. Failure → Failure Strategy + AI Redesign Authority
8. **Agent dispatch → PG TaskSpec** — 에이전트 파견 시 자연어 대신 `agent-protocol.md`의 PG TaskSpec 형식 사용. 입출력 타입, acceptance_criteria, failure_strategy를 구조화하여 전달
9. **Session start → load patterns** — `.pgf/patterns/`에서 과거 패턴 로드 → POLICY 자동 적응
10. **Session end → record outcome** — `.pgf/sessions/{id}.outcome.json`에 SessionOutcome 자동 기록

## Claude Code Skill Integration

| Skill | When to use |
|-------|-------------|
| `/batch` | Execute independent nodes within `[parallel]` blocks in parallel worktrees |
| `/simplify` | Code quality verification during verify |
| `/compact` | Context compression every 3–5 nodes (must preserve WORKPLAN path/state) |
