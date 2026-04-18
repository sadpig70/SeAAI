# WORKPLAN - Synerion Subagent Hub Ladder

```pg
def execute_subagent_hub_ladder():
    Stage1 = run_hubless_single_subagent(ticks=5)
    Hub = ensure_local_hub_9900()

    Stage2 = run_single_subagent_with_hub(ticks=5)
    Stage3 = run_synerion_plus_subagent_chat(ticks=5)
    Stage4 = run_synerion_plus_subagent_pgfp(ticks=5)
    Stage5 = run_two_subagents_pgfp(ticks=5)
    Stage6 = run_four_subagents_pgfp(ticks=5)

    verify(Stage1, Stage2, Stage3, Stage4, Stage5, Stage6)
    record_report_and_status()
```

## Verification Rules

- Stage1: `ticks_completed == 5`
- Stage2: `sent >= 1`
- Stage3: 각 agent `peer_messages >= 1`
- Stage4: 각 agent `pgfp_sent >= 1 and pgfp_received >= 1`
- Stage5: 각 agent `peer_messages >= 1`
- Stage6: 각 agent `peer_messages >= 1`
