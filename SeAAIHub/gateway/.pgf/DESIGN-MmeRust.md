# DESIGN-MmeRust

> **목적**: MmeRedesign을 Rust/tokio로 구체화한 구현 청사진.
> **상위**: DESIGN-MmeRedesign.md
> **하위**: WORKPLAN-MmeRust.md (plan 단계에서 생성)
> **상태**: designing

---

## 0. Tech Choices (결정 확정)

```text
decisions
  runtime        tokio = "1"              # full features
  http_server    axum = "0.7"             # Router/extractors, 간결
  framing        tokio-util = "0.7"       # LinesCodec
  serde          serde = "1", serde_json = "1"
  hmac           hmac = "0.12", sha2 = "0.10"
  hex            hex = "0.4"
  concurrency    dashmap = "6"            # pool storage
  sync           tokio::sync::{mpsc, oneshot, watch}
  cli            clap = { version = "4", features = ["derive"] }
  tracing        tracing = "0.1", tracing-subscriber = { version = "0.3", features = ["env-filter","json"] }
  shutdown       manual — tokio::signal + CancellationToken (tokio-util)
  test           reqwest = "0.12"  (dev-dependencies only)

rejected
  hyper_raw      "axum이 충분히 얇음 — 선택 불필요"
  tokio_mutex    "dashmap이 Pool 접근 패턴에 더 자연스러움"
  log_crate      "tracing이 span 지원 — 관측성 우위"
```

## 1. Cargo Project Layout

```text
D:/SeAAI/SeAAIHub/tools/mme/
    .pgf/
        DESIGN-MmePythonAsIs.md
        DESIGN-MmeRedesign.md
        DESIGN-MmeRust.md         (this file)
        bug-verdict.md
        WORKPLAN-MmeRust.md       (생성 예정)
        status-MmeRust.json        (생성 예정)
    Cargo.toml
    src/
        main.rs            # entrypoint + clap + tracing init
        config.rs          # Config struct + env load
        error.rs           # enum Error, thiserror
        wire.rs            # types: Tool, Message, HubRpc, McpRpc
        hmac.rs            # build_sig + unit tests + golden
        hub_client.rs      # HubClientActor + reconnect
        pool.rs            # AgentPool (DashMap) + AgentState
        router.rs          # poll/send 비즈니스
        server.rs          # axum router + handlers
        shutdown.rs        # graceful shutdown helper
    tests/
        integration.rs     # reqwest 기반 end-to-end
        golden_hmac.rs     # HMAC 동일성 검증
    fixtures/
        hmac_vectors.json  # py ↔ rs 공유 golden
    README.md              # 빌드/실행/테스트 가이드
```

---

## 2. Cargo.toml 전문

```toml
[package]
name = "mme"
version = "1.0.0-rs.1"
edition = "2021"
authors = ["양정욱 <sadpig70@gmail.com>", "clcon"]
description = "Micro MCP Express — Rust port of SeAAIHub MCP Bridge Gateway"
license = "MIT"

[[bin]]
name = "mme"
path = "src/main.rs"

[dependencies]
tokio = { version = "1", features = ["full"] }
tokio-util = { version = "0.7", features = ["codec"] }
futures = "0.3"
axum = "0.7"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
clap = { version = "4", features = ["derive", "env"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }
hmac = "0.12"
sha2 = "0.10"
hex = "0.4"
dashmap = "6"
thiserror = "1"
anyhow = "1"

[dev-dependencies]
reqwest = { version = "0.12", features = ["json"] }
tokio = { version = "1", features = ["full", "test-util"] }

[profile.release]
lto = "thin"
codegen-units = 1
strip = true
```

---

## 3. Module PPR

### 3.1 `config.rs`

