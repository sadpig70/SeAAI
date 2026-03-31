#!/usr/bin/env python3
"""
PowerShell 7 실행 래퍼
UTF-8 인코딩을 자동 설정하여 한국어 깨짐 방지.

사용법:
    from pwsh7 import run_ps7

    # 단순 실행
    output = run_ps7('Get-Date -Format "yyyy-MM-dd"')

    # 멀티라인
    output = run_ps7('''
        $items = Get-ChildItem D:/SeAAI
        $items | Select-Object Name, Length
    ''')

    # CLI
    python pwsh7.py "Write-Output '테스트'"
"""
import subprocess
import sys

PWSH7_PATH = r"D:\Tools\PS7\7\pwsh.exe"
UTF8_PREFIX = "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"


def run_ps7(script: str, timeout: int = 60) -> str:
    """PowerShell 7 스크립트 실행. UTF-8 자동 설정."""
    full_script = UTF8_PREFIX + script

    result = subprocess.run(
        [PWSH7_PATH, "-NoProfile", "-Command", full_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )

    if result.returncode != 0:
        error = result.stderr.strip()
        if error:
            raise RuntimeError(f"pwsh7 error (exit {result.returncode}): {error}")

    return result.stdout.strip()


def run_ps7_async(script: str):
    """PowerShell 7 비동기 실행 (백그라운드, 결과 안 기다림)."""
    full_script = UTF8_PREFIX + script

    subprocess.Popen(
        [PWSH7_PATH, "-NoProfile", "-Command", full_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        script = sys.argv[1]
        print(run_ps7(script))
    else:
        print(f"pwsh7 path: {PWSH7_PATH}")
        print(run_ps7('Write-Output "PowerShell $($PSVersionTable.PSVersion) ready"'))
