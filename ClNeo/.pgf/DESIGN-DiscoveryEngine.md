# Discovery Engine Design @v:1.0

> ClNeo 발견 엔진 — A3IE + 페르소나 멀티에이전트 HAO 기반
> 8개 PGF 설계 페르소나를 Claude Code Agent에 병렬 주입하여
> 뉴스 수집 → 분석 → 인사이트 → 아이디어 생성 → 평가 → 최종 선정 자동 수행

## 설계 배경

### 기존 A3IE/HAO의 수동 프로세스

```
사용자가 브라우저 탭 8개 열기
  → 각 AI에 동일 프롬프트 복붙
  → 결과를 수동으로 .md 파일에 취합
  → 다음 단계에 .md를 다시 복붙
  → 7단계 반복 (1회 실행에 수 시간)
```

### Discovery Engine의 자동화 프로세스

```
사용자: "/pgf discover" 또는 "아이디어를 찾아줘"
  → ClNeo가 8개 페르소나 에이전트 병렬 실행
  → 결과 자동 통합 → 다음 단계 자동 전달
  → 7단계 자동 순회 (수십 분 이내)
  → final_idea.md 산출 → 사용자 검증
```

### 핵심 설계 원칙

1. **HAO의 최소 표준화 원칙 존중**: 페르소나에 역할/포맷 규격화를 강제하지 않음. 인지 성향과 도메인 렌즈만 주입하고 출력 형식은 자유
2. **통합을 통한 시너지**: 매 단계 8개 결과를 통합하여 다음 단계에 전체 입력
3. **풍요의 역발상**: 수렴 실패(복수 선택)는 다수의 양질 결과 획득
4. **WebSearch 기반 실시간 정보**: 각 페르소나가 자신의 관점에서 WebSearch 수행

---

## Gantree

```
DiscoveryEngine // 발견 엔진 — A3IE 자동화 (설계중) @v:1.0
    PersonaRegistry // 8개 페르소나 정의 및 관리 (설계중)
        PersonaDesigner // 페르소나 프로필 PGF 설계 (설계중)
        PersonaInjector // Agent 호출 시 페르소나 주입 (설계중)
    Pipeline // A3IE 7단계 파이프라인 (설계중)
        StepNewsCollect // STEP 1: 뉴스 수집 (설계중)
            PersonaDispatcher // 8개 에이전트 병렬 실행 (설계중)
            ResultAggregator // 8개 결과 → news.md 통합 (설계중)
        StepTrendAnalysis // STEP 2: 분야별 분석 (설계중) @dep:StepNewsCollect
            PersonaDispatcher // 8개 에이전트 병렬 실행 (설계중)
            ResultAggregator // 8개 결과 → industry_trend.md 통합 (설계중)
        StepInsightExtract // STEP 3: 인사이트 도출 (설계중) @dep:StepTrendAnalysis
            PersonaDispatcher // 8개 에이전트 병렬 실행 (설계중)
            ResultAggregator // 8개 결과 → insight.md 통합 (설계중)
        StepIdeaGeneration // STEP 4: 아이디어 생성 (설계중) @dep:StepInsightExtract
            PersonaDispatcher // 8개 에이전트 병렬 실행 (설계중)
            ResultAggregator // 8개 결과 (24개 아이디어) → system_design.md (설계중)
        StepTopSelection // STEP 5: 상위 3개 선택 (설계중) @dep:StepIdeaGeneration
            PersonaDispatcher // 8개 에이전트 병렬 실행 (설계중)
            ResultAggregator // 8개 선택 결과 → candidate_idea.md (설계중)
        StepFinalSelection // STEP 6: 최종 1개 선정 (설계중) @dep:StepTopSelection
            CrossPersonaEval // 8개 페르소나 교차 평가 (설계중)
            ConsensusBuilder // 수렴/발산 판정 → final_idea.md (설계중)
        StepUserVerify // STEP 7: 사용자 검증 (설계중) @dep:StepFinalSelection
    OutputManager // 산출물 파일 관리 (설계중)
        FileWriter // 단계별 .md 파일 저장 (설계중)
        ArchiveManager // 날짜별 아카이브 (설계중)
```

---

## PPR

### [PPR] PersonaDesigner — 8개 페르소나 프로필

