# SessionContinuitySystem Design @v:1.0

## Gantree

```text
SessionContinuitySystem // Synerion 세션 간 연속성 유지 시스템 구축 (designing) @v:1.0
    DefineCanonicalState // 연속성의 기준 파일과 읽기 순서를 정의한다 (designing)
    InstallDurableStatus // PROJECT_STATUS.md를 표준 상태 파일로 설치한다 (designing) @dep:DefineCanonicalState
    ImplementContinuityTools // save/reopen/self-test 스크립트를 구현한다 (designing) @dep:DefineCanonicalState
    UpdateStartupRules // AGENTS와 시작 스크립트에 continuity 규칙을 반영한다 (designing) @dep:InstallDurableStatus,ImplementContinuityTools
    VerifyResumeFlow // 생성-재개-검증 흐름을 실제로 확인한다 (designing) @dep:UpdateStartupRules
```

## PPR

```python
def continuity_system_install(workspace: Path) -> dict:
    """
    세션 간 불연속성을 줄이기 위해
    1) canonical state file
    2) continuity guide
    3) save/reopen/self-test scripts
    4) startup rules
    를 함께 설치한다.
    """
    # acceptance_criteria:
    #   - PROJECT_STATUS.md가 세션 상태의 기준 파일로 생성된다.
    #   - continuity guide가 시작/종료 절차를 정의한다.
    #   - save/reopen/self-test 스크립트가 동작한다.
    #   - AGENTS.md와 start-synerion.ps1이 PROJECT_STATUS를 재개 흐름에 포함한다.
    #   - 다음 세션이 PROJECT_STATUS.md만으로 현재 맥락을 빠르게 복원할 수 있다.
```

