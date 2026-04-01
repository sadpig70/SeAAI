param(
    [ValidateSet("auto", "powershell51", "pwsh7", "cmd", "bash")]
    [string]$Shell = "auto",

    [string]$Command,

    [string]$ScriptPath,

    [string]$WorkingDirectory,

    [int]$TimeoutSec = 0,

    [string[]]$Env = @(),

    [switch]$CaptureJson,

    [switch]$PassThru,

    [switch]$NoProfile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Quote-Arg {
    param([string]$Value)

    if ($null -eq $Value) {
        return '""'
    }

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    return '"' + ($Value -replace '"', '\"') + '"'
}

function Resolve-ShellPath {
    param([string]$Name)

    switch ($Name) {
        "powershell51" {
            $path = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
            if (-not (Test-Path -LiteralPath $path)) {
                throw "powershell51 not found at $path"
            }
            return @{ name = "powershell51"; path = $path }
        }
        "pwsh7" {
            $path = "D:\Tools\PS7\7\pwsh.exe"
            if (-not (Test-Path -LiteralPath $path)) {
                throw "pwsh7 not found at $path"
            }
            return @{ name = "pwsh7"; path = $path }
        }
        "cmd" {
            $path = if ($env:ComSpec) { $env:ComSpec } else { "cmd.exe" }
            return @{ name = "cmd"; path = $path }
        }
        "bash" {
            $cmd = Get-Command bash.exe -ErrorAction SilentlyContinue
            if (-not $cmd) {
                throw "bash.exe not found on PATH"
            }
            return @{ name = "bash"; path = $cmd.Source }
        }
        default {
            throw "Unsupported shell: $Name"
        }
    }
}

function Test-BashPattern {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $false
    }

    return $Text -match '(^|\s)(grep|awk|sed|export)\s' -or
        $Text -match '\$\([^)]+\)' -or
        $Text -match '\s&&\s' -or
        $Text -match '\s\|\s'
}

function Resolve-RequestedShell {
    if ($Shell -ne "auto") {
        return Resolve-ShellPath -Name $Shell
    }

    if (-not [string]::IsNullOrWhiteSpace($ScriptPath)) {
        $ext = [IO.Path]::GetExtension($ScriptPath).ToLowerInvariant()
        switch ($ext) {
            ".ps1" {
                if (Test-Path -LiteralPath "D:\Tools\PS7\7\pwsh.exe") {
                    return Resolve-ShellPath -Name "pwsh7"
                }
                return Resolve-ShellPath -Name "powershell51"
            }
            ".cmd" { return Resolve-ShellPath -Name "cmd" }
            ".bat" { return Resolve-ShellPath -Name "cmd" }
            ".sh" { return Resolve-ShellPath -Name "bash" }
        }
    }

    if ($Command -match '^\s*cmd(\.exe)?\s+/c\s+') {
        return Resolve-ShellPath -Name "cmd"
    }

    if (Test-BashPattern -Text $Command) {
        $bash = Get-Command bash.exe -ErrorAction SilentlyContinue
        if ($bash) {
            return Resolve-ShellPath -Name "bash"
        }
    }

    return Resolve-ShellPath -Name "powershell51"
}

function Build-PowerShellCommand {
    param(
        [string]$BaseCommand,
        [switch]$Core
    )

    $prefix = '[Console]::InputEncoding=[System.Text.UTF8Encoding]::new($false); [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $OutputEncoding=[System.Text.UTF8Encoding]::new($false);'
    if ([string]::IsNullOrWhiteSpace($BaseCommand)) {
        return $prefix
    }
    return "$prefix $BaseCommand"
}

