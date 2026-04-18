# IdentityMarkdownReduction Work Plan

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
IdentityMarkdownReduction // identity markdown 의존을 줄여 AGENTS + SOUL + STATE 기동을 완성한다 (done) @v:1.0
    DefineIdentityCore // identity 최소 코어를 AGENTS.md, SOUL.md, STATE.json[self_recognition]으로 고정한다 (done)
    MakeIdentityDocsOptional // Synerion.md와 persona.md를 optional identity docs로 강등한다 (done) @dep:DefineIdentityCore
    AlignGeneratedViews // PROJECT_STATUS, ADP_BOOTSTRAP, reopen summary에 최소 코어 모델을 반영한다 (done) @dep:MakeIdentityDocsOptional
    VerifyIdentityReduction // Synerion.md와 persona.md 부재 시 sync/self-test가 유지되는지 검증한다 (done) @dep:AlignGeneratedViews
```
