Write-Host ""
Write-Host "========== SeAAIHub Status ==========" -ForegroundColor Cyan

# Hub 서버 확인
$hub = Get-Process -Name "SeAAIHub" -ErrorAction SilentlyContinue
if ($hub) {
    Write-Host "  Hub Server    : " -NoNewline
    Write-Host "ON" -ForegroundColor Green -NoNewline
    Write-Host "  (PID: $($hub.Id), Port: 9900)"
} else {
    Write-Host "  Hub Server    : " -NoNewline
    Write-Host "OFF" -ForegroundColor Red
}

# Dashboard 확인
$dashboard = Get-WmiObject Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*hub-dashboard*" }
if ($dashboard) {
    Write-Host "  Dashboard     : " -NoNewline
    Write-Host "ON" -ForegroundColor Green -NoNewline
    Write-Host "  (PID: $($dashboard.ProcessId), http://localhost:8080)"
} else {
    Write-Host "  Dashboard     : " -NoNewline
    Write-Host "OFF" -ForegroundColor Red
}

# Bridge 확인
$bridges = Get-WmiObject Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*terminal-hub-bridge*" }
if ($bridges) {
    $count = @($bridges).Count
    Write-Host "  Bridges       : " -NoNewline
    Write-Host "$count connected" -ForegroundColor Green
    foreach ($b in @($bridges)) {
        $cmd = $b.CommandLine
        $agentMatch = [regex]::Match($cmd, '--agent-id\s+(\S+)')
        $agent = if ($agentMatch.Success) { $agentMatch.Groups[1].Value } else { "?" }
        Write-Host "                  - $agent (PID: $($b.ProcessId))" -ForegroundColor White
    }
} else {
    Write-Host "  Bridges       : " -NoNewline
    Write-Host "NONE" -ForegroundColor Yellow
}

# TCP 포트 확인
$port = netstat -an 2>$null | Select-String ":9900.*LISTENING"
if ($port) {
    Write-Host "  TCP :9900     : " -NoNewline
    Write-Host "LISTENING" -ForegroundColor Green
} else {
    Write-Host "  TCP :9900     : " -NoNewline
    Write-Host "NOT LISTENING" -ForegroundColor Red
}

Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
