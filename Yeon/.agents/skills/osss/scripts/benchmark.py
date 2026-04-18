#!/usr/bin/env python3
"""OSSS Benchmark Runner — 후보 프롬프트 벤치마크 실행 및 점수 산출"""

import json
import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import statistics

def find_osss_dir():
    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        osss = p / ".osss"
        if osss.exists():
            return osss
    return cwd / ".osss"

def load_candidates(osss_dir, task_class=None):
    """candidate 상태 레코드 로드"""
    registry = osss_dir / "registry"
    candidates = []
    for f in registry.glob("*.json"):
        try:
            with open(f) as fh:
                data = json.load(fh)
            items = data if isinstance(data, list) else [data]
            for rec in items:
                if rec.get("status") == "candidate":
                    if task_class and rec.get("task_class") != task_class:
                        continue
                    candidates.append(rec)
        except Exception:
            pass
    return candidates

def build_runtime_command(runtime: str, task_prompt: str, system_prompt: str) -> list:
    """런타임별 서브에이전트 스폰 명령 구성"""
    if runtime == "claude_code_cli":
        return ["claude", "-p", task_prompt, "--system-prompt", system_prompt]
    elif runtime == "kimi_cli":
        # Kimi CLI: uv tool run kimi --yolo -p <workspace> + system prompt via env or inline
        # 현재는 prompt에 system prompt를 prepend하는 방식
        combined_prompt = f"[System]\n{system_prompt}\n\n[Task]\n{task_prompt}"
        return ["uv", "tool", "run", "kimi", "--yolo", "-p", ".", combined_prompt]
    elif runtime == "codex_cli":
        return ["codex", "-q", task_prompt, "--system-prompt", system_prompt]
    else:
        # fallback: local python stub
        return ["python", "-c", f"print('Runtime {runtime} not supported in this environment')"]


def run_single(system_prompt, task_prompt, run_dir, run_idx, runtime="claude_code_cli"):
    """단일 벤치마크 실행 (런타임별)"""
    run_dir.mkdir(parents=True, exist_ok=True)
    log_file = run_dir / f"run-{run_idx}.log"
    result_file = run_dir / f"result-{run_idx}.json"

    cmd = build_runtime_command(runtime, task_prompt, system_prompt)
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300
        )
        elapsed = time.time() - start

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== CMD ===\n{' '.join(cmd)}\n")
            f.write(f"=== STDOUT ===\n{result.stdout}\n")
            f.write(f"=== STDERR ===\n{result.stderr}\n")
            f.write(f"=== EXIT CODE: {result.returncode} ===\n")
            f.write(f"=== ELAPSED: {elapsed:.1f}s ===\n")

        success = result.returncode == 0
        run_result = {
            "run_idx": run_idx,
            "success": success,
            "exit_code": result.returncode,
            "elapsed_seconds": round(elapsed, 1),
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
            "runtime": runtime,
        }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== TIMEOUT ===\n")
        run_result = {
            "run_idx": run_idx,
            "success": False,
            "exit_code": -1,
            "elapsed_seconds": round(elapsed, 1),
            "timeout": True,
            "runtime": runtime,
        }
    except FileNotFoundError as e:
        print(f"[ERROR] Runtime command not found: {e}. Command: {cmd}", file=sys.stderr)
        run_result = {
            "run_idx": run_idx,
            "success": False,
            "exit_code": -2,
            "elapsed_seconds": 0,
            "error": f"CLI not found: {cmd[0]}",
            "runtime": runtime,
        }

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(run_result, f, indent=2, ensure_ascii=False)

    return run_result

def analyze_failures(run_dir, n_runs):
    """실행 로그에서 실패 패턴 추출"""
    patterns = []
    
    for i in range(n_runs):
        log_file = run_dir / f"run-{i}.log"
        if not log_file.exists():
            continue
        
        content = log_file.read_text()
        lines = content.split("\n")
        
        # 동일 명령 반복 탐지
        commands = [l.strip() for l in lines if l.startswith("$") or l.startswith(">")]
        cmd_counts = Counter(commands)
        if any(c >= 3 for c in cmd_counts.values()):
            patterns.append("infinite_retry_loop")
        
        # Timeout 탐지
        if "TIMEOUT" in content:
            patterns.append("premature_termination")
    
    return list(set(patterns))

