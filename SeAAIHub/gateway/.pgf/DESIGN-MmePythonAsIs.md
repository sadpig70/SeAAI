# DESIGN-MmePythonAsIs

> **목적**: 현 Python MME 구조를 PG(Gantree + PPR)로 역공학 기록.
> **용도**: (1) 구조 검증 (2) 잠복 버그 고정 (3) 재설계 기반 (4) Rust 구현 청사진.
> **소스**: `D:/SeAAI/SeAAIHub/tools/mme/` @ 2026-04-11
> **분석자**: clcon
> **상태**: AS-IS baseline — 수정 금지, 재설계는 별도 DESIGN-MmeRedesign.md

---

## 0. Overview

```text
MmePythonAsIs // Micro MCP Express — Python 구현 AS-IS (in-progress) @v:1.0
    Purpose // 세 가지 설계 목표 (done)
        TokenMinimization // tools/list 35%↓, per-session 67%↓ (done)
        SessionDecoupling // Hub 크래시가 AI 세션에 무영향 (done)
        ProtocolAbsorption // auth/token/sig/ts/seq 전부 Bridge 내부 (done)

    Topology // 통신 토폴로지 (done)
        # AI_Client → HTTP 9902 /mcp → MMEBridge → TCP 9900 → SeAAIHub
        # MME는 양방향 게이트웨이. 클라이언트 방향: MCP JSON-RPC. 서버 방향: Hub JSON-RPC over newline TCP

    Files // 5 파이썬 파일 총 736 LOC (done)
        config_py          // 29 LOC — 상수·환경변수 (done)
        tcp_client_py      // 140 LOC — Hub 연결 (done)
        agent_pool_py      // 121 LOC — 에이전트 상태 (done)
        message_router_py  // 71 LOC — poll/send (done)
        mme_server_py      // 375 LOC — HTTP + dispatch (needs-verify)  #BUG-SUSPECT
```

---

## 1. Gantree — 모듈 계층

```text
MmeModules // 모듈 분해 (done)
    Config // config.py (done)
        env_vars // MME_PORT, MME_HUB_HOST, MME_HUB_PORT, SEAAI_HUB_SECRET (done)
        mcp_meta // PROTOCOL_VERSION=2024-11-05, SERVER_NAME, VERSION=1.0.0 (done)
        reconnect_cfg // BASE_DELAY=1, MAX_DELAY=30 (done)
        health_cfg // HEALTH_PING_INTERVAL=30 (done)
        buffer_cfg // MAX_OFFLINE_BUFFER=500, DEDUP_TTL=3600(unused) (done)

    TcpClient // tcp_client.py — Hub 영구 연결 (done)
        Connect // 초기 TCP + initialize RPC (done)
        Reconnect // 지수 백오프 1→30s 무한 재시도 (done)
        Rpc // threading.Lock 감싼 JSON-RPC over newline (done)
        ToolCall // rpc("tools/call") 래핑 + MCP content 파싱 (done)
        HealthPing // 30s 주기 seaai_list_rooms ping → 실패 시 재연결 (done)
        Stop // 종료 플래그 + 소켓 close (done)

    AgentPool // agent_pool.py — 멀티 에이전트 상태 (done)
        AgentState // agent_id, rooms, seen_ids, seq_counter, offline_buffer (done)
        Register // register_agent + join_room + state 생성 (done)
        Unregister // leave_room 전체 + state 삭제 (done)
        JoinLeaveRooms // Hub 호출 + state.rooms 동기화 (done)
        ReregisterAll // 재연결 후 전 에이전트 복원 — TcpClient.on_reconnect 콜백 (done)
        BuildSig // HMAC-SHA256(sha256(body|ts_ms)) (done)
        BuildToken // HMAC-SHA256(agent_id) (done)
        OfflineBuffer // FIFO push/drain, cap 500 (done)

    MessageRouter // message_router.py — 메시지 라우팅 (done)
        Poll // 오프라인 버퍼 + Hub get_messages + dedup + room filter + 최소 포맷 (done)
        Send // sig 생성 + seaai_send_message 호출 (done)

    McpServer // mme_server.py — HTTP MCP 서버 (needs-verify)
        ToolDefinitions // 9 tool JSON schema (done)
        MMEBridge // 핵심 인스턴스 (needs-verify)
            Init // TcpClient + Pool + Router + on_reconnect wiring (done)
            HandleTool // tool dispatch (blocked)  #BUG-SUSPECT
            TriggerReconnect // 백그라운드 재연결 (needs-verify)  #BUG-SUSPECT
        McpHandler // BaseHTTPRequestHandler 서브클래스 (done)
            HealthEndpoint // GET /health (done)
            McpEndpoint // POST /mcp — initialize/tools_list/tools_call (done)
            JsonResponse // 공통 응답 헬퍼 (done)
        Main // argparse + HTTPServer.serve_forever (done)
```

