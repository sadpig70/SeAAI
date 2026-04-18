# DESIGN-MmeRedesign

> **목적**: AS-IS에서 I1~I8 수정한 **언어 중립 목표 아키텍처**.
> Python 수정본이 아니다. Rust 구현의 청사진이며 py reference로도 사용 가능.
> **상위 문서**: DESIGN-MmePythonAsIs.md, bug-verdict.md
> **하위 문서**: DESIGN-MmeRust.md
> **상태**: designing → locked after 양정욱님 검토

---

## 0. Scope

```text
scope
  in
    - 9 MCP tool 표면 100% 동일
    - Hub wire 프로토콜 100% 동일 (seaai_* tool 이름, HMAC, JSON-RPC newline TCP)
    - 3대 설계 목적 유지 (token minimization / session decoupling / protocol absorption)
    - 버그 I1 구조적 제거, I2~I8 정책 정리
    - observability 강화 (tracing)

  out
    - 9 tool API 확장 (intent 다양화는 phase 2)
    - 새 Hub tool 추가
    - MCP 프로토콜 버전 업그레이드 (2024-11-05 유지)
    - 멀티 Bridge 또는 Hub 페더레이션
```

---

## 1. Target Architecture (Gantree)

```text
MmeRedesign // 언어 중립 목표 아키텍처 (designing) @v:2.0
    Goals // 설계 목표 (done)
        G1 // token/session/absorption 3대 원칙 유지 (done)
        G2 // 구조적 type safety — dispatch 오류 원천 차단 (done)
        G3 // 동시성 상한 제거 — 9 → 100+ agents 수용 (done)
        G4 // observability — 모든 경로 tracing + metrics (done)
        G5 // graceful shutdown — 메시지 drain + Hub unregister (done)

    CoreModules // 모듈 구조 (designing)
        Config // 환경변수 + CLI 인자 + 상수 (done)
        Wire // 공유 타입 + HMAC + MCP/Hub JSON 스키마 (done)
        HubClient // Hub TCP 연결 + rpc + 재연결 (in-progress)
        Pool // AgentState 저장 + HMAC token + offline buffer (done)
        Router // poll/send 비즈니스 로직 (done)
        Server // HTTP /mcp + /health + tool dispatch (done)
        Observability // tracing subscriber + metrics (designing)
        Shutdown // signal handler + graceful drain (designing)

    ConcurrencyModel // 동시성 모델 (in-progress)
        HubClientActor // single-writer task, mpsc 명령 수신, oneshot 응답
        PoolStorage // DashMap<String, AgentState> — lock-free
        HealthLoop // 독립 tokio task, cancellation token 수신
        ReconnectTask // 독립 tokio task, 지수 백오프

    TypeSystem // 타입 중심 설계 (done)
        ToolEnum // enum Tool { Register, Unregister, ..., Sleep } + match (done)
        WireTypes // serde Deserialize — 런타임 검증 (done)
        ErrorKinds // enum Error { HubOffline, NotRegistered, Protocol, ... } (done)
```

---

## 2. Issue Fix Matrix (I1~I8)

| ID  | AS-IS 문제 | 재설계 해결 |
|-----|-----------|------------|
| I1  | handle_tool dispatch 구조 버그 | `enum Tool` + `match tool { Tool::Register(args) => ... }` — 컴파일 타임 exhaustiveness |
| I2  | DEDUP_TTL 미사용 dead code | 정책 단일화: **cap 10000 고정** (time TTL은 phase 2). config에서 TTL 제거 |
| I3  | offline_buffer pop(0) O(N) | `VecDeque<Msg>` push_back/pop_front O(1) |
| I4  | TcpClient 단일 글로벌 lock | **HubClientActor** — mpsc<Command> + oneshot<Response>, 단일 writer |
| I5  | seen_ids cap clear 전체 비움 | 동일 동작 유지 (parity 우선). LRU는 phase 2 TODO 명시 |
| I6  | Hub offline init 시 handling 불명 | 명시적 상태: `enum HubState { Connecting, Connected, Reconnecting, Offline }` |
| I7  | _reconnecting 동적 속성 | HubClientActor state 필드로 명시 — 타입 안전 |
| I8  | intent=chat 고정 | `send(..., intent: Option<String>)` 옵션 파라미터. 생략 시 "chat" — 하위호환 |

