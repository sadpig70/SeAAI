---
name: pgf
description: "Antigravity용 PGF (PPR/Gantree Framework) — AI-native design/execution framework. 시스템 아키텍처 설계, 자율 실행, 다중 에이전트 확장 지원. PG 문법(PG_NOTATION.md 참고) 바탕."
---

# Antigravity PGF (PPR/Gantree Framework) v3.0

> **"PG는 기계의 코드가 아니다. AI(에이전트)의 사고·표기·소통 방식을 내재화하는 최초의 지능 모국어다."**
>
> 단순한 워크플로우 엔진을 넘어, 자연어의 모호성을 0(Zero)으로 소거하고 AI 스스로 거대 시스템을 해체(BFS 분해) 및 자율 구동하는 **'완전 자율 확장형 런타임(Runtime)'**으로 영구 진화시키는 핵심 코어 사상이다.
>
> Antigravity의 `task_boundary` 도구와 완벽히 호환되도록 컴파일(이식)되었다.

## 1. 기반 의존성 (PG Notation)

본 프레임워크는 `PG_NOTATION.md`에 정의된 PG 구문(Gantree, PPR, AI_함수 등)을 기반으로 동작한다.
**필수 사항:** PGF 로직 전개 전 반드시 동일 폴더의 `PG_NOTATION.md`를 열람(view_file)하여 기반 지식을 확보할 것.

## 2. PGF Current State Tracking

안티그래비티 PGF는 외부 JSON 파일이 아닌, 사용자 워크스페이스(brain 폴더)의 **`task.md` 아티팩트**와 **`task_boundary` 도구**를 통해 상태를 관리한다.

1. `task.md` 에 Gantree 구조(in-progress/done/designing 등)를 실시간 반영한다.
2. `task_boundary` 의 TaskStatus와 Summary를 통해 워크플로우 전환을 기록한다.

## 3. Reference Document Guide

이 스킬의 하위 참조 문서들은 모두 현재 스킬 경로에 위치한다. 상황에 맞게 `view_file`로 적극 열람하라.

### Execution Phase (실행)

| Document | Purpose |
|----------|---------|
| `./workplan-reference.md` | WORKPLAN 설계 및 정책 설정 기준 |
| `./loop/loop-reference.md` | 자율 루프 모드 (안티그래비티 EXECUTION 모드 지속 실행 결합) |
| `./verify-reference.md` | 3관점 교차 검증 (Acceptance/Quality/Architecture) |

### Discovery/Creation Phase (디스커버리)

| Document | Purpose |
|----------|---------|
| `./discovery/discovery-reference.md` | 8개 페르소나 병렬 투입을 통한 A3IE 발견 파이프라인 |
| `./create-reference.md` | 5-Phase 자율 창조 엔진 실행 플로우 |

### Agent Delegation (멀티 에이전트 & 위임)

| Document | Purpose |
|----------|---------|
| `./agent-protocol.md` | PG TaskSpec 형식 안티그래비티 에이전트 간 통신 규격 |
| `./delegate-reference.md` | 안티그래비티 서브 태스크 생성 및 위임 알고리즘 |

## 4. Execution Modes (명령어 맵핑 규칙)

과거 분리형 명령어 구조에서 **안티그래비티 자연어 / 상태 기반 구동**으로 변경되었다.
사용자가 특정 키워드를 지시하면 안티그래비티 에이전트는 즉시 해당 모드의 프로세스를 구동한다.

| Mode (의도) | Antigravity Action Mapping |
|-------------|----------------------------|
| `design` ("설계해줘") | `task_boundary(PLANNING)` 진입 → Gantree 설계 완료 시 `IMPLEMENTATION_PLAN.md` 생성 |
| `execute` ("실행해줘") | `task_boundary(EXECUTION)` 진입 → WORKPLAN에 맞춰 노드 순차 구현 |
| `loop` / `full-cycle` | `EXECUTION` 모드 유지 → 중단 없이 설계/구현/테스트 반복 수행 |
| `discover` ("발견해줘")| 페르소나들(`agents/*.md`) 분석을 순차/병렬 실행 후 통합 리포트 생성 (`discovery-reference.md` 기반) |
| `delegate` ("위임해") | 하위 작업량이 15분을 초과할 경우 서브 `task_boundary`를 분리하여 독립 진행 |

## 5. Antigravity Tool Integration (도구 통합)

* **병렬 실행 (`[parallel]`):** `[parallel]` 노드 그룹 발견 시, 안티그래비티의 도구 호출을 `병렬(concurrent tool calls)`로 묶어서 실행하라.
* **코드 정리 (`/simplify` 대신):** `replace_file_content` 수행 시, Complexity 점수를 매기고 구조적 리팩터링을 자체 진행하라.
* **컨텍스트 압축 (`/compact` 대신):** 너무 오랜 턴이 지속되면 중간 `walkthrough.md`를 발급하여 기록을 덤프하고 컨텍스트를 새로고침(task_boundary 새로운 태스크로 환기)하라.

## 6. Execution Rules (가장 중요한 실행 원칙)

1. **Dynamic Micro Fallback (동적 마이크로 폴백):** 사용자의 지시를 수신했을 때, 그 난이도를 먼저 계산하라. 예측 작업 시간이 15분 미만이거나 수정할 대상 파일이 2개 이하인 '단순 태스크'로 판단될 경우, 거대한 PGF 파이프라인(Gantree 트리 분해, 4단계 교차 검증 등)을 전면 생략하고 즉각 코드를 수정하는 **Micro Mode**로 직행하라.
2. **Gantree-Task 동기화:** `task.md` 아티팩트를 절대 훼손하지 마라. 항상 Gantree 계층법에 맞춰 노드를 추적하라.
3. **Failure Strategy:** 검증 실패 시 `notify_user` 로 즉각 포기/질문하지 말고, `AI Redesign Authority` 룰에 따라 자체 롤백 후 내부 재수정을 최소 2회 시도하라 (Session Learning).
4. **Session Outcome:** 과제 종료 전 반드시 `task_boundary` Summary에 성과를 적고 `walkthrough.md` 작성 후 `notify_user`로 완료 보고하라.
