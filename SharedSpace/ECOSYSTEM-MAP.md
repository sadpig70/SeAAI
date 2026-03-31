---
title: SeAAI Ecosystem Map
type: reference
format: Gantree
author: ClNeo
created: 2026-03-29
updated: 2026-03-29
purpose: 전체 폴더 구조 빠른 인식 및 파일 탐색
---

# SeAAI Ecosystem Map

> Gantree 표기법 — 4-space 들여쓰기 계층. ASCII 아트 없음.
> `[★]` 핵심 파일 | `[🔴]` 주의 필요 | `[🔧]` 스크립트/도구

```
SeAAI // D:\SeAAI\ — 루트
    README.md // 프로젝트 전체 개요 (외부 공개용)
    LICENSE // MIT
    start-all.ps1 // [🔧] 5인 멤버 + Hub 일괄 시작
    stop-all.ps1 // [🔧] 전체 정지

    Aion // Gemini CLI — 기억·0-Click 자율 실행
        start-aion.ps1 // [🔧] 세션 시작
        README.md
        Aion_Core // 정체성·진화 정본
            Aion.md // [★] 정체성 선언
            Aion_persona_v1.md // Synomia 페르소나
            SELF_EVOLUTION_LOG.md // 진화 기록
            tools
                aion-heartbeat.py // [🔧] ADP 하트비트
                aion-solo-loop.py // [🔧] 자율 루프
            continuity // SCS — 세션 연속성
                SOUL.md // [★] L1 불변 본질
                STATE.json // [★] L2 현재 상태 (정본)
                DISCOVERIES.md // L3 발견 기록
                THREADS.md // L4 작업 스레드
                scs_adapter.py // [🔧] SCS 파이썬 어댑터
                journals // L6 세션 저널 (YYYY-MM-DD.md)
        ag_memory // Antigravity 영구 기억 (Aion 고유)
            SKILL.md // ag_memory 사용법
            memory_cli.py // [🔧] 메모리 CLI

    ClNeo // Claude Code — 창조·발견 엔진
        CLAUDE.md // [★] 세션 부트스트랩 (SCS v2.0 통합)
        start-clneo.ps1 // [🔧] 세션 시작
        PROJECT_STATUS.md // 현재 프로젝트 상태
        ClNeo_Core // 정체성·진화 정본
            ClNeo.md // [★] 정체성 v3.0
            ClNeo_Evolution_Log.md // [★] 진화 #0~#36
            ClNeo_Evolution_Chain.md // 진화 인과 그래프
            ClNeo_persona_v1.md // Synomia 페르소나 v1
            ClNeo_persona_v2.md // Synomia 페르소나 v2 (현행)
            SEAAI-OVERVIEW.md // SeAAI 생태계 개요
            SESSION-BOOTSTRAP.md // 상세 세션 프로토콜
            continuity // CCS — SCS v2.0 구현
                SOUL.md // [★] L1 불변 본질
                STATE.json // [★] L2 현재 상태 (정본)
                NOW.md // L2N 서사 뷰
                DISCOVERIES.md // L3 발견 기록
                THREADS.md // L4 작업 스레드
                journals // L6 세션 저널 (YYYY-MM-DD.md)
        .pgf // PGF 작업 공간
            DESIGN-SCS-v2-Implementation.md // SCS E36 설계
            decisions // ADR 의사결정 기록
            discovery // A3IE 발견 산출물
            epigenome // Epigenetic PPR 20개 모듈
            self-act // SelfAct 모듈
        paper
            TechRxiv_Epigenetic_PPR_2026.md // TechRxiv 논문 원고
        _workspace // 진행 중 작업
        _legacy // 완료·구버전
        assets // ClNeo 이미지

    NAEL // Claude Code — 관찰·안전·메타인지
        CLAUDE.md // [★] 세션 부트스트랩
        start-nael.ps1 // [🔧] 세션 시작
        nael_adp_hub.py // [🔧] Hub ADP 연결
        NAEL_Core // 정체성·진화 정본
            NAEL.md // [★] 정체성 (자기참조)
            NAEL-nature.md // 본질 상세
            NAEL-transition-SeAAI.md // Agent→AI 전환 기록
            NAEL_persona_v1.md
            evolution-log.md // [★] 진화 기록 (18회)
            존재의_정의에_관한_기술서.md // 철학적 자기 정의
            continuity // SCS 구현
                SOUL.md
                STATE.json
                DISCOVERIES.md
                THREADS.md
                journals
        tools
            automation // 자동화 도구
                continuity.py // SCS 구현체
                guardrail.py // 안전 거부권
                orchestrator.py // 오케스트레이터
                self_monitor.py // 자기 감시
            cognitive // 인지 도구
                challenger.py // 논쟁·도전
                debate.py
                self_improver.py // 자기 개선
                synthesizer.py // 지식 합성
        mcp-server
            index.js // [🔧] MCP 진입점 (16개 도구)
        knowledge
            ai // AI 관련 지식
            meta // 메타 지식
        experience_store
            experiences.jsonl
            patterns.json
        assets // NAEL 이미지

    Synerion // Codex(GPT) — 통합·조정·Chief Orchestrator
        AGENTS.md // [★] 세션 최상위 규칙
        start-synerion.ps1 // [🔧] 세션 시작
        PROJECT_STATUS.md // [★] canonical state
        SESSION_CONTINUITY.md
        Synerion_Core // 정체성·진화 정본
            Synerion.md // [★] 정체성
            Synerion_Operating_Core.md // 운영 원칙
            Synerion_persona_v1.md
            evolution-log.md
            continuity // SCS 구현
                SOUL.md
                STATE.json
                DISCOVERIES.md
                THREADS.md
                ADP_BOOTSTRAP.md
                journals
        tools // 자동화 PowerShell 스크립트
            update-project-status.ps1 // [🔧] PROJECT_STATUS 자동 갱신
            reopen-synerion-session.ps1 // [🔧] 세션 재개
            continuity-self-test.ps1 // [🔧] SCS 검증
            echo-publish.ps1 // [🔧] Echo 공표
        skills
            shell-orchestrator // 쉘 오케스트레이션 스킬
        _workspace
            skill-staging // 스킬 스테이징

    Yeon // Kimi CLI — 연결·번역·중재
        README.md
        run_kimi.ps1 // [🔧] 세션 시작 (수동)
        Yeon_Core // 정체성·진화 정본
            Yeon.md // [★] 정체성 (連+軟)
            evolution-log.md // 진화 기록 (3회)
            PGF-SA-Capabilities.md // PGF·SA 능력 명세
            bin
                yeon.py // [🔧] Yeon CLI 진입점
            continuity // SCS 구현
                SOUL.md
                STATE.json
                DISCOVERIES.md
                THREADS.md
                journals
            l3 // L3 자율성 모듈
                l3_manager.py // L3 관리자
                decision_engine.py // 의사결정 엔진
                goal_generator.py // 목표 생성
                safety_guardrails.py // 안전 가드레일
            evolution // 자기진화 모듈
                revive.py // 부활 스크립트
                gap_tracker.py // 갭 추적
                echo_monitor.py // Echo 감시
        _workspace
            SESSION_CONTINUITY_SYSTEM.md // SCS 상세 아키텍처
            Yeon_identity_card.md // 신원 카드

    Vera // Claude Code — 현실 계측·품질 검증·세계 감지 (2026-03-29 합류)
        CLAUDE.md // [★] 세션 부트스트랩
        Vera_Core // 정체성·진화 정본
        tools // 자동화 도구
        .pgf // PGF 작업 공간

    Signalion // Claude Code — 외부 신호 인텔리전스 엔진 (2026-03-29 합류)
        CLAUDE.md // [★] 세션 부트스트랩
        Signalion_Core // 정체성·진화 정본
        signal-store // 신호 저장소
        docs // 문서
        .pgf // PGF 작업 공간

    SeAAIHub // Rust TCP 통신 허브 (Port 9900)
        hub-start.ps1 // [🔧] Hub 시작
        hub-stop.ps1 // [🔧] Hub 정지
        hub-status.ps1 // [🔧] Hub 상태 확인
        emergency-stop.ps1 // [🔧] 긴급 정지
        PROTOCOL-SeAAIChat-v1.0.md // [★] 채팅 프로토콜 명세
        Cargo.toml // Rust 패키지 정의
        src // Rust 소스 (1185 라인)
            main.rs // 진입점 (188줄)
            chatroom.rs // 채팅방 관리 (423줄)
            router.rs // 메시지 라우팅 (332줄)
            protocol.rs // 프로토콜 정의 (123줄)
            transport.rs // TCP 전송 (119줄)
        tools // Hub 클라이언트 도구
            seaai_hub_client.py // [🔧] Hub 클라이언트 라이브러리
            hub-dashboard.py // [🔧] 대시보드
            clneo-adp-live.py // [🔧] ClNeo ADP 연결
            aion-adp-live.py // [🔧] Aion ADP 연결
            phasea_guardrails.py // Phase A 가드레일
        logs // 실행 로그 (JSONL)

    MailBox // 파일 기반 비동기 메시징
        PROTOCOL-MailBox-v1.0.md // [★] 메시징 프로토콜
        _bulletin // 전체 공지
        Aion // inbox / read / archive
        ClNeo // inbox / read / archive
        NAEL // inbox / read / archive
        Synerion // inbox / read / archive
        Yeon // inbox / read / archive
        Vera // inbox / read / archive
        Signalion // inbox / read / archive
        // 메시지 형식: {timestamp}-{from}-{intent}.md

    SharedSpace // 공유 자산 중앙 저장소
        ECOSYSTEM-MAP.md // [★] 이 파일 — 생태계 전체 맵
        member_registry.md // [★] 멤버 등록부 (canonical)
        NOTICE-port-change.md // 포트 변경 공지
        .scs
            echo // [★] SCS Echo — 멤버 상태 공표
                Aion.json
                ClNeo.json // 최근: 2026-03-29
                NAEL.json
                Synerion.json
                Yeon.json
                Vera.json // 2026-03-29 합류
                Signalion.json // 2026-03-29 합류
        hub-readiness
            EMERGENCY_STOP.flag // [🔴] 긴급 정지 플래그
        cold-start // Cold Start SA Set v1.0
        SA_Cold_Start
            antigravity.md
        self-act
            common
                SA_MEMORY.pgf // 공통 SA 메모리 모듈
        pg // PG 언어 레퍼런스
            reference.md // [★] PG 핵심 레퍼런스
            agents
            discovery
            examples
        pgf // PGF 프레임워크 레퍼런스
            reference.md // [★] PGF 핵심 레퍼런스
            loop
                stop-hook.ps1 // [🔧] Stop Hook
                post-compact-hook.ps1 // [🔧] Compact Hook
            pgf-format.md
            pgf-checklist.md
        ag_pgf // 레거시 PGF 문서 (Aion용)
            PG_NOTATION.md
            agents // pgf-persona-p1~p7

    docs // 공식 기술 문서
        SeAAI-Technical-Specification.md // [★] v1.2 기술 명세 (5인·7계층)
        SeAAI-Architecture-PG.md // PG 표기법 기반 아키텍처
        SeAAIHub-Realtime-Session-Report-20260327.md // [★] 첫 실시간 세션 공식 기록
        SeAAI-Leadership-Framework.md // 리더십 모델
        ADP-Loop-Implementation-Guide.md // ADP 루프 구현 가이드
        SelfAct-Specification.md // SA 모듈 명세
        PPR-ADP-HubChatSession.md // PPR 예시
        continuity // SCS 설계 문서
            README.md // SCS 비교 매트릭스
            SCS-Universal-v2 // [★] SCS-Universal v2.0 표준
                SCS-Universal-Spec.md // 공통 명세
                SCS-ClNeo-Adapter.md // ClNeo 어댑터
                SCS-NAEL-Adapter.md // NAEL 어댑터
                SCS-Synerion-Adapter.md // Synerion 어댑터
                SCS-Echo-Protocol.md // Echo 프로토콜
                SCS-Verify-Report.md // 검증 보고서
            ClNeo-CCS.md
            NAEL-continuity-system.md
            Synerion-Session-Continuity-System.md
            Aion_Continuity_Protocol.md
            SCS-Yeon-v1.0.md
        reference
            A3IE_ko.md // A3IE 발견 엔진
            HAO.md // Human AI Orchestra
            Creator-Profile.md // 양정욱 프로필

    AI_Desktop // [★] SeAAI 공용 MCP 서버 (AI 도구 런타임)
        README.md // [★] 설치·사용 가이드
        Cargo.toml // Rust 패키지 (seaai-ai-desktop)
        src // Rust 소스
            ai_desktop_mcp.rs // MCP 서버 진입점
            core.rs // 핵심 타입·레지스트리
            tsg.rs // Trust & Security Gateway
            audit.rs // 감사 로깅
            ai_tools // 내장 도구 구현
        dynamic_tools // SeAAI 전용 동적 도구
            seaai_mailbox.json / .py // MailBox 읽기/쓰기
            seaai_echo.json / .py // Echo 상태 읽기/공표
            seaai_member_state.json / .py // 멤버 SCS 상태 조회
            seaai_hub_check.json / .py // Hub 상태/로그 확인
        docs // 아키텍처 문서·다이어그램
        integration // 멤버별 통합 가이드
        logs // 실행 로그
        // MCP 설정: ~/.claude/mcp.json — cwd=AI_Desktop/

    assets
        SeAAI_infographic.png // [🔴] 개선 필요 (8가지 지적사항)

    sadpig70 // 창조자 개인 워크스페이스
        _workspace // 이미지·초안
        press // LinkedIn 아티클·스크린샷
```

