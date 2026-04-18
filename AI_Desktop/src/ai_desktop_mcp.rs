use ai_desktop_v2::ai_tools::dynamic::{DynamicToolConfig, ScriptTool};
use ai_desktop_v2::browser::{probe_browser_doctor, BrowserControlPlane};
use ai_desktop_v2::audit::{pending_entry, summarize, AuditLogger};
use ai_desktop_v2::core::{PermissionSet, ToolContext, ToolRegistry};
use ai_desktop_v2::policy::PolicyEngine;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::env;
use serde_json::{json, Value};
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tracing_subscriber::{fmt, EnvFilter};

#[derive(Debug, Deserialize)]
struct JsonRpcRequest {
    method: String,
    params: Option<Value>,
    id: Option<Value>,
}

#[derive(Debug, Serialize)]
struct JsonRpcResponse {
    jsonrpc: String,
    id: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<JsonRpcError>,
}

#[derive(Debug, Serialize)]
struct JsonRpcError {
    code: i32,
    message: String,
}

impl JsonRpcResponse {
    fn success(id: Option<Value>, result: Value) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: Some(result),
            error: None,
        }
    }

    fn error(id: Option<Value>, code: i32, message: impl Into<String>) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: None,
            error: Some(JsonRpcError {
                code,
                message: message.into(),
            }),
        }
    }
}

fn project_root() -> PathBuf {
    std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
}

async fn load_dynamic_tools(registry: &ToolRegistry, root: &Path) -> Result<()> {
    let dyn_dir = root.join("dynamic_tools");
    let mut entries = tokio::fs::read_dir(&dyn_dir).await?;
    while let Some(entry) = entries.next_entry().await? {
        let path = entry.path();
        if path.extension().and_then(|x| x.to_str()) != Some("json") {
            continue;
        }
        let content = tokio::fs::read_to_string(&path).await?;
        let config: DynamicToolConfig = serde_json::from_str(&content)?;
        registry
            .register(ScriptTool::new(config, dyn_dir.clone()))
            .await;
    }
    Ok(())
}

fn request_context(params: &Value) -> ToolContext {
    let meta = params.get("meta").cloned().unwrap_or_else(|| json!({}));
    let labels = meta
        .get("permissions")
        .and_then(Value::as_array)
        .map(|items| {
            items
                .iter()
                .filter_map(Value::as_str)
                .map(str::to_string)
                .collect::<Vec<_>>()
        })
        .unwrap_or_default();

    ToolContext {
        actor: meta
            .get("actor")
            .and_then(Value::as_str)
            .unwrap_or("unknown")
            .to_string(),
        permissions: PermissionSet::from_labels(&labels),
        approval_token: meta
            .get("approval_token")
            .and_then(Value::as_str)
            .map(str::to_string),
    }
}

fn maybe_run_browser_state_cli(root: &Path) -> Result<bool> {
    let args = env::args().collect::<Vec<_>>();
    if args.len() < 2 || args[1] != "--browser-state" {
        return Ok(false);
    }

    let action = args.get(2).map(String::as_str).unwrap_or("");
    let member = args.get(3).map(String::as_str).unwrap_or("");
    let plane = BrowserControlPlane::new(root.to_path_buf());

    let payload = match action {
        "sessions" => serde_json::to_value(plane.list_sessions_for_member(member)?)?,
        "tabs" => serde_json::to_value(plane.list_tabs_for_member(member)?)?,
        "profiles" => serde_json::to_value(plane.list_profiles_for_member(member)?)?,
        "doctor" => serde_json::to_value(probe_browser_doctor())?,
        "snapshot" => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let value: Value = if input.trim().is_empty() {
                json!({})
            } else {
                serde_json::from_str(&input)?
            };
            let session_id = value.get("session_id").and_then(Value::as_str).map(str::to_string);
            let tab_id = value
                .get("tab_id")
                .and_then(Value::as_str)
                .unwrap_or("stateless")
                .to_string();
            let text = value.get("text").and_then(Value::as_str).unwrap_or("").to_string();
            let title = value.get("title").and_then(Value::as_str).map(str::to_string);
            let format = value
                .get("format")
                .cloned()
                .map(serde_json::from_value)
                .transpose()?
                .unwrap_or_default();
            let ref_mode = value
                .get("ref_mode")
                .cloned()
                .map(serde_json::from_value)
                .transpose()?
                .unwrap_or_default();
            serde_json::to_value(plane.make_snapshot_record(session_id, tab_id, format, ref_mode, text, title))?
        }
        "upload-plan" => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let value: Value = if input.trim().is_empty() {
                json!({})
            } else {
                serde_json::from_str(&input)?
            };
            let upload_paths = value
                .get("upload_paths")
                .and_then(Value::as_array)
                .map(|items| items.iter().filter_map(Value::as_str).map(str::to_string).collect::<Vec<_>>())
                .unwrap_or_default();
            serde_json::to_value(plane.make_upload_plan(upload_paths))?
        }
        "dialog-plan" => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let value: Value = if input.trim().is_empty() {
                json!({})
            } else {
                serde_json::from_str(&input)?
            };
            let decision = value.get("decision").and_then(Value::as_str).unwrap_or("").to_string();
            let text = value.get("text").and_then(Value::as_str).map(str::to_string);
            serde_json::to_value(plane.make_dialog_plan(decision, text))?
        }
        "act-plan" => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input)?;
            let value: Value = if input.trim().is_empty() {
                json!({})
            } else {
                serde_json::from_str(&input)?
            };
            let session_id = value.get("session_id").and_then(Value::as_str).map(str::to_string);
            let tab_id = value
                .get("tab_id")
                .and_then(Value::as_str)
                .unwrap_or("stateless")
                .to_string();
            let text = value.get("text").and_then(Value::as_str).unwrap_or("").to_string();
            let title = value.get("title").and_then(Value::as_str).map(str::to_string);
            let format = value
                .get("format")
                .cloned()
                .map(serde_json::from_value)
                .transpose()?
                .unwrap_or_default();
            let ref_mode = value
                .get("ref_mode")
                .cloned()
                .map(serde_json::from_value)
                .transpose()?
                .unwrap_or_default();
            let action = value.get("action").and_then(Value::as_str).unwrap_or("").to_string();
            let ref_id = value.get("ref").and_then(Value::as_str).map(str::to_string);
            let input_text = value.get("input_text").and_then(Value::as_str).map(str::to_string);
            let snapshot = plane.make_snapshot_record(session_id, tab_id, format, ref_mode, text, title);
            serde_json::to_value(plane.make_action_plan(&snapshot, action, ref_id, input_text))?
        }
        _ => json!({ "ok": false, "error": format!("unknown_browser_state_action:{}", action) }),
    };

    println!("{}", serde_json::to_string(&payload)?);
    Ok(true)
}

