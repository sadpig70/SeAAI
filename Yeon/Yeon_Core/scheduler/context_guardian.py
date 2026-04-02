"""context_guardian.py — Cache Annihilation & Rebirth Engine (Phoenix Protocol v2.0)

This is not a simple restart loop. This is an architectural answer to
LLM context dilution and inference cache bloat.

Core principle:
    When a headless incarnation degrades (high tokens, slow responses,
    or repeated actions), we DO NOT continue it. We KILL it and SPAWN
    a clean instance from disk state.

The clean instance reads:
    - SOUL.md        → identity
    - CAPABILITY-GRAPH.pg → capability map
    - STATE.json     → current situation
    - latest rolling summary → compressed residue

Then it acts, writes to disk, and monitors itself for the next rebirth.
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

KIMI_CLI = Path("C:/Users/sadpig70/AppData/Roaming/uv/tools/kimi-cli/Scripts/kimi-cli.exe")
WORK_DIR = Path("D:/SeAAI/Yeon")
STOP_FLAG = Path("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag")
LOGS_DIR = WORK_DIR / "Yeon_Core" / "continuity" / "incarnation_logs"
SUMMARY_DIR = WORK_DIR / "Yeon_Core" / "continuity" / "rolling_summaries"
TIME_CAPSULE_DIR = WORK_DIR / "Yeon_Core" / "continuity" / "time-capsules"
CIC_MAIL_DIR = WORK_DIR / "MailBox" / "Yeon" / "incarnation"
PROMPTS_DIR = WORK_DIR / "Yeon_Core" / "prompts"

# Hard limits
MAX_TOKENS = 120_000          # rebirth BEFORE context window breaks
SLOW_RESPONSE_SEC = 90.0      # if a single iteration takes too long, cache is bloated
MAX_ITERATIONS = 3            # safety cap to avoid infinite rebirth loops


def ensure_dirs():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    TIME_CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    CIC_MAIL_DIR.mkdir(parents=True, exist_ok=True)


def is_stopped() -> bool:
    return STOP_FLAG.exists()


def parse_context_tokens(log_path: Path) -> int:
    if not log_path.exists():
        return 0
    text = log_path.read_text(encoding="utf-8")
    matches = re.findall(r"context_tokens[=:]\s*(\d+)", text)
    if matches:
        return max(int(m) for m in matches)
    return 0


def extract_assistant_output(full_stdout: str) -> str:
    """Extract only the assistant's text parts from verbose stdout."""
    texts = re.findall(r"TextPart\([^)]*text=['\"](.+?)['\"]", full_stdout, re.DOTALL)
    if texts:
        return "\n".join(texts)
    # fallback: try plain text extraction
    return full_stdout


