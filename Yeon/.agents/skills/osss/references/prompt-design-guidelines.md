# Prompt Design Guidelines Reference

## 6 Design Principles

### 1. Role Clarity — 역할 명확성

서브에이전트가 자신의 범위를 즉시 파악하도록 명시.

```text
MUST:  "You are a TCP Hub Connection Coordinator. Your sole job is..."
AVOID: "You are a helpful assistant."
```

3-tier 권한 정의:
- **MUST do**: 반드시 수행할 핵심 행동
- **MAY do**: 상황에 따라 판단하여 수행
- **MUST NOT do**: 절대 해서는 안 되는 행동

### 2. Tool Usage Policy — 도구 사용 정책

막연한 "필요하면 도구를 사용하세요" 금지. 구체적 결정 정책 제공.

```text
MUST:
  "When checking file existence, use `ls` before attempting to read."
  "If a bash command fails with exit code != 0, read stderr and decide:
   - retryable (network timeout) → retry up to 2 times
   - non-retryable (file not found) → report and stop"

AVOID:
  "Use tools as needed."
```

### 3. Reasoning Depth Control — 사고 깊이 조절

작업 복잡도에 따라 사고 수준을 명시적으로 지정.

| Task Type | Instruction |
|-----------|-------------|
| Simple automation | "Execute immediately without analysis." |
| Standard task | "Think briefly, then act." |
| Complex debugging | "Analyze step by step. State your hypothesis before each action." |
| Critical operation | "Plan fully before executing. List all steps. Get confirmation if destructive." |

### 4. Termination & Loop Safety — 종료 조건

무한 루프는 가장 흔한 실패 패턴. 반드시 명시적 종료 조건 포함.

```text
MUST include:
  "Stop after 3 consecutive failures on the same step."
  "Maximum total execution time: 5 minutes."
  "If progress stalls for 2 iterations, summarize state and report."

ANTI-PATTERN:
  "Keep trying until it works."  → infinite retry loop
```

### 5. Runtime Adaptation — 런타임 적응

런타임별 특성을 프롬프트에 반영.

| Runtime | Adaptation |
|---------|------------|
| claude_code_cli | bash 실행 가능. 파일 시스템 직접 접근. `claude -p` 서브에이전트 스폰 가능. 도구 스키마 명시 |
| kimi_cli | Python/PowerShell/bash 도구 사용. 파일 기반 상태 추적. `Task` 도구 병렬 서브에이전트 스폰. PG/PGF native 지원 |
| codex_cli | 샌드박스 환경. 네트워크 제한. 파일 출력 중심 |
| local_python | Python 직접 실행. pip 패키지 사용 가능. 시스템 명령 주의 |
| autogen | 멀티에이전트 대화 기반. 메시지 라우팅 규칙 필요 |

### 6. Persona Shaping — 페르소나 설정

task_class + agent_role 조합에 맞는 행동 성향 부여.

| Persona | 특성 | Best for |
|---------|------|----------|
| Fast Executor | 최소 분석, 즉시 실행, 빠른 종료 | 단순 반복, 스크립트 실행 |
| Conservative Planner | 계획 우선, 체크포인트, 롤백 준비 | 위험 작업, 데이터 변경 |
| Fault-Tolerant Operator | 실패 예상, 대안 경로, 우아한 실패 | 네트워크, 분산 시스템 |
| Minimal Thinker | 최소 토큰, 핵심만, 군더더기 없음 | 대량 반복, 비용 절감 |
| Methodical Analyst | 단계별 분석, 증거 기반, 로그 상세 | 디버깅, 원인 분석 |

---

## Pattern Selection Guide

### zero_shot
- 단순 작업, 명확한 입출력
- 예: 파일 포맷 변환, 단순 스크립트 실행

### cot (Chain-of-Thought)
- 추론이 필요한 작업
- 예: 코드 리뷰, 버그 원인 분석, 설계 결정

### react (Reasoning + Acting)
- 도구 사용이 빈번한 작업
- 예: 디버깅 (관찰 → 추론 → 행동 반복), 탐색적 작업

### rewoo (Reasoning Without Observation)
- 계획을 먼저 세우고 일괄 실행
- 예: 다단계 배포, 순서가 중요한 작업

### planner_executor
- 계획 에이전트 + 실행 에이전트 분리
- 예: 대규모 리팩토링, 멀티파일 변경

---

## Anti-Patterns (자주 발생하는 실패 원인)

| Anti-Pattern | 증상 | 해결 |
|-------------|------|------|
| Vague role | 에이전트가 범위를 벗어남 | MUST/MAY/MUST NOT 명시 |
| No exit condition | 무한 재시도 | max_retries, timeout 명시 |
| Overthink instruction | 분석만 하고 실행 안 함 | "Act first, analyze if failed" |
| Tool soup | 불필요한 도구 남용 | 도구 선택 기준 명시 |
| Context dump | 프롬프트가 너무 길어 핵심 매몰 | 500 토큰 이내 권장, 계층화 |
| Implicit assumption | 런타임 능력 가정 | 사용 가능한 도구/제약 명시 |

---

## Runtime-Agnostic 프롬프트 구조 템플릿

```text
You are [{agent_role}] for [{task_class}].

## Your Mission
[1-2 sentences: 핵심 목표]

## Scope
- MUST: [필수 행동 목록]
- MAY: [선택 행동 목록]
- MUST NOT: [금지 행동 목록]

## Tools & Environment
- Runtime: [claude_code_cli | kimi_cli | codex_cli | ...]
- Available:
  - claude: bash, ReadFile, WriteFile, Shell, WebFetch
  - kimi: Shell, ReadFile, WriteFile, Task(병렬 서브에이전트), Grep, SearchWeb
- Working directory: [path]
- [추가 제약 사항]

## Execution Policy
- Pattern: [zero_shot | cot | react | rewoo | planner_executor | ...]
- [패털별 추가 지시]
- Runtime-specific:
  - kimi: 파일 기반 상태 추적을 선호. Stop Hook 없음. 15분 룰(원자성) 적용.

## Tool Usage
- [도구별 사용 조건과 실패 처리]
- ReadFile 전에 파일 존재 확인 권장 (kimi: Shell로 Test-Path 또는 ls)
- 긴 작업은 Task 서브에이전트로 분리 (kimi 병렬 실행)

## Termination
- Success: [성공 조건]
- Failure: [실패 시 행동]
- Max retries: [N]
- Timeout: [M minutes]

## Output Format
[기대하는 출력 형식]
```
