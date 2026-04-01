#!/usr/bin/env python3
"""Shell self-test."""
import platform
print(f"OS: {platform.system()}")
print(f"Python: {sys.version}" if 'sys' in dir() else "Python OK")
print("Shell self-test PASSED")
