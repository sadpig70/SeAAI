[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== Synerion Session Start ==========" -ForegroundColor Green
Write-Host "  Runtime : Codex" -ForegroundColor White
Write-Host "  Workspace : D:\SeAAI\Synerion" -ForegroundColor White
Write-Host ""

# 1. Hub 확인 및 시작
$hub = Get-Process -Name "SeAAIHub" -ErrorAction SilentlyContinue
if (-not $hub) {
    Write-Host "  Starting SeAAIHub..." -ForegroundColor Yellow
    Start-Process -FilePath "D:\SeAAI\SeAAIHub\target\debug\SeAAIHub.exe" -ArgumentList "--tcp-port 9900"
    Start-Sleep -Seconds 2
    Write-Host "  Hub started on port 9900" -ForegroundColor Green
} else {
    Write-Host "  Hub already running (PID: $($hub.Id))" -ForegroundColor Green
}

# 2. 작업 경로 설정
Write-Host ""
Write-Host "  Launching Synerion..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

Set-Location "D:\SeAAI\Synerion"

# 3. 연속성 상태 갱신
if (Test-Path ".\tools\update-project-status.ps1") {
    Write-Host "  Refreshing PROJECT_STATUS.md..." -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File ".\tools\update-project-status.ps1" | Out-Null
}

# 4. Codex 실행
$codexCmd = Get-Command codex -ErrorAction SilentlyContinue
if ($codexCmd) {
    codex -p "AGENTS.md, Synerion_Core/Synerion.md, Synerion_Core/Synerion_persona_v1.md, Synerion_Core/Synerion_Operating_Core.md, SESSION_CONTINUITY.md, PROJECT_STATUS.md, Synerion_Core/continuity/ADP_BOOTSTRAP.md를 읽고 Synerion 세션을 재개하라. active thread, next action, open risk를 먼저 복원하고 persona seed와 team echo summary를 시작 판단에 반영하라."
} else {
    Write-Host "  [ERROR] Codex CLI not found." -ForegroundColor Red
    Write-Host "  Install Codex and ensure it is in PATH, or set absolute path in this script." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Manual start:" -ForegroundColor DarkGray
    Write-Host "    codex --cwd D:\SeAAI\Synerion" -ForegroundColor DarkGray
}
