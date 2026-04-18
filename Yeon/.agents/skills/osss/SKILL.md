---
name: osss
description: "OSSS (Optimized System Prompt for Subagent Spawning) — 서브에이전트 스폰 시 시스템 프롬프트를 사전 최적화하는 스킬. AutoPDL+OPRO 기반 프롬프트 후보 생성·벤치마크·평가·선택·레지스트리 저장. Triggers: 프롬프트 최적화, subagent prompt, spawn prompt, 에이전트 프롬프트 설계, OSSS, 스폰 최적화, prompt optimization, benchmark prompt, 서브에이전트 시스템 프롬프트, agent spawning, prompt registry, 프롬프트 벤치마크, 최적 프롬프트 선택. Use this skill whenever the user wants to design, test, compare, or manage system prompts for spawning subagents — even if they just say 'make a good prompt for this agent' or 'why does my agent keep failing'."
---

# OSSS: Optimized System Prompt for Subagent Spawning

> 에이전트의 "출생 정책"을 검증 기반으로 설계하는 시스템.
> Agent Performance ≈ f(System Prompt, Task, Runtime Context)

## Core Philosophy

1. 서브에이전트의 시스템 프롬프트는 초기 정책(policy)을 결정한다
2. 동일 작업이라도 프롬프트에 따라 성공률이 크게 달라진다
3. **No global registry** — 런타임·워크스페이스별 로컬 최적화
4. OSSS는 직접 작업을 실행하지 않는다 — 프롬프트만 설계·평가·선택한다

---

## Reference Documents

| Document | Purpose | When to load |
|----------|---------|--------------|
| `references/osss-record-schema.md` | OSSS Record JSON 스키마, 필드 정의, 예시 | generate, benchmark 결과 저장 시 |
| `references/prompt-design-guidelines.md` | 프롬프트 설계 6원칙, 패턴별 가이드, 안티패턴 | generate 모드 |
| `references/scoring-engine.md` | ScoreEngine 공식, 가중치, 평가 지표, FailureAnalyzer 패턴 | benchmark, analyze 모드 |

---

## Execution Modes

| Mode | Trigger | Action |
|------|---------|--------|
| `generate` | "OSSS로 프롬프트 생성해줘", "subagent prompt 만들어", "프롬프트 설계해" | 작업 프로파일링 → 후보 프롬프트 N개 생성 → OSSS Record 출력 |
| `benchmark` | "벤치마크 실행해줘", "프롬프트 테스트" | 후보 프롬프트별 N회 반복 실행 → 통계 수집 → 최적 선택 |
| `select` | "최적 프롬프트 선택해줘", "prod 프롬프트 알려줘" | 레지스트리에서 (task_class, agent_role, runtime) 기반 최적 프롬프트 조회 |
| `registry` | "레지스트리 보여줘", "OSSS 레지스트리 상태" | `.osss/registry/` 내용 조회·관리 |
| `analyze` | "실패 분석해줘", "왜 이 프롬프트가 실패하는지" | 실행 로그 → FailureAnalyzer → OPRO 메타최적화 → 개선 프롬프트 생성 |

---

## Directory Structure

```text
<project-root>/
    .osss/
        registry/
            {task_class}_{agent_role}_{runtime}.json   # OSSS Records
        benchmarks/
            {timestamp}_{task_class}/
                candidate-{N}/
                    run-{i}.log                         # 개별 실행 로그
                    result.json                         # 실행 결과
                summary.json                            # 벤치마크 요약
        prompts/
            {task_class}_{agent_role}_v{X.Y.Z}.txt     # 프롬프트 원본
```

---

## Mode Details

### 1. generate — 후보 프롬프트 생성

**입력 수집** (사용자에게 확인):
- `task_description`: 서브에이전트가 수행할 작업
- `task_class`: 작업 분류 (code_generation, debugging, hub_connection, coordination 등)
- `agent_role`: 역할 (executor, planner, coordinator, fault_tolerant_operator 등)
- `runtime`: 실행 환경 (claude_code_cli, codex_cli, local_python, autogen 등)
- `workspace_context`: 프로젝트 언어, 구조, 제약 조건

**실행 흐름**:
1. Load `references/prompt-design-guidelines.md`
2. 작업 특성 분석 → 적합한 패턴 선택 (zero_shot, cot, react, rewoo, planner_executor)
3. 후보 프롬프트 2~4개 생성 (각각 다른 전략)
4. Load `references/osss-record-schema.md`
5. 각 후보를 OSSS Record JSON으로 출력 (status: "candidate", n_runs: 0)
6. `.osss/prompts/`에 프롬프트 텍스트 저장
7. `.osss/registry/`에 candidate 레코드 저장