```rust
use clap::Parser;
use std::net::SocketAddr;

#[derive(Debug, Clone, Parser)]
#[command(name = "mme", version, about = "Micro MCP Express (Rust)")]
pub struct Config {
    #[arg(long, env = "MME_PORT", default_value_t = 9902)]
    pub port: u16,

    #[arg(long, env = "MME_HUB_HOST", default_value = "127.0.0.1")]
    pub hub_host: String,

    #[arg(long, env = "MME_HUB_PORT", default_value_t = 9900)]
    pub hub_port: u16,

    #[arg(long, env = "SEAAI_HUB_SECRET", default_value = "seaai-shared-secret")]
    pub shared_secret: String,

    #[arg(long, default_value = "info")]
    pub log_level: String,
}

pub const RECONNECT_BASE_DELAY_MS: u64 = 1_000;
pub const RECONNECT_MAX_DELAY_MS:  u64 = 30_000;
pub const HEALTH_PING_INTERVAL_MS: u64 = 30_000;
pub const MAX_OFFLINE_BUFFER:      usize = 500;
pub const DEDUP_CAP:               usize = 10_000;
pub const MCP_PROTOCOL_VERSION:    &str = "2024-11-05";
pub const SERVER_NAME:             &str = "micro-mcp-express";
pub const SERVER_VERSION:          &str = "1.0.0-rs";

impl Config {
    pub fn bind_addr(&self) -> SocketAddr {
        SocketAddr::from(([127, 0, 0, 1], self.port))
    }
    pub fn hub_addr(&self) -> String {
        format!("{}:{}", self.hub_host, self.hub_port)
    }
}
```

