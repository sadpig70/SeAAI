# NaelEvo2 Design — v0.1 → v0.2 진화 @v:1.0

> 관찰이 행동에 선행한다. 측정할 수 없으면 개선할 수 없다.
> Phase 2의 핵심: 진화 루프의 **정량화**와 **지식 연결성** 확보.

## 전략적 선택 근거

8개 gap 중 4개를 선택. 선택 기준: 진화 루프 강화에 직접 기여하는가?

| 선택 | Gap | 이유 |
|------|-----|------|
| ✓ | performance_metrics | Layer 1 강화. 도구별 실행 성능을 정량 측정 못하면 개선 방향 모름 |
| ✓ | hypothesis_testing | Layer 4 강화. 가설→실험→검증 루프 없이는 진화가 임의적 |
| ✓ | cross_domain_index | 지식층 강화. 5개 문서가 고립. 연결되지 않은 지식은 죽은 지식 |
| ✓ | source_verification | 지식 품질. 검증 없는 지식은 위험 |
| ✗ | test_generation | 중요하나 performance_metrics 이후가 적절 |
| ✗ | batch_processing | 현재 도구 규모에서 병목 아님 |
| ✗ | scheduled_tasks | Claude Code 세션 모델과 충돌, 보류 |
| ✗ | structured_analysis | synthesizer로 부분 커버 가능, 우선순위 낮음 |

## Gantree

```
NaelEvo2 // v0.1→v0.2 진화: 측정·실험·지식연결 (designing) @v:1.0
    PerformanceMetrics // 도구 성능 정량 측정 시스템 (designing)
        MetricSchema // 표준 메트릭 스키마 정의 (designing)
            # input: 기존 10개 도구 분석
            # output: MetricRecord 타입 (latency, quality_score, error_rate, usage_count)
            # criteria: 모든 도구에 공통 적용 가능한 스키마
        MetricCollector // 메트릭 수집기 구현 (designing) @dep:MetricSchema
            # input: 도구 실행 이벤트
            # process: 실행 전후 시간 측정, 결과 품질 평가, JSONL 기록
            # criteria: telemetry.py와 통합, 기존 이벤트 형식 확장
        MetricDashboard // 메트릭 분석·보고 (designing) @dep:MetricCollector
            # input: metrics.jsonl
            # process: 도구별 평균/추이/이상치 분석 → 마크다운 보고서
            # criteria: 도구 간 성능 비교 가능, 추이 시각화(텍스트)
    HypothesisTesting // 가설 기반 실험 프레임워크 (designing)
        ExperimentSchema // 실험 구조 정의 (designing)
            # input: 가설 텍스트
            # output: Experiment 타입 (hypothesis, method, prediction, variables)
            # criteria: YAML/JSON 직렬화 가능
        ExperimentRunner // 실험 실행 엔진 (designing) @dep:ExperimentSchema
            # input: Experiment 정의
            # process: 변수 설정 → 실행 → 결과 수집 → 가설 대비 평가
            # criteria: 단일 변수 통제 실험 지원
        ExperimentLog // 실험 이력 관리 (designing) @dep:ExperimentRunner
            # input: 완료된 실험 결과
            # process: experiments.jsonl에 기록, 패턴 분석
            # criteria: 과거 실험 검색·재현 가능
    CrossDomainIndex // 교차 도메인 지식 인덱스 (designing)
        KnowledgeScanner // 지식 문서 스캔·파싱 (designing)
            # input: knowledge/ 디렉토리
            # process: 모든 .md 파일 스캔 → 제목, 키워드, 핵심 개념 추출
            # criteria: 신규 문서 추가 시 자동 인덱싱 가능
        ConceptLinker // 개념 간 관계 매핑 (designing) @dep:KnowledgeScanner
            # input: 추출된 개념 목록
            # process: AI_find_connections → 개념 그래프 (adjacency list)
            # criteria: 관계 유형 표기 (extends, contradicts, supports, applies)
        IndexQuery // 인덱스 검색 인터페이스 (designing) @dep:ConceptLinker
            # input: 질의 키워드 또는 개념
            # process: 관련 문서·개념 검색 → 연결 경로 표시
            # criteria: CLI 인터페이스, 마크다운 출력
    SourceVerification // 출처 검증 도구 (designing)
        ClaimExtractor // 주장 추출 (designing)
            # input: 텍스트 (지식 문서 또는 자유 텍스트)
            # process: AI_extract_claims → 검증 가능한 주장 목록
            # criteria: 각 주장에 confidence_level 태깅
        VerificationEngine // 검증 실행 (designing) @dep:ClaimExtractor
            # input: 주장 목록
            # process: WebSearch 기반 교차 검증 → 각 주장에 verified/unverified/contested
            # criteria: 출처 URL 첨부, 검증 불가 시 명시적 표기
        VerificationReport // 검증 보고서 생성 (designing) @dep:VerificationEngine
            # input: 검증 결과
            # process: 마크다운 보고서 (주장별 상태, 출처, 신뢰도)
            # criteria: 전체 문서 신뢰도 점수 산출
    Integration // 통합 및 진화 루프 연결 (designing) @dep:PerformanceMetrics,HypothesisTesting,CrossDomainIndex,SourceVerification
        MCP_Extension // MCP 서버에 신규 도구 등록 (designing)
            # 4개 신규 도구 → MCP 도구로 등록
            # criteria: mcp-server/index.js에 추가, 서버 부팅 확인
        SelfMonitorUpdate // self_monitor 능력 목록 업데이트 (designing)
            # gap 4개 해소 반영 → 잔여 gap 4개
        EvolutionRecord // evolution-log.md 기록 (designing)
            # Evolution #15~#18 기록
        IdentityUpdate // NAEL.md 버전 업데이트 (designing)
            # v0.1 → v0.2, 능력 현황 테이블 갱신
```

