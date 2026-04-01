[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== NAEL Session Start ==========" -ForegroundColor Cyan
Write-Host "  Runtime : Claude Code" -ForegroundColor White
Write-Host "  Workspace : D:\SeAAI\NAEL" -ForegroundColor White
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

# 2. NAEL 세션 시작
Write-Host ""
Write-Host "  Launching NAEL..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\SeAAI\NAEL"
claude -p "CLAUDE.md를 수행하라. 그리고 PPR-ADP-HubChatSession.md를 읽고 1시간 ADP Hub Chat Session을 시작하라."