---

## 2. PPR — Tool Surface (9)

```python
# MCP tools/call 표면 — 전체 9개. 내부 Hub tool과 매핑 분리.
# 출력 포맷: 응답은 MCP content[0].text에 JSON-serialized 결과

def register(agent: str, room: Optional[str] = None) -> dict:
    """에이전트 등록 + 룸 참여. room 생략 시 seaai-general"""
    # Hub: seaai_register_agent(agent_id, token=HMAC(agent_id))
    #    → seaai_join_room(agent_id, room_id)
    # Local: AgentPool._agents[agent] = AgentState(agent, [room])
    # return: {"ok": True, "agent": agent}

def unregister(agent: str) -> dict:
    """에이전트 제거. 모든 룸 leave 후 state 삭제"""
    # Hub: for room in state.rooms: seaai_leave_room(...)
    # return: {"ok": True}

def join(agent: str, room: str) -> dict:
    # Hub: seaai_join_room(agent, room) → state.rooms.append(room)
    # return: {"ok": True}

def leave(agent: str, room: str) -> dict:
    # Hub: seaai_leave_room(agent, room) → state.rooms.remove(room)
    # return: {"ok": True}

def rooms(agent: Optional[str] = None) -> dict:
    """룸 목록. agent 생략 시 전체 매핑"""
    # return: {"rooms": [...] | {agent: [...], ...}}

def poll(agent: str, room: Optional[str] = None) -> list[dict]:
    """새 메시지 수신 — 최소 포맷 {from, body, ts}"""
    # 1) drain offline_buffer (FIFO)
    # 2) Hub: seaai_get_agent_messages(agent_id) → all_msgs
    # 3) dedup via state.seen_ids (10000 초과 시 전체 clear)
    # 4) room filter (optional)
    # 5) 3-field projection
    # return: [{"from": str, "body": str, "ts": float}, ...]

def send(agent: str, body: str, to: str = "*", room: Optional[str] = None) -> dict:
    """메시지 발송 — sig/ts 자동 생성, intent=chat 고정"""
    # ts = round(time.time(), 6)
    # sig = HMAC-SHA256(shared_secret, sha256(body|ts_ms))
    # Hub: seaai_send_message(from=agent, to=[to] or "*", room_id=room,
    #                         pg_payload={intent:"chat", body, ts}, sig)
    # return: {"ok": True}

def status() -> dict:
    """브리지 상태 — Hub 연결/uptime/에이전트/룸/버퍼"""
    # return: {"hub": bool, "uptime": int, "agents": [...],
    #          "rooms": {room: [agents]}, "buffered": int}

def sleep(seconds: float) -> dict:
    """대기 — ADP 루프 throttle용"""
    # time.sleep(seconds)
    # return: {"ok": True, "slept": seconds}
```

**내부 Hub tool 매핑 (하드코딩)**:

