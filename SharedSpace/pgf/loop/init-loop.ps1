# PGF-Loop: Loop Initialization
# Receives WORKPLAN-{Name}.md path and creates the loop state file.
# DESIGN-{Name}.md is optional — supports Lightweight mode (WORKPLAN only).
#
# Arguments: -WorkplanPath (required), -DesignPath (optional), -MaxIterations (default 0=unlimited)
# Output: Initialization result message

param(
    [Parameter(Mandatory=$true)][string]$WorkplanPath,
    [string]$DesignPath = "",
    [int]$MaxIterations = 0
)

$ErrorActionPreference = "Stop"

$STATE_FILE = ".claude/pgf-loop-state.json"

# ─── 1. Verify file existence ───
if (-not (Test-Path $WorkplanPath)) {
    Write-Error "[PGF-Loop] WORKPLAN not found: $WorkplanPath"
    exit 1
}

# DESIGN is optional — present = Standard mode, absent = Lightweight mode
$mode = "lightweight"
if ($DesignPath -and $DesignPath -ne "") {
    if (Test-Path $DesignPath) {
        $mode = "standard"
    } else {
        Write-Warning "[PGF-Loop] DESIGN not found: $DesignPath — switching to lightweight mode."
        $DesignPath = ""
    }
}

# ─── 2. Check for existing loop ───
if (Test-Path $STATE_FILE) {
    Write-Error "[PGF-Loop] Loop already active. Use /PGF loop cancel to stop it first."
    exit 1
}

# ─── 3. Ensure .claude directory exists ───
$claudeDir = Split-Path $STATE_FILE -Parent
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}

# ─── 4. Determine status.json path ───
# Extract Name from WORKPLAN filename: WORKPLAN-{Name}.md → Name
$wpFileName = [System.IO.Path]::GetFileNameWithoutExtension($WorkplanPath)
if ($wpFileName -match '^WORKPLAN-(.+)$') {
    $wpName = $Matches[1]
} else {
    $wpName = $wpFileName
}
$statusPath = Join-Path (Split-Path $WorkplanPath -Parent) "status-$wpName.json"

# ─── 5. Extract POLICY from WORKPLAN ───
$workplanText = Get-Content $WorkplanPath -Raw -Encoding UTF8
$policy = @{
    max_retry           = 3
    on_blocked          = "skip_and_continue"
    design_modify_scope = @("impl", "internal_interface")
    completion          = "all_done_or_blocked"
}

# Attempt POLICY block parsing
if ($workplanText -match 'POLICY\s*=\s*\{([^}]+)\}') {
    $policyBlock = $Matches[1]
    if ($policyBlock -match '"max_retry"\s*:\s*(\d+)') { $policy.max_retry = [int]$Matches[1] }
    if ($policyBlock -match '"on_blocked"\s*:\s*"([^"]+)"') { $policy.on_blocked = $Matches[1] }
    if ($policyBlock -match '"completion"\s*:\s*"([^"]+)"') { $policy.completion = $Matches[1] }
}

# ─── 6. Extract project name ───
$projectName = "unknown"
if ($workplanText -match '# (.+?) Work Plan') {
    $projectName = $Matches[1].Trim()
} elseif ($workplanText -match '# (.+?) Design') {
    $projectName = $Matches[1].Trim()
}

# ─── 7. Session ID ───
$sessionId = if ($env:CLAUDE_CODE_SESSION_ID) { $env:CLAUDE_CODE_SESSION_ID } else { [guid]::NewGuid().ToString() }

# ─── 8. Create state file ───
$loopState = @{
    active          = $true
    session_id      = $sessionId
    iteration       = 1
    max_iterations  = $MaxIterations
    workplan_path   = $WorkplanPath
    design_path     = $DesignPath
    status_path     = $statusPath
    project         = $projectName
    mode            = $mode
    policy          = $policy
    current_node    = $null
    retry_counts    = @{}
    started_at      = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
} | ConvertTo-Json -Depth 10

$loopState | Set-Content $STATE_FILE -Encoding UTF8

# ─── 9. Configure hooks.json ───
$hooksFile = ".claude/hooks.json"
$skillDir = $PSScriptRoot

$hookEntry = @{
    hooks = @(
        @{
            type    = "command"
            command = "powershell -ExecutionPolicy Bypass -File `"$skillDir/stop-hook.ps1`""
            timeout = 15
        }
    )
}

if (Test-Path $hooksFile) {
    try {
        $hooks = Get-Content $hooksFile -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $hooks = @{ hooks = @{} }
    }
} else {
    $hooks = @{ hooks = @{} }
}

# Add to Stop hook array (prevent duplicates)
$stopHooks = @()
if ($hooks.hooks.Stop) {
    $stopHooks = @($hooks.hooks.Stop)
}

$alreadyExists = $false
foreach ($sh in $stopHooks) {
    if ($sh.hooks) {
        foreach ($h in $sh.hooks) {
            if ($h.command -and $h.command -match "PGF.*stop-hook") {
                $alreadyExists = $true
                break
            }
        }
    }
}

if (-not $alreadyExists) {
    $stopHooks += $hookEntry

    # Construct hooks object
    $hooksObj = @{ hooks = @{ Stop = $stopHooks } }

    # Preserve other existing hooks
    if ($hooks.hooks.PSObject) {
        foreach ($prop in $hooks.hooks.PSObject.Properties) {
            if ($prop.Name -ne "Stop") {
                $hooksObj.hooks[$prop.Name] = $prop.Value
            }
        }
    }

    $hooksObj | ConvertTo-Json -Depth 10 | Set-Content $hooksFile -Encoding UTF8
}

# ─── 10. Output results ───
Write-Output "[PGF-Loop] Initialized successfully."
Write-Output "  Project:        $projectName"
Write-Output "  Mode:           $mode$(if ($mode -eq 'lightweight') { ' (WORKPLAN-only, no DESIGN-{Name}.md)' } else { '' })"
Write-Output "  WORKPLAN:       $WorkplanPath"
if ($DesignPath) {
    Write-Output "  DESIGN:         $DesignPath"
}
Write-Output "  status:         $statusPath"
Write-Output "  Max iterations: $(if ($MaxIterations -eq 0) { 'unlimited' } else { $MaxIterations })"
Write-Output "  Policy:         max_retry=$($policy.max_retry), on_blocked=$($policy.on_blocked)"
Write-Output ""
Write-Output "Loop will start on next session end. Execute the first node now."