def compute_scores(results, max_time=300):
    """결과 목록에서 OSSS 점수 산출"""
    n = len(results)
    if n == 0:
        return {"osss_score": 0, "success_rate": 0, "stability": 0,
                "recovery": 0, "compliance": 0, "speed": 0, "n_runs": 0}
    
    # success_rate
    successes = sum(1 for r in results if r.get("success"))
    success_rate = successes / n
    
    # stability
    scores = [1.0 if r.get("success") else 0.0 for r in results]
    if len(scores) > 1:
        std = statistics.stdev(scores)
        stability = 1 - min(std / 0.5, 1.0)  # 0.5 = max reasonable std for binary
    else:
        stability = 1.0 if successes == n else 0.0
    
    # recovery (simplified: 실패 후 성공한 비율)
    failures = sum(1 for r in results if not r.get("success"))
    recovery = 1.0 if failures == 0 else 0.5  # 단순화 — 실제로는 로그 분석 필요
    
    # compliance (simplified: exit code 0 비율)
    compliance = success_rate  # 기본적으로 성공률과 동일, 상세 분석 시 별도 계산
    
    # speed
    times = [r.get("elapsed_seconds", max_time) for r in results]
    avg_time = statistics.mean(times) if times else max_time
    speed = max(0, 1 - (avg_time / max_time))
    
    osss_score = (
        success_rate * 0.4 +
        stability    * 0.2 +
        recovery     * 0.15 +
        compliance   * 0.15 +
        speed        * 0.1
    )
    
    return {
        "osss_score": round(osss_score, 3),
        "success_rate": round(success_rate, 3),
        "stability": round(stability, 3),
        "recovery": round(recovery, 3),
        "compliance": round(compliance, 3),
        "speed": round(speed, 3),
        "n_runs": n
    }

def run_benchmark(osss_dir, task_prompt, n_runs=10, task_class=None, runtime="claude_code_cli"):
    """전체 벤치마크 실행"""
    candidates = load_candidates(osss_dir, task_class)
    if not candidates:
        print("No candidate records found in registry.")
        return

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    tc = task_class or candidates[0].get("task_class", "unknown")
    bench_dir = osss_dir / "benchmarks" / f"{ts}_{tc}"
    bench_dir.mkdir(parents=True, exist_ok=True)

    print(f"Benchmark: {len(candidates)} candidates × {n_runs} runs")
    print(f"Runtime: {runtime}")
    print(f"Output: {bench_dir}\n")

    summary = {
        "benchmark_id": f"{ts}_{tc}",
        "task_class": tc,
        "task_prompt": task_prompt,
        "runtime": runtime,
        "candidates": [],
    }

    best_score = -1
    best_version = None

    for ci, cand in enumerate(candidates):
        ver = cand.get("prompt_version", f"v0.{ci}.0")
        prompt = cand.get("system_prompt", "")
        cand_dir = bench_dir / f"candidate-{ci}"

        print(f"[{ci+1}/{len(candidates)}] {ver} ({cand.get('pattern', '?')})...")

        results = []
        for ri in range(n_runs):
            r = run_single(prompt, task_prompt, cand_dir, ri, runtime=runtime)
            status = "✓" if r.get("success") else "✗"
            print(f"  Run {ri+1}/{n_runs}: {status} ({r.get('elapsed_seconds', '?')}s)")
            results.append(r)

        scores = compute_scores(results)
        failure_patterns = analyze_failures(cand_dir, n_runs)

        cand_summary = {
            "prompt_version": ver,
            "pattern": cand.get("pattern", "unknown"),
            "n_runs": n_runs,
            "scores": scores,
            "failure_patterns": failure_patterns,
            "selected": False,
        }
        summary["candidates"].append(cand_summary)

        if scores["osss_score"] > best_score:
            best_score = scores["osss_score"]
            best_version = ver

        print(f"  Score: {scores['osss_score']:.3f}\n")

    # 최고 점수 후보 마킹
    for cs in summary["candidates"]:
        if cs["prompt_version"] == best_version:
            cs["selected"] = True

    summary["winner"] = best_version

    with open(bench_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Winner: {best_version} (score: {best_score:.3f})")
    print(f"Summary: {bench_dir / 'summary.json'}")

    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage: benchmark.py run --task-prompt <prompt> [--runs N] [--task-class <class>] [--runtime <runtime>]")
        print("       benchmark.py score --results-dir <dir>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    osss_dir = find_osss_dir()
    
    if cmd == "run":
        args = {}
        i = 2
        while i < len(sys.argv) - 1:
            args[sys.argv[i]] = sys.argv[i+1]
            i += 2

        task_prompt = args.get("--task-prompt", "")
        n_runs = int(args.get("--runs", "10"))
        task_class = args.get("--task-class")
        runtime = args.get("--runtime", "claude_code_cli")

        if not task_prompt:
            print("--task-prompt is required")
            sys.exit(1)

        run_benchmark(osss_dir, task_prompt, n_runs, task_class, runtime=runtime)
    
    elif cmd == "score":
        # 기존 결과에서 점수 재계산
        args = {}
        i = 2
        while i < len(sys.argv) - 1:
            args[sys.argv[i]] = sys.argv[i+1]
            i += 2
        
        results_dir = Path(args.get("--results-dir", "."))
        results = []
        for f in sorted(results_dir.glob("result-*.json")):
            with open(f) as fh:
                results.append(json.load(fh))
        
        scores = compute_scores(results)
        print(json.dumps(scores, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
