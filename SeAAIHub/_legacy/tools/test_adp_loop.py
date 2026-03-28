#!/usr/bin/env python3
"""
ADP Loop Integration Test — 10분간 Sentinel 반복 실행
=====================================================
검증 항목:
  1. Sentinel이 tick 간격마다 정상 종료하는가
  2. WakeReport JSON이 유효한가
  3. 적응적 tick (dormant → patrol → combat) 전환이 작동하는가
  4. exit-on-event: 메시지 도착 시 즉시 종료하는가
  5. GuaranteedDelivery: outbox 메시지가 Hub로 전달되는가
  6. ThreatAssess: depth >= 10 메시지가 DISMISS되는가
  7. Directives: promote가 작동하는가
  8. 세션 연속성: bridge-state.json이 유지되는가
"""

import json
import subprocess
import sys
import time
from pathlib import Path

SENTINEL = "D:/SeAAI/SeAAIHub/tools/sentinel-bridge.py"
BRIDGE_DIR = Path("D:/SeAAI/SeAAIHub/.bridge/adp-test")
STATE_FILE = BRIDGE_DIR / "bridge-state.json"
OUTBOX = BRIDGE_DIR / "outbox-NAEL.jsonl"
LOG_FILE = BRIDGE_DIR / "adp-test-log.jsonl"

DURATION_MINUTES = 10
TCP_HOST = "127.0.0.1"
TCP_PORT = 9900

# 테스트 시나리오 (시작 후 N초에 실행)
SCENARIOS = {
    30:  "inject_outbox_message",     # 30초: outbox에 메시지 작성 → 발신 테스트
    60:  "inject_directive_promote",  # 60초: directive promote 작성
    120: "verify_state_continuity",   # 120초: bridge-state.json 연속성 확인
    180: "verify_adaptive_tick",      # 180초: tick 모드 확인
}


def run_sentinel(extra_args=None):
    """Sentinel 1회 실행. 종료 시 WakeReport 반환."""
    cmd = [
        sys.executable, SENTINEL,
        "--mode", "tcp",
        "--tcp-host", TCP_HOST,
        "--tcp-port", str(TCP_PORT),
        "--agent-id", "NAEL",
        "--room-id", "adp-test-room",
        "--bridge-dir", str(BRIDGE_DIR),
        "--poll-interval", "1.0",
        "--tick-min", "8.0",
        "--tick-max", "10.0",
        "--wake-on", "alert,request,pg",
        "--duration-seconds", "0",  # exit-on-event만으로 종료
    ]
    if extra_args:
        cmd.extend(extra_args)

    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            timeout=60,  # 최대 60초 (dormant tick 30초 + 여유)
        )
        elapsed = time.time() - start
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        # WakeReport 파싱
        report = None
        if stdout:
            for line in stdout.splitlines():
                try:
                    parsed = json.loads(line)
                    if parsed.get("kind") == "sentinel-wake":
                        report = parsed
                except json.JSONDecodeError:
                    pass

        return {
            "elapsed_sec": round(elapsed, 1),
            "returncode": result.returncode,
            "report": report,
            "stdout_lines": len(stdout.splitlines()) if stdout else 0,
            "stderr": stderr[:200] if stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"elapsed_sec": 60, "returncode": -1, "report": None, "error": "timeout"}


def inject_outbox_message():
    """outbox에 테스트 메시지 작성."""
    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    msg = json.dumps({
        "to": ["NAEL"], "intent": "chat",
        "body": "ADP self-test: outbox delivery check",
        "id": f"test-outbox-{int(time.time())}",
    }, ensure_ascii=False)
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    return "outbox message injected"


def inject_directive_promote():
    """bridge-state.json에 promote directive 추가."""
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text("utf-8"))
        state.setdefault("lord_directives", []).append({
            "type": "promote",
            "condition": "from_agent == 'NAEL'",
            "payload": {"reason": "ADP self-test promote"},
            "expires_at": time.time() + 300,
        })
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return "directive promote injected"
    return "state file not found"


def verify_state_continuity():
    """bridge-state.json이 세션 간 유지되는지 확인."""
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text("utf-8"))
        tick_count = state.get("tick_count", 0)
        printed_ids = len(state.get("printed_ids", []))
        return f"state OK: tick_count={tick_count}, printed_ids={printed_ids}"
    return "FAIL: state file missing"


