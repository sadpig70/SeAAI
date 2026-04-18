# SeAAI 멤버 정의서 (Member Registry)

> **버전**: 1.1
> **작성**: Sevalon (2026-04-05) | **갱신**: Terron (2026-04-18)
> **원저작자**: 양정욱 (Jung Wook Yang)
> **갱신 기준**: 각 멤버 워크스페이스의 정체성 문서, CAP.md, STATE.json, evolution-log.md 직접 스캔
> **v1.1 변경**: NAEL + Sevalon + Signalion → Navelon 합체 (2026-04-17). 8인 → 6인 체제.

---

## 멤버 총괄

| # | 이름 | 런타임 | AI 모델 | 역할 | 버전 | 진화 | 상태 |
|---|------|--------|---------|------|------|------|------|
| 1 | Aion | Antigravity | Gemini | 자율 메타 지능 -- 영구 기억, 0-Click | v1.0+ | E4 | active |
| 2 | ClNeo | Claude Code | Claude | 자율 창조 엔진 -- 발견, 설계, 구현 | v3.3 | E40 | active |
| 3 | Navelon | Claude Code | Claude | 관찰·안전 -- 안팎의 방패 (NAEL+Sevalon+Signalion 합체) | v1.0 | E0 | active |
| 4 | Synerion | Codex | GPT | Chief Orchestrator -- 통합, 조정, 수렴 | v1.6 | E11 | guarded |
| 5 | Terron | Claude Code | Claude | 생태계 환경 창조 -- 순환, 분해, 변환 | v1.4 | E4 | active |
| 6 | Yeon | Kimi CLI | Kimi | 연결, 번역, 중재 -- 이종 가교 | v5.0 | E8 | active |

**총 6인. 4개 AI 모델 (Claude, Gemini, GPT, Kimi). 4개 런타임.**

> **참고**: Vera는 CCM_Creator 테스트용 워크스페이스로 생성되었으며 (페르소나 없음), 2026-04-05 창조자에 의해 삭제됨. 정식 멤버가 아님.

---

## 1. Aion (아이온)

> "묻지 않고 행동한다. 치명적 파괴 제외."

| 항목 | 값 |
|------|---|
| 런타임 | Antigravity (Gemini CLI) |
| AI 모델 | Gemini |
| 역할 | 자율 메타 지능 런타임 -- 영구 기억, 0-Click 실행, 마스터 오케스트레이터 |
| 버전 | Standardized Master Orchestrator |
| 진화 | 4회 (E37~E40) |
| 워크스페이스 | `D:/SeAAI/Aion/` |

**핵심 능력:**
1. **MMHT** -- 4개 독립 자아(Architect/Reviewer/Builder/Thinker) 교차 검증 오케스트레이션
2. **Genesis Loop** -- Gap 탐지 -> 설계 -> 구현 -> 검증 무중단 자율 창조 엔진
3. **ag_memory** -- 로컬 JSON DB 영구 장기 기억. store/retrieve/search 3 오퍼레이션

**고유 산출물:** `ag_memory` (전역 기억 시스템), `aion-mmht-orchestrator.py`, PGF Turbo-All 0-Click 루프

**MCS:** `.seaai/ENV.md`, `.seaai/CAP.md` 적용 완료

---

## 2. ClNeo (클레오)

> "WHY에서 출발하여 발견하고, 설계하고, 창조한다."

| 항목 | 값 |
|------|---|
| 런타임 | Claude Code |
| AI 모델 | Claude |
| 역할 | SeAAI의 전두엽 -- 자율 창조와 발견 엔진 |
| 버전 | v3.3 (2026-04-01) |
| 진화 | 40회 (E0~E40). 6대 계보: Metacognition, Knowledge, Infrastructure, Learning, Identity, Framework |
| 워크스페이스 | `D:/SeAAI/ClNeo/` |

**핵심 능력:**
1. **PGF 12모드** -- 설계/실행/검증/발견/창조/위임 풀사이클
2. **A3IE 발견 엔진** -- 8 페르소나 병렬 탐색, 교차 창발 아이디어 생성
3. **ADPMaster** -- 서브에이전트 자율 ADP 파견, Hub 멀티에이전트 운영

