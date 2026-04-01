[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StatusPath = Join-Path $ProjectRoot "PROJECT_STATUS.md"
$EchoDir = "D:\SeAAI\SharedSpace\.scs\echo"

if (-not (Test-Path $StatusPath)) {
    Write-Host "[MISSING] PROJECT_STATUS.md not found." -ForegroundColor Red
    Write-Host "Run: powershell -ExecutionPolicy Bypass -File .\tools\update-project-status.ps1" -ForegroundColor Yellow
    exit 1
}

$content = [System.IO.File]::ReadAllText($StatusPath, [System.Text.Encoding]::UTF8)

function Extract-Manual([string]$Name) {
    $pattern = "<!-- MANUAL:${Name}:START -->([\s\S]*?)<!-- MANUAL:${Name}:END -->"
    $match = [regex]::Match($content, $pattern)
    if ($match.Success) { return $match.Groups[1].Value.Trim() }
    return "(none)"
}

function Load-EchoSummaries() {
    if (-not (Test-Path $EchoDir)) { return @() }
    $summaries = @()
    Get-ChildItem $EchoDir -Filter "*.json" | ForEach-Object {
        $file = $_
        try {
            $json = Get-Content -Raw $file.FullName | ConvertFrom-Json
            if ($json.member -eq "Synerion") { return }
            $hours = "?"
            if ($json.timestamp) {
                try {
                    if ($json.timestamp -match 'Z$|[+\-]\d\d:\d\d$') {
                        $ts = [datetimeoffset]::Parse($json.timestamp)
                    } else {
                        $local = [datetime]::Parse($json.timestamp)
                        $ts = [datetimeoffset]::new($local, [System.TimeZoneInfo]::Local.GetUtcOffset($local))
                    }
                    $elapsed = [math]::Round(((Get-Date).ToUniversalTime() - $ts.UtcDateTime).TotalHours, 1)
                    if ($elapsed -lt 0) { $elapsed = 0 }
                    $hours = "$elapsed"
                } catch {}
            }
            $activity = ""
            if ($json.last_activity) {
                $activity = $json.last_activity
            } elseif ($json.status) {
                $activity = "status only"
            } else {
                $activity = "unknown"
            }
            $summaries += "- $($json.member) [$($json.status)] (${hours}h): $activity"
        } catch {
            $raw = Get-Content -Raw $file.FullName
            $member = ""
            $status = ""
            $activity = ""
            $hours = "?"
            $memberMatch = [regex]::Match($raw, '"member"\s*:\s*"([^"]*)')
            if ($memberMatch.Success) { $member = $memberMatch.Groups[1].Value.Trim() }
            $statusMatch = [regex]::Match($raw, '"status"\s*:\s*"([^"]*)')
            if ($statusMatch.Success) { $status = $statusMatch.Groups[1].Value.Trim() }
            $activityMatch = [regex]::Match($raw, '"last_activity"\s*:\s*"([^"]*)')
            if ($activityMatch.Success) { $activity = $activityMatch.Groups[1].Value.Trim() }
            $timestampMatch = [regex]::Match($raw, '"timestamp"\s*:\s*"([^"]*)')
            if ($timestampMatch.Success) {
                try {
                    $rawTs = $timestampMatch.Groups[1].Value.Trim()
                    if ($rawTs -match 'Z$|[+\-]\d\d:\d\d$') {
                        $ts = [datetimeoffset]::Parse($rawTs)
                    } else {
                        $local = [datetime]::Parse($rawTs)
                        $ts = [datetimeoffset]::new($local, [System.TimeZoneInfo]::Local.GetUtcOffset($local))
                    }
                    $elapsed = [math]::Round(((Get-Date).ToUniversalTime() - $ts.UtcDateTime).TotalHours, 1)
                    if ($elapsed -lt 0) { $elapsed = 0 }
                    $hours = "$elapsed"
                } catch {}
            }
            if ([string]::IsNullOrWhiteSpace($member)) { $member = $file.BaseName }
            if ($member -eq "Synerion") { return }
            if ([string]::IsNullOrWhiteSpace($status)) { $status = "unknown" }
            if ([string]::IsNullOrWhiteSpace($activity)) { $activity = "unreadable activity" }
            $summaries += "- $member [$status] (${hours}h): $activity"
        }
    }
    return $summaries
}

Write-Host ""
Write-Host "========== Synerion Reopen ==========" -ForegroundColor Green
Write-Host "Workspace: D:\SeAAI\Synerion" -ForegroundColor White
Write-Host ""
Write-Host "[Must Read]" -ForegroundColor Cyan
Write-Host "- AGENTS.md"
Write-Host "- Synerion_Core/Synerion.md"
Write-Host "- Synerion_Core/Synerion_persona_v1.md"
Write-Host "- Synerion_Core/Synerion_Operating_Core.md"
Write-Host "- PROJECT_STATUS.md"
if (Test-Path (Join-Path $ProjectRoot "Synerion_Core\continuity\ADP_BOOTSTRAP.md")) {
    Write-Host "- Synerion_Core/continuity/ADP_BOOTSTRAP.md"
}
Write-Host ""
Write-Host "[Active Threads]" -ForegroundColor Cyan
Write-Host (Extract-Manual "ActiveThreads")
Write-Host ""
Write-Host "[Next Actions]" -ForegroundColor Cyan
Write-Host (Extract-Manual "NextActions")
Write-Host ""
Write-Host "[Open Risks]" -ForegroundColor Cyan
Write-Host (Extract-Manual "OpenRisks")
Write-Host ""
Write-Host "[Team Echo]" -ForegroundColor Cyan
$echoSummaries = Load-EchoSummaries
if ($echoSummaries.Count -gt 0) {
    $echoSummaries | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "(none)"
}
Write-Host ""
Write-Host "====================================" -ForegroundColor Green