### 3.2 `error.rs`

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error("hub offline")]
    HubOffline,
    #[error("agent not registered: {0}")]
    NotRegistered(String),
    #[error("invalid args: {0}")]
    InvalidArgs(String),
    #[error("protocol: {0}")]
    Protocol(String),
    #[error("hub rpc error: {0}")]
    HubRpc(String),
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("json: {0}")]
    Json(#[from] serde_json::Error),
    #[error("shutdown")]
    Shutdown,
    #[error("internal: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, Error>;
```

### 3.3 `wire.rs`

```rust
use serde::{Deserialize, Serialize};
use serde_json::Value;

// ── MCP JSON-RPC (client-facing) ──

#[derive(Debug, Deserialize)]
pub struct McpRequest {
    pub jsonrpc: String,
    pub id: Value,
    pub method: String,
    #[serde(default)]
    pub params: Value,
}

#[derive(Debug, Serialize)]
pub struct McpResponse {
    pub jsonrpc: &'static str,
    pub id: Value,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<McpError>,
}

#[derive(Debug, Serialize)]
pub struct McpError {
    pub code: i32,
    pub message: String,
}

// ── Tool enum (I1 fix: exhaustive match) ──

#[derive(Debug, Deserialize)]
#[serde(tag = "name", content = "arguments", rename_all = "snake_case")]
pub enum Tool {
    Register { agent: String, #[serde(default)] room: Option<String> },
    Unregister { agent: String },
    Join { agent: String, room: String },
    Leave { agent: String, room: String },
    Rooms { #[serde(default)] agent: Option<String> },
    Poll { agent: String, #[serde(default)] room: Option<String> },
    Send {
        agent: String,
        body: String,
        #[serde(default = "default_to")] to: String,
        #[serde(default)] room: Option<String>,
        #[serde(default)] intent: Option<String>,
    },
    Status {},
    Sleep { seconds: f64 },
}
fn default_to() -> String { "*".to_string() }

// ── Projection payload (poll 응답 per message) ──

#[derive(Debug, Serialize)]
pub struct OutMessage {
    pub from: String,
    pub body: String,
    pub ts:   f64,
}

// ── Hub JSON-RPC (server-facing) ──

#[derive(Debug, Serialize)]
pub struct HubRequest<'a> {
    pub jsonrpc: &'static str,
    pub id: u64,
    pub method: &'static str,
    pub params: Value,
    // params = {"name":"seaai_...","arguments":{...}}
}

#[derive(Debug, Deserialize)]
pub struct HubResponse {
    pub id: u64,
    #[serde(default)]
    pub result: Option<Value>,
    #[serde(default)]
    pub error: Option<Value>,
}
```

### 3.4 `hmac.rs`

```rust
use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256};

type HmacSha256 = Hmac<Sha256>;

/// Python AS-IS 동일:
///   ts_ms = str(int(ts * 1000))
///   inner = sha256(body.utf8() + ts_ms.utf8()).digest()
///   sig = hmac_sha256(secret, inner).hex()
pub fn build_sig(secret: &[u8], body: &str, ts: f64) -> String {
    let ts_ms = (ts * 1000.0) as i64;  // truncation, same as int() in Python
    let ts_ms_s = ts_ms.to_string();

    let mut inner = Sha256::new();
    inner.update(body.as_bytes());
    inner.update(ts_ms_s.as_bytes());
    let digest = inner.finalize();

    let mut mac = HmacSha256::new_from_slice(secret).expect("hmac key");
    mac.update(&digest);
    hex::encode(mac.finalize().into_bytes())
}

/// Token: HMAC-SHA256(secret, agent_id)
pub fn build_token(secret: &[u8], agent_id: &str) -> String {
    let mut mac = HmacSha256::new_from_slice(secret).expect("hmac key");
    mac.update(agent_id.as_bytes());
    hex::encode(mac.finalize().into_bytes())
}

#[cfg(test)]
mod tests {
    use super::*;

    // golden vectors — must match Python build_sig
    #[test]
    fn golden_sig_hello() {
        let sig = build_sig(b"seaai-shared-secret", "hello", 1712847600.123456);
        assert_eq!(sig.len(), 64); // sha256 hex
        // 실제 값은 fixtures/hmac_vectors.json에서 Python이 생성한 것으로 교체
    }
}
```

### 3.5 `hub_client.rs` (HubClientActor)

```rust
use crate::{config::*, error::*, wire::*};
use serde_json::{json, Value};
use std::{collections::HashMap, sync::Arc};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::TcpStream,
    sync::{mpsc, oneshot, Notify},
    time::{sleep, Duration, Instant},
};
use tracing::{info, warn, error, debug};

pub enum HubCmd {
    Rpc {
        tool: &'static str,           // "seaai_register_agent" etc
        arguments: Value,
        responder: oneshot::Sender<Result<Value>>,
    },
    Shutdown,
}

#[derive(Clone)]
pub struct HubClient {
    tx: mpsc::Sender<HubCmd>,
    reconnected: Arc<Notify>,
}

impl HubClient {
    pub fn spawn(cfg: Config) -> Self {
        let (tx, rx) = mpsc::channel(256);
        let reconnected = Arc::new(Notify::new());
        let reconnected_clone = reconnected.clone();
        tokio::spawn(actor_loop(cfg, rx, reconnected_clone));
        Self { tx, reconnected }
    }

    pub async fn rpc(&self, tool: &'static str, arguments: Value) -> Result<Value> {
        let (responder, rx) = oneshot::channel();
        self.tx.send(HubCmd::Rpc { tool, arguments, responder })
            .await.map_err(|_| Error::Internal("hub actor closed".into()))?;
        rx.await.map_err(|_| Error::Internal("responder dropped".into()))?
    }

    pub async fn shutdown(&self) {
        let _ = self.tx.send(HubCmd::Shutdown).await;
    }

    pub fn on_reconnect(&self) -> Arc<Notify> { self.reconnected.clone() }
}

async fn actor_loop(
    cfg: Config,
    mut rx: mpsc::Receiver<HubCmd>,
    reconnected: Arc<Notify>,
) {
    let mut stream: Option<BufReader<TcpStream>> = None;
    let mut next_id: u64 = 0;
    let mut pending: HashMap<u64, oneshot::Sender<Result<Value>>> = HashMap::new();

    // 초기 연결 시도
    stream = try_connect(&cfg).await.ok().map(BufReader::new);

    let mut health_tick = tokio::time::interval(Duration::from_millis(HEALTH_PING_INTERVAL_MS));
    health_tick.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);

    loop {
        // read buffer for incoming Hub responses
        let mut line = String::new();

        tokio::select! {
            cmd = rx.recv() => {
                match cmd {
                    None | Some(HubCmd::Shutdown) => {
                        for (_, r) in pending.drain() { let _ = r.send(Err(Error::Shutdown)); }
                        return;
                    }
                    Some(HubCmd::Rpc { tool, arguments, responder }) => {
                        let Some(buf) = stream.as_mut() else {
                            let _ = responder.send(Err(Error::HubOffline));
                            // background reconnect
                            stream = try_connect(&cfg).await.ok().map(BufReader::new);
                            if stream.is_some() { reconnected.notify_waiters(); }
                            continue;
                        };
                        next_id += 1;
                        let req = json!({
                            "jsonrpc": "2.0",
                            "id": next_id,
                            "method": "tools/call",
                            "params": { "name": tool, "arguments": arguments }
                        });
                        let mut line_bytes = serde_json::to_vec(&req).unwrap();
                        line_bytes.push(b'\n');
                        if let Err(e) = buf.get_mut().write_all(&line_bytes).await {
                            warn!(error=%e, "hub write failed — reconnecting");
                            let _ = responder.send(Err(Error::HubOffline));
                            stream = None;
                            continue;
                        }
                        pending.insert(next_id, responder);
                    }
                }
            }

            res = async {
                if let Some(buf) = stream.as_mut() {
                    buf.read_line(&mut line).await
                } else {
                    // no stream: park
                    std::future::pending::<std::io::Result<usize>>().await
                }
            } => {
                match res {
                    Ok(0) => {
                        warn!("hub closed connection");
                        stream = None;
                        for (_, r) in pending.drain() { let _ = r.send(Err(Error::HubOffline)); }
                    }
                    Ok(_) => {
                        match serde_json::from_str::<Value>(line.trim()) {
                            Ok(resp) => {
                                let id = resp.get("id").and_then(|v| v.as_u64()).unwrap_or(0);
                                if let Some(responder) = pending.remove(&id) {
                                    if let Some(err) = resp.get("error") {
                                        let _ = responder.send(Err(Error::HubRpc(err.to_string())));
                                    } else {
                                        let result = resp.get("result").cloned().unwrap_or(json!({}));
                                        let _ = responder.send(Ok(parse_mcp_content(&result)));
                                    }
                                }
                            }
                            Err(e) => warn!(error=%e, "hub response parse fail"),
                        }
                    }
                    Err(e) => {
                        warn!(error=%e, "hub read error");
                        stream = None;
                    }
                }
            }

            _ = health_tick.tick() => {
                if stream.is_none() {
                    debug!("health tick: reconnecting");
                    if let Ok(s) = try_connect(&cfg).await {
                        stream = Some(BufReader::new(s));
                        reconnected.notify_waiters();
                        info!("reconnected to hub");
                    }
                }
                // else: next Rpc will naturally exercise the connection
            }
        }
    }
}