function Build-Arguments {
    param(
        [hashtable]$ResolvedShell
    )

    switch ($ResolvedShell.name) {
        "powershell51" {
            if ($ScriptPath) {
                $parts = @("-NoLogo", "-ExecutionPolicy", "Bypass")
                if ($NoProfile) { $parts += "-NoProfile" }
                $parts += @("-File", (Quote-Arg $ScriptPath))
                return ($parts -join " ")
            }
            $parts = @("-NoLogo", "-ExecutionPolicy", "Bypass")
            if ($NoProfile) { $parts += "-NoProfile" }
            $parts += @("-Command", (Quote-Arg (Build-PowerShellCommand -BaseCommand $Command)))
            return ($parts -join " ")
        }
        "pwsh7" {
            if ($ScriptPath) {
                $parts = @("-NoLogo")
                if ($NoProfile) { $parts += "-NoProfile" }
                $parts += @("-File", (Quote-Arg $ScriptPath))
                return ($parts -join " ")
            }
            $parts = @("-NoLogo")
            if ($NoProfile) { $parts += "-NoProfile" }
            $parts += @("-Command", (Quote-Arg (Build-PowerShellCommand -BaseCommand $Command -Core)))
            return ($parts -join " ")
        }
        "cmd" {
            if ($ScriptPath) {
                return "/d /c call " + (Quote-Arg $ScriptPath)
            }
            return "/d /c chcp 65001>nul & " + $Command
        }
        "bash" {
            if ($ScriptPath) {
                return "-lc " + (Quote-Arg ("bash " + (Quote-Arg $ScriptPath)))
            }
            return "-lc " + (Quote-Arg $Command)
        }
        default {
            throw "Unsupported resolved shell: $($ResolvedShell.name)"
        }
    }
}

function Parse-EnvMap {
    $map = @{}
    foreach ($item in $Env) {
        if ([string]::IsNullOrWhiteSpace($item)) {
            continue
        }
        $parts = $item -split "=", 2
        if ($parts.Count -ne 2 -or [string]::IsNullOrWhiteSpace($parts[0])) {
            throw "Invalid env entry: $item"
        }
        $map[$parts[0]] = $parts[1]
    }
    return $map
}

if ([string]::IsNullOrWhiteSpace($Command) -and [string]::IsNullOrWhiteSpace($ScriptPath)) {
    throw "Provide either -Command or -ScriptPath."
}

if (-not [string]::IsNullOrWhiteSpace($Command) -and -not [string]::IsNullOrWhiteSpace($ScriptPath)) {
    throw "Use only one of -Command or -ScriptPath."
}

$resolved = Resolve-RequestedShell
$arguments = Build-Arguments -ResolvedShell $resolved
$envMap = Parse-EnvMap

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $resolved.path
$psi.Arguments = $arguments
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true

if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
    $psi.WorkingDirectory = $WorkingDirectory
}

foreach ($key in $envMap.Keys) {
    $null = $psi.EnvironmentVariables.Remove($key)
    $psi.EnvironmentVariables.Add($key, $envMap[$key])
}

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
$null = $process.Start()

$stdoutTask = $process.StandardOutput.ReadToEndAsync()
$stderrTask = $process.StandardError.ReadToEndAsync()

$timedOut = $false
if ($TimeoutSec -gt 0) {
    if (-not $process.WaitForExit($TimeoutSec * 1000)) {
        $timedOut = $true
        try {
            $process.Kill()
        } catch {
        }
    }
}

$process.WaitForExit()
$stdoutTask.Wait()
$stderrTask.Wait()

$result = [ordered]@{
    shell = $resolved.name
    executable = $resolved.path
    arguments = $arguments
    working_directory = if ($psi.WorkingDirectory) { $psi.WorkingDirectory } else { (Get-Location).Path }
    exit_code = if ($timedOut) { 124 } else { $process.ExitCode }
    timed_out = $timedOut
    stdout = $stdoutTask.Result
    stderr = $stderrTask.Result
}

if ($CaptureJson) {
    $json = [pscustomobject]$result | ConvertTo-Json -Depth 5
    Write-Output $json
    exit $result.exit_code
}

if ($PassThru) {
    [pscustomobject]$result
    exit $result.exit_code
}

if (-not [string]::IsNullOrEmpty($result.stdout)) {
    Write-Output $result.stdout.TrimEnd("`r", "`n")
}

if (-not [string]::IsNullOrEmpty($result.stderr)) {
    [Console]::Error.WriteLine($result.stderr.TrimEnd("`r", "`n"))
}

exit $result.exit_code
