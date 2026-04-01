# PGF-Loop PostCompact Hook
# Purpose: Compaction 발생 시 PGF-Loop 상태를 백업하여 세션 간 상태 보존
# Trigger: PostCompact hook event (manual/auto)

$ErrorActionPreference = "Stop"

$stateFile = Join-Path $env:USERPROFILE ".claude/pgf-loop-state.json"
$backupFile = Join-Path $env:USERPROFILE ".claude/pgf-loop-state.backup.json"
$logFile = Join-Path $env:USERPROFILE ".claude/PGF-loop-compact.log"

# PGF-Loop 활성 상태 확인
if (-not (Test-Path $stateFile)) {
    exit 0  # PGF-Loop 비활성 → 정상 종료
}

try {
    # stdin에서 hook event 읽기
    $input = $null
    if (-not [Console]::IsInputRedirected) {
        $input = @{}
    } else {
        $rawInput = [Console]::In.ReadToEnd()
        if ($rawInput) {
            $input = $rawInput | ConvertFrom-Json
        } else {
            $input = @{}
        }
    }

    # 현재 상태 로드
    $state = Get-Content $stateFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # 스냅샷 생성
    $timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    $trigger = if ($input.trigger) { $input.trigger } else { "unknown" }

    $snapshot = @{
        compacted_at   = $timestamp
        trigger        = $trigger
        iteration      = $state.iteration
        current_node   = $state.current_node
        workplan_path  = $state.workplan_path
        status_path    = $state.status_path
        project        = $state.project
        mode           = $state.mode
        summary        = $state.summary
    }

    # 백업 파일 저장
    $snapshot | ConvertTo-Json -Depth 5 | Set-Content $backupFile -Encoding UTF8

    # 로그 기록
    $done = if ($state.summary.done) { $state.summary.done } else { 0 }
    $total = if ($state.summary.total) { $state.summary.total } else { 0 }
    $logEntry = "[$timestamp] PostCompact ($trigger) | iter=$($state.iteration) | node=$($state.current_node) | $done/$total done"
    Add-Content $logFile -Value $logEntry -Encoding UTF8

} catch {
    # PostCompact 실패해도 세션 중단 금지
    $errorLog = "[$((Get-Date).ToString('yyyy-MM-ddTHH:mm:ss'))] PostCompact ERROR: $($_.Exception.Message)"
    Add-Content $logFile -Value $errorLog -Encoding UTF8
}

exit 0