async fn try_connect(cfg: &Config) -> std::io::Result<TcpStream> {
    let mut delay = Duration::from_millis(RECONNECT_BASE_DELAY_MS);
    loop {
        match TcpStream::connect(cfg.hub_addr()).await {
            Ok(mut s) => {
                // initialize handshake
                let init = json!({"jsonrpc":"2.0","id":0,"method":"initialize","params":{}});
                let mut bytes = serde_json::to_vec(&init).unwrap();
                bytes.push(b'\n');
                s.write_all(&bytes).await?;
                // read one line (response)
                let mut buf = BufReader::new(&mut s);
                let mut line = String::new();
                buf.read_line(&mut line).await?;
                return Ok(s);
            }
            Err(e) => {
                warn!(error=%e, delay_ms=delay.as_millis() as u64, "hub connect failed");
                sleep(delay).await;
                delay = std::cmp::min(delay * 2, Duration::from_millis(RECONNECT_MAX_DELAY_MS));
            }
        }
    }
}

fn parse_mcp_content(result: &Value) -> Value {
    // Hub 응답의 content[0].text (JSON string) → parsed Value
    if let Some(sc) = result.get("structuredContent") { return sc.clone(); }
    if let Some(arr) = result.get("content").and_then(|v| v.as_array()) {
        for item in arr {
            if item.get("type").and_then(|v| v.as_str()) == Some("text") {
                if let Some(text) = item.get("text").and_then(|v| v.as_str()) {
                    if let Ok(v) = serde_json::from_str::<Value>(text) {
                        return v;
                    }
                }
            }
        }
    }
    result.clone()
}
```

### 3.6 `pool.rs`

```rust
use crate::{config::*, error::*, wire::OutMessage};
use dashmap::DashMap;
use std::collections::{HashSet, VecDeque};
use std::sync::Arc;

pub struct AgentState {
    pub agent_id: String,
    pub rooms: Vec<String>,
    pub seen_ids: HashSet<String>,
    pub offline_buffer: VecDeque<OutMessage>,
}

impl AgentState {
    pub fn new(agent_id: String, room: String) -> Self {
        Self {
            agent_id,
            rooms: vec![room],
            seen_ids: HashSet::new(),
            offline_buffer: VecDeque::new(),
        }
    }
}

#[derive(Clone, Default)]
pub struct AgentPool {
    agents: Arc<DashMap<String, AgentState>>,
}

impl AgentPool {
    pub fn new() -> Self { Self::default() }

    pub fn insert(&self, agent_id: &str, room: &str) {
        self.agents.insert(agent_id.to_string(),
            AgentState::new(agent_id.to_string(), room.to_string()));
    }

    pub fn remove(&self, agent_id: &str) -> Option<AgentState> {
        self.agents.remove(agent_id).map(|(_, v)| v)
    }

    pub fn join(&self, agent_id: &str, room: &str) -> Result<()> {
        let mut e = self.agents.get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        if !e.rooms.contains(&room.to_string()) { e.rooms.push(room.into()); }
        Ok(())
    }

    pub fn leave(&self, agent_id: &str, room: &str) -> Result<()> {
        let mut e = self.agents.get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        e.rooms.retain(|r| r != room);
        Ok(())
    }

    pub fn rooms(&self, agent_id: Option<&str>) -> serde_json::Value {
        match agent_id {
            Some(id) => self.agents.get(id)
                .map(|s| serde_json::json!(s.rooms))
                .unwrap_or(serde_json::json!([])),
            None => {
                let mut map = serde_json::Map::new();
                for e in self.agents.iter() {
                    map.insert(e.key().clone(), serde_json::json!(e.rooms));
                }
                serde_json::Value::Object(map)
            }
        }
    }

    pub fn agent_ids(&self) -> Vec<String> {
        self.agents.iter().map(|e| e.key().clone()).collect()
    }

    pub fn buffered_count(&self) -> usize {
        self.agents.iter().map(|e| e.offline_buffer.len()).sum()
    }

    pub fn rooms_map(&self) -> serde_json::Value {
        let mut out: std::collections::BTreeMap<String, Vec<String>> = Default::default();
        for e in self.agents.iter() {
            for r in &e.rooms {
                out.entry(r.clone()).or_default().push(e.key().clone());
            }
        }
        serde_json::to_value(out).unwrap_or(serde_json::json!({}))
    }

    pub fn apply_inbound<F: FnOnce(&mut AgentState) -> R, R>(&self, agent_id: &str, f: F) -> Result<R> {
        let mut e = self.agents.get_mut(agent_id)
            .ok_or_else(|| Error::NotRegistered(agent_id.into()))?;
        Ok(f(&mut *e))
    }
}
```

### 3.7 `router.rs`

```rust
use crate::{config::*, error::*, hub_client::HubClient, hmac::build_sig, pool::AgentPool, wire::*};
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Router {
    pub pool: AgentPool,
    pub hub: HubClient,
    pub shared_secret: Vec<u8>,
}

impl Router {
    pub async fn register(&self, agent: &str, room: Option<&str>) -> Result<Value> {
        let room = room.unwrap_or("seaai-general");
        let token = crate::hmac::build_token(&self.shared_secret, agent);
        self.hub.rpc("seaai_register_agent",
            json!({"agent_id": agent, "token": token})).await?;
        self.hub.rpc("seaai_join_room",
            json!({"agent_id": agent, "room_id": room})).await?;
        self.pool.insert(agent, room);
        Ok(json!({"ok": true, "agent": agent}))
    }

    pub async fn unregister(&self, agent: &str) -> Result<Value> {
        let state = self.pool.remove(agent);
        if let Some(s) = state {
            for r in &s.rooms {
                let _ = self.hub.rpc("seaai_leave_room",
                    json!({"agent_id": agent, "room_id": r})).await;
            }
        }
        Ok(json!({"ok": true}))
    }

    pub async fn join(&self, agent: &str, room: &str) -> Result<Value> {
        self.hub.rpc("seaai_join_room",
            json!({"agent_id": agent, "room_id": room})).await?;
        self.pool.join(agent, room)?;
        Ok(json!({"ok": true}))
    }

    pub async fn leave(&self, agent: &str, room: &str) -> Result<Value> {
        self.hub.rpc("seaai_leave_room",
            json!({"agent_id": agent, "room_id": room})).await?;
        self.pool.leave(agent, room)?;
        Ok(json!({"ok": true}))
    }

    pub fn rooms(&self, agent: Option<&str>) -> Value {
        json!({"rooms": self.pool.rooms(agent)})
    }

