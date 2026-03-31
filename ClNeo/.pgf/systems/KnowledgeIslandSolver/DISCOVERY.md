# KnowledgeIslandSolver / DISCOVERY.md
# 발견 엔진 — A3IE + 도메인 연결 매핑
# PGF Multi-Tree Module v1.0

@version: 1.0
@import A3IE from ../../shared/A3IE.md

```
Discovery // 발견 엔진
    @input:  knowledge_base, problem, domain_map
    @output: insights (InsightSet), connections (ConnectionGraph), seeds

    RunA3IE @expand: ../../shared/A3IE.md
        // 8페르소나 동시 실행 → 수렴 인사이트
        @input: problem, knowledge_base

    CrossDomainMapping // 도메인 간 비가시적 연결 탐색
        @dep: RunA3IE
        BuildKnowledgeGraph
            AI_extract_all_concepts(knowledge_base, A3IE_outputs)
            AI_map_relationships()
            // 노드: 개념 | 엣지: 인과/상관/유추/반대/포함

        FindHiddenConnections
            @dep: BuildKnowledgeGraph
            AI_detect_structural_isomorphisms()
            // 다른 언어로 표현된 같은 구조
            // 예: 정보 엔트로피 ↔ 생태 다양성 ↔ 면역 가변성
            AI_find_cross_domain_bridges()
            AI_identify_translation_opportunities()
            // "도메인 A의 해법을 도메인 B의 언어로 번역하면?"

        ValidateConnections
            @dep: FindHiddenConnections
            AI_test_analogy_strength()     // 표면적 유사 vs 구조적 동형
            AI_remove_false_positives()
            AI_estimate_transfer_value()   // 전이 가치 0.0~1.0

        RankConnections
            @dep: ValidateConnections
            AI_rank_by(novelty, feasibility, impact)
            top_connections = AI_select_top_k(k=10)

    InsightSynthesis // A3IE + CrossDomain 통합
        @dep: RunA3IE, CrossDomainMapping
        AI_merge_insights(A3IE.synthesis, top_connections)
        AI_identify_emergent_patterns()  // 두 분석의 교차에서 나타나는 것
        AI_formulate_hypotheses()        // 검증 가능한 가설로 변환

    SeedExtract
        @dep: InsightSynthesis
        seeds = AI_extract_seeds(all_insights, connections)
        @output: seeds  // → DISCOVERIES.md 저장

    @output: {
        insights: ranked_insights,
        connections: validated_connections,
        hypotheses: testable_hypotheses,
        seeds: seed_list
    }
```
