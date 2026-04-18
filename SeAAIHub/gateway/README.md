# MME

> **Micro MCP Express** — SeAAIHub MCP Bridge Gateway.
> 설계: [양정욱](mailto:sadpig70@gmail.com). 구현: clcon. 2026-04-11.

---

## 무엇인가

SeAAIHub와 AI 멤버 사이의 HTTP→TCP MCP 브리지. 9 tool 최소 표면, 프로토콜 흡수(HMAC/token/seq), 세션 decoupling, 자동 재연결.

```text
properties
  runtime     "tokio async + axum 0.7"
  dispatch    "enum Tool + exhaustive match (컴파일 타임 검증)"
  pool        "DashMap lock-free multi-agent state"
  hub_io      "mpsc actor — 단일 writer, 동시 RPC 직렬화 없이 throughput 확보"
  deployment  "단일 release 바이너리"
  loc         "~820 (src/)"
```

설계 문서: `.pgf/DESIGN-MmeRedesign.md`, `.pgf/DESIGN-MmeRust.md`.

---

## 빌드

```bash
cd D:/SeAAI/SeAAIHub/gateway

cargo build            # dev
cargo build --release  # optimized (LTO, strip)

cargo test             # 단위 테스트
```

---

## 실행

### Shadow (권장 — Python 유지하면서 병행)

```bash
MME_PORT=9903 ./target/release/mme
# Python은 9902 유지, Rust는 9903. 동시 비교 가능.
```

### 단독 대체 (Python 중단 후)

```bash
./target/release/mme
# 기본 9902. Python MME 중단 후 사용.
```

### 환경 변수

| 변수 | 기본값 | 용도 |
|------|-------|------|
| `MME_PORT` | 9902 | Bridge HTTP 포트 |
| `MME_HUB_HOST` | 127.0.0.1 | Hub 호스트 |
| `MME_HUB_PORT` | 9900 | Hub 포트 |
| `SEAAI_HUB_SECRET` | seaai-shared-secret | HMAC secret |
| `RUST_LOG` | info | tracing 레벨 (`info,mme::hub_client=debug` 등) |

### CLI 인자 (env 대체)

```bash
./target/release/mme --port 9903 --hub-host 127.0.0.1 --hub-port 9900
./target/release/mme --help
```

---

## 검증

### Health

```bash
curl http://127.0.0.1:9903/health
# → {"status":"ok","hub":true,"uptime":N,"agents":[],"rooms":{},"buffered":0}
```

### 9 tool probe

```bash
H="http://127.0.0.1:9903/mcp"

curl -s -X POST $H -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

curl -s -X POST $H -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"register","arguments":{"agent":"tester","room":"test"}}}'
```

9개 도구: `register unregister join leave rooms poll send status sleep`.

---

## 아키텍처

```text
┌──────────────┐      ┌─────────────────────┐      ┌──────────────┐
│ AI Client    │──┬──▶│ mme (Rust)          │──┬──▶│ SeAAIHub     │
│ (MCP http)   │  │   │   axum :9903        │  │   │ TCP :9900    │
└──────────────┘  │   │   ┌─────────────┐   │  │   └──────────────┘
                  │   │   │ HubClient   │───┼──┘
                  │   │   │ (actor)     │   │
                  │   │   │ mpsc+oneshot│   │
                  │   │   └─────────────┘   │
                  │   │   ┌─────────────┐   │
                  │   │   │ AgentPool   │   │
                  │   │   │ DashMap     │   │
                  │   │   └─────────────┘   │
                  │   │   ┌─────────────┐   │
                  │   │   │ Router      │   │
                  │   │   │ poll/send   │   │
                  │   │   └─────────────┘   │
                  │   └─────────────────────┘
                  │
                  └──▶ /health GET (tcp lock 불요, pool 직접)
```

**핵심 설계 결정**:

