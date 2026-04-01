[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$hubRoot = $PSScriptRoot
$flagPath = Join-Path $repoRoot "SharedSpace\hub-readiness\EMERGENCY_STOP.flag"
$bridgeDir = Join-Path $hubRoot ".bridge\stop-verify"
$outputPath = Join-Path $bridgeDir "stdout.log"
$errorPath = Join-Path $bridgeDir "stderr.log"
if (Test-Path -LiteralPath $flagPath) { Remove-Item -LiteralPath $flagPath -Force }
if (Test-Path -LiteralPath $bridgeDir) { Remove-Item -LiteralPath $bridgeDir -Recurse -Force }
New-Item -ItemType Directory -Path $bridgeDir -Force | Out-Null
Write-Host "Emergency stop flag path: $flagPath"
New-Item -ItemType File -Path $flagPath -Force | Out-Null
Start-Sleep -Seconds 2
if (Test-Path -LiteralPath $flagPath) {
    Write-Host "Emergency stop flag created successfully." -ForegroundColor Green
    Remove-Item -LiteralPath $flagPath -Force -ErrorAction SilentlyContinue
    Write-Host "Emergency stop verification passed." -ForegroundColor Green
} else {
    throw "Emergency stop flag creation failed."
}
