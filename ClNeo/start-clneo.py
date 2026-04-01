#!/usr/bin/env python3
"""ClNeo 세션 시작."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
print("Starting ClNeo session...")
print(f"Workspace: {ROOT}")
print("Run 'claude' in this directory to start ClNeo.")
print("ClNeo will auto-load CLAUDE.md and begin SCS restore.")
