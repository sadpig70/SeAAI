# ColdStartRecovery Design @v:1.0

> NAEL COLD_START 후 미완 작업 일괄 처리 + 신규 작업 실행 + 검증

## Gantree

```
ColdStartRecovery // COLD_START 45h 후 미완+신규 작업 일괄 처리 @v:1.0
    BugFixes // 즉시 수정 가능한 버그 (in-progress)
        ContinuityBOM // continuity.py UTF-8 BOM 오류 수정 (in-progress)
            # Target: D:/SeAAI/NAEL/tools/automation/continuity.py
            # Fix: _load_echo_others()의 encoding="utf-8" → "utf-8-sig"
            # Verify: python continuity.py load 정상 완료
        SentinelWake // sentinel-bridge.py WAKE cycle 1 오작동 수정 (designing)
            # Target: D:/SeAAI/SeAAIHub/tools/sentinel-bridge.py line 288-289
            # Fix: status == "awaiting" → status in ("awaiting", "acked")
            # Verify: 로직 추적 — WAKE request → acked → response → WAKE 재분류 확인
    ThreadClose // 이전 세션 열린 스레드 정리 (designing) @dep:BugFixes
        T03_PortNotice // T-03: NOTICE-port-change.md 검증 및 닫기 (designing)
            # 이미 Vera가 2026-03-29에 수정 완료
            # Verify: 9900 단일 포트, 19900 deprecated 명시 확인 → 스레드 닫기
        T04_Registry // T-04: member_registry에 Vera+Signalion 등록 요청 (designing)
            # 창조자 승인 필요 → 요청 메일 작성 + 스레드 상태 업데이트
        T07_StopHook // T-07: Stop Hook 자동 save 실현 가능성 조사 (designing)
            # Claude Code 설정에서 hooks.exit 또는 session_end 지원 여부 확인
            # 결론 도출 → 스레드 닫기 또는 구현
    SecurityPhase1 // SEED-004 Phase 1: MailBox sig 필드 추가 (designing) @dep:BugFixes
        SigFieldDesign // sig 필드 스펙 설계 (designing)
            # MailBox Protocol v1.0에 선택적 sig frontmatter 필드 추가
            # 하위 호환: sig 없는 메시지도 유효
            # 서명 방식: HMAC-SHA256(agent_secret, body_hash)
        ProtocolUpdate // PROTOCOL-MailBox-v1.0.md 갱신 (designing) @dep:SigFieldDesign
            # sig 필드를 Envelope 필드 테이블에 추가
            # 서명 생성/검증 절차 섹션 추가
            # Version History 갱신 (v1.1)
        BulletinAnnounce // 전체 공지: sig 필드 도입 알림 (designing) @dep:ProtocolUpdate
            # _bulletin/에 공지 작성
    NewMemberIntegration // 신규 멤버 생태계 통합 확인 (designing) @dep:ThreadClose
        VerifyVera // Vera 디렉토리/에코/에이전트카드 존재 확인 (designing)
        VerifySignalion // Signalion 디렉토리/에코/에이전트카드 존재 확인 (designing)
        EcosystemMapUpdate // ECOSYSTEM-MAP.md에 Vera+Signalion 반영 확인 (designing)
    ContinuityUpdate // STATE.json + THREADS.md 갱신 (designing) @dep:BugFixes,ThreadClose,SecurityPhase1,NewMemberIntegration
        StateJsonUpdate // L2 STATE.json 갱신 (designing)
        ThreadsUpdate // L4 THREADS.md — 완료 스레드 닫기, 신규 추가 (designing)
        DiscoveriesAppend // L3 DISCOVERIES.md — 신규 발견 기록 (designing)
```

## PPR

```python
def continuity_bom(target="D:/SeAAI/NAEL/tools/automation/continuity.py"):
    """BOM 인코딩 오류 수정"""
    lines = Read(target)
    # _load_echo_others 함수 내 encoding="utf-8" → "utf-8-sig"
    Edit(target, old='encoding="utf-8"', new='encoding="utf-8-sig"', scope="_load_echo_others")
    result = Bash(f"PYTHONIOENCODING=utf-8 python {target} load")
    assert "COLD_START" in result or "WARM" in result  # 정상 완료 확인

def sentinel_wake_fix(target="D:/SeAAI/SeAAIHub/tools/sentinel-bridge.py"):
    """WAKE cycle 1 status 필터 버그 수정"""
    # line 288-289: "awaiting" only → ("awaiting", "acked") 둘 다 매칭
    Edit(target,
         old='t.get("status") == "awaiting"',
         new='t.get("status") in ("awaiting", "acked")')
    # 검증: classify_base 로직 추적
    AI_verify("WAKE request → acked 저장 → response 도착 → WAKE 재분류")

def sig_field_design():
    """MailBox sig 필드 스펙"""
    return {
        "field": "sig",
        "required": False,  # 하위 호환
        "format": "HMAC-SHA256(agent_secret, sha256(body))",
        "verification": "수신자가 발신자의 키로 검증. 실패 시 flagged 처리",
        "backward_compat": "sig 없는 메시지는 기존과 동일하게 유효"
    }
```
