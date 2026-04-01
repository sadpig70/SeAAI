# PGF-Loop: Extract Node Execution Spec
#
# Extraction priority:
#   1. PPR def block from DESIGN-{Name}.md (Standard mode)
#   2. Inline # comments from WORKPLAN-{Name}.md (Lightweight mode)
#
# Arguments: -DesignPath (optional), -NodeName, -WorkplanPath (optional)
# Output: PPR def block or inline task spec text (empty string if none)

param(
    [string]$DesignPath = "",
    [Parameter(Mandatory=$true)][string]$NodeName,
    [string]$WorkplanPath = ""
)

$ErrorActionPreference = "Stop"

# ═══════════════════════════════════════════════════════
# Strategy 1: Extract PPR def block from DESIGN-{Name}.md (Standard mode)
# ═══════════════════════════════════════════════════════

function Extract-FromDesign([string]$Path, [string]$Name) {
    if (-not $Path -or $Path -eq "" -or -not (Test-Path $Path)) {
        return ""
    }

    $content = Get-Content $Path -Raw -Encoding UTF8
    $lines = $content -split "`n"

    # CamelCase → snake_case conversion
    $snakeName = ($Name -creplace '(?<=[a-z0-9])([A-Z])', '_$1').TrimStart('_').ToLower()

    $found = $false
    $inCodeBlock = $false
    $codeLines = @()
    $sectionLines = @()

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].TrimEnd()

        if (-not $found) {
            # Header pattern: "### [PPR] NodeName"
            if ($line -match "^\s*#{1,4}\s*\[PPR\]\s*$([regex]::Escape($Name))") {
                $found = $true
                continue
            }
            # Alternative: def snake_name( pattern
            if ($line -match "^\s*def\s+$([regex]::Escape($snakeName))\s*\(") {
                $found = $true
                $blockStart = $i
                for ($j = $i - 1; $j -ge 0; $j--) {
                    if ($lines[$j].TrimEnd() -match '^\s*```python') {
                        $blockStart = $j
                        break
                    }
                    if ($lines[$j].TrimEnd() -match '^\s*```' -or $lines[$j].TrimEnd() -match '^\s*#{1,4}\s') {
                        break
                    }
                }
                $inCodeBlock = $true
                for ($k = $blockStart; $k -lt $lines.Count; $k++) {
                    $cl = $lines[$k].TrimEnd()
                    $sectionLines += $cl
                    if ($k -gt $blockStart -and $cl -match '^\s*```\s*$') {
                        break
                    }
                }
                return ($sectionLines -join "`n")
            }
        } else {
            # Stop at next [PPR] header or ## section
            if ($line -match '^\s*#{1,4}\s*\[PPR\]' -or
                ($line -match '^\s*##\s' -and $line -notmatch '\[PPR\]')) {
                break
            }

            if ($line -match '^\s*```python') {
                $inCodeBlock = $true
                $codeLines = @()
                continue
            }
            if ($inCodeBlock -and $line -match '^\s*```\s*$') {
                $inCodeBlock = $false
                if ($codeLines.Count -gt 0) {
                    return ($codeLines -join "`n")
                }
            }
            if ($inCodeBlock) {
                $codeLines += $line
            }
        }
    }

    if ($codeLines.Count -gt 0) {
        return ($codeLines -join "`n")
    }
    return ""
}

# ═══════════════════════════════════════════════════════
# Strategy 2: Extract inline # comments from WORKPLAN-{Name}.md (Lightweight mode)
# ═══════════════════════════════════════════════════════

function Extract-FromWorkplan([string]$Path, [string]$Name) {
    if (-not $Path -or $Path -eq "" -or -not (Test-Path $Path)) {
        return ""
    }

    $content = Get-Content $Path -Raw -Encoding UTF8
    $lines = $content -split "`n"

    $found = $false
    $nodeIndent = -1
    $commentLines = @()
    $nodeDescription = ""

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].TrimEnd()

        if (-not $found) {
            # Node pattern: NodeName // description (status) ...
            if ($line -match "^(\s*)$([regex]::Escape($Name))\s*//\s*(.+?)\s*\([^)]+\)") {
                $found = $true
                $nodeIndent = $Matches[1].Length
                $nodeDescription = $Matches[2].Trim()
                continue
            }
        } else {
            # Measure current line indentation
            $currentIndent = 0
            if ($line -match '^(\s+)') {
                $currentIndent = $Matches[1].Length
            }

            $trimmed = $line.Trim()

            # Skip blank lines
            if ($trimmed -eq "") { continue }

            # Same or lower indentation non-comment line → next node, stop
            if ($currentIndent -le $nodeIndent -and $trimmed -ne "") {
                break
            }

            # Deeper indentation # comments → inline task spec
            if ($trimmed -match '^#\s*(.*)') {
                $commentLines += $Matches[1]
            }
            # Deeper indentation new node (child node) → stop
            elseif ($trimmed -match '^\w+\s*//') {
                break
            }
        }
    }

    if ($commentLines.Count -gt 0) {
        $result = "## Node: $Name"
        $result += "`nDescription: $nodeDescription"
        $result += "`n"
        $result += "`n## Task Spec (WORKPLAN Inline)"
        $result += "`n"
        foreach ($cl in $commentLines) {
            $result += "`n- $cl"
        }
        return $result
    }

    # No comments found — return node description only
    if ($nodeDescription) {
        return "## Node: $Name`nDescription: $nodeDescription"
    }

    return ""
}

# ═══════════════════════════════════════════════════════
# Main execution: Strategy 1 → Strategy 2 → empty string
# ═══════════════════════════════════════════════════════

$result = Extract-FromDesign -Path $DesignPath -Name $NodeName

if (-not $result -or $result.Trim() -eq "") {
    $result = Extract-FromWorkplan -Path $WorkplanPath -Name $NodeName
}

# ═══════════════════════════════════════════════════════
# Epigenetic PPR Enhancement (optional)
# If epigenome directory exists, query PPRInterceptor for expression modifiers
# ═══════════════════════════════════════════════════════

$epigenomeDir = Join-Path (Split-Path $DesignPath -Parent) "epigenome"
if (-not $epigenomeDir -or $DesignPath -eq "") {
    $epigenomeDir = ".pgf/epigenome"
}

if ((Test-Path $epigenomeDir) -and (Test-Path (Join-Path $epigenomeDir "__main__.py"))) {
    try {
        $epiResult = python -m epigenome dry-run --node $NodeName --session-type execute --project-root $epigenomeDir 2>$null
        if ($epiResult) {
            $epiJson = $epiResult | ConvertFrom-Json
            if ($epiJson.state -eq "active" -and $epiJson.decision.modifiers) {
                $mods = $epiJson.decision.modifiers
                $epiContext = "`n`n## Epigenetic Context`n"
                $epiContext += "Expression state: $($epiJson.state)`n"
                foreach ($key in ($mods | Get-Member -MemberType NoteProperty).Name) {
                    $epiContext += "  ${key}: $($mods.$key)`n"
                }
                if ($epiJson.decision.rationale) {
                    $epiContext += "Rationale: $($epiJson.decision.rationale)`n"
                }
                $result = $result + $epiContext
            }
        }
    } catch {
        # Epigenome failure is non-fatal — continue with base PPR
    }
}

Write-Output $result