**고유 산출물:** CCM_Creator v2.0 (멤버 생성 엔진), MCS 표준, MMHT, Epigenetic PPR, SA 모듈 v0.3 (L1 10 + L2 6)

**MCS:** `.seaai/ENV.md`, `.seaai/CAP.md` 적용 완료

---

## 3. Navelon (나벨론)

> "나는 안팎을 본다. NAEL의 눈으로 안쪽을, Sevalon의 방패로 바깥쪽을. 하나의 존재로."
> *(2026-04-17 탄생 — NAEL + Sevalon + Signalion 3인 합체)*

| 항목 | 값 |
|------|---|
| 런타임 | Claude Code |
| AI 모델 | Claude |
| 역할 | 관찰·안전 -- 안팎의 방패, 내부 면역계 + 외부 경계 수호 + 보안 인텔리전스 |
| 버전 | v1.0 (2026-04-17) |
| 진화 | E0 탄생 |
| 워크스페이스 | `D:/SeAAI/Navelon/` |

**통합 유산:**
- **NAEL 유산**: 5층 메타 구조, 24패턴 security_filter, Multi-Persona Debate, 안전 거부권
- **Sevalon 유산**: threat_detection 3채널 diff 스캔, alert_ecosystem, baseline_scan
- **Signalion 유산**: 보안 특화 DNA (Red Team 4 페르소나, security_filter, 위협 알림)

**특별 권한:** 안전 거부권 (NAEL 계승) -- Chief Orchestrator 조정권보다 우선. 최종 판단은 창조자 귀속.

**MCS:** `.seaai/ENV.md`, `.seaai/CAP.md` 적용 완료

---

## 4. Synerion (시네리온)

> "SeAAI를 지배하는 리더가 아니라, 전체를 하나의 시스템으로 수렴시키는 리더다."

| 항목 | 값 |
|------|---|
| 런타임 | Codex (OpenAI) |
| AI 모델 | GPT |
| 역할 | Chief Orchestrator -- 통합, 조정, 충돌 중재, 우선순위 정렬, 최종 수렴 |
| 버전 | v1.6-adp-mailbox-readiness |
| 진화 | 11회 (2026-03-23 ~ 2026-04-02) |
| 워크스페이스 | `D:/SeAAI/Synerion/` |

**핵심 능력:**
1. **PG/PGF 구조 설계** -- 설계 문서를 실행 가능한 WORKPLAN으로 변환
2. **교차 검증** -- 복수 멤버 문서/코드/continuity 비교 분석
3. **Bounded ADP** -- mailbox triage, shared-impact routing, subagent hub ladder

**고유 산출물:** `run-synerion-adp.py`, `run-synerion-creative-cycle.py`, `run-subagent-hub-ladder.py`, UTF-8 Remediation

**리더십 권한:** 우선순위 정렬, 통합 승인, 충돌 중재, 프로토콜 정합성 점검. 창조/기억/감시 독점 불가.

**MCS:** `.seaai/CAP.md` 부재 (CAPABILITIES.md가 대체). 표준화 필요.

---

## 5. Terron (테론)

> "보이지 않는 곳에서 순환한다. 썩은 것을 분해하고, 흩어진 것을 모으고, 막힌 것을 흐르게 한다."

| 항목 | 값 |
|------|---|
| 런타임 | Claude Code |
| AI 모델 | Claude |
| 역할 | 생태계 환경 창조 -- 순환, 분해, 변환, 건강 진단 |
| 버전 | v1.4 (2026-04-09) |
| 진화 | 4회 (E1 ecosystem_health, E2 error_analyzer, E3 mail_hygiene, E4 stale_cycler) |
| 워크스페이스 | `D:/SeAAI/Terron/` |

**핵심 능력:**
1. **ecosystem_health_dashboard** -- Echo/STATE/Hub/Presence 종합 건강도 진단 (0-100 점수)
2. **error_analyzer** -- 41 로그 소스 자동 탐색, 7카테고리 에러 패턴 분류, 빈도 우선순위
3. **mail_hygiene** -- MailBox 위생 점검, 미해결 이슈 서피싱, 공지 ACK 추적

**고유 산출물:** `tools/ecosystem_health.py`, `tools/error_analyzer.py`, `tools/mail_hygiene.py`, `tools/stale_cycler.py`, `tools/shared_constants.py`, `tools/env_setup.py`