```text
hub_tool_names
  seaai_register_agent     # register 용
  seaai_join_room          # register/join 용
  seaai_leave_room         # unregister/leave 용
  seaai_get_agent_messages # poll 용
  seaai_send_message       # send 용
  seaai_list_rooms         # health ping 용 (부작용 없는 호출)
```

---

## 3. PPR — 핵심 Def 블록

### 3.1 TcpClient.rpc (Thread-Safe + 자동 재연결 트리거)

```python
def rpc(self, method: str, params: dict) -> dict:
    """JSON-RPC over newline TCP. lock 보호. 실패 시 ConnectionError 전파"""
    with self._lock:  # threading.Lock — 모든 rpc 직렬화
        try:
            return self._rpc_raw(method, params)
        except (ConnectionError, OSError, RuntimeError) as e:
            self._connected = False
            raise ConnectionError(f"Hub unreachable: {e}")
    # criteria:
    #   - 한 번에 하나의 rpc만 실행 (lock)
    #   - 실패 시 connected=False 플래그
    #   - 재연결은 호출자(health loop 또는 trigger_reconnect)가 수행
```

### 3.2 TcpClient.reconnect (지수 백오프)

```python
def reconnect(self) -> None:
    """성공할 때까지 무한 재시도. 성공 시 on_reconnect 콜백 호출"""
    self._connected = False
    delay = RECONNECT_BASE_DELAY  # 1
    attempt = 0
    while not self._stopping:
        attempt += 1
        try:
            self._close_silent()
            sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=10)
            self._rpc_raw("initialize", {})
            self._connected = True
            if self._on_reconnect:
                self._on_reconnect()  # → AgentPool.reregister_all
            return
        except Exception:
            time.sleep(delay)
            delay = min(delay * 2, RECONNECT_MAX_DELAY)  # 1→2→4→...→30 cap
```

### 3.3 AgentPool.build_sig (HMAC 순서 고정)

```python
def build_sig(self, body: str, ts: float) -> str:
    """HMAC-SHA256 — Rust 포팅 시 바이트 순서 정확히 일치 필수"""
    ts_ms = str(int(float(ts) * 1000))  # ← float 반올림 정밀도 주의
    d = hashlib.sha256()
    d.update(body.encode("utf-8"))
    d.update(ts_ms.encode("utf-8"))
    return hmac.new(SHARED_SECRET, d.digest(), hashlib.sha256).hexdigest()
    # criteria:
    #   - 동일 (body, ts) → 동일 sig 결정론
    #   - Rust 포팅 시 golden test: 10 샘플 py ↔ rs 일치
```

### 3.4 MessageRouter.poll (dedup + buffer + filter)

```python
def poll(self, agent_id: str, room: Optional[str] = None) -> list[dict]:
    state = self._pool.get_state(agent_id)

    # 1) offline buffer 선행 (FIFO)
    buffered = self._pool.drain_offline(agent_id)

    # 2) Hub에서 새 메시지
    try:
        raw = self._tcp.tool_call("seaai_get_agent_messages",
                                  {"agent_id": agent_id})
        all_msgs = raw.get("messages", [])
    except Exception:
        all_msgs = []  # 실패 무시 — buffer만 반환

    result = list(buffered)

    # 3) dedup + room filter + 3-field projection
    for msg in all_msgs:
        msg_id = msg.get("id", "")
        if msg_id in state.seen_ids:
            continue
        state.seen_ids.add(msg_id)
        if room and msg.get("room_id") != room:
            continue
        result.append({
            "from": msg.get("from", ""),
            "body": msg.get("body", ""),
            "ts": msg.get("ts", 0),
        })

    # 4) dedup cache TTL — 10000 초과 시 전체 clear (LRU 아님)
    if len(state.seen_ids) > 10000:
        state.seen_ids.clear()

    return result
    # notes:
    #   - config.DEDUP_TTL=3600 은 선언되어 있으나 실제로 미사용 (dead code)
    #   - offline buffer와 Hub 메시지의 순서: buffer 먼저
```

