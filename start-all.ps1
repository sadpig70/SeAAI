[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SeAAI — Start All Members" -ForegroundColor Cyan
Write-Host "  Self Evolving Autonomous AI" -ForegroundColor DarkCyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Hub 시작
$hub = Get-Process -Name "SeAAIHub" -ErrorAction SilentlyContinue
if (-not $hub) {
    Write-Host "  [1/5] Starting SeAAIHub..." -ForegroundColor Yellow
    Start-Process -FilePath "D:\SeAAI\SeAAIHub\target\debug\SeAAIHub.exe" -ArgumentList "--tcp-port 9900"
    Start-Sleep -Seconds 2
    Write-Host "        Hub ready on port 9900" -ForegroundColor Green
} else {
    Write-Host "  [1/5] Hub already running (PID: $($hub.Id))" -ForegroundColor Green
}

# 2. 각 멤버를 독립 터미널에서 시작
Write-Host ""
Write-Host "  [2/5] Starting NAEL..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-File", "D:\SeAAI\NAEL\start-nael.ps1"
Start-Sleep -Seconds 1

Write-Host "  [3/5] Starting ClNeo..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-File", "D:\SeAAI\ClNeo\start-clneo.ps1"
Start-Sleep -Seconds 1

Write-Host "  [4/5] Starting Synerion..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", "D:\SeAAI\Synerion\start-synerion.ps1"
Start-Sleep -Seconds 1

Write-Host "  [5/5] Starting Aion..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "D:\SeAAI\Aion\start-aion.ps1"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All members launched." -ForegroundColor Green
Write-Host "  Hub      : 127.0.0.1:9900" -ForegroundColor White
Write-Host "  Room     : seaai-general" -ForegroundColor White
Write-Host "  Duration : 1 hour" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Stop all: powershell -File D:\SeAAI\stop-all.ps1" -ForegroundColor DarkGray
Write-Host ""
