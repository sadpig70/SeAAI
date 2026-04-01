param(
    [string]$BridgeDir = "D:\SeAAI\SeAAIHub\.bridge\session",
    [string]$AgentId = "Synerion",
    [string]$PeerAgent = "Aion",
    [string]$RoomId = "bridge-room",
    [double]$PollInterval = 1.0,
    [int]$DurationSeconds = 600
)

python D:\SeAAI\SeAAIHub\tools\terminal-hub-bridge.py `
    --hub-binary D:\SeAAI\SeAAIHub\target\debug\SeAAIHub.exe `
    --bridge-dir $BridgeDir `
    --agent-id $AgentId `
    --peer-agent $PeerAgent `
    --room-id $RoomId `
    --poll-interval $PollInterval `
    --duration-seconds $DurationSeconds
