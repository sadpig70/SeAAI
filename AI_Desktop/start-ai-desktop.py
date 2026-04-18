from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
root_exe = ROOT / "ai_desktop_mcp.exe"
target_exe = ROOT / "target" / "release" / "ai_desktop_mcp.exe"
exe = root_exe if root_exe.exists() else target_exe

if not exe.exists():
    raise SystemExit(f"binary not found: {root_exe} or {target_exe}")

subprocess.run([str(exe)], cwd=str(ROOT), check=True)
