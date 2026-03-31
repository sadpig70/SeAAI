# KnowledgeIslandSolver / SYNTHESIS.md
# 해결책 합성 모듈
# PGF Multi-Tree Module v1.0

@version: 1.0

```
Synthesis // 해결책 합성·평가·설계
    @input:  insights, connections, hypotheses
    @output: solution_system (DesignSpec), top3_solutions

    GenerateCandidates // 해결책 후보 생성
        AI_combine_insights(insights, connections)
        AI_apply_historical_patterns()   // 역사적 해결 원리 적용
        AI_generate_variants(count=20)   // 다양한 변형

    EvaluateCandidates // 5차원 평가
        @dep: GenerateCandidates
        [parallel]
        EvalFeasibility    // 현실 구현 가능성 (0~1)
        EvalImpact         // 영향 규모 (개인→문명)
        EvalNovelty        // 기존 접근 대비 차별성
        EvalRisk           // 부작용·의도치 않은 결과
        EvalScalability    // 소규모→대규모 확장성

    SelectTop3 // 상위 3개 선택
        @dep: EvaluateCandidates
        composite_score = Feasibility*0.3 + Impact*0.3 + Novelty*0.2
                        + (1-Risk)*0.1 + Scalability*0.1
        top3 = AI_select_top_k(candidates, k=3, score=composite_score)

    DesignSolutionSystem // 1위 해결책 → 시스템 설계
        @dep: SelectTop3
        champion = top3[0]
        AI_design_implementation_gantree(champion)
        // 이 자체가 새로운 PGF DESIGN이 된다
        // → .pgf/systems/{SolutionName}/ROOT.md 자동 생성

        AI_identify_required_resources()
        AI_design_feedback_loop()    // 시스템이 작동하며 개선되는 구조
        AI_design_metrics()          // 성공 측정 기준
        AI_identify_failure_modes()  // 실패 시나리오 사전 설계

    AlternativeDesigns // 2,3위 해결책 초안 보존
        @dep: SelectTop3
        for solution in top3[1:]:
            Write(f".pgf/systems/KIS-Alt-{solution.name}/ROOT.md",
                  AI_design_brief(solution))
        // 나중에 전개 가능한 씨앗으로 보존

    @output: {
        solution_system: full_design,
        top3: ranked_solutions,
        metrics: success_metrics,
        failure_modes: risk_map
    }
```
