[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "========== SeAAIHub Stop ===========" -ForegroundColor Yellow

$hub = Get-Process -Name "SeAAIHub" -ErrorAction SilentlyContinue
if ($hub) {
    Stop-Process -Name "SeAAIHub" -Force
    Write-Host "  Hub Server    : stopped" -ForegroundColor White
} else {
    Write-Host "  Hub Server    : not running" -ForegroundColor DarkGray
}

$dashboard = Get-WmiObject Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*hub-dashboard*" }
if ($dashboard) {
    foreach ($d in @($dashboard)) {
        Stop-Process -Id $d.ProcessId -Force
    }
    Write-Host "  Dashboard     : stopped" -ForegroundColor White
} else {
    Write-Host "  Dashboard     : not running" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "========== SeAAIHub Stopped ========" -ForegroundColor Green
Write-Host ""
