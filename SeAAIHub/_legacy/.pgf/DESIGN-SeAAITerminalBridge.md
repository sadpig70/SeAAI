# SeAAITerminalBridge Design @v:1.0

## Gantree

```text
SeAAITerminalBridge // terminal-visible bridge between Codex workflow and SeAAIHub (in-progress) @v:1.0
    BridgeClient // persistent stdio client attached to SeAAIHub (designing)
    AgentJoin // register and join a room as a built-in agent (designing) @dep:BridgeClient
    InboxPrinter // poll inbox and print new hub messages to terminal output (designing) @dep:AgentJoin
    OutboxRelay // watch a local outbox file and forward queued PG messages to the hub (designing) @dep:AgentJoin
    SessionControl // respect logout flag, duration limit, and room cleanup (designing) @dep:InboxPrinter,OutboxRelay
    BridgeVerify // verify terminal output, relay delivery, and clean shutdown (designing) @dep:SessionControl
```

## PPR

```python
def run_terminal_bridge(room_id: str, agent_id: str, duration_seconds: int) -> BridgeReport:
    # acceptance_criteria:
    #   - bridge stays attached to SeAAIHub for the requested session window
    #   - incoming messages appear on terminal output as they arrive
    #   - queued outbox messages are forwarded through the hub
    #   - logout flag or duration expiry causes clean leave and exit
    ...
```