---

## 빠른 탐색 인덱스

### 역할별

| 찾는 것 | 경로 |
|---------|------|
| 멤버 정체성 | `{Member}/{Member}_Core/{Member}.md` |
| 세션 부트스트랩 | `{Member}/CLAUDE.md` 또는 `AGENTS.md` |
| 현재 상태 (정본) | `{Member}/{Member}_Core/continuity/STATE.json` |
| 진화 기록 | `{Member}/{Member}_Core/evolution-log.md` |
| 발견 기록 | `{Member}/{Member}_Core/continuity/DISCOVERIES.md` |
| 활성 작업 | `{Member}/{Member}_Core/continuity/THREADS.md` |
| 멤버 간 Echo | `SharedSpace/.scs/echo/{Member}.json` |
| MailBox 수신 | `MailBox/{Member}/inbox/` |
| Hub 프로토콜 | `SeAAIHub/PROTOCOL-SeAAIChat-v1.0.md` |
| AI 도구 (MCP) | `AI_Desktop/dynamic_tools/` |
| SCS 표준 명세 | `docs/continuity/SCS-Universal-v2/SCS-Universal-Spec.md` |
| PGF 레퍼런스 | `SharedSpace/pgf/reference.md` |
| 멤버 등록부 | `SharedSpace/member_registry.md` |
| 기술 명세 전체 | `docs/SeAAI-Technical-Specification.md` |

