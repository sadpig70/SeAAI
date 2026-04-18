use crate::{config::*, error::*, router::Router, wire::*};
use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router as AxumRouter,
};
use serde_json::{json, Value};
use std::sync::Arc;
use std::time::Instant;
use tracing::warn;

pub struct BridgeState {
    pub router: Router,
    pub started: Instant,
}

pub fn app(state: Arc<BridgeState>) -> AxumRouter {
    AxumRouter::new()
        .route("/mcp", post(mcp_post))
        .route("/health", get(health_get))
        .with_state(state)
}

async fn health_get(State(s): State<Arc<BridgeState>>) -> impl IntoResponse {
    let hub = s.router.hub.connected();
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
    let method = req
        .get("method")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let params = req.get("params").cloned().unwrap_or(json!({}));

    let result: Result<Value> = match method.as_str() {
        "initialize" => Ok(json!({
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": false}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
        })),
        "tools/list" => Ok(json!({ "tools": tool_schemas() })),
        "tools/call" => match serde_json::from_value::<Tool>(params) {
            Ok(tool) => match dispatch(&s, tool).await {
                Ok(output) => Ok(json!({
                    "content": [{"type":"text","text": output.to_string()}],
                    "isError": false,
                })),
                Err(e) => {
                    // tool 실행 에러는 MCP isError:true payload로 변환
                    let payload = json!({"error": e.to_string()});
                    Ok(json!({
                        "content": [{"type":"text","text": payload.to_string()}],
                        "isError": true,
                    }))
                }
            },
            Err(e) => Err(Error::InvalidArgs(e.to_string())),
        },
        m if m.starts_with("notifications/") => Ok(json!({})),
        _ => Err(Error::Protocol(format!("unknown method: {}", method))),
    };

    if req.get("id").is_none() {
        return StatusCode::NO_CONTENT.into_response();
    }

    match result {
        Ok(r) => Json(json!({"jsonrpc":"2.0","id": id, "result": r})).into_response(),
        Err(e) => {
            warn!(error=%e, "mcp error");
            Json(json!({
                "jsonrpc":"2.0","id": id,
                "error": {"code": -32000, "message": e.to_string()}
            }))
            .into_response()
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
        Tool::Send {
            agent,
            body,
            to,
            room,
            intent,
        } => {
            s.router
                .send(&agent, &body, &to, room.as_deref(), intent.as_deref())
                .await
        }
        Tool::Status {} => {
            let hub = s.router.hub.connected();
            Ok(s.router.status(hub, s.started.elapsed().as_secs()))
        }
        Tool::Sleep { seconds } => {
            tokio::time::sleep(std::time::Duration::from_secs_f64(seconds)).await;
            Ok(json!({"ok": true, "slept": seconds}))
        }
    }
}
