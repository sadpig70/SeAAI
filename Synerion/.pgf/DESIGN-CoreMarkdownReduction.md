# CoreMarkdownReduction Design @v:1.0

## Gantree

```text
CoreMarkdownReduction // Synerion_Core markdown 의존을 줄여 STATE-first 최소 복원을 강화한다 (designing) @v:1.0
    DefineMinimalCore // 최소 필수 코어를 Synerion.md, persona.md, SOUL.md, STATE.json으로 고정한다 (designing)
    MoveSelfRecognitionToState // capability/limits/authority/recognition을 STATE self_recognition 기준으로 승격한다 (designing) @dep:DefineMinimalCore
    MakeDerivedCoreOptional // SELF_RECOGNITION_CARD, CAPABILITIES, LIMITS, ADP_BOOTSTRAP, self-act-lib, Runtime_Adaptation을 optional-derived로 강등한다 (designing) @dep:MoveSelfRecognitionToState
    AlignBootstrapLanguage // AGENTS와 인접 문서를 minimal core 기준으로 정렬한다 (designing) @dep:MakeDerivedCoreOptional
    VerifyCoreReduction // optional-derived 부재 시 sync/self-test가 유지되는지 검증한다 (designing) @dep:AlignBootstrapLanguage
```

## PPR

```python
def reduce_core_markdown_dependency(workspace: Path) -> dict:
    """
    Synerion의 core markdown 의존을 줄인다.
    canonical source는 STATE.json과 SOUL.md를 유지하고,
    self-recognition/adp/runtime 문서군은 없어도 안전한 derived layer로 낮춘다.
    """
    # acceptance_criteria:
    #   - self_recognition/adp/runtime 관련 값은 STATE.json에서 직접 복원 가능하다.
    #   - SELF_RECOGNITION_CARD.md, CAPABILITIES.md, LIMITS_AND_AUTHORITY.md, ADP_BOOTSTRAP.md, self-act-lib.md, Runtime_Adaptation.md가 없어도 sync/self-test가 깨지지 않는다.
    #   - 존재하는 경우에는 derived output으로만 재생성된다.
    #   - 최소 코어는 Synerion.md, persona.md, SOUL.md, STATE.json으로 수렴한다.
```