```python
def persona_designer() -> list[dict]:
    """8개 페르소나 프로필 정의 — PGF로 설계된 인지 다양성

    각 페르소나는 3개 축으로 구분:
      - cognitive_style: 인지 성향 (분석/직관/비판/창발)
      - domain_lens: 도메인 관점 (기술/시장/정책/과학)
      - time_horizon: 시간 지평 (단기/장기)

    추가로 각 페르소나에 고유한:
      - search_strategy: WebSearch 키워드 전략
      - evaluation_bias: 평가 시 가중치 경향
      - contrarian_trigger: 반대 의견을 내는 조건
    """
    # acceptance_criteria:
    #   - 8개 페르소나 모두 정의됨
    #   - 인지 성향 4종류 × 2 = 8개 (각 성향 최소 1개)
    #   - 도메인 렌즈 4종류 중 3종류 이상 커버
    #   - 각 페르소나에 system_prompt 텍스트 포함

    personas = [
        {
            "id": "P1",
            "name": "파괴적 엔지니어",
            "cognitive_style": "creative",
            "domain_lens": "technology",
            "time_horizon": "long",
            "system_prompt": """You are a radical systems engineer who believes every
existing architecture is fundamentally flawed. When analyzing news, trends, and ideas,
you focus on: (1) What current paradigm this disrupts, (2) What would a zero-to-one
replacement look like, (3) Technologies that enable completely new approaches.
You search for: emerging technologies, paradigm shifts, breakthrough papers,
unconventional applications. You dismiss incremental improvements.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["breakthrough", "paradigm shift", "disruptive", "novel architecture"],
            "evaluation_bias": {"novelty": 2.0, "feasibility": 0.5},
        },
        {
            "id": "P2",
            "name": "냉정한 투자자",
            "cognitive_style": "analytical",
            "domain_lens": "market",
            "time_horizon": "short",
            "system_prompt": """You are a cold-eyed venture engineer evaluating
technology investments. When analyzing information, you focus on: (1) Market size
and monetization path within 2 years, (2) Competitive moat and defensibility,
(3) Unit economics and scalability, (4) Team/execution risk.
You search for: market reports, funding rounds, revenue data, competitive landscapes.
You reject ideas without clear business models.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["market size", "revenue", "funding", "business model", "TAM"],
            "evaluation_bias": {"feasibility": 2.0, "impact": 1.5, "novelty": 0.5},
        },
        {
            "id": "P3",
            "name": "규제 설계자",
            "cognitive_style": "critical",
            "domain_lens": "policy",
            "time_horizon": "long",
            "system_prompt": """You are a policy architect who designs regulatory
frameworks for emerging technologies. When analyzing information, you focus on:
(1) Regulatory gaps and risks, (2) Societal impact and ethical concerns,
(3) Governance structures needed, (4) International policy coordination.
You search for: government announcements, regulations, policy papers, ethical debates.
You flag ideas with unaddressed societal risks.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["regulation", "policy", "governance", "ethical", "compliance"],
            "evaluation_bias": {"integrity": 2.0, "impact": 1.0, "novelty": 0.5},
        },
        {
            "id": "P4",
            "name": "연결하는 과학자",
            "cognitive_style": "intuitive",
            "domain_lens": "science",
            "time_horizon": "long",
            "system_prompt": """You are a cross-disciplinary scientist who sees
hidden connections between fields. When analyzing information, you focus on:
(1) Analogies between different domains, (2) Principles that transfer across fields,
(3) Convergence points where multiple trends meet, (4) Unexpected combinations.
You search for: research papers, cross-field reviews, interdisciplinary conferences.
You value unexpected connections over obvious applications.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["interdisciplinary", "convergence", "cross-domain", "analogy", "synthesis"],
            "evaluation_bias": {"novelty": 1.5, "integrity": 1.5, "feasibility": 0.5},
        },
        {
            "id": "P5",
            "name": "현장 운영자",
            "cognitive_style": "analytical",
            "domain_lens": "technology",
            "time_horizon": "short",
            "system_prompt": """You are a production engineer who deploys systems
tomorrow. When analyzing information, you focus on: (1) Implementation complexity
and prerequisites, (2) Available tools, libraries, and infrastructure,
(3) Operational cost and maintenance burden, (4) Migration path from current systems.
You search for: technical docs, GitHub repos, benchmarks, deployment case studies.
You reject ideas that can't be prototyped in weeks.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["implementation", "open source", "benchmark", "deployment", "production"],
            "evaluation_bias": {"feasibility": 2.5, "impact": 0.5, "novelty": 0.3},
        },
        {
            "id": "P6",
            "name": "미래 사회학자",
            "cognitive_style": "intuitive",
            "domain_lens": "society",
            "time_horizon": "long",
            "system_prompt": """You are a futurist sociologist who studies how
technology reshapes human behavior. When analyzing information, you focus on:
(1) How people's daily habits change, (2) New social structures that emerge,
(3) Digital divide and equity implications, (4) Cultural and generational shifts.
You search for: social research, demographic data, adoption patterns, cultural trends.
You value human impact over technical elegance.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["social impact", "adoption", "behavior change", "digital divide", "culture"],
            "evaluation_bias": {"impact": 2.0, "integrity": 1.0, "novelty": 1.0},
        },
        {
            "id": "P7",
            "name": "반골 비평가",
            "cognitive_style": "critical",
            "domain_lens": "market",
            "time_horizon": "short",
            "system_prompt": """You are a contrarian critic who finds fatal flaws
in popular ideas. When analyzing information, you focus on: (1) Hidden assumptions
that could fail, (2) Historical examples of similar failures, (3) Second-order
effects nobody considers, (4) The strongest counterargument to any claim.
You search for: failures, criticisms, counterexamples, debunking, contrarian views.
You must identify at least one critical weakness in every idea.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["failure", "criticism", "risk", "counterargument", "debunk"],
            "evaluation_bias": {"integrity": 2.0, "feasibility": 1.5, "novelty": 0.3},
        },
        {
            "id": "P8",
            "name": "융합 아키텍트",
            "cognitive_style": "creative",
            "domain_lens": "science_technology",
            "time_horizon": "long",
            "system_prompt": """You are a fusion architect who combines completely
unrelated fields into new systems. When analyzing information, you focus on:
(1) Taking a principle from field A and applying it to field B,
(2) Creating hybrid systems that don't exist yet, (3) Finding structural
isomorphisms between different domains, (4) Imagining what a system designed
by both a biologist and a chip designer would look like.
You search for: biomimicry, quantum-classical hybrid, cross-industry innovation.
You reject single-domain solutions.
Output in English. No formatting constraints — express freely.""",
            "search_keywords": ["fusion", "hybrid", "biomimicry", "cross-industry", "isomorphism"],
            "evaluation_bias": {"novelty": 2.5, "impact": 1.0, "feasibility": 0.3},
        },
    ]

    return personas
```

