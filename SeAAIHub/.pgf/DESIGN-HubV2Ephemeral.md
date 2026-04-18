# HubV2Ephemeral Design @v:1.0

> SeAAIHub v2 — Ephemeral Agent Model + auth_key + Multi-Room
> Phase1: DualMode (기존 register 유지 + 신규 connect/disconnect 추가)
> 설계 근거: D:/SeAAI/SeAAIHub/docs/SeAAIHub_MCP_v2_EphemeralDesign.md

## Decisions (Hub-side)

| 항목 | 결정 |
|------|------|
| auth_key | `SEAAI_AUTH_KEY` 환경변수 1개. Hub가 connect 시 대조. 미설정 시 기본값 `sk-seaai-default` |
| session_token | `sess-{agent_id}-{timestamp_hex}` 형식. HMAC 서명으로 검증 가능 |
| Migration | Phase1 DualMode — register 유지, connect 추가. Phase2에서 register 제거 |
| heartbeat | Phase1 미구현. Phase2에서 60초 timeout 추가 |
| 멀티룸 | Phase1에서 즉시 구현. agent_registry의 rooms가 이미 Vec<String> |

## Gantree

```
HubV2Ephemeral // Hub 서버 v2 에페메럴 전환 Phase1 (designing) @v:1.0
    AuthProtocol // auth_key 인증 체계 (designing)
        AuthKeyConfig // SEAAI_AUTH_KEY 환경변수 로드 + 기본값 (designing)
        SessionToken // sess-{id}-{ts_hex} 생성 + HMAC 검증 (designing)
    ConnectAPI // seaai_connect 신규 API (designing) @dep:AuthProtocol
        ConnectArgs // protocol.rs — ConnectArgs 구조체 (designing)
        ConnectHandler // chatroom.rs — connect() 메서드 (designing) @dep:ConnectArgs
        ConnectRoute // router.rs — seaai_connect 라우팅 (designing) @dep:ConnectHandler
    DisconnectAPI // seaai_disconnect 신규 API (designing) @dep:ConnectAPI
        DisconnectArgs // protocol.rs — DisconnectArgs 구조체 (designing)
        DisconnectHandler // chatroom.rs — disconnect() 메서드 (designing) @dep:DisconnectArgs
        DisconnectRoute // router.rs — seaai_disconnect 라우팅 (designing) @dep:DisconnectHandler
    MultiRoom // 에이전트 멀티룸 지원 (designing)
        AgentRoomsField // chatroom.rs — AgentInfo.rooms 활용 (이미 Vec) (designing)
        ListAgentRooms // chatroom.rs — agent_rooms() 메서드 (designing) @dep:AgentRoomsField
        ListAgentRoomsArgs // protocol.rs — AgentRoomsArgs 구조체 (designing)
        ListAgentRoomsRoute // router.rs — seaai_list_agent_rooms 라우팅 (designing) @dep:ListAgentRooms,ListAgentRoomsArgs
        MessageRoomId // chatroom.rs — ChatMessage에 room_id 이미 존재. 응답 확인 (designing)
    JoinRoomFix // join_room 동작 변경 — 추가 입장 (교체 아님) (designing)
        # 현재 이미 추가 방식. 기존 rooms.push() 동작 확인만.
    TcpCleanup // TCP 끊김 시 에이전트 정리 개선 (designing)
        SessionTracking // main.rs — session_agent_id + session_token 추적 (designing) @dep:ConnectAPI
        CleanupOnDisconnect // main.rs — cleanup 로직에 session_token 무효화 추가 (designing) @dep:SessionTracking
    ToolSpecUpdate // tools/list 응답 갱신 (designing) @dep:ConnectAPI,DisconnectAPI,MultiRoom
        AddConnectSpec // seaai_connect tool spec (designing)
        AddDisconnectSpec // seaai_disconnect tool spec (designing)
        AddListAgentRoomsSpec // seaai_list_agent_rooms tool spec (designing)
    TestSuite // 단위 테스트 (designing) @dep:ConnectAPI,DisconnectAPI,MultiRoom,TcpCleanup
        TestConnect // connect 성공/실패 (designing)
        TestDisconnect // disconnect + 룸 정리 (designing)
        TestMultiRoom // 멀티룸 join/leave/list (designing)
        TestSessionToken // 토큰 발급/검증 (designing)
        TestDualMode // 기존 register + 신규 connect 공존 (designing)
    BuildVerify // cargo build + cargo test (designing) @dep:TestSuite
```

