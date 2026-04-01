# PGF-Loop: Select Next Executable Node
# Parses node list/dependencies from WORKPLAN-{Name}.md, checks status in status-{Name}.json,
# and returns the next executable node whose dependencies are resolved.
#
# Arguments: -WorkplanPath, -StatusPath
# Output: Node name (empty string if none)

param(
    [Parameter(Mandatory=$true)][string]$WorkplanPath,
    [Parameter(Mandatory=$true)][string]$StatusPath
)

$ErrorActionPreference = "Stop"

# ─── 0. Status normalization (Korean → English backward compatibility) ───
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

# ─── 1. Load files ───
if (-not (Test-Path $WorkplanPath) -or -not (Test-Path $StatusPath)) {
    Write-Output ""
    exit 0
}

$workplanText = Get-Content $WorkplanPath -Raw -Encoding UTF8
$status = Get-Content $StatusPath -Raw -Encoding UTF8 | ConvertFrom-Json

# ─── 2. Parse nodes from WORKPLAN ───
# Pattern: indentation + NodeName // description (status) [@dep:X,Y]
# Exclude [parallel], [/parallel], POLICY blocks, blank lines, comments

$nodes = @()
$lineNum = 0

foreach ($line in ($workplanText -split "`n")) {
    $lineNum++
    $trimmed = $line.TrimEnd()

    # Skip code blocks, POLICY, parallel markers, blank lines
    if ($trimmed -match '^\s*```' -or
        $trimmed -match '^\s*POLICY\s*=' -or
        $trimmed -match '^\s*\[/?parallel\]' -or
        $trimmed -match '^\s*#' -or
        $trimmed -match '^\s*"' -or
        $trimmed -match '^\s*\}' -or
        $trimmed -match '^\s*\{' -or
        $trimmed.Trim() -eq "") {
        continue
    }

    # Node pattern matching: NodeName // description (status) [@dep:...]
    if ($trimmed -match '^\s*(\w+)\s*//\s*(.+?)\s*\(([^)]+)\)(.*)$') {
        $nodeName = $Matches[1]
        $nodeDesc = $Matches[2]
        $nodeStatus = $Matches[3]
        $rest = $Matches[4]

        # Extract @dep:
        $deps = @()
        if ($rest -match '@dep:([^\s\]]+)') {
            $deps = $Matches[1] -split ','
        }

        $nodes += @{
            name        = $nodeName
            description = $nodeDesc
            status      = $nodeStatus
            deps        = $deps
            line        = $lineNum
        }
    }
}

if ($nodes.Count -eq 0) {
    Write-Output ""
    exit 0
}

# ─── 3. Check status via status.json ───
$statusNodes = @{}
if ($status.nodes) {
    foreach ($prop in $status.nodes.PSObject.Properties) {
        $statusNodes[$prop.Name] = $prop.Value.status
    }
}

# ─── 4. Prioritize in-progress nodes ───
foreach ($n in $nodes) {
    $s = ConvertTo-EnglishStatus $(if ($statusNodes.ContainsKey($n.name)) { $statusNodes[$n.name] } else { $n.status })
    if ($s -eq "in_progress") {
        Write-Output $n.name
        exit 0
    }
}

# ─── 5. Select pending node with resolved dependencies ───
foreach ($n in $nodes) {
    $s = ConvertTo-EnglishStatus $(if ($statusNodes.ContainsKey($n.name)) { $statusNodes[$n.name] } else { $n.status })
    if ($s -ne "pending") { continue }

    # Check dependencies
    $allDepsDone = $true
    foreach ($dep in $n.deps) {
        $depTrimmed = $dep.Trim()
        if ($depTrimmed -eq "") { continue }
        $depStatus = ConvertTo-EnglishStatus $(if ($statusNodes.ContainsKey($depTrimmed)) { $statusNodes[$depTrimmed] } else { "pending" })
        if ($depStatus -ne "done") {
            $allDepsDone = $false
            break
        }
    }

    if ($allDepsDone) {
        Write-Output $n.name
        exit 0
    }
}

# ─── 6. No candidates ───
Write-Output ""