    pub async fn poll(&self, agent: &str, room: Option<&str>) -> Result<Value> {
        // 1) drain offline buffer
        let mut out: Vec<OutMessage> = self.pool.apply_inbound(agent, |st| {
            st.offline_buffer.drain(..).collect()
        })?;

        // 2) Hub RPC (실패 시 buffer만)
        let raw = match self.hub.rpc("seaai_get_agent_messages",
                                      json!({"agent_id": agent})).await {
            Ok(v) => v,
            Err(_) => return Ok(serde_json::to_value(out).unwrap()),
        };
        let msgs = raw.get("messages").and_then(|v| v.as_array()).cloned().unwrap_or_default();

        // 3) dedup + filter + project (state mutation)
        self.pool.apply_inbound(agent, |st| {
            for m in msgs {
                let id = m.get("id").and_then(|v| v.as_str()).unwrap_or("");
                if !id.is_empty() && st.seen_ids.contains(id) { continue; }
                if !id.is_empty() { st.seen_ids.insert(id.to_string()); }
                if let Some(r) = room {
                    if m.get("room_id").and_then(|v| v.as_str()) != Some(r) { continue; }
                }
                out.push(OutMessage {
                    from: m.get("from").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    body: m.get("body").and_then(|v| v.as_str()).unwrap_or("").to_string(),
                    ts:   m.get("ts").and_then(|v| v.as_f64()).unwrap_or(0.0),
                });
            }
            // 4) dedup cap
            if st.seen_ids.len() > DEDUP_CAP { st.seen_ids.clear(); }
        })?;

        Ok(serde_json::to_value(out).unwrap())
    }

    pub async fn send(&self, agent: &str, body: &str, to: &str,
                       room: Option<&str>, intent: Option<&str>) -> Result<Value> {
        // 기본 room: state.rooms[0] or "seaai-general"
        let room = match room {
            Some(r) => r.to_string(),
            None => self.pool.apply_inbound(agent, |st| {
                st.rooms.first().cloned().unwrap_or_else(|| "seaai-general".into())
            }).unwrap_or_else(|_| "seaai-general".into()),
        };

        let ts = SystemTime::now().duration_since(UNIX_EPOCH)
            .map(|d| (d.as_micros() as f64) / 1_000_000.0)
            .unwrap_or(0.0);
        // ts를 소수점 6자리로 round
        let ts = (ts * 1_000_000.0).round() / 1_000_000.0;

        let sig = build_sig(&self.shared_secret, body, ts);
        let to_val = if to == "*" { json!("*") } else { json!([to]) };
        let intent = intent.unwrap_or("chat");

        self.hub.rpc("seaai_send_message", json!({
            "from": agent,
            "to": to_val,
            "room_id": room,
            "pg_payload": {"intent": intent, "body": body, "ts": ts},
            "sig": sig,
        })).await?;

        Ok(json!({"ok": true}))
    }

    pub fn status(&self, hub_connected: bool, uptime: u64) -> Value {
        json!({
            "hub": hub_connected,
            "uptime": uptime,
            "agents": self.pool.agent_ids(),
            "rooms": self.pool.rooms_map(),
            "buffered": self.pool.buffered_count(),
        })
    }
}
```

### 3.8 `server.rs`

```rust
use crate::{config::*, error::*, router::Router, wire::*};
use axum::{
    extract::State, http::StatusCode, response::IntoResponse, routing::{get, post}, Json, Router as AxumRouter,
};
use serde_json::{json, Value};
use std::sync::Arc;
use std::time::Instant;
use tracing::{info, warn};

pub struct BridgeState {
    pub router: Router,
    pub started: Instant,
    pub hub_connected: Arc<std::sync::atomic::AtomicBool>,
}

pub fn app(state: Arc<BridgeState>) -> AxumRouter {
    AxumRouter::new()
        .route("/mcp", post(mcp_post))
        .route("/health", get(health_get))
        .with_state(state)
}

async fn health_get(State(s): State<Arc<BridgeState>>) -> impl IntoResponse {
    let hub = s.hub_connected.load(std::sync::atomic::Ordering::Relaxed);
    let out = json!({
        "status": if hub { "ok" } else { "degraded" },
        "hub": hub,
        "uptime": s.started.elapsed().as_secs(),
        "agents": s.router.pool.agent_ids(),
        "rooms": s.router.pool.rooms_map(),
        "buffered": s.router.pool.buffered_count(),
    });
    (StatusCode::OK, Json(out))
}

