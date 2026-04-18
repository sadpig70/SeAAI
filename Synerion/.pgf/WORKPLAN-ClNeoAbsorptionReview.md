# ClNeoAbsorptionReview Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "skip_and_continue",
    "completion": "all_done_or_blocked",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": [
        "D:/SeAAI/Synerion",
        "D:/SeAAI/ClNeo",
        "D:/SeAAI/docs",
        "D:/SeAAI/SeAAIHub",
    ],
    "forbidden_actions": [
        "destructive_without_user_request",
        "unapproved_network",
    ],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
ClNeoAbsorptionReview // ClNeo를 분석해 Synerion 흡수 후보를 선별한다 (done) @v:1.0
    CollectClNeoContext // 정체성, continuity, ADP, 진화, 인프라 문서를 읽는다 (done)
    CompareWithSynerion // Synerion 현재 구조와 대조해 gap을 찾는다 (done) @dep:CollectClNeoContext
    SelectAbsorptionSet // adopt / adapt / defer / reject로 분류한다 (done) @dep:CompareWithSynerion
    RecordDurableReport // PGF 아티팩트와 최종 보고서를 저장한다 (done) @dep:SelectAbsorptionSet
```
