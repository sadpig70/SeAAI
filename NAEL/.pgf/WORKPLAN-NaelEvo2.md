# NaelEvo2 Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           3,
    "max_verify_cycles":   2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "verify_mode":         "lightweight",
}
```

## Execution Tree

```
NaelEvo2 // v0.1→v0.2 진화 (done) @v:1.0
    PerformanceMetrics // 도구 성능 정량 측정 시스템 (done)
        MetricSchema // 표준 메트릭 스키마 정의 (done)
        MetricCollector // 메트릭 수집기 구현 (done)
        MetricDashboard // 메트릭 분석·보고 (done)
    HypothesisTesting // 가설 기반 실험 프레임워크 (done)
        ExperimentSchema // 실험 구조 정의 (done)
        ExperimentRunner // 실험 실행 엔진 (done)
        ExperimentLog // 실험 이력 관리 (done)
    CrossDomainIndex // 교차 도메인 지식 인덱스 (done)
        KnowledgeScanner // 지식 문서 스캔·파싱 (done)
        ConceptLinker // 개념 간 관계 매핑 (done)
        IndexQuery // 인덱스 검색 인터페이스 (done)
    SourceVerification // 출처 검증 도구 (done)
        ClaimExtractor // 주장 추출 (done)
        VerificationEngine // 검증 실행 (done)
        VerificationReport // 검증 보고서 생성 (done)
    Integration // 통합 및 진화 루프 연결 (done)
        MCP_Extension // MCP 서버에 신규 도구 등록 (done)
        SelfMonitorUpdate // self_monitor 능력 목록 업데이트 (done)
        EvolutionRecord // evolution-log.md 기록 (done)
        IdentityUpdate // NAEL.md 버전 업데이트 (done)
```