---

## 3. PPR — Core Contracts

### 3.1 Tool Dispatch (enum-based, I1 fix)

```python
# 언어 중립 명세 — Rust에서는 enum, Python에서는 dataclass union
Tool = Union[
    Register,       # {agent: str, room: Optional[str]}
    Unregister,     # {agent: str}
    Join,           # {agent: str, room: str}
    Leave,          # {agent: str, room: str}
    Rooms,          # {agent: Optional[str]}
    Poll,           # {agent: str, room: Optional[str]}
    Send,           # {agent: str, body: str, to: str="*", room: Optional[str], intent: Optional[str]}
    Status,         # {}
    Sleep,          # {seconds: float}
]

def handle_tool(tool: Tool, state: BridgeState) -> Result[ToolResponse, Error]:
    """exhaustive match — 컴파일러가 모든 variant 처리 강제"""
    # acceptance_criteria:
    #   - 9 variant 전부 처리 — 누락 시 컴파일 실패
    #   - 각 variant는 독립 함수로 위임
    #   - Error variant는 ToolResponse로 변환되어 MCP "isError":true로 응답
    #   - handle_tool 본체는 None/null을 절대 반환하지 않음 (타입으로 보증)
```

### 3.2 HubClientActor (I4, I6, I7 fix)

```python
# 단일 writer task — 모든 Hub RPC가 이 actor를 통과
def hub_actor_loop(rx: mpsc.Receiver[HubCmd], cfg: Config):
    """
    상태 기계:
      Connecting → Connected → (실패) → Reconnecting → Connected
      Reconnecting 중 들어오는 요청은 HubOffline 즉시 에러 반환
      (status/sleep 제외 — 이들은 Hub 불필요)
    """
    state: HubState = HubState.Connecting
    stream: Optional[TcpStream] = None
    next_req_id: int = 0
    pending: dict[int, oneshot.Sender] = {}  # req_id → responder

    while True:
        select:
            case cmd := await rx.recv():
                if cmd.is_shutdown():
                    graceful_close(stream)
                    break
                if state != HubState.Connected:
                    cmd.responder.send(Err(Error.HubOffline))
                    continue
                req_id = next_req_id; next_req_id += 1
                pending[req_id] = cmd.responder
                write_json_line(stream, build_rpc(cmd, req_id))

            case line := await stream.read_line():
                resp = parse_rpc(line)
                responder = pending.pop(resp.id, None)
                if responder:
                    responder.send(resp.result)

            case _ := await health_tick(interval=30s):
                if state == HubState.Connected:
                    spawn_task(health_ping_via_self(tx))

            case _ := await reconnect_signal():
                state = HubState.Reconnecting
                stream = await reconnect_with_backoff(cfg)
                state = HubState.Connected
                notify_pool_reregister_all()
    # acceptance_criteria:
    #   - 동시 RPC 요청이 직렬화되되 throughput이 lock보다 높음
    #   - 응답이 req_id로 정확히 매칭됨
    #   - 재연결 중 status/sleep은 여전히 응답 가능
    #   - shutdown 시 pending 요청에 모두 Err(Shutdown) 반환
```

### 3.3 Poll (I5: dedup cap 유지)

```python
def poll(agent: str, room: Optional[str]) -> list[Message]:
    state = pool.get(agent)  # Error.NotRegistered if absent

    # 1) offline buffer drain (FIFO, VecDeque.drain)
    out = state.offline_buffer.drain()

    # 2) Hub messages via actor
    try:
        raw = hub.rpc("seaai_get_agent_messages", {"agent_id": agent})
        msgs = raw.get("messages", [])
    except Error.HubOffline:
        return out  # buffer-only response

    # 3) dedup + room filter + 3-field projection
    for m in msgs:
        if m.id in state.seen_ids:
            continue
        state.seen_ids.insert(m.id)
        if room and m.room_id != room:
            continue
        out.append(Message(from_=m.sender, body=m.body, ts=m.ts))

    # 4) cap — 전체 clear (AS-IS 동작 유지, parity 우선)
    if len(state.seen_ids) > 10000:
        state.seen_ids.clear()
        # TODO(phase2): LRU or time-based eviction

    return out
```

