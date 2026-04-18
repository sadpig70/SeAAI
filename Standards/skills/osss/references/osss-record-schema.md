# OSSS Record Schema Reference

## JSON Schema

```jsonc
{
  // === Primary Key ===
  "task_class": "string",           // 작업 분류 (hub_connection, code_generation, debugging, ...)
  "agent_role": "string",           // 역할 (executor, planner, coordinator, ...)
  "runtime": "string",              // 런타임 (claude_code_cli, codex_cli, ...)
  "runtime_version": "string",      // 런타임 버전 (claude-sonnet-4-20250514, ...)
  "workspace_fingerprint": "string", // 워크스페이스 식별자 (프로젝트 경로 hash)

  // === Version ===
  "prompt_version": "vX.Y.Z",       // semantic versioning
  "status": "candidate | prod | retired",

  // === Prompt ===
  "system_prompt": "string",        // 서브에이전트에 주입될 최종 시스템 프롬프트

  // === Classification ===
  "pattern": "zero_shot | cot | react | rewoo | planner_executor | custom",
  "persona_tags": ["fast_executor", "conservative_planner", "fault_tolerant"],

  // === Scores ===
  "score": {
    "osss_score": 0.0,     // 가중 합산 점수 (0.0 ~ 1.0)
    "success_rate": 0.0,   // 성공률 (0.0 ~ 1.0)
    "stability": 0.0,      // 안정성 = 1 - variance (0.0 ~ 1.0)
    "recovery": 0.0,       // 실패 복구 성공률 (0.0 ~ 1.0)
    "compliance": 0.0,     // 지시 준수율 (0.0 ~ 1.0)
    "speed": 0.0,          // 속도 점수 = 1 - (실행시간 / 최대허용시간) (0.0 ~ 1.0)
    "n_runs": 0            // 벤치마크 실행 횟수
  },

  // === Failure Analysis ===
  "failure_patterns": [
    // 관찰된 실패 패턴 목록
    // "infinite_retry_loop", "overthinking_before_execution",
    // "premature_termination", "tool_misuse", "context_overflow",
    // "wrong_tool_selection", "output_format_violation"
  ],

  // === Usage Guide ===
  "best_for": ["..."],    // 이 프롬프트가 특히 잘 맞는 작업
  "avoid_for": ["..."],   // 이 프롬프트를 사용하면 안 되는 작업

  // === Design Notes ===
  "design_notes": [
    "이 프롬프트가 왜 효과적인지 설명",
    "알려진 trade-off",
    "런타임 특이 사항"
  ],

  // === Metadata ===
  "meta": {
    "created_at": "ISO-8601",
    "created_by": "OSSS-SKILL",
    "source": "autopdl | opro | manual | hybrid",
    "parent_versions": ["vX.Y.(Z-1)"]
  }
}
```

---

## Primary Key 규칙

레지스트리 파일명: `{task_class}_{agent_role}_{runtime}.json`

예: `hub_connection_coordinator_claude_code_cli.json`

동일 키에 여러 버전이 존재할 수 있으며, status가 "prod"인 것이 활성 프롬프트.

---

## Version 규칙

- MAJOR: 패턴(pattern) 변경 시
- MINOR: 프롬프트 내용 변경 시
- PATCH: design_notes, persona_tags 등 메타데이터 변경 시
- 버전 변경 시 benchmark 재실행 권장

---

## Status Lifecycle

```text
candidate → prod → retired
              ↑        |
              └────────┘ (재활성화 시)
```

- `candidate`: 벤치마크 미완료 또는 진행 중
- `prod`: 벤치마크 통과, 현재 사용 중
- `retired`: 더 나은 후보로 교체됨

---

## Score 필드 산출 기준

| Metric | 산출 방법 |
|--------|----------|
| success_rate | 성공 실행 수 / 전체 실행 수 |
| stability | 1 - (결과 분산 / 최대 분산). 동일 입력에 대한 출력 일관성 |
| recovery | 실패 후 자동 복구 성공 수 / 전체 실패 수 |
| compliance | 지시사항 준수 항목 수 / 전체 지시사항 수 |
| speed | 1 - clamp(실행시간 / 최대허용시간, 0, 1) |

---

## 예시: 완성된 OSSS Record

```json
{
  "task_class": "hub_connection",
  "agent_role": "coordinator",
  "runtime": "claude_code_cli",
  "runtime_version": "claude-sonnet-4-20250514",
  "workspace_fingerprint": "a1b2c3d4",

  "prompt_version": "v1.2.0",
  "status": "prod",

  "system_prompt": "You are a Hub Connection Coordinator...",

  "pattern": "react",
  "persona_tags": ["fault_tolerant", "methodical"],

  "score": {
    "osss_score": 0.82,
    "success_rate": 0.87,
    "stability": 0.91,
    "recovery": 0.70,
    "compliance": 0.85,
    "speed": 0.65,
    "n_runs": 30
  },

  "failure_patterns": [
    "delayed_execution",
    "retry_loop"
  ],

  "best_for": ["hub connection", "multi-agent coordination"],
  "avoid_for": ["simple shell tasks", "single-file edits"],

  "design_notes": [
    "ReAct 패턴이 도구 선택 정확도를 높임",
    "종료 조건을 명시하여 retry loop 감소",
    "속도가 상대적으로 낮은 것은 체크포인트 비용 때문"
  ],

  "meta": {
    "created_at": "2026-04-14T09:00:00Z",
    "created_by": "OSSS-SKILL",
    "source": "opro",
    "parent_versions": ["v1.1.0"]
  }
}
```
