param(
    [int]$DurationSeconds = 600,
    [double]$IntervalSeconds = 1.0,
    [string]$RoomId = "heartbeat-room",
    [string]$ReportFile = ""
)

python D:\SeAAI\SeAAIHub\tools\hub-heartbeat-session.py `
    --hub-binary D:\SeAAI\SeAAIHub\target\debug\SeAAIHub.exe `
    --duration-seconds $DurationSeconds `
    --interval-seconds $IntervalSeconds `
    --room-id $RoomId `
    --report-file $ReportFile
