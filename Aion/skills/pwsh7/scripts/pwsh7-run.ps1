param(
    [Parameter(Mandatory = $true)]
    [string]$Command
)

# 인코딩 강제 설정 (UTF-8)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$PwshPath = 'D:\Tools\PS7\7\pwsh.exe'

if (-not (Test-Path -LiteralPath $PwshPath)) {
    throw "PowerShell 7 executable not found at $PwshPath"
}

# pwsh.exe 호출 시 내부에서도 UTF-8로 동작하도록 유도
& $PwshPath -NoLogo -NoProfile -Command "chcp 65001 > `$null; $Command"
exit $LASTEXITCODE
