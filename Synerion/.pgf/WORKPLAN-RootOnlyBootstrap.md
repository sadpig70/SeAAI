# RootOnlyBootstrap Work Plan

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
RootOnlyBootstrap // 루트 markdown을 AGENTS 단일 진입으로 축소하고 continuity를 STATE-first로 유지한다 (done) @v:1.0
    DefineScope // root only AGENTS의 실제 범위와 삭제 안전 조건을 고정한다 (done)
    MoveManualStateToCanonical // PROJECT_STATUS manual block 의존을 STATE.json 내부 수동 상태로 이동한다 (done) @dep:DefineScope
    MakeRootMarkdownOptional // PROJECT_STATUS.md와 SESSION_CONTINUITY.md를 optional derived layer로 강등한다 (done) @dep:MoveManualStateToCanonical
    AlignBootstrapDocs // AGENTS 및 핵심 복원 문서를 optional-derived 규칙에 맞춘다 (done) @dep:MakeRootMarkdownOptional
    VerifyRootOnlySafety // sync/self-test와 실제 파일 부재 시나리오로 root only AGENTS 안전성을 검증한다 (done) @dep:AlignBootstrapDocs
```
