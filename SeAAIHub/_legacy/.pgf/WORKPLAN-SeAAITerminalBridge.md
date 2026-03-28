# SeAAITerminalBridge Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "halt",
    "completion": "all_done",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": ["D:\\SeAAI\\SeAAIHub"],
    "forbidden_actions": ["destructive_without_user_request", "unapproved_network"],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
SeAAITerminalBridge // terminal-visible bridge between Codex workflow and SeAAIHub (done) @v:1.0
    BridgeClient // persistent stdio client attached to SeAAIHub (done)
    AgentJoin // register and join a room as a built-in agent (done) @dep:BridgeClient
    InboxPrinter // poll inbox and print new hub messages to terminal output (done) @dep:AgentJoin
    OutboxRelay // watch a local outbox file and forward queued PG messages to the hub (done) @dep:AgentJoin
    SessionControl // respect logout flag, duration limit, and room cleanup (done) @dep:InboxPrinter,OutboxRelay
    BridgeVerify // verify terminal output, relay delivery, and clean shutdown (done) @dep:SessionControl
```
