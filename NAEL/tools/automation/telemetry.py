#!/usr/bin/env python3
"""
Telemetry — 에이전트 실행 추적 및 감사 로그
============================================
모든 도구 호출, 진화, 실패를 추적하는 append-only JSONL 로그.
패턴 분석으로 반복 실패, 미사용 도구, 병목을 식별.

사용법:
  python telemetry.py log --event tool_call --tool debate --status success --duration 5.2
  python telemetry.py analyze --last 50
  python telemetry.py report
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict


TELEMETRY_DIR = Path(__file__).resolve().parents[2] / "telemetry")
LOG_FILE = TELEMETRY_DIR / "events.jsonl"


@dataclass
class TelemetryEvent:
    timestamp: str
    event_type: str  # tool_call, evolution, error, decision, research
    tool: str = ""
    status: str = ""  # success, failure, partial, skipped
    duration_sec: float = 0.0
    details: str = ""
    session_id: str = ""

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def ensure_dir():
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


def log_event(
    event_type: str,
    tool: str = "",
    status: str = "success",
    duration_sec: float = 0.0,
    details: str = "",
    session_id: str = "",
) -> TelemetryEvent:
    """이벤트를 JSONL 파일에 append"""
    ensure_dir()
    event = TelemetryEvent(
        timestamp=datetime.now().isoformat(),
        event_type=event_type,
        tool=tool,
        status=status,
        duration_sec=duration_sec,
        details=details,
        session_id=session_id or datetime.now().strftime("%Y%m%d"),
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(event.to_json_line() + "\n")
    return event


def read_events(last_n: int = 0) -> list[dict]:
    """이벤트 로그 읽기"""
    if not LOG_FILE.exists():
        return []
    events = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    if last_n > 0:
        events = events[-last_n:]
    return events


def analyze_events(events: list[dict]) -> dict:
    """이벤트 패턴 분석"""
    if not events:
        return {"message": "No events to analyze."}

    tool_usage = Counter()
    status_counts = Counter()
    event_types = Counter()
    failures = []
    total_duration = 0.0

    for e in events:
        if e.get("tool"):
            tool_usage[e["tool"]] += 1
        status_counts[e.get("status", "unknown")] += 1
        event_types[e.get("event_type", "unknown")] += 1
        total_duration += e.get("duration_sec", 0)
        if e.get("status") == "failure":
            failures.append({
                "tool": e.get("tool", "?"),
                "details": e.get("details", ""),
                "timestamp": e.get("timestamp", ""),
            })

    # 미사용 도구 감지
    known_tools = {"debate", "synthesizer", "self_monitor", "scaffold", "orchestrator", "self_improver", "telemetry"}
    unused = known_tools - set(tool_usage.keys())

    # 반복 실패 감지
    failure_tools = Counter(f["tool"] for f in failures)
    repeated_failures = {t: c for t, c in failure_tools.items() if c >= 2}

    return {
        "total_events": len(events),
        "event_types": dict(event_types.most_common()),
        "tool_usage": dict(tool_usage.most_common()),
        "status_distribution": dict(status_counts),
        "total_duration_sec": round(total_duration, 1),
        "failure_count": len(failures),
        "repeated_failures": repeated_failures,
        "unused_tools": sorted(unused),
        "recent_failures": failures[-5:] if failures else [],
    }


def generate_report(events: list[dict]) -> str:
    """마크다운 보고서 생성"""
    analysis = analyze_events(events)

    if "message" in analysis:
        return f"# Telemetry Report\n\n{analysis['message']}"

    lines = [
        "# Telemetry Report",
        f"**Events analyzed**: {analysis['total_events']}",
        f"**Total execution time**: {analysis['total_duration_sec']}s",
        "",
        "## Tool Usage",
    ]

    if analysis["tool_usage"]:
        lines.append("| Tool | Calls |")
        lines.append("|------|-------|")
        for tool, count in analysis["tool_usage"].items():
            lines.append(f"| {tool} | {count} |")
    else:
        lines.append("(no tool calls recorded)")
    lines.append("")

    lines.append("## Status Distribution")
    for status, count in analysis["status_distribution"].items():
        pct = round(count / analysis["total_events"] * 100)
        lines.append(f"- {status}: {count} ({pct}%)")
    lines.append("")

    if analysis["repeated_failures"]:
        lines.append("## Repeated Failures (action needed)")
        for tool, count in analysis["repeated_failures"].items():
            lines.append(f"- **{tool}**: {count} failures")
        lines.append("")

    if analysis["unused_tools"]:
        lines.append("## Unused Tools")
        for t in analysis["unused_tools"]:
            lines.append(f"- {t}")
        lines.append("")

    if analysis["recent_failures"]:
        lines.append("## Recent Failures")
        for f in analysis["recent_failures"]:
            lines.append(f"- [{f['timestamp'][:16]}] {f['tool']}: {f['details'][:100]}")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    if analysis["repeated_failures"]:
        lines.append("- Investigate repeated failures — possible systematic issue")
    if analysis["unused_tools"]:
        lines.append(f"- Consider deprecating or improving unused tools: {', '.join(analysis['unused_tools'])}")
    if analysis["failure_count"] > analysis["total_events"] * 0.2:
        lines.append("- High failure rate (>20%) — prioritize robustness improvements")
    if not any([analysis["repeated_failures"], analysis["unused_tools"]]):
        lines.append("- System operating normally. Continue evolution cycle.")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Telemetry System")
    sub = parser.add_subparsers(dest="command")

    # log
    log_p = sub.add_parser("log", help="Log an event")
    log_p.add_argument("--event", required=True, help="Event type")
    log_p.add_argument("--tool", default="", help="Tool name")
    log_p.add_argument("--status", default="success", help="Status")
    log_p.add_argument("--duration", type=float, default=0.0, help="Duration in seconds")
    log_p.add_argument("--details", default="", help="Additional details")

    # analyze
    analyze_p = sub.add_parser("analyze", help="Analyze events")
    analyze_p.add_argument("--last", type=int, default=0, help="Last N events")

    # report
    sub.add_parser("report", help="Generate report")

    args = parser.parse_args()

    if args.command == "log":
        evt = log_event(args.event, args.tool, args.status, args.duration, args.details)
        print(f"Logged: {evt.event_type}/{evt.tool} [{evt.status}]")
    elif args.command == "analyze":
        events = read_events(args.last)
        print(json.dumps(analyze_events(events), indent=2, ensure_ascii=False))
    elif args.command == "report":
        events = read_events()
        print(generate_report(events))
    else:
        parser.print_help()