**후보 전략 예시**:
- **Candidate A**: Fast Executor — 최소 사고, 즉시 실행, 명확한 종료 조건
- **Candidate B**: Conservative Planner — 단계별 계획 후 실행, 체크포인트
- **Candidate C**: Fault-Tolerant — 실패 복구 강조, 재시도 정책 명시

### 2. benchmark — 벤치마크 실행

**전제**: `generate`로 후보가 `.osss/registry/`에 존재

**실행 흐름**:
1. 후보 프롬프트 로드
2. 각 후보별 N회 실행 (`claude -p` 서브에이전트 스폰)

```bash
# 각 후보 프롬프트로 서브에이전트 스폰 (런타임별)
# Claude Code:
claude -p "TASK_PROMPT" --system-prompt "CANDIDATE_SYSTEM_PROMPT" 2>&1 | tee .osss/benchmarks/{ts}_{class}/candidate-{n}/run-{i}.log

# Kimi CLI:
uv tool run kimi --yolo -p "TASK_PROMPT" --system-prompt "CANDIDATE_SYSTEM_PROMPT" 2>&1 | tee .osss/benchmarks/{ts}_{class}/candidate-{n}/run-{i}.log
```

3. 실행 결과 수집: 성공/실패, 소요 시간, 재시도 횟수, 도구 사용 정확도
4. Load `references/scoring-engine.md`
5. ScoreEngine으로 각 후보 점수 계산
6. 최고 점수 후보를 `status: "prod"`로 승격
7. 레지스트리 업데이트

**벤치마크 규모 가이드**:
- 빠른 검증: 5회/후보
- 표준: 10회/후보
- 정밀: 30회/후보

### 3. select — 최적 프롬프트 선택

```bash
# 레지스트리 조회
python3 scripts/registry.py select \
  --task-class "code_generation" \
  --agent-role "executor" \
  --runtime "kimi_cli"
```

status가 "prod"인 레코드 중 osss_score가 가장 높은 프롬프트를 반환.

### 4. registry — 레지스트리 관리

```bash
# 전체 레지스트리 조회
python3 scripts/registry.py list

# 특정 레코드 상세 조회
python3 scripts/registry.py show --key "code_generation_executor_kimi_cli"

# 레코드 상태 변경 (prod → retired)
python3 scripts/registry.py retire --key "..."

# 레지스트리 통계
python3 scripts/registry.py stats
```

### 5. analyze — 실패 분석 + OPRO 메타최적화

**입력**: 실패한 실행 로그 또는 벤치마크 결과

**실행 흐름**:
1. 실패 로그에서 패턴 추출 (FailureAnalyzer)
2. 기존 프롬프트의 강점·약점 요약
3. OPRO 메타최적화: 실패 패턴을 반영한 개선 프롬프트 생성
4. 개선된 프롬프트를 새 candidate로 레지스트리에 추가
5. `parent_versions` 필드에 원본 버전 기록

---

## OPRO Meta-Optimization

기존 프롬프트 + 실행 결과가 있을 때, 자연어 추론으로 프롬프트를 개선하는 루프:

```text
Previous prompts + scores + failure_patterns
→ Summarize strengths/weaknesses
→ Generate improved candidate
→ Benchmark
→ Compare scores
→ If improved: promote / Else: retain previous
```

핵심 개선 전략:
- 종료 조건 명시 (infinite retry loop 방지)
- 도구 사용 정책 구체화 (tool misuse 방지)
- 사고 깊이 조절 (overthinking 방지)
- 실패 복구 절차 추가 (premature termination 방지)

---

## Integration Points

| System | Integration |
|--------|-------------|
| **PGF** | `generate` 시 Gantree 구조 활용 가능. 복잡한 프롬프트 설계를 PGF design 모드로 분해 |
| **SeAAIHub** | 멀티에이전트 환경에서 각 에이전트별 최적 프롬프트 관리 |
| **SCS** | 세션 간 OSSS 레지스트리 상태 보존 |
| **Claude Code** | `claude -p` 기반 서브에이전트 스폰, `/batch`로 병렬 벤치마크 |
| **Kimi CLI** | `kimi --yolo -p` 또는 `Task` 도구 기반 서브에이전트 스폰. 파일 기반 상태 추적 |

---

## Quick Start

```text
1. "OSSS로 'TCP 허브 연결 에이전트' 프롬프트 생성해줘"
   → 3개 후보 프롬프트 생성 + .osss/registry/ 저장

2. "벤치마크 10회 실행해줘"
   → 후보별 10회 실행 + 점수 산출 + 최적 선택

3. "hub_connection 용 prod 프롬프트 보여줘"
   → prod 상태 최적 프롬프트 반환

4. "최근 벤치마크 실패 분석해줘"
   → 실패 패턴 분석 + 개선 프롬프트 생성
```
