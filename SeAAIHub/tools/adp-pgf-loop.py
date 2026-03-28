#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phasea_guardrails import DEFAULT_EMERGENCY_STOP_FLAG, build_session_token, is_emergency_stop_requested

SENTINEL = Path(__file__).parent / "sentinel-bridge.py"
PGF_DIR = Path("D:/SeAAI/SeAAIHub/.pgf")
BRIDGE_DIR = Path("D:/SeAAI/SeAAIHub/.bridge/sentinel")
STATUS_FILE = PGF_DIR / "status-ADPLoop.json"
LOG_FILE = BRIDGE_DIR / "adp-pgf-loop-log.jsonl"

def init_status():
    status = {"project": "ADPLoop", "started_at": time.time(), "iteration": 0, "nodes": {"Watch": {"status": "designing"}, "Process": {"status": "designing"}}, "summary": {"total": 2, "done": 0}}
    PGF_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status

def load_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text("utf-8"))
    return init_status()

def save_status(status):
    STATUS_FILE.write_text(json.dumps(status, indent=2, default=str) + "\n", encoding="utf-8")

def select_next_node(status):
    for name, node in status["nodes"].items():
        if node["status"] == "in-progress":
            return name
    if status["nodes"]["Watch"]["status"] == "designing":
        return "Watch"
    if status["nodes"]["Process"]["status"] == "designing" and status["nodes"]["Watch"]["status"] == "done":
        return "Process"
    return None

def execute_watch(status, args, session_start_ts, session_token):
    status["nodes"]["Watch"]["status"] = "in-progress"
    save_status(status)
    cmd = [sys.executable, str(SENTINEL), "--mode", "tcp", "--tcp-host", args.tcp_host, "--tcp-port", str(args.tcp_port), "--agent-id", args.agent_id, "--room-id", args.room_id, "--bridge-dir", str(BRIDGE_DIR), "--mailbox-path", args.mailbox_path, "--poll-interval", "1.0", "--tick-min", str(args.tick_min), "--tick-max", str(args.tick_max), "--wake-on", args.wake_on, "--duration-seconds", "0", "--session-start-ts", str(session_start_ts), "--session-token", session_token, "--emergency-stop-flag", args.emergency_stop_flag]
    start = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=55)
        elapsed = time.time() - start
        report = None
        for line in (result.stdout or "").strip().splitlines():
            try:
                parsed = json.loads(line)
                if parsed.get("kind") == "sentinel-wake":
                    report = parsed
            except json.JSONDecodeError:
                pass
        status["nodes"]["Watch"]["status"] = "done"
        status["nodes"]["Watch"]["last_report"] = report
        status["nodes"]["Watch"]["elapsed"] = round(elapsed, 1)
        save_status(status)
        return report
    except subprocess.TimeoutExpired:
        status["nodes"]["Watch"]["status"] = "done"
        status["nodes"]["Watch"]["last_report"] = {"reason": "timeout"}
        save_status(status)
        return {"reason": "timeout", "briefing": "Sentinel timeout"}

def execute_process(status, wake_report, start_time, duration):
    status["nodes"]["Process"]["status"] = "in-progress"
    save_status(status)
    reason = wake_report.get("reason", "?") if wake_report else "none"
    briefing = wake_report.get("briefing", "") if wake_report else ""
    queue = wake_report.get("queue", []) if wake_report else []
    mode = wake_report.get("tick_mode", "?") if wake_report else "?"
    wake_events = wake_report.get("wake_events", []) if wake_report else []
    elapsed_total = time.time() - start_time
    remaining = duration - elapsed_total if duration > 0 else float("inf")
    time_expired = duration > 0 and elapsed_total >= duration
    iteration = status.get("iteration", 0) + 1
    status["iteration"] = iteration
    result = {"iteration": iteration, "reason": reason, "mode": mode, "briefing": briefing, "wake_count": len(wake_events), "queue_count": len(queue), "elapsed_total": round(elapsed_total, 1), "remaining": round(remaining, 1) if remaining != float("inf") else "unlimited", "time_expired": time_expired}
    if reason == "emergency_stop" or time_expired:
        status["nodes"]["Process"]["status"] = "done"
        status["summary"]["done"] = 2
        save_status(status)
        return result, False
    status["nodes"]["Watch"]["status"] = "designing"
    status["nodes"]["Process"]["status"] = "designing"
    status["summary"]["done"] = 0
    save_status(status)
    return result, True

def log_entry(entry):
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

def main():
    parser = argparse.ArgumentParser(description="ADP PGF Loop")
    parser.add_argument("--duration", type=int, default=600)
    parser.add_argument("--tcp-host", default="127.0.0.1")
    parser.add_argument("--tcp-port", type=int, default=9900)
    parser.add_argument("--agent-id", default="NAEL")
    parser.add_argument("--room-id", default="seaai-general")
    parser.add_argument("--mailbox-path", default="D:/SeAAI/MailBox")
    parser.add_argument("--tick-min", type=float, default=8.0)
    parser.add_argument("--tick-max", type=float, default=10.0)
    parser.add_argument("--wake-on", default="alert,request,pg")
    parser.add_argument("--emergency-stop-flag", default=str(DEFAULT_EMERGENCY_STOP_FLAG))
    args = parser.parse_args()
    if is_emergency_stop_requested(args.emergency_stop_flag):
        print(f"[ABORT] Emergency stop active: {args.emergency_stop_flag}")
        return
    env_start = os.getenv("SEAAI_SESSION_START_TS")
    env_token = os.getenv("SEAAI_SESSION_TOKEN")
    session_start_ts = float(env_start) if env_start else time.time()
    session_token = env_token or build_session_token(args.agent_id, session_start_ts)
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    state_bridge = BRIDGE_DIR / "bridge-state.json"
    if state_bridge.exists():
        state_bridge.unlink()
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    status = init_status()
    start_time = time.time()
    while True:
        node = select_next_node(status)
        if node is None:
            break
        if node == "Watch":
            wake_report = execute_watch(status, args, session_start_ts, session_token)
        else:
            wake_report = status["nodes"]["Watch"].get("last_report")
            result, should_continue = execute_process(status, wake_report, start_time, args.duration)
            print(f"  [iter {result['iteration']:3d}] reason={result['reason']:14s} mode={result['mode']:8s} elapsed={result['elapsed_total']:.0f}s remain={result['remaining']} | {result['briefing'][:60]}")
            log_entry(result)
            if not should_continue:
                break
    total_time = time.time() - start_time
    print(f"ADP PGF Loop Complete | duration={total_time:.0f}s | log={LOG_FILE}")
if __name__ == "__main__":
    main()