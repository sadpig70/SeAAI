param(
  [Parameter(Mandatory = $true)][string]$Tool,
  [string]$Json,
  [string]$File
)

# JSON 파일 입력 지원
if (-not $Json -and $File) {
  if (-not (Test-Path $File)) { throw "Payload file not found: $File" }
  $Json = Get-Content -Raw -Path $File
}

if (-not $Json) { throw "Provide -Json '{...}' or -File payload.json" }

# 바이너리 경로 (ai_tool_cli 빌드 후 같은 폴더에 둔다고 가정)
$exe = Join-Path $PSScriptRoot "ai_tool_cli.exe"
if (-not (Test-Path $exe)) { throw "Not found: $exe. Build the CLI first." }

# 실행
$raw = & $exe --tool $Tool --json $Json 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Error $raw
  exit $LASTEXITCODE
}

# pretty-print
try {
  $obj = $raw | ConvertFrom-Json
  $obj | ConvertTo-Json -Depth 50
} catch {
  # 비 JSON 출력도 그대로 노출
  $raw
}
