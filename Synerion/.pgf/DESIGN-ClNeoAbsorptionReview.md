# ClNeoAbsorptionReview Design @v:1.0

## Gantree

```text
ClNeoAbsorptionReview // ClNeo를 분석해 Synerion 흡수 후보를 선별한다 (done) @v:1.0
    CollectClNeoContext // 정체성, continuity, ADP, 진화, 인프라 문서를 읽는다 (done)
    CompareWithSynerion // Synerion 현재 구조와 대조해 gap을 찾는다 (done) @dep:CollectClNeoContext
    SelectAbsorptionSet // adopt / adapt / defer / reject로 분류한다 (done) @dep:CompareWithSynerion
    RecordDurableReport // PGF 아티팩트와 최종 보고서를 저장한다 (done) @dep:SelectAbsorptionSet
```

## PPR

```python
def select_absorption_set(clneo: dict, synerion: dict) -> dict:
    """ClNeo의 구조를 Synerion 역할에 맞게 변환 가능한지 판정한다."""
    # acceptance_criteria:
    #   - 모든 채택 판단이 실제 ClNeo 문서 근거를 가진다
    #   - Synerion 역할과 충돌하는 항목은 명시적으로 보류 또는 비채택한다
    #   - 즉시 흡수 / 변형 흡수 / 보류의 실행 순서가 포함된다

    evidence = AI_collect_evidence(
        identity=clneo["identity"],
        continuity=clneo["continuity"],
        autonomy=clneo["autonomy"],
        evolution=clneo["evolution"],
    )

    fit = AI_assess_role_fit(
        target_role="Synerion_orchestration_and_convergence",
        candidate_mechanisms=evidence,
    )

    verdict = AI_partition(
        fit,
        buckets=["adopt_now", "adapt_later", "defer_or_reject"],
    )

    return verdict
```
