# IdentityMarkdownReduction Design @v:1.0

## Gantree

```text
IdentityMarkdownReduction // identity markdown 의존을 줄여 AGENTS + SOUL + STATE 기동을 완성한다 (designing) @v:1.0
    DefineIdentityCore // identity 최소 코어를 AGENTS.md, SOUL.md, STATE.json[self_recognition]으로 고정한다 (designing)
    MakeIdentityDocsOptional // Synerion.md와 persona.md를 optional identity docs로 강등한다 (designing) @dep:DefineIdentityCore
    AlignGeneratedViews // PROJECT_STATUS, ADP_BOOTSTRAP, reopen summary에 최소 코어 모델을 반영한다 (designing) @dep:MakeIdentityDocsOptional
    VerifyIdentityReduction // Synerion.md와 persona.md 부재 시 sync/self-test가 유지되는지 검증한다 (designing) @dep:AlignGeneratedViews
```

## PPR

```python
def reduce_identity_markdown_dependency(workspace: Path) -> dict:
    """
    identity 설명 문서인 Synerion.md와 persona.md를 optional로 낮춘다.
    bootstrap은 AGENTS + SOUL + STATE self_recognition block만으로 복원 가능해야 한다.
    """
    # acceptance_criteria:
    #   - AGENTS.md가 Synerion.md/persona.md를 optional identity docs로 취급한다.
    #   - continuity_lib self-test의 minimal core에서 Synerion.md/persona.md가 빠진다.
    #   - persona seed와 identity summary는 SOUL/state fallback만으로 계산 가능하다.
    #   - Synerion.md와 persona.md 부재 상태에서 update-project-status/self-test가 통과한다.
```
