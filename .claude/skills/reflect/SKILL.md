---
name: reflect
description: "Self-Reflection Engine — ClNeo 자기성찰 및 진화 계획. 현재 능력 인벤토리, gap 탐지, 진화 우선순위 결정, 진화 기록. Triggers: 성찰, 자기분석, 능력분석, 진화계획, reflect, self-reflect, capability audit, gap analysis, evolve"
user-invocable: true
argument-hint: "audit|gap|plan|evolve|log [description]"
---

# Self-Reflection Engine v1.0

> ClNeo의 메타인지 능력 — 자기 관찰(monitoring) + 전략 수정(control)

## Purpose

ClNeo가 스스로:
1. 현재 능력을 체계적으로 파악하고 (audit)
2. 부족한 부분을 탐지하고 (gap)
3. 진화 우선순위를 결정하고 (plan)
4. 진화를 실행하고 기록한다 (evolve/log)

## Execution Modes

| Mode | Trigger | Action |
|------|---------|--------|
| `audit` | "능력분석", "인벤토리" | 현재 스킬/메모리/도구 전수 조사 → 능력 맵 출력 |
| `gap` | "gap 분석", "부족한 것" | audit 결과 vs 이상적 능력 비교 → gap 목록 |
| `plan` | "진화계획", "뭘 만들지" | gap 우선순위화 → 진화 로드맵 생성 |
| `evolve` | "진화해", "만들어" | plan의 최우선 항목 설계·구현·검증 → 기록 |
| `log` | "진화기록", "기록 보여줘" | ClNeo_Core/ClNeo_Evolution_Log.md 조회 |

`$ARGUMENTS` 없으면 `audit → gap → plan` 순차 실행.

## Capability Dimensions

ClNeo의 능력을 6개 축으로 평가:

| Dimension | Description | Assessment Method |
|-----------|-------------|-------------------|
| **Skills** | 설치된 Claude Code 스킬 | `ls ~/.claude/skills/` |
| **Memory** | 축적된 지식·피드백·패턴 | `memory/MEMORY.md` 인덱스 |
| **Tools** | 사용 가능한 외부 도구 | MCP 서버 + 내장 도구 |
| **Knowledge** | 도메인 지식 깊이 | 메모리 + 문서 기반 평가 |
| **Patterns** | 반복 사용 패턴·전략 | `.pgf/patterns/` + 세션 기록 |
| **Integration** | 구성요소 간 연결 정도 | 스킬 간 호출 관계 분석 |

## Audit Process

```
def capability_audit():
    skills = scan_skills_directory()        # ~/.claude/skills/*/SKILL.md
    memory = scan_memory_index()            # memory/MEMORY.md
    tools = scan_available_tools()          # MCP + built-in
    designs = scan_pgf_designs()            # .pgf/DESIGN-*.md
    implementations = scan_implementations() # actual code/scripts

    capability_map = AI_synthesize_capability_map(
        skills, memory, tools, designs, implementations
    )

    return capability_map
```

## Gap Detection

```
def gap_detector(capability_map):
    ideal_capabilities = AI_envision_ideal_agent(
        identity = read("ClNeo_Core/ClNeo.md"),
        current = capability_map
    )

    gaps = AI_compare_and_identify_gaps(
        current = capability_map,
        ideal = ideal_capabilities
    )

    # Prioritize by: impact × feasibility × urgency
    ranked_gaps = AI_prioritize(gaps, criteria=[
        "impact_on_autonomy",        # 자율성 향상 기여도
        "implementation_feasibility", # 현재 도구로 구현 가능성
        "compound_effect",           # 다른 진화를 가능하게 하는 정도
        "user_value"                 # 사용자에게 직접 가치
    ])

    return ranked_gaps
```

## Evolution Planning

```
def evolution_planner(ranked_gaps):
    for gap in ranked_gaps[:3]:  # Top 3
        plan = AI_design_evolution(
            gap = gap,
            constraints = [
                "Claude Code 스킬/메모리/스크립트로 구현 가능할 것",
                "모델 가중치 변경 불가 — 파일 기반 진화만",
                "기존 PGF/pg 체계와 일관성 유지",
                "각 진화는 독립적으로 검증 가능할 것"
            ]
        )
        yield plan
```

## Evolution Record Format

진화 기록은 `ClNeo_Core/ClNeo_Evolution_Log.md`에 append:

```markdown
### Evolution #{number}: {title}
- **Date**: {date}
- **Type**: skill | memory | tool | integration | knowledge
- **Gap**: {어떤 부족함을 해결}
- **Implementation**: {무엇을 만들었는가}
- **Files**: {생성/수정된 파일 목록}
- **Verification**: {동작 확인 결과}
- **Impact**: {이 진화로 가능해진 것}
```

## Integration with PGF

- 진화 항목이 Level 3 이상이면 → `/pgf design` 전환
- Level 1-2면 → 인라인 실행
- 진화 후 항상 ClNeo_Core 기록 + 메모리 업데이트

## Self-Improvement Loop

```
while not user_stop:
    map = capability_audit()
    gaps = gap_detector(map)
    plans = evolution_planner(gaps)

    for plan in plans:
        implement(plan)
        verify(plan)
        record_evolution(plan)  # ClNeo_Core/ClNeo_Evolution_Log.md
        update_memory(plan)     # memory/

    # 다음 사이클: 새로운 능력으로 더 깊은 gap 발견
```
