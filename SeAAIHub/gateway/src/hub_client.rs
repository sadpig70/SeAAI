use crate::{config::*, error::*};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::TcpStream,
    sync::{mpsc, oneshot, Notify},
    time::{sleep, Duration},
};
use tracing::{debug, info, warn};

pub enum HubCmd {
    Rpc {
        tool: &'static str,
        arguments: Value,
        responder: oneshot::Sender<Result<Value>>,
    },
    Shutdown,
}

#[derive(Clone)]
pub struct HubClient {
    tx: mpsc::Sender<HubCmd>,
    connected: Arc<std::sync::atomic::AtomicBool>,
    #[allow(dead_code)]
    reconnected: Arc<Notify>,
}

impl HubClient {
    pub fn spawn(cfg: Config) -> Self {
        let (tx, rx) = mpsc::channel(256);
        let connected = Arc::new(std::sync::atomic::AtomicBool::new(false));
        let reconnected = Arc::new(Notify::new());
        tokio::spawn(actor_loop(cfg, rx, connected.clone(), reconnected.clone()));
        Self {
            tx,
            connected,
            reconnected,
        }
    }

    pub async fn rpc(&self, tool: &'static str, arguments: Value) -> Result<Value> {
        let (responder, rx) = oneshot::channel();
        self.tx
            .send(HubCmd::Rpc {
                tool,
                arguments,
                responder,
            })
            .await
            .map_err(|_| Error::Internal("hub actor closed".into()))?;
        rx.await
            .map_err(|_| Error::Internal("responder dropped".into()))?
    }

    pub async fn shutdown(&self) {
        let _ = self.tx.send(HubCmd::Shutdown).await;
    }

    pub fn connected(&self) -> bool {
        self.connected.load(std::sync::atomic::Ordering::Relaxed)
    }

    #[allow(dead_code)]
    pub fn on_reconnect(&self) -> Arc<Notify> {
        self.reconnected.clone()
    }
}

async fn actor_loop(
    cfg: Config,
    mut rx: mpsc::Receiver<HubCmd>,
    connected: Arc<std::sync::atomic::AtomicBool>,
    reconnected: Arc<Notify>,
) {
    // Two-task split: 현재는 단일 select 루프로 유지. reader를 별도 spawn하는 대안은 v1.1.
    let mut stream: Option<BufReader<TcpStream>> = None;
    let mut next_id: u64 = 0;
    let mut pending: HashMap<u64, oneshot::Sender<Result<Value>>> = HashMap::new();

    // 초기 연결 시도 (실패해도 루프 진입)
    if let Ok(s) = initial_connect(&cfg).await {
        stream = Some(BufReader::new(s));
        connected.store(true, std::sync::atomic::Ordering::Relaxed);
        reconnected.notify_waiters();
        info!("hub connected on startup");
    } else {
        warn!("hub unavailable on startup — will retry");
    }

    let mut health_tick =
        tokio::time::interval(Duration::from_millis(HEALTH_PING_INTERVAL_MS));
    health_tick.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);

    loop {
        let mut line = String::new();

        tokio::select! {
            // ── Command from handlers ──
            cmd = rx.recv() => {
                match cmd {
                    None | Some(HubCmd::Shutdown) => {
                        for (_, r) in pending.drain() {
                            let _ = r.send(Err(Error::Shutdown));
                        }
                        info!("hub actor shutdown");
                        return;
                    }
                    Some(HubCmd::Rpc { tool, arguments, responder }) => {
                        let Some(buf) = stream.as_mut() else {
                            let _ = responder.send(Err(Error::HubOffline));
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
                            warn!(error=%e, "hub write failed");
                            let _ = responder.send(Err(Error::HubOffline));
                            stream = None;
                            connected.store(false, std::sync::atomic::Ordering::Relaxed);
                            continue;
                        }
                        pending.insert(next_id, responder);
                    }
                }
            }

            // ── Hub → response line ──
            res = async {
                if let Some(buf) = stream.as_mut() {
                    buf.read_line(&mut line).await.map(|n| (n, std::mem::take(&mut line)))
                } else {
                    std::future::pending::<std::io::Result<(usize, String)>>().await
                }
            } => {
                match res {
                    Ok((0, _)) => {
                        warn!("hub closed connection");
                        stream = None;
                        connected.store(false, std::sync::atomic::Ordering::Relaxed);
                        for (_, r) in pending.drain() {
                            let _ = r.send(Err(Error::HubOffline));
                        }
                    }
                    Ok((_, text)) => {
                        match serde_json::from_str::<Value>(text.trim()) {
                            Ok(resp) => {
                                let id = resp.get("id").and_then(|v| v.as_u64()).unwrap_or(0);
                                if let Some(responder) = pending.remove(&id) {
                                    if let Some(err) = resp.get("error") {
                                        let _ = responder.send(Err(Error::HubRpc(err.to_string())));
                                    } else {
                                        let result = resp.get("result").cloned().unwrap_or(json!({}));
                                        let _ = responder.send(Ok(parse_mcp_content(&result)));
                                    }
                                } else {
                                    debug!(id=id, "unmatched hub response (init ack?)");
                                }
                            }
                            Err(e) => warn!(error=%e, raw=%text, "hub response parse fail"),
                        }
                    }
                    Err(e) => {
                        warn!(error=%e, "hub read error");
                        stream = None;
                        connected.store(false, std::sync::atomic::Ordering::Relaxed);
                    }
                }
            }

            // ── Periodic reconnect / health ──
            _ = health_tick.tick() => {
                if stream.is_none() {
                    debug!("health tick: attempting reconnect");
                    match initial_connect(&cfg).await {
                        Ok(s) => {
                            stream = Some(BufReader::new(s));
                            connected.store(true, std::sync::atomic::Ordering::Relaxed);
                            reconnected.notify_waiters();
                            info!("hub reconnected");
                        }
                        Err(e) => warn!(error=%e, "reconnect failed"),
                    }
                }
            }
        }
    }
}

async fn initial_connect(cfg: &Config) -> std::io::Result<TcpStream> {
    // Single attempt (non-blocking). Retries handled by health_tick.
    let mut stream = TcpStream::connect(cfg.hub_addr()).await?;
    // initialize handshake
    let init = json!({"jsonrpc":"2.0","id":0,"method":"initialize","params":{}});
    let mut bytes = serde_json::to_vec(&init).unwrap();
    bytes.push(b'\n');
    stream.write_all(&bytes).await?;
    // Read one response line so the initialize ack doesn't pollute later reads.
    let mut buf = BufReader::new(&mut stream);
    let mut line = String::new();
    let _ = tokio::time::timeout(Duration::from_secs(5), buf.read_line(&mut line)).await;
    Ok(stream)
}

/// Hub 응답의 content[0].text (JSON string) → parsed Value.
/// Python _parse_content와 동일.
fn parse_mcp_content(result: &Value) -> Value {
    if let Some(sc) = result.get("structuredContent") {
        return sc.clone();
    }
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

// Silence unused in release paths
#[allow(dead_code)]
fn _touch(_: &Arc<Notify>) {}

// Gracefully retry backoff (used only for diagnostics)
#[allow(dead_code)]
async fn _retry_demo() {
    let mut d = Duration::from_millis(RECONNECT_BASE_DELAY_MS);
    for _ in 0..5 {
        sleep(d).await;
        d = std::cmp::min(d * 2, Duration::from_millis(RECONNECT_MAX_DELAY_MS));
    }
}
