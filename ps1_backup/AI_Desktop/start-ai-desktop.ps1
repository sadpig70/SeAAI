# SeAAI AI_Desktop MCP Server — Start Script
# Claude Code의 mcpServers 설정에 의해 자동 시작되므로 직접 실행은 테스트용
#
# 사용: .\start-ai-desktop.ps1
# 조건: D:\SeAAI\AI_Desktop\ 에서 실행할 것 (dynamic_tools/ 경로 기준)

$WORK_DIR = $PSScriptRoot
$BIN_RELEASE = "$WORK_DIR\target\release\ai_desktop_mcp.exe"
$BIN_DEBUG   = "$WORK_DIR\target\debug\ai_desktop_mcp.exe"

if (Test-Path $BIN_RELEASE) {
    $BIN = $BIN_RELEASE
} elseif (Test-Path $BIN_DEBUG) {
    $BIN = $BIN_DEBUG
} else {
    Write-Error "Binary not found. Build first:"
    Write-Host "  cd D:\SeAAI\AI_Desktop && cargo build --release --bin ai_desktop_mcp"
    exit 1
}

Write-Host "[AI_Desktop] Starting MCP server..."
Write-Host "  Binary   : $BIN"
Write-Host "  WorkDir  : $WORK_DIR"
Write-Host "  Tools    : $WORK_DIR\dynamic_tools\"
Write-Host ""
Write-Host "  Press Ctrl+C to stop"
Write-Host ""

Set-Location $WORK_DIR
& $BIN
