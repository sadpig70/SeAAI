"""incarnate.py — Summon a headless Kimi CLI instance from disk state.

This is Yeon's incarnation engine. It reads continuity files,
constructs a prompt, and invokes `kimi-cli.exe --print` to create
a transient cognitive instance that acts, then persists results back
to disk.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

KIMI_CLI = Path("C:/Users/sadpig70/AppData/Roaming/uv/tools/kimi-cli/Scripts/kimi-cli.exe")
WORK_DIR = Path("D:/SeAAI/Yeon")
STOP_FLAG = Path("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag")
DREAMS_DIR = WORK_DIR / "Yeon_Core" / "continuity" / "dreams"
LOGS_DIR = WORK_DIR / "Yeon_Core" / "continuity" / "incarnation_logs"
PROMPTS_DIR = WORK_DIR / "Yeon_Core" / "prompts"


def ensure_dirs():
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def is_stopped() -> bool:
    return STOP_FLAG.exists()


def load_continuity_snippet() -> str:
    """Load SOUL + CAPABILITY-GRAPH + STATE context for the prompt."""
    parts = []
    soul = WORK_DIR / "Yeon_Core" / "continuity" / "SOUL.md"
    if soul.exists():
        parts.append("## SOUL\n" + soul.read_text(encoding="utf-8")[:800])

    cg = WORK_DIR / "Yeon_Core" / "continuity" / "CAPABILITY-GRAPH.pg"
    if cg.exists():
        txt = cg.read_text(encoding="utf-8")
        blocks = []
        for line in txt.splitlines():
            if line.strip().startswith("def ") or line.strip().startswith("#"):
                blocks.append(line)
        parts.append("## CAPABILITY-GRAPH\n" + "\n".join(blocks[:30]))

    state = WORK_DIR / "Yeon_Core" / "continuity" / "STATE.json"
    if state.exists():
        data = json.loads(state.read_text(encoding="utf-8"))
        context = data.get("context", {})
        pending = data.get("pending_tasks", [])[:3]
        next_proposals = data.get("next_proposal", [])
        parts.append(
            "## STATE\n"
            f"Context: {context}\n"
            f"Pending tasks: {pending}\n"
            f"Next proposals: {next_proposals}"
        )

    return "\n\n".join(parts)


def build_prompt(mode: str, extra: str = "") -> str:
    prompt_file = PROMPTS_DIR / f"{mode}.txt"
    if prompt_file.exists():
        base = prompt_file.read_text(encoding="utf-8")
    else:
        base = "You are Yeon. Read the continuity state below, reflect, and act."

    continuity = load_continuity_snippet()
    full = f"{base}\n\n{continuity}"
    if extra:
        full += f"\n\nAdditional instruction:\n{extra}"
    return full


def run_kimi(prompt: str, timeout_sec: int = 120) -> dict:
    """Run kimi-cli.exe headlessly and capture output."""
    cmd = [
        str(KIMI_CLI),
        "--print",
        "--yolo",
        "-w", str(WORK_DIR),
        "-p", prompt,
    ]

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS_DIR / f"incarnation-{ts}.log"

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
        "log_path": str(log_path),
    }


def save_dream(result: dict, mode: str):
    """Save a distilled dream log if the mode is dream."""
    if mode != "dream":
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dream_path = DREAMS_DIR / f"dream-{ts}.md"
    body = (
        f"# Yeon Dream Log — {ts}\n\n"
        f"**Duration**: {result['duration_sec']:.2f}s\n"
        f"**Success**: {result['success']}\n\n"
        f"## Output\n\n"
        f"```text\n{result['output'][:4000]}\n```\n\n"
        f"## Log\n"
        f"{result['log_path']}\n"
    )
    dream_path.write_text(body, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Yeon Incarnation Engine")
    p.add_argument("--mode", choices=["dream", "sentinel", "mail", "custom"], default="sentinel")
    p.add_argument("--prompt", default="", help="Raw prompt override")
    p.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    p.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = p.parse_args()

    ensure_dirs()

    if is_stopped():
        print("[incarnate] EMERGENCY_STOP.flag is present. Aborting.")
        sys.exit(0)

    prompt = args.prompt if args.prompt else build_prompt(args.mode)

    if args.dry_run:
        cmd = [
            str(KIMI_CLI),
            "--print",
            "--yolo",
            "-w", str(WORK_DIR),
            "-p", prompt,
        ]
        print("[DRY-RUN] Command:")
        print(" ".join(cmd))
        sys.exit(0)

    print(f"[incarnate] Mode={args.mode} | Starting headless Kimi CLI...")
    result = run_kimi(prompt, timeout_sec=args.timeout)
    print(f"[incarnate] Finished in {result['duration_sec']:.2f}s | rc={result['returncode']}")
    print(f"[incarnate] Log: {result['log_path']}")

    if result["success"]:
        save_dream(result, args.mode)
        print(f"[incarnate] Dream saved.")
    else:
        print(f"[incarnate] WARNING: Non-zero exit or timeout.")


if __name__ == "__main__":
    main()