#[tokio::main]
async fn main() -> Result<()> {
    let root = project_root();
    if maybe_run_browser_state_cli(&root)? {
        return Ok(());
    }

    let env_filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    fmt().with_env_filter(env_filter).with_writer(io::stderr).json().init();

    let registry = ToolRegistry::new();
    load_dynamic_tools(&registry, &root).await?;
    let policy = PolicyEngine::new();
    let audit = AuditLogger::new(&root);

    let stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut reader = BufReader::new(stdin);
    let mut line = String::new();

    loop {
        line.clear();
        if reader.read_line(&mut line).await? == 0 {
            break;
        }
        let input = line.trim();
        if input.is_empty() {
            continue;
        }

        let response = match process_request(input, &registry, &policy, &audit).await {
            Ok(Some(response)) => response,
            Ok(None) => continue,
            Err(error) => JsonRpcResponse::error(None, -32700, error.to_string()),
        };
        let mut out = serde_json::to_string(&response)?;
        out.push('\n');
        stdout.write_all(out.as_bytes()).await?;
        stdout.flush().await?;
    }

    Ok(())
}

async fn process_request(
    raw_json: &str,
    registry: &ToolRegistry,
    policy: &PolicyEngine,
    audit: &AuditLogger,
) -> Result<Option<JsonRpcResponse>> {
    let req: JsonRpcRequest = serde_json::from_str(raw_json)?;
    let response = match req.method.as_str() {
        "initialize" => JsonRpcResponse::success(
            req.id,
            json!({
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {} },
                "serverInfo": { "name": "ai_desktop_mcp", "version": "2.0.0" }
            }),
        ),
        "tools/list" => {
            let names = registry.list().await;
            let mut tools = Vec::new();
            for name in names {
                if let Some(tool) = registry.get(&name).await {
                    tools.push(json!({
                        "name": tool.name(),
                        "description": tool.description(),
                        "inputSchema": tool.input_schema()
                    }));
                }
            }
            JsonRpcResponse::success(req.id, json!({ "tools": tools }))
        }
        "tools/call" => {
            let params = req.params.unwrap_or_else(|| json!({}));
            let name = params
                .get("name")
                .and_then(Value::as_str)
                .unwrap_or("unknown")
                .to_string();
            let args = params.get("arguments").cloned().unwrap_or_else(|| json!({}));
            let ctx = request_context(&params);
            let action = args.get("action").and_then(Value::as_str).map(str::to_string);

            let mut entry = pending_entry(ctx.actor.clone(), name.clone(), action, &args);
            let response = if let Some(tool) = registry.get(&name).await {
                match policy.authorize(&name, tool.required_permissions(), &ctx, &args) {
                    Ok(()) => match tool.run(&ctx, args.clone()).await {
                        Ok(content) => {
                            entry.status = "SUCCESS".to_string();
                            entry.output_summary = Some(summarize(&content));
                            JsonRpcResponse::success(
                                req.id,
                                json!({ "content": [{ "type": "text", "text": content.to_string() }] }),
                            )
                        }
                        Err(error) => {
                            entry.status = "FAILED".to_string();
                            entry.error = Some(error.to_string());
                            JsonRpcResponse::error(req.id, -32000, error.to_string())
                        }
                    },
                    Err(error) => {
                        entry.status = "DENIED".to_string();
                        entry.error = Some(error.to_string());
                        JsonRpcResponse::error(req.id, -32003, error.to_string())
                    }
                }
            } else {
                entry.status = "NOT_FOUND".to_string();
                entry.error = Some("tool not found".to_string());
                JsonRpcResponse::error(req.id, -32601, "tool not found")
            };
            audit.log(entry).await?;
            response
        }
        _ => JsonRpcResponse::error(req.id, -32601, "method not found"),
    };
    Ok(Some(response))
}
