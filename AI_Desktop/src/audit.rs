// src/audit.rs

use anyhow::Result;
use chrono::Local;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::path::PathBuf;
use tokio::fs::{self, OpenOptions};
use tokio::io::AsyncWriteExt;
use tokio::sync::mpsc;
use tracing::{error, info};

const MAX_LOG_SIZE: u64 = 10 * 1024 * 1024; // 10MB
const LOG_DIR: &str = "logs";
const LOG_FILE: &str = "audit.jsonl";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub timestamp: String,
    pub actor: String,
    pub action: String, // tool name or "TSG_BLOCK"
    pub status: String, // "SUCCESS", "FAILED", "DENIED"
    pub input_summary: Value,
    pub output_summary: Option<Value>,
    pub duration_ms: Option<u64>,
    pub error: Option<String>,
}

pub struct AuditLogger {
    tx: mpsc::Sender<AuditEntry>,
}

impl AuditLogger {
    /// 로거 초기화: 백그라운드 워커 시작
    pub fn new() -> Self {
        let (tx, mut rx) = mpsc::channel(100); // 버퍼 100개

        // 백그라운드 로깅 태스크
        tokio::spawn(async move {
            // 로그 디렉토리 생성
            if let Err(e) = fs::create_dir_all(LOG_DIR).await {
                error!("Failed to create log dir: {}", e);
                return;
            }

            let log_path = PathBuf::from(LOG_DIR).join(LOG_FILE);

            while let Some(entry) = rx.recv().await {
                if let Err(e) = write_log(&log_path, entry).await {
                    error!("Failed to write audit log: {}", e);
                }
            }
        });

        Self { tx }
    }

    /// 로그 기록 (Non-blocking)
    pub async fn log(&self, entry: AuditEntry) {
        if let Err(_) = self.tx.send(entry).await {
            error!("Audit log channel closed");
        }
    }
}

/// 실제 파일 쓰기 및 로테이션 로직
async fn write_log(path: &PathBuf, entry: AuditEntry) -> Result<()> {
    // 1. 로테이션 체크
    if let Ok(metadata) = fs::metadata(path).await {
        if metadata.len() > MAX_LOG_SIZE {
            let timestamp = Local::now().format("%Y%m%d_%H%M%S");
            let new_name = path.with_file_name(format!("{}.{}", LOG_FILE, timestamp));
            info!("🔄 Rotating log file to {:?}", new_name);
            fs::rename(path, new_name).await?;
        }
    }

    // 2. 로그 쓰기 (Append)
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .await?;

    let json_line = serde_json::to_string(&entry)?;
    file.write_all(json_line.as_bytes()).await?;
    file.write_all(b"\n").await?;

    Ok(())
}

/// 입력값 요약 (너무 긴 데이터 자르기)
pub fn summarize(val: &Value) -> Value {
    match val {
        Value::String(s) if s.len() > 200 => {
            json!(format!("{}... (truncated, len={})", &s[..50], s.len()))
        }
        Value::Object(map) => {
            let mut new_map = serde_json::Map::new();
            for (k, v) in map {
                if k == "data" || k == "content" {
                    new_map.insert(k.clone(), summarize(v)); // 재귀적 요약
                } else {
                    new_map.insert(k.clone(), v.clone());
                }
            }
            Value::Object(new_map)
        }
        _ => val.clone(),
    }
}
