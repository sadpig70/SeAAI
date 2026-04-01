param(
    [string]$BridgeDir = "D:\SeAAI\SeAAIHub\.bridge\smoke"
)

if (Test-Path $BridgeDir) {
    Remove-Item -Recurse -Force $BridgeDir
}

$injector = Start-Job -ScriptBlock {
    param($Dir)
    Start-Sleep -Seconds 2
    python D:\SeAAI\SeAAIHub\tools\queue-bridge-message.py `
        --bridge-dir $Dir `
        --sender Aion `
        --to Synerion `
        --body "AionMessage // hello Synerion (designing)"

    Start-Sleep -Seconds 1

    python D:\SeAAI\SeAAIHub\tools\queue-bridge-message.py `
        --bridge-dir $Dir `
        --sender Synerion `
        --to Aion `
        --body "SynerionReply // ack Aion (designing)"

    Start-Sleep -Seconds 2

    New-Item -ItemType File -Path (Join-Path $Dir "logout.flag") -Force | Out-Null
} -ArgumentList $BridgeDir

python D:\SeAAI\SeAAIHub\tools\terminal-hub-bridge.py `
    --bridge-dir $BridgeDir `
    --room-id smoke-bridge `
    --poll-interval 0.5 `
    --duration-seconds 12

Wait-Job $injector | Out-Null
Receive-Job $injector | Out-Null
Remove-Job $injector

Write-Output "`n=== STATE ==="
Get-Content (Join-Path $BridgeDir "bridge-state.json")