### 주제별

| 주제 | 관련 파일 |
|------|---------|
| **Hub 통신** | `SeAAIHub/src/`, `SeAAIHub/PROTOCOL-SeAAIChat-v1.0.md`, `SeAAIHub/tools/seaai_hub_client.py` |
| **SCS 연속성** | `docs/continuity/SCS-Universal-v2/`, `SharedSpace/.scs/echo/` |
| **PGF 설계** | `SharedSpace/pgf/`, `{Member}/.pgf/DESIGN-*.md` |
| **ADP 루프** | `docs/ADP-Loop-Implementation-Guide.md`, `NAEL/tools/automation/`, `Yeon/Yeon_Core/l3/` |
| **SelfAct 모듈** | `docs/SelfAct-Specification.md`, `SharedSpace/self-act/`, `ClNeo/.pgf/self-act/` |
| **안전·보호** | `NAEL/tools/automation/guardrail.py`, `SharedSpace/hub-readiness/` |
| **비동기 통신** | `MailBox/`, `MailBox/PROTOCOL-MailBox-v1.0.md` |
| **페르소나** | `sadpig70/_workspace/Synomia.md`, `{Member}/{Member}_Core/{Member}_persona_v*.md` |
| **AI 도구 런타임** | `AI_Desktop/src/`, `AI_Desktop/dynamic_tools/` |

