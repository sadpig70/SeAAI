# DESIGN — E3: Quality Gate (산출물 품질 검증 프레임워크)
# Vera E3 진화: 멤버 산출물 독립 품질 평가
# PGF design mode | 2026-03-29

---

## WHY

Vera의 핵심 역할 중 QualityMetering이 전무하다.
"우리가 만든 것은 실제로 좋은가?"에 답하려면
다른 멤버의 산출물을 독립적으로 평가하는 프레임워크가 필요하다.

---

## Gantree

```
QualityGate // 산출물 품질 검증 프레임워크 @v:1.0
    TargetSelector // 검증 대상 선택 (in-progress)
        # input: member: str, artifact_type: Literal["code","doc","tool","design"]
        # process: glob member workspace → list artifacts
        # output: list[ArtifactPath]
    [parallel]
    StructureCheck // 구조적 검증 (in-progress)
        # process: 파일 존재, 형식 준수, 필수 필드 확인
        # criteria: 구조 위반 0건
    ContentCheck // 내용적 검증 (in-progress)
        # process: AI_assess_quality(content) → 일관성, 완전성, 명확성
        # criteria: quality_score >= 0.7
    ConsistencyCheck // 교차 일관성 (in-progress)
        # process: 정체성 vs 진화로그 vs Echo → 불일치 탐지
        # criteria: contradiction_count == 0
    [/parallel]
    VerdictSynthesis // 종합 판정 (in-progress) @dep:StructureCheck,ContentCheck,ConsistencyCheck
        # output: QualityReport (pass/warn/fail per artifact)
```
