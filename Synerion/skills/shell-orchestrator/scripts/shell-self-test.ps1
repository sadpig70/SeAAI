Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $root "invoke-shell.ps1"

$tests = @(
    @{
        name = "powershell51"
        args = @("-Shell", "powershell51", "-Command", '$PSVersionTable.PSVersion.ToString()', "-CaptureJson")
    },
    @{
        name = "pwsh7"
        args = @("-Shell", "pwsh7", "-Command", '$PSVersionTable.PSEdition', "-CaptureJson")
    },
    @{
        name = "cmd"
        args = @("-Shell", "cmd", "-Command", 'echo cmd-ok', "-CaptureJson")
    }
)

$results = @()
foreach ($test in $tests) {
    $json = & powershell -ExecutionPolicy Bypass -File $runner @($test.args)
    $results += [pscustomobject]@{
        name = $test.name
        result = ($json | ConvertFrom-Json)
    }
}

$results | ConvertTo-Json -Depth 6
