// src/ai_tools/dynamic.rs

use crate::core::{Permission, Tool, ToolContext, ToolResult};
use anyhow::{anyhow, Context};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::PathBuf;
use tokio::process::Command;
use tracing::{debug, error, instrument};

/// 동적 도구 정의 (JSON 메타데이터)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DynamicToolConfig {
    pub name: String,
    pub description: String,
    pub script_path: PathBuf, // 실행할 스크립트 경로 (상대 경로)
    pub schema: Value,        // Input Schema
    pub interpreter: String,  // "python", "node", "powershell" 등
}

/// 스크립트 실행 래퍼 도구
#[derive(Debug, Clone)]
pub struct ScriptTool {
    config: DynamicToolConfig,
    base_path: PathBuf,
}

impl ScriptTool {
    pub fn new(config: DynamicToolConfig, base_path: PathBuf) -> Self {
        Self { config, base_path }
    }
}

#[async_trait]
impl Tool for ScriptTool {
    fn name(&self) -> &'static str {
        // 메모리 수명 문제 회피를 위해 String을 누수(leak)시켜 static str로 변환
        // (동적 도구는 개수가 제한적이므로 MVP에서 허용)
        Box::leak(self.config.name.clone().into_boxed_str())
    }

    fn description(&self) -> &'static str {
        Box::leak(self.config.description.clone().into_boxed_str())
    }

    fn required_permissions(&self) -> Permission {
        // 동적 도구는 기본적으로 권한을 보수적으로 잡거나, Config에서 로드해야 함
        // MVP: 실행 권한 요구
        Permission(Permission::EXECUTE)
    }

    fn input_schema(&self) -> Value {
        self.config.schema.clone()
    }

    #[instrument(skip(self, _ctx))]
    async fn run(&self, _ctx: &ToolContext, payload: Value) -> ToolResult {
        let script_full_path = self.base_path.join(&self.config.script_path);

        if !script_full_path.exists() {
            return Err(anyhow!("Script file not found: {:?}", script_full_path));
        }

        // Payload를 JSON 문자열로 변환하여 인자로 전달
        let payload_json = serde_json::to_string(&payload)?;

        debug!(script=?script_full_path, "Running dynamic script");

        let output = Command::new(&self.config.interpreter)
            .arg(&script_full_path)
            .arg(&payload_json) // Argument 1: JSON Payload
            .output()
            .await
            .context("Failed to execute script process")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            error!(stderr=?stderr, "Script execution failed");
            return Err(anyhow!("Script error: {}", stderr));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);

        // 스크립트 출력은 JSON이어야 한다고 가정
        match serde_json::from_str(&stdout) {
            Ok(v) => Ok(v),
            Err(_) => {
                // JSON이 아니면 텍스트로 래핑
                Ok(serde_json::json!({ "output": stdout.trim() }))
            }
        }
    }
}
