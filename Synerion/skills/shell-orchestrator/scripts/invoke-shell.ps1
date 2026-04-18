param(
    [ValidateSet('auto', 'pwsh7', 'powershell51', 'cmd', 'bash')]
    [string]$Shell = 'auto',

    [string]$Command,

    [string]$ScriptPath,

    [string]$WorkingDirectory,

    [string[]]$Env,

    [int]$TimeoutSec = 0,

    [switch]$CaptureJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Command) -and [string]::IsNullOrWhiteSpace($ScriptPath)) {
    throw 'Specify -Command or -ScriptPath.'
}

if (-not [string]::IsNullOrWhiteSpace($Command) -and -not [string]::IsNullOrWhiteSpace($ScriptPath)) {
    throw 'Use either -Command or -ScriptPath, not both.'
}

function Resolve-ShellPath {
    param(
        [string]$RequestedShell,
        [string]$ResolvedScriptPath,
        [string]$InlineCommand
    )

    $pwsh7 = 'D:\Tools\PS7\7\pwsh.exe'
    $powershell51 = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
    $cmdPath = if ($env:ComSpec) { $env:ComSpec } else { 'C:\Windows\System32\cmd.exe' }
    $bashPath = (Get-Command bash.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)

    if ($RequestedShell -eq 'auto') {
        if ($ResolvedScriptPath) {
            switch ([IO.Path]::GetExtension($ResolvedScriptPath).ToLowerInvariant()) {
                '.ps1' { $RequestedShell = if (Test-Path -LiteralPath $pwsh7) { 'pwsh7' } else { 'powershell51' } }
                '.cmd' { $RequestedShell = 'cmd' }
                '.bat' { $RequestedShell = 'cmd' }
                '.sh'  { $RequestedShell = 'bash' }
                default { $RequestedShell = 'powershell51' }
            }
        } elseif ($InlineCommand -match '^\s*cmd\s+/c\b') {
            $RequestedShell = 'cmd'
        } elseif ($InlineCommand -match '(^|\s)(grep|awk|sed|bash)\b' -and $bashPath) {
            $RequestedShell = 'bash'
        } else {
            $RequestedShell = 'powershell51'
        }
    }

    switch ($RequestedShell) {
        'pwsh7' {
            if (-not (Test-Path -LiteralPath $pwsh7)) {
                throw "PowerShell 7 executable not found at $pwsh7"
            }
            return @{ Shell = 'pwsh7'; Path = $pwsh7 }
        }
        'powershell51' {
            if (-not (Test-Path -LiteralPath $powershell51)) {
                throw "Windows PowerShell executable not found at $powershell51"
            }
            return @{ Shell = 'powershell51'; Path = $powershell51 }
        }
        'cmd' {
            return @{ Shell = 'cmd'; Path = $cmdPath }
        }
        'bash' {
            if (-not $bashPath) {
                throw 'bash.exe not found on PATH.'
            }
            return @{ Shell = 'bash'; Path = $bashPath }
        }
        default {
            throw "Unsupported shell: $RequestedShell"
        }
    }
}