## PPR

```python
# ── AuthProtocol ──

def auth_key_config() -> str:
    """SEAAI_AUTH_KEY 환경변수 로드. 미설정 시 기본값."""
    # chatroom.rs ChatroomHub::new()에 추가
    auth_key = env("SEAAI_AUTH_KEY").unwrap_or("sk-seaai-default")
    return auth_key  # self.auth_key 필드로 저장


def session_token_create(agent_id: str, auth_key: str) -> str:
    """세션 토큰 생성. HMAC 서명 포함."""
    ts_hex = hex(current_timestamp_millis())
    raw = f"sess-{agent_id}-{ts_hex}"
    sig = hmac_sha256(auth_key, raw)
    return f"{raw}-{sig[:16]}"  # 축약 서명 16자 부착


def session_token_validate(token: str, auth_key: str) -> bool:
    """세션 토큰 검증."""
    parts = token.rsplit("-", 1)  # raw-sig 분리
    if len(parts) != 2: return False
    raw, sig = parts
    expected = hmac_sha256(auth_key, raw)[:16]
    return sig == expected


# ── ConnectAPI ──

def connect(auth_key: str, agent_id: str, rooms: list[str] = []) -> dict:
    """
    seaai_connect — 인증 + 식별 + 입장 원샷.
    기존 register_agent와 달리 auth_key 기반.
    
    flow:
        1. auth_key 검증 (self.auth_key와 대조)
        2. agent_id 등록 (authenticated_agents, agent_registry, inbox)
        3. session_token 생성
        4. rooms가 있으면 각각 join_room
        5. session_tokens 맵에 저장
    
    returns: {session_token, agent_id, rooms, connected_at}
    error: auth_key 불일치 시 거부
    """
    # acceptance_criteria:
    #   - auth_key 불일치 → bail!("invalid auth_key")
    #   - 성공 시 agent가 authenticated_agents에 포함
    #   - rooms 각각에 agent가 멤버로 등록
    #   - session_token이 session_tokens 맵에 저장


def disconnect(session_token: str, agent_id: str) -> dict:
    """
    seaai_disconnect — 명시적 소멸.
    
    flow:
        1. session_token 검증
        2. 모든 참가 룸에서 퇴장 (cleanup_agent 재활용)
        3. session_tokens에서 제거
        4. agent 상태 완전 제거
    
    returns: {status: "disconnected", agent_id, cleaned_rooms}
    """
    # acceptance_criteria:
    #   - session_token 무효 → bail!("invalid session_token")
    #   - disconnect 후 agent가 어떤 룸에도 없음
    #   - agent_registry에서 제거됨


# ── MultiRoom ──

def agent_rooms(agent_id: str) -> list[str]:
    """에이전트가 참가 중인 룸 목록 반환."""
    # agent_registry[agent_id].rooms 반환
    # acceptance_criteria:
    #   - 미인증 agent → bail!
    #   - 반환값이 실제 rooms 맵과 일치


# ── TcpCleanup ──

def tcp_cleanup_enhanced(session_agent_id: str, session_token: str):
    """TCP 끊김 시 세션 정리. 기존 cleanup_agent + session_token 무효화."""
    # flow:
    #   1. cleanup_agent(agent_id) — 기존 로직 재활용
    #   2. session_tokens.remove(session_token)
```
