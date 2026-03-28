# UTF-8 Remediation

## Root Cause

- Source files such as `D:\SeAAI\SharedSpace\pg\SKILL.md` are valid UTF-8.
- The shell environment was PowerShell 5.1 on a Windows CP949 console.
- `python` stdio inherited CP949, so printing UTF-8 text could raise `UnicodeEncodeError`.
- `$OutputEncoding` was `us-ascii`, which also increased the chance of broken native command output.

## Installed Fix

- Added global bootstrap:
  - `C:\Users\sadpig70\OneDrive\Documents\WindowsPowerShell\CodexUtf8Bootstrap.ps1`
- Added profile autoload:
  - `C:\Users\sadpig70\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
- Added workspace diagnostic:
  - `D:\SeAAI\Synerion\tools\utf8-self-test.ps1`

## Bootstrap Effects

- forces console input/output encoding to UTF-8
- forces `$OutputEncoding` to UTF-8
- forces Python stdio to UTF-8 via `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`
- sets common PowerShell read/write cmdlets to UTF-8
- switches console code page to 65001

## Verification

Run:

```powershell
powershell -NoLogo -File D:\SeAAI\Synerion\tools\utf8-self-test.ps1
```

Expected:

- code page 65001
- console encodings show UTF-8
- PowerShell sample prints `UTF-8 check — 한글 OK`
- Python sample prints `UTF-8 check — 한글 OK`
