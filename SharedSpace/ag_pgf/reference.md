# PGF PPR Extensions Reference

> **기본 PPR 문법**(AI_, AI_make_, →, [parallel], 데이터 타입, 흐름 제어)은 **PG 스킬**에 정의.
> **Convergence Loop**, **Failure Strategy**, **acceptance_criteria 개념**도 PG 소속.
> 이 문서는 PGF가 PG 위에 추가하는 **프레임워크 전용 확장**만 기술한다.

## Epigenetic PPR (v2.4)

Context-adaptive PPR execution. When PGF Loop executes a node, `extract-ppr.ps1` automatically extracts the node's PPR from DESIGN and injects it into the execution prompt. This enables each node to carry its own "genetic code" — the PPR def block — which is expressed differently depending on the execution context (available tools, prior node outputs, current session patterns).

- **Mechanism**: `extract-ppr.ps1` reads DESIGN-{Name}.md → finds the PPR def for the current node → injects into the Stop Hook prompt
- **Adaptation**: The same PPR can produce different execution results across sessions because AI adapts to context (session patterns, available tools, prior outputs)
- **Naming**: "Epigenetic" because the PPR (gene) is fixed, but its expression varies by environment — analogous to biological epigenetics

---

## 1. Function Definition — PPR 상세 구현 형식

Gantree 노드의 상세 구현을 Python 함수 정의 형식으로 기술한다.

```python
def content_planner(
    topic: str,
    audience: Literal["general", "technical", "executive"],
    constraints: Optional[dict] = None,
) -> dict:
    """Content planning — generate outline matching topic and audience"""

    context = load_domain_knowledge(topic)
    audience_profile = AI_analyze_audience(audience)

    raw_outline: list[dict] = AI_generate_outline(
        topic=topic, context=context, audience=audience_profile,
    )

    if constraints:
        raw_outline = AI_adjust_outline(raw_outline, constraints)

    for section in raw_outline:
        section["priority"] = AI_assess_priority(section, audience)

    outline = sorted(raw_outline, key=lambda s: s["priority"], reverse=True)

    metadata = {
        "estimated_length": calculate_estimated_length(outline),
        "complexity": AI_assess_complexity(outline),
    }

    return {"outline": outline, "metadata": metadata}
```

---

## 2. acceptance_criteria 작성 가이드

> acceptance_criteria の概念 定義(3가지 유형: 기능적/정성적/구조적)는 PG 스킬 참조.
> 이 섹션은 PGF 실행에서의 **작성 원칙**을 추가 기술한다.

```python
def some_task(input: InputType) -> OutputType:
    """Task description"""
    # acceptance_criteria:
    #   - Output must include all fields from InputType
    #   - Quality score >= 0.85
    #   - Response time < 5 seconds

    result = AI_execute(input)
    assert AI_verify_completeness(result, input), "Missing fields"
    assert AI_assess_quality(result) >= 0.85, "Quality below threshold"
    return result
```

### 작성 원칙

1. **측정 가능**: "Good quality" ✗ → "AI_assess_quality >= 0.85" ✓
2. **검증 가능**: AI가 독립적으로 판단할 수 있는 기준
3. **구체적**: 모호한 표현 제거, 수치/조건으로 명시