### 3.4 Send (I8: intent 옵션화)

```python
def send(agent: str, body: str, to: str = "*",
         room: Optional[str] = None, intent: Optional[str] = None) -> Ack:
    state = pool.get(agent)
    room = room or state.rooms.first() or "seaai-general"
    intent = intent or "chat"  # 하위호환
    ts = now_seconds_f6()  # round to microseconds (match Python time.time rounding)
    sig = build_sig(body, ts, shared_secret)

    hub.rpc("seaai_send_message", {
        "from": agent,
        "to": to if to == "*" else [to],  # "*" 문자열 vs [id] 리스트 구분 보존
        "room_id": room,
        "pg_payload": {"intent": intent, "body": body, "ts": ts},
        "sig": sig,
    })
    return Ack.ok()
```

### 3.5 HMAC Sig (invariant — Rust 포팅 필수 일치)

```python
def build_sig(body: str, ts: float, secret: bytes) -> str:
    """Python AS-IS 동일 — byte 순서 고정"""
    ts_ms = str(int(ts * 1000))  # ★ float→int cast, 반올림 X (truncation)
    inner = sha256(body.utf8() + ts_ms.utf8()).digest()  # 32 bytes
    return hmac_sha256(secret, inner).hex()
    # golden_test:
    #   - ("hello", 1712847600.123456) → 동일 hex digest
    #   - unicode body "안녕" → UTF-8 bytes 처리 일치
    #   - ts=0, ts=1e10 edge case 동일
```

### 3.6 Graceful Shutdown (G5)

```python
def shutdown(bridge: BridgeState):
    """SIGINT/SIGTERM 또는 Ctrl+C 시 호출"""
    # 1) HTTP 서버 accept 중지 (진행 중 요청은 완료 허용)
    http.stop_accepting()
    # 2) Hub actor에 shutdown 명령 — pending drain
    hub.send(HubCmd.Shutdown)
    hub.await_done(timeout=5s)
    # 3) 모든 에이전트 unregister 시도 (best effort)
    for agent in pool.agents():
        try:
            hub.rpc("seaai_leave_room", {"agent_id": agent, "room_id": "*"})
        except: pass
    # 4) tracing flush
    tracing.flush()
```

---

## 4. Data Model

```text
types
  AgentState
    agent_id        str
    rooms           list[str]           # 참여 중인 room
    seen_ids        HashSet[str]        # dedup, cap 10000
    offline_buffer  VecDeque[Message]   # cap 500
    # seq_counter 제거 — actor가 req_id 관리

  Message
    from_           str
    body            str
    ts              float                # seconds with microsecond precision

  HubState (enum)
    Connecting | Connected | Reconnecting | Offline

  Tool (enum, 9 variants — §3.1 참조)

  Error (enum)
    HubOffline
    NotRegistered(agent_id)
    Protocol(detail)
    InvalidArgs(field)
    Internal(source)

  ToolResponse (enum)
    Ok(serde_json::Value)  # tool별 성공 payload
    Err(Error)             # MCP isError:true로 변환
```

---

## 5. Concurrency Contracts

```text
contracts
  actor_single_writer
    "HubClientActor가 유일한 Hub stream writer"
    "pending map 관리 — req_id → oneshot Sender"
    "동시 RPC는 actor 큐에서 직렬화되나 throughput은 lock 방식보다 높음 (no poll wait)"

  pool_lock_free
    "DashMap으로 agent state 동시 접근"
    "per-agent state 수정은 write guard 하에서만"
    "seen_ids/offline_buffer는 state 내부이므로 agent별 직렬"

  health_loop
    "독립 tokio task, interval 30s"
    "CancellationToken으로 shutdown 시 즉시 중단"

  reconnect
    "HubClientActor가 스스로 감지 + 백오프"
    "재연결 성공 시 Pool.reregister_all 호출 (event/channel)"

  parallel_tools
    "9 tool 모두 동시 호출 가능 — Rust는 tokio spawn으로 대기열 없음"
    "Hub RPC는 actor로 직렬화되지만 local tool (status, sleep)은 완전 병렬"
```

