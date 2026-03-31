# plan-lib/grand-challenge/KnowledgeIslandSolver.md
# @sig: problem? → InsightReport, SeedList, SolutionSystem
# @scale: GRAND | @cost: HIGH | @ver: 1.0
# 진입점 — 실제 구현은 multi-tree 시스템으로 위임

```
KnowledgeIslandSolver
    @input:  problem (string, optional)
    @output: insight_report (path), seeds (SeedList), solution_system (DesignSpec)
    @ref:    .pgf/systems/KnowledgeIslandSolver/ROOT.md

    // 이 Plan은 multi-tree 시스템의 진입점이다.
    // ROOT.md를 @expand하여 전체 시스템을 전개한다.

    PreCheck @expand: ../safety/SafetyPreFlight.md

    Execute @expand: ../../systems/KnowledgeIslandSolver/ROOT.md
        @dep: PreCheck
        @input: problem = problem or AI_select_problem()

    // ROOT.md가 전개되면서:
    //   Safety       → shared/SafetyCheck.md
    //   ProblemSelect → systems/.../PROBLEM-SELECT.md
    //   Ingestion    → shared/KnowledgeIngestion.md
    //   Discovery    → systems/.../DISCOVERY.md (A3IE 포함)
    //   Synthesis    → systems/.../SYNTHESIS.md
    //   POC          → systems/.../POC.md
    //   Output       → systems/.../OUTPUT.md
    //   Evolution    → systems/.../EVOLUTION.md
    //   Teardown     → shared/SCSSessionEnd.md
```
