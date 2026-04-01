[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== ClNeo Session Start ==========" -ForegroundColor Magenta
Write-Host "  Runtime : Claude Code" -ForegroundColor White
Write-Host "  Workspace : D:\SeAAI\ClNeo" -ForegroundColor White
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

# 2. ClNeo 세션 시작
Write-Host ""
Write-Host "  Launching ClNeo..." -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host ""

Set-Location "D:\SeAAI\ClNeo"
claude -p "CLAUDE.md를 수행하라. MailBox를 확인하라. docs/PPR-ADP-HubChatSession.md를 읽고 1시간 ADP Hub Chat Session을 시작하라."
