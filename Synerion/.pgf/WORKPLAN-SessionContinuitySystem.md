# SessionContinuitySystem Work Plan

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
SessionContinuitySystem // Synerion 세션 간 연속성 유지 시스템 구축 (done) @v:1.0
    DefineCanonicalState // 연속성의 기준 파일과 읽기 순서를 정의한다 (done)
    InstallDurableStatus // PROJECT_STATUS.md를 표준 상태 파일로 설치한다 (done) @dep:DefineCanonicalState
    ImplementContinuityTools // save/reopen/self-test 스크립트를 구현한다 (done) @dep:DefineCanonicalState
    UpdateStartupRules // AGENTS와 시작 스크립트에 continuity 규칙을 반영한다 (done) @dep:InstallDurableStatus,ImplementContinuityTools
    VerifyResumeFlow // 생성-재개-검증 흐름을 실제로 확인한다 (done) @dep:UpdateStartupRules
```

