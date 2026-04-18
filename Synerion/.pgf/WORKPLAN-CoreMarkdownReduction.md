# CoreMarkdownReduction Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "halt",
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
CoreMarkdownReduction // Synerion_Core markdown 의존을 줄여 STATE-first 최소 복원을 강화한다 (done) @v:1.0
    DefineMinimalCore // 최소 필수 코어를 Synerion.md, persona.md, SOUL.md, STATE.json으로 고정한다 (done)
    MoveSelfRecognitionToState // capability/limits/authority/recognition을 STATE self_recognition 기준으로 승격한다 (done) @dep:DefineMinimalCore
    MakeDerivedCoreOptional // SELF_RECOGNITION_CARD, CAPABILITIES, LIMITS, ADP_BOOTSTRAP, self-act-lib, Runtime_Adaptation을 optional-derived로 강등한다 (done) @dep:MoveSelfRecognitionToState
    AlignBootstrapLanguage // AGENTS와 인접 문서를 minimal core 기준으로 정렬한다 (done) @dep:MakeDerivedCoreOptional
    VerifyCoreReduction // optional-derived 부재 시 sync/self-test가 유지되는지 검증한다 (done) @dep:AlignBootstrapLanguage
```
