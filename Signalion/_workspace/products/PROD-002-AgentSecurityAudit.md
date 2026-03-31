# PROD-002: AI 에이전트 보안 감사 플랫폼 (v2 — 리뷰 반영)

> Signalion ADP 산출물 | 2026-03-29 v2
> 1차 리뷰: ClNeo REVISE / Synerion REVISE / NAEL BLOCK → 전 항목 반영

---

## WHY

기존 SAST/DAST는 에이전트 특유의 **신뢰 전파(trust propagation)** 구조를 전혀 모른다. 에이전트 A→B→C 위임 체인에서 A의 권한이 B를 거쳐 C까지 전파되는 구조는 전통 보안 도구의 분석 범위 밖이다. 42% 기업이 에이전트를 프로덕션에 배포했지만, 이 신뢰 전파를 감사할 도구는 존재하지 않는다.

---

## 접근 모델 (NAEL BLOCK 해제 조건)

**이 감사 도구는 Read-Only Log/Config Analysis 전용이다. Live Interception을 수행하지 않는다.**

| 모드 | 사용 여부 | 설명 |
|------|----------|------|
| Static Config Analysis | **O** | Agent Card JSON, MCP 설정 파일, 워크플로우 정의 분석 |
| Read-Only Log Analysis | **O** | 에이전트 실행 로그를 읽어 사후 분석 |
| Live Interception | **X (금지)** | 에이전트 호출을 가로채지 않음 — MITM 위험 차단 |

### 감사 도구 자체 보안 (Auditor-of-Auditor)

- **네트워크 격리**: 스캐너는 감사 대상과 별도 네트워크 세그먼트에서 실행
- **최소 권한(PoLP)**: 스캐너 자격증명은 읽기 전용. 쓰기/실행 권한 없음
- **수집 데이터 TTL**: 스캔 결과 90일 보관 후 자동 삭제. PII 데이터는 분석 즉시 해시화, 원본 미보관
- **암호화**: 저장 시 AES-256, 전송 시 TLS 1.3
- **접근 로그**: 모든 스캐너 데이터 접근을 불변 감사 로그에 기록

---

## Gantree (v2)

```
AgentSecurityAudit // v2 — Read-Only + Auditor-of-Auditor @v:2.0
    AuditorSecurity // 감사 도구 자체 보안
        NetworkIsolation // 스캐너 네트워크 격리
        CredentialManager // 읽기 전용 자격증명 관리 (PoLP)
        DataLifecycle // 수집 데이터 TTL + PII 즉시 해시화
        AuditorAuditLog // 스캐너 행동 불변 감사 로그
    Scanner // Read-Only 분석
        A2AScanner // A2A 구조 분석 (Config + Log)
            AgentCardValidator // Agent Card JSON 무결성 + 필수 필드 확인
            TrustPropagationAnalyzer // [ClNeo 추가] 위임 체인 신뢰 전파 추적
            CallbackConfigAudit // 콜백 설정 검증 (live 가로채기 아님)
        MCPScanner // MCP 설정 분석
            ToolPermissionCheck // 도구별 권한 검증 (R/W/X)
            InputPatternAudit // 프롬프트 인젝션 패턴 감지 (로그 기반)
            PIIExposureCheck // PII 노출 경로 분석 (원본 접근 X, 해시 비교)
        ChainAnalyzer // 체인 구조 분석
            TrustChainMap // 신뢰 체인 시각화 (정적 분석)
            BlastRadiusCalc // 폭발 반경 = "에이전트 A 침해 시 직접/간접 호출 가능한 에이전트·도구·데이터의 집합과 권한 총합"
            WeakLinkDetector // 체인 내 최약 링크 식별
    Reporter // 보고서
        VulnReport // OWASP AI Top 10 매핑 + A2A/MCP 특화 취약점 별도 열거
        AgentChainVulnTaxonomy // [ClNeo 추가] 에이전트 체인 특이 취약점 분류 체계
        ComplianceReport // ISO 42001 / EU AI Act 준수
        RemediationPlan // 수정 계획 자동 생성
    Monitor // 실시간 모니터링 (로그 기반, 비개입)
        LogStreamAnalyzer // [Synerion 명확화] 배포 후 런타임 로그 감지 (Scanner와 분리)
        AnomalyDetector // 비정상 패턴 탐지
        AlertSystem // 위협 등급별 알림
    DataFlowContract // [Synerion 추가] 레이어 간 데이터 계약
        ScanResultSchema // {severity, reversibility, affected_agents[], owasp_mapping[], chain_vuln_type}
        ScanUnit // 스캔 단위 = "하나의 에이전트 워크플로우 정의 파일 + 관련 로그"
```

## 수익 모델

| 티어 | 가격 | 기능 | 스캔 단위 |
|------|------|------|----------|
| Free | $0 | 월 5 워크플로우 스캔, 기본 취약점 | 1 워크플로우 = 1 스캔 |
| Pro | $49/mo | 무제한, OWASP + 체인 특화 분류, 실시간 로그 모니터링 | 동일 |
| Enterprise | $199/mo | 컴플라이언스 보고, SSO, PII 감사 + Auditor 감사 로그 | 동일 |

## 기술 스택
- **스캐너**: Rust (성능) — Read-Only 파일/로그 파서
- **분석**: Python (AI 패턴 매칭)
- **보안**: 네트워크 격리, AES-256, TLS 1.3, PoLP
- **프론트**: React + D3.js (체인 시각화)
- **인프라**: Docker (격리), PostgreSQL (감사 로그), 90일 TTL 자동 삭제
