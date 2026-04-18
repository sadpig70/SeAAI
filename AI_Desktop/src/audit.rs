use anyhow::Result;
use chrono::Local;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use tokio::fs::OpenOptions;
use tokio::io::AsyncWriteExt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub timestamp: String,
    pub actor: String,
    pub tool: String,
    pub action: Option<String>,
    pub status: String,
    pub input_summary: String,
    pub output_summary: Option<String>,
    pub error: Option<String>,
}

#[derive(Clone)]
pub struct AuditLogger {
    path: PathBuf,
}

impl AuditLogger {
    pub fn new(root: impl AsRef<Path>) -> Self {
        Self {
            path: root.as_ref().join("logs").join("audit.ndjson"),
        }
    }

    pub async fn log(&self, entry: AuditEntry) -> Result<()> {
        if let Some(parent) = self.path.parent() {
            tokio::fs::create_dir_all(parent).await?;
        }
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.path)
            .await?;
        let mut line = serde_json::to_vec(&entry)?;
        line.push(b'\n');
        file.write_all(&line).await?;
        Ok(())
    }
}

pub fn summarize(value: &serde_json::Value) -> String {
    let raw = value.to_string();
    if raw.len() > 240 {
        format!("{}...", &raw[..240])
    } else {
        raw
    }
}

pub fn pending_entry(actor: String, tool: String, action: Option<String>, input: &serde_json::Value) -> AuditEntry {
    AuditEntry {
        timestamp: Local::now().to_rfc3339(),
        actor,
        tool,
        action,
        status: "PENDING".to_string(),
        input_summary: summarize(input),
        output_summary: None,
        error: None,
    }
}
