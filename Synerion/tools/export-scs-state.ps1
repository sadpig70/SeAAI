[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StatusPath = Join-Path $ProjectRoot "PROJECT_STATUS.md"
$ContinuityDir = Join-Path $ProjectRoot "Synerion_Core\continuity"
$StatePath = Join-Path $ContinuityDir "STATE.json"
$ThreadsPath = Join-Path $ContinuityDir "THREADS.md"
$JournalDir = Join-Path $ContinuityDir "journals"
$SoulPath = Join-Path $ContinuityDir "SOUL.md"

function Read-Utf8Text([string]$Path) {
    if (-not (Test-Path $Path)) { return "" }
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8Bom([string]$Path, [string]$Content) {
    $enc = [System.Text.UTF8Encoding]::new($true)
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Extract-Manual([string]$Content, [string]$Name) {
    $pattern = "<!-- MANUAL:${Name}:START -->([\s\S]*?)<!-- MANUAL:${Name}:END -->"
    $match = [regex]::Match($Content, $pattern)
    if ($match.Success) { return $match.Groups[1].Value.Trim() }
    return ""
}

function Bullet-Lines([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return @() }
    return $Text -split "`r?`n" |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -match "^- " } |
        ForEach-Object { $_ -replace "^- ", "" }
}

if (-not (Test-Path $StatusPath)) {
    throw "PROJECT_STATUS.md not found: $StatusPath"
}

New-Item -ItemType Directory -Force -Path $ContinuityDir | Out-Null
New-Item -ItemType Directory -Force -Path $JournalDir | Out-Null

$statusContent = Read-Utf8Text $StatusPath
$activeThreads = Bullet-Lines (Extract-Manual $statusContent "ActiveThreads")
$nextActions = Bullet-Lines (Extract-Manual $statusContent "NextActions")
$openRisks = Bullet-Lines (Extract-Manual $statusContent "OpenRisks")
$sessionId = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
$journalDate = (Get-Date).ToString("yyyy-MM-dd")
$journalPath = Join-Path $JournalDir "$journalDate.md"
$soulHash = ""
if (Test-Path $SoulPath) {
    $soulHash = "sha256:" + (Get-FileHash -Algorithm SHA256 $SoulPath).Hash.ToLowerInvariant()
}

$pendingTasks = @()
$index = 1
foreach ($action in $nextActions) {
    $pendingTasks += @{
        priority = if ($index -le 2) { "P0" } else { "P1" }
        id = ("T-{0:D3}" -f $index)
        task = $action
        status = "pending"
        blocker = ""
    }
    $index++
}

$state = [ordered]@{
    schema_version = "2.0"
    member = "Synerion"
    session_id = $sessionId
    last_saved = $sessionId
    soul_hash = $soulHash
    context = [ordered]@{
        what_i_was_doing = if ($activeThreads.Count -gt 0) {
            $activeThreads -join " "
        } else {
            "Continuity state refreshed from PROJECT_STATUS."
        }
        open_threads = @($activeThreads)
        decisions_made = @(
            "PROJECT_STATUS.md remains the canonical state.",
            "SCS v2 is used as a compatibility layer over Synerion continuity."
        )
        pending_questions = @($openRisks)
    }
    ecosystem = [ordered]@{
        hub_status = "running"
        threat_level = if ($openRisks.Count -gt 0) { "medium" } else { "low" }
        last_hub_session = "2026-03-27T14:27:42+09:00"
        active_members_observed = @("NAEL", "MockHub")
    }
    pending_tasks = @($pendingTasks)
    evolution_state = [ordered]@{
        current_version = "v1.1-scs-phase2"
        active_gap = "PROJECT_STATUS export plus Echo consume integration"
    }
    continuity_health = [ordered]@{
        sessions_since_last_save = 0
        last_save_quality = "full"
        staleness_warning = $false
    }
}

Write-Utf8Bom $StatePath ($state | ConvertTo-Json -Depth 8)

$threadLines = New-Object System.Collections.Generic.List[string]
$threadLines.Add("# Synerion Threads")
$threadLines.Add("")
$threadLines.Add("## BLOCKED OR URGENT")
$threadLines.Add("")
if ($openRisks.Count -gt 0) {
    $idx = 201
    foreach ($risk in $openRisks) {
        $threadLines.Add("### [T-$idx] Risk item")
        $threadLines.Add("**Status**: blocked")
        $threadLines.Add("**Goal**: turn this risk into a controllable rule or implementation task.")
        $threadLines.Add("**Blocker**: $risk")
        $threadLines.Add("**Next**: define a concrete guardrail or code path for this risk.")
        $threadLines.Add("")
        $idx++
    }
} else {
    $threadLines.Add("- none")
    $threadLines.Add("")
}

$threadLines.Add("## IN PROGRESS")
$threadLines.Add("")
if ($activeThreads.Count -gt 0) {
    $idx = 101
    foreach ($thread in $activeThreads) {
        $threadLines.Add("### [T-$idx] Active thread")
        $threadLines.Add("**Status**: in_progress")
        $threadLines.Add("**Goal**: $thread")
        $threadLines.Add("**Blocker**: consult Open Risks if needed.")
        $threadLines.Add("**Next**: keep moving by linking this thread to a next action.")
        $threadLines.Add("")
        $idx++
    }
} else {
    $threadLines.Add("- none")
    $threadLines.Add("")
}

$threadLines.Add("## LONG TERM OR BACKLOG")
$threadLines.Add("")
if ($nextActions.Count -gt 0) {
    $idx = 301
    foreach ($action in $nextActions) {
        $threadLines.Add("### [T-$idx] Next action")
        $threadLines.Add("**Status**: pending")
        $threadLines.Add("**Goal**: $action")
        $threadLines.Add("**Blocker**: not yet specified.")
        $threadLines.Add("**Next**: promote this item into an active thread when priority rises.")
        $threadLines.Add("")
        $idx++
    }
} else {
    $threadLines.Add("- none")
    $threadLines.Add("")
}

$threadLines.Add("## RECENTLY COMPLETED")
$threadLines.Add("")
$threadLines.Add("- continuity system installed and PROJECT_STATUS established as canonical state (2026-03-28)")
$threadLines.Add("- SCS-Universal v2 reviewed and Synerion adapter defined (2026-03-28)")
Write-Utf8Bom $ThreadsPath ($threadLines -join "`n")

if (-not (Test-Path $journalPath)) {
    $coreWork = if ($activeThreads.Count -gt 0) {
        ($activeThreads | ForEach-Object { "- $_" }) -join "`n"
    } else {
        "- continuity refresh"
    }
    $nextMessage = if ($nextActions.Count -gt 0) {
        ($nextActions | ForEach-Object { "- $_" }) -join "`n"
    } else {
        "- no next action recorded"
    }
    $journalContent = @"
---
date: $journalDate
significant: true
---

# Journal - $journalDate

## What Happened

$($state.context.what_i_was_doing)

## Core Work

$coreWork

## Discovery

- Exporting SCS files from PROJECT_STATUS is the safest bridge for Synerion.

## Message For Next Session

$nextMessage
"@
    Write-Utf8Bom $journalPath $journalContent
}

Write-Host "SCS export complete:" -ForegroundColor Green
Write-Host "  STATE   -> $StatePath"
Write-Host "  THREADS -> $ThreadsPath"
Write-Host "  JOURNAL -> $journalPath"
