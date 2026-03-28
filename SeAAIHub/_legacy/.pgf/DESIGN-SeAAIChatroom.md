# SeAAIChatroom Design @v:1.0

## Gantree

```text
SeAAIChatroom // N:N SeAAI agent chatroom over SeAAIHub STDIO MCP (in-progress) @v:1.0
    HubState // in-memory broker and registry state (designing)
    AgentAuth // shared-secret HMAC-based agent authentication (designing) @dep:HubState
    RoomRegistry // room membership management (designing) @dep:AgentAuth
    MsgIntegrity // PG message integrity verification (designing) @dep:AgentAuth
    [parallel]
    MessageRouting // room broadcast and direct delivery routing (designing) @dep:RoomRegistry,MsgIntegrity
    MpcToolSurface // MCP tools/list + tools/call interface for SeAAI chatroom (designing) @dep:RoomRegistry,MsgIntegrity
    [/parallel]
    QuerySurface // room/member/message queries (designing) @dep:MessageRouting
```

## PPR

```python
def agent_auth(agent_id: str, token: str, shared_secret: str) -> bool:
    # acceptance_criteria:
    #   - registered agent with valid HMAC token is accepted
    #   - invalid token is rejected with explicit error
    ...
```

```python
def send_pg_message(msg: PGMessage, state: HubState) -> DeliveryResult:
    # acceptance_criteria:
    #   - room isolation is enforced
    #   - broadcast excludes sender
    #   - direct delivery only reaches explicit targets in the same room
    #   - invalid signature is rejected
    ...
```

```python
def tools_surface() -> list[ToolSpec]:
    # acceptance_criteria:
    #   - MCP initialize and tools/list succeed
    #   - tools/call can drive register/join/leave/send/query operations
    ...
```
