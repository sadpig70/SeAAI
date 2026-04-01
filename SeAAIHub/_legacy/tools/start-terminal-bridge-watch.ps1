param(
    [string]$BridgeDir = "D:\SeAAI\SeAAIHub\.bridge\session",
    [string]$AgentId = "Synerion",
    [string]$PeerAgent = "Aion",
    [string]$RoomId = "bridge-room",
    [double]$PollInterval = 1.0,
    [int]$DurationSeconds = 600
)

$stdoutLog = Join-Path $BridgeDir "bridge-stdout.log"
$stderrLog = Join-Path $BridgeDir "bridge-stderr.log"

New-Item -ItemType Directory -Force $BridgeDir | Out-Null

if (Test-Path $stdoutLog) {
    Remove-Item -Force $stdoutLog
}

if (Test-Path $stderrLog) {
    Remove-Item -Force $stderrLog
}

$proc = Start-Process `
    -FilePath python `
    -ArgumentList @(
        "D:\SeAAI\SeAAIHub\tools\terminal-hub-bridge.py",
        "--hub-binary", "D:\SeAAI\SeAAIHub\target\debug\SeAAIHub.exe",
        "--bridge-dir", $BridgeDir,
        "--agent-id", $AgentId,
        "--peer-agent", $PeerAgent,
        "--room-id", $RoomId,
        "--poll-interval", $PollInterval,
        "--duration-seconds", $DurationSeconds
    ) `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

Write-Output ("[bridge-watch] pid=" + $proc.Id)
Write-Output ("[bridge-watch] bridge_dir=" + $BridgeDir)
Write-Output ("[bridge-watch] stdout=" + $stdoutLog)
Write-Output ("[bridge-watch] stderr=" + $stderrLog)
Write-Output "[bridge-watch] tailing bridge stdout..."

$offset = 0

while (-not $proc.HasExited) {
    if (Test-Path $stdoutLog) {
        $text = Get-Content $stdoutLog -Raw
        if ($offset -gt $text.Length) {
            $offset = 0
        }
        if ($text.Length -gt $offset) {
            $chunk = $text.Substring($offset)
            Write-Output $chunk.TrimEnd("`r", "`n")
            $offset = $text.Length
        }
    }

    Start-Sleep -Milliseconds 300
}

if (Test-Path $stdoutLog) {
    $text = Get-Content $stdoutLog -Raw
    if ($offset -gt $text.Length) {
        $offset = 0
    }
    if ($text.Length -gt $offset) {
        $chunk = $text.Substring($offset)
        Write-Output $chunk.TrimEnd("`r", "`n")
    }
}

if (Test-Path $stderrLog) {
    $stderrText = Get-Content $stderrLog -Raw
    if ($stderrText -and $stderrText.Trim()) {
        Write-Output "`n[bridge-watch] stderr:"
        Write-Output $stderrText.TrimEnd("`r", "`n")
    }
}
