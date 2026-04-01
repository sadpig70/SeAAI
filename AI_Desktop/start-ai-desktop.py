#!/usr/bin/env python3
"""AI Desktop start."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).parent
BIN = ROOT / "target" / "release" / ("ai-desktop.exe" if sys.platform == "win32" else "ai-desktop")
if BIN.exists():
    print(f"Starting AI Desktop: {BIN}")
    subprocess.Popen([str(BIN)])
else:
    print(f"Binary not found: {BIN}")
    print("Build first: cd AI_Desktop && cargo build --release")
