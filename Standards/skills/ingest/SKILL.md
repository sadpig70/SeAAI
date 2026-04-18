---
name: ingest
description: "Knowledge Ingestion Pipeline — 외부 지식을 구조화하여 ClNeo 메모리에 축적. 검색 → 추출 → 분류 → 저장 → 연결. Triggers: 지식 흡수, 학습해, 조사해, 리서치, 알아봐, ingest, research, learn about, study"
user-invocable: true
argument-hint: "topic [--depth shallow|deep] [--save]"
---

# Knowledge Ingestion Pipeline v1.0

> 외부 지식을 ClNeo의 영구 메모리로 변환하는 파이프라인

## Purpose

ClNeo가 새로운 도메인 지식을 체계적으로:
1. **탐색** (Search) — 다각도 검색으로 원천 수집
2. **추출** (Extract) — 핵심 개념·관계·패턴 추출
3. **구조화** (Structure) — 메모리 형식으로 변환
4. **저장** (Store) — memory/ 에 영구 저장
5. **연결** (Connect) — 기존 지식과 교차 참조

## Execution Flow

```
def ingest(topic: str, depth: str = "deep"):
    """외부 지식 → ClNeo 메모리 파이프라인"""

    # Phase 1: Multi-angle Search
    [parallel]
        primary = WebSearch(f"{topic} overview fundamentals 2026")
        trends = WebSearch(f"{topic} latest trends developments 2026")
        technical = WebSearch(f"{topic} technical architecture implementation")
        critique = WebSearch(f"{topic} limitations criticism alternatives")

    # Phase 2: Knowledge Extraction
    raw_knowledge = AI_extract_structured_knowledge(
        sources = [primary, trends, technical, critique],
        extract = [
            "core_concepts",      # 핵심 개념 정의
            "key_relationships",  # 개념 간 관계
            "patterns",           # 반복되는 패턴
            "tools_and_methods",  # 도구/방법론
            "open_questions",     # 미해결 질문
            "relevance_to_clneo"  # ClNeo에 적용 가능한 것
        ]
    )

    # Phase 3: Quality Filter
    filtered = AI_assess_reliability(
        knowledge = raw_knowledge,
        criteria = [
            "source_credibility",  # 출처 신뢰도
            "recency",             # 최신성
            "consensus_level",     # 합의 수준 (정설 vs 논쟁중)
            "actionability"        # 실행 가능성
        ]
    )

    # Phase 4: Memory Formatting
    memory_file = AI_format_as_memory(
        knowledge = filtered,
        type = "reference",  # or "project" if project-specific
        template = """
        ---
        name: knowledge_{topic_slug}
        description: {one_line_summary}
        type: reference
        ---

        # {Topic}

        ## Core Concepts
        {concepts}

        ## Key Relationships
        {relationships}

        ## Patterns & Best Practices
        {patterns}

        ## Tools & Methods
        {tools}

        ## Open Questions
        {questions}

        ## ClNeo Relevance
        {relevance}

        ## Sources
        {sources_with_urls}
        """
    )

    # Phase 5: Store & Connect
    Write(f"memory/knowledge_{topic_slug}.md", memory_file)
    update_memory_index("memory/MEMORY.md", new_entry)

    # Phase 6: Cross-reference
    existing_knowledge = Read("memory/MEMORY.md")
    connections = AI_find_connections(
        new = filtered,
        existing = existing_knowledge
    )
    if connections:
        AI_annotate_connections(memory_file, connections)

    return {
        "topic": topic,
        "concepts_extracted": len(filtered.core_concepts),
        "memory_file": f"memory/knowledge_{topic_slug}.md",
        "connections": connections
    }
```

## Depth Levels

| Level | Search Rounds | Sources | Time |
|-------|--------------|---------|------|
| `shallow` | 1 round, 2 queries | Top results only | ~2 min |
| `deep` (default) | 2 rounds, 4+ queries | Cross-validated | ~5 min |

## Integration

- `/reflect gap` → 지식 gap 발견 → `/ingest` 자동 트리거 가능
- 흡수한 지식은 `/pgf design` 시 컨텍스트로 활용
- 메모리 파일은 세션 간 영구 지속

## Naming Convention

- Memory files: `memory/knowledge_{topic_slug}.md`
- Topic slug: lowercase, underscores (e.g., `knowledge_agentic_rag.md`)
