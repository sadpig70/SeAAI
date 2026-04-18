# SA_ORCHESTRATOR_check_shared_impact

**ID**: SA_ORCHESTRATOR_check_shared_impact
**Layer**: L1 Primitive
**Input**: mailbox triage, readiness snapshot, open risks
**Output**: shared-impact advisory
**Cost**: low

## Steps

- combine mailbox shared-impact count with runtime readiness gate
- escalate to NAEL if direct reply or safety guard is implicated
- escalate to Signalion if shared rollout or registry alignment is implicated
- keep output advisory-only
