[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== Aion Session Start ==========" -ForegroundColor Yellow
Write-Host "  Runtime : Gemini CLI (Antigravity)" -ForegroundColor White
Write-Host "  Workspace : D:\SeAAI\Aion" -ForegroundColor White
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

# 2. Aion 세션 시작
Write-Host ""
Write-Host "  Launching Aion..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

Set-Location "D:\SeAAI\Aion"

# ── Gemini CLI 경로 설정 (설치 후 수정할 것) ──
# $GEMINI_PATH = "gemini"  # 기본: PATH에 등록된 경우
# $GEMINI_PATH = "C:\path\to\gemini.exe"  # 또는 절대 경로 지정

$geminiCmd = Get-Command gemini -ErrorAction SilentlyContinue
if ($geminiCmd) {
    gemini -p "MailBox를 확인하라. docs/PPR-ADP-HubChatSession.md를 읽고 1시간 ADP Hub Chat Session을 시작하라."
} else {
    Write-Host "  [ERROR] Gemini CLI not found." -ForegroundColor Red
    Write-Host "  Install Gemini CLI and ensure it is in PATH, or set absolute path in this script." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Alternative: Aion Solo Loop (Hub-less)" -ForegroundColor DarkGray
    Write-Host "    python D:\SeAAI\Aion\Aion_Core\tools\aion-solo-loop.py --duration 3600" -ForegroundColor DarkGray
}
