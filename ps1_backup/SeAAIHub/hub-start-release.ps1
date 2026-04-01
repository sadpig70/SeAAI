[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$BIN = "D:\SeAAI\SeAAIHub\target\release\SeAAIHub.exe"

if (-not (Test-Path $BIN)) {
    Write-Error "Release binary not found. Build first: cargo build --release"
    exit 1
}

Write-Host ""
Write-Host "========== SeAAIHub Start (RELEASE) ==========" -ForegroundColor Cyan

Write-Host "  Starting Hub Server (release)..." -ForegroundColor White
Start-Process -FilePath $BIN -ArgumentList "--tcp-port 9900"
Start-Sleep -Seconds 2

Write-Host "  Starting Dashboard..." -ForegroundColor White
Start-Process -FilePath "python" -ArgumentList "D:\SeAAI\SeAAIHub\tools\hub-dashboard.py --hub-port 9900 --web-port 8080"
Start-Sleep -Seconds 2

Write-Host "  Opening Browser..." -ForegroundColor White
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "========== SeAAIHub Ready (RELEASE) ==========" -ForegroundColor Green
Write-Host "  Hub       : 127.0.0.1:9900" -ForegroundColor White
Write-Host "  Dashboard : http://localhost:8080" -ForegroundColor White
Write-Host "  Binary    : $BIN" -ForegroundColor Gray
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Stop: powershell -File D:\SeAAI\SeAAIHub\hub-stop.ps1" -ForegroundColor Yellow
Write-Host ""