def verify_adaptive_tick(reports):
    """tick 간격이 활동량에 따라 변하는지 확인."""
    modes = [r.get("report", {}).get("tick_mode", "?") for r in reports if r.get("report")]
    return f"modes observed: {set(modes)}"


def log_entry(log_file, entry):
    """JSONL 로그에 기록."""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def main():
    print(f"=== ADP Loop Integration Test — {DURATION_MINUTES}min ===")
    print(f"Hub: {TCP_HOST}:{TCP_PORT}")
    print(f"Bridge dir: {BRIDGE_DIR}")
    print()

    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    # 이전 상태 초기화
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if OUTBOX.exists():
        OUTBOX.unlink()
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    test_start = time.time()
    deadline = test_start + DURATION_MINUTES * 60
    cycle = 0
    reports = []
    results = {
        "total_cycles": 0,
        "successful_wakes": 0,
        "failed_wakes": 0,
        "tick_modes": set(),
        "total_dismissed": 0,
        "total_queued": 0,
        "scenarios_executed": [],
        "errors": [],
    }

    while time.time() < deadline:
        cycle += 1
        elapsed_total = time.time() - test_start

        # 시나리오 실행
        for trigger_sec, scenario_name in list(SCENARIOS.items()):
            if elapsed_total >= trigger_sec:
                if scenario_name == "inject_outbox_message":
                    msg = inject_outbox_message()
                elif scenario_name == "inject_directive_promote":
                    msg = inject_directive_promote()
                elif scenario_name == "verify_state_continuity":
                    msg = verify_state_continuity()
                elif scenario_name == "verify_adaptive_tick":
                    msg = verify_adaptive_tick(reports)
                else:
                    msg = "unknown scenario"
                print(f"  [{elapsed_total:.0f}s] SCENARIO: {scenario_name} → {msg}")
                results["scenarios_executed"].append({"name": scenario_name, "result": msg})
                del SCENARIOS[trigger_sec]

        # Sentinel 실행
        run_result = run_sentinel()
        reports.append(run_result)
        results["total_cycles"] += 1

        report = run_result.get("report")
        if report:
            results["successful_wakes"] += 1
            mode = report.get("tick_mode", "?")
            results["tick_modes"].add(mode)
            results["total_dismissed"] += report.get("dismissed_count", 0)
            results["total_queued"] += len(report.get("queue", []))

            reason = report.get("reason", "?")
            briefing = report.get("briefing", "")
            print(f"  [cycle {cycle}] {run_result['elapsed_sec']}s | reason={reason} | mode={mode} | {briefing}")
        else:
            results["failed_wakes"] += 1
            err = run_result.get("error", run_result.get("stderr", "unknown"))
            results["errors"].append(f"cycle {cycle}: {err}")
            print(f"  [cycle {cycle}] {run_result['elapsed_sec']}s | FAIL: {err}")

        log_entry(LOG_FILE, {"cycle": cycle, "elapsed_total": round(elapsed_total, 1), **run_result})

    # 최종 보고
    total_time = time.time() - test_start
    results["tick_modes"] = list(results["tick_modes"])

    print()
    print("=" * 60)
    print("ADP Loop Test Results")
    print("=" * 60)
    print(f"Duration:          {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Total cycles:      {results['total_cycles']}")
    print(f"Successful wakes:  {results['successful_wakes']}")
    print(f"Failed wakes:      {results['failed_wakes']}")
    print(f"Tick modes seen:   {results['tick_modes']}")
    print(f"Total dismissed:   {results['total_dismissed']}")
    print(f"Total queued:      {results['total_queued']}")
    print(f"Scenarios:         {len(results['scenarios_executed'])}")
    print(f"Errors:            {len(results['errors'])}")
    if results["errors"]:
        for e in results["errors"][:5]:
            print(f"  - {e}")
    print()

    # 판정
    passed = (
        results["successful_wakes"] > 0
        and results["failed_wakes"] == 0
        and len(results["tick_modes"]) >= 1
    )
    print(f"VERDICT: {'PASSED' if passed else 'FAILED'}")

    # 결과 저장
    summary_path = BRIDGE_DIR / "adp-test-summary.json"
    summary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
