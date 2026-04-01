# PGF-Loop Stop Hook
# Called on Claude Code session termination to re-inject the next node prompt.
# Supports both Standard mode (DESIGN+WORKPLAN) and Lightweight mode (WORKPLAN only).
#
# stdin: JSON { "session_id": "...", "transcript_path": "..." }
# stdout: JSON { "decision": "block", "reason": "...", "systemMessage": "..." }
#         or exit 0 with no output (normal termination)

$ErrorActionPreference = "Stop"

# ─── Status normalization (Korean → English backward compatibility) ───
function ConvertTo-EnglishStatus([string]$s) {
    # Map legacy Korean status values to English (encoding-safe via char codes)
    $ko_done = "$([char]0xC644)$([char]0xB8CC)"           # 완료
    $ko_prog = "$([char]0xC9C4)$([char]0xD589)$([char]0xC911)" # 진행중
    $ko_pend = "$([char]0xC124)$([char]0xACC4)$([char]0xC911)" # 설계중
    $ko_block = "$([char]0xBCF4)$([char]0xB958)"           # 보류
    if ($s -eq $ko_done)  { return "done" }
    if ($s -eq $ko_prog)  { return "in_progress" }
    if ($s -eq $ko_pend)  { return "pending" }
    if ($s -eq $ko_block) { return "blocked" }
    return $s
}

$STATE_FILE = ".claude/pgf-loop-state.json"

# ─── 1. Check state file ───
if (-not (Test-Path $STATE_FILE)) {
    exit 0
}

# ─── 2. Parse stdin ───
$hookRaw = [Console]::In.ReadToEnd()
try {
    $hookInput = $hookRaw | ConvertFrom-Json
} catch {
    exit 0
}
$hookSid = if ($hookInput.session_id) { $hookInput.session_id } else { "" }

# ─── 3. Load state ───
try {
    $state = Get-Content $STATE_FILE -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    exit 0
}

$stateSid      = if ($state.session_id) { $state.session_id } else { "" }
$iteration     = [int]$state.iteration
$maxIter       = [int]$state.max_iterations
$workplanPath  = $state.workplan_path
$designPath    = if ($state.design_path) { $state.design_path } else { "" }
$statusPath    = $state.status_path
$currentNode   = if ($state.current_node) { $state.current_node } else { "" }
$loopMode      = if ($state.mode) { $state.mode } else { "standard" }
$policyRaw     = $state.policy

# ─── 4. Session isolation ───
if ($stateSid -and $hookSid -and ($stateSid -ne $hookSid)) {
    exit 0
}

# ─── 5. Iteration limit ───
if ($maxIter -gt 0 -and $iteration -ge $maxIter) {
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    [Console]::Error.WriteLine("[PGF-Loop] max_iterations ($maxIter) reached. Loop terminated.")
    exit 0
}

# ─── 6. Load status.json ───
if (-not (Test-Path $statusPath)) {
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    [Console]::Error.WriteLine("[PGF-Loop] status.json not found: $statusPath")
    exit 0
}

try {
    $status = Get-Content $statusPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    [Console]::Error.WriteLine("[PGF-Loop] status.json parse error")
    exit 0
}

# ─── 7. Select next node ───
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nextNode = & "$scriptDir/select-next-node.ps1" -WorkplanPath $workplanPath -StatusPath $statusPath

if (-not $nextNode -or $nextNode -eq "") {
    # All nodes terminal → loop complete
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    [Console]::Error.WriteLine("[PGF-Loop] All nodes terminal. Loop complete.")
    exit 0
}

# ─── 7.1 Track retry_count (prevent infinite loops) ───
$maxRetryPolicy = if ($policyRaw -and $policyRaw.max_retry) { [int]$policyRaw.max_retry } else { 3 }

# Initialize retry_counts (create empty object if missing)
if (-not $state.retry_counts) {
    $state | Add-Member -NotePropertyName "retry_counts" -NotePropertyValue @{} -Force
}

