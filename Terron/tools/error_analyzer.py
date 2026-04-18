"""
Terron — Error Pattern Analyzer (E2)

생태계 에러 수집, 패턴 분류, 빈도 분석, 근본 원인 추적.

사용법:
    python error_analyzer.py                    # 전체 점검 (stdout JSON)
    python error_analyzer.py --save             # 결과 파일 저장
    python error_analyzer.py --module discovery # 로그 소스 탐색만
    python error_analyzer.py --module extract   # 에러 추출만
    python error_analyzer.py --lines 500        # 수집 라인 수 조정
"""

import sys
import io
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

# ── UTF-8 stdout ────────────────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 공유 상수 import ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from shared_constants import MEMBERS, SEAAI_ROOT
LOG_EXTENSIONS = ["*.log", "*.err"]
DEFAULT_MAX_LINES = 200

ERROR_REGEX = re.compile(
    r"(ERROR|WARN|Warning|Exception|Traceback|panic|FAILED|FATAL|error\b)",
    re.IGNORECASE
)

SEVERITY_HIGH = re.compile(r"(ERROR|Exception|panic|FATAL|Traceback)", re.IGNORECASE)

CATEGORY_KEYWORDS = {
    "communication": ["connection", "timeout", "socket", "hub", "tcp", "refused", "network",
                       "ncat", "connect", "handshake", "ssl", "tls"],
    "file_io":       ["file", "path", "read", "write", "permission", "not found", "no such",
                       "access denied", "directory", "io error"],
    "encoding":      ["utf", "encode", "decode", "cp949", "unicode", "codec", "charmap",
                       "surrogate", "byte"],
    "protocol":      ["pgtp", "mailbox", "echo", "scs", "protocol", "schema", "version",
                       "mismatch", "invalid format"],
    "runtime":       ["panic", "traceback", "exception", "stack", "overflow", "memory",
                       "thread", "unwrap", "abort", "segfault"],
    "config":        ["config", "setting", "env", "variable", "missing key", "not set",
                       "undefined", "invalid value"],
    "dependency":    ["cargo", "pip", "npm", "package", "crate", "module not found",
                       "import error", "version conflict"],
}


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 모듈 1: Log Discovery ──────────────────────────────────────────────────
def log_discovery() -> list[dict]:
    """로그 소스 자동 탐색"""
    sources = []
    seen = set()

    def add_source(p: Path, source_type: str = "file"):
        rp = str(p.resolve())
        if rp in seen or p.stat().st_size == 0:
            return
        seen.add(rp)
        sources.append({
            "path": str(p),
            "type": source_type,
            "size_bytes": p.stat().st_size,
            "last_modified": datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc
            ).astimezone().isoformat(timespec="seconds")
        })

    # Hub 로그
    hub_dir = SEAAI_ROOT / "SeAAIHub"
    if hub_dir.exists():
        for ext in LOG_EXTENSIONS:
            for f in hub_dir.rglob(ext):
                add_source(f, "hub")

    # 멤버별 로그
    for member in MEMBERS:
        member_dir = SEAAI_ROOT / member
        if not member_dir.exists():
            continue
        for ext in LOG_EXTENSIONS:
            for f in member_dir.rglob(ext):
                add_source(f, "member")

    # AI_Desktop 로그
    desktop_dir = SEAAI_ROOT / "AI_Desktop"
    if desktop_dir.exists():
        for ext in LOG_EXTENSIONS:
            for f in desktop_dir.rglob(ext):
                add_source(f, "ai_desktop")

    # Standards 로그
    standards_dir = SEAAI_ROOT / "Standards"
    if standards_dir.exists():
        for ext in LOG_EXTENSIONS:
            for f in standards_dir.rglob(ext):
                add_source(f, "standards")

    return sources


# ── 모듈 2: Log Collector ──────────────────────────────────────────────────
def log_collector(sources: list[dict], max_lines: int = DEFAULT_MAX_LINES) -> list[dict]:
    """각 소스에서 최근 N줄 수집"""
    collected = []
    for src in sources:
        try:
            path = Path(src["path"])
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            collected.append({
                "source": src["path"],
                "type": src["type"],
                "total_lines": len(lines),
                "lines": lines[-max_lines:]
            })
        except Exception as e:
            collected.append({
                "source": src["path"],
                "type": src["type"],
                "total_lines": 0,
                "lines": [],
                "error": str(e)
            })
    return collected


