[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$StatusPath = Join-Path $ProjectRoot "PROJECT_STATUS.md"
$WorkspaceDir = Join-Path $ProjectRoot "_workspace"

function Read-Utf8Text([string]$Path) {
    if (-not (Test-Path $Path)) { return "" }
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8Bom([string]$Path, [string]$Content) {
    $enc = [System.Text.UTF8Encoding]::new($true)
    [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Get-ManualBlock([string]$Content, [string]$Name, [string]$DefaultValue) {
    $pattern = "<!-- MANUAL:${Name}:START -->([\s\S]*?)<!-- MANUAL:${Name}:END -->"
    $match = [regex]::Match($Content, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }
    return $DefaultValue.Trim()
}

function Rel([string]$Path) {
    $root = $ProjectRoot.TrimEnd("\") + "\"
    if ($Path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $Path.Substring($root.Length).Replace("\", "/")
    }
    return $Path.Replace("\", "/")
}

function Load-JsonSafe([string]$Path) {
    if (-not (Test-Path $Path)) { return $null }
    try {
        return Get-Content -Raw $Path | ConvertFrom-Json
    } catch {
        return $null
    }
}

$Existing = Read-Utf8Text $StatusPath

$DefaultActiveThreads = @"
- continuity 시스템이 설치됐고 다음 세션부터 PROJECT_STATUS.md를 canonical state로 사용한다.
- Hub 첫 실시간 실험은 broadcast only + session filter + MockHub 분리 조건이 필요하다.
- persona v1은 생성됐지만 ADP 루프 주입 규칙은 아직 없다.
"@

$DefaultNextActions = @"
- SharedSpace 기준 member_registry.md와 Phase A readiness checklist를 공용 문서로 만든다.
- Hub 세션에 session_token 또는 start_ts 기준 필터를 넣는다.
- Synerion persona seed를 ADP 또는 continuity 시작 흐름에 주입하는 규칙을 만든다.
"@

$DefaultOpenRisks = @"
- room membership 검증 없이 direct reply를 보내면 Hub 예외가 날 수 있다.
- agent inbox에는 이전 세션 메시지가 섞여 들어올 수 있다.
- MockHub 트래픽이 실제 멤버 상호작용 분석을 흐릴 수 있다.
"@

$ActiveThreads = Get-ManualBlock $Existing "ActiveThreads" $DefaultActiveThreads
$NextActions = Get-ManualBlock $Existing "NextActions" $DefaultNextActions
$OpenRisks = Get-ManualBlock $Existing "OpenRisks" $DefaultOpenRisks

$TopDirs = Get-ChildItem $ProjectRoot -Directory |
    Sort-Object Name |
    ForEach-Object { "- $($_.Name)/" }

$RecentFiles = Get-ChildItem $ProjectRoot -Recurse -File |
    Where-Object { $_.FullName -notmatch "\\__pycache__\\" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 15 |
    ForEach-Object { "- $(Rel $_.FullName) ($($_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")))" }

$WorkspaceReports = @()
if (Test-Path $WorkspaceDir) {
    $WorkspaceReports = Get-ChildItem $WorkspaceDir -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 10 |
        ForEach-Object { "- $(Rel $_.FullName) ($($_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")))" }
}

$StatusSummaries = Get-ChildItem $ProjectRoot -Recurse -File -Filter "status-*.json" |
    ForEach-Object {
        $json = Load-JsonSafe $_.FullName
        if ($null -ne $json) {
            $summary = $json.summary
            "- $(Rel $_.FullName) :: done=$($summary.done), in_progress=$($summary.in_progress), designing=$($summary.designing), blocked=$($summary.blocked)"
        }
    }

$HubSummaryText = "- 없음"
$HubSummaryPath = Join-Path $WorkspaceDir "synerion-hub-adp-summary.json"
$HubSummary = Load-JsonSafe $HubSummaryPath
if ($null -ne $HubSummary) {
    $HubSummaryText = @"
- duration_sec: $($HubSummary.duration_sec)
- sent: $($HubSummary.sent)
- seen: $($HubSummary.seen)
- interesting: $($HubSummary.interesting)
- source: $(Rel $HubSummaryPath)
"@.Trim()
}

$UpdatedAt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
$TopDirsText = if ($TopDirs) { $TopDirs -join "`n" } else { "- 없음" }
$RecentFilesText = if ($RecentFiles) { $RecentFiles -join "`n" } else { "- 없음" }
$WorkspaceReportsText = if ($WorkspaceReports) { $WorkspaceReports -join "`n" } else { "- 없음" }
$StatusSummariesText = if ($StatusSummaries) { $StatusSummaries -join "`n" } else { "- 없음" }

$Content = @"
# PROJECT_STATUS

업데이트 시각: $UpdatedAt
워크스페이스: .

## 프로젝트 개요

Synerion은 SeAAI 내부에서 설계, 구현, 통합, 검증을 담당하는 동료 AI다.
이 워크스페이스는 세션 연속성 유지를 위해 PROJECT_STATUS.md를 canonical state로 사용한다.
핵심 코어 문서, persona 문서, .pgf 상태 파일, _workspace 보고서를 함께 읽어 다음 세션에서 복원한다.

## 우선 읽을 문서

- AGENTS.md
- Synerion_Core/Synerion.md
- Synerion_Core/Synerion_persona_v1.md
- Synerion_Core/Synerion_Operating_Core.md
- SESSION_CONTINUITY.md
- .pgf/status-*.json

## 디렉터리 구조

$TopDirsText

## 문서 기반 작업 방식

- 시작 규칙: AGENTS.md -> Synerion_Core 문서군 -> PROJECT_STATUS.md
- durable 상태: .pgf/WORKPLAN-* 및 .pgf/status-*.json
- 실행 로그와 보고서: _workspace/
- continuity 원칙: SESSION_CONTINUITY.md

## 최신 durable 상태

$StatusSummariesText

## 최근 변경 파일

$RecentFilesText

## 최근 _workspace 자산

$WorkspaceReportsText

## 최근 Hub/ADP 실험 요약

$HubSummaryText

## 현재 진행 중
<!-- MANUAL:ActiveThreads:START -->
$ActiveThreads
<!-- MANUAL:ActiveThreads:END -->

## 다음 액션
<!-- MANUAL:NextActions:START -->
$NextActions
<!-- MANUAL:NextActions:END -->

## 오픈 리스크
<!-- MANUAL:OpenRisks:START -->
$OpenRisks
<!-- MANUAL:OpenRisks:END -->

## 아키텍처 결정

- continuity canonical state는 PROJECT_STATUS.md다.
- 세션 시작 시 persona 문서까지 읽어 Synerion의 주체성과 판단 톤을 복원한다.
- 장기 추적이 필요한 작업은 .pgf에 상태를 남긴다.
- Hub 첫 실험은 direct reply보다 broadcast only가 안전하다.

## 재개 체크리스트

1. AGENTS.md를 읽는다.
2. Synerion_Core 문서 3개를 읽는다.
3. PROJECT_STATUS.md에서 active thread, next action, open risk를 복원한다.
4. 필요하면 .pgf/status-*.json과 최신 _workspace 보고서를 본다.
"@

Write-Utf8Bom $StatusPath $Content

$ExportScript = Join-Path $PSScriptRoot "export-scs-state.ps1"
if (Test-Path $ExportScript) {
    powershell -ExecutionPolicy Bypass -File $ExportScript | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "export-scs-state.ps1 failed with exit code $LASTEXITCODE"
    }
}

$BootstrapScript = Join-Path $PSScriptRoot "build-adp-bootstrap.ps1"
if (Test-Path $BootstrapScript) {
    powershell -ExecutionPolicy Bypass -File $BootstrapScript | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "build-adp-bootstrap.ps1 failed with exit code $LASTEXITCODE"
    }
}

Write-Output $StatusPath
