// src/bin/ai_tool_cli.rs
use std::{fs, path::PathBuf};

use clap::Parser;
use serde_json::Value;

use ai_desktop_lib::ai_tools::{FileManagerTool, SystemInfoTool, WebSearchTool};
use ai_desktop_lib::core::{Tool, ToolContext};

#[derive(Parser, Debug)]
#[command(
    name = "ai_tool_cli",
    version,
    about = "Run a single AI Desktop tool with JSON payload"
)]
struct Cli {
    /// Tool name (file_manager | system_info | web_search)
    #[arg(long)]
    tool: String,

    /// JSON payload string
    #[arg(long, conflicts_with = "file")]
    json: Option<String>,

    /// JSON payload file path
    #[arg(long)]
    file: Option<PathBuf>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let args = Cli::parse();

    let payload_str = if let Some(s) = &args.json {
        s.clone()
    } else if let Some(p) = &args.file {
        fs::read_to_string(p)?
    } else {
        anyhow::bail!("Provide --json '{{...}}' or --file payload.json");
    };

    let payload: Value = serde_json::from_str(&payload_str)
        .map_err(|e| anyhow::anyhow!("Invalid JSON payload: {e}"))?;

    // 최소 컨텍스트 (필요시 core::ToolContext::new(...)로 교체)
    let ctx = ToolContext::default();

    let out = match args.tool.as_str() {
        "file_manager" => {
            let tool = FileManagerTool::default();
            tool.run(&ctx, payload).await?
        }
        "system_info" => {
            let tool = SystemInfoTool::default();
            tool.run(&ctx, payload).await?
        }
        "web_search" => {
            let tool = WebSearchTool::default();
            tool.run(&ctx, payload).await?
        }
        other => {
            serde_json::json!({ "ok": false, "error": format!("unknown tool or not implemented: {}", other) })
        }
    };

    println!("{}", serde_json::to_string_pretty(&out)?);
    Ok(())
}