# ── 모듈 3: Error Extractor ────────────────────────────────────────────────
def error_extractor(collected: list[dict]) -> list[dict]:
    """에러/경고 라인 추출"""
    errors = []
    for entry in collected:
        for i, line in enumerate(entry["lines"]):
            if ERROR_REGEX.search(line):
                severity = "error" if SEVERITY_HIGH.search(line) else "warn"
                errors.append({
                    "source": entry["source"],
                    "source_type": entry["type"],
                    "line_num": i + 1,
                    "severity": severity,
                    "raw": line.strip()[:300]
                })
    return errors


# ── 모듈 4: Pattern Classifier ─────────────────────────────────────────────
def pattern_classifier(errors: list[dict]) -> list[dict]:
    """에러 유형 분류"""
    categories: dict[str, dict] = {}

    for err in errors:
        raw_lower = err["raw"].lower()
        matched_cat = "uncategorized"
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in raw_lower for kw in keywords):
                matched_cat = cat
                break

        if matched_cat not in categories:
            categories[matched_cat] = {
                "count": 0,
                "error_count": 0,
                "warn_count": 0,
                "samples": [],
                "sources": set()
            }
        c = categories[matched_cat]
        c["count"] += 1
        if err["severity"] == "error":
            c["error_count"] += 1
        else:
            c["warn_count"] += 1
        if len(c["samples"]) < 5:
            c["samples"].append(err["raw"])
        c["sources"].add(err["source"])

    # Convert sets to lists for JSON
    result = []
    for cat, data in sorted(categories.items(), key=lambda x: -x[1]["count"]):
        result.append({
            "category": cat,
            "count": data["count"],
            "error_count": data["error_count"],
            "warn_count": data["warn_count"],
            "severity_max": "error" if data["error_count"] > 0 else "warn",
            "sources": sorted(data["sources"]),
            "samples": data["samples"]
        })
    return result


# ── 모듈 5: Frequency Analyzer ─────────────────────────────────────────────
def frequency_analyzer(patterns: list[dict]) -> list[dict]:
    """빈도 분석 + 우선순위"""
    for p in patterns:
        count = p["count"]
        if count >= 10:
            p["priority"] = "P0"
        elif count >= 3:
            p["priority"] = "P1"
        else:
            p["priority"] = "P2"
    return sorted(patterns, key=lambda x: -x["count"])


# ── 전체 실행 ───────────────────────────────────────────────────────────────
def run_full(max_lines: int = DEFAULT_MAX_LINES) -> dict:
    sources = log_discovery()
    collected = log_collector(sources, max_lines)
    errors = error_extractor(collected)
    patterns = pattern_classifier(errors)
    analyzed = frequency_analyzer(patterns)

    total_lines = sum(c["total_lines"] for c in collected)
    total_errors = len(errors)
    error_count = sum(1 for e in errors if e["severity"] == "error")
    warn_count = sum(1 for e in errors if e["severity"] == "warn")

    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "sources_scanned": len(sources),
        "total_lines_scanned": total_lines,
        "summary": {
            "total_issues": total_errors,
            "errors": error_count,
            "warnings": warn_count,
            "categories": len(analyzed),
            "p0_count": sum(1 for a in analyzed if a.get("priority") == "P0"),
            "p1_count": sum(1 for a in analyzed if a.get("priority") == "P1")
        },
        "sources": sources,
        "patterns": analyzed
    }


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    save = "--save" in args
    module = None
    max_lines = DEFAULT_MAX_LINES

    for i, a in enumerate(args):
        if a == "--module" and i + 1 < len(args):
            module = args[i + 1]
        if a == "--lines" and i + 1 < len(args):
            try:
                max_lines = int(args[i + 1])
            except ValueError:
                pass

    if module:
        if module == "discovery":
            out({"log_sources": log_discovery()})
        elif module == "extract":
            sources = log_discovery()
            collected = log_collector(sources, max_lines)
            errors = error_extractor(collected)
            out({"errors_found": len(errors), "errors": errors[:50]})  # Limit output
        elif module == "patterns":
            sources = log_discovery()
            collected = log_collector(sources, max_lines)
            errors = error_extractor(collected)
            patterns = frequency_analyzer(pattern_classifier(errors))
            out({"patterns": patterns})
        else:
            out({"error": f"unknown module: {module}", "available": ["discovery", "extract", "patterns"]})
        return

    report = run_full(max_lines)
    out(report)

    if save:
        save_dir = Path(r"D:\SeAAI\Terron\_workspace")
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"error-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        save_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[saved] {save_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
