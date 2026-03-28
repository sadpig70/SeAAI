#!/usr/bin/env python3
"""
Performance Metrics — 도구 성능 정량 측정 시스템
================================================
도구 실행의 지연시간, 품질 점수, 에러율, 사용 빈도를 수집·분석·보고.
telemetry.py와 통합되며, 메트릭 전용 JSONL로 정밀 추적.

사용법:
  python perf_metrics.py collect --tool debate --latency 1200 --quality 0.85
  python perf_metrics.py dashboard
  python perf_metrics.py dashboard --tool debate
  python perf_metrics.py trend --tool debate --last 20
  python perf_metrics.py compare
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Optional

METRICS_DIR = Path("D:/SeAAI/NAEL/metrics")
METRICS_FILE = METRICS_DIR / "metrics.jsonl"


@dataclass
class MetricRecord:
    """도구 성능 메트릭의 표준 스키마"""
    tool: str                           # 도구 이름
    timestamp: str                      # ISO 8601
    latency_ms: float                   # 실행 시간 (밀리초)
    quality_score: float                # 결과 품질 (0.0~1.0)
    error: Optional[str] = None         # 에러 메시지 (없으면 None)
    usage_context: str = ""             # 사용 맥락 (어떤 작업에서 호출)
    input_size: int = 0                 # 입력 크기 (문자 수 또는 항목 수)
    output_size: int = 0                # 출력 크기
    session_id: str = ""                # 세션 식별자

    @property
    def success(self) -> bool:
        return self.error is None

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def ensure_dir():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def collect(
    tool: str,
    latency_ms: float,
    quality_score: float = 1.0,
    error: Optional[str] = None,
    usage_context: str = "",
    input_size: int = 0,
    output_size: int = 0,
    session_id: str = "",
) -> MetricRecord:
    """메트릭 레코드를 JSONL 파일에 기록"""
    ensure_dir()
    record = MetricRecord(
        tool=tool,
        timestamp=datetime.now().isoformat(),
        latency_ms=round(latency_ms, 2),
        quality_score=round(min(max(quality_score, 0.0), 1.0), 3),
        error=error,
        usage_context=usage_context,
        input_size=input_size,
        output_size=output_size,
        session_id=session_id or datetime.now().strftime("%Y%m%d"),
    )
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(record.to_json_line() + "\n")
    return record


def read_metrics(tool: str = "", last_n: int = 0) -> list[dict]:
    """메트릭 로그 읽기"""
    if not METRICS_FILE.exists():
        return []
    records = []
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if tool and rec.get("tool") != tool:
                continue
            records.append(rec)
    if last_n > 0:
        records = records[-last_n:]
    return records


def compute_stats(records: list[dict]) -> dict:
    """메트릭 레코드 리스트의 통계 산출"""
    if not records:
        return {}

    latencies = [r["latency_ms"] for r in records]
    qualities = [r["quality_score"] for r in records if r.get("error") is None]
    errors = [r for r in records if r.get("error") is not None]

    return {
        "count": len(records),
        "error_count": len(errors),
        "error_rate": round(len(errors) / len(records), 3) if records else 0,
        "latency_avg_ms": round(sum(latencies) / len(latencies), 1),
        "latency_min_ms": round(min(latencies), 1),
        "latency_max_ms": round(max(latencies), 1),
        "latency_p50_ms": round(sorted(latencies)[len(latencies) // 2], 1),
        "quality_avg": round(sum(qualities) / len(qualities), 3) if qualities else 0,
        "quality_min": round(min(qualities), 3) if qualities else 0,
        "quality_max": round(max(qualities), 3) if qualities else 0,
    }


def dashboard(tool: str = "") -> str:
    """마크다운 대시보드 생성"""
    all_records = read_metrics()
    if not all_records:
        return "# Performance Dashboard\n\nNo metrics recorded yet."

    lines = [
        "# Performance Dashboard",
        f"**Total records**: {len(all_records)}",
        f"**Period**: {all_records[0]['timestamp'][:10]} ~ {all_records[-1]['timestamp'][:10]}",
        "",
    ]

    # 도구별 통계
    by_tool = defaultdict(list)
    for r in all_records:
        by_tool[r["tool"]].append(r)

    if tool:
        tools_to_show = {tool: by_tool.get(tool, [])}
    else:
        tools_to_show = dict(by_tool)

    lines.append("## Tool Performance Summary")
    lines.append("")
    lines.append("| Tool | Calls | Err% | Latency(avg) | Latency(p50) | Quality(avg) |")
    lines.append("|------|-------|------|-------------|-------------|-------------|")

    tool_stats = {}
    for t in sorted(tools_to_show.keys()):
        recs = tools_to_show[t]
        stats = compute_stats(recs)
        tool_stats[t] = stats
        if stats:
            lines.append(
                f"| {t} | {stats['count']} | {stats['error_rate']*100:.1f}% "
                f"| {stats['latency_avg_ms']:.0f}ms "
                f"| {stats['latency_p50_ms']:.0f}ms "
                f"| {stats['quality_avg']:.2f} |"
            )
    lines.append("")

    # 이상치 경고
    lines.append("## Alerts")
    alerts = []
    for t, stats in tool_stats.items():
        if not stats:
            continue
        if stats["error_rate"] > 0.2:
            alerts.append(f"- **{t}**: error rate {stats['error_rate']*100:.1f}% (> 20% threshold)")
        if stats["quality_avg"] < 0.6:
            alerts.append(f"- **{t}**: quality avg {stats['quality_avg']:.2f} (< 0.6 threshold)")
        if stats["latency_max_ms"] > stats["latency_avg_ms"] * 5:
            alerts.append(f"- **{t}**: latency spike detected (max {stats['latency_max_ms']:.0f}ms vs avg {stats['latency_avg_ms']:.0f}ms)")

    if alerts:
        lines.extend(alerts)
    else:
        lines.append("No alerts. All tools operating within normal parameters.")
    lines.append("")

    # 랭킹
    if len(tool_stats) > 1:
        lines.append("## Rankings")
        ranked_quality = sorted(
            [(t, s) for t, s in tool_stats.items() if s and s.get("quality_avg", 0) > 0],
            key=lambda x: x[1]["quality_avg"], reverse=True,
        )
        if ranked_quality:
            lines.append("**Quality (best → worst):** " + " > ".join(
                f"{t}({s['quality_avg']:.2f})" for t, s in ranked_quality
            ))
        ranked_speed = sorted(
            [(t, s) for t, s in tool_stats.items() if s],
            key=lambda x: x[1]["latency_avg_ms"],
        )
        if ranked_speed:
            lines.append("**Speed (fastest → slowest):** " + " > ".join(
                f"{t}({s['latency_avg_ms']:.0f}ms)" for t, s in ranked_speed
            ))
        lines.append("")

    return "\n".join(lines)


def trend(tool: str, last_n: int = 20) -> str:
    """도구별 성능 추이 (텍스트 시각화)"""
    records = read_metrics(tool=tool, last_n=last_n)
    if not records:
        return f"No metrics for tool '{tool}'."

    lines = [
        f"# Performance Trend: {tool}",
        f"**Last {len(records)} records**",
        "",
        "## Quality Trend",
    ]

    # 텍스트 바 차트
    for r in records:
        ts = r["timestamp"][5:16]  # MM-DDTHH:MM
        q = r["quality_score"]
        bar_len = int(q * 30)
        bar = "#" * bar_len + "." * (30 - bar_len)
        err = " ERR" if r.get("error") else ""
        lines.append(f"  {ts} |{bar}| {q:.2f}{err}")

    lines.append("")
    lines.append("## Latency Trend")

    max_lat = max(r["latency_ms"] for r in records) if records else 1
    for r in records:
        ts = r["timestamp"][5:16]
        lat = r["latency_ms"]
        bar_len = int((lat / max_lat) * 30) if max_lat > 0 else 0
        bar = "#" * bar_len + "." * (30 - bar_len)
        lines.append(f"  {ts} |{bar}| {lat:.0f}ms")

    lines.append("")

    # 추이 판단
    if len(records) >= 4:
        first_half = records[:len(records)//2]
        second_half = records[len(records)//2:]
        q_first = sum(r["quality_score"] for r in first_half) / len(first_half)
        q_second = sum(r["quality_score"] for r in second_half) / len(second_half)
        l_first = sum(r["latency_ms"] for r in first_half) / len(first_half)
        l_second = sum(r["latency_ms"] for r in second_half) / len(second_half)

        lines.append("## Trend Analysis")
        q_delta = q_second - q_first
        l_delta = l_second - l_first
        q_dir = "improving" if q_delta > 0.02 else ("degrading" if q_delta < -0.02 else "stable")
        l_dir = "improving" if l_delta < -50 else ("degrading" if l_delta > 50 else "stable")
        lines.append(f"- Quality: {q_dir} ({q_first:.2f} → {q_second:.2f}, delta={q_delta:+.3f})")
        lines.append(f"- Latency: {l_dir} ({l_first:.0f}ms → {l_second:.0f}ms, delta={l_delta:+.0f}ms)")

    return "\n".join(lines)


def compare_tools() -> str:
    """모든 도구 성능 비교"""
    all_records = read_metrics()
    if not all_records:
        return "No metrics to compare."

    by_tool = defaultdict(list)
    for r in all_records:
        by_tool[r["tool"]].append(r)

    lines = [
        "# Tool Performance Comparison",
        "",
        "| Tool | Calls | Err% | Latency(avg) | Quality(avg) | Score |",
        "|------|-------|------|-------------|-------------|-------|",
    ]

    scored = []
    for t in sorted(by_tool.keys()):
        stats = compute_stats(by_tool[t])
        if not stats:
            continue
        # 종합 점수: quality 70% + (1 - error_rate) 20% + speed_norm 10%
        score = (
            stats["quality_avg"] * 0.7
            + (1 - stats["error_rate"]) * 0.2
            + max(0, 1 - stats["latency_avg_ms"] / 10000) * 0.1
        )
        scored.append((t, stats, round(score, 3)))

    scored.sort(key=lambda x: x[2], reverse=True)

    for t, stats, score in scored:
        lines.append(
            f"| {t} | {stats['count']} | {stats['error_rate']*100:.1f}% "
            f"| {stats['latency_avg_ms']:.0f}ms "
            f"| {stats['quality_avg']:.2f} "
            f"| {score:.3f} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Performance Metrics System")
    sub = parser.add_subparsers(dest="command")

    # collect
    col_p = sub.add_parser("collect", help="Record a metric")
    col_p.add_argument("--tool", required=True, help="Tool name")
    col_p.add_argument("--latency", type=float, required=True, help="Latency in ms")
    col_p.add_argument("--quality", type=float, default=1.0, help="Quality score 0-1")
    col_p.add_argument("--error", default=None, help="Error message if failed")
    col_p.add_argument("--context", default="", help="Usage context")

    # dashboard
    dash_p = sub.add_parser("dashboard", help="Generate dashboard")
    dash_p.add_argument("--tool", default="", help="Filter by tool")

    # trend
    trend_p = sub.add_parser("trend", help="Show performance trend")
    trend_p.add_argument("--tool", required=True, help="Tool name")
    trend_p.add_argument("--last", type=int, default=20, help="Last N records")

    # compare
    sub.add_parser("compare", help="Compare all tools")

    args = parser.parse_args()

    if args.command == "collect":
        rec = collect(args.tool, args.latency, args.quality, args.error, args.context)
        print(f"Recorded: {rec.tool} latency={rec.latency_ms}ms quality={rec.quality_score}")
    elif args.command == "dashboard":
        print(dashboard(args.tool))
    elif args.command == "trend":
        print(trend(args.tool, args.last))
    elif args.command == "compare":
        print(compare_tools())
    else:
        parser.print_help()