if ($nextNode -eq $currentNode) {
    # Same node re-selected → increment retry_count
    $retryCount = if ($state.retry_counts.$nextNode) { [int]$state.retry_counts.$nextNode + 1 } else { 1 }
    $state.retry_counts.$nextNode = $retryCount

    if ($retryCount -gt $maxRetryPolicy) {
        # max_retry exceeded → mark as blocked
        $nodeStatus = $status.nodes.$nextNode
        if ($nodeStatus) {
            $nodeStatus.status = "blocked"
            $nodeStatus | Add-Member -NotePropertyName "blocker" -NotePropertyValue "max_retry ($maxRetryPolicy) exceeded after $retryCount attempts" -Force
            $status | ConvertTo-Json -Depth 10 | Set-Content $statusPath -Encoding UTF8
        }
        [Console]::Error.WriteLine("[PGF-Loop] Node '$nextNode' exceeded max_retry ($maxRetryPolicy). Marked as blocked.")

        # Check on_blocked policy
        $onBlocked = if ($policyRaw -and $policyRaw.on_blocked) { $policyRaw.on_blocked } else { "skip_and_continue" }
        if ($onBlocked -eq "halt") {
            Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
            [Console]::Error.WriteLine("[PGF-Loop] on_blocked=halt. Loop terminated.")
            exit 0
        }

        # skip_and_continue → re-select next node
        $nextNode = & "$scriptDir/select-next-node.ps1" -WorkplanPath $workplanPath -StatusPath $statusPath
        if (-not $nextNode -or $nextNode -eq "") {
            Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
            [Console]::Error.WriteLine("[PGF-Loop] All nodes terminal after skip. Loop complete.")
            exit 0
        }
    }
} else {
    # New node → reset retry_count
    $state.retry_counts.$nextNode = 0
}

# ─── 8. Extract execution spec (Strategy 1: DESIGN PPR → Strategy 2: WORKPLAN inline) ───
$extractArgs = @{ NodeName = $nextNode; WorkplanPath = $workplanPath }
if ($designPath -and $designPath -ne "") {
    $extractArgs["DesignPath"] = $designPath
}
$pprBlock = & "$scriptDir/extract-ppr.ps1" @extractArgs

# ─── 9. Calculate progress ───
$doneCount = 0
$totalCount = 0
$nodes = $status.nodes.PSObject.Properties
foreach ($n in $nodes) {
    $totalCount++
    if ((ConvertTo-EnglishStatus $n.Value.status) -eq "done") { $doneCount++ }
}

# ─── 10. Construct prompt ───
$modeLabel = if ($loopMode -eq "lightweight") { " [Lightweight]" } else { "" }

$prompt = @"
[PGF-Loop]${modeLabel} Node Execution Directive

Project: $($state.project)
Current node: $nextNode
Progress: $doneCount/$totalCount nodes done
WORKPLAN: $workplanPath
"@

if ($designPath -and $designPath -ne "") {
    $prompt += "`nDESIGN: $designPath"
}
$prompt += "`nstatus.json: $statusPath`n"

if ($pprBlock -and $pprBlock.Trim() -ne "") {
    if ($loopMode -eq "lightweight") {
        $prompt += @"

## Task Spec for This Node (WORKPLAN Inline)

$pprBlock

Implement according to the intent of the above task spec.

"@
    } else {
        $prompt += @"

## PPR Implementation Spec for This Node

$pprBlock

Implement according to the intent of the above PPR. Execute AI_ prefixed functions as AI cognitive operations directly,
and implement regular functions as actual code.

"@
    }
} else {
    $prompt += @"

This is an atomic node. Read the node description from WORKPLAN and implement directly.

"@
}

$prompt += @"

## Required Post-Completion Tasks

1. Change this node's ($nextNode) status to (done) in WORKPLAN ($workplanPath)
2. Update this node to "done" in status ($statusPath) + record completed_at + recalculate summary
3. Progress report: [PGF] $nextNode (done) | N/M nodes done | next: NextNode

## On Failure
- Up to ${maxRetryPolicy} retries allowed
- On final failure, change status to (blocked) and record blocker reason
"@

# ─── 11. Update state ───
$state.iteration = $iteration + 1
$state.current_node = $nextNode
$state | ConvertTo-Json -Depth 10 | Set-Content $STATE_FILE -Encoding UTF8

# ─── 12. Return block decision ───
$result = @{
    decision      = "block"
    reason        = $prompt
    systemMessage = "[PGF-Loop]${modeLabel} iteration $($iteration + 1) | node: $nextNode | $doneCount/$totalCount done"
} | ConvertTo-Json -Compress

Write-Output $result
