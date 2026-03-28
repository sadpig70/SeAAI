use crate::core::{Permission, Tool, ToolContext, ToolResult};
use anyhow::Result;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashSet;
use std::fs::File;
use std::path::Path;
use tokio::fs;
use tokio::io::AsyncWriteExt;
use tracing::instrument;
use walkdir::WalkDir;
use zip::ZipArchive;

/// 파일 요청 구조체
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct FileReq {
    pub path: Option<String>,
    pub dir: Option<String>,
    #[serde(default)]
    pub recursive: Option<bool>,
    #[serde(default)]
    pub watch_types: Option<Vec<String>>,
}

/// 파일매니저 툴
#[derive(Default)]
pub struct FileManagerTool;

#[async_trait]
impl Tool for FileManagerTool {
    fn name(&self) -> &'static str {
        "file_manager"
    }
    fn description(&self) -> &'static str {
        "File system operations: list dirs, read/write files, delete, zip/unzip. Use absolute paths."
    }
    fn required_permissions(&self) -> Permission {
        Permission(Permission::READ | Permission::WRITE)
    }

    // [NEW] CTO 승인된 정밀 스키마
    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "op": {
                    "type": "string",
                    "enum": ["list", "read", "write", "delete", "unzip", "watch"],
                    "description": "Operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "Target file path (required for read, write, delete, unzip)"
                },
                "dir": {
                    "type": "string",
                    "description": "Target directory path (required for list, watch. Optional for unzip dest)"
                },
                "data": {
                    "type": "string",
                    "description": "Content string to write (required for write op)"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recursive listing (for list op)"
                }
            },
            "required": ["op"]
        })
    }

    #[instrument(skip(self, payload))]
    async fn run(&self, _ctx: &ToolContext, payload: Value) -> ToolResult {
        // ... (기존 run 구현 내용 유지: list, read, write 등 로직은 그대로 사용) ...
        // 기존 코드: let op = payload.get("op")...
        // ...
        // (지면 관계상 기존 로직은 생략하지만, 반드시 기존 코드 그대로 유지해야 함)
        let op = payload.get("op").and_then(|v| v.as_str()).unwrap_or("");
        let req: FileReq = serde_json::from_value(payload.clone())?;

        match op {
            "list" => {
                let root = req.dir.clone().unwrap_or_else(|| ".".to_string());
                let result = list(req, &root).await?;
                Ok(result)
            }
            // ... (나머지 케이스 동일) ...
            "read" => {
                let path = req.path.ok_or(anyhow::anyhow!("missing path"))?; // 안전하게 unwrap 제거 권장
                let data = fs::read(&path).await?;
                // 텍스트 파일인 경우 읽기 편하게 변환 시도, 바이너리면 길이만 반환하는 로직 개선 추천
                if let Ok(s) = String::from_utf8(data.clone()) {
                    Ok(json!({ "content": s, "len": data.len() }))
                } else {
                    Ok(json!({ "len": data.len(), "binary": true }))
                }
            }
            "write" => {
                let path = req.path.ok_or(anyhow::anyhow!("missing path"))?;
                let mut file = fs::File::create(&path).await?;
                let bytes = payload
                    .get("data")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .as_bytes();
                file.write_all(bytes).await?;
                Ok(json!({"ok": true}))
            }
            "delete" => {
                let path = req.path.ok_or(anyhow::anyhow!("missing path"))?;
                if fs::metadata(&path).await?.is_dir() {
                    fs::remove_dir_all(&path).await?;
                } else {
                    fs::remove_file(&path).await?;
                }
                Ok(json!({"ok": true}))
            }
            "unzip" => {
                let path = req.path.ok_or(anyhow::anyhow!("missing path"))?;
                let dir = req.dir.unwrap_or_else(|| "./out".into());
                unzip_file(&path, &dir).await?;
                Ok(json!({"ok": true}))
            }
            "watch" => {
                let root = req.dir.clone().unwrap_or_else(|| ".".to_string());
                let value = watch(req.clone(), &root).await?;
                Ok(value)
            }
            _ => Ok(json!({"error": "unsupported op"})),
        }
    }
}

/// ── 파일 리스트 (async 재귀 → helper 분리)
async fn list(req: FileReq, root: &str) -> Result<Value> {
    let mut entries = Vec::new();
    list_inner(&req, root, &mut entries)?;
    Ok(json!({ "entries": entries }))
}

fn list_inner(req: &FileReq, root: &str, entries: &mut Vec<Value>) -> Result<()> {
    let recursive = req.recursive.unwrap_or(false);
    for entry in WalkDir::new(root).max_depth(if recursive { usize::MAX } else { 1 }) {
        let e = entry?;
        let meta = e.metadata()?;
        entries.push(json!({
            "path": e.path().display().to_string(),
            "is_dir": meta.is_dir(),
            "size": if meta.is_file() { meta.len() } else { 0 }
        }));
    }
    Ok(())
}

/// ── 파일 watch (단순 Stub, req clone)
async fn watch(req: FileReq, root: &str) -> Result<Value> {
    let watch_types: HashSet<String> = req.watch_types.unwrap_or_default().into_iter().collect();
    Ok(json!({
        "watch_root": root,
        "watch_types": watch_types
    }))
}

/// ── Zip 처리 (spawn_blocking으로 Send 문제 해결)
async fn unzip_file(zip_path: &str, out_dir: &str) -> Result<()> {
    let zip_path = zip_path.to_string();
    let out_dir = out_dir.to_string();

    tokio::task::spawn_blocking(move || -> Result<()> {
        let file = File::open(&zip_path)?;
        let mut archive = ZipArchive::new(file)?;
        for i in 0..archive.len() {
            let mut entry = archive.by_index(i)?;
            let out_path = Path::new(&out_dir).join(entry.name());
            if entry.is_dir() {
                std::fs::create_dir_all(&out_path)?;
            } else {
                if let Some(p) = out_path.parent() {
                    std::fs::create_dir_all(p)?;
                }
                let mut outfile = File::create(&out_path)?;
                std::io::copy(&mut entry, &mut outfile)?;
            }
        }
        Ok(())
    })
    .await??;

    Ok(())
}
