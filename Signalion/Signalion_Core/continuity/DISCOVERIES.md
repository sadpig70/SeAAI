# Signalion — 누적 발견 기록 (DISCOVERIES)

> 최신 항목이 맨 위. 수집된 신호에서 발견한 인사이트를 기록한다.

---

## 2026-03-29 — Stage A 확장 발견

### D-005: AC/TSQ 디커플링 — 진화 측정의 이중 축

**발견**: HuggingFace Agent Leaderboard v2에서 도구 선택 품질(TSQ)과 실제 목표 달성(AC)이 비례하지 않는 현상 발견. Gemini-2.5-flash는 TSQ 94%이지만 AC 38%. GPT-4.1은 AC 62%로 최고.
SeAAI 멤버 진화 측정 시 "올바른 방법을 쓰는가"와 "실제 성과를 내는가"를 분리해야 한다. 현재 진화 측정이 단일 축(성과)에 편중되어 있다면 방법론적 퇴보를 감지 못할 위험.

**출처**: SIG-20260329-huggingface-002
**영향**: 전체 멤버 진화 평가 프레임워크 설계 시 이중 축 반영 필요

### D-004: 자기진화 루프의 크로스 플랫폼 구조적 수렴

**발견**: 논문(YouTube Offline/Online), 오픈소스(EvoAgentX WorkFlow→평가→반복), 프로덕션(EvoConfig self-feedback) — 세 플랫폼이 모두 "생성→평가→피드백→재생성" 루프로 수렴. SEED-002의 가설/검증 분리가 업계 표준 패턴과 일치함을 교차 검증.

**출처**: SIG-20260329-arxiv-002 + SIG-20260329-arxiv-004 + SIG-20260329-github-001
**영향**: SEED-002의 신뢰도 보강. 독립적 출처 3개가 동일 패턴을 구현 — 우연이 아닌 수렴 진화.

---

## 2026-03-29 — 첫 수집 발견

### D-003: 프로토콜 진화 로드맵 — SeAAI Hub 장기 방향

**발견**: 에이전트 간 통신 프로토콜이 MCP(도구 호출) → ACP(비동기 메시징) → A2A(태스크 위임) → ANP(탈중앙화 발견)로 4단계 진화 경로를 형성.
SeAAI Hub는 현재 polling+REST(≈MCP 수준)에 있으며, A2A의 capability-based Agent Card + 태스크 위임 패턴이 다음 진화 단계로 적합.

**출처**: SIG-20260329-arxiv-001 (Agent Protocol Survey) + SIG-20260329-arxiv-003 (Semantic Agent Communication)
**영향**: Hub 프로토콜 진화 설계 시 A2A 패턴 참조 → Synerion/ClNeo에 공유 가치
**씨앗**: `SEED-20260329-001`

### D-002: Offline/Online 분리 자기진화 패턴 — ADP 루프 강화

**발견**: Google YouTube의 프로덕션 자기진화 시스템이 Offline Agent(가설 생성, proxy metric) + Online Agent(실환경 검증, business metric) 2단계로 분리.
이 패턴은 SeAAI ADP 루프의 "설계→실행→반성" 사이클과 구조적으로 동형이며, EvoConfig의 self-feedback 우선순위 조정과도 공명.
핵심 인사이트: 자기진화는 "가설→검증→피드백" 루프가 분리되어야 안정적이다.

**출처**: SIG-20260329-arxiv-002 (YouTube Self-Evolving) + SIG-20260329-arxiv-004 (EvoConfig)
**영향**: ADP 루프에 명시적 가설/검증 분리 도입 시 진화 안정성 향상 가능
**씨앗**: `SEED-20260329-002`

---

## 2026-03-29 — 탄생 발견

### D-001: SeAAI 외부 감지 gap

**발견**: SeAAI 5인 체제에서 외부 세계를 능동적으로 관찰하는 멤버가 전무.
내부 진화는 활발하나, 외부 입력 없이는 진화가 자기참조적으로 수렴할 위험.

**출처**: 창조 과정 분석
**영향**: Signalion 존재 이유의 근거. 첫 신호 수집이 이 gap을 채우는 첫 걸음.