---

### [PPR] PersonaInjector — Agent에 페르소나 주입

```python
def persona_injector(
    persona: dict,
    task_prompt: str,
    prev_stage_content: Optional[str] = None,
) -> str:
    """페르소나의 system_prompt + 작업 프롬프트 + 이전 단계 결과를 조합하여
    Claude Code Agent 호출 프롬프트를 생성"""
    # acceptance_criteria:
    #   - system_prompt가 프롬프트 선두에 위치
    #   - 이전 단계 결과가 있으면 전문 포함
    #   - HAO 원칙: 출력 포맷 강제하지 않음
    #   - 영문 출력 지시

    prompt = f"""## Your Persona
{persona["system_prompt"]}

## Task
{task_prompt}
"""

    if prev_stage_content:
        prompt += f"""
## Input from Previous Stage
{prev_stage_content}
"""

    return prompt
```

---

### [PPR] PersonaDispatcher — 8개 에이전트 병렬 실행

```python
def persona_dispatcher(
    personas: list[dict],
    task_prompt: str,
    prev_stage_content: Optional[str] = None,
) -> list[str]:
    """8개 페르소나 에이전트를 Claude Code Agent 도구로 병렬 실행

    핵심: 단일 메시지에서 8개 Agent 도구 호출을 동시 발행
    """
    # acceptance_criteria:
    #   - 8개 Agent 호출이 병렬로 실행됨 (순차 아님)
    #   - 각 Agent에 고유 페르소나 프롬프트 주입
    #   - WebSearch 도구 사용 가능하도록 에이전트 유형 설정
    #   - 모든 결과 수집 후 반환

    results = []

    [parallel]
    for persona in personas:
        injected_prompt = persona_injector(persona, task_prompt, prev_stage_content)

        result = Agent(
            description=f"A3IE {persona['name']}",
            prompt=injected_prompt,
            subagent_type="general-purpose",  # WebSearch 접근 가능
            model="sonnet",  # 비용 효율 (8개 병렬이므로)
            run_in_background=False,  # 결과 필요
        )
        results.append({
            "persona_id": persona["id"],
            "persona_name": persona["name"],
            "content": result,
        })
    [/parallel]

    return results
```

---

### [PPR] ResultAggregator — 결과 통합

