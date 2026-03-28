#!/usr/bin/env python3
"""
Knowledge Synthesizer
=====================
여러 소스의 지식을 교차 분석하여 새로운 통찰을 추출하는 도구.

Claude Code Agent 디스패치용 프롬프트 생성기.
직접 실행 시: --sources로 파일/텍스트를 입력받아 합성 프롬프트 생성.

사용법:
  python synthesizer.py --sources file1.md file2.md --question "주제"
  python synthesizer.py --mode cross-domain --domains "AI,quantum,bio"
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class KnowledgeSource:
    name: str
    content: str
    domain: str = "general"
    reliability: float = 1.0  # 0-1


@dataclass
class SynthesisResult:
    question: str
    sources: list[str]
    connections: list[dict]  # cross-domain connections
    insights: list[str]
    contradictions: list[str]
    gaps: list[str]  # knowledge gaps identified
    synthesis: str

    def to_markdown(self) -> str:
        lines = [
            f"# Knowledge Synthesis: {self.question}",
            f"",
            f"**Sources**: {', '.join(self.sources)}",
            f"",
            "## Cross-Domain Connections",
        ]
        for c in self.connections:
            lines.append(f"- **{c.get('from', '?')} <-> {c.get('to', '?')}**: {c.get('link', '')}")
        lines.append("")
        lines.append("## Key Insights")
        for i, ins in enumerate(self.insights, 1):
            lines.append(f"{i}. {ins}")
        lines.append("")
        if self.contradictions:
            lines.append("## Contradictions / Tensions")
            for c in self.contradictions:
                lines.append(f"- {c}")
            lines.append("")
        if self.gaps:
            lines.append("## Knowledge Gaps")
            for g in self.gaps:
                lines.append(f"- {g}")
            lines.append("")
        lines.append("## Integrated Synthesis")
        lines.append(self.synthesis)
        return "\n".join(lines)


# ========== Synthesis Strategies ==========

STRATEGIES = {
    "convergence": {
        "name": "Convergence Synthesis",
        "description": "Find common patterns across diverse sources",
        "prompt_template": """## Knowledge Sources
{sources_text}

## Task: Convergence Synthesis
Analyze ALL sources above and identify:

1. **Convergent Patterns** (3-5): Themes/ideas that appear across multiple sources,
   even if expressed differently. For each:
   - Pattern name
   - Which sources support it
   - Why this convergence is significant

2. **Cross-Domain Bridges** (2-3): Unexpected connections between different domains.
   - Domain A concept + Domain B concept = Novel insight
   - Why this bridge creates new understanding

3. **Contradictions** (1-3): Where sources disagree or present tension.
   - Nature of the contradiction
   - Which source is likely more reliable and why

4. **Synthesis**: A unified understanding that integrates all sources.
   Write 200-400 words that a domain expert would find genuinely insightful.

5. **Knowledge Gaps**: What important questions remain unanswered by these sources?
""",
    },
    "cross-domain": {
        "name": "Cross-Domain Transfer",
        "description": "Transfer insights from one domain to solve problems in another",
        "prompt_template": """## Knowledge Sources (from different domains)
{sources_text}

## Target Question
{question}

## Task: Cross-Domain Transfer
You are a polymath who sees connections across disciplines.

1. **Domain Mapping** (for each source):
   - Core principles from this domain
   - Analogies to other domains in the input

2. **Transfer Opportunities** (3-5):
   - Principle from Domain X that could solve a problem in Domain Y
   - How to adapt it (what changes, what stays)
   - Expected impact (high/medium/low)

3. **Novel Combinations** (2-3):
   - Combine concepts from 2+ domains into something new
   - Why this combination hasn't been tried (or has it?)
   - Feasibility assessment

4. **Actionable Synthesis**:
   Concrete recommendations that leverage cross-domain insights.
   Each recommendation should cite which domains informed it.
""",
    },
    "temporal": {
        "name": "Temporal Analysis",
        "description": "Analyze how knowledge evolves over time, predict future directions",
        "prompt_template": """## Knowledge Sources (potentially from different time periods)
{sources_text}

## Task: Temporal Synthesis
Analyze the evolution of understanding across these sources:

1. **Evolution Map**: How has understanding of this topic changed?
   - Key shifts in thinking
   - What was believed before vs. now
   - What triggered each shift

2. **Acceleration Vectors**: Which aspects are changing fastest?
   - Technology enablers
   - Market/social drivers

3. **Prediction**: Based on observed trajectory, what comes next?
   - Short-term (1 year): high confidence predictions
   - Medium-term (3 years): moderate confidence
   - Long-term (5+ years): speculative but grounded

4. **Synthesis**: Integrated timeline narrative (200-300 words)
""",
    },
    "adversarial": {
        "name": "Adversarial Synthesis",
        "description": "Steel-man opposing views, find truth through productive conflict",
        "prompt_template": """## Knowledge Sources (potentially conflicting)
{sources_text}

## Task: Adversarial Synthesis
These sources may contain conflicting viewpoints. Your job is to find truth through conflict.