function Get-ShellArguments {
    param(
        [string]$ResolvedShell,
        [string]$InlineCommand,
        [string]$ResolvedScriptPath
    )

    switch ($ResolvedShell) {
        'pwsh7' {
            if ($ResolvedScriptPath) {
                return @('-NoLogo', '-NoProfile', '-File', $ResolvedScriptPath)
            }
            return @('-NoLogo', '-NoProfile', '-Command', $InlineCommand)
        }
        'powershell51' {
            if ($ResolvedScriptPath) {
                return @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $ResolvedScriptPath)
            }
            return @('-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $InlineCommand)
        }
        'cmd' {
            if ($ResolvedScriptPath) {
                return @('/d', '/c', "`"$ResolvedScriptPath`"")
            }
            return @('/d', '/c', $InlineCommand)
        }
        'bash' {
            if ($ResolvedScriptPath) {
                return @($ResolvedScriptPath)
            }
            return @('-lc', $InlineCommand)
        }
    }
}

function New-ProcessInfo {
    param(
        [string]$ExecutablePath,
        [string[]]$ArgumentList,
        [string]$ResolvedShell,
        [string]$ResolvedWorkingDirectory,
        [string[]]$EnvPairs
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $ExecutablePath
    foreach ($arg in $ArgumentList) {
        [void]$psi.ArgumentList.Add($arg)
    }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
    $psi.WorkingDirectory = $ResolvedWorkingDirectory

    foreach ($entry in $EnvPairs) {
        if ($entry -notmatch '=') {
            throw "Invalid -Env entry: $entry"
        }
        $name, $value = $entry -split '=', 2
        $psi.Environment[$name] = $value
    }

    foreach ($pair in @(
        @{ Name = 'SystemRoot'; Value = 'C:\Windows' },
        @{ Name = 'windir'; Value = 'C:\Windows' },
        @{ Name = 'ComSpec'; Value = 'C:\Windows\System32\cmd.exe' }
    )) {
        if (-not $psi.Environment.ContainsKey($pair.Name) -or [string]::IsNullOrWhiteSpace($psi.Environment[$pair.Name])) {
            $psi.Environment[$pair.Name] = $pair.Value
        }
    }

    if ($ResolvedShell -in @('pwsh7', 'powershell51')) {
        if (-not $psi.Environment.ContainsKey('PYTHONIOENCODING') -or [string]::IsNullOrWhiteSpace($psi.Environment['PYTHONIOENCODING'])) {
            $psi.Environment['PYTHONIOENCODING'] = 'utf-8'
        }
    }

    return $psi
}

$resolvedScriptPath = if ($ScriptPath) {
    (Resolve-Path -LiteralPath $ScriptPath).Path
} else {
    $null
}

$resolvedWorkingDirectory = if ($WorkingDirectory) {
    (Resolve-Path -LiteralPath $WorkingDirectory).Path
} else {
    (Get-Location).Path
}

$shellInfo = Resolve-ShellPath -RequestedShell $Shell -ResolvedScriptPath $resolvedScriptPath -InlineCommand $Command
$arguments = Get-ShellArguments -ResolvedShell $shellInfo.Shell -InlineCommand $Command -ResolvedScriptPath $resolvedScriptPath
$processInfo = New-ProcessInfo -ExecutablePath $shellInfo.Path -ArgumentList $arguments -ResolvedShell $shellInfo.Shell -ResolvedWorkingDirectory $resolvedWorkingDirectory -EnvPairs $Env

$process = [System.Diagnostics.Process]::new()
$process.StartInfo = $processInfo

if (-not $process.Start()) {
    throw "Failed to start $($shellInfo.Path)"
}

$stdoutTask = $process.StandardOutput.ReadToEndAsync()
$stderrTask = $process.StandardError.ReadToEndAsync()

if ($TimeoutSec -gt 0) {
    if (-not $process.WaitForExit($TimeoutSec * 1000)) {
        try {
            $process.Kill($true)
        } catch {
        }
        throw "Process timed out after ${TimeoutSec}s."
    }
} else {
    $process.WaitForExit()
}

$stdoutTask.Wait()
$stderrTask.Wait()

$stdout = $stdoutTask.Result
$stderr = $stderrTask.Result
$exitCode = $process.ExitCode

if ($CaptureJson) {
    [pscustomobject]@{
        shell = $shellInfo.Shell
        command = if ($resolvedScriptPath) { $resolvedScriptPath } else { $Command }
        working_directory = $resolvedWorkingDirectory
        exit_code = $exitCode
        stdout = $stdout
        stderr = $stderr
    } | ConvertTo-Json -Depth 5
} else {
    if ($stdout) {
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        Write-Output ($stdout.TrimEnd("`r", "`n"))
    }
    if ($stderr) {
        [Console]::Error.WriteLine($stderr.TrimEnd("`r", "`n"))
    }
}

exit $exitCode