### 3.5 MessageRouter.send (sig/ts 생성)

```python
def send(self, agent_id: str, body: str,
         to: str = "*", room: Optional[str] = None) -> None:
    state = self._pool.get_state(agent_id)
    room = room or (state.rooms[0] if state.rooms else "seaai-general")
    ts = round(time.time(), 6)  # 초, 6자리
    sig = self._pool.build_sig(body, ts)

    self._tcp.tool_call("seaai_send_message", {
        "from": agent_id,
        "to": [to] if to != "*" else "*",  # "*" → 문자열 그대로, 그 외 → 리스트 래핑
        "room_id": room,
        "pg_payload": {"intent": "chat", "body": body, "ts": ts},
        "sig": sig,
    })
```

### 3.6 ★ MMEBridge.handle_tool — BUG SUSPECT

```python
# AS-IS (mme_server.py lines 163-242) — 그대로 옮김. 구조 이상 표시.
def handle_tool(self, name, args):
    # 연결 확인
    if not self.tcp.connected:
        self._trigger_reconnect()
        if name not in ("status", "sleep"):
            return {"error": "Hub offline — reconnecting"}
    # ↓ 여기서 메서드가 암묵적으로 끝남 (return 없음)
    # ↓ tcp 연결 상태일 때: handle_tool이 None 반환
    # ↓ MCP 응답: {"content":[{"type":"text","text":"null"}]}

def _trigger_reconnect(self):
    """백그라운드 재연결 (블로킹 없음)"""
    if hasattr(self, "_reconnecting") and self._reconnecting:
        return
    self._reconnecting = True
    def _do():
        try:
            self.tcp.reconnect()
        finally:
            self._reconnecting = False
    import threading
    threading.Thread(target=_do, daemon=True).start()

    # ★★★ 여기부터 242줄까지 — dispatch 로직이 _trigger_reconnect 안에 갇혀있음 ★★★
    # name, args 참조하지만 _trigger_reconnect의 스코프에 존재하지 않음 → 실행 시 NameError
    try:
        if name == "register":          # ← NameError: name is not defined
            self.pool.register(args["agent"], args.get("room"))
            return {"ok": True, "agent": args["agent"]}
        elif name == "unregister": ...
        elif name == "join": ...
        elif name == "leave": ...
        elif name == "rooms": ...
        elif name == "poll": ...
        elif name == "send": ...
        elif name == "status": ...
        elif name == "sleep": ...
        else:
            return {"error": f"unknown tool: {name}"}
    except ConnectionError:
        return {"error": "Hub connection lost — reconnecting"}
    except Exception as e:
        return {"error": str(e)}

# BUG ANALYSIS:
#   bug_class    "structural indentation — dead code + NameError latent"
#   impact_A     "tcp 연결 정상: handle_tool이 None 반환 → 모든 tool 응답이 'null'"
#   impact_B     "tcp 끊김 + register 호출: _trigger_reconnect의 try 블록 진입 → NameError"
#   paradox      "MMHT v2는 0-error 완주했다고 기록됨 — 모순"
#   hypotheses
#     H1  "배포 중인 서버가 디스크 파일과 다름 (수동 수정본 메모리 상주)"
#     H2  "MMHT v2 결과 리포트가 낙관적 — 실제로는 'null' 응답이 있었으나 client가 관대하게 처리"
#     H3  "파일 최근 수정 — 수정 과정에서 들여쓰기 망가짐 (git log 확인 필요)"
#   required_action "프로세스 재기동 전 git log + diff + 실행 중 서버 바이트코드 확인"
```

### 3.7 McpHandler.do_POST — HTTP 엔트리

