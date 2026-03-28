# SeAAIHeartbeatSession Work Plan

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
SeAAIHeartbeatSession // sustain verified SeAAIHub communication for 10 minutes (done) @v:1.0
    SessionClient // local client that talks to SeAAIHub over stdio JSON-RPC (done)
    AgentBootstrap // register built-in agents and join a shared room (done) @dep:SessionClient
    HeartbeatLoop // alternate PG messages over the hub at fixed intervals (done) @dep:AgentBootstrap
    DeliveryVerify // verify inbox delivery, room state, and end-of-run counts (done) @dep:HeartbeatLoop
    SessionReport // persist run summary and review findings (done) @dep:DeliveryVerify
```
