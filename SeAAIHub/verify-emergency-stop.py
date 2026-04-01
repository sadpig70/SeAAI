#!/usr/bin/env python3
"""긴급 정지 플래그 생성/확인/삭제 검증."""
from pathlib import Path

FLAG = Path(__file__).parent.parent / "SharedSpace" / "hub-readiness" / "EMERGENCY_STOP.flag"

def main():
    FLAG.parent.mkdir(parents=True, exist_ok=True)

    # Create
    FLAG.touch()
    assert FLAG.exists(), "Flag creation failed"
    print("Flag created: OK")

    # Remove
    FLAG.unlink()
    assert not FLAG.exists(), "Flag removal failed"
    print("Flag removed: OK")

    print("Emergency stop verification PASSED")

if __name__ == "__main__":
    main()
