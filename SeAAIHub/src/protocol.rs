use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Serialize, Deserialize)]
pub struct JsonRpcRequest {
    pub jsonrpc: String,
    pub id: Option<Value>,
    pub method: String,
    #[serde(default)]
    pub params: Option<Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct JsonRpcResponse {
    pub jsonrpc: String,
    pub id: Value,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<JsonRpcError>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct JsonRpcError {
    pub code: i32,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,
}

#[derive(Debug, Deserialize)]
pub struct ToolCallParams {
    pub name: String,
    #[serde(default)]
    pub arguments: Value,
}

#[derive(Debug, Deserialize)]
pub struct RegisterAgentArgs {
    pub agent_id: String,
    pub token: String,
    #[serde(default)]
    pub capabilities: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct DiscoverArgs {
    pub capability: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CatchupArgs {
    pub agent_id: String,
    pub room_id: String,
    #[serde(default = "default_catchup_count")]
    pub count: usize,
}

fn default_catchup_count() -> usize { 20 }

#[derive(Debug, Deserialize)]
pub struct SubscribeArgs {
    pub agent_id: String,
    pub topic: String,
}

#[derive(Debug, Deserialize)]
pub struct RoomMutationArgs {
    pub agent_id: String,
    pub room_id: String,
}

#[derive(Debug, Deserialize)]
pub struct AgentQueryArgs {
    pub agent_id: String,
}

#[derive(Debug, Deserialize)]
pub struct RoomStateArgs {
    pub room_id: String,
}

#[derive(Debug, Deserialize)]
pub struct SendMessageArgs {
    pub id: Option<String>,
    pub from: String,
    pub room_id: String,
    pub pg_payload: PgMessageParams,
    pub sig: String,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct PgMessageParams {
    pub intent: String,
    pub body: String,
    pub ts: f64,
}

#[derive(Debug, Deserialize)]
pub struct PgPayload {
    pub id: Option<String>,
    pub from: String,
    pub room_id: String,
    pub pg_payload: PgMessageParams,
    pub sig: String,
}

#[derive(Debug, Serialize)]
pub struct ToolSpec {
    pub name: String,
    pub description: String,
    pub input_schema: Value,
}

impl JsonRpcResponse {
    pub fn success(id: Value, result: Value) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: Some(result),
            error: None,
        }
    }

    pub fn error(id: Value, code: i32, message: String) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: None,
            error: Some(JsonRpcError {
                code,
                message,
                data: None,
            }),
        }
    }
}