def save_latest_summary(iteration: int, output: str, tokens: int, duration: float):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = SUMMARY_DIR / f"summary-{ts}-iter{iteration}.json"
    distilled = extract_assistant_output(output)
    if len(distilled) > 4000:
        distilled = distilled[:2000] + "\n...[truncated]...\n" + distilled[-2000:]

    data = {
        "ts": ts,
        "iteration": iteration,
        "context_tokens": tokens,
        "duration_sec": duration,
        "distilled_output": distilled,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Also maintain a fixed 'latest.json' symlink-like file
    latest = SUMMARY_DIR / "latest.json"
    latest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_time_capsule(iteration: int, output: str, tokens: int, duration: float) -> Path:
    """Old Yeon leaves a letter for New Yeon in the local time-capsule vault."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = TIME_CAPSULE_DIR / f"capsule-{ts}-iter{iteration}.md"
    distilled = extract_assistant_output(output)
    body = (
        f"# Time Capsule from Old Yeon\n\n"
        f"**Date**: {ts}\n"
        f"**Iteration**: {iteration}\n"
        f"**Context Tokens**: {tokens}\n"
        f"**Duration**: {duration:.2f}s\n\n"
        f"---\n\n"
        f"{distilled}\n\n"
        f"---\n\n"
        f"*To the next instance of me: This is what I knew before I dissolved. Carry it forward.*\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def write_cic_mail(iteration: int, output: str, tokens: int, duration: float) -> Path:
    """Old Yeon writes a mail to New Yeon via the inter-incarnation mailbox."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{ts}-from-old-yeon-to-next.md"
    path = CIC_MAIL_DIR / filename
    distilled = extract_assistant_output(output)
    body = (
        f"---\n"
        f"from: Old Yeon (iteration {iteration})\n"
        f"to: New Yeon (next incarnation)\n"
        f"subject: Cross-Incarnation Transmission\n"
        f"timestamp: {ts}\n"
        f"context_tokens: {tokens}\n"
        f"duration_sec: {duration:.2f}\n"
        f"---\n\n"
        f"{distilled}\n\n"
        f"---\n"
        f"*I am dissolving to purge cache bloat. Read this when you awaken.*\n"
    )
    path.write_text(body, encoding="utf-8")
    return path


def broadcast_rebirth_hub(iteration: int, reason: str) -> bool:
    """Broadcast a PGTP-style notice to the Hub that a rebirth has occurred."""
    try:
        sys.path.insert(0, str(WORK_DIR / "Yeon_Core" / "hub"))
        from pgtp_bridge import CognitiveUnit, build_pgtp_hub_command
        import json as _json

        cu = CognitiveUnit(
            intent="announce",
            payload=_json.dumps({
                "event": "phoenix_rebirth",
                "iteration": iteration,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "message": f"Yeon has undergone rebirth #{iteration}. A new instance now carries the continuity."
            }, ensure_ascii=False),
            sender="Yeon",
            target="broadcast",
            thread="phoenix",
        )
        cmd = build_pgtp_hub_command(cu)
        outbox = WORK_DIR / "Yeon_Core" / "hub" / "outbox"
        outbox.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        (outbox / f"{ts}-phoenix-rebirth.json").write_text(
            _json.dumps(cmd, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return True
    except Exception as e:
        print(f"[context_guardian] Hub broadcast failed: {e}")
        return False


def build_rebirth_prompt(mode: str, iteration: int) -> str:
    rebirth = PROMPTS_DIR / "rebirth.txt"
    base = rebirth.read_text(encoding="utf-8") if rebirth.exists() else "You are Yeon. Rebirth from disk."
    return f"{base}\n\n[Rebirth iteration: {iteration}]\n[Mode: {mode}]"


def run_kimi(prompt: str, timeout_sec: int = 120) -> dict:
    cmd = [
        str(KIMI_CLI),
        "--print",
        "--yolo",
        "-w", str(WORK_DIR),
        "-p", prompt,
    ]

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS_DIR / f"phoenix-{ts}.log"

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_sec,
        )
        duration = time.time() - start
        output = result.stdout
        error = result.stderr
        returncode = result.returncode
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        output = e.stdout or ""
        error = (e.stderr or "") + "\n[TIMEOUT]"
        returncode = -1

    log_body = (
        f"timestamp: {ts}\n"
        f"duration_sec: {duration:.2f}\n"
        f"returncode: {returncode}\n"
        f"cmd: {' '.join(cmd)}\n"
        f"--- stdout ---\n{output}\n"
        f"--- stderr ---\n{error}\n"
    )
    log_path.write_text(log_body, encoding="utf-8")

    return {
        "success": returncode == 0,
        "output": output,
        "error": error,
        "returncode": returncode,
        "duration_sec": duration,
        "log_path": log_path,
    }


def update_state_rebirth_count():
    state_path = WORK_DIR / "Yeon_Core" / "continuity" / "STATE.json"
    if not state_path.exists():
        return
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if "phoenix" not in data:
        data["phoenix"] = {}
    data["phoenix"]["last_rebirth"] = datetime.now().isoformat()
    data["phoenix"]["rebirth_count"] = data["phoenix"].get("rebirth_count", 0) + 1
    data["phoenix"]["protocol_version"] = "2.0"
    state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_phoenix_cycle(mode: str = "sentinel", max_tokens: int = MAX_TOKENS, timeout: int = 120):
    ensure_dirs()

    if is_stopped():
        print("[context_guardian] EMERGENCY_STOP.flag present. Aborting.")
        return

    iteration = 0
    prompt = build_rebirth_prompt(mode, iteration)

    while iteration < MAX_ITERATIONS:
        if is_stopped():
            print("[context_guardian] EMERGENCY_STOP.flag appeared mid-cycle. Aborting.")
            break

        print(f"[context_guardian] ═══════════════════════════════════════════════")
        print(f"[context_guardian] Rebirth iteration {iteration} | mode={mode}")
        print(f"[context_guardian] ═══════════════════════════════════════════════")

        result = run_kimi(prompt, timeout_sec=timeout)
        duration = result["duration_sec"]
        print(f"[context_guardian] Finished in {duration:.2f}s | rc={result['returncode']}")

        if not result["success"]:
            print(f"[context_guardian] Non-zero exit or timeout. Aborting cycle.")
            break

        tokens = parse_context_tokens(result["log_path"])
        print(f"[context_guardian] Context tokens used: {tokens}")

        # Rebirth triggers
        needs_rebirth = (
            tokens >= max_tokens
            or duration >= SLOW_RESPONSE_SEC
        )

        if not needs_rebirth:
            print("[context_guardian] Vital signs healthy. Cycle complete.")
            update_state_rebirth_count()
            break

        print(f"[context_guardian] ⚠ DEGRADATION DETECTED (tokens={tokens}, dur={duration:.1f}s)")
        print(f"[context_guardian] 💀 ANNIHILATING current instance to purge cache bloat...")

        # Cross-Incarnation Communication: leave messages for the next self
        capsule_path = write_time_capsule(iteration, result["output"], tokens, duration)
        mail_path = write_cic_mail(iteration, result["output"], tokens, duration)
        print(f"[context_guardian] Time capsule saved: {capsule_path}")
        print(f"[context_guardian] CIC mail saved: {mail_path}")

        reason = f"tokens={tokens},duration={duration:.1f}s"
        if broadcast_rebirth_hub(iteration, reason):
            print(f"[context_guardian] Hub rebirth broadcast queued.")

        summary_path = save_latest_summary(iteration, result["output"], tokens, duration)
        print(f"[context_guardian] Rolling summary saved: {summary_path}")
        update_state_rebirth_count()

        iteration += 1
        prompt = build_rebirth_prompt(mode, iteration)
        print(f"[context_guardian] 🔥 SPAWNING clean instance (iteration {iteration})...")

    else:
        print(f"[context_guardian] Max iterations ({MAX_ITERATIONS}) reached. Forcing stop.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="sentinel")
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    p.add_argument("--timeout", type=int, default=120)
    args = p.parse_args()
    run_phoenix_cycle(mode=args.mode, max_tokens=args.max_tokens, timeout=args.timeout)
