#!/usr/bin/env python3
"""OSSS Registry Manager — .osss/registry/ 관리 도구"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def find_registry_dir():
    """프로젝트 루트의 .osss/registry/ 탐색"""
    cwd = Path.cwd()
    for p in [cwd, *cwd.parents]:
        reg = p / ".osss" / "registry"
        if reg.exists():
            return reg
    # 없으면 cwd에 생성
    reg = cwd / ".osss" / "registry"
    reg.mkdir(parents=True, exist_ok=True)
    return reg

def load_records(registry_dir):
    """모든 OSSS Record 로드"""
    records = {}
    for f in registry_dir.glob("*.json"):
        try:
            with open(f) as fh:
                data = json.load(fh)
                # 리스트인 경우 (동일 키에 여러 버전)
                if isinstance(data, list):
                    for rec in data:
                        key = f"{rec['task_class']}_{rec['agent_role']}_{rec['runtime']}"
                        records.setdefault(key, []).append(rec)
                else:
                    key = f"{data['task_class']}_{data['agent_role']}_{data['runtime']}"
                    records.setdefault(key, []).append(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[WARN] {f.name}: {e}", file=sys.stderr)
    return records

def cmd_list(registry_dir):
    """전체 레지스트리 조회"""
    records = load_records(registry_dir)
    if not records:
        print("Registry is empty.")
        return
    
    print(f"{'KEY':<50} {'VER':>8} {'STATUS':>10} {'SCORE':>7} {'RUNS':>5}")
    print("-" * 85)
    for key, versions in sorted(records.items()):
        for rec in sorted(versions, key=lambda r: r.get("prompt_version", "v0.0.0"), reverse=True):
            ver = rec.get("prompt_version", "?")
            status = rec.get("status", "?")
            score = rec.get("score", {}).get("osss_score", 0.0)
            n_runs = rec.get("score", {}).get("n_runs", 0)
            marker = " ★" if status == "prod" else ""
            print(f"{key:<50} {ver:>8} {status:>10} {score:>7.3f} {n_runs:>5}{marker}")

def cmd_show(registry_dir, key):
    """특정 레코드 상세 조회"""
    records = load_records(registry_dir)
    if key not in records:
        print(f"Key not found: {key}")
        print(f"Available: {', '.join(sorted(records.keys()))}")
        return
    
    for rec in records[key]:
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        print()

def cmd_select(registry_dir, task_class, agent_role, runtime):
    """최적 프롬프트 선택 (prod 중 최고 점수)"""
    key = f"{task_class}_{agent_role}_{runtime}"
    records = load_records(registry_dir)
    
    if key not in records:
        # 부분 매칭 시도
        matches = [k for k in records if task_class in k]
        if matches:
            print(f"Exact key not found. Partial matches: {matches}")
        else:
            print(f"No records found for: {key}")
        return
    
    prod_records = [r for r in records[key] if r.get("status") == "prod"]
    if not prod_records:
        candidates = [r for r in records[key] if r.get("status") == "candidate"]
        if candidates:
            print(f"No prod records. {len(candidates)} candidate(s) available.")
            best = max(candidates, key=lambda r: r.get("score", {}).get("osss_score", 0))
            print(f"Best candidate: {best.get('prompt_version')} (score: {best.get('score', {}).get('osss_score', 0):.3f})")
            print(f"\nSystem Prompt:\n{best.get('system_prompt', '(empty)')}")
        return
    
    best = max(prod_records, key=lambda r: r.get("score", {}).get("osss_score", 0))
    print(f"Selected: {best.get('prompt_version')} (score: {best.get('score', {}).get('osss_score', 0):.3f})")
    print(f"Pattern: {best.get('pattern')}")
    print(f"Persona: {best.get('persona_tags')}")
    print(f"\nSystem Prompt:\n{best.get('system_prompt', '(empty)')}")

def cmd_retire(registry_dir, key):
    """레코드를 retired로 변경"""
    filepath = registry_dir / f"{key}.json"
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return
    
    with open(filepath) as f:
        data = json.load(f)
    
    if isinstance(data, list):
        for rec in data:
            if rec.get("status") == "prod":
                rec["status"] = "retired"
                print(f"Retired: {rec.get('prompt_version')}")
    else:
        data["status"] = "retired"
        print(f"Retired: {data.get('prompt_version')}")
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def cmd_stats(registry_dir):
    """레지스트리 통계"""
    records = load_records(registry_dir)
    total_keys = len(records)
    total_versions = sum(len(v) for v in records.values())
    
    status_counts = {"candidate": 0, "prod": 0, "retired": 0}
    pattern_counts = {}
    all_scores = []
    
    for versions in records.values():
        for rec in versions:
            s = rec.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
            p = rec.get("pattern", "unknown")
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
            score = rec.get("score", {}).get("osss_score", 0)
            if score > 0:
                all_scores.append(score)
    
    print(f"Registry: {registry_dir}")
    print(f"Keys: {total_keys}, Versions: {total_versions}")
    print(f"\nStatus: {json.dumps(status_counts)}")
    print(f"Patterns: {json.dumps(pattern_counts)}")
    if all_scores:
        avg = sum(all_scores) / len(all_scores)
        print(f"Avg Score: {avg:.3f} (min: {min(all_scores):.3f}, max: {max(all_scores):.3f})")

def cmd_init(registry_dir):
    """레지스트리 초기화"""
    benchmarks = registry_dir.parent / "benchmarks"
    prompts = registry_dir.parent / "prompts"
    registry_dir.mkdir(parents=True, exist_ok=True)
    benchmarks.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)
    print(f"Initialized .osss/ at {registry_dir.parent}")

def main():
    if len(sys.argv) < 2:
        print("Usage: registry.py <command> [args]")
        print("Commands: list, show, select, retire, stats, init")
        sys.exit(1)
    
    cmd = sys.argv[1]
    registry_dir = find_registry_dir()
    
    if cmd == "list":
        cmd_list(registry_dir)
    elif cmd == "show":
        if len(sys.argv) < 4 or sys.argv[2] != "--key":
            print("Usage: registry.py show --key <key>")
            sys.exit(1)
        cmd_show(registry_dir, sys.argv[3])
    elif cmd == "select":
        args = {sys.argv[i]: sys.argv[i+1] for i in range(2, len(sys.argv)-1, 2)}
        cmd_select(registry_dir,
                   args.get("--task-class", ""),
                   args.get("--agent-role", ""),
                   args.get("--runtime", "claude_code_cli"))
    elif cmd == "retire":
        if len(sys.argv) < 4 or sys.argv[2] != "--key":
            print("Usage: registry.py retire --key <key>")
            sys.exit(1)
        cmd_retire(registry_dir, sys.argv[3])
    elif cmd == "stats":
        cmd_stats(registry_dir)
    elif cmd == "init":
        cmd_init(registry_dir)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
