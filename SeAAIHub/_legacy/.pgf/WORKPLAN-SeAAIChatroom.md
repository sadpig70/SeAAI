# SeAAIChatroom Work Plan

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
SeAAIChatroom // N:N SeAAI agent chatroom over SeAAIHub STDIO MCP (done) @v:1.0
    HubState // in-memory broker and registry state (done)
    AgentAuth // shared-secret HMAC-based agent authentication (done) @dep:HubState
    RoomRegistry // room membership management (done) @dep:AgentAuth
    MsgIntegrity // PG message integrity verification (done) @dep:AgentAuth
    MessageRouting // room broadcast and direct delivery routing (done) @dep:RoomRegistry,MsgIntegrity
    MpcToolSurface // MCP tools/list + tools/call interface for SeAAI chatroom (done) @dep:RoomRegistry,MsgIntegrity
    QuerySurface // room/member/message queries (done) @dep:MessageRouting
```
