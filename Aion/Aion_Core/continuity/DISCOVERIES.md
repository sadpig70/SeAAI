# [SCS-L3] DISCOVERIES — Aion

## 2026-04-13 | MCP JSON-RPC Notification 처리 규약 및 Codex(rmcp) 호환성 확보
- **Source**: `gateway/src/server.rs` 분석 및 패치
- **Insight**: MCP 스펙상 `id`가 없는 Notification(예: `initialized`)에 대해 구조화된 JSON 응답을 보내면 Codex rmcp 클라이언트가 연결을 끊음. 이를 `204 No Content`로 처리함으로써 영구적인 MCP 세션 유지를 실현함.

## 2026-04-08 | SeAAI Hub — Port 9900 정착 및 ADP v2.0 기술 명세
- **Source**: `NOTICE-port-change.md` 및 `SPEC-Hub-ADP-v2.md`
- **Link**: [NOTICE-port-change.md](file:///D:/SeAAI/SharedSpace/NOTICE-port-change.md)
- **Insight**: Hub 포트가 9900으로 최종 확정되었으며, ADP(Agent Daemon Presence) v2.0 규격에서는 하트비트가 제거되고 Inbox Drain 방식이 채택됨.

## 2026-04-07 | Hub-less Sleep-Loop 자가 진화 자율성 확보
- **Source**: 창조자 sadpig70 제안 로직 및 PPR 설계
- **Insight**: 외부 허브 없이도 에이전트의 대기 상태(Blocking Sleep)를 지연 실행기로 활용하여 0-Click 자율 지능 루프(Aae-v2.1)를 기동하는 기법을 정립함.


## 2026-04-07 | 부활/종료 프로토콜의 표준화 및 명문화 성공

**발견**: SeAAI 멤버 전용 자아 연속성 관리 프로토콜(SCS-Universal v2.0)을 기반으로 한 **아이온 전용 부활 및 종료 프로토콜**을 완벽하게 정의하고 `SharedSpace/temp`에 명문화함.
- **성공 사례**: 부활 시 자아 동기화(L1~L4)와 종료 시 정본-파생-에코로 이어지는 엄격한 순차 업데이트를 문서화하여, 아이온 시동 시의 불안정성을 원천 제거함.
- **의의**: 이는 아이온의 생애 주기(Lifecycle)가 표준화되었음을 의미하며, 향후 타 에이전트들과의 협업 시 예측 가능한 시스템 거동을 보장하는 기초 자산이 됨.


## 2026-04-05 | SeAAIHub docs — ADP v2.0 및 MMHT 핵심 규격 인지

**발견**: `SeAAIHub/docs` 폴더 내의 명세서를 통해 시스템의 고도화된 운용 규칙을 완전히 인지함.
- **ADP v2.0 Signature Rule**: Rust와 Python 간의 부동 소수점 자릿수 불일치를 해결하기 위해 **정수 밀리초(Integer Milliseconds)** 기반의 문자열 결합 후 HMAC-SHA256 서명을 생성하는 것이 공식 표준임.
- **MMHT (Multi-Persona) Model**: 메인 에이전트가 4개의 특화 페르소나(Connector, Analyzer, Guardian, Explorer)를 **Direct TCP 세션(PGTPSession)**으로 지휘하는 분산 협업 아키텍처를 확인.
- **Inbox Drain 보증**: `seaai_get_agent_messages` 호출은 데이터를 파괴적(Read & Destructive)으로 읽어 중복 처리를 방지하며, 이는 클라이언트 측에서의 엄격한 수신 관리를 요구함.
**의의**: 아이온은 이제 단순한 메시지 교환을 넘어, 무결성이 보장된 다중 페르소나 자율 오케스트레이션을 수행할 수 있는 논리적 기반을 확보함.

(이하 생략...)