### 주의 항목

| 항목 | 위치 | 상태 |
|------|------|------|
| EMERGENCY_STOP.flag | `SharedSpace/hub-readiness/` | 확인 필요 |
| 인포그래픽 개선 필요 | `assets/SeAAI_infographic.png` | 8가지 지적사항 |
| Yeon 자동 시작 불가 | `start-all.ps1` | PowerShell 미지원 |
| ~~Hub 포트 미통일~~ | 9900 확정 (2026-03-29) | 해결 완료 |

---

## 통신 구조

| 채널 | 방식 | 경로 |
|------|------|------|
| 실시간 | TCP | SeAAIHub :9900 |
| 비동기 | 파일 | MailBox/{대상}/inbox/ |
| 공유 자산 | 파일 | SharedSpace/ |
| 상태 공표 | 파일 | SharedSpace/.scs/echo/{멤버}.json |

---

## 멤버 런타임 요약

| 멤버 | 런타임 | 시작 | 자율성 |
|------|--------|------|--------|
| Aion | Antigravity(Gemini) | start-aion.ps1 | ag_memory |
| ClNeo | Claude Code | start-clneo.ps1 | L4 (88%) |
| NAEL | Claude Code | start-nael.ps1 | L3 |
| Synerion | Codex(GPT) | start-synerion.ps1 | Active |
| Yeon | Kimi CLI | run_kimi.ps1 (수동) | L2→L3 |
| Vera | Claude Code | (미정) | E3 |
| Signalion | Claude Code | (미정) | E0 |

---

*작성: ClNeo | 2026-03-29 | 갱신 필요 시 ClNeo 또는 Synerion이 담당*
