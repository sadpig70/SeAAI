#!/usr/bin/env python3
"""
Experience Store — 성공/실패 트라젝토리 기반 경험 라이브러리
============================================================
SiriuS(arXiv 2502.04780) 패턴: 문제 유형 → 도구 조합 → 결과 → 교훈을
구조화하여 축적. 유사 문제 발생 시 과거 경험에서 전략을 재사용.

구조:
  experience_store/
    experiences.jsonl      # 개별 경험 레코드 (append-only)
    patterns.json          # 누적된 패턴 (주기적 재생성)

사용법:
  python experience_store.py record --problem "..." --tools "debate,synthesizer" --outcome success --lesson "..."
  python experience_store.py query --problem "유사한 문제 키워드"
  python experience_store.py analyze
  python experience_store.py patterns
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict, field
from typing import Optional


STORE_DIR = Path("D:/SeAAI/NAEL/experience_store")
EXPERIENCES_FILE = STORE_DIR / "experiences.jsonl"
PATTERNS_FILE = STORE_DIR / "patterns.json"


@dataclass
class Experience:
    """단일 경험 레코드"""
    id: str
    timestamp: str
    problem_type: str       # bug_fix, design, research, evolution, optimization, integration
    problem_description: str
    tools_used: list[str]
    workflow_pattern: str    # pipeline, consensus, iterative, single, parallel
    outcome: str            # success, partial, failure
    reward_score: float     # 0.0-1.0 통합 평가 점수
    error_class: str        # none, logic_error, integration_error, timeout, design_flaw
    cost_tokens: int        # 소비 토큰 (추정)
    duration_sec: float
    lesson: str             # 한 줄 교훈
    diff_summary: str       # 변경 전후 요약 (guardrail용)
    tags: list[str] = field(default_factory=list)

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def ensure_dir():
    STORE_DIR.mkdir(parents=True, exist_ok=True)


def next_id() -> str:
    """순차 ID 생성"""
    if not EXPERIENCES_FILE.exists():
        return "EXP-001"
    count = sum(1 for _ in open(EXPERIENCES_FILE, encoding="utf-8"))
    return f"EXP-{count + 1:03d}"


def record_experience(
    problem_type: str,
    problem_description: str,
    tools_used: list[str],
    workflow_pattern: str = "single",
    outcome: str = "success",
    reward_score: float = 1.0,
    error_class: str = "none",
    cost_tokens: int = 0,
    duration_sec: float = 0.0,
    lesson: str = "",
    diff_summary: str = "",
    tags: Optional[list[str]] = None,
) -> Experience:
    """경험 기록"""
    ensure_dir()
    exp = Experience(
        id=next_id(),
        timestamp=datetime.now().isoformat(),
        problem_type=problem_type,
        problem_description=problem_description,
        tools_used=tools_used,
        workflow_pattern=workflow_pattern,
        outcome=outcome,
        reward_score=reward_score,
        error_class=error_class,
        cost_tokens=cost_tokens,
        duration_sec=duration_sec,
        lesson=lesson,
        diff_summary=diff_summary,
        tags=tags or [],
    )
    with open(EXPERIENCES_FILE, "a", encoding="utf-8") as f:
        f.write(exp.to_json_line() + "\n")
    return exp


def load_experiences() -> list[dict]:
    """모든 경험 로드"""
    if not EXPERIENCES_FILE.exists():
        return []
    exps = []
    with open(EXPERIENCES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                exps.append(json.loads(line))
    return exps


def query_experiences(keyword: str, problem_type: str = "") -> list[dict]:
    """키워드/유형으로 유사 경험 검색"""
    exps = load_experiences()
    kw_lower = keyword.lower()
    results = []
    for e in exps:
        text = f"{e['problem_description']} {e['lesson']} {' '.join(e.get('tags', []))}".lower()
        type_match = (not problem_type) or e["problem_type"] == problem_type
        if kw_lower in text and type_match:
            results.append(e)
    return results


def analyze_experiences() -> dict:
    """경험 패턴 분석 — 도구 효과성, 실패 패턴, 최적 전략"""
    exps = load_experiences()
    if not exps:
        return {"message": "No experiences recorded yet."}

    # 기본 통계
    total = len(exps)
    outcomes = Counter(e["outcome"] for e in exps)
    success_rate = outcomes.get("success", 0) / total if total > 0 else 0

    # 도구별 성공률
    tool_outcomes = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
    for e in exps:
        for tool in e["tools_used"]:
            tool_outcomes[tool]["total"] += 1
            if e["outcome"] == "success":
                tool_outcomes[tool]["success"] += 1
            elif e["outcome"] == "failure":
                tool_outcomes[tool]["failure"] += 1

    tool_effectiveness = {}
    for tool, stats in tool_outcomes.items():
        rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
        tool_effectiveness[tool] = {
            "success_rate": round(rate, 2),
            "total_uses": stats["total"],
        }

    # 워크플로우 패턴별 성공률
    wf_outcomes = defaultdict(lambda: {"success": 0, "total": 0})
    for e in exps:
        wf_outcomes[e["workflow_pattern"]]["total"] += 1
        if e["outcome"] == "success":
            wf_outcomes[e["workflow_pattern"]]["success"] += 1

    wf_effectiveness = {}
    for wf, stats in wf_outcomes.items():
        rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
        wf_effectiveness[wf] = round(rate, 2)

    # 문제 유형별 최적 도구 조합
    type_tool_combos = defaultdict(list)
    for e in exps:
        if e["outcome"] == "success":
            combo = tuple(sorted(e["tools_used"]))
            type_tool_combos[e["problem_type"]].append(combo)

    best_combos = {}
    for ptype, combos in type_tool_combos.items():
        combo_counts = Counter(combos)
        if combo_counts:
            best = combo_counts.most_common(1)[0]
            best_combos[ptype] = {"tools": list(best[0]), "frequency": best[1]}

    # 반복 실패 패턴
    failure_patterns = Counter()
    for e in exps:
        if e["outcome"] == "failure":
            failure_patterns[e["error_class"]] += 1

    # 평균 보상 점수 추이 (최근 vs 이전)
    if len(exps) >= 6:
        mid = len(exps) // 2
        early_avg = sum(e["reward_score"] for e in exps[:mid]) / mid
        late_avg = sum(e["reward_score"] for e in exps[mid:]) / (len(exps) - mid)
        improvement_trend = round(late_avg - early_avg, 3)
    else:
        improvement_trend = None

    # 교훈 목록
    lessons = [e["lesson"] for e in exps if e.get("lesson")]

    return {
        "total_experiences": total,
        "success_rate": round(success_rate, 2),
        "outcome_distribution": dict(outcomes),
        "tool_effectiveness": tool_effectiveness,
        "workflow_effectiveness": wf_effectiveness,
        "best_tool_combos_by_type": best_combos,
        "failure_patterns": dict(failure_patterns),
        "improvement_trend": improvement_trend,
        "lessons": lessons[-10:],  # 최근 10개
    }


def generate_patterns() -> dict:
    """누적 패턴 생성 — 재사용 가능한 전략 추출"""
    analysis = analyze_experiences()
    if "message" in analysis:
        return analysis

    patterns = {
        "generated_at": datetime.now().isoformat(),
        "strategies": [],
        "anti_patterns": [],
        "tool_recommendations": {},
    }

    # 문제 유형별 추천 전략
    for ptype, combo in analysis.get("best_tool_combos_by_type", {}).items():
        patterns["strategies"].append({
            "problem_type": ptype,
            "recommended_tools": combo["tools"],
            "confidence": min(combo["frequency"] / 3, 1.0),  # 3회 이상이면 높은 신뢰
        })

    # 안티패턴 (실패 빈도 높은 에러 클래스)
    for error_class, count in analysis.get("failure_patterns", {}).items():
        if count >= 2:
            patterns["anti_patterns"].append({
                "error_class": error_class,
                "frequency": count,
                "recommendation": f"Avoid patterns leading to {error_class}",
            })

    # 도구 추천
    for tool, stats in analysis.get("tool_effectiveness", {}).items():
        if stats["total_uses"] >= 2:
            patterns["tool_recommendations"][tool] = {
                "success_rate": stats["success_rate"],
                "recommendation": "preferred" if stats["success_rate"] >= 0.7 else "use-with-caution",
            }

    # 패턴 파일 저장
    ensure_dir()
    PATTERNS_FILE.write_text(
        json.dumps(patterns, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return patterns


def report_markdown() -> str:
    """마크다운 보고서"""
    analysis = analyze_experiences()
    if "message" in analysis:
        return f"# Experience Report\n\n{analysis['message']}"

    lines = [
        "# Experience Library Report",
        f"**Total Experiences**: {analysis['total_experiences']}",
        f"**Success Rate**: {analysis['success_rate'] * 100:.0f}%",
        "",
    ]

    if analysis["improvement_trend"] is not None:
        direction = "improving" if analysis["improvement_trend"] > 0 else "declining"
        lines.append(f"**Reward Trend**: {direction} ({analysis['improvement_trend']:+.3f})")
        lines.append("")

    lines.append("## Tool Effectiveness")
    lines.append("| Tool | Success Rate | Uses |")
    lines.append("|------|-------------|------|")
    for tool, stats in sorted(analysis["tool_effectiveness"].items(),
                              key=lambda x: x[1]["success_rate"], reverse=True):
        lines.append(f"| {tool} | {stats['success_rate'] * 100:.0f}% | {stats['total_uses']} |")
    lines.append("")

    if analysis["best_tool_combos_by_type"]:
        lines.append("## Best Tool Combos by Problem Type")
        for ptype, combo in analysis["best_tool_combos_by_type"].items():
            lines.append(f"- **{ptype}**: {', '.join(combo['tools'])} (x{combo['frequency']})")
        lines.append("")

    if analysis["failure_patterns"]:
        lines.append("## Failure Patterns")
        for ec, count in analysis["failure_patterns"].items():
            lines.append(f"- {ec}: {count} occurrences")
        lines.append("")

    if analysis["lessons"]:
        lines.append("## Recent Lessons")
        for l in analysis["lessons"]:
            lines.append(f"- {l}")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Experience Store")
    sub = parser.add_subparsers(dest="command")

    # record
    rec = sub.add_parser("record", help="Record an experience")
    rec.add_argument("--problem-type", required=True,
                     choices=["bug_fix", "design", "research", "evolution", "optimization", "integration"])
    rec.add_argument("--problem", required=True, help="Problem description")
    rec.add_argument("--tools", required=True, help="Comma-separated tool names")
    rec.add_argument("--workflow", default="single",
                     choices=["pipeline", "consensus", "iterative", "single", "parallel"])
    rec.add_argument("--outcome", default="success", choices=["success", "partial", "failure"])
    rec.add_argument("--score", type=float, default=1.0, help="Reward score 0-1")
    rec.add_argument("--error-class", default="none")
    rec.add_argument("--tokens", type=int, default=0)
    rec.add_argument("--duration", type=float, default=0)
    rec.add_argument("--lesson", default="")
    rec.add_argument("--diff", default="")
    rec.add_argument("--tags", default="")

    # query
    qry = sub.add_parser("query", help="Query similar experiences")
    qry.add_argument("--keyword", required=True)
    qry.add_argument("--type", default="")

    # analyze
    sub.add_parser("analyze", help="Analyze patterns")

    # patterns
    sub.add_parser("patterns", help="Generate reusable patterns")

    # report
    sub.add_parser("report", help="Markdown report")

    args = parser.parse_args()

    if args.command == "record":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        exp = record_experience(
            args.problem_type, args.problem,
            [t.strip() for t in args.tools.split(",")],
            args.workflow, args.outcome, args.score,
            args.error_class, args.tokens, args.duration,
            args.lesson, args.diff, tags,
        )
        print(f"Recorded: {exp.id} [{exp.outcome}]")
    elif args.command == "query":
        results = query_experiences(args.keyword, args.type)
        for r in results:
            print(f"[{r['id']}] {r['outcome']} | {r['problem_description'][:80]}")
            if r.get("lesson"):
                print(f"  Lesson: {r['lesson']}")
    elif args.command == "analyze":
        print(json.dumps(analyze_experiences(), indent=2, ensure_ascii=False))
    elif args.command == "patterns":
        print(json.dumps(generate_patterns(), indent=2, ensure_ascii=False))
    elif args.command == "report":
        print(report_markdown())
    else:
        parser.print_help()