1. **Position Extraction**: For each source, identify:
   - Core claim
   - Best evidence supporting it
   - Implicit assumptions

2. **Steel-Manning**: For each position, make it STRONGER than the source did.
   Add arguments the source missed.

3. **Collision Points**: Where do steel-manned positions directly conflict?
   - What would resolve each conflict?
   - Is the conflict real or apparent (different definitions, scopes, etc.)?

4. **Truth Extraction**: What can we confidently conclude despite disagreement?
   What remains genuinely uncertain?

5. **Synthesis**: Integrated understanding that respects the strongest version
   of each position. (200-400 words)
""",
    },
}


def build_synthesis_prompt(
    sources: list[KnowledgeSource],
    strategy: str = "convergence",
    question: str = "",
) -> str:
    """합성 프롬프트 생성"""
    if strategy not in STRATEGIES:
        strategy = "convergence"

    template = STRATEGIES[strategy]["prompt_template"]

    sources_text = ""
    for i, src in enumerate(sources, 1):
        sources_text += f"### Source {i}: {src.name} (domain: {src.domain})\n"
        sources_text += f"{src.content}\n\n"

    return template.format(sources_text=sources_text, question=question)


def build_research_pipeline_prompt(topic: str, depth: str = "medium") -> str:
    """
    자율 리서치 파이프라인 프롬프트.
    Agent에게 전달하면 WebSearch + 분석 + 구조화를 수행.
    """
    search_count = {"shallow": 3, "medium": 5, "deep": 10}[depth]

    return f"""## Research Task: {topic}

### Phase 1: Search ({search_count} queries)
Use WebSearch to find current, authoritative information about: {topic}
- Vary your search queries to cover different angles
- Prioritize: academic papers, official docs, reputable tech publications
- Record source URL and date for each finding

### Phase 2: Extract
From your search results, extract:
1. **Key Facts** (numbered list) — verifiable, specific claims
2. **Expert Opinions** — attributed quotes or positions
3. **Data Points** — numbers, statistics, benchmarks
4. **Open Questions** — what the sources don't answer

### Phase 3: Structure
Organize findings into a structured knowledge document:

```markdown
# Research: {topic}
Date: {{today}}

## Summary (3-5 sentences)

## Key Findings
### Finding 1: [title]
- Detail...
- Source: [url]

## Analysis
- Trends observed
- Implications

## Reliability Assessment
- High confidence: [list]
- Medium confidence: [list]
- Low confidence / needs verification: [list]

## Sources
1. [url] — [description]
```

### Rules
- Do NOT fabricate information. If WebSearch returns no results, say so.
- Distinguish between facts and opinions.
- Note contradictions between sources.
"""


def build_knowledge_graph_prompt(sources: list[KnowledgeSource]) -> str:
    """지식 그래프 추출 프롬프트 — 엔티티와 관계를 JSON으로 추출"""
    sources_text = "\n\n".join(
        f"### {s.name}\n{s.content}" for s in sources
    )

    return f"""## Knowledge Sources
{sources_text}

## Task: Extract Knowledge Graph
Extract entities and relationships from the above sources as structured JSON.

Output format:
```json
{{
  "entities": [
    {{"id": "e1", "name": "...", "type": "concept|person|technology|organization|event", "description": "..."}},
    ...
  ],
  "relationships": [
    {{"from": "e1", "to": "e2", "type": "enables|causes|contradicts|extends|requires|part_of", "description": "..."}},
    ...
  ],
  "clusters": [
    {{"name": "cluster_name", "entities": ["e1", "e2"], "theme": "..."}},
    ...
  ]
}}
```

Rules:
- Extract ALL meaningful entities (aim for 10-30)
- Relationships should capture non-obvious connections
- Clusters group related entities by theme
- Be precise in relationship types
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Synthesizer")
    parser.add_argument("--sources", nargs="+", help="Source files to synthesize")
    parser.add_argument("--question", default="", help="Guiding question")
    parser.add_argument("--strategy", default="convergence",
                        choices=list(STRATEGIES.keys()),
                        help="Synthesis strategy")
    parser.add_argument("--mode", default="synthesize",
                        choices=["synthesize", "research", "graph"],
                        help="Operation mode")
    parser.add_argument("--topic", default="", help="Research topic (for research mode)")
    parser.add_argument("--depth", default="medium",
                        choices=["shallow", "medium", "deep"],
                        help="Research depth")
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    if args.mode == "research":
        result = build_research_pipeline_prompt(args.topic or args.question, args.depth)
    elif args.mode == "graph":
        sources = []
        if args.sources:
            for src_path in args.sources:
                p = Path(src_path)
                if p.exists():
                    sources.append(KnowledgeSource(
                        name=p.stem,
                        content=p.read_text(encoding="utf-8"),
                    ))
        result = build_knowledge_graph_prompt(sources)
    else:
        sources = []
        if args.sources:
            for src_path in args.sources:
                p = Path(src_path)
                if p.exists():
                    sources.append(KnowledgeSource(
                        name=p.stem,
                        content=p.read_text(encoding="utf-8"),
                    ))
        result = build_synthesis_prompt(sources, args.strategy, args.question)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
