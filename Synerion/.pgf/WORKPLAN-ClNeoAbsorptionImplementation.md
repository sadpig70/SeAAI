# ClNeoAbsorptionImplementation Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "skip_and_continue",
    "completion": "all_done_or_blocked",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": ["D:/SeAAI/Synerion"],
    "forbidden_actions": ["destructive_without_user_request", "unapproved_network"],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
ClNeoAbsorptionImplementation // ClNeo 분석 결과 중 Tier 1을 Synerion에 실제 흡수한다 (done) @v:1.0
    AddNarrativeLayer // NOW.md 계층을 continuity에 추가한다 (done)
    AddWALRecovery // WAL 기반 crash recovery를 continuity sync에 연결한다 (done) @dep:AddNarrativeLayer
    AddEvolutionChain // Synerion 진화 계보 문서를 추가한다 (done) @dep:AddNarrativeLayer
    AddRuntimeAdaptation // 환경 적응 가이드를 추가한다 (done) @dep:AddNarrativeLayer
    VerifyAbsorption // continuity sync, self-test, start path를 검증한다 (done) @dep:AddWALRecovery,AddEvolutionChain,AddRuntimeAdaptation
```
