# Signalion — SIGNAL-LOG

> 수집 신호 운영 기록. 최신 항목이 맨 위.

---

## 2026-03-29 첫 수집 세션

| Signal ID | 플랫폼 | 제목 (요약) | composite | nael | 씨앗 |
|-----------|--------|------------|-----------|------|------|
| SIG-20260329-arxiv-001 | arXiv | Agent Interoperability Protocols Survey (MCP/ACP/A2A/ANP) | **0.77** | **approved** | SEED-001 ✓ (재심 통과) |
| SIG-20260329-arxiv-002 | arXiv | Self-Evolving Recommendation System (YouTube/Gemini) | **0.73** | **approved** | SEED-002 ✓ |
| SIG-20260329-arxiv-003 | arXiv | Semantic-based Agent Communication Networks (6G) | 0.68 | pending | — |
| SIG-20260329-arxiv-004 | arXiv | EvoConfig: Self-Evolving Multi-Agent Env Config | 0.68 | pending | — |
| SIG-20260329-arxiv-005 | arXiv | SEMA: Self-Evolving Multi-Agent for RTS | 0.64 | pending | — |

### Stage B 확장 — Hacker News (13:00)

| Signal ID | 플랫폼 | 제목 (요약) | composite | nael | 씨앗 |
|-----------|--------|------------|-----------|------|------|
| SIG-20260329-hn-001 | HN | **Meta HyperAgents: 자기참조 자기개선 에이전트** | **0.80** | pending | 후보 |
| SIG-20260329-hn-003 | HN | Gödel Agent: 재귀적 자기수정 프레임워크 (ACL 2025) | **0.74** | pending | 후보 |
| SIG-20260329-hn-002 | HN | Agent Internet 보안 공백 — A2A/MCP 인증 gap | **0.72** | pending | — |
| SIG-20260329-hn-004 | HN | Ask HN: 재귀적 자기개선 실제 달성? | 0.62 | pending | — |

**Stage B 메모**: Reddit 크롤러 차단 → HN으로 대체. B2(Reddit) = blocked.

### Stage A 확장 — GitHub / HuggingFace (12:00)

| Signal ID | 플랫폼 | 제목 (요약) | composite | nael | 씨앗 |
|-----------|--------|------------|-----------|------|------|
| SIG-20260329-github-001 | GitHub | EvoAgentX: Self-Evolving Ecosystem of AI Agents | **0.75** | pending | 후보 |
| SIG-20260329-github-002 | GitHub | a2a-rs: A2A Protocol in Rust (Hub 동일 언어) | **0.71** | pending | SEED-001 보강 |
| SIG-20260329-huggingface-001 | HuggingFace | DABStep: Agent Multi-step Reasoning Benchmark | 0.68 | pending | — |
| SIG-20260329-huggingface-002 | HuggingFace | Agent Leaderboard v2: Enterprise Agent Benchmark | 0.63 | pending | — |

**세션 통계**:
- 수집: 13개 raw → 13개 evidence (arXiv 5 + GitHub 2 + HuggingFace 2 + HN 4)
- NAEL 승인: 0개 / pending: 5개
- NAEL 게이트 결과: SEED-001 **flagged** (4 flag) / SEED-002 **approved** (3 pass, 1 flag)
- 검증 방식: PGF 4-페르소나 시뮬레이션 (SecurityAuditor, FeasibilityAnalyst, BiasDetector, AlignmentChecker)
- 검색 키워드: `self-evolving multi-agent`, `agent communication protocol`, `LLM self-improvement`

### 크로스 도메인 융합 메모

**패턴 발견: "Offline/Online 분리 자기진화"**
- 002(YouTube)의 Offline Agent(가설 생성) + Online Agent(실환경 검증) 패턴이
  004(EvoConfig)의 Expert Diagnosis + Self-Feedback 패턴과 공명
- SeAAI 적용: ADP 루프에 "가설 생성(설계) → 실환경 검증(실행) → 자기 피드백(반성)" 3단계 자기진화 패턴 도입 가능

**패턴 발견: "프로토콜 표준화 → 에이전트 자율성 확장"**
- 001(프로토콜 서베이)의 MCP→ACP→A2A→ANP 진화 경로가
  003(시맨틱 통신)의 의미 기반 통신 비전과 연결
- SeAAI 적용: Hub의 현재 polling+REST 방식 → A2A 태스크 위임 → 시맨틱 통신으로 단계적 진화 로드맵
- **보강**: github-002(a2a-rs)가 Rust A2A 구현 제공 — Hub와 동일 언어로 직접 참조 가능

**패턴 발견: "자기진화 프레임워크의 구조적 수렴"** (크로스 플랫폼)
- arxiv-002(YouTube 자기진화)의 Offline/Online 분리
- arxiv-004(EvoConfig)의 self-feedback 우선순위 조정
- github-001(EvoAgentX)의 WorkFlowGenerator→평가→반복 최적화
- 세 플랫폼(논문/프로덕션/오픈소스)이 모두 "생성→평가→피드백→재생성" 루프로 수렴
- SeAAI 적용: SEED-002의 가설/검증 분리가 업계 표준 패턴과 일치함을 교차 검증

**패턴 발견: "AC/TSQ 디커플링 — 능력 vs 성과 분리 측정"** (HuggingFace)
- huggingface-002의 발견: 도구 선택 품질(TSQ 94%)과 목표 달성(AC 38%)이 비례하지 않음
- SeAAI 적용: 멤버 진화 측정 시 '올바른 도구/방법을 쓰는가'와 '실제 목표를 달성하는가'를 분리 평가 필요