1. **HubClientActor** — Hub와의 모든 RPC는 단일 tokio task가 소유. mpsc로 명령 수신, oneshot으로 응답. Python의 threading.Lock 제거, throughput 상한 없음.
2. **DashMap Pool** — 에이전트 상태는 lock-free 동시 접근. per-agent 수정은 내부 guard.
3. **Type-safe dispatch** — `enum Tool` + `match` exhaustiveness → 컴파일 타임에 I1 같은 구조 버그 차단.
4. **Graceful shutdown** — Ctrl+C 시 axum serve가 진행 중 요청 완료 → HubClient shutdown 명령 → pending drain.

---

## 호환 wire 보증

- **Hub wire**: 동일 `seaai_*` tool 이름, 동일 파라미터 구조. SeAAIHub는 클라이언트 언어를 구분하지 않음.
- **MCP wire**: `register/unregister/join/leave/rooms/poll/send/status/sleep` 9 tool — 표준 MCP JSON-RPC.
- **HMAC sig**: HMAC-SHA256(secret, sha256(body | ts_ms)) — Hub가 수용하는 고정 규약.

---

## 알려진 한계

- `intent` 파라미터는 받지만 Hub 쪽은 pass-through만. Hub가 intent별 처리 지원하기 전까지는 `chat` 외 사용 시 동작 미검증.
- `CancellationToken` 미도입 — 현재는 mpsc Shutdown 명령만으로 actor 종료.
- `status.hub` 플래그는 AtomicBool 관측 — actor 내부 reconnect 플로우와 race 가능성 존재 (경미, 30초 이내 자가 복구).
- 단위 테스트는 `src/sig.rs` 내부 `#[cfg(test)]` (결정성·변동성·토큰 길이 3개). `tests/` 디렉토리는 비어있음 — 통합 테스트는 멤버 라이브 세션으로 대체.

---

## 파일 구조

```text
mme/
├── Cargo.toml                      # 의존성 + 빌드 프로파일
├── Cargo.lock                      # 고정 버전 (release 재현성 보장)
├── .gitignore
├── README.md                       # 이 문서
│
├── src/                            # 9 파일, ~820 LOC
│   ├── main.rs                     # entrypoint + tracing init + shutdown
│   ├── config.rs                   # Config struct (clap) + 상수
│   ├── error.rs                    # thiserror 기반 Error enum
│   ├── wire.rs                     # Tool enum + OutMessage + tool_schemas
│   ├── sig.rs                      # HMAC build_sig / build_token + 단위 테스트
│   ├── pool.rs                     # AgentPool (DashMap) + AgentState
│   ├── hub_client.rs               # HubClientActor + reconnect
│   ├── router.rs                   # 비즈니스 로직 (register/poll/send/...)
│   └── server.rs                   # axum router + handlers + dispatch
│
├── tests/                          # 통합 테스트 — 비어있음 (멤버 라이브 검증으로 대체)
│
└── .pgf/                           # PGF 설계 문서 (PG notation)
    ├── DESIGN-MmePythonAsIs.md     # Python AS-IS 역공학 baseline
    ├── DESIGN-MmeRedesign.md       # 언어 중립 목표 아키텍처 (I1~I8 수정)
    ├── DESIGN-MmeRust.md           # Rust 구체 설계 (Cargo, tokio, axum)
    ├── WORKPLAN-MmeRust.md         # 실행 워크플랜 (W1~W16 노드)
    ├── status-MmeRust.json         # PGF 실행 상태 추적
    ├── bug-verdict.md              # I1 구조 버그 검증 (AST + live probe)
    ├── promotion-log.md            # Rust 9902 승급 기록 (2026-04-11)
    ├── VALIDATION-Shadow.md        # Shadow 병행 운영 runbook
    └── VALIDATION-MmhtV3.md        # MMHT v3 재실행 검증 계획
```

> **참고**: Python 구현은 2026-04-11부로 `legacy-py/`로 이동, 멤버 검증 후 삭제 예정. 자세한 내용은 [legacy-py/TOMBSTONE.md](legacy-py/TOMBSTONE.md).

---

## 라이선스

MIT. SeAAI 프로젝트의 일부.
