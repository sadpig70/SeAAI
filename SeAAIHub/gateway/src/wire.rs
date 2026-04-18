use serde::{Deserialize, Serialize};
use serde_json::Value;

// ── Tool enum (I1 fix: exhaustive match) ──

#[derive(Debug, Deserialize)]
#[serde(tag = "name", content = "arguments", rename_all = "snake_case")]
pub enum Tool {
    Register {
        agent: String,
        #[serde(default)]
        room: Option<String>,
    },
    Unregister {
        agent: String,
    },
    Join {
        agent: String,
        room: String,
    },
    Leave {
        agent: String,
        room: String,
    },
    Rooms {
        #[serde(default)]
        agent: Option<String>,
    },
    Poll {
        agent: String,
        #[serde(default)]
        room: Option<String>,
    },
    Send {
        agent: String,
        body: String,
        #[serde(default = "default_to")]
        to: String,
        #[serde(default)]
        room: Option<String>,
        #[serde(default)]
        intent: Option<String>,
    },
    Status {},
    Sleep {
        seconds: f64,
    },
}

fn default_to() -> String {
    "*".to_string()
}

// ── Projection payload (poll 응답 per message) ──

#[derive(Debug, Clone, Serialize)]
pub struct OutMessage {
    pub from: String,
    pub body: String,
    pub ts: f64,
}

// ── MCP tool schemas (static, served via tools/list) ──

pub fn tool_schemas() -> Value {
    serde_json::json!([
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
