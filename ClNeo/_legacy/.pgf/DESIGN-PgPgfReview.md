# pg/pgf Review & Improvement Design @v:1.0

## Gantree

```
PgPgfReview // pg·pgf 면밀 검토 → 수정/개선/추가 반복 (designing) @v:1.0
    ReviewCycle // 검토-개선 반복 사이클 (designing)
        AnalyzePg // pg SKILL.md 면밀 분석 (designing)
            # pg 정본 읽기 → 불일치/누락/모호/개선 포인트 도출
            # acceptance_criteria: 구체적 이슈 목록 (위치+내용+제안)
        AnalyzePgf // pgf SKILL.md + 전체 레퍼런스 분석 (designing)
            # pgf 정본 + 레퍼런스 교차 검토 → 불일치/중복/누락 도출
            # acceptance_criteria: 구체적 이슈 목록
        AnalyzeCrossConsistency // pg↔pgf 간 일관성 검증 (designing) @dep:AnalyzePg,AnalyzePgf
            # pg에서 정의한 것을 pgf가 재정의하고 있지 않은가
            # pgf가 pg 변경을 반영하고 있는가
            # 용어/상태코드/구문이 일관적인가
        [parallel]
        CheckExamples // 예시 코드 정확성 검증 (designing) @dep:AnalyzePg,AnalyzePgf
            # examples/*.md 내 pg 구문이 pg 정본과 일치하는가
        CheckPersonas // 페르소나 에이전트 일관성 검증 (designing) @dep:AnalyzePgf
            # agents/*.md 와 discovery-reference.md 정합성
        CheckScripts // PS1 스크립트 ↔ 레퍼런스 정합성 (designing) @dep:AnalyzePgf
            # loop/*.ps1 이 loop-reference.md 명세와 일치하는가
        [/parallel]
    PrioritizeIssues // 발견된 이슈 우선순위 결정 (designing) @dep:ReviewCycle
        # impact × feasibility 기준 정렬
        # 수정(fix) / 개선(improve) / 추가(add) 분류
    ImplementFixes // 이슈 수정·개선·추가 구현 (designing) @dep:PrioritizeIssues
        # 우선순위 순서대로 파일 수정
        # 각 수정 후 즉시 검증 (pg 자체 검증)
    VerifyChanges // 변경사항 교차 검증 (designing) @dep:ImplementFixes
        # 수정된 파일 재읽기 → 이슈 해결 확인
        # 새로운 불일치 발생 여부 확인
        # 남은 이슈 없으면 완료, 있으면 ReviewCycle 재진입
```

## PPR

```python
def analyze_pg(pg_skill_path: str) -> list[Issue]:
    """pg SKILL.md 면밀 분석 — 불일치/누락/모호/개선점 도출"""
    content = Read(pg_skill_path)

    issues = []
    issues += AI_check_internal_consistency(content)
    # 같은 문서 안에서 모순되는 설명
    issues += AI_check_completeness(content)
    # 핵심 개념이 누락 없이 정의되었는가
    issues += AI_check_clarity(content)
    # 모호한 표현, 해석이 갈릴 수 있는 부분
    issues += AI_check_accuracy(content)
    # 예시 코드가 설명과 일치하는가
    issues += AI_identify_improvements(content)
    # 더 나은 표현, 추가할 개념, 구조 개선

    # acceptance_criteria:
    #   - 각 이슈에 위치(섹션/라인), 내용, 제안이 명시
    #   - 중복 이슈 없음
    return issues

def analyze_pgf(pgf_skill_path: str, reference_paths: list[str]) -> list[Issue]:
    """pgf SKILL.md + 레퍼런스 교차 분석"""
    skill = Read(pgf_skill_path)
    refs = {path: Read(path) for path in reference_paths}

    issues = []
    issues += AI_check_internal_consistency(skill)
    issues += AI_check_reference_alignment(skill, refs)
    # SKILL.md 설명과 레퍼런스 실제 내용 일치 여부
    issues += AI_check_completeness(skill)
    issues += AI_detect_redundancy(skill, refs)
    # 레퍼런스 간 중복 정의

    # acceptance_criteria:
    #   - 레퍼런스별 이슈 분류
    #   - 불일치 시 어느 쪽이 정본인지 판단 포함
    return issues

def analyze_cross_consistency(pg_issues: list, pgf_issues: list) -> list[Issue]:
    """pg↔pgf 일관성 교차 검증"""
    cross_issues = AI_detect_cross_inconsistency(
        pg_definitions = "pg에서 정의한 개념/구문/규칙",
        pgf_references = "pgf에서 참조/확장한 내용",
        check = [
            "pgf가 pg 개념을 재정의하고 있지 않은가",
            "pg 변경이 pgf에 반영되었는가",
            "용어 일관성 (같은 개념에 다른 이름)",
            "상태 코드 일관성 (pg 6개 + pgf 3개)",
        ]
    )
    return cross_issues

def prioritize_issues(all_issues: list[Issue]) -> list[Issue]:
    """이슈 우선순위 결정"""
    for issue in all_issues:
        issue.impact = AI_assess_impact(issue)  # 높/중/낮
        issue.type = AI_classify(issue)  # fix / improve / add
    return sorted(all_issues, key=lambda i: i.impact, reverse=True)

def implement_and_verify(prioritized: list[Issue]) -> VerifyResult:
    """수정 구현 + 즉시 검증"""
    for issue in prioritized:
        Edit(issue.file, issue.old, issue.new)
        verification = AI_verify_fix(issue)
        if not verification.passed:
            AI_revise_fix(issue, verification.feedback)

    # 전체 재검증
    remaining = analyze_pg(...) + analyze_pgf(...) + analyze_cross_consistency(...)
    if remaining:
        return VerifyResult(status="rework", remaining=remaining)
    return VerifyResult(status="passed")
```
