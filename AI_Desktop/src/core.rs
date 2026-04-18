use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Default)]
pub struct PermissionSet(pub u8);

impl PermissionSet {
    pub const READ: u8 = 0b0001;
    pub const WRITE: u8 = 0b0010;
    pub const EXECUTE: u8 = 0b0100;
    pub const APPROVE: u8 = 0b1000;

    pub fn from_labels(labels: &[String]) -> Self {
        let mut value = 0u8;
        for label in labels {
            match label.to_ascii_lowercase().as_str() {
                "read" => value |= Self::READ,
                "write" => value |= Self::WRITE,
                "execute" => value |= Self::EXECUTE,
                "approve" => value |= Self::APPROVE,
                _ => {}
            }
        }
        Self(value)
    }

    pub fn has_all(self, required: PermissionSet) -> bool {
        (self.0 & required.0) == required.0
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ToolContext {
    pub actor: String,
    pub permissions: PermissionSet,
    pub approval_token: Option<String>,
}

pub type ToolResult = Result<Value>;

#[async_trait::async_trait]
pub trait Tool: Send + Sync {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn required_permissions(&self) -> PermissionSet;
    fn input_schema(&self) -> Value {
        json!({"type":"object","properties":{},"required":[]})
    }
    async fn run(&self, ctx: &ToolContext, payload: Value) -> ToolResult;
}

#[derive(Clone, Default)]
pub struct ToolRegistry {
    tools: Arc<RwLock<HashMap<String, Arc<dyn Tool>>>>,
}

impl ToolRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub async fn register<T: Tool + 'static>(&self, tool: T) {
        let name = tool.name().to_string();
        self.tools.write().await.insert(name, Arc::new(tool));
    }

    pub async fn get(&self, name: &str) -> Option<Arc<dyn Tool>> {
        self.tools.read().await.get(name).cloned()
    }

    pub async fn list(&self) -> Vec<String> {
        let mut keys = self.tools.read().await.keys().cloned().collect::<Vec<_>>();
        keys.sort();
        keys
    }
}
