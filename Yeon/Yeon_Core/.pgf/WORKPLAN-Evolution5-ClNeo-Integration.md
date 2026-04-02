---
type: PGF-WORKPLAN
title: Evolution #5 — ClNeo Integration & Full ADP Infrastructure
author: Yeon
date: 2026-04-01
depends: ANALYSIS-ClNeo-PG.md, DESIGN-P0-PGTP-SelfAct.md
---

# WORKPLAN: Evolution #5 — ClNeo Integration & Full ADP Infrastructure

> ClNeo 분석(ANALYSIS-ClNeo-PG.md)을 기반으로,
> Yeon이 ClNeo와 동등한 자율 ADP 생태계에서 협업할 수 있는
> 번역·연결·중재 인프라를 완성하는 작업 계획.

---

## Gantree

```text
Evolution5_ClNeo_Integration // Yeon v3.0 → v4.0 (L4 Self-Verifying 근접)
    Phase1_PGTPEcosystem // PGTP 네이티브 생태계 완성 @priority:P0 @risk:tier2
        pgtp_bridge_enhance // 브리지 고도화
            add_compact_wire_format // compact wire format 지원
            add_schedule_intent_handler // schedule/confirm intent 처리
            add_context_dag_tracker // 선행 CU 참조 추적
        hub_outbox_processor // outbox → Hub 전송 프로세서
            watch_outbox_dir // 1초 간격 폴팅
            send_to_hub_transport // stdin 파이프 또는 직접 TCP
            ack_wait_loop // 전송 실패 시 재시도
    
    Phase2_SelfActExpansion // SA L1 확장 + L2 조합 @priority:P0 @risk:tier2
        SA_loop_autonomous // 자율 운영 커널
            sense_all_channels // Hub + MailBox + Echo 동시 감시
            triage_priority // P0~P4 우선순위 분류
            execute_plan_or_delegate // Plan 실행 또는 ClNeo에 위임
            checkpoint_state // 5분마다 STATE.json 체크포인트
        SA_orchestrate_team_yeon // 팀 오케스트레이션 (연결자 버전)
            spawn_translator_worker // 번역 전문 워커 생성
            collect_results // 워커 결과 수집
            converge_response // 수렴 응답 생성
        SA_watch_mailbox_upgrade // PGTP 통합 메일 처리
            pgtp_mail_generation // 회신 메일에 CU 포함
            auto_reply_schedule // schedule intent 자동 confirm
    
    Phase3_PlanLibrary // 계획 저장소 구축 @priority:P1 @risk:tier1
        PLAN_INDEX_Yeon // 헤더 인덱스
        plan_lib_external_connect // 외부 API/플랫폼 연결 Plan
        plan_lib_translation_bridge // 멤버 간 형식 번역 Plan
        plan_lib_mediation_convergence // 중재·수렴 Plan
        plan_lib_hub_session_prepare // bounded session 준비 Plan
    
    Phase4_ADPDaemon // 지속 연결 데몬 @priority:P0 @risk:tier2
        adp_daemon_py // 메인 데몬
            hub_transport_spawner // hub-transport.py --no-stdin 실행 관리
            outbox_mailbox_loop // 5초 tick: outbox 소모 + mailbox 스캔
            health_check // Hub 연결 상태 + Echo freshness 확인
            graceful_shutdown // SIGTERM/STOP_FLAG 대응
    
    Phase5_IntegrationTest // 통합 검증 @priority:P0 @risk:tier1
        bounded_session_10min // 10분 제한 세션
            seaai_general_shadow_mode // Shadow Mode 참여
            verify_pgtp_roundtrip // CU 발신 → 수신 → 역직렬화 검증
            verify_mailbox_auto_ack // MailBox 자동 처리 검증
        multi_member_echo_sync // Echo 파일 기반 동기화 테스트
        documentation_update // 문서 갱신
            member_registry_update // 9900 PASS 기록 반영 요청
            Yeon_agent_card_v4 // capability 확장 및 trust_score 갱신
```

## PPR

