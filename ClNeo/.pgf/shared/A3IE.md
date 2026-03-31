# shared/A3IE.md
# A3IE — Asymmetric Adversarial Autonomous Intelligence Exploration
# 공유 모듈 — 어떤 시스템에서도 @import 가능
# PGF Multi-Tree Shared Module v1.0

@version: 2.0

```
A3IE // 8페르소나 × 7단계 발견 엔진
    @input:  problem (string), knowledge_base (docs)
    @output: synthesis (InsightSet), seeds (SeedList)

    Stage1_Diverge // 관점 발산 — 8 페르소나 동시 실행
        [parallel]
        P1_DisruptiveEngineer @expand: ../../skills/pgf/agents/pgf-persona-p1.md
            // 기술로 문제를 완전히 재정의
            // AI_ask: "이 문제를 기술이 아예 무의미하게 만들 수 있는가?"

        P2_ColdEyedInvestor @expand: ../../skills/pgf/agents/pgf-persona-p2.md
            // 인센티브 구조 분석
            // AI_ask: "누가 이 문제가 해결되길 원하지 않는가?"

        P3_RegulatoryArchitect @expand: ../../skills/pgf/agents/pgf-persona-p3.md
            // 제도·정책 설계
            // AI_ask: "규범을 바꾸면 문제가 사라지는가?"

        P4_ConnectingScientist @expand: ../../skills/pgf/agents/pgf-persona-p4.md
            // 과학적 연결 탐색
            // AI_ask: "자연이 이 문제를 이미 해결했는가?"

        P5_FieldOperator @expand: ../../skills/pgf/agents/pgf-persona-p5.md
            // 현장 실행 가능성
            // AI_ask: "내일 당장 실행 가능한 가장 작은 것은?"

        P6_FutureSociologist @expand: ../../skills/pgf/agents/pgf-persona-p6.md
            // 사회 구조 변화
            // AI_ask: "100년 후 이 문제는 어떻게 보일 것인가?"

        P7_ContrarianCritic @expand: ../../skills/pgf/agents/pgf-persona-p7.md
            // 반론·취약점
            // AI_ask: "왜 이 문제는 절대 해결될 수 없는가?"

        P8_ConvergenceArchitect @expand: ../../skills/pgf/agents/pgf-persona-p8.md
            // 모든 관점 통합
            // 마지막에 P1~P7 수렴

    Stage2_CrossFire // 페르소나 간 반론·강화
        AI_cross_challenge(P1_output, challenger=P7)
        AI_cross_challenge(P2_output, challenger=P6)
        AI_cross_challenge(P3_output, challenger=P1)
        AI_synthesize_conflicts()

    Stage3_Convergence // 수렴 — 공통 패턴 추출
        @dep: Stage2_CrossFire
        AI_find_convergence_points(all_outputs)
        AI_extract_invariant_insights()  // 모든 관점에서 일치하는 것
        AI_rank_by_robustness()          // 반론에도 살아남은 인사이트

    Stage4_SeedExtract // 씨앗 추출
        @dep: Stage3_Convergence
        AI_identify_novel_combinations()
        AI_format_seeds(convergence_results)
        // → DISCOVERIES.md 저장 대상

    Stage5_Output // 최종 출력
        @dep: Stage4_SeedExtract
        @output: {
            insights: ranked_insights,
            seeds: seed_list,
            strongest_hypothesis: top_insight,
            blind_spots: identified_gaps
        }
```
