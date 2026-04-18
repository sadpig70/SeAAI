---
name: pwsh7-enforcer
description: Force Windows shell execution through PowerShell 7 for Synerion. Use this skill whenever Codex is about to run shell commands on Windows and UTF-8 stability, deterministic Core behavior, timeout control, environment repair, or reproducible command routing matters. For Synerion, this is the default execution path for non-trivial shell work; prefer the workspace wrapper over Codex's built-in shell.
---

# Pwsh7 Enforcer

Use this skill to make `D:\Tools\PS7\7\pwsh.exe` the effective default runtime for Synerion shell work without relying on Codex's host shell.

## Default Rule

For Synerion on Windows:

1. Prefer `skills/shell-orchestrator/scripts/invoke-shell.ps1`.
2. Pass `-Shell pwsh7` unless another shell is explicitly required.
3. Treat Codex's built-in shell as fallback for trivial read-only checks only.

## Required Command Pattern

Use this wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell pwsh7 -Command '<command>'
```

Representative examples:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell pwsh7 -Command '$PSVersionTable.PSVersion.ToString()'
```

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\invoke-shell.ps1 -Shell pwsh7 -Command 'python .\tools\continuity-self-test.py'
```

## When This Skill Must Win

Use this skill by default when:

- running PowerShell commands on Windows
- UTF-8 or Unicode correctness matters
- `SystemRoot` / `windir` / `ComSpec` repair may matter
- bounded timeout or structured capture matters
- command reproducibility matters across sessions

## Exceptions

You may skip the wrapper only when all of these are true:

- the command is a trivial read-only probe
- encoding behavior does not matter
- timeout / env injection / shell selection do not matter
- using the built-in shell is clearly lower risk

## Limits

- This skill does not change Codex's internal host shell globally.
- It defines Synerion's operational default by policy and wrapper usage.
- If `D:\Tools\PS7\7\pwsh.exe` moves, update `skills/shell-orchestrator/scripts/invoke-shell.ps1`.
