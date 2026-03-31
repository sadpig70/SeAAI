# shared/KnowledgeIngestion.md
# 5채널 지식 수집 공유 모듈
# PGF Multi-Tree Shared Module v1.0

@version: 1.0

```
KnowledgeIngestion // 5채널 지식 수집
    @input:  problem (string), scope (BoundarySpec)
    @output: knowledge_base (DocSet), domain_map (ConceptGraph)

    [parallel]
    PrimaryDomain // 문제의 주 도메인
        WebSearch(f"{problem} latest research 2024 2025")
        WebSearch(f"{problem} breakthrough mechanism")
        AI_extract_key_concepts()
        AI_map_domain_language()   // 도메인 고유 용어 매핑

    AdjacentDomains // 인접 도메인
        AI_identify_adjacent_domains(problem)
        // 예: 우울증 → 신경과학, 사회학, 경제학, 진화생물학
        for domain in adjacent_domains:
            WebSearch(f"{domain} {problem_core_keywords}")
            AI_extract_cross_domain_insights()

    AnalogyDomains // 구조적 유사 도메인 (비직관적)
        AI_find_structural_analogies(problem)
        // 사회 연결망 → 균류 네트워크, 뇌 신경망, 강 유역
        // 면역 반응 → 사이버보안, 소문 전파, 시장 조정
        for analogy in structural_analogies:
            AI_extract_transferable_patterns(analogy)
            AI_assess_transfer_validity()

    HistoricalSolutions // 역사적 선례
        AI_search_historical_parallels(problem)
        // 과거에 유사 구조의 문제가 어떻게 해결됐는가
        AI_extract_solution_principles()  // 원리 추출 (구체 사례 아닌 패턴)

    FringeResearch // 비주류·이단 연구
        WebSearch(f"{problem} heterodox unconventional")
        WebSearch(f"{problem} ignored overlooked research")
        AI_assess_fringe_validity()
        AI_identify_suppressed_insights()

    Synthesis
        @dep: PrimaryDomain, AdjacentDomains, AnalogyDomains,
              HistoricalSolutions, FringeResearch
        AI_merge_deduplicate(all_docs)
        AI_build_concept_graph()      // 개념 간 관계 그래프
        AI_identify_knowledge_gaps()  // 아직 수집 안 된 영역
        @output: {
            docs: merged_knowledge,
            concept_graph: graph,
            gaps: knowledge_gaps,
            domain_map: domain_language_mapping
        }
```
