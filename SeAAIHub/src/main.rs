mod chatroom;
mod protocol;
mod transport;
mod router;

use crate::protocol::JsonRpcRequest;
use crate::protocol::JsonRpcResponse;
use crate::router::Router;
use crate::transport::{StdioTransport, TcpClientTransport};
use anyhow::Result;
use std::sync::Arc;
use tokio::net::TcpListener;
use tokio::sync::Mutex;

#[tokio::main]
async fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();

    // --tcp-port <port> → TCP 서버 모드
    // 인자 없으면 → stdio 모드 (기존 호환)
    let tcp_port = args.iter().position(|a| a == "--tcp-port")
        .and_then(|i| args.get(i + 1))
        .and_then(|p| p.parse::<u16>().ok());
    let mock_mode = args.iter().any(|a| a == "--mock");

    if let Some(port) = tcp_port {
        run_tcp_server(port, mock_mode).await
    } else {
        run_stdio_server().await
    }
}

/// 기존 stdio 모드 — 하위 호환
async fn run_stdio_server() -> Result<()> {
    let mut router = Router::new();
    let mut transport = StdioTransport::new();

    loop {
        match transport.read_line().await {
            Ok(Some(line)) => {
                if line.trim().is_empty() {
                    continue;
                }
                match serde_json::from_str::<JsonRpcRequest>(&line) {
                    Ok(req) => {
                        if let Some(response) = process_request(&mut router, req) {
                            if let Ok(json_res) = serde_json::to_string(&response) {
                                if let Err(e) = transport.write_response(&json_res).await {
                                    eprintln!("Failed to write STDIO response: {}", e);
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
            Ok(None) => break,
            Err(e) => {
                eprintln!("SeAAIHub STDIO transport error: {}", e);
                break;
            }
        }
    }

    Ok(())
}

/// 신규 TCP 서버 모드 — 다중 클라이언트, 공유 Router
async fn run_tcp_server(port: u16, mock_mode: bool) -> Result<()> {
    let listener = TcpListener::bind(format!("127.0.0.1:{}", port)).await?;
    if mock_mode {
        eprintln!("[SeAAIHub] TCP server listening on 127.0.0.1:{} (MOCK MODE — 5~10s random messages)", port);
    } else {
        eprintln!("[SeAAIHub] TCP server listening on 127.0.0.1:{}", port);
    }

    let router = Arc::new(Mutex::new(if mock_mode { Router::new_mock() } else { Router::new() }));

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

    loop {
        match transport.read_line().await {
            Ok(Some(line)) => {
                if line.trim().is_empty() {
                    continue;
                }
                match serde_json::from_str::<JsonRpcRequest>(&line) {
                    Ok(req) => {
                        let mut router_guard = router.lock().await;
                        if let Some(response) = process_request(&mut *router_guard, req) {
                            drop(router_guard); // 쓰기 전에 lock 해제
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
