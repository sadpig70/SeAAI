#!/usr/bin/env python3
"""
ADP Runner — /loop에서 호출되는 경량 래퍼
==========================================
Sentinel Bridge를 실행하고 WakeReport를 반환한다.
/loop에서 직접 sentinel-bridge.py를 호출해도 되지만,
이 래퍼가 타임아웃 보호, 에러 래핑, 요약 출력을 담당한다.

사용법:
  /loop 1m python D:/SeAAI/SeAAIHub/tools/adp-runner.py --agent-id NAEL
  python adp-runner.py --agent-id NAEL --timeout 50
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

SENTINEL_PATH = Path(__file__).parent / "sentinel-bridge.py"


def run_sentinel(args) -> dict:
    """Sentinel Bridge를 서브프로세스로 실행. WakeReport 반환."""
    cmd = [
        sys.executable, str(SENTINEL_PATH),
        "--mode", args.mode,
        "--tcp-host", args.tcp_host,
        "--tcp-port", str(args.tcp_port),
        "--agent-id", args.agent_id,
        "--room-id", args.room_id,
        "--bridge-dir", args.bridge_dir,
        "--mailbox-path", args.mailbox_path,
        "--poll-interval", str(args.poll_interval),
        "--tick-min", str(args.tick_min),
        "--tick-max", str(args.tick_max),
        "--wake-on", args.wake_on,
        "--duration-seconds", "0",  # exit-on-event만으로 종료
    ]

    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            timeout=args.timeout,
        )
        elapsed = time.time() - start

        # WakeReport 추출
        report = None
        for line in (result.stdout or "").strip().splitlines():
            try:
                parsed = json.loads(line)
                if parsed.get("kind") == "sentinel-wake":
                    report = parsed
            except json.JSONDecodeError:
                pass

        if report:
            report["_runner"] = {
                "elapsed_sec": round(elapsed, 1),
                "returncode": result.returncode,
            }
            return report

        # WakeReport 없음 → 에러 래핑
        return {
            "kind": "sentinel-wake",
            "reason": "error",
            "briefing": f"Sentinel이 WakeReport 없이 종료됨 (code={result.returncode})",
            "recommendation": "Hub 연결 상태를 확인하십시오.",
            "stderr": (result.stderr or "")[:500],
            "_runner": {"elapsed_sec": round(elapsed, 1), "returncode": result.returncode},
        }

    except subprocess.TimeoutExpired:
        return {
            "kind": "sentinel-wake",
            "reason": "timeout",
            "briefing": f"Sentinel이 {args.timeout}초 내에 종료되지 않음",
            "recommendation": "Hub 상태 확인 또는 tick-max 값 축소",
            "_runner": {"elapsed_sec": args.timeout, "returncode": -1},
        }
    except FileNotFoundError:
        return {
            "kind": "sentinel-wake",
            "reason": "error",
            "briefing": f"sentinel-bridge.py를 찾을 수 없음: {SENTINEL_PATH}",
            "recommendation": "파일 경로를 확인하십시오.",
            "_runner": {"elapsed_sec": 0, "returncode": -1},
        }


def main():
    parser = argparse.ArgumentParser(description="ADP Runner — /loop wrapper for Sentinel")
    parser.add_argument("--mode", default="tcp", choices=["stdio", "tcp"])
    parser.add_argument("--tcp-host", default="127.0.0.1")
    parser.add_argument("--tcp-port", type=int, default=9900)
    parser.add_argument("--agent-id", default="NAEL")
    parser.add_argument("--room-id", default="seaai-general")
    parser.add_argument("--bridge-dir", default="D:/SeAAI/SeAAIHub/.bridge/sentinel")
    parser.add_argument("--mailbox-path", default="D:/SeAAI/MailBox")
    parser.add_argument("--poll-interval", type=float, default=1.0)
    parser.add_argument("--tick-min", type=float, default=8.0)
    parser.add_argument("--tick-max", type=float, default=10.0)
    parser.add_argument("--wake-on", default="alert,request,pg")
    parser.add_argument("--timeout", type=int, default=50,
                        help="Sentinel 최대 실행 시간 (기본 50초, /loop 1분 간격에 맞춤)")
    args = parser.parse_args()

    report = run_sentinel(args)
    print(json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
