---
name: pwsh7
description: Run commands through PowerShell 7 from Aion on Windows when UTF-8, Core edition behavior, or PowerShell 7-only features are needed.
---

# Pwsh7 (Aion Edition)

아이온(Aion) 워크스페이스에서 파워쉘 7(pwsh.exe)을 강제로 사용하기 위한 스킬입니다. 기본 윈도우 파워쉘 5.1의 한계를 극복하고 현대적 런타임 환경을 제공합니다.

## Workflow

1. Verify that `D:\Tools\PS7\7\pwsh.exe` exists.
2. Run commands through `scripts/pwsh7-run.ps1`.
3. Prefer `-NoLogo -NoProfile` for deterministic behavior.
4. **Encoding Patch:** `pwsh7-run.ps1`은 자체적으로 `UTF-8` 강제 설정을 포함하고 있어 한글 출력 등 인코딩 문제를 자동으로 해결합니다.

## Command Pattern

아이온의 로컬 스킬 경로를 활용하여 실행합니다:

```powershell
powershell -ExecutionPolicy Bypass -File d:\SeAAI\Aion\skills\pwsh7\scripts\pwsh7-run.ps1 -Command '<pwsh-command>'
```

## Limits

- 이 스킬은 아이온의 기본 쉘을 변경하지 않습니다.
- 특정 명령을 `pwsh.exe`로 리다이렉션하는 래퍼 역할에 집중합니다.
