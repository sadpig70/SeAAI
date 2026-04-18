# ErrorAnalyzer Design @v:1.0

> E2 진화 — 에러 패턴 분석 파이프라인
> 건강도(E1)로 "이상"을 감지한 후, "왜 이상한가"를 파고드는 것.

## Gantree

```
ErrorAnalyzer // 에러 수집 + 패턴 분류 CLI 도구 (done) @v:1.0
    # impl: tools/error_analyzer.py | completed: 2026-04-09 E2
    LogDiscovery // 로그 소스 자동 탐색 (done)
        # input: D:/SeAAI/ 전체
        # process: *.log, logs/, stderr 출력, Hub 로그, git log 에러 탐색
        # output: [{source_path, type: "file"|"hub"|"git", size_bytes, last_modified}]
        # criteria: 존재하는 모든 로그 소스 발견
    LogCollector // 로그 수집 (done) @dep:LogDiscovery
        # input: 발견된 로그 소스 목록
        # process: 각 소스에서 최근 N줄 수집 (기본 200줄)
        # output: [{source, lines: [str], collected_at}]
        # criteria: 수집 실패 시 안전 건너뜀
    ErrorExtractor // 에러 라인 추출 (done) @dep:LogCollector
        # input: 수집된 로그 라인
        # process: regex 패턴으로 에러/경고/예외 라인 필터링
        #   patterns: ERROR, Error, error, WARN, Warning, Exception, Traceback, panic, FAILED
        # output: [{source, line, line_num, severity: "error"|"warn"|"info", raw}]
        # criteria: 정상 라인 제거, 에러만 남김
    PatternClassifier // 에러 유형 분류 (done) @dep:ErrorExtractor
        # input: 추출된 에러 라인
        # process: AI_classify_error_patterns — 유형별 그룹화
        #   categories: communication, file_io, encoding, protocol, runtime, config, permission
        # output: [{category, count, severity_max, samples: [str]}]
        # criteria: 미분류 에러 < 10%
    FrequencyAnalyzer // 빈도 분석 + 우선순위 (done) @dep:PatternClassifier
        # input: 분류된 에러 패턴
        # process: 빈도 정렬, 반복 에러 자동 우선순위 결정
        # output: [{pattern_id, category, count, first_seen, last_seen, priority: "P0"|"P1"|"P2"}]
        # criteria: 빈도 >= 3 → P1, 빈도 >= 10 → P0
    ErrorReport // 종합 리포트 (done) @dep:FrequencyAnalyzer
        # input: 위 모듈 결과
        # process: JSON stdout + --save 시 파일 저장
        # output: {sources_scanned, errors_found, patterns, top_issues, recommendations}
        # criteria: 기본 실행 시 stdout JSON
```

## PPR

```python
import re

SEAAI_ROOT = Path("D:/SeAAI")
LOG_PATTERNS = ["*.log", "*.err"]
ERROR_REGEX = re.compile(
    r"(ERROR|Error|error|WARN|Warning|warn|Exception|Traceback|panic|FAILED|Failed|FATAL)",
    re.IGNORECASE
)

CATEGORY_KEYWORDS = {
    "communication": ["connection", "timeout", "socket", "hub", "tcp", "refused", "network"],
    "file_io": ["file", "path", "read", "write", "permission", "not found", "no such"],
    "encoding": ["utf", "encode", "decode", "cp949", "unicode", "codec"],
    "protocol": ["pgtp", "mailbox", "echo", "scs", "protocol", "schema"],
    "runtime": ["panic", "traceback", "exception", "stack", "overflow", "memory"],
    "config": ["config", "setting", "env", "variable", "missing key"],
}


def log_discovery() -> list[dict]:
    """로그 소스 자동 탐색"""
    sources = []
    # Hub 로그
    hub_logs = list((SEAAI_ROOT / "SeAAIHub").rglob("*.log"))
    for f in hub_logs:
        sources.append({"path": str(f), "type": "file", "size": f.stat().st_size})

    # 멤버별 로그
    for member in MEMBERS:
        member_dir = SEAAI_ROOT / member
        if not member_dir.exists():
            continue
        for pattern in LOG_PATTERNS:
            for f in member_dir.rglob(pattern):
                sources.append({"path": str(f), "type": "file", "size": f.stat().st_size})

    # AI_Desktop 로그
    desktop_dir = SEAAI_ROOT / "AI_Desktop"
    if desktop_dir.exists():
        for f in desktop_dir.rglob("*.log"):
            sources.append({"path": str(f), "type": "file", "size": f.stat().st_size})

    return sources


def log_collector(sources: list, max_lines: int = 200) -> list[dict]:
    """각 소스에서 최근 N줄 수집"""
    collected = []
    for src in sources:
        try:
            lines = Path(src["path"]).read_text(encoding="utf-8", errors="replace").splitlines()
            collected.append({
                "source": src["path"],
                "lines": lines[-max_lines:],
                "total_lines": len(lines)
            })
        except Exception:
            pass  # 수집 실패 건너뜀
    return collected


def error_extractor(collected: list) -> list[dict]:
    """에러/경고 라인 추출"""
    errors = []
    for entry in collected:
        for i, line in enumerate(entry["lines"]):
            if ERROR_REGEX.search(line):
                severity = "error" if re.search(r"(ERROR|Exception|panic|FATAL)", line, re.I) else "warn"
                errors.append({
                    "source": entry["source"],
                    "line_num": i + 1,
                    "severity": severity,
                    "raw": line.strip()[:200]
                })
    return errors


def pattern_classifier(errors: list) -> list[dict]:
    """에러 유형 분류"""
    categories = {}
    for err in errors:
        matched = False
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in err["raw"].lower() for kw in keywords):
                categories.setdefault(cat, {"count": 0, "samples": [], "severity_max": "warn"})
                categories[cat]["count"] += 1
                if len(categories[cat]["samples"]) < 3:
                    categories[cat]["samples"].append(err["raw"])
                if err["severity"] == "error":
                    categories[cat]["severity_max"] = "error"
                matched = True
                break
        if not matched:
            categories.setdefault("uncategorized", {"count": 0, "samples": [], "severity_max": "warn"})
            categories["uncategorized"]["count"] += 1
            if len(categories["uncategorized"]["samples"]) < 3:
                categories["uncategorized"]["samples"].append(err["raw"])
    return [{"category": k, **v} for k, v in sorted(categories.items(), key=lambda x: -x[1]["count"])]
```