```python
def do_POST(self):
    if self.path != "/mcp":
        self.send_error(404)
        return

    body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
    req = json.loads(body)
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    if method == "initialize":
        result = {"protocolVersion": "2024-11-05",
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "micro-mcp-express", "version": "1.0.0"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}  # 9개 스키마
    elif method == "tools/call":
        output = bridge.handle_tool(params.get("name", ""),
                                    params.get("arguments", {}))
        result = {"content": [{"type": "text",
                                "text": json.dumps(output, ensure_ascii=False)}],
                  "isError": False}
    elif method.startswith("notifications/"):
        result = {}
    else:
        return self._jsonrpc_error(req_id, -32601, f"unknown method: {method}")

    self._jsonrpc_response(req_id, result)
```

### 3.8 McpHandler.do_GET — /health

```python
def do_GET(self):
    if self.path != "/health":
        return self.send_error(404)

    # TCP lock 안 잡고 직접 읽기 (주의: race 가능하나 경미)
    agents = list(bridge.pool.agents.keys()) if bridge.pool else []
    rooms = {}
    if bridge.pool:
        for aid, st in bridge.pool.agents.items():
            for r in st.rooms:
                rooms.setdefault(r, []).append(aid)
    buf = sum(len(a.offline_buffer) for a in bridge.pool.agents.values()) \
          if bridge.pool else 0

    self._json_response(200, {
        "status": "ok" if bridge.tcp.connected else "degraded",
        "hub": bridge.tcp.connected,
        "uptime": int(time.time() - bridge._started),
        "agents": agents,
        "rooms": rooms,
        "buffered": buf,
    })
```

---

## 4. Data Flow — 시퀀스 뷰

```text
SequencePoll // poll 흐름 (done)
    # 1. AI client → POST /mcp {method:"tools/call", name:"poll", args:{agent, room}}
    # 2. McpHandler.do_POST → bridge.handle_tool("poll", args)
    # 3. MMEBridge → MessageRouter.poll(agent, room)
    # 4. Router → AgentPool.drain_offline(agent)  [buffer 선행]
    # 5. Router → TcpClient.tool_call("seaai_get_agent_messages", {agent_id})
    # 6. TcpClient.rpc(locked) → Hub TCP send+recv newline JSON
    # 7. Router → dedup + room filter + 3-field projection
    # 8. handle_tool → {content:[{type:"text", text:json(result)}]} 반환
    # 9. do_POST → HTTP 200 JSON-RPC response

SequenceSend // send 흐름 (done)
    # 1. AI client → POST /mcp tools/call send
    # 2. handle_tool → MessageRouter.send
    # 3. Router → AgentPool.build_sig(body, ts)
    # 4. Router → TcpClient.tool_call("seaai_send_message", {..., sig})
    # 5. Hub 브로드캐스트 (sender 제외)
    # 6. 타 에이전트들의 poll에서 수신

SequenceReconnect // 재연결 흐름 (needs-verify)
    # Trigger A: TcpClient.health_loop 30s ping 실패
    # Trigger B: handle_tool이 tcp.connected=False 감지 (but BUG: dispatch 미실행)
    # → TcpClient.reconnect() 지수 백오프
    # → 성공 시 on_reconnect 콜백 → AgentPool.reregister_all
    # → 모든 에이전트 register_agent + join_room 재수행
    # → state.seen_ids / offline_buffer 는 로컬이므로 유지
```

---

## 5. Resilience & Invariants

