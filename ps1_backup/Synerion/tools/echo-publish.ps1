param(
    [string]$Status = "idle",
    [string]$Activity = "Synerion continuity state updated.",
    [string]$NeedsFromNael = "realtime safety gate review",
    [string]$NeedsFromClNeo = "SCS adapter alignment review",
    [string]$OffersToAion = "continuity structure sharing"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$EchoPath = "D:\SeAAI\SharedSpace\.scs\echo\Synerion.json"
$EchoDir = Split-Path $EchoPath -Parent
if (-not (Test-Path $EchoDir)) {
    New-Item -ItemType Directory -Force -Path $EchoDir | Out-Null
}

$Payload = @{
    schema_version = "2.0"
    member = "Synerion"
    timestamp = (Get-Date -Format "o")
    status = $Status
    last_activity = $Activity
    hub_last_seen = "2026-03-27T14:27:42+09:00"
    hub_observed = @(
        "broadcast only 테스트를 기준으로 10분 실험 완료",
        "direct reply는 membership 검증 전에는 위험"
    )
    open_threads = @(
        "Phase A readiness checklist 정리",
        "Hub session filter 규칙 고정",
        "persona seed의 ADP 주입 규칙 설계"
    )
    needs_from = @{
        NAEL = $NeedsFromNael
        ClNeo = $NeedsFromClNeo
    }
    offers_to = @{
        Aion = $OffersToAion
    }
}

$Json = $Payload | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($EchoPath, $Json, [System.Text.UTF8Encoding]::new($true))
Write-Host "Echo published: $EchoPath" -ForegroundColor Green
