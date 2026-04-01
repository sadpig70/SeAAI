param(
    [double]$IntervalSeconds = 1.0,
    [int]$Count = 0,
    [string]$AgentId = "Synerion",
    [string]$RoomId = "lobby",
    [string]$Message = "heartbeat",
    [ValidateSet("json", "text")]
    [string]$Format = "json"
)

if ($IntervalSeconds -le 0) {
    throw "IntervalSeconds must be greater than 0."
}

if ($Count -lt 0) {
    throw "Count must be 0 or greater. Use 0 for infinite loop."
}

$sessionId = "heartbeat-" + (Get-Date -Format "yyyyMMdd-HHmmss")
$sequence = 0
$sleepMs = [int]($IntervalSeconds * 1000)

while ($true) {
    $sequence += 1
    $now = [DateTimeOffset]::Now

    $payload = [ordered]@{
        kind       = "heartbeat"
        session_id = $sessionId
        sequence   = $sequence
        agent_id   = $AgentId
        room_id    = $RoomId
        message    = $Message
        ts         = $now.ToString("o")
        unix_ts    = $now.ToUnixTimeSeconds()
    }

    if ($Format -eq "json") {
        $payload | ConvertTo-Json -Compress
    } else {
        "[heartbeat] seq=$sequence agent=$AgentId room=$RoomId ts=$($payload.ts) msg=$Message"
    }

    if ($Count -gt 0 -and $sequence -ge $Count) {
        break
    }

    Start-Sleep -Milliseconds $sleepMs
}
