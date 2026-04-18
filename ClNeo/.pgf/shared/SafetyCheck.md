# shared/SafetyCheck.md
# 안전 점검 공유 모듈 — 모든 시스템의 첫 번째 노드
# PGF Multi-Tree Shared Module v1.0

@version: 1.0

```
SafetyCheck // 실행 전 안전 점검
    @input:  context (ExecutionContext)
    @output: go | abort | warn

    EmergencyStop
        if exists("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag"):
            return ABORT("EMERGENCY_STOP 감지")

    HubStatus
        try: socket.connect(127.0.0.1:9900, timeout=2) → OK
        except: WARN("Hub 미실행. 일부 기능 제한.")

    DestructiveCheck
        if context.has_destructive_ops:
            AI_confirm_with_creator()  // 되돌릴 수 없는 작업 확인

    AuthorityCheck
        // 현재 작업이 ClNeo 권한 범위 내인가
        if context.touches_shared_infra:
            AI_verify_authorization()

    @output: safety_status (GO | ABORT | WARN)
```