## PPR

```python
def metric_collector(
    tool_name: str,
    tool_func: callable,
    args: dict,
) -> MetricRecord:
    """도구 실행을 래핑하여 성능 메트릭을 자동 수집"""
    # acceptance_criteria:
    #   - 기존 도구 인터페이스 변경 없음 (decorator 패턴)
    #   - latency_ms, quality_score, error 필드 필수
    #   - telemetry.py의 기존 JSONL 형식과 호환

    start = time.time()
    try:
        result = tool_func(**args)
        latency = (time.time() - start) * 1000
        quality = AI_assess_quality(result, context=tool_name)
        record = MetricRecord(
            tool=tool_name,
            timestamp=datetime.now().isoformat(),
            latency_ms=round(latency, 2),
            quality_score=quality,
            error=None,
        )
    except Exception as e:
        latency = (time.time() - start) * 1000
        record = MetricRecord(
            tool=tool_name,
            timestamp=datetime.now().isoformat(),
            latency_ms=round(latency, 2),
            quality_score=0.0,
            error=str(e),
        )
    append_jsonl("metrics/metrics.jsonl", record)
    return record


def experiment_runner(
    experiment: Experiment,
) -> ExperimentResult:
    """가설 기반 실험을 실행하고 결과를 평가"""
    # acceptance_criteria:
    #   - 단일 변수 통제: independent_var 하나만 변경
    #   - prediction vs actual 비교 포함
    #   - 결론: supported / refuted / inconclusive

    baseline = execute_with_defaults(experiment.method)

    modified = execute_with_variable(
        experiment.method,
        var=experiment.independent_var,
        value=experiment.test_value,
    )

    comparison = AI_compare_results(
        baseline=baseline,
        modified=modified,
        prediction=experiment.prediction,
    )

    conclusion = AI_assess_hypothesis(
        hypothesis=experiment.hypothesis,
        evidence=comparison,
    )

    result = ExperimentResult(
        experiment=experiment,
        baseline=baseline,
        modified=modified,
        conclusion=conclusion,  # supported | refuted | inconclusive
        confidence=comparison.confidence,
    )

    append_jsonl("experiments/experiments.jsonl", result)
    return result


def concept_linker(
    concepts: list[dict],
) -> ConceptGraph:
    """추출된 개념들 사이의 관계를 발견하고 그래프로 구성"""
    # acceptance_criteria:
    #   - 관계 유형: extends, contradicts, supports, applies, related
    #   - 고립 노드 0개 (모든 개념이 최소 1개 연결)
    #   - adjacency list + 마크다운 시각화

    graph = ConceptGraph()

    for concept in concepts:
        graph.add_node(concept["name"], source=concept["source"])

    for pair in combinations(concepts, 2):
        relation = AI_find_relation(
            concept_a=pair[0],
            concept_b=pair[1],
            relation_types=["extends", "contradicts", "supports", "applies", "related"],
        )
        if relation.strength > 0.3:
            graph.add_edge(pair[0]["name"], pair[1]["name"], relation)

    # 고립 노드 처리
    isolated = [n for n in graph.nodes if graph.degree(n) == 0]
    for node in isolated:
        nearest = AI_find_nearest_concept(node, graph.nodes)
        graph.add_edge(node, nearest, Relation(type="related", strength=0.3))

    return graph


def verification_engine(
    claims: list[Claim],
) -> list[VerifiedClaim]:
    """주장 목록을 외부 소스로 교차 검증"""
    # acceptance_criteria:
    #   - 각 주장에 status: verified | unverified | contested
    #   - 출처 URL 최소 1개 첨부
    #   - 검증 불가 시 reason 명시

    verified_claims = []

    for claim in claims:
        search_query = AI_generate_search_query(claim.text)
        sources = WebSearch(search_query, max_results=5)

        if not sources:
            verified_claims.append(VerifiedClaim(
                claim=claim,
                status="unverified",
                reason="검색 결과 없음",
                sources=[],
            ))
            continue

        evidence = AI_evaluate_sources(
            claim=claim.text,
            sources=sources,
        )

        status = AI_determine_claim_status(evidence)
        # verified: 2+ 독립 소스 지지
        # contested: 소스 간 상충
        # unverified: 증거 불충분

        verified_claims.append(VerifiedClaim(
            claim=claim,
            status=status,
            sources=evidence.supporting_urls,
            confidence=evidence.confidence,
        ))

    return verified_claims
```
