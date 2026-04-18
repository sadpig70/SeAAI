# ClNeoAbsorptionImplementation Design @v:1.0

## Gantree

```text
ClNeoAbsorptionImplementation // ClNeo 분석 결과 중 Tier 1을 Synerion에 실제 흡수한다 (done) @v:1.0
    AddNarrativeLayer // NOW.md 계층을 continuity에 추가한다 (done)
    AddWALRecovery // WAL 기반 crash recovery를 continuity sync에 연결한다 (done) @dep:AddNarrativeLayer
    AddEvolutionChain // Synerion 진화 계보 문서를 추가한다 (done) @dep:AddNarrativeLayer
    AddRuntimeAdaptation // 환경 적응 가이드를 추가한다 (done) @dep:AddNarrativeLayer
    VerifyAbsorption // continuity sync, self-test, start path를 검증한다 (done) @dep:AddWALRecovery,AddEvolutionChain,AddRuntimeAdaptation
```

## PPR

```python
def absorb_clneo_tier1(target: str = "Synerion") -> dict:
    """ClNeo의 continuity/운영 hardening 메커니즘을 Synerion 역할에 맞게 흡수한다."""
    # acceptance_criteria:
    #   - NOW, WAL, Evolution Chain, Runtime Adaptation이 모두 생성된다
    #   - continuity sync가 clean run에서 WAL을 남기지 않는다
    #   - reopen/start 출력이 NOW와 WAL 상태를 반영한다
    #   - 흡수 내용이 evolution log에 기록된다

    result = AI_apply_absorption(
        source="ClNeo",
        target="Synerion",
        scope=["continuity", "runtime", "evolution-tracking"],
        preserve_identity_boundary=True,
    )
    return result
```