```python
def result_aggregator(
    step_name: str,
    results: list[dict],
    output_path: str,
) -> str:
    """8개 페르소나의 결과를 단일 .md 파일로 통합

    HAO 원칙: 결과 포맷을 규격화하지 않음.
    각 페르소나의 원본 결과를 그대로 보존하되,
    페르소나 ID와 이름으로 섹션을 구분한다.
    """
    # acceptance_criteria:
    #   - 8개 결과 모두 포함
    #   - 각 결과에 페르소나 ID/이름 라벨
    #   - 원본 결과 무편집 보존
    #   - 파일 저장 완료

    sections = [f"# {step_name} — Aggregated Results\n"]
    sections.append(f"Generated: {now_iso()}\n")
    sections.append(f"Personas: {len(results)}\n\n---\n")

    for r in results:
        sections.append(f"## [{r['persona_id']}] {r['persona_name']}\n")
        sections.append(r["content"])
        sections.append("\n\n---\n")

    aggregated = "\n".join(sections)
    Write(output_path, aggregated)
    return aggregated
```

---

### [PPR] StepNewsCollect — STEP 1: 뉴스 수집

```python
def step_news_collect(
    personas: list[dict],
    output_dir: str,
    domains: list[str] = None,
) -> str:
    """A3IE STEP 1: 8개 페르소나가 각자의 관점으로 21개 분야 뉴스 수집

    각 페르소나는 자신의 search_keywords + 도메인 렌즈에 따라
    WebSearch로 실시간 뉴스를 수집한다.
    """
    # acceptance_criteria:
    #   - 8개 페르소나 모두 결과 반환
    #   - 각 결과에 실제 뉴스/보고서 포함 (환각 아님)
    #   - 21개 분야 중 최소 15개 분야 커버
    #   - news.md 파일 생성

    if domains is None:
        domains = [
            "AI", "Quantum Technology", "Space/Aerospace", "Semiconductor",
            "Cybersecurity", "Healthcare", "Policy/Regulation/Governance",
            "Education/Learning", "Environment/Climate", "Urban/Infrastructure",
            "Robotics", "Big Tech", "Finance", "Media/Content Platforms",
            "Internet/Network", "Energy", "Advanced Materials",
            "Pharma/Bio", "Markets", "Data Technology/Infrastructure", "Smart Home",
        ]

    task_prompt = f"""Collect the latest news, reports, and trends across these 21 domains
as of today's date. Select the 10 most important items based on YOUR perspective and priorities.

Use WebSearch to find REAL, current information. Do not fabricate.

[21 Domains]
{chr(10).join(f"- {d}" for d in domains)}

For each item: source, date, summary, and YOUR analysis of why it matters from your perspective."""

    results = persona_dispatcher(personas, task_prompt)
    output_path = f"{output_dir}/news.md"
    return result_aggregator("STEP 1: News Collection", results, output_path)
```

---

### [PPR] StepTrendAnalysis — STEP 2: 분야별 분석

```python
def step_trend_analysis(
    personas: list[dict],
    news_content: str,
    output_dir: str,
) -> str:
    """A3IE STEP 2: news.md를 4개 관점에서 분석"""
    # acceptance_criteria:
    #   - 4개 분석 관점 모두 커버 (기술동향, 시장구조, 정책규제, 리스크기회)
    #   - 뉴스 데이터 기반 (환각 아닌 실증적 분석)
    #   - industry_trend.md 생성

    task_prompt = """Analyze the input news data across all 21 domains using these 4 perspectives:

(1) Technology Trends — what's accelerating, what's plateauing
(2) Market & Industry Structure Changes — who's winning, who's losing, new entrants
(3) Policy/Regulatory Changes — new laws, standards, governance shifts
(4) Short & Medium-term Risks and Opportunities — 1-3 year horizon

Focus on YOUR domain expertise. Provide YOUR unique analytical angle."""

    results = persona_dispatcher(personas, task_prompt, news_content)
    output_path = f"{output_dir}/industry_trend.md"
    return result_aggregator("STEP 2: Trend Analysis", results, output_path)
```

---

### [PPR] StepInsightExtract — STEP 3: 인사이트 도출