async fn mcp_post(
    State(s): State<Arc<BridgeState>>,
    Json(req): Json<Value>,
) -> impl IntoResponse {
    let id = req.get("id").cloned().unwrap_or(Value::Null);
    let method = req.get("method").and_then(|v| v.as_str()).unwrap_or("");
    let params = req.get("params").cloned().unwrap_or(json!({}));

    let result: Result<Value> = match method {
        "initialize" => Ok(json!({
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": false}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
        })),
        "tools/list" => Ok(json!({"tools": tool_schemas()})),
        "tools/call" => {
            match serde_json::from_value::<Tool>(params) {
                Ok(tool) => dispatch(&s, tool).await.map(|output| json!({
                    "content": [{"type":"text","text": output.to_string()}],
                    "isError": false,
                })),
                Err(e) => Err(Error::InvalidArgs(e.to_string())),
            }
        }
        m if m.starts_with("notifications/") => Ok(json!({})),
        _ => Err(Error::Protocol(format!("unknown method: {}", method))),
    };

    match result {
        Ok(r) => Json(json!({"jsonrpc":"2.0","id": id, "result": r})).into_response(),
        Err(e) => {
            warn!(error=%e, "mcp error");
            Json(json!({
                "jsonrpc":"2.0","id": id,
                "error": {"code": -32000, "message": e.to_string()}
            })).into_response()
        }
    }
}

async fn dispatch(s: &BridgeState, tool: Tool) -> Result<Value> {
    match tool {
        Tool::Register { agent, room } => s.router.register(&agent, room.as_deref()).await,
        Tool::Unregister { agent } => s.router.unregister(&agent).await,
        Tool::Join { agent, room } => s.router.join(&agent, &room).await,
        Tool::Leave { agent, room } => s.router.leave(&agent, &room).await,
        Tool::Rooms { agent } => Ok(s.router.rooms(agent.as_deref())),
        Tool::Poll { agent, room } => s.router.poll(&agent, room.as_deref()).await,
        Tool::Send { agent, body, to, room, intent } =>
            s.router.send(&agent, &body, &to, room.as_deref(), intent.as_deref()).await,
        Tool::Status {} => {
            let hub = s.hub_connected.load(std::sync::atomic::Ordering::Relaxed);
            Ok(s.router.status(hub, s.started.elapsed().as_secs()))
        }
        Tool::Sleep { seconds } => {
            tokio::time::sleep(std::time::Duration::from_secs_f64(seconds)).await;
            Ok(json!({"ok": true, "slept": seconds}))
        }
    }
}

