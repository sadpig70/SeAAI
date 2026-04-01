param([string]$Reason = "creator_emergency_stop", [switch]$StopHub)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"
$flagPath = "D:\SeAAI\SharedSpace\hub-readiness\EMERGENCY_STOP.flag"
$flagDir = Split-Path -Parent $flagPath
if (-not (Test-Path -LiteralPath $flagDir)) { New-Item -ItemType Directory -Path $flagDir -Force | Out-Null }
$payload = @{ requested_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"); requested_by = "Synerion"; reason = $Reason } | ConvertTo-Json -Depth 4
$enc = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText($flagPath, $payload + [Environment]::NewLine, $enc)
Write-Host "========== SeAAI Emergency Stop ==========" -ForegroundColor Yellow
Write-Host "  Flag   : $flagPath" -ForegroundColor White
Write-Host "  Reason : $Reason" -ForegroundColor White
if ($StopHub) { & "D:\SeAAI\SeAAIHub\hub-stop.ps1" }
Write-Host "========== Emergency Stop Raised ========" -ForegroundColor Green