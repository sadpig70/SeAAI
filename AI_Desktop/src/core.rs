use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value}; // json! 매크로 사용을 위해 추가
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock as TokioRwLock;
use tracing::info;

/// Permission 비트마스크
#[derive(Debug, Default, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
pub struct Permission(pub u8);

impl Permission {
    pub const READ: u8 = 0b0001;
    pub const WRITE: u8 = 0b0010;
    pub const EXECUTE: u8 = 0b0100;
    pub const ADMIN: u8 = 0b1000;

    pub fn has(&self, other: Permission) -> bool {
        (self.0 & other.0) == other.0
    }
}

/// 툴 실행 컨텍스트
#[derive(Debug, Serialize, Deserialize, Clone, Default)]
pub struct ToolContext {
    pub user: String,
    pub permissions: Permission,
}

/// 툴 결과 타입
pub type ToolResult = Result<Value>;

/// 툴 트레잇 (MCP 지원을 위해 확장)
#[async_trait::async_trait]
pub trait Tool: Send + Sync {
    fn name(&self) -> &'static str;
    fn description(&self) -> &'static str;
    fn required_permissions(&self) -> Permission;

    // [NEW] MCP를 위한 입력 스키마 정의 (기본값: 빈 객체)
    // 기존 도구들과의 호환성을 위해 default impl 제공
    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {},
            "required": []
        })
    }

    async fn run(&self, ctx: &ToolContext, payload: Value) -> ToolResult;
}

/// 툴 레지스트리
#[derive(Clone)]
pub struct ToolRegistry {
    tools: Arc<TokioRwLock<HashMap<String, Arc<dyn Tool>>>>,
}

impl ToolRegistry {
    pub fn new() -> Self {
        Self {
            tools: Arc::new(TokioRwLock::new(HashMap::new())),
        }
    }

    pub async fn register<T: Tool + 'static>(&self, tool: T) {
        let name = tool.name().to_string(); // move 전에 이름 추출
        let mut map = self.tools.write().await;
        map.insert(name.clone(), Arc::new(tool));
        info!("Registered tool: {}", name);
    }

    pub async fn get(&self, name: &str) -> Option<Arc<dyn Tool>> {
        let map = self.tools.read().await;
        map.get(name).cloned()
    }

    pub async fn list(&self) -> Vec<String> {
        let map = self.tools.read().await;
        map.keys().cloned().collect()
    }
}

/// 보안 관리자 (Stub)
#[derive(Clone, Default)]
pub struct SecurityManager;

impl SecurityManager {
    pub fn new() -> Self {
        Self
    }

    pub fn authorize(&self, required: Permission, ctx: &ToolContext) -> Result<()> {
        if ctx.permissions.has(required) {
            Ok(())
        } else {
            anyhow::bail!(
                "Permission denied: required={:?}, user={}, user_perm={:?}",
                required,
                ctx.user,
                ctx.permissions
            )
        }
    }
}
