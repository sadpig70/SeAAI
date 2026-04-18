mod chatroom;
mod protocol;
mod transport;
mod router;

use crate::protocol::JsonRpcRequest;
use crate::protocol::JsonRpcResponse;
use crate::router::Router;
use crate::transport::TcpClientTransport;
use anyhow::Result;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::Mutex;

const DEFAULT_TCP_PORT: u16 = 9900;

#[tokio::main]
async fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();

    // Root Hub binary always serves the TCP path.
    // 인자가 없으면 정식 운영 포트(9900)로 TCP 서버를 띄운다.
    let tcp_port = args.iter().position(|a| a == "--tcp-port")
        .and_then(|i| args.get(i + 1))
        .and_then(|p| p.parse::<u16>().ok())
        .unwrap_or(DEFAULT_TCP_PORT);

    run_tcp_server(tcp_port).await
}

/// 신규 TCP 서버 모드 — 다중 클라이언트, 공유 Router
async fn run_tcp_server(port: u16) -> Result<()> {
    let listener = TcpListener::bind(format!("127.0.0.1:{}", port)).await?;
    eprintln!("[SeAAIHub] TCP server listening on 127.0.0.1:{}", port);

    let router = Arc::new(Mutex::new(Router::new()));

    loop {
        let (stream, addr) = listener.accept().await?;
        eprintln!("[SeAAIHub] Client connected: {}", addr);
        let router = Arc::clone(&router);

        tokio::spawn(async move {
            if let Err(e) = handle_tcp_client(stream, router).await {
                eprintln!("[SeAAIHub] Client {} error: {}", addr, e);
            }
            eprintln!("[SeAAIHub] Client disconnected: {}", addr);
        });
    }
}

async fn handle_tcp_client(
    stream: tokio::net::TcpStream,
    router: Arc<Mutex<Router>>,
) -> Result<()> {
    let mut transport = TcpClientTransport::new(stream);
    let mut session_agent_id: Option<String> = None;
    let mut session_token: Option<String> = None;

    loop {
        match transport.read_line().await {
            Ok(Some(line)) => {
                if line.trim().is_empty() {
                    continue;
                }
                match serde_json::from_str::<JsonRpcRequest>(&line) {
                    Ok(req) => {
                        // Track agent_id from register_agent or connect calls
                        if req.method == "tools/call" {
                            if let Some(params) = &req.params {
                                if let Some(name) = params.get("name").and_then(|n| n.as_str()) {
                                    if name == "seaai_register_agent" || name == "seaai_connect" {
                                        if let Some(args) = params.get("arguments") {
                                            if let Some(aid) = args.get("agent_id").and_then(|a| a.as_str()) {
                                                session_agent_id = Some(aid.to_string());
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        let mut router_guard = router.lock().await;
                        if let Some(response) = process_request(&mut *router_guard, req) {
                            drop(router_guard);
                            // Capture session_token from connect response
                            if let Some(result) = &response.result {
                                if let Some(content) = result.get("content").and_then(|c| c.as_array()) {
                                    for item in content {
                                        if let Some(text) = item.get("text").and_then(|t| t.as_str()) {
                                            if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(text) {
                                                if let Some(tok) = parsed.get("session_token").and_then(|t| t.as_str()) {
                                                    session_token = Some(tok.to_string());
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            if let Ok(json_res) = serde_json::to_string(&response) {
                                if let Err(e) = transport.write_response(&json_res).await {
                                    eprintln!("Failed to write TCP response: {}", e);
                                    break;
                                }
                            }
                        }
                    }
                    Err(e) => {
                        let err_res = protocol::JsonRpcResponse::error(
                            serde_json::Value::Null,
                            -32700,
                            format!("Parse error: {}", e),
                        );
                        if let Ok(json_res) = serde_json::to_string(&err_res) {
                            let _ = transport.write_response(&json_res).await;
                        }
                    }
                }
            }
            Ok(None) => break, // Client disconnected
            Err(e) => {
                eprintln!("TCP transport error: {}", e);
                break;
            }
        }
    }

    // Cleanup: remove agent from all rooms on disconnect
    if let Some(agent_id) = &session_agent_id {
        let mut router_guard = router.lock().await;
        // If connected via v2 connect, also invalidate session token
        if let Some(token) = &session_token {
            let _ = router_guard.disconnect_agent(agent_id, token);
        } else {
            router_guard.cleanup_agent(agent_id);
        }
        eprintln!("[SeAAIHub] Cleaned up agent: {}", agent_id);
    }

    Ok(())
}

fn process_request(router: &mut Router, req: JsonRpcRequest) -> Option<JsonRpcResponse> {
    let should_respond = req.id.is_some();
    let response = router.handle_request(req);
    should_respond.then_some(response)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn suppresses_notification_responses() {
        let mut router = Router::new();
        let req = JsonRpcRequest {
            jsonrpc: "2.0".to_string(),
            id: None,
            method: "notifications/initialized".to_string(),
            params: Some(json!({})),
        };

        let response = process_request(&mut router, req);
        assert!(response.is_none());
    }

    #[test]
    fn returns_response_for_regular_requests() {
        let mut router = Router::new();
        let req = JsonRpcRequest {
            jsonrpc: "2.0".to_string(),
            id: Some(json!(1)),
            method: "initialize".to_string(),
            params: Some(json!({})),
        };

        let response = process_request(&mut router, req);
        assert!(response.is_some());
    }
}
