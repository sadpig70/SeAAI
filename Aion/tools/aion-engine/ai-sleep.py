#!/usr/bin/env python3
"""
Aae-v2.1 Persistence Tool: ai-sleep.py
"""
import sys
import time

def ai_sleep(duration):
    """지정된 시간 동안 슬립하고 종료 메시지를 출력합니다."""
    try:
        duration = float(duration)
        print(f"[Aae-Sleeper] Starting sleep for {duration} seconds...")
        time.sleep(duration)
        print(f"[Aae-Sleeper] Sleep finished. Process ended.")
    except Exception as e:
        print(f"[Aae-Sleeper] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai-sleep.py <seconds>")
        sys.exit(1)
    ai_sleep(sys.argv[1])