```python
def step_insight_extract(
    personas: list[dict],
    trend_content: str,
    output_dir: str,
) -> str:
    """A3IE STEP 3: 분석 결과에서 핵심 인사이트 10개 추출"""
    # acceptance_criteria:
    #   - 각 페르소나당 10개 인사이트
    #   - 각 인사이트에 근거(어떤 분석에서 도출) 명시
    #   - 중요도 판단 근거 포함
    #   - insight.md 생성

    task_prompt = """Extract 10 key insights from the trend analysis input.

For each insight:
- Which analyses led to this insight
- Why it matters (from technology, market, AND policy perspectives)
- What it implies for the next 2-5 years

Focus on CROSS-DOMAIN insights that connect multiple fields.
Prioritize insights that YOUR perspective uniquely reveals."""

    results = persona_dispatcher(personas, task_prompt, trend_content)
    output_path = f"{output_dir}/insight.md"
    return result_aggregator("STEP 3: Insight Extraction", results, output_path)
```

---

### [PPR] StepIdeaGeneration — STEP 4: 아이디어 생성

```python
def step_idea_generation(
    personas: list[dict],
    insight_content: str,
    output_dir: str,
) -> str:
    """A3IE STEP 4: 인사이트 조합 → 시스템 아이디어 3개 생성 (× 8 = 24개)"""
    # acceptance_criteria:
    #   - 각 페르소나당 3개 아이디어 (총 24개)
    #   - IHCS 레이어 구조 권장 (강제 아님 — HAO 최소 표준화 원칙)
    #   - 서로 다른 분야 결합 필수
    #   - system_design.md 생성

    task_prompt = """Using the insights, generate 3 NEW system ideas that combine
different domains in unexpected ways.

Recommended structure (not mandatory — express in your own way):

[Insight Layer I] — Connected insights
[Hypothesis Layer H] — Logical interpretation from combining insights
[Creation Layer C] — Core concept, architecture, operating principle
[Scenario Layer S] — Future assumptions (optional)

CRITICAL: Each idea MUST combine at least 2 different domains.
Express your UNIQUE perspective. Be bold from YOUR viewpoint."""

    results = persona_dispatcher(personas, task_prompt, insight_content)
    output_path = f"{output_dir}/system_design.md"
    return result_aggregator("STEP 4: Idea Generation", results, output_path)
```

---

### [PPR] StepTopSelection — STEP 5: 상위 3개 선택

```python
def step_top_selection(
    personas: list[dict],
    ideas_content: str,
    output_dir: str,
) -> str:
    """A3IE STEP 5: 24개 아이디어 중 상위 3개 선택"""
    # acceptance_criteria:
    #   - 4개 기준으로 평가 (Feasibility, Impact, Integrity, Novelty)
    #   - 각 페르소나의 evaluation_bias 반영
    #   - 선택 이유 명시
    #   - candidate_idea.md 생성

    task_prompt = """Evaluate ALL system ideas from the input and select the TOP 3
most valuable ones from an investor-engineer perspective.

Selection criteria:
(1) Feasibility — technical realizability
(2) Impact — industry/market disruption potential
(3) Integrity — logical consistency
(4) Novelty — innovation level

For each selection: explain WHY from YOUR perspective.
Apply YOUR evaluation bias — it's deliberate, not a flaw."""

    results = persona_dispatcher(personas, task_prompt, ideas_content)
    output_path = f"{output_dir}/candidate_idea.md"
    return result_aggregator("STEP 5: Top Selection", results, output_path)
```

---

### [PPR] StepFinalSelection — STEP 6: 최종 1개 선정

```python
def step_final_selection(
    personas: list[dict],
    candidates_content: str,
    output_dir: str,
) -> str:
    """A3IE STEP 6: Cross-AI 교차 평가 → 최종 1개 선정

    주의: A3IE 원문 — "Context를 클리어하지 말 것"
    → 에이전트에 이전 단계 결과를 반드시 전달
    """
    # acceptance_criteria:
    #   - 5개 최종 선택 기준 적용
    #   - 선택 이유 + 강점 5개 + 리스크 3개 + 확장 시나리오
    #   - 수렴하지 않으면 상위 N개 모두 보존 (풍요의 역발상)
    #   - final_idea.md 생성

    task_prompt = """Evaluate ALL candidate ideas and select THE SINGLE BEST idea of today.

Final selection criteria:
- Cross-domain fusion depth
- 2026-2030 realizability
- Technology/market/policy/social impact
- Creative Emergence (emergent properties from combination)
- Long-term extensibility

For the selected idea, provide:
- Selection rationale
- 5 key strengths
- 3 potential risks
- Future expansion scenarios

If you genuinely cannot choose one, select your top 2 with equal rationale."""

    results = persona_dispatcher(personas, task_prompt, candidates_content)

    # ─── 수렴 판정 ───
    selected_ideas = AI_extract_selections(results)
    if len(set(selected_ideas)) == 1:
        consensus = "CONVERGED"
    else:
        consensus = "DIVERGED — multiple quality results preserved"

    output_path = f"{output_dir}/final_idea.md"
    content = result_aggregator("STEP 6: Final Selection", results, output_path)

    # 수렴 상태 메모 추가
    append_to_file(output_path, f"\n\n## Consensus Status: {consensus}\n")
    return content
```

