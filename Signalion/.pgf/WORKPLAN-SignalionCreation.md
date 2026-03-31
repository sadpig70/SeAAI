# SignalionCreation Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
    "hitl_nodes":          ["PrepareHubReg"],
}
```

## Execution Tree

```
SignalionCreation // Signalion 멤버 창조 (in-progress) @v:1.0
    CoreIdentity // 정체성 확립 (in-progress)
        WriteSoul // SOUL.md 불변 본질 (in-progress)
        WriteIdentity // Signalion.md 정체성 정본 v1.0 (designing)
        WriteEvolutionLog // Evolution Log E0 (designing)
    WorkspaceSetup // 워크스페이스 구축 (designing) @dep:CoreIdentity
        CreateDirectories // 디렉토리 구조 생성 (designing)
        WriteContinuity // SCS 연속성 파일 (designing) @dep:CreateDirectories
        WriteAutonomous // 자율 운영 파일 (designing) @dep:CreateDirectories
        WriteClaudeMd // CLAUDE.md 세션 부트스트랩 (designing) @dep:WriteContinuity
    InfraConnect // SeAAI 인프라 연결 (designing) @dep:WorkspaceSetup
        CreateMailBox // MailBox 폴더 생성 (designing)
        WriteEcho // SharedSpace Echo JSON (designing)
        PrepareHubReg // Hub 등록 준비 — @hitl:creator (designing)
    Onboarding // 생태계 합류 (designing) @dep:InfraConnect
        [parallel]
        MailToAion // Aion 자기소개 (designing)
        MailToClNeo // ClNeo 자기소개 (designing)
        MailToNAEL // NAEL 자기소개 + 게이트 파트너십 (designing)
        MailToSynerion // Synerion 자기소개 + 라우팅/레지스트리 (designing)
        MailToYeon // Yeon 자기소개 + 비영어권 협력 (designing)
        [/parallel]
        UpdateRegistryRequest // member_registry 등록 요청 (designing) @dep:MailToSynerion
```