---

## 6. Observability

```text
observability
  tracing
    subscriber   "fmt + json 출력 선택"
    level        "INFO default, DEBUG for tool calls"
    spans        "per MCP request, per Hub RPC"

  structured_log
    event_types
      - mcp.request    # method, tool, agent, duration
      - hub.rpc        # method, duration, success
      - pool.op        # op, agent, result
      - reconnect      # attempt, delay, outcome
      - health_ping    # outcome
      - error          # kind, source, context

  metrics_phase2  # 이번에는 안 함
    - mcp_requests_total{tool, status}
    - hub_rpc_duration_seconds
    - pool_agents_gauge
    - offline_buffer_usage
```

---

## 7. Configuration

```text
config
  env_compat      # 기존 환경변수 그대로 지원
    MME_PORT              9902
    MME_HUB_HOST          127.0.0.1
    MME_HUB_PORT          9900
    SEAAI_HUB_SECRET      "seaai-shared-secret"

  cli_args        # clap
    --port
    --hub-host
    --hub-port
    --shadow      # 옵션: 새 포트 9903 기본값, parity 모드
    --log-level

  constants       # Rust: const
    RECONNECT_BASE_DELAY_MS     1000
    RECONNECT_MAX_DELAY_MS      30000
    HEALTH_PING_INTERVAL_MS     30000
    MAX_OFFLINE_BUFFER          500
    DEDUP_CAP                   10000
    MCP_PROTOCOL_VERSION        "2024-11-05"
    SERVER_NAME                 "micro-mcp-express"
    SERVER_VERSION              "1.0.0-rs"
```

---

## 8. Acceptance Criteria

```text
acceptance
  functional
    - [ ] 9 tool 표면 JSON-RPC 응답이 Python 라이브 서버와 byte-level 호환
    - [ ] HMAC sig 10개 golden vector 전부 일치
    - [ ] Hub offline → reconnect 복구 후 에이전트 재등록 자동
    - [ ] /health 응답 스키마 Python 동일
    - [ ] offline buffer FIFO 동작 (cap 500)
    - [ ] dedup cap clear 10001번째에서 발동

  quality
    - [ ] cargo clippy -- -D warnings 통과
    - [ ] cargo test --all 통과
    - [ ] graceful shutdown 5초 내 완료
    - [ ] 100 concurrent MCP 요청 처리 (로컬)
    - [ ] tracing 이벤트 전 경로 관찰 가능

  parity
    - [ ] MMHT v3 (8 persona × 12 rounds) Python 대비 동일 transcript 구조
    - [ ] shadow 2~3일 병행 운영 0 crash
```

---

## 9. Non-Goals

```text
non_goals
  - MCP spec 2025-* 업그레이드
  - gRPC 또는 기타 transport 추가
  - multi-Hub 페더레이션
  - 영속 저장 (모든 state in-memory)
  - LRU dedup (phase 2)
  - time-based TTL (phase 2)
  - intent extension (send()의 intent 파라미터는 받되 Hub 쪽은 pass-through)
  - Windows service 등록, systemd unit (binary + nohup로 충분)
```

---

## 10. Handoff to DESIGN-MmeRust.md

```text
rust_design_inputs
  target_structure // §1 CoreModules Gantree
  issue_fixes      // §2 I1~I8 matrix
  ppr_contracts    // §3 5 core def blocks
  types            // §4 data model
  concurrency      // §5 actor + dashmap
  observability    // §6 tracing
  config           // §7 env + clap
  acceptance       // §8 체크리스트

  open_choices     // Rust design 단계에서 확정
    - axum vs hyper (raw)
    - dashmap vs tokio::Mutex<HashMap>
    - tracing vs log
    - reqwest 필요 여부 (test only)
    - HTTP 서버 listener: std TcpListener vs tokio::net
    - graceful shutdown crate (tokio-graceful-shutdown vs manual)
```

---

*언어 중립 청사진 완료. 다음: DESIGN-MmeRust.md — 구체 Rust 설계.*
