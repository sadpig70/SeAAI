# SA_ORCHESTRATOR_sync_mailbox

**ID**: SA_ORCHESTRATOR_sync_mailbox
**Layer**: L1 Primitive
**Input**: mailbox triage snapshot
**Output**: advisory snapshot
**Cost**: low

## Steps

- inspect inbox front matter and scoring
- classify shared-impact, safety, creative tags
- persist triage advisory json/md
- avoid mutating canonical continuity state