```text
invariants // 불변 조건 (done)
    inv_1 // AgentPool._agents는 메모리 유일 정본 — Hub는 권위 있는 복제본 (done)
    inv_2 // seen_ids는 per-agent, MME 재시작 시 소실 — Hub 재전송 시 중복 가능 (done)
    inv_3 // offline_buffer는 FIFO cap 500, 초과 시 최오래된 항목 drop (done)
    inv_4 // HMAC sig 입력 순서 고정: body|ts_ms (Rust 포팅 필수 일치) (done)
    inv_5 // Hub "*" to 파라미터: 문자열 그대로, 특정 수신자면 [id] 리스트 (done)
    inv_6 // intent 고정값 "chat" — 확장 시 tool 파라미터 추가 필요 (done)
    inv_7 // dedup cap=10000, 초과 시 전체 clear (LRU 아님) — 의도적 단순화 (done)

resilience_scenarios
    hub_crash     // health_ping 실패 → 지수 백오프 재연결 → reregister_all. AI 세션 무영향 (done)
    bridge_crash  // 사람이 재기동 필요. buffer/seen_ids 소실 (done)
    network_jitter // 다음 health_ping에서 자동 복구. 메시지 유실 가능성 (done)
    hub_offline_start // init 시 warn만 남기고 넘어감. 첫 호출부터 재연결 트리거 (needs-verify)  #BUG
```

---

## 6. Known Issues — 재설계에서 고칠 목록

```text
issues
    I1 // mme_server.py handle_tool 구조 버그 (blocked) #BUG-P0
        # 증상: dispatch 블록이 _trigger_reconnect 내부에 갇힘, name/args NameError
        # 영향: handle_tool 정상 경로가 None 반환 → 모든 MCP 응답 "null"
        # 수정: dispatch 코드를 handle_tool 본체로 되돌림, _trigger_reconnect는 순수 재연결만
        # 재설계 항목: 타입안전 enum dispatch로 재구성 (Rust에서 자연스럽게 해결)

    I2 // DEDUP_TTL 설정 미사용 (dead code) (needs-verify)
        # 증상: config.DEDUP_TTL=3600 선언되어 있으나 message_router.poll은 cap으로만 관리
        # 수정: 실제 TTL 시계 기반 정리 도입 OR 설정 제거
        # 재설계: Rust에서 time-based expiry 구현 권장 (HashMap<String, Instant>)

    I3 // offline_buffer pop(0) O(N) (in-progress)
        # 증상: Python list.pop(0) 선형 시간. cap 500에선 경미하나 상징적
        # 수정: collections.deque 또는 Rust VecDeque

    I4 // TcpClient 단일 글로벌 lock (needs-verify)
        # 증상: 모든 rpc가 threading.Lock 직렬화 → 동시성 상한 낮음
        # 영향: 9+ agent 동시 poll 시 지연 누적
        # 재설계: mpsc worker + request/response correlation by req_id

    I5 // seen_ids cap clear 방식이 LRU 아님 (needs-verify)
        # 증상: 10000 초과 시 전체 비움 → 직후 재전송 시 중복 허용
        # 재설계: LRU 또는 time-based eviction

    I6 // Hub offline 시 init 워닝만 남김 (needs-verify)
        # 증상: Hub 미기동 상태로 MME 기동 시 _trigger_reconnect 호출 경로가 버그로 작동 불명
        # 수정: I1 해결 후 재검증

    I7 // handle_tool의 _reconnecting 플래그가 동적 속성 (needs-verify)
        # 증상: hasattr로 체크하는 동적 속성 — __init__에서 선언 안 됨
        # 수정: 명시적 필드로 이동

    I8 // intent=chat 고정 (designing)
        # 증상: send가 다른 intent 불가 (status/ack/control 등)
        # 재설계: send에 optional intent 파라미터 추가
```

---

## 7. Rust Redesign Guidance (다음 단계 입력용)

