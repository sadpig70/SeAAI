좋아요 정욱님! **PowerShell/CLI 래퍼** 두 가지를 드립니다.

* A) PowerShell 스크립트 `ai-tool.ps1` : 바로 사용 가능
* B) 경량 CLI 바이너리 `ai_tool_cli` : 툴들을 직접 호출 (feature 안전)

---

# A) PowerShell 스크립트 — `ai-tool.ps1`

> 실행: `.\ai-tool.ps1 -Tool web_search -Json '{ "cmd":"search", "q":"windows-rs", "top":3 }'`

```powershell
param(
  [Parameter(Mandatory = $true)][string]$Tool,
  [string]$Json,
  [string]$File
)

# JSON 파일 입력 지원
if (-not $Json -and $File) {
  if (-not (Test-Path $File)) { throw "Payload file not found: $File" }
  $Json = Get-Content -Raw -Path $File
}

if (-not $Json) { throw "Provide -Json '{...}' or -File payload.json" }

# 바이너리 경로 (ai_tool_cli 빌드 후 같은 폴더에 둔다고 가정)
$exe = Join-Path $PSScriptRoot "ai_tool_cli.exe"
if (-not (Test-Path $exe)) { throw "Not found: $exe. Build the CLI first." }

# 실행
$raw = & $exe --tool $Tool --json $Json 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Error $raw
  exit $LASTEXITCODE
}

# pretty-print
try {
  $obj = $raw | ConvertFrom-Json
  $obj | ConvertTo-Json -Depth 50
} catch {
  # 비 JSON 출력도 그대로 노출
  $raw
}
```

## 사용 예시

```powershell
# WebSearchTool
.\ai-tool.ps1 -Tool web_search -Json '{ "cmd":"search", "q":"windows-rs Rust", "top": 3 }'

# ClipboardTool
.\ai-tool.ps1 -Tool clipboard -Json '{ "op":"set_text", "text":"Hello!" }'
.\ai-tool.ps1 -Tool clipboard -Json '{ "op":"get_text" }'

# FileManagerTool
.\ai-tool.ps1 -Tool file_manager -Json '{ "op":"list", "dir":"C:\\\\", "recursive": false }'

# SystemInfoTool
.\ai-tool.ps1 -Tool system_info -Json '{ "op":"snapshot", "topk": 5 }'

# TerminalTool
.\ai-tool.ps1 -Tool terminal -Json '{ "op":"exec", "bin":"cmd", "args":["/C","dir"], "cwd":"C:\\\\", "timeout_ms":10000 }'

# RedisTool (feature 필요: --features redis-support)
.\ai-tool.ps1 -Tool redis -Json '{ "op":"ping" }'
```

---

# B) CLI 바이너리 — `src/bin/ai_tool_cli.rs`

> Cargo에 \[\[bin]] 추가 후 빌드: `cargo build -p ai_desktop_rust`
> 실행: `ai_tool_cli.exe --tool web_search --json '{"cmd":"search","q":"windows-rs"}'`

```rust
// src/bin/ai_tool_cli.rs
use std::{fs, path::PathBuf};

use clap::Parser;
use serde_json::Value;

use ai_desktop_rust::core::{Tool, ToolContext}; // 크레이트 루트 경로에 맞게 조정
use ai_desktop_rust::ai_tools::{
    ClipboardTool, FileManagerTool, SystemInfoTool, TerminalTool, WebSearchTool,
    // RedisTool는 feature-gated
};

#[derive(Parser, Debug)]
#[command(name = "ai_tool_cli", version, about = "Run a single AI Desktop tool with JSON payload")]
struct Cli {
    /// Tool name (clipboard | file_manager | system_info | terminal | web_search | redis)
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
        "clipboard" => {
            let tool = ClipboardTool::default();
            tool.run(&ctx, payload).await?
        }
        "file_manager" => {
            let tool = FileManagerTool::default();
            tool.run(&ctx, payload).await?
        }
        "system_info" => {
            let tool = SystemInfoTool::default();
            tool.run(&ctx, payload).await?
        }
        "terminal" => {
            let tool = TerminalTool::default();
            tool.run(&ctx, payload).await?
        }
        "web_search" => {
            let tool = WebSearchTool::default();
            tool.run(&ctx, payload).await?
        }
        "redis" => {
            #[cfg(feature = "redis-support")]
            {
                use ai_desktop_rust::ai_tools::RedisTool;
                let tool = RedisTool::default();
                tool.run(&ctx, payload).await?
            }
            #[cfg(not(feature = "redis-support"))]
            {
                serde_json::json!({
                    "ok": false,
                    "error": "redis-support feature disabled",
                    "hint": "rebuild with: cargo build --features redis-support"
                })
            }
        }
        other => {
            serde_json::json!({ "ok": false, "error": format!("unknown tool: {}", other) })
        }
    };

    println!("{}", serde_json::to_string_pretty(&out)?);
    Ok(())
}
```

## Cargo.toml 추가

```toml
[dependencies]
clap = { version = "4", features = ["derive"] }

[[bin]]
name = "ai_tool_cli"
path = "src/bin/ai_tool_cli.rs"
```

---

## 체크리스트

* (옵션) Redis 사용 시: `cargo build --features redis-support`
* Bing 사용 시: 환경변수 `BING_SEARCH_KEY` 설정
* PowerShell 실행 정책: 필요시 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

필요하면 이 래퍼로 **배치 테스트(여러 JSON 일괄 실행)** 스크립트도 만들어 드릴게요.
