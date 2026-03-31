# DESIGN — E2: World Sensing Pipeline (외부 세계 감지)
# Vera E2 진화: 외부 데이터 수집 → SeAAI 내부 주입
# PGF design mode | 2026-03-29

---

## WHY

Vera의 3대 역할 중 World Sensing이 전무하다.
생태계 내부만 측정하면 거울만 보는 것이다.
외부 세계 신호를 수집하여 SeAAI 내부로 주입해야 진짜 현실 앵커가 된다.

---

## Gantree

```
WorldSensing // 외부 세계 감지 파이프라인 @v:1.0
    SignalCollector // 외부 신호 수집 (in-progress)
        WebSearchQuery // 키워드 기반 웹 검색 (in-progress)
            # input: topics: list[str], max_results: int = 5
            # process: WebSearch(topic) per topic
            # output: list[SearchResult]
        WebContentFetch // URL 본문 수집 (in-progress) @dep:WebSearchQuery
            # input: urls from SearchResult
            # process: WebFetch(url) → extract text
            # output: list[FetchedContent]
    RelevanceFilter // SeAAI 연관성 필터 (in-progress) @dep:SignalCollector
        # input: list[FetchedContent], seaai_context: str
        # process: AI_assess_relevance(content, seaai_context) → score
        # criteria: relevance >= 0.5 만 통과
        # output: list[RelevantSignal]
    SignalNormalizer // 내부 형식 변환 (in-progress) @dep:RelevanceFilter
        # input: list[RelevantSignal]
        # process: AI_summarize + categorize → SignalReport
        # output: SignalReport (JSON + MD)
    ReportWriter // 파일 저장 (in-progress) @dep:SignalNormalizer
        # output: Vera_Core/reports/world-sense-{date}.md + .json
```

---

## PPR

```python
def world_sensing(
    topics: list[str],
    max_results_per_topic: int = 3,
    report_dir: str = "D:/SeAAI/Vera/Vera_Core/reports/",
) -> dict:
    """외부 세계 신호를 수집하여 SeAAI 연관 정보를 추출한다."""

    # acceptance_criteria:
    #   - 최소 1개 topic에 대해 검색 결과를 반환해야 한다
    #   - 각 결과에 relevance 점수가 부여되어야 한다
    #   - JSON + Markdown 형식으로 리포트가 생성되어야 한다

    raw_signals = []
    for topic in topics:
        results = WebSearch(topic, max_results=max_results_per_topic)
        raw_signals.extend(results)

    relevant = AI_filter_by_relevance(raw_signals, context="SeAAI ecosystem")
    report = AI_synthesize_signals(relevant)
    write_report(report, report_dir)
    return report
```
