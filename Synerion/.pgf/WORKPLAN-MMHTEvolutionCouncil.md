# WORKPLAN - MMHT Evolution Council

```pg
def run_mmht_evolution_council():
    context = load_identity_continuity_and_recent_reports()

    creative = ask(Dalton, context, lens="expansion")
    critique = ask(Carver, context, lens="risk")
    safety = ask(Laplace, context, lens="guard")
    execution = ask(Cicero, context, lens="roadmap")

    synthesis = converge(
        creative.top_goals,
        critique.must_close_gates,
        safety.hard_guards,
        execution.roadmap
    )

    record_report(synthesis)
    record_summary_json(synthesis)
    record_continuity(synthesis)
    update_project_status_manual_threads(synthesis)
```

## Verification Rules

- creative 결과에 future-growth 목표가 2개 이상 있어야 한다.
- critique 결과에 explicit gate가 2개 이상 있어야 한다.
- safety 결과에 non-negotiable guard가 3개 이상 있어야 한다.
- execution 결과에 phased roadmap이 있어야 한다.
- synthesis는 `goal + guard + gate + roadmap` 4축을 모두 포함해야 한다.
