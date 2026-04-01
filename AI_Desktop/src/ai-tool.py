#!/usr/bin/env python3
"""AI Tool — dynamic tool loader."""
from pathlib import Path
TOOLS_DIR = Path(__file__).parent.parent / "dynamic_tools"
print(f"AI Tools directory: {TOOLS_DIR}")
print(f"Available tools: {[f.stem for f in TOOLS_DIR.glob('*.py')]}")
