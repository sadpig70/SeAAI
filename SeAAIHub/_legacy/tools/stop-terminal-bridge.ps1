param(
    [string]$BridgeDir = "D:\SeAAI\SeAAIHub\.bridge\session"
)

$logoutFlag = Join-Path $BridgeDir "logout.flag"
New-Item -ItemType File -Path $logoutFlag -Force | Out-Null
Write-Output ("[bridge-stop] logout flag created at " + $logoutFlag)
