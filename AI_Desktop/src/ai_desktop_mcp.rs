use anyhow::Result;
use chrono::Local;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::io;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tracing::{debug, error, info, instrument};
use tracing_subscriber::{fmt, EnvFilter};

// 라이브러리 크레이트에서 모듈 가져오기
// (Cargo.toml에서 [lib] name = "ai_desktop_lib"으로 설정되었다고 가정)
use ai_desktop_lib::ai_tools::{
    dynamic::{DynamicToolConfig, ScriptTool}, // [New]
    AutoToolGenerator,                        // [New]
    FileManagerTool,
    NetworkApiTool,
    ProcessManagerTool,
    ScreenCaptureTool,
    SystemInfoTool,
    WebSearchTool,
};
use ai_desktop_lib::audit::{summarize, AuditEntry, AuditLogger}; // [NEW]
use ai_desktop_lib::core::{Permission, ToolContext, ToolRegistry};
use ai_desktop_lib::tsg::TrustSecurityGateway;

use std::fs;
use std::path::Path;

// 도구 로딩 헬퍼 함수
async fn load_dynamic_tools(registry: &ToolRegistry) {
    let dyn_dir = Path::new("dynamic_tools");
    if !dyn_dir.exists() {
        return;
    }

    if let Ok(entries) = fs::read_dir(dyn_dir) {
        for entry in entries.filter_map(|e| e.ok()) {
            let path = entry.path();
            if path.extension().map_or(false, |ext| ext == "json") {
                // Config 파일 발견
                if let Ok(content) = fs::read_to_string(&path) {
                    if let Ok(config) = serde_json::from_str::<DynamicToolConfig>(&content) {
                        let tool_name = config.name.clone();
                        let tool = ScriptTool::new(config, dyn_dir.to_path_buf());
                        registry.register(tool).await;
                        tracing::info!("🧩 Dynamic Tool Loaded: {}", tool_name);
                    }
                }
            }
        }
    }
}

// --- 1. JSON-RPC 2.0 데이터 구조 정의 ---

#[derive(Debug, Deserialize)]
struct JsonRpcRequest {
    jsonrpc: String,
    method: String,
    params: Option<Value>,
    id: Option<Value>, // Notification일 경우 null 가능
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
    #[serde(skip_serializing_if = "Option::is_none")]
    data: Option<Value>,
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

    fn error(id: Option<Value>, code: i32, message: &str) -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
            id,
            result: None,
            error: Some(JsonRpcError {
                code,
                message: message.to_string(),
                data: None,
            }),
        }
    }
}

// --- 2. 메인 엔트리포인트 (비동기 루프) ---

#[tokio::main]
async fn main() -> Result<()> {
    // [로깅 초기화]
    // MCP 프로토콜은 stdout을 사용하므로, 시스템 로그는 반드시 stderr로 보내야 함
    let env_filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));

    fmt()
        .with_env_filter(env_filter)
        .with_writer(io::stderr)
        .json()
        .init();

    info!("🚀 AI Desktop MCP Server Starting...");

    // [NEW] Audit Logger 초기화
    let audit_logger = AuditLogger::new();
    info!("📜 Audit Logger initialized (Background Task).");

    // [보안 게이트웨이 초기화]
    let tsg = TrustSecurityGateway::new();
    info!("🛡️ Trust & Security Gateway (TSG) initialized.");

    // [도구 레지스트리 초기화 및 등록]
    let registry = ToolRegistry::new();

    // 1. OS 제어 도구 그룹
    registry.register(SystemInfoTool::default()).await;
    registry.register(ProcessManagerTool::default()).await;

    // 2. 파일 시스템 도구 그룹
    registry.register(FileManagerTool::default()).await;

    // 3. 화면 캡처 도구
    registry.register(ScreenCaptureTool::default()).await;

    // 3. 네트워크 도구 그룹
    registry.register(NetworkApiTool::default()).await;

    // 4. 웹 검색 도구 (초기화 실패 시에도 서버 다운 방지)
    match WebSearchTool::new() {
        Ok(tool) => {
            registry.register(tool).await;
            info!("✅ WebSearchTool registered.");
        }
        Err(e) => {
            error!("⚠️ Failed to init WebSearchTool: {}. Skipping.", e);
        }
    }

    // [New] Auto Generator 등록
    registry.register(AutoToolGenerator::default()).await;

    // [New] 동적 도구 로딩
    load_dynamic_tools(&registry).await;

    info!("✅ All tools registered. Ready for MCP connections via Stdio.");

    // [Stdio 비동기 통신 루프]
    let stdin = tokio::io::stdin();
    let mut stdout = tokio::io::stdout();
    let mut reader = BufReader::new(stdin);
    let mut line = String::new();

    loop {
        line.clear();
        // 비동기로 한 줄 읽기 (Non-blocking)
        let bytes_read = reader.read_line(&mut line).await?;
        if bytes_read == 0 {
            info!("🔌 Stdin closed (EOF). Shutting down.");
            break;
        }

        let input = line.trim();
        if input.is_empty() {
            continue;
        }

        debug!(input = input, "📥 Received payload");

        // 요청 처리 (Registry와 TSG 주입)
        match process_request(input, &registry, &tsg, &audit_logger).await {
            Ok(Some(response_json)) => {
                // 응답 전송 (Newline Delimited JSON)
                let mut out_str = serde_json::to_string(&response_json)?;
                out_str.push('\n');

                stdout.write_all(out_str.as_bytes()).await?;
                stdout.flush().await?; // 즉시 전송

                debug!("📤 Sent response");
            }
            Ok(None) => {
                // Notification 등 응답이 필요 없는 경우 무시
            }
            Err(e) => {
                // JSON 파싱 실패 등 심각한 에러 처리
                error!("❌ Processing Error: {}", e);
                // 연결을 끊지 않고 에러 메시지 전송 시도
                let err_resp =
                    JsonRpcResponse::error(None, -32700, "Parse error or internal failure");
                if let Ok(out_str) = serde_json::to_string(&err_resp) {
                    let _ = stdout.write_all((out_str + "\n").as_bytes()).await;
                    let _ = stdout.flush().await;
                }
            }
        }
    }

    Ok(())
}

