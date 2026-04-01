[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$Checks = @(
    "AGENTS.md",
    "SESSION_CONTINUITY.md",
    "PROJECT_STATUS.md",
    "Synerion_Core\Synerion.md",
    "Synerion_Core\Synerion_persona_v1.md",
    "Synerion_Core\Synerion_Operating_Core.md",
    ".pgf\DESIGN-SessionContinuitySystem.md",
    ".pgf\WORKPLAN-SessionContinuitySystem.md",
    ".pgf\status-SessionContinuitySystem.json",
    "tools\update-project-status.ps1",
    "tools\export-scs-state.ps1",
    "tools\build-adp-bootstrap.ps1",
    "tools\reopen-synerion-session.ps1",
    "tools\continuity-self-test.ps1"
)

$Failed = $false

Write-Host "========== Continuity Self Test ==========" -ForegroundColor Green
foreach ($rel in $Checks) {
    $full = Join-Path $ProjectRoot $rel
    if (Test-Path $full) {
        Write-Host "[OK] $rel" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $rel" -ForegroundColor Red
        $Failed = $true
    }
}

if (-not $Failed) {
    Write-Host "Continuity system is installed." -ForegroundColor Green
    exit 0
}

Write-Host "Continuity system is incomplete." -ForegroundColor Yellow
exit 1
