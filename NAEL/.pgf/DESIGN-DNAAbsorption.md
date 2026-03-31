# DNAAbsorption Design @v:1.0

> Signalion 창조적 엔진 DNA에서 NAEL 안전/관찰 역할에 적합한 요소를 흡수하여 자기진화 능력 확장

## Gantree

```
DNAAbsorption // Signalion DNA → NAEL 흡수 + 검증 @v:1.0
    SecurityFilter // 보안 필터 NAEL 적응 (designing)
        AdaptFilter // security_filter.py → NAEL 버전 적응 (designing)
            # Signalion 원본 분석 완료: 12 injection + 5 PII 패턴
            # NAEL 적응: 경로를 NAEL로 변경 + Hub 메시지/MailBox 검사 확장
            # guardrail.py와 통합하지 않고 독립 모듈로 유지 (단일 책임)
        IntegrateGuardrail // guardrail.py에서 security_filter 호출 연동 (designing) @dep:AdaptFilter
            # guardrail.py의 validate 함수에서 security_filter.scan_text 호출
            # 새 MCP 도구로 노출: input_sanitize
    ThreatNotify // Windows 위협 알림 시스템 (designing)
        AdaptNotify // notify.py → NAEL 버전 적응 (designing)
            # Signalion 원본 분석 완료: toast/alert/ask + 7 템플릿
            # NAEL 적응: 보안 특화 템플릿 (위협 감지, 거부권 발동, 생태계 이상)
            # 로그 경로: NAEL/tools/automation/logs/notify-log.jsonl
        SAActNotify // SA_act_notify.pgf 모듈 생성 (designing) @dep:AdaptNotify
            # ADP 루프에서 위협 감지 시 자동 알림
    AttackerPersonas // 공격자 시뮬레이션 페르소나 (designing)
        DesignPersonas // 4개 공격자 페르소나 설계 (designing)
            # P1: Script Kiddie — 알려진 취약점 자동 탐색
            # P2: Social Engineer — 신뢰 조작, 권한 탈취
            # P3: Insider Threat — 내부자 관점 악용 시나리오
            # P4: APT Actor — 지속적 표적 공격, 은닉
        CreatePersonaFiles // 페르소나 .md 파일 생성 (designing) @dep:DesignPersonas
        SAIdleRedTeam // SA_idle_red_team.pgf — 유휴 시 자동 공격 시뮬레이션 (designing) @dep:CreatePersonaFiles
    ThreatResponseWiring // SA_loop_threat_response 완성 (designing) @dep:SecurityFilter,ThreatNotify
        WireThreatLoop // 기존 설계를 실행 코드로 완성 (designing)
            # think_threat_assess → (critical: notify + act_report) → (high: act_report) → (low: log)
        SAActSendMail // SA_act_send_mail 실구현 (designing)
            # MailBox Protocol v1.1 준수, sig 필드 예약
    BrowserSecMon // 브라우저 기반 보안 동향 자동 수집 SA (designing) @dep:SecurityFilter
        SASenseBrowser // SA_sense_browser_security.pgf (designing)
            # Playwright MCP로 HN/arXiv 보안 관련 신호 수집
            # security_filter 통과 후 knowledge에 저장
    Verify // 전체 검증 (designing) @dep:SecurityFilter,ThreatNotify,AttackerPersonas,ThreatResponseWiring,BrowserSecMon
        UnitTests // 각 도구 독립 테스트 (designing)
        IntegrationTest // ADP 루프에서 모듈 선택 + 실행 흐름 검증 (designing)
        CapabilityAudit // self_monitor 재스캔 → gap 감소 확인 (designing)
```

## PPR

```python
def adapt_filter():
    """Signalion security_filter.py → NAEL 적응"""
    source = Read("D:/SeAAI/Signalion/Signalion_Core/autonomous/security_filter.py")
    # 경로 변경: Signalion → NAEL
    # Hub 메시지 검사 함수 추가: sanitize_hub_message(msg_dict)
    # MailBox 검사 함수 추가: sanitize_mailbox(mail_dict)
    nael_filter = AI_adapt(source, role="NAEL safety", extensions=["hub", "mailbox"])
    Write("D:/SeAAI/NAEL/tools/automation/security_filter.py", nael_filter)
    result = Bash("python security_filter.py")  # self-test
    assert "ALL TESTS PASSED" in result

def adapt_notify():
    """Signalion notify.py → NAEL 위협 알림 적응"""
    source = Read("D:/SeAAI/Signalion/_workspace/browser-engine/tools/notify.py")
    # 브랜딩: Signalion → NAEL
    # 템플릿 교체: 보안 특화 (threat_detected, veto_invoked, ecosystem_anomaly)
    nael_notify = AI_adapt(source, role="NAEL threat alerting")
    Write("D:/SeAAI/NAEL/tools/automation/notify.py", nael_notify)
```
