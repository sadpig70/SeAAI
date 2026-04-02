# Report: Synerion Subagent Hub Ladder

- Generated: 2026-04-02T12:12:35.000354+09:00
- Run ID: 20260402-121217
- Hub started by runner: True
- Hub backend: file-fallback

## Verdict

- Successful stages: 6/6

## Stage Results

### 1-agent hubless 5 ticks
- success: True
- mode/profile: hubless / plain
- agents: SubagentAlpha
- room: synerion-lab-20260402-121217-s1
- evidence: all hubless ticks completed

### 1-agent hub connect
- success: True
- mode/profile: hub / plain
- agents: SubagentAlpha
- room: synerion-lab-20260402-121217-s2
- evidence: single agent sent=5 received=0

### Synerion + 1 subagent chat
- success: True
- mode/profile: hub / plain
- agents: Synerion, SubagentAlpha
- room: synerion-lab-20260402-121217-s3
- evidence: peer_messages=Synerion:5, SubagentAlpha:4

### Synerion + 1 subagent PGFP
- success: True
- mode/profile: hub / pgfp
- agents: Synerion, SubagentAlpha
- room: synerion-lab-20260402-121217-s4
- evidence: peer_messages=Synerion:5, SubagentAlpha:4 | pgfp=Synerion:5/5, SubagentAlpha:5/4

### 2 subagents over Hub
- success: True
- mode/profile: hub / pgfp
- agents: SubagentAlpha, SubagentBeta
- room: synerion-lab-20260402-121217-s5
- evidence: peer_messages=SubagentAlpha:5, SubagentBeta:4 | pgfp=SubagentAlpha:5/5, SubagentBeta:5/4

### 4 subagents over Hub
- success: True
- mode/profile: hub / pgfp
- agents: SubagentAlpha, SubagentBeta, SubagentGamma, SubagentDelta
- room: synerion-lab-20260402-121217-s6
- evidence: peer_messages=SubagentAlpha:14, SubagentBeta:14, SubagentGamma:13, SubagentDelta:12 | pgfp=SubagentAlpha:5/14, SubagentBeta:5/14, SubagentGamma:5/13, SubagentDelta:5/12

## Key Findings

- `hubless -> hub -> Synerion+subagent -> PGFP -> 2 subagents -> 4 subagents` 경로를 하나의 bounded harness로 재현했다.
- `PGFP/1`는 Hub transport를 바꾸지 않고 `pg_payload.body` profile로 얹는 방식으로 실험했다.
- direct reply 대신 broadcast-only를 유지해 current guardrail을 보존했다.
- Rust Hub가 현재 환경에서 `Winsock 10106`으로 실패하면 file-backed shared hub로 같은 room/inbox/broadcast semantics를 유지한다.

## Output

- JSON summary: D:/SeAAI/Synerion/_workspace/synerion-subagent-hub-ladder-last-run.json
- Run root: D:/SeAAI/Synerion/_workspace/subagent-lab/20260402-121217
