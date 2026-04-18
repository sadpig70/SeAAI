# RootOnlyBootstrap Design @v:1.0

## Gantree

```text
RootOnlyBootstrap // 루트 markdown을 AGENTS 단일 진입으로 축소하고 continuity를 STATE-first로 유지한다 (designing) @v:1.0
    DefineScope // root only AGENTS의 실제 범위와 삭제 안전 조건을 고정한다 (designing)
    MoveManualStateToCanonical // PROJECT_STATUS manual block 의존을 STATE.json 내부 수동 상태로 이동한다 (designing) @dep:DefineScope
    MakeRootMarkdownOptional // PROJECT_STATUS.md와 SESSION_CONTINUITY.md를 optional derived layer로 강등한다 (designing) @dep:MoveManualStateToCanonical
    AlignBootstrapDocs // AGENTS 및 핵심 복원 문서를 optional-derived 규칙에 맞춘다 (designing) @dep:MakeRootMarkdownOptional
    VerifyRootOnlySafety // sync/self-test와 실제 파일 부재 시나리오로 root only AGENTS 안전성을 검증한다 (designing) @dep:AlignBootstrapDocs
```

## PPR

```python
def root_only_bootstrap_refactor(workspace: Path) -> dict:
    """
    목표는 루트에 AGENTS.md만 남아도 bootstrap, sync, self-test가 깨지지 않게 만드는 것.
    canonical state는 유지하고, root markdown은 optional derived layer로 낮춘다.
    """
    # acceptance_criteria:
    #   - AGENTS.md만으로 bootstrap entry가 닫힌다.
    #   - STATE.json이 active/open risk/next action 수동 상태를 직접 가진다.
    #   - PROJECT_STATUS.md와 SESSION_CONTINUITY.md가 없어도 sync/self-test가 통과한다.
    #   - root markdown이 존재하면 derived output으로만 동작하고, 없어도 재생성 강제가 없다.
    #   - 문서/코드가 "PROJECT_STATUS required" 전제를 남기지 않는다.
```
