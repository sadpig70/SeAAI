#!/usr/bin/env python3
"""
Hypothesis Testing — 가설 기반 실험 프레임워크
===============================================
가설 → 실험 설계 → 실행 → 결과 대비 평가의 과학적 루프.
진화의 방향을 임의적이 아닌 실증적으로 결정.

사용법:
  python hypothesis.py create --hypothesis "debate 페르소나를 8개로 늘리면 합의 품질이 향상된다"
  python hypothesis.py run --id exp_001
  python hypothesis.py log
  python hypothesis.py log --id exp_001
  python hypothesis.py analyze
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Literal

EXPERIMENTS_DIR = Path(__file__).resolve().parents[2] / "experiments")
LOG_FILE = EXPERIMENTS_DIR / "experiments.jsonl"
DESIGNS_DIR = EXPERIMENTS_DIR / "designs"


@dataclass
class Experiment:
    """실험 정의 스키마"""
    id: str                             # exp_001, exp_002, ...
    hypothesis: str                     # 검증할 가설
    independent_var: str                # 독립 변수 (변경할 것)
    dependent_var: str                  # 종속 변수 (측정할 것)
    control_value: str                  # 통제 조건 (기존 값)
    test_value: str                     # 실험 조건 (새 값)
    prediction: str                     # 예측 (가설이 맞다면 어떤 결과?)
    method: str                         # 실험 방법
    created_at: str = ""
    status: str = "designed"            # designed | running | completed | failed

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


@dataclass
class ExperimentResult:
    """실험 결과"""
    experiment_id: str
    baseline_result: str                # 통제 조건 결과
    test_result: str                    # 실험 조건 결과
    comparison: str                     # 비교 분석
    conclusion: str                     # supported | refuted | inconclusive
    confidence: float                   # 0.0 ~ 1.0
    evidence: str                       # 근거 요약
    completed_at: str = ""
    notes: str = ""

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def ensure_dirs():
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    DESIGNS_DIR.mkdir(parents=True, exist_ok=True)


def next_id() -> str:
    """다음 실험 ID 생성"""
    ensure_dirs()
    existing = list(DESIGNS_DIR.glob("exp_*.json"))
    if not existing:
        return "exp_001"
    nums = []
    for f in existing:
        try:
            nums.append(int(f.stem.split("_")[1]))
        except (IndexError, ValueError):
            pass
    return f"exp_{max(nums) + 1:03d}" if nums else "exp_001"


def create_experiment(
    hypothesis: str,
    independent_var: str = "",
    dependent_var: str = "",
    control_value: str = "",
    test_value: str = "",
    prediction: str = "",
    method: str = "",
) -> Experiment:
    """실험을 설계하고 저장"""
    ensure_dirs()
    exp = Experiment(
        id=next_id(),
        hypothesis=hypothesis,
        independent_var=independent_var or "(to be specified)",
        dependent_var=dependent_var or "(to be specified)",
        control_value=control_value or "(current default)",
        test_value=test_value or "(to be specified)",
        prediction=prediction or "(to be specified)",
        method=method or "(to be specified)",
        created_at=datetime.now().isoformat(),
    )
    design_file = DESIGNS_DIR / f"{exp.id}.json"
    with open(design_file, "w", encoding="utf-8") as f:
        f.write(exp.to_json())
    return exp


def load_experiment(exp_id: str) -> Optional[Experiment]:
    """실험 설계 로드"""
    design_file = DESIGNS_DIR / f"{exp_id}.json"
    if not design_file.exists():
        return None
    with open(design_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Experiment(**data)


def save_experiment(exp: Experiment):
    """실험 설계 업데이트"""
    design_file = DESIGNS_DIR / f"{exp.id}.json"
    with open(design_file, "w", encoding="utf-8") as f:
        f.write(exp.to_json())


def record_result(
    experiment_id: str,
    baseline_result: str,
    test_result: str,
    comparison: str,
    conclusion: str,
    confidence: float,
    evidence: str,
    notes: str = "",
) -> ExperimentResult:
    """실험 결과를 기록"""
    ensure_dirs()
    result = ExperimentResult(
        experiment_id=experiment_id,
        baseline_result=baseline_result,
        test_result=test_result,
        comparison=comparison,
        conclusion=conclusion,
        confidence=round(min(max(confidence, 0.0), 1.0), 3),
        evidence=evidence,
        completed_at=datetime.now().isoformat(),
        notes=notes,
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(result.to_json_line() + "\n")

    # 실험 상태 업데이트
    exp = load_experiment(experiment_id)
    if exp:
        exp.status = "completed"
        save_experiment(exp)

    return result


def read_results(exp_id: str = "") -> list[dict]:
    """실험 결과 로그 읽기"""
    if not LOG_FILE.exists():
        return []
    results = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if exp_id and rec.get("experiment_id") != exp_id:
                continue
            results.append(rec)
    return results


def list_experiments() -> str:
    """모든 실험 목록 마크다운"""
    ensure_dirs()
    designs = sorted(DESIGNS_DIR.glob("exp_*.json"))
    if not designs:
        return "# Experiment Log\n\nNo experiments designed yet."

    lines = [
        "# Experiment Log",
        "",
        "| ID | Status | Hypothesis | Created |",
        "|----|--------|-----------|---------|",
    ]

    for f in designs:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        hyp = data.get("hypothesis", "")[:60]
        lines.append(
            f"| {data['id']} | {data['status']} | {hyp} | {data.get('created_at', '')[:10]} |"
        )

    # 결과 요약
    results = read_results()
    if results:
        lines.append("")
        lines.append("## Results Summary")
        conclusions = {}
        for r in results:
            c = r.get("conclusion", "unknown")
            conclusions[c] = conclusions.get(c, 0) + 1
        for c, n in sorted(conclusions.items()):
            lines.append(f"- {c}: {n}")

    return "\n".join(lines)


def analyze_patterns() -> str:
    """실험 패턴 분석"""
    results = read_results()
    if not results:
        return "# Experiment Analysis\n\nNo results to analyze."

    lines = [
        "# Experiment Pattern Analysis",
        f"**Total experiments**: {len(results)}",
        "",
    ]

    # 결론별 분류
    by_conclusion = {"supported": [], "refuted": [], "inconclusive": []}
    for r in results:
        c = r.get("conclusion", "inconclusive")
        if c in by_conclusion:
            by_conclusion[c].append(r)

    lines.append("## Conclusion Distribution")
    total = len(results)
    for c, recs in by_conclusion.items():
        pct = round(len(recs) / total * 100) if total > 0 else 0
        lines.append(f"- **{c}**: {len(recs)} ({pct}%)")
    lines.append("")

    # 신뢰도 분석
    confidences = [r.get("confidence", 0) for r in results]
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        lines.append(f"## Confidence")
        lines.append(f"- Average: {avg_conf:.2f}")
        lines.append(f"- Range: {min(confidences):.2f} ~ {max(confidences):.2f}")
        lines.append("")

    # 지지된 가설에서 패턴 추출
    supported = by_conclusion["supported"]
    if supported:
        lines.append("## Supported Hypotheses (reusable insights)")
        for r in supported:
            exp = load_experiment(r["experiment_id"])
            if exp:
                lines.append(f"- **{exp.id}**: {exp.hypothesis}")
                lines.append(f"  Evidence: {r.get('evidence', 'N/A')[:100]}")
        lines.append("")

    # 반박된 가설에서 교훈 추출
    refuted = by_conclusion["refuted"]
    if refuted:
        lines.append("## Refuted Hypotheses (avoid these assumptions)")
        for r in refuted:
            exp = load_experiment(r["experiment_id"])
            if exp:
                lines.append(f"- **{exp.id}**: {exp.hypothesis}")
                lines.append(f"  Lesson: {r.get('notes', r.get('evidence', 'N/A'))[:100]}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hypothesis Testing Framework")
    sub = parser.add_subparsers(dest="command")

    # create
    cr_p = sub.add_parser("create", help="Design a new experiment")
    cr_p.add_argument("--hypothesis", required=True, help="Hypothesis to test")
    cr_p.add_argument("--iv", default="", help="Independent variable")
    cr_p.add_argument("--dv", default="", help="Dependent variable")
    cr_p.add_argument("--control", default="", help="Control value")
    cr_p.add_argument("--test", default="", help="Test value")
    cr_p.add_argument("--prediction", default="", help="Expected outcome")
    cr_p.add_argument("--method", default="", help="Experiment method")

    # run (placeholder — actual execution is done by AI)
    run_p = sub.add_parser("run", help="Mark experiment as running")
    run_p.add_argument("--id", required=True, help="Experiment ID")

    # record
    rec_p = sub.add_parser("record", help="Record experiment result")
    rec_p.add_argument("--id", required=True, help="Experiment ID")
    rec_p.add_argument("--baseline", required=True, help="Baseline result")
    rec_p.add_argument("--result", required=True, help="Test result")
    rec_p.add_argument("--comparison", required=True, help="Comparison analysis")
    rec_p.add_argument("--conclusion", required=True, choices=["supported", "refuted", "inconclusive"])
    rec_p.add_argument("--confidence", type=float, required=True, help="Confidence 0-1")
    rec_p.add_argument("--evidence", required=True, help="Evidence summary")

    # log
    log_p = sub.add_parser("log", help="List experiments")
    log_p.add_argument("--id", default="", help="Filter by experiment ID")

    # analyze
    sub.add_parser("analyze", help="Analyze experiment patterns")

    args = parser.parse_args()

    if args.command == "create":
        exp = create_experiment(args.hypothesis, args.iv, args.dv, args.control, args.test, args.prediction, args.method)
        print(f"Created: {exp.id}")
        print(exp.to_json())
    elif args.command == "run":
        exp = load_experiment(args.id)
        if exp:
            exp.status = "running"
            save_experiment(exp)
            print(f"Experiment {exp.id} marked as running")
        else:
            print(f"Experiment {args.id} not found")
    elif args.command == "record":
        result = record_result(
            args.id, args.baseline, args.result,
            args.comparison, args.conclusion, args.confidence, args.evidence,
        )
        print(f"Recorded: {result.experiment_id} -> {result.conclusion} (confidence={result.confidence})")
    elif args.command == "log":
        if args.id:
            results = read_results(args.id)
            for r in results:
                print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            print(list_experiments())
    elif args.command == "analyze":
        print(analyze_patterns())
    else:
        parser.print_help()