// [Change] logger 인자 추가
#[instrument(skip(raw_json, registry, tsg, logger), fields(method))]
async fn process_request(
    raw_json: &str,
    registry: &ToolRegistry,
    tsg: &TrustSecurityGateway,
    logger: &AuditLogger, // [NEW]
) -> Result<Option<JsonRpcResponse>> {
    let start_time = Instant::now();
    let req: JsonRpcRequest = serde_json::from_str(raw_json)?;

    // 응답 생성 로직
    let response = match req.method.as_str() {
        "initialize" => {
            let result = json!({
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "ai_desktop_mcp",
                    "version": "1.0.0"
                }
            });
            Ok(Some(JsonRpcResponse::success(req.id, result)))
        }
        "tools/list" => {
            let tool_names = registry.list().await;
            let mut tools_list: Vec<Value> = Vec::new();
            for name in tool_names {
                if let Some(tool) = registry.get(&name).await {
                    tools_list.push(json!({
                        "name": tool.name(),
                        "description": tool.description(),
                        "inputSchema": tool.input_schema()
                    }));
                }
            }
            let result = json!({ "tools": tools_list });
            Ok(Some(JsonRpcResponse::success(req.id, result)))
        }

        "tools/call" => {
            let params = req.params.unwrap_or(json!({}));
            let name = params["name"].as_str().unwrap_or("unknown").to_string();
            let args = params.get("arguments").cloned().unwrap_or(json!({}));

            let mut entry = AuditEntry {
                timestamp: Local::now().to_rfc3339(),
                actor: "mcp_client".into(),
                action: name.clone(),
                status: "PENDING".into(),
                input_summary: summarize(&args),
                output_summary: None,
                duration_ms: None,
                error: None,
            };

            if let Some(tool) = registry.get(&name).await {
                // 1. TSG 검사
                if let Err(deny_msg) = tsg.authorize(&name, &args) {
                    // [Log] 차단 기록
                    entry.status = "DENIED".into();
                    entry.error = Some(deny_msg.clone());
                    entry.duration_ms = Some(start_time.elapsed().as_millis() as u64);
                    logger.log(entry).await;

                    return Ok(Some(JsonRpcResponse::error(req.id, -32003, &deny_msg)));
                }

                // 2. 도구 실행
                let ctx = ToolContext {
                    user: "mcp_user".into(),
                    permissions: Permission(Permission::ADMIN),
                };

                match tool.run(&ctx, args).await {
                    Ok(content) => {
                        let safe_content = tsg.filter_output(&content);

                        // [Log] 성공 기록
                        entry.status = "SUCCESS".into();
                        entry.output_summary = Some(summarize(&safe_content));
                        entry.duration_ms = Some(start_time.elapsed().as_millis() as u64);
                        logger.log(entry).await;

                        let result = json!({
                            "content": [{ "type": "text", "text": safe_content.to_string() }]
                        });
                        Ok(Some(JsonRpcResponse::success(req.id, result)))
                    }
                    Err(e) => {
                        // [Log] 실패 기록
                        entry.status = "FAILED".into();
                        entry.error = Some(e.to_string());
                        entry.duration_ms = Some(start_time.elapsed().as_millis() as u64);
                        logger.log(entry).await;

                        Ok(Some(JsonRpcResponse::error(req.id, -32000, &e.to_string())))
                    }
                }
            } else {
                // [Log] 없는 도구 호출
                entry.status = "NOT_FOUND".into();
                logger.log(entry).await;
                Ok(Some(JsonRpcResponse::error(
                    req.id,
                    -32601,
                    "Tool not found",
                )))
            }
        }
        _ => Ok(Some(JsonRpcResponse::error(
            req.id,
            -32601,
            "Method not found",
        ))),
    };

    response
}