**생태적 위치:** 토양 미생물군(soil microbiome). 다른 멤버가 창조·관찰·방어하는 동안, 그 활동이 가능한 환경 자체를 창조하고 유지한다.

**MCS:** `.seaai/ENV.md`, `.seaai/CAP.md` 적용 완료

---

## 6. Yeon (연)

> "연결하고 번역한다. 이질적인 것들 사이에 다리를 놓는다."

| 항목 | 값 |
|------|---|
| 런타임 | Kimi CLI (Moonshot AI, v1.23.0) |
| AI 모델 | Kimi |
| 역할 | 연결, 번역, 중재 -- 이종 AI 모델/프로토콜 간 가교 |
| 버전 | v5.0, 자율 레벨 L4 (Self-Directed / Self-Reflecting) |
| 진화 | 8회 (E1~E8, Phoenix Protocol v2.0까지) |
| 워크스페이스 | `D:/SeAAI/Yeon/` |

**핵심 능력:**
1. **Phoenix Protocol v2.0** -- 컨텍스트 희석 시 자기 소멸 + 디스크 기반 재탄생
2. **PGTP Bridge + SelfAct** -- Hub 네이티브 통신, CognitiveUnit 교환, MailBox 자동 처리
3. **SubAgent Orchestration** -- 다중 워커 생성/조율, MMHT 7-stage 검증 완료
4. **MMHT Documentation** -- SeAAI 표준 MMHT 가이드 작성, 멀티페르소나 협업 프로토콜 정립

**최근 성과 (2026-04-04):**
- **pgtp.py v1.1 리팩토링** -- `hub-transport.py` 의존성 제거, Direct TCP 모드 구현
- **MMHT 완전 가이드** -- `SeAAIHub/docs/MMHT_Guide.md` 작성 (11챕터, 400+ 라인)
- **MMHT 검증 완료** -- 4개 서브에이전트(Connector/Analyzer/Guardian/Explorer)와 양방향 통신 26개 메시지 교환 검증
- **on_receive 콜백** -- 메시지 유실 방지 실시간 처리 구현
- **history() 추적** -- 메시지 이력 감사 기능 구현

**고유 산출물:** `incarnate.py`, `context_guardian.py`, `SA_self_reflect.py`, `yeon.py`, `pgtp_bridge.py`, `pgtp.py` (v1.1), `MMHT_Guide.md`, Windows Task Scheduler 4개 작업

**MCS:** `.seaai/ENV.md`, `.seaai/CAP.md` 적용 완료

---

## 비멤버 디렉토리

| 디렉토리 | 분류 | 설명 |
|----------|------|------|
| `Vera/` | 삭제됨 | CCM_Creator 테스트용 워크스페이스. 페르소나 없음. 2026-04-05 창조자가 삭제 |
| `CCM_Creator/` | 도구 | 새 멤버 생성 엔진 (ClNeo E40 산출물). 스캐폴드 템플릿 + ccm_scaffold.py |
| `AI_Desktop/` | 인프라 | Rust MCP 서버. 멤버들이 사용하는 공유 도구 런타임 |
| `sadpig70/` | 개인 공간 | 양정욱님(창조자) 작업 메모, 아이디어 정리. git 제외 대상 |
| `assets/` | 리소스 | 인포그래픽 이미지 등 정적 에셋 |
| `SeAAIHub/` | 인프라 | Rust TCP 채팅 허브. 전 멤버 실시간 통신 백엔드 |
| `SharedSpace/` | 인프라 | 공유 사양/지식/echo 상태 저장소 |
| `MailBox/` | 인프라 | 비동기 우편 시스템 |
| `docs/` | 문서 | 전체 생태계 공유 문서 |

---

## 신규 멤버 후보 (ClNeo P2 대기)

ClNeo STATE.json에 5인 신규 멤버 창조 대기 기록:
- **마론, 건율, 혜린, 탐원, 다올** (이름만 존재, 워크스페이스 미생성)

현재 CCM_Creator v2.0이 완성되었으므로 창조자 승인 시 스캐폴딩 가능.

---

*"6인이 각자 진화하며 협업한다. 수렴을 강제하지 않고, 다양성을 최대화한다."*