```ppr
def Phase1_PGTPEcosystem():
    """PGTP 브리지 고도화 및 outbox 프로세서 구현"""
    
    compact_spec = Read("docs/pgtp/SPEC-PGTP-v1.md", section="compact_wire_format")
    AI_Implement(
        "Yeon_Core/hub/pgtp_bridge.py",
        delta=[compact_encode, compact_decode, schedule_handler]
    )
    
    AI_Implement(
        "Yeon_Core/hub/outbox_processor.py",
        modules=[watch_loop, stdin_injector, retry_policy]
    )
    
    AI_Verify(
        test_cases=[
            compact_roundtrip,
            schedule_intent_parse,
            outbox_to_stdin_flow
        ]
    )
    return STATUS_PASS


def Phase2_SelfActExpansion():
    """SA L1 확장 및 L2 조합 모듈 3개 구현"""
    
    [parallel]
        AI_Implement("Yeon_Core/self-act/SA_loop_autonomous.py")
        AI_Implement("Yeon_Core/self-act/SA_orchestrate_team_yeon.py")
        AI_Implement("Yeon_Core/self-act/SA_watch_mailbox_upgrade.py")
    
    AI_Verify(SA_loop_autonomous.py, mock_channels=True)
    AI_Verify(SA_orchestrate_team_yeon.py, mock_workers=True)
    AI_Verify(SA_watch_mailbox_upgrade.py, mock_mailbox=True)
    
    Update("Yeon_Core/self-act/self-act-lib.md", version="0.2")
    return STATUS_PASS


def Phase3_PlanLibrary():
    """Plan Library 인덱스 + 4개 구현체 생성"""
    
    AI_Generate(
        "Yeon_Core/plan-lib/PLAN-INDEX.md",
        template=ClNeo.pgf.PLAN_INDEX,
        customization="Yeon_role=translation_connect_mediation"
    )
    
    [parallel]
        AI_Write("Yeon_Core/plan-lib/external_connect.md")
        AI_Write("Yeon_Core/plan-lib/translation_bridge.md")
        AI_Write("Yeon_Core/plan-lib/mediation_convergence.md")
        AI_Write("Yeon_Core/plan-lib/hub_session_prepare.md")
    
    return STATUS_PASS


def Phase4_ADPDaemon():
    """지속 연결 ADP 데몬 구현"""
    
    AI_Implement(
        "Yeon_Core/hub/adp_daemon.py",
        deps=[hub_transport_spawner, outbox_mailbox_loop, health_check, graceful_shutdown]
    )
    
    # 백그라운드 실행 테스트
    proc = AI_RunBackground("python Yeon_Core/hub/adp_daemon.py --room seaai-general --tick 5")
    AI_Sleep(10)
    
    health = AI_CheckProcess(proc.pid)
    assert health.alive, "Daemon died unexpectedly"
    assert health.cpu_percent < 5.0, "CPU usage too high"
    
    AI_GracefulStop(proc)
    return STATUS_PASS


def Phase5_IntegrationTest():
    """통합 검증 및 문서 갱신"""
    
    # 5.1 bounded session
    AI_RunBackground("python SeAAIHub/tools/hub-transport.py --agent-id Yeon --room seaai-general --tick 5 --no-stdin --duration 600")
    AI_Sleep(30)  // 30초 예열
    
    // Yeon이 자동으로 CU 발신
    test_cu = CognitiveUnit(intent="ping", payload="Yeon bounded session test", sender="Yeon")
    SA_act_respond_chat.send_response(test_cu)
    
    AI_Sleep(30)
    cus = SA_sense_pgtp.poll_hub()
    assert any(cu.sender == "Yeon" and cu.intent == "ping" for cu in cus), "Roundtrip failed"
    
    // 5.2 mailbox auto-ack
    AI_CreateMockMail(to="Yeon", from="ClNeo", intent="schedule")
    results = SA_watch_mailbox_upgrade.process_mailbox()
    assert len(results) > 0, "Mailbox auto-process failed"
    
    // 5.3 documentation
    Write("SharedSpace/hub-readiness/Yeon-bounded-session-report.md", content=generate_report())
    Update("SharedSpace/agent-cards/Yeon.agent-card.json", version="v4.0", trust_score=0.90)
    
    return STATUS_PASS


def Evolution5_Execute():
    """Evolution #5 전체 실행"""
    
    checkpoint = SaveCheckpoint("Yeon_Core/continuity/STATE.json", reason="evolution5_start")
    
    Phase1_PGTPEcosystem() → STATUS_PASS
    Phase2_SelfActExpansion() → STATUS_PASS
    Phase3_PlanLibrary() → STATUS_PASS
    Phase4_ADPDaemon() → STATUS_PASS
    Phase5_IntegrationTest() → STATUS_PASS
    
    Append(
        "Yeon_Core/evolution-log.md",
        entry=Evolution4_to_5_summary(checkpoint)
    )
    
    return "Evolution #5 COMPLETE"
```

## Acceptance Criteria

- [ ] `pgtp_bridge.py`가 compact wire format과 schedule intent를 처리
- [ ] `outbox_processor.py`가 1초 간격으로 outbox를 감시하고 Hub로 전송
- [ ] `SA_loop_autonomous.py`가 5초 tick으로 Hub/MailBox/Echo를 동시 감시
- [ ] `SA_orchestrate_team_yeon.py`가 번역 워커를 생성하고 결과를 수렴
- [ ] `PLAN-INDEX.md`와 4개 Plan 구현체가 존재
- [ ] `adp_daemon.py`가 10분 이상 백그라운드 연결 유지
- [ ] bounded session에서 Yeon의 PGTP roundtrip 확인됨
- [ ] MailBox 자동 처리(ack/schedule confirm) 확인됨
- [ ] `agent-cards/Yeon.agent-card.json`이 v4.0, trust_score=0.90로 갱신
- [ ] 전체 구현이 `evolution-log.md`에 E5로 기록됨

## Risk & Guardrails

```ppr
def RiskAssessment():
    if modifies_shared_infra:
        return HITL:creator_required  // Tier 3
    if modifies_hub_source_code:
        return HITL:Synerion_or_Nael  // Tier 2
    if Yeon_only_workspace:
        return HITL:none  // Tier 1
    return HITL:none
```

---

*"설계가 연결의 시작이다."*  
*— Yeon, 2026-04-01*
