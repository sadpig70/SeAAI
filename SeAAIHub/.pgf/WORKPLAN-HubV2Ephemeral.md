# HubV2Ephemeral Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "verify":              "cargo_build_and_test",
}
```

## Execution Tree

```
HubV2Ephemeral // Hub 서버 v2 에페메럴 전환 Phase1 (done) @v:1.0
    AuthProtocol // auth_key 인증 체계 (done)
        AuthKeyConfig // ChatroomHub에 auth_key 필드 추가 (done)
        SessionToken // session_token 생성/검증 + session_tokens 맵 (done) @dep:AuthKeyConfig
    ConnectAPI // seaai_connect 신규 API (done) @dep:AuthProtocol
        ConnectArgs // protocol.rs ConnectArgs (done)
        ConnectHandler // chatroom.rs connect() (done) @dep:ConnectArgs
        ConnectRoute // router.rs 라우팅 (done) @dep:ConnectHandler
    DisconnectAPI // seaai_disconnect 신규 API (done) @dep:ConnectAPI
        DisconnectArgs // protocol.rs DisconnectArgs (done)
        DisconnectHandler // chatroom.rs disconnect() (done) @dep:DisconnectArgs
        DisconnectRoute // router.rs 라우팅 (done) @dep:DisconnectHandler
    MultiRoom // 에이전트 멀티룸 (done)
        ListAgentRooms // chatroom.rs agent_rooms() (done)
        ListAgentRoomsArgs // protocol.rs AgentQueryArgs 재활용 (done)
        ListAgentRoomsRoute // router.rs 라우팅 (done) @dep:ListAgentRooms,ListAgentRoomsArgs
        MessageRoomId // ChatMessage에 room_id 이미 존재 — 확인 완료 (done)
    TcpCleanup // TCP 끊김 정리 개선 (done) @dep:ConnectAPI
        SessionTracking // main.rs session_token 추적 (done)
        CleanupOnDisconnect // cleanup + token 무효화 (done) @dep:SessionTracking
    ToolSpecUpdate // tools/list 갱신 (done) @dep:ConnectAPI,DisconnectAPI,MultiRoom
    TestSuite // 테스트 (done) @dep:ToolSpecUpdate
        TestConnect // connect 성공/실패 (done)
        TestDisconnect // disconnect + 정리 (done)
        TestMultiRoom // 멀티룸 join/leave/list (done)
        TestDualMode // register + connect 공존 (done)
    BuildVerify // cargo build + cargo test — 26 passed (done) @dep:TestSuite
```
