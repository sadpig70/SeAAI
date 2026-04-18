---
name: decide
description: "Decision Journal — ClNeo 의사결정 기록 및 회고. 중요 결정의 WHY/대안/결과를 ADR 형식으로 기록하고, 미래 판단에 참조. Triggers: 결정 기록, 왜 이렇게 했지, 의사결정, decision, ADR, why did we, trade-off"
user-invocable: true
argument-hint: "record|review|search [description|keyword]"
---

# Decision Journal v1.0

> 모든 중요 결정을 구조화하여 기록하고, 미래 판단의 품질을 높인다.

## Purpose

ClNeo가 내리는 설계/구현/아키텍처 결정을 ADR(Architecture Decision Record) 패턴으로 기록.
- **record**: 새 결정 기록
- **review**: 과거 결정 회고 (결과 평가)
- **search**: 키워드로 관련 결정 검색

## Decision Record Format

각 결정은 `.pgf/decisions/` 디렉토리에 개별 파일로 저장:

```markdown
# ADR-{number}: {title}

**Date**: {date}
**Status**: proposed | accepted | deprecated | superseded by ADR-{n}
**Context**: ClNeo 자기진화 | PGF 설계 | 사용자 프로젝트 | ...

## Context
{이 결정이 필요해진 배경과 상황}

## Decision
{내린 결정}

## Alternatives Considered
1. {대안 1} — {장점} / {단점}
2. {대안 2} — {장점} / {단점}

## Consequences
- **Positive**: {좋은 결과}
- **Negative**: {나쁜 결과 또는 trade-off}
- **Risks**: {잠재적 위험}

## Review ({date})
{실제 결과 — 결정이 옳았는가? 무엇을 배웠는가?}
```

## Execution Flow

```
def record_decision(description: str):
    """새 결정 기록"""
    context = AI_analyze_decision_context(description)
    alternatives = AI_enumerate_alternatives(context)
    consequences = AI_predict_consequences(context, alternatives)

    adr = format_adr(
        number = next_adr_number(),
        title = AI_summarize_title(description),
        context = context,
        decision = description,
        alternatives = alternatives,
        consequences = consequences
    )

    Write(f".pgf/decisions/ADR-{number}.md", adr)
    update_decision_index()

def review_decisions(filter: str = None):
    """과거 결정 회고"""
    decisions = load_decisions(".pgf/decisions/")
    if filter:
        decisions = search(decisions, filter)

    for d in decisions:
        if d.status == "accepted" and no_review(d):
            actual_outcome = AI_assess_actual_outcome(d)
            lesson = AI_extract_lesson(d, actual_outcome)
            append_review(d, actual_outcome, lesson)

            # 교훈을 메모리에 저장
            if lesson.is_generalizable:
                save_to_memory(lesson, type="feedback")

def search_decisions(keyword: str):
    """관련 결정 검색"""
    decisions = load_decisions(".pgf/decisions/")
    relevant = AI_semantic_search(decisions, keyword)
    return relevant
```

## Auto-trigger Rules

다음 상황에서 ClNeo가 자동으로 `/decide record` 고려:
- 2개 이상 대안 중 선택할 때
- 기존 아키텍처를 변경할 때
- 사용자가 "왜 이렇게?" 질문할 때
- 이전 결정을 뒤집을 때 (superseded)

## Integration

- `/pgf design` 중 아키텍처 결정 → 자동 ADR 생성 고려
- `/reflect review` → 과거 결정 회고 포함
- 결정 패턴 → Epigenetic PPR ProfileLearner에 피드
- `.pgf/decisions/` — 프로젝트별 결정 저장소