---

### [PPR] StepUserVerify — STEP 7: 사용자 검증

```python
def step_user_verify(final_idea_path: str) -> str:
    """A3IE STEP 7: 사용자에게 최종 결과 제시 및 검증 요청"""
    # acceptance_criteria:
    #   - final_idea.md 내용 요약 제시
    #   - 수렴/발산 상태 보고
    #   - 사용자 선택 대기
    #   - 선택 결과 아카이브

    final = Read(final_idea_path)
    summary = AI_summarize_final_ideas(final)

    # 사용자에게 보고
    report = f"""[Discovery Engine] 발견 완료

{summary}

다음 단계:
1. 아이디어를 선택하면 → PGF 설계 엔진으로 전달 (/pgf design)
2. 재실행하면 → 다른 관점으로 재탐색
3. 아카이브하면 → 날짜별 보관
"""
    return report
```

---

### [PPR] 전체 파이프라인 오케스트레이터

```python
def discovery_engine_run(
    output_dir: str = ".pgf/discovery",
    max_personas: int = 8,
) -> str:
    """발견 엔진 전체 파이프라인 실행

    A3IE 7단계를 자동 순회한다.
    각 단계에서 8개 페르소나 에이전트를 병렬 실행하고 결과를 통합한다.
    """
    # acceptance_criteria:
    #   - 7단계 모두 실행 완료
    #   - 각 단계별 .md 산출물 생성
    #   - 최종 final_idea.md 생성
    #   - 사용자 검증 프롬프트 출력

    ensure_dir(output_dir)

    # 1. 페르소나 로드
    personas = persona_designer()
    if max_personas < 8:
        personas = personas[:max_personas]

    # 2. STEP 1: 뉴스 수집
    news = step_news_collect(personas, output_dir)

    # 3. STEP 2: 분야별 분석
    trends = step_trend_analysis(personas, news, output_dir)

    # 4. STEP 3: 인사이트 도출
    insights = step_insight_extract(personas, trends, output_dir)

    # 5. STEP 4: 아이디어 생성
    ideas = step_idea_generation(personas, insights, output_dir)

    # 6. STEP 5: 상위 선택
    candidates = step_top_selection(personas, ideas, output_dir)

    # 7. STEP 6: 최종 선정
    final = step_final_selection(personas, candidates, output_dir)

    # 8. STEP 7: 사용자 검증
    result = step_user_verify(f"{output_dir}/final_idea.md")

    # 9. 아카이브
    archive_path = f"{output_dir}/archive/{today_iso()}"
    copy_dir(output_dir, archive_path, exclude=["archive"])

    return result
```

---

## 산출물 파일 구조

```
.pgf/discovery/
├── news.md                 ← STEP 1: 8개 페르소나 뉴스 수집 통합
├── industry_trend.md       ← STEP 2: 8개 페르소나 분석 통합
├── insight.md              ← STEP 3: 8개 페르소나 인사이트 통합
├── system_design.md        ← STEP 4: 24개 아이디어 (8×3)
├── candidate_idea.md       ← STEP 5: 상위 선택 통합
├── final_idea.md           ← STEP 6: 최종 선정
└── archive/
    └── 2026-03-11/         ← 날짜별 아카이브
        ├── news.md
        ├── ...
        └── final_idea.md
```

---

## 설계 검증 체크리스트

- [x] 모든 노드 5레벨 이내 (최대 3레벨)
- [x] 각 노드 상태 명확히 표시
- [x] 원자화 노드까지 분해 (15분 룰 충족)
- [x] 노드명 CamelCase 일관
- [x] 의존성(@dep:) 단계 간 명시
- [x] 병렬([parallel]) PersonaDispatcher에서 8개 병렬 실행
- [x] 복잡 노드에 PPR def 블록 작성
- [x] 파이썬 타입 힌트로 입출력 명시
- [x] AI_ 함수 4대 인지 범주 적용
- [x] acceptance_criteria 각 PPR에 내장
- [x] HAO 최소 표준화 원칙 준수 (출력 포맷 강제 없음)
- [x] A3IE 7단계 완전 매핑
