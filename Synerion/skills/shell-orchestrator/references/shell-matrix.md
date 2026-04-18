# Shell Matrix

## Use `powershell51`

- legacy Windows PowerShell compatibility
- scripts that depend on Desktop edition behavior
- older modules that do not support PowerShell Core

## Use `pwsh7`

- UTF-8-heavy output
- PowerShell Core semantics
- modern scripting
- cross-platform-oriented PowerShell code

Fixed path in this workspace:

- `D:\Tools\PS7\7\pwsh.exe`

## Use `cmd`

- `.bat` and `.cmd` scripts
- built-ins such as `dir`, `copy`, `type`, `set`
- commands that assume `cmd /c` parsing rules

## Use `bash`

- `.sh` scripts
- pipelines or syntax that assume POSIX shell behavior
- Git Bash or WSL-compatible command flows when `bash.exe` exists

## Use `auto`

Use `auto` when:

- the script extension clearly identifies the shell
- the command comes from mixed tooling and wrapper inference is acceptable

Inference rules:

- `.ps1` -> `pwsh7` if present, otherwise `powershell51`
- `.cmd` / `.bat` -> `cmd`
- `.sh` -> `bash`
- command starting with `cmd /c` -> `cmd`
- command containing obvious bash patterns and `bash.exe` exists -> `bash`
- otherwise -> `powershell51`
