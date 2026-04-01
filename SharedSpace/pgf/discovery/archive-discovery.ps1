<#
.SYNOPSIS
    Copies Discovery Engine artifacts to a date-based archive directory.

.DESCRIPTION
    Copies the 6 artifact files (+ creation_log.md) from the .pgf/discovery/
    directory into an archive/YYYY-MM-DD/ subdirectory.
    If the same date folder already exists, appends a sequence number (_2, _3, etc.).
    Original files are preserved.

.PARAMETER DiscoveryDir
    Directory where artifacts are located (default: .pgf/discovery)

.PARAMETER ProjectRoot
    Project root directory (default: current directory)

.EXAMPLE
    .\archive-discovery.ps1
    .\archive-discovery.ps1 -ProjectRoot "D:\MyProject"
    .\archive-discovery.ps1 -DiscoveryDir ".pgf/discovery" -ProjectRoot "D:\MyProject"
#>

param(
    [string]$DiscoveryDir = ".pgf/discovery",
    [string]$ProjectRoot  = (Get-Location).Path
)

# Resolve full path
$discoveryPath = Join-Path $ProjectRoot $DiscoveryDir

# Validate discovery directory
if (-not (Test-Path $discoveryPath)) {
    Write-Error "[Discovery Archive] Directory not found: $discoveryPath"
    exit 1
}

# 1. Archive directory - date-based
$today       = Get-Date -Format "yyyy-MM-dd"
$archiveBase = Join-Path $discoveryPath "archive"
$archiveDir  = Join-Path $archiveBase $today

# 2. Duplicate handling
if (Test-Path $archiveDir) {
    $n = 2
    while (Test-Path "${archiveDir}_$n") { $n++ }
    $archiveDir = "${archiveDir}_$n"
}

# 3. Create archive directory
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null

# 4. Copy files
$files = @(
    "news.md",
    "industry_trend.md",
    "insight.md",
    "system_design.md",
    "candidate_idea.md",
    "final_idea.md",
    "creation_log.md"
)

$copied = 0
foreach ($f in $files) {
    $src = Join-Path $discoveryPath $f
    if (Test-Path $src) {
        Copy-Item $src -Destination $archiveDir
        $copied++
    }
}

# 5. Result output
if ($copied -eq 0) {
    Write-Warning "[Discovery Archive] No files found to archive in: $discoveryPath"
    exit 1
} else {
    Write-Output "[Discovery Archive] $copied files -> $archiveDir"
}