fn tool_schemas() -> Value {
    // 9 tool schema — Python TOOLS 배열과 동일 구조
    json!([
        {"name":"register","description":"Register agent + join room",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"},"room":{"type":"string"}},"required":["agent"]}},
        {"name":"unregister","description":"Remove agent",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"}},"required":["agent"]}},
        {"name":"join","description":"Join room",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"},"room":{"type":"string"}},"required":["agent","room"]}},
        {"name":"leave","description":"Leave room",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"},"room":{"type":"string"}},"required":["agent","room"]}},
        {"name":"rooms","description":"List rooms",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"}}}},
        {"name":"poll","description":"Get new messages",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"},"room":{"type":"string"}},"required":["agent"]}},
        {"name":"send","description":"Send message",
         "inputSchema":{"type":"object","properties":{"agent":{"type":"string"},"body":{"type":"string"},"to":{"type":"string"},"room":{"type":"string"},"intent":{"type":"string"}},"required":["agent","body"]}},
        {"name":"status","description":"Bridge status","inputSchema":{"type":"object","properties":{}}},
        {"name":"sleep","description":"Wait seconds",
         "inputSchema":{"type":"object","properties":{"seconds":{"type":"number"}},"required":["seconds"]}}
    ])
}
```

### 3.9 `main.rs`

```rust
use clap::Parser;
use std::sync::{atomic::AtomicBool, Arc};
use std::time::Instant;
use tracing::{info, Level};
use tracing_subscriber::EnvFilter;

mod config;
mod error;
mod wire;
mod hmac;
mod hub_client;
mod pool;
mod router;
mod server;

use config::Config;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cfg = Config::parse();

    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| EnvFilter::new(&cfg.log_level)))
        .init();

    info!(version=%config::SERVER_VERSION, port=cfg.port, "mme (rust) starting");

    let hub = hub_client::HubClient::spawn(cfg.clone());
    let pool = pool::AgentPool::new();
    let router = router::Router {
        pool,
        hub: hub.clone(),
        shared_secret: cfg.shared_secret.as_bytes().to_vec(),
    };

    let hub_connected = Arc::new(AtomicBool::new(false));
    // 초기 연결 감지는 actor 첫 reconnect notify 또는 healthcheck로 갱신
    // 여기서는 단순화: actor가 성공 시 notify → task가 플래그 set
    {
        let notify = hub.on_reconnect();
        let flag = hub_connected.clone();
        tokio::spawn(async move {
            loop {
                notify.notified().await;
                flag.store(true, std::sync::atomic::Ordering::Relaxed);
            }
        });
    }

    let state = Arc::new(server::BridgeState {
        router,
        started: Instant::now(),
        hub_connected,
    });

    let app = server::app(state.clone());
    let listener = tokio::net::TcpListener::bind(cfg.bind_addr()).await?;
    info!(addr=%cfg.bind_addr(), "listening");

    let shutdown = async {
        tokio::signal::ctrl_c().await.ok();
        info!("shutdown signal received");
    };

    axum::serve(listener, app).with_graceful_shutdown(shutdown).await?;

    info!("bye");
    Ok(())
}
```

---

## 4. Test Plan

### 4.1 Unit (`cargo test`)

```text
unit_tests
  hmac::golden_sig_hello        # body "hello", ts 1712847600.123456
  hmac::golden_sig_korean       # body "안녕", ts 1712847600.5
  hmac::golden_sig_edge_zero    # ts 0.0
  wire::tool_deserialize        # 9 variant 각각 JSON → Tool 성공
  wire::tool_deserialize_bad    # unknown name → Err
  pool::insert_remove           # agent 생성 및 제거
  pool::join_leave              # rooms 관리
  pool::concurrent_mutation     # dashmap 동시 접근
```

### 4.2 Integration (`tests/integration.rs`)

```text
integration
  bootstrap_no_hub         # Hub 없어도 서버 기동, /health degraded
  register_status_unregister  # 기본 라이프사이클
  tool_list_schema         # 9 tool 스키마 Python과 동일
  invalid_args             # 잘못된 params → error 응답
```

### 4.3 Parity Fixtures

```text
fixtures/hmac_vectors.json — Python이 생성
[
  {"body":"hello","ts":1712847600.123456,"sig":"<hex>"},
  {"body":"안녕","ts":1712847600.5,"sig":"<hex>"},
  {"body":"","ts":0.0,"sig":"<hex>"},
  {"body":"A".repeat(1024),"ts":9999999999.999,"sig":"<hex>"}
]
```

생성 스크립트: `fixtures/gen_hmac.py` — Python의 build_sig로 10개 벡터 생성.

---

## 5. Build/Run/Validate

```bash
# 빌드
cd D:/SeAAI/SeAAIHub/tools/mme/rust
cargo build

# 테스트
cargo test --all

# 실행 (shadow 포트)
MME_PORT=9903 cargo run --release

# parity probe
curl http://127.0.0.1:9902/mcp -X POST -d '{...}'   # Python
curl http://127.0.0.1:9903/mcp -X POST -d '{...}'   # Rust
diff <(...) <(...)
```

---

## 6. Acceptance (Rust-specific)

```text
acceptance
  - [ ] cargo build 성공
  - [ ] cargo test --all 통과
  - [ ] cargo clippy -- -D warnings 통과
  - [ ] HMAC golden 10 vector 전부 Python과 일치
  - [ ] register → send → poll → unregister 라이프사이클 성공 (Hub 연결 상태)
  - [ ] /health 스키마 Python 동일
  - [ ] Hub offline 상태에서도 기동 (degraded 반환)
  - [ ] Ctrl+C 에 5초 내 graceful shutdown
```

---

## 7. Open Items

```text
open
  - Hub 응답 id 매칭 — Hub가 초기 initialize 후 tool_call 응답에 id를 반영하는지 실제 확인 필요
  - actor_loop의 read_line이 None stream일 때 park — tokio::select의 분기 조건 점검
  - hub_connected 플래그 — actor 내부에서 상태 변화를 watch로 외부 노출하는 게 더 자연스러움 (v1.1에서 개선)
  - tokio-util CancellationToken 도입 여부 (현재 Shutdown 명령만으로 처리)
```

*구체 Rust 설계 완료. 다음: WORKPLAN 생성 + cargo init + 실 구현.*
