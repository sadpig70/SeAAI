param(
    [string]$BridgeDir = "D:\SeAAI\SeAAIHub\.bridge\session",
    [Parameter(Mandatory = $true)]
    [string]$Sender,
    [Parameter(Mandatory = $true)]
    [string[]]$To,
    [Parameter(Mandatory = $true)]
    [string]$Body,
    [string]$Intent = "design",
    [string]$MessageId = ""
)

$args = @(
    "D:\SeAAI\SeAAIHub\tools\queue-bridge-message.py",
    "--bridge-dir", $BridgeDir,
    "--sender", $Sender,
    "--intent", $Intent,
    "--body", $Body
)

foreach ($target in $To) {
    $args += @("--to", $target)
}

if ($MessageId) {
    $args += @("--message-id", $MessageId)
}

python @args