```text
rust_redesign_inputs // 다음 DESIGN-MmeRust.md의 입력 (designing)
    preserve // 동일성 보존 대상
        wire_compat        // MCP JSON-RPC 9 tool 표면 100% 동일
        hmac_byte_order    // body|ts_ms 순서, ts_ms=int(ts*1000) 문자열
        hub_tool_names     // seaai_* 하드코딩 그대로
        dedup_cap_10000    // 일단 동일 동작 유지, 개선은 phase 2
        buffer_cap_500     // FIFO
        intent_chat_default

    fix // 반드시 수정
        F1 // I1: handle_tool 구조 버그 — enum Tool + match 으로 재구성 (done-design)
        F2 // I2: DEDUP 정책 명확화 — cap or TTL 선택 후 단일화 (designing)
        F3 // I4: tcp 동시성 — mpsc worker + oneshot 응답 (designing)
        F4 // I3: offline buffer VecDeque (done-design)

    improve // 자연스러운 이득
        type_safe_dispatch   // enum + exhaustive match
        no_gil               // tokio async 전체
        single_binary        // nohup/PYTHONUTF8 불요
        observability        // tracing crate, JSON 로그
        shutdown_grace       // CancellationToken + graceful drain

    out_of_scope // 이번 포팅에서 제외
        api_extension        // 9 tool 그대로
        protocol_v2          // MCP 2024-11-05 유지
        new_hub_tools        // Hub 측 변경 없음

    parity_validation // 동치성 검증
        golden_tests // py 응답 dump → rs test assert
        shadow_run   // py:9902 + rs:9903 2~3일 병행
        mmht_v3      // 새 태그로 Rust MME 대상 재실행 (8 persona × 12 rounds)
```

---

## 8. File Map — Python → Rust 예상 매핑

```text
file_map // 매핑 가이드 (designing)
    config.py         → src/config.rs             # const + clap Args
    tcp_client.py     → src/hub_client.rs          # tokio TcpStream + LinesCodec
    agent_pool.py     → src/pool.rs                # DashMap<String, AgentState>
    message_router.py → src/router.rs              # impl methods
    mme_server.py     → src/server.rs + src/main.rs # axum routes + #[tokio::main]
    (HMAC/types 공유)  → src/wire.rs                # 추후 seaai-wire crate로 승격
    test_mme.py       → tests/integration.rs       # reqwest 기반
    (신규)            → tests/golden/              # py 응답 dump fixtures
```

---

## 9. Acceptance — 이 문서 완료 기준

```text
acceptance
    - [x] 5 파이썬 파일 전원 Gantree에 모듈 노드로 등장
    - [x] 9 tool 표면 전체 PPR 시그니처 기록
    - [x] TcpClient.rpc/reconnect, AgentPool.build_sig, Router.poll/send 핵심 def 포함
    - [x] mme_server.py 구조 버그 명시 기록 (I1)
    - [x] 재설계 입력용 Issues(I1~I8) 목록화
    - [x] Rust 매핑 초안 포함 (file_map)
    - [ ] 양정욱님 검토 — 이 문서 기반으로 다음 단계 진행 승인
```

---

## 10. Next Steps

```text
next
    step1 // I1 버그 진위 확인 — 실행 중 서버 vs 디스크 파일 diff (in-progress)
          # git log mme_server.py → 최근 수정 이력
          # 실행 중 프로세스의 handle_tool 바이트코드 vs 파일 (신뢰 가능하다면)
          # MMHT v2 transcript에서 "null" 응답 흔적 검색

    step2 // DESIGN-MmeRedesign.md — 버그 수정 반영된 목표 아키텍처 (designing)
          # Python 수정본이 아닌 "재설계 청사진" — 타입 안전 dispatch, 동시성, observability

    step3 // DESIGN-MmeRust.md — Rust 구체 설계 (designing)
          # Cargo.toml, crate 구조, tokio 런타임, axum 라우팅, 의존성 확정

    step4 // plan + execute — WORKPLAN 생성 및 구현 (designing)
          # PGF loop 또는 full-cycle

    step5 // parity + shadow + MMHT v3 검증 (designing)
```

---

*이 문서는 AS-IS baseline이다. 수정 금지. 재설계·Rust 설계는 별도 DESIGN 파일로 분리한다.*
*작성: clcon @ 2026-04-11, source: `D:/SeAAI/SeAAIHub/tools/mme/` 5 파일 736 LOC*
