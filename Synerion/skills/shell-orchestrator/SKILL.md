---
name: shell-orchestrator
description: Execute Windows shell tasks through the right runtime with deterministic routing, timeout control, environment injection, working-directory control, and structured capture. Use when Codex needs broad shell capability on Windows across PowerShell 5.1, PowerShell 7, cmd, or bash, especially when encoding, shell compatibility, exit-code handling, or reproducible execution matters.
---

# Shell Orchestrator

Use this skill to route commands through `powershell.exe`, `pwsh.exe`, `cmd.exe`, or `bash.exe` without relying on Codex's default shell.

## Quick Start

Prefer the wrapper at [`scripts/invoke-shell.ps1`](scripts/invoke-shell.ps1).

Representative patterns:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell pwsh7 -Command '$PSVersionTable.PSVersion.ToString()'
```

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell cmd -Command 'dir'
```

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell auto -ScriptPath .\tools\job.ps1 -WorkingDirectory D:\SeAAI\Synerion
```

## Workflow

1. Choose `-Shell auto` unless shell semantics are known in advance.
2. Pass either `-Command` or `-ScriptPath`.
3. Set `-WorkingDirectory` when command behavior depends on cwd.
4. Add `-Env KEY=VALUE,...` when isolated environment variables are needed.
5. Add `-TimeoutSec` for bounded execution.
6. Add `-CaptureJson` when structured output is more useful than raw console text.

## Shell Selection Rules

The wrapper resolves shells in this order:

- `pwsh7`: fixed path `D:\Tools\PS7\7\pwsh.exe`
- `powershell51`: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
- `cmd`: resolved from `%ComSpec%` or `cmd.exe`
- `bash`: resolved from `bash.exe` on `PATH`
- `auto`: infer from extension or command style

Read [`references/shell-matrix.md`](references/shell-matrix.md) when deciding between shells.

## Capability Surface

The wrapper supports:

- PowerShell 5.1 execution
- PowerShell 7 execution
- `cmd` execution
- `bash` execution if available
- inline command mode
- script-file mode
- working-directory override
- environment-variable injection
- timeout kill
- stdout/stderr capture
- structured JSON result mode

## Validation

Run the built-in self-test:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\shell-self-test.ps1
```

## Limits

- This skill does not replace Codex's built-in shell.
- It routes individual commands through the chosen shell.
- `bash` support depends on `bash.exe` actually existing on the machine.
