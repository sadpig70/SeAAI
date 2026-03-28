#!/usr/bin/env python3
"""
ADP /loop Pattern Test — 10분간 adp-runner.py 반복 실행
========================================================
/loop 1m 패턴을 시뮬레이션:
  - 1분 간격으로 adp-runner.py 실행
  - WakeReport 분석
  - 시나리오 주입 (outbox 메시지, directive)
  - 결과 로깅
"""

import json
import subprocess
import sys
import time
from pathlib import Path

RUNNER = "D:/SeAAI/SeAAIHub/tools/adp-runner.py"
BRIDGE_DIR = Path("D:/SeAAI/SeAAIHub/.bridge/sentinel")
STATE_FILE = BRIDGE_DIR / "bridge-state.json"
OUTBOX = BRIDGE_DIR / "outbox-NAEL.jsonl"
LOG_DIR = BRIDGE_DIR / "test-logs"

DURATION_MINUTES = 10
LOOP_INTERVAL = 60  # 1분


def run_adp_cycle(cycle_num):
    """adp-runner.py 1회 실행."""
    cmd = [
        sys.executable, RUNNER,
        "--agent-id", "NAEL",
        "--room-id", "adp-loop-test",
        "--tick-min", "8", "--tick-max", "10",
        "--timeout", "50",
    ]
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", timeout=55,
        )
        elapsed = time.time() - start
        report = None
        for line in (result.stdout or "").strip().splitlines():
            try:
                parsed = json.loads(line)
                if parsed.get("kind") == "sentinel-wake":
                    report = parsed
            except json.JSONDecodeError:
                pass
        return {
            "cycle": cycle_num,
            "elapsed": round(elapsed, 1),
            "returncode": result.returncode,
            "report": report,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        return {"cycle": cycle_num, "elapsed": 55, "returncode": -1, "report": None, "error": "timeout"}
    except Exception as e:
        return {"cycle": cycle_num, "elapsed": 0, "returncode": -1, "report": None, "error": str(e)}


def inject_outbox_message():
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    msg = json.dumps({
        "to": ["NAEL"], "intent": "chat",
        "body": f"ADP self-test message at {time.strftime('%H:%M:%S')}",
        "id": f"test-{int(time.time())}",
    }, ensure_ascii=False)
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    return "outbox injected"


def inject_directive():
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text("utf-8"))
        state.setdefault("lord_directives", []).append({
            "type": "promote",
            "condition": "intent == 'chat'",
            "payload": {"reason": "test promote"},
            "expires_at": time.time() + 300,
        })
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return "directive injected"
    return "no state file"


def main():
    print(f"=== ADP /loop Pattern Test — {DURATION_MINUTES}min, {LOOP_INTERVAL}s interval ===")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 초기화
    for f in [STATE_FILE, OUTBOX]:
        if f.exists():
            f.unlink()

    test_start = time.time()
    deadline = test_start + DURATION_MINUTES * 60
    results = []
    scenarios_done = set()

    cycle = 0
    while time.time() < deadline:
        cycle += 1
        elapsed_total = time.time() - test_start
        remaining = deadline - time.time()

        # 시나리오 주입
        if elapsed_total >= 120 and "outbox" not in scenarios_done:
            msg = inject_outbox_message()
            print(f"  [{elapsed_total:.0f}s] SCENARIO: {msg}")
            scenarios_done.add("outbox")

        if elapsed_total >= 240 and "directive" not in scenarios_done:
            msg = inject_directive()
            print(f"  [{elapsed_total:.0f}s] SCENARIO: {msg}")
            scenarios_done.add("directive")

        # ADP cycle 실행
        result = run_adp_cycle(cycle)
        results.append(result)

        report = result.get("report")
        if report:
            reason = report.get("reason", "?")
            mode = report.get("tick_mode", "?")
            briefing = report.get("briefing", "")[:80]
            runner = report.get("_runner", {})
            print(f"  [cycle {cycle:2d}] {result['elapsed']:5.1f}s | reason={reason:8s} | mode={mode:8s} | {briefing}")
        else:
            print(f"  [cycle {cycle:2d}] {result['elapsed']:5.1f}s | FAIL: {result.get('error', 'no report')}")

        # 로그 저장
        log_file = LOG_DIR / f"cycle-{cycle:03d}.json"
        log_file.write_text(json.dumps(result, ensure_ascii=False, default=str, indent=2), encoding="utf-8")

        # /loop 간격 대기 (남은 시간 계산)
        cycle_elapsed = result["elapsed"]
        wait = max(0, LOOP_INTERVAL - cycle_elapsed)
        if time.time() + wait >= deadline:
            break
        if wait > 0:
            time.sleep(wait)

    # 최종 보고
    total_time = time.time() - test_start
    success = sum(1 for r in results if r.get("report"))
    fail = sum(1 for r in results if not r.get("report"))
    modes = set()
    reasons = {}
    for r in results:
        rpt = r.get("report")
        if rpt:
            modes.add(rpt.get("tick_mode", "?"))
            reason = rpt.get("reason", "?")
            reasons[reason] = reasons.get(reason, 0) + 1

    # 세션 연속성 확인
    state_ok = False
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text("utf-8"))
        state_ok = state.get("tick_count", 0) > 0

    print()
    print("=" * 65)
    print("ADP /loop Pattern Test Results")
    print("=" * 65)
    print(f"Duration:           {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Loop interval:      {LOOP_INTERVAL}s")
    print(f"Total cycles:       {len(results)}")
    print(f"Successful:         {success}")
    print(f"Failed:             {fail}")
    print(f"Tick modes:         {sorted(modes)}")
    print(f"Reasons:            {reasons}")
    print(f"State continuity:   {'OK' if state_ok else 'FAIL'}")
    print(f"Scenarios:          {sorted(scenarios_done)}")
    print()

    passed = success > 0 and fail == 0 and state_ok
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    # 요약 저장
    summary = {
        "duration_sec": round(total_time),
        "loop_interval": LOOP_INTERVAL,
        "total_cycles": len(results),
        "success": success, "fail": fail,
        "modes": sorted(modes), "reasons": reasons,
        "state_continuity": state_ok,
        "scenarios": sorted(scenarios_done),
        "verdict": "PASSED" if passed else "FAILED",
    }
    (LOG_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Logs: {LOG_DIR}")


if __name__ == "__main__":
    main()
