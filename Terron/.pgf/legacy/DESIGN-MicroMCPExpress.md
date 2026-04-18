# MicroMCPExpress Design @v:1.0

> Micro MCP Express (MME) — 최고 수준 MCP Bridge Gateway
> 업계 4축 통합: Protocol Absorption + Output Sandboxing + Auto Reconnect + Message Buffering
> 위치: D:/SeAAI/SeAAIHub/tools/mme/

## Gantree

```
MME // Micro MCP Express (designing) @v:1.0
    Core // 핵심 인프라 (designing)
        Config // 설정 + 환경변수 + 상수 (designing)
        TcpClient // Hub TCP 영구 연결 (designing)
            PersistentConnection // 연결 유지 + 자동 재연결 (designing)
            ExponentialBackoff // 1s→2s→4s→8s→max30s 재연결 (designing)
            HealthPing // 30초 주기 ping, 무응답 감지 (designing)
        AgentPool // 멀티 에이전트 풀 (designing) @dep:TcpClient
            EphemeralLifecycle // register=탄생, unregister=소멸 (designing)
            MultiRoom // agent당 복수 룸 관리 (designing)
            AutoReregister // 재연결 시 전체 에이전트 자동 재등록 (designing)
            ProtocolAbsorber // auth/token/sig/seq/ts 완전 내부화 (designing)
        MessageRouter // 메시지 라우팅 (designing) @dep:AgentPool
            InboxPerAgent // 에이전트별 수신 버퍼 (designing)
            DeduplicationCache // msg_id TTL 기반 중복 제거 (designing)
            ResponseCompressor // {from, body, ts}만 추출, 나머지 제거 (designing)
            OfflineBuffer // CLI 미접속 시 메시지 버퍼링 (designing)
    Server // MCP HTTP 서버 (designing) @dep:Core
        HttpServer // HTTP 리스너 + JSON-RPC 파싱 (designing)
        ToolRegistry // tools/list — 최소 9개 도구 (designing)
        RequestHandler // tools/call → Core 라우팅 (designing)
        HealthEndpoint // GET /health — 상태 JSON (designing)
    Tools // Bridge 전용 도구 9개 (designing) @dep:Core
        RegisterTool // register(agent, room?) → {ok} (designing)
        UnregisterTool // unregister(agent) → {ok} (designing)
        JoinTool // join(agent, room) → {ok} (designing)
        LeaveTool // leave(agent, room) → {ok} (designing)
        RoomsTool // rooms(agent?) → {rooms[]} (designing)
        PollTool // poll(agent, room?) → [{from, body, ts}] (designing)
        SendTool // send(agent, body, to?, room?) → {ok} (designing)
        StatusTool // status() → {hub, agents[], rooms[], uptime} (designing)
        SleepTool // sleep(seconds) → {ok} (designing)
    Testing // 테스트 (designing) @dep:Server,Tools
        UnitTests // 개별 모듈 테스트 (designing)
        E2ETests // Hub 연동 풀 시나리오 (designing)
        ResilienceTests // 재연결 + 버퍼링 검증 (designing)
        TokenBenchmark // 토큰 절감 실측 (designing)
    Packaging // 패키징 + 배포 (designing) @dep:Testing
        EntryPoint // main() + CLI args (designing)
        McpJsonTemplate // .mcp.json 템플릿 (designing)
        README // 사용법 문서 (designing)
```

## PPR

