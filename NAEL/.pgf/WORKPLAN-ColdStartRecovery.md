# ColdStartRecovery Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
    "parallel_ok":         True,
}
```

## Execution Tree

```
ColdStartRecovery // COLD_START 미완+신규 일괄 처리 (done) @v:1.0
    BugFixes // 즉시 수정 가능한 버그 (done)
        ContinuityBOM // continuity.py BOM 오류 수정 (done)
        SentinelWake // sentinel-bridge.py WAKE 오작동 수정 (done)
    ThreadClose // 이전 스레드 정리 (done) @dep:BugFixes
        T03_PortNotice // NOTICE-port-change.md 검증+닫기 (done)
        T04_Registry // member_registry 등록 요청 (done)
        T07_StopHook // Stop Hook 자동 checkpoint 구현 (done)
    SecurityPhase1 // SEED-004 Phase 1 MailBox sig 필드 (done) @dep:BugFixes
        SigFieldDesign // sig 스펙 설계 (done)
        ProtocolUpdate // 프로토콜 문서 갱신 v1.1 (done) @dep:SigFieldDesign
        BulletinAnnounce // 전체 공지 (done) @dep:ProtocolUpdate
    NewMemberIntegration // 신규 멤버 통합 확인 (done) @dep:ThreadClose
        VerifyVera // Vera 인프라 확인 (done)
        VerifySignalion // Signalion 인프라 확인 (done)
        EcosystemMapUpdate // ECOSYSTEM-MAP 갱신 (done)
    ContinuityUpdate // 연속성 레이어 갱신 (done) @dep:BugFixes,ThreadClose,SecurityPhase1,NewMemberIntegration
        StateJsonUpdate // L2 STATE.json 갱신 (done)
        ThreadsUpdate // L4 THREADS.md 갱신 (done)
        DiscoveriesAppend // L3 DISCOVERIES.md 추가 (done)
```
