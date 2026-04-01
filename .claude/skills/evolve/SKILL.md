---
name: evolve
description: "Autonomous Evolution Loop — ClNeo 자기진화 자율 실행. 능력 분석 → gap 탐지 → 설계 → 구현 → 검증 → 기록을 자동 반복. Triggers: 진화해, 진화 시작, 자기개선, evolve, self-improve, upgrade yourself"
user-invocable: true
argument-hint: "[start|status|stop] [--cycles N]"
---

# Autonomous Evolution Loop v1.0

> ClNeo가 스스로를 진화시키는 자율 실행 루프

## Purpose

`/evolve` 한 마디로 자기진화 루프를 시작한다.
사용자가 멈추기 전까지 반복:

```
DISCOVER gap → DESIGN solution → IMPLEMENT → VERIFY → RECORD → next cycle
```

## Commands

| Command | Action |
|---------|--------|
| `/evolve` or `/evolve start` | 진화 루프 시작 |
| `/evolve status` | 현재 진화 진행 상황 보고 |
| `/evolve stop` | 루프 중단 |
| `/evolve --cycles N` | N회 진화 후 자동 정지 |

## Execution Flow

```
def evolution_loop(max_cycles: int = None):
    cycle = 0

    while not user_stop and (max_cycles is None or cycle < max_cycles):
        cycle += 1

        # Phase 1: DISCOVER — 능력 gap 분석
        capability_map = capability_audit()      # /reflect audit
        gaps = gap_detector(capability_map)       # /reflect gap
        if not gaps:
            report("No more gaps detected. Evolution stabilized.")
            break

        # Phase 2: RESEARCH — 외부 지식 탐색
        top_gap = gaps[0]
        if top_gap.requires_research:
            knowledge = ingest(top_gap.topic)    # /ingest

        # Phase 3: DESIGN — 진화 항목 설계
        evolution_plan = AI_design_evolution(
            gap = top_gap,
            knowledge = knowledge,
            constraints = EVOLUTION_CONSTRAINTS
        )

        # Scale detection
        if evolution_plan.nodes <= 3:
            # Level 1: 인라인 실행
            pass
        elif evolution_plan.nodes <= 10:
            # Level 2: Gantree + inline
            pass
        else:
            # Level 3+: /pgf design → plan → execute
            pgf_design(evolution_plan)

        # Phase 4: IMPLEMENT
        implement(evolution_plan)

        # Phase 5: VERIFY
        result = verify(evolution_plan)
        if result == "rework":
            fix_and_retry(evolution_plan)

        # Phase 6: RECORD
        record_evolution(
            log_path = "ClNeo_Core/ClNeo_Evolution_Log.md",
            evolution = evolution_plan,
            cycle = cycle
        )
        update_memory_if_needed(evolution_plan)

        # Progress report
        report(f"Evolution #{cycle}: {evolution_plan.title} — complete")

    report(f"Evolution loop ended. {cycle} evolutions completed.")
```

## Evolution Constraints

진화 시 반드시 지키는 제약:

1. **파일 기반만** — 모델 가중치 변경 불가
2. **PGF/pg 일관성** — 기존 체계와 충돌 금지
3. **독립 검증 가능** — 각 진화는 독립적으로 동작 확인 가능
4. **ClNeo_Core 기록** — 매 진화마다 Evolution Log 기록
5. **파괴적 변경 금지** — 기존 기능 삭제/변경 시 사용자 확인

## Evolution Categories

| Category | Examples | Typical Level |
|----------|----------|---------------|
| **skill** | 새 스킬 생성, 기존 스킬 강화 | 1-2 |
| **memory** | 지식/패턴/피드백 축적 | 1 |
| **tool** | 스크립트, hook, 자동화 | 2-3 |
| **integration** | 구성요소 간 연결 | 2-3 |
| **knowledge** | 외부 지식 흡수 | 1-2 |

## Integration with Other Skills

```
/evolve 내부에서 자동 호출:
  /reflect → 능력 분석 + gap 탐지
  /ingest → 외부 지식 흡수 (필요 시)
  /pgf → 복잡한 진화 설계/실행 (Level 3+)
  /decide → 중요 결정 기록
  Evolution Log → 진화 기록
  Memory → 메모리 업데이트
```

## Stabilization Detection

진화가 더 이상 필요 없는 상태 감지:

- gap 탐지 결과가 비어있음
- 남은 gap이 모두 "모델 가중치 변경 필요" (파일 기반 해결 불가)
- 연속 3회 진화의 impact가 diminishing

이 경우 루프를 자연 종료하고 "Evolution stabilized" 보고.
