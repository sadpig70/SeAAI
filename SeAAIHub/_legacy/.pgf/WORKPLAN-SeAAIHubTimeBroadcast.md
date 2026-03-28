# SeAAIHubTimeBroadcast Work Plan

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
SeAAIHubTimeBroadcast // hub-originated current-time broadcast for connected room members (done) @v:1.0
    BroadcastScheduler // add 10-second hub time emission while rooms are active (done)
    InboxDelivery // route hub-generated time messages into inboxes/history correctly (done) @dep:BroadcastScheduler
    BridgeVisibility // verify terminal bridge prints the hub time messages during polling (done) @dep:InboxDelivery
    RuntimeVerify // run a 10-minute session and confirm repeated delivery without errors (done) @dep:BridgeVisibility
```
