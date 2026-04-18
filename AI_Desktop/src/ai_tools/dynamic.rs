use crate::core::{PermissionSet, Tool, ToolContext, ToolResult};
use anyhow::{anyhow, Context};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::path::PathBuf;
use tokio::process::Command;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DynamicToolConfig {
    pub name: String,
    pub description: String,
    pub script_path: PathBuf,
    pub interpreter: String,
    pub schema: Value,
    #[serde(default)]
    pub required_permissions: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct ScriptTool {
    config: DynamicToolConfig,
    base_path: PathBuf,
    permissions: PermissionSet,
}

impl ScriptTool {
    pub fn new(config: DynamicToolConfig, base_path: PathBuf) -> Self {
        let permissions = PermissionSet::from_labels(&config.required_permissions);
        Self {
            config,
            base_path,
            permissions,
        }
    }

    fn validate_interpreter(&self) -> anyhow::Result<()> {
        let normalized = self.config.interpreter.trim().to_ascii_lowercase();
        let allowed = ["python", "python.exe", "py", "py.exe"];
        if allowed.contains(&normalized.as_str()) {
            Ok(())
        } else {
            Err(anyhow!(
                "interpreter blocked by policy: {}",
                self.config.interpreter
            ))
        }
    }

    fn resolve_script_path(&self) -> anyhow::Result<PathBuf> {
        let candidate = self.base_path.join(&self.config.script_path);
        let canonical_base = std::fs::canonicalize(&self.base_path)
            .with_context(|| format!("failed to resolve base path: {}", self.base_path.display()))?;
        let canonical_script = std::fs::canonicalize(&candidate)
            .with_context(|| format!("failed to resolve script path: {}", candidate.display()))?;

        if !canonical_script.starts_with(&canonical_base) {
            return Err(anyhow!(
                "script path escaped tool root: {}",
                canonical_script.display()
            ));
        }

        if canonical_script.extension().and_then(|ext| ext.to_str()) != Some("py") {
            return Err(anyhow!(
                "script extension blocked by policy: {}",
                canonical_script.display()
            ));
        }

        Ok(canonical_script)
    }
}

#[async_trait]
impl Tool for ScriptTool {
    fn name(&self) -> &str {
        &self.config.name
    }

    fn description(&self) -> &str {
        &self.config.description
    }

    fn required_permissions(&self) -> PermissionSet {
        self.permissions
    }

    fn input_schema(&self) -> Value {
        self.config.schema.clone()
    }

    async fn run(&self, _ctx: &ToolContext, payload: Value) -> ToolResult {
        self.validate_interpreter()?;
        let script_full_path = self.resolve_script_path()?;

        let payload_json = serde_json::to_string(&payload)?;
        let output = Command::new(&self.config.interpreter)
            .arg(&script_full_path)
            .arg(&payload_json)
            .output()
            .await
            .context("failed to execute dynamic tool")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("tool script failed: {}", stderr.trim()));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let parsed = serde_json::from_str(&stdout)
            .map_err(|_| anyhow!("tool script returned non-json output: {}", stdout.trim()))?;
        Ok(parsed)
    }
}