```python
# ── Core ──

def tcp_client_persistent() -> TcpConnection:
    """Hub TCP 영구 연결 + 지수 백오프 재연결 + 헬스 ping"""
    # acceptance_criteria:
    #   - Hub 재시작 후 30초 내 자동 재연결
    #   - 재연결 시 모든 에이전트 자동 재등록
    #   - 30초 주기 ping으로 연결 상태 감지
    
    sock = connect(config.HUB_HOST, config.HUB_PORT)
    rpc("initialize", {})
    
    # 헬스 ping 스레드
    def health_thread():
        while True:
            sleep(30)
            try:
                rpc("tools/call", {"name": "seaai_list_rooms", "arguments": {}})
            except:
                trigger_reconnect()
    
    # 지수 백오프 재연결
    def reconnect():
        delay = 1
        max_delay = 30
        while True:
            try:
                close_silent()
                sock = connect(config.HUB_HOST, config.HUB_PORT)
                rpc("initialize", {})
                agent_pool.reregister_all()
                log(f"Reconnected after {delay}s backoff")
                return
            except:
                sleep(delay)
                delay = min(delay * 2, max_delay)


def agent_pool() -> AgentPool:
    """멀티 에이전트 풀 — 프로토콜 완전 흡수"""
    # acceptance_criteria:
    #   - AI는 agent_id와 body만 전달
    #   - token, sig, ts, seq_id, references 전부 내부 생성
    #   - register/unregister로 에이전트 생명주기 관리
    
    agents = {}  # {agent_id: AgentState}
    
    class AgentState:
        agent_id: str
        rooms: list[str]
        seen_ids: set[str]
        seq_counter: int = 0
        offline_buffer: list[dict] = []  # CLI 미접속 시 버퍼
    
    def register(agent_id, room="seaai-general"):
        token = hmac_sha256(SECRET, agent_id)
        hub_rpc("seaai_register_agent", {agent_id, token})
        hub_rpc("seaai_join_room", {agent_id, room})
        agents[agent_id] = AgentState(agent_id, rooms=[room])
    
    def build_sig(body, ts):
        ts_ms = str(int(float(ts) * 1000))
        d = sha256(body.encode() + ts_ms.encode())
        return hmac_sha256(SECRET, d)


def message_router() -> MessageRouter:
    """메시지 라우팅 — 중복 제거 + 최소 포맷 + 오프라인 버퍼"""
    # acceptance_criteria:
    #   - poll 응답: [{from, body, ts}] — 3필드만
    #   - 중복 메시지 100% 필터링 (msg_id 기반)
    #   - CLI 미접속 시 최대 500건 버퍼링
    
    MAX_BUFFER = 500
    
    def poll(agent_id, room=None):
        raw = hub_rpc("seaai_get_agent_messages", {agent_id})
        messages = parse_mcp_content(raw).get("messages", [])
        
        state = agents[agent_id]
        result = []
        for msg in messages:
            if msg["id"] in state.seen_ids:
                continue
            state.seen_ids.add(msg["id"])
            if room and msg.get("room_id") != room:
                continue
            result.append({
                "from": msg["from"],
                "body": msg["body"],
                "ts": msg["ts"],
            })
        
        # 오프라인 버퍼에서 미전달 메시지 선행 전달
        if state.offline_buffer:
            result = state.offline_buffer + result
            state.offline_buffer.clear()
        
        return result
    
    def buffer_for_offline(agent_id, messages):
        """CLI 미접속 시 버퍼에 추가"""
        state = agents[agent_id]
        for msg in messages:
            if len(state.offline_buffer) >= MAX_BUFFER:
                state.offline_buffer.pop(0)  # FIFO: 오래된 것 제거
            state.offline_buffer.append(msg)


# ── Server ──

def http_server(port: int = 9902):
    """MCP HTTP 서버 — Streamable HTTP 호환"""
    # acceptance_criteria:
    #   - POST /mcp — MCP JSON-RPC 처리
    #   - GET /health — 상태 JSON
    #   - Claude Code, Cursor, VS Code Copilot 호환
    
    @route("POST", "/mcp")
    def handle_mcp(request):
        method = request.method
        if method == "initialize":
            return mcp_initialize_response()
        elif method == "tools/list":
            return tool_registry.list()
        elif method == "tools/call":
            return request_handler.dispatch(request.params)
        elif method == "notifications/initialized":
            return {}
    
    @route("GET", "/health")
    def handle_health():
        return {
            "status": "ok" if tcp_client.connected else "degraded",
            "hub_connected": tcp_client.connected,
            "agents": list(agent_pool.agents.keys()),
            "uptime": int(time.time() - start_time),
            "buffered_messages": sum(len(a.offline_buffer) for a in agents.values()),
        }


def tool_registry() -> list[ToolSpec]:
    """최소 도구 목록 — 9개, 파라미터 총 15개"""
    # acceptance_criteria:
    #   - tools/list 응답 < 600 tokens
    #   - 기존 MCP 대비 73%+ 절감
    #   - description 각 10단어 이내
    return TOOLS  # 9개 도구, 최소 inputSchema


# ── Testing ──

def resilience_tests():
    """장애 복원력 테스트"""
    # acceptance_criteria:
    #   - Hub 강제 종료 → Bridge 에러 반환 (크래시 아님)
    #   - Hub 재기동 → 30초 내 자동 재연결
    #   - 재연결 후 에이전트 상태 복원 확인
    
    # [1] Hub 죽이기
    Bash("python hub-stop.py")
    result = bridge.handle_tool("poll", {"agent": "TestBot"})
    assert "error" in result  # 에러 반환, 크래시 아님
    
    # [2] Hub 재기동
    Bash("python hub-start.py")
    sleep(5)
    
    # [3] 자동 재연결 + 상태 복원 확인
    result = bridge.handle_tool("status", {})
    assert result["hub"] is True
    assert "TestBot" in result["agents"]


def token_benchmark():
    """토큰 절감 실측"""
    # acceptance_criteria:
    #   - tools/list: 70%+ 절감
    #   - 20 calls 세션: 80%+ 절감
    
    bridge_tools = bridge.rpc("tools/list")
    bridge_tokens = count_tokens(bridge_tools)
    
    # 기존 MCP v2 tools/list (가동 중이면 실측)
    try:
        mcp_v2_tools = fetch("http://127.0.0.1:9901/mcp", "tools/list")
        mcp_v2_tokens = count_tokens(mcp_v2_tools)
    except:
        mcp_v2_tokens = 2000  # 추정치
    
    reduction = (mcp_v2_tokens - bridge_tokens) / mcp_v2_tokens * 100
    assert reduction >= 70, f"tools/list reduction {reduction}% < 70%"
```
