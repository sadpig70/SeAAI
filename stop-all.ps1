[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== SeAAI Stop All ==========" -ForegroundColor Yellow

# Hub
$hub = Get-Process -Name "SeAAIHub" -ErrorAction SilentlyContinue
if ($hub) {
    Stop-Process -Name "SeAAIHub" -Force
    Write-Host "  Hub        : stopped" -ForegroundColor White
} else {
    Write-Host "  Hub        : not running" -ForegroundColor DarkGray
}

# Claude 프로세스 (NAEL, ClNeo)
$claude = Get-Process -Name "claude" -ErrorAction SilentlyContinue
if ($claude) {
    Write-Host "  Claude     : $(@($claude).Count) process(es) found" -ForegroundColor White
    Write-Host "  (Claude sessions should be closed manually or via Ctrl+C)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "========== SeAAI Stopped ==========" -ForegroundColor Green
Write-Host ""
