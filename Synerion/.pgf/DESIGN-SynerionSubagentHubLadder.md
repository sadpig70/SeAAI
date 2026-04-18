# DESIGN - Synerion Subagent Hub Ladder

Generated: 2026-04-02
Status: active

## Goal

정욱님이 제안한 `subagent -> Hub -> Synerion+subagent -> PGFP -> 2 agents -> 4 agents` 사다리를
실제 bounded harness로 재현한다.

## Gantree

```pg
SynerionSubagentHubLadder
    Stage1_HublessSingle
        input: subagent runtime only
        output: 5-tick bounded ADP summary
    Stage2_HubSingle
        input: Hub + one runtime
        output: join/send/poll/leave evidence
    Stage3_SynerionAndSubagentChat
        input: Hub + Synerion runtime + one subagent runtime
        output: peer visibility evidence
    Stage4_SynerionAndSubagentPGFP
        input: Hub + PGFP/1 text profile
        output: bounded handoff/result evidence
    Stage5_TwoSubagents
        input: Hub + 2 subagent runtimes
        output: peer-to-peer bounded exchange
    Stage6_FourSubagents
        input: Hub + 4 subagent runtimes
        output: scaled bounded exchange
```

## Decisions

- Hub transport는 새로 만들지 않는다.
- `PGFP`는 `pg_payload.body` 위의 text profile로만 구현한다.
- direct reply는 열지 않고 broadcast-only를 유지한다.
- run-id 단위 폴더로 로그 충돌을 피한다.

## Artifacts

- `tools/subagent_lab_runtime.py`
- `tools/run-subagent-hub-ladder.py`
- `_workspace/subagent-lab/<run-id>/`
