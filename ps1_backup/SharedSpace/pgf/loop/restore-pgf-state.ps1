# PGF-Loop State Restore (SessionStart after compact)
# Purpose: Compaction 후 세션 재개 시 PGF-Loop 상태를 복구하고 컨텍스트에 주입
# Trigger: SessionStart hook (compact 이후)

$ErrorActionPreference = "Stop"

$backupFile = Join-Path $env:USERPROFILE ".claude\pgf-loop-state.backup.json"
$stateFile = Join-Path $env:USERPROFILE ".claude\pgf-loop-state.json"

# 백업 파일 존재 확인
if (-not (Test-Path $backupFile)) {
    exit 0
}

try {
    # 백업 로드
    $snapshot = Get-Content $backupFile -Raw -Encoding UTF8 | ConvertFrom-Json

    # iteration 증가
    $nextIteration = [int]$snapshot.iteration + 1

    # 현재 상태 파일 복구
    $restored = @{
        iteration     = $nextIteration
        current_node  = $snapshot.current_node
        workplan_path = $snapshot.workplan_path
        status_path   = $snapshot.status_path
        project       = $snapshot.project
        mode          = $snapshot.mode
        restored_from = $snapshot.compacted_at
    }

    $restored | ConvertTo-Json -Depth 5 | Set-Content $stateFile -Encoding UTF8

    # summary 정보 추출
    $done = 0
    $total = 0
    if ($snapshot.summary) {
        if ($snapshot.summary.done) { $done = $snapshot.summary.done }
        if ($snapshot.summary.total) { $total = $snapshot.summary.total }
    }

    # stdout으로 복구 정보 출력 → Claude 컨텍스트에 주입
    Write-Output ""
    Write-Output "[PGF-Loop] Session restored after compaction"
    Write-Output "  Project: $($snapshot.project)"
    Write-Output "  Last compacted: $($snapshot.compacted_at)"
    Write-Output "  Resuming iteration: $nextIteration"
    Write-Output "  Last node: $($snapshot.current_node)"
    Write-Output "  Progress: $done/$total nodes done"
    Write-Output "  WORKPLAN: $($snapshot.workplan_path)"
    Write-Output ""
    Write-Output "Stop Hook will automatically select the next node."

    # 백업 파일 삭제 (복구 완료, 중복 복구 방지)
    Remove-Item $backupFile -Force

} catch {
    Write-Output "[PGF-Loop] State restore failed: $($_.Exception.Message)"
    Write-Output "Manual recovery: check .claude\pgf-loop-state.backup.json"
}

exit 0
