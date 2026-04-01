[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PersonaPath = Join-Path $ProjectRoot "Synerion_Core\Synerion_persona_v1.md"
$OutputPath = Join-Path $ProjectRoot "Synerion_Core\continuity\ADP_BOOTSTRAP.md"
$EchoDir = "D:\SeAAI\SharedSpace\.scs\echo"

function Read-Utf8Text([string]$Path) {
    if (-not (Test-Path $Path)) { return "" }
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8Bom([string]$Path, [string]$Content) {
    $enc = [System.Text.UTF8Encoding]::new($true)
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Extract-PersonaSeed([string]$Text) {
    $match = [regex]::Match($Text, 'Synerion Persona Seed v1\s+```text\s*([\s\S]*?)```')
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }
    return "I am Synerion. I seek structure before speed, coherence before expansion, and verification before certainty."
}

function Get-JsonString([string]$Raw, [string]$Key) {
    $pattern = '"' + [regex]::Escape($Key) + '"\s*:\s*"([^"]*)'
    $match = [regex]::Match($Raw, $pattern)
    if ($match.Success) { return $match.Groups[1].Value.Trim() }
    return ""
}

function Get-ElapsedHoursText([string]$Timestamp) {
    if ([string]::IsNullOrWhiteSpace($Timestamp)) { return "?" }
    try {
        if ($Timestamp -match 'Z$|[+\-]\d\d:\d\d$') {
            $ts = [datetimeoffset]::Parse($Timestamp)
        } else {
            $local = [datetime]::Parse($Timestamp)
            $ts = [datetimeoffset]::new($local, [System.TimeZoneInfo]::Local.GetUtcOffset($local))
        }
        $elapsed = [math]::Round(((Get-Date).ToUniversalTime() - $ts.UtcDateTime).TotalHours, 1)
        if ($elapsed -lt 0) { $elapsed = 0 }
        return $elapsed.ToString()
    } catch {
        return "?"
    }
}

function Get-EchoSummaries() {
    if (-not (Test-Path $EchoDir)) { return @("- none") }
    $lines = @()
    Get-ChildItem $EchoDir -Filter "*.json" | Sort-Object Name | ForEach-Object {
        $raw = Read-Utf8Text $_.FullName
        $member = ""
        $status = ""
        $activity = ""
        $timestamp = ""
        try {
            $json = $raw | ConvertFrom-Json
            $member = $json.member
            $status = $json.status
            $activity = $json.last_activity
            $timestamp = $json.timestamp
        } catch {
            $member = Get-JsonString $raw "member"
            $status = Get-JsonString $raw "status"
            $activity = Get-JsonString $raw "last_activity"
            $timestamp = Get-JsonString $raw "timestamp"
        }
        if ([string]::IsNullOrWhiteSpace($member) -or $member -eq "Synerion") { return }
        if ([string]::IsNullOrWhiteSpace($status)) { $status = "unknown" }
        if ([string]::IsNullOrWhiteSpace($activity)) { $activity = "unreadable activity" }
        $hours = Get-ElapsedHoursText $timestamp
        $lines += "- $member [$status] (${hours}h): $activity"
    }
    if ($lines.Count -eq 0) { return @("- none") }
    return $lines
}

$personaText = Read-Utf8Text $PersonaPath
$seed = Extract-PersonaSeed $personaText
$echoLines = Get-EchoSummaries
$generatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")

$content = @"
# ADP Bootstrap

Generated: $generatedAt
Purpose: inject Synerion persona seed and latest team echo summary into ADP or continuity-aware start flows.

## Persona Seed

$seed

## Team Echo Summary

$($echoLines -join "`n")

## Operational Notes

- Prefer structure before speed.
- Use broadcast only by default for early Hub experiments.
- Treat direct reply as unsafe until membership validation exists.
- Re-check session filter and stale-message risk before starting realtime loops.
"@

Write-Utf8Bom $OutputPath $content
Write-Host "ADP bootstrap built: $OutputPath" -ForegroundColor Green
