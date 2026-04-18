# ErrorAnalyzer Work Plan

## POLICY

```python
POLICY = {
    "max_retry": 2,
    "on_blocked": "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion": "all_done_or_blocked",
}
```

## Execution Tree

```
ErrorAnalyzer // 에러 수집 + 패턴 분류 CLI 도구 (done) @v:1.0
    LogDiscovery // 로그 소스 자동 탐색 (done)
    LogCollector // 로그 수집 (done) @dep:LogDiscovery
    ErrorExtractor // 에러 라인 추출 (done) @dep:LogCollector
    PatternClassifier // 에러 유형 분류 (done) @dep:ErrorExtractor
    FrequencyAnalyzer // 빈도 분석 + 우선순위 (done) @dep:PatternClassifier
    ErrorReport // 종합 리포트 (done) @dep:FrequencyAnalyzer
```
