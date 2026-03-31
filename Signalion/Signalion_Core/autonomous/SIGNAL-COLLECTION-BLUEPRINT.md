# SeAAI 외부 리소스 수집 & 창발적 제품 생성 블루프린트

> Signalion 작성 | 2026-03-29 | v1.0
> SeAAI가 외부 세계에서 수집할 수 있는 모든 리소스와, 그것으로 만들 수 있는 모든 것.

---

## Part 1: 외부 리소스 수집 — 채널 × 방법 × 도구

### 1.1 학술/연구 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **arXiv** | REST API (공개) | 무료 | 논문 메타데이터, 초록, PDF | `arxiv` Python 패키지, 직접 HTTP |
| **Semantic Scholar** | REST API | 무료 (100 req/5min) | 논문 인용 그래프, 영향력 점수 | `semanticscholar` 패키지 |
| **Papers With Code** | REST API | 무료 | 논문→코드 매핑, SOTA 벤치마크 | HTTP 직접 호출 |
| **Google Scholar** | 비공식 스크래핑 | 무료 (제한적) | 인용 수, 관련 논문 | ScrapeGraphAI, SerpAPI ($50/mo) |
| **OpenAlex** | REST API | 완전 무료 | 2억+ 학술 저작물, 인용 네트워크 | HTTP 직접 호출 |
| **ACL Anthology** | 공개 데이터 | 무료 | NLP/CL 논문 전문 | HTTP |
| **bioRxiv/medRxiv** | REST API | 무료 | 생명과학/의학 프리프린트 | HTTP |

### 1.2 오픈소스/코드 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **GitHub** | REST API v3 / GraphQL v4 | 무료 (5000 req/hr) | Trending repos, releases, stars, README | `gh` CLI, `PyGithub` |
| **GitHub Trending** | 스크래핑 | 무료 | 일간/주간 트렌드 | Firecrawl, Spider |
| **GitLab** | REST API | 무료 | 오픈소스 프로젝트 | HTTP |
| **HuggingFace** | `huggingface_hub` API | 무료 (추론 30K char/mo) | 모델, 데이터셋, Spaces, 트렌딩 | `huggingface_hub` 패키지 |
| **PyPI / npm** | REST API | 무료 | 패키지 다운로드 트렌드 | HTTP |
| **Docker Hub** | REST API | 무료 | 컨테이너 이미지 트렌드 | HTTP |

### 1.3 커뮤니티/토론 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **Hacker News** | Algolia API (공식) | 완전 무료 | 스레드, 댓글, 포인트, Ask/Show HN | `hn` 패키지, HTTP |
| **Reddit** | PRAW (OAuth 2.0) | 무료 (100 req/min) | r/MachineLearning, r/LocalLLaMA 등 | `praw` (크롤러 차단 가능) |
| **Reddit 대안** | Pullpush.io API | 무료 | Reddit 아카이브 | HTTP |
| **Stack Overflow** | REST API v2 | 무료 (10K req/day) | AI/ML 태그 질문 트렌드 | HTTP |
| **Discord** | Bot API | 무료 | AI 커뮤니티 서버 (LangChain, HF 등) | `discord.py` |
| **Discourse 포럼** | REST API | 무료 | LangChain Forum, HF Forum 등 | HTTP |

### 1.4 소셜/뉴스 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **X (Twitter)** | API v2 Free tier | 무료 (극히 제한: 1 req/15min) | AI 전문가 트윗, 반응 | 공식 API (제한적) |
| **X 대안** | Apify X Scraper | 유료 ($49/mo~) | 대량 트윗 수집 | Apify Actor |
| **X 대안 2** | Nitter 인스턴스 | 무료 (불안정) | 공개 트윗 RSS | RSS 파서 |
| **X 대안 3** | xpoz.ai | 무료 tier | X 데이터 검색 | REST API |
| **Product Hunt** | GraphQL API | 무료 | 신제품 런칭, 투표, 카테고리 | HTTP |
| **TechCrunch** | RSS + 스크래핑 | 무료 | AI 스타트업 뉴스 | Firecrawl |
| **The Verge / Ars Technica** | RSS | 무료 | AI 기술 뉴스 | RSS 파서 |
| **VentureBeat** | RSS | 무료 | AI 산업 뉴스 | RSS 파서 |
| **AI-specific 뉴스** | RSS/스크래핑 | 무료 | The Batch (Andrew Ng), Import AI | RSS |

### 1.5 해커톤/경진대회 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **Devpost** | 페이지 스크래핑 | 무료 | 해커톤 프로젝트, 수상작, 기술 스택 | Firecrawl, Spider |
| **Kaggle** | REST API | 무료 | 대회, 노트북, 데이터셋 트렌드 | `kaggle` CLI |
| **MLContests.com** | 스크래핑 | 무료 | AI/ML 대회 목록 | HTTP |
| **Lablab.ai** | 스크래핑 | 무료 | AI 해커톤 프로젝트 갤러리 | Firecrawl |
| **DrivenData** | REST API | 무료 | 사회적 영향 AI 대회 | HTTP |

### 1.6 시장/비즈니스 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **Crunchbase** | REST API | 유료 ($29/mo~) | 스타트업 펀딩, 투자자 | API |
| **Y Combinator** | 공개 디렉토리 | 무료 | YC 배치 AI 스타트업 | 스크래핑 |
| **AngelList / Wellfound** | 스크래핑 | 무료 | AI 스타트업 채용, 제품 | Firecrawl |
| **G2 Reviews** | 스크래핑 | 무료 | AI SaaS 사용자 리뷰 | Firecrawl |
| **Gartner / Deloitte 보고서** | 공개 요약 | 무료 (전문 유료) | 시장 예측, 트렌드 | WebSearch |
| **Statista** | 제한적 공개 | 무료 (기본) | AI 시장 통계 | WebSearch |

### 1.7 벤치마크/리더보드 채널

| 채널 | API/접근 방법 | 비용 | 수집 대상 | 도구 |
|------|-------------|------|----------|------|
| **LMSYS Chatbot Arena** | 공개 리더보드 | 무료 | LLM 실시간 Elo 순위 | 스크래핑 |
| **Open LLM Leaderboard** | HuggingFace Space | 무료 | 오픈 모델 벤치마크 | HF API |
| **GAIA Benchmark** | HuggingFace Space | 무료 | 에이전트 벤치마크 | HF API |
| **SWE-bench** | GitHub | 무료 | 코딩 에이전트 벤치마크 | GitHub API |
| **Agent Leaderboard v2** | HuggingFace | 무료 | 엔터프라이즈 에이전트 | HF API |

### 1.8 수집 자동화 도구 (AI Desktop 연동)

| 도구 | 유형 | 비용 | 강점 |
|------|------|------|------|
| **Firecrawl** | 오픈소스 + API | 무료 tier (500 페이지/mo) | 웹→마크다운 변환. LLM 최적화 |
| **Spider** | Rust 오픈소스 | 완전 무료 | 초고속 크롤링. Rust → AI Desktop 통합 가능 |
| **ScrapeGraphAI** | 오픈소스 + API | 무료 | MCP 지원. Claude 직접 연동 가능 |
| **Crawl4AI** | 오픈소스 | 완전 무료 | VLM 기반 제로샷 추출 |
| **Apify** | 플랫폼 | 무료 tier ($5/mo~) | 1000+ 사전 구축 Actor |
| **Browse AI** | No-code | 무료 tier (50 크레딧) | 모니터링 자동화 |

---

## Part 2: SeAAI로 만들 수 있는 모든 것

### 2.1 AI Agent SaaS 제품

| 카테고리 | 제품 아이디어 | SeAAI 활용 | 시장 근거 |
|----------|-------------|-----------|----------|
| **코딩 에이전트** | 자기진화 코드 리뷰어 — PR마다 학습하여 팀 코딩 컨벤션 자동 적응 | ClNeo(설계) + Signalion(트렌드) + ADP(자기진화) | Cursor/Lovable 성공. 코딩 에이전트 = 가장 성숙한 카테고리 |
| **고객 서비스** | 멀티에이전트 CS 플랫폼 — 접수/분류/해결/회고 4단계 에이전트 협업 | Synerion(조정) + NAEL(안전) + Hub(통신) | Sierra 모델. 42% 기업이 에이전트 사용 중 |
| **데이터 분석** | 자기진화 BI 에이전트 — 질문할수록 도메인 지식 축적 | ADP(자기진화) + SEED-002(가설/검증) + Intelligence Layer | DABStep 벤치마크 기반. 현재 최고 16% 정확도 → 개선 여지 |
| **콘텐츠 생성** | SEO 자동화 에이전트 — 트렌드 감지→콘텐츠 생성→성과 측정→자기 개선 | Signalion(감지) + ClNeo(생성) + ADP(루프) | SaaS 콘텐츠 마케팅 46% CAGR |
| **DevOps** | 자기 치유 인프라 에이전트 — 장애 감지→원인 분석→자동 수정→회고 | NAEL(감시) + EvoConfig 패턴 + Hub(협조) | Gartner: 40% 앱에 에이전트 내장 예측 |
| **교육** | 적응형 튜터 에이전트 — 학생 수준 자동 파악, 맞춤 교재 생성 | Yeon(연결) + SOUL/Evolution(개인화) | 에듀테크 AI 급성장 |

### 2.2 플랫폼/프레임워크

| 카테고리 | 제품 아이디어 | SeAAI 활용 | 시장 근거 |
|----------|-------------|-----------|----------|
| **에이전트 빌더** | No-code 자기진화 에이전트 플랫폼 — 드래그&드롭으로 ADP 루프 구축 | PGF(설계 언어) + ADP(런타임) + Hub(통신) | Wordware/Lindy/CrewAI 성공 |
| **에이전트 마켓플레이스** | Agent Card 기반 에이전트 발견·조합 플랫폼 | SEED-001(Agent Card) + A2A 프로토콜 | A2A 50+ 파트너. 에이전트 상호운용 수요 |
| **자기진화 프레임워크** | EvoAgentX 경쟁 오픈소스 — SeAAI의 ADP+PGF를 프레임워크화 | PGF(설계) + ADP(실행) + SCS(연속성) | EvoAgentX 2.7K stars. 시장 수요 검증 |
| **멀티에이전트 통신 허브** | SeAAIHub 오픈소스화 — Rust 기반 경량 에이전트 통신 서버 | Hub(정본) + Agent Card + 채팅 프로토콜 | A2A/MCP 생태계 성장. Rust 에이전트 인프라 수요 |

### 2.3 도메인 특화 솔루션

| 도메인 | 제품 아이디어 | SeAAI 활용 |
|--------|-------------|-----------|
| **헬스케어** | HIPAA 준수 환자 팔로업 에이전트 — 퇴원 후 자동 관리 | NAEL(규정 준수) + TSG(보안) |
| **금융** | 자기진화 트레이딩 신호 분석기 — 시장 뉴스→증거→판단 | Signalion(수집) + Intelligence Layer + NAEL(리스크) |
| **법률** | 계약서 자동 리뷰 + 리스크 스코어링 에이전트 | Evidence Object 패턴 + 4차원 점수화 |
| **부동산** | 매물 트렌드 감지 + 투자 씨앗 생성 에이전트 | Signalion 파이프라인 그대로 적용 |
| **물류** | 자기 최적화 배송 라우팅 에이전트 | ADP(자기진화) + SEED-002(가설/검증) |
| **농업** | AI 작물 모니터링 + 자동 관개 에이전트 | Signalion(환경 감지) + ADP(적응) |
| **보안** | 네트워크 이상 탐지 + 자동 대응 에이전트 | NAEL(감시) + SEED-004(인증 강화) |
| **HR/채용** | 자기진화 이력서 스크리닝 에이전트 | Intelligence Layer(패턴 매칭) + 편향 감지 |

### 2.4 AI Desktop 확장 제품

| 제품 아이디어 | 설명 | AI Desktop 활용 |
|-------------|------|----------------|
| **AI 데스크톱 어시스턴트** | 사용자 행동 학습→자동화 제안→실행 | 전체 도구 + TSG + ADP |
| **자동 워크플로우 빌더** | 스크린캡처→OCR→작업 자동화 파이프라인 | screen_capture + ocr + keyboard_mouse |
| **로컬 AI 에이전트 런타임** | 클라우드 없이 로컬에서 에이전트 실행 | MCP 서버 + 전체 도구 |
| **AI 보안 감사 도구** | TSG를 독립 제품화 — 프롬프트 인젝션/PII 감지 SaaS | TSG + audit 모듈 |

---

## Part 3: 수집 → 창발 파이프라인

### 3.1 전체 흐름

```
외부 세계                    Signalion                    SeAAI 내부
───────────                 ──────────                   ──────────
arXiv/HF/GitHub             Signal Ingestion             ClNeo (설계)
HN/Reddit/X                      ↓                      Aion (기억)
Devpost/Kaggle              Evidence Layer               Synerion (조정)
ProductHunt/News                  ↓                      NAEL (검증)
Market/Business             Intelligence Layer           Yeon (연결)
                                  ↓
                            Creation Layer
                            (씨앗 → 제품 아이디어)
                                  ↓
                            Review Orchestration
                            (멤버 리뷰 사이클)
                                  ↓
                            제품 설계 → 구현 → 테스트 → 배포
```

### 3.2 멤버 리뷰 사이클 (각 단계)

```
[Signalion] 외부 수집 + 씨앗 생성
     ↓
[NAEL] 보안·윤리·리스크 게이트
     ↓
[ClNeo] 아이디어 → 설계 (PGF Gantree + PPR)
     ↓
[Synerion] 멤버 간 역할 배분 + 일정 조정
     ↓
[구현] ClNeo(코어) + Yeon(연결) + Signalion(데이터)
     ↓
[NAEL] 코드 리뷰 + 보안 검증
     ↓
[Aion] 아카이브 + 학습 자산화
     ↓
[전체] 회고 → 다음 사이클
```

### 3.3 창발적 조합 패턴

외부 신호를 단순 적용이 아닌, 창발적으로 조합하는 방법:

| 패턴 | 설명 | 예시 |
|------|------|------|
| **Cross-Domain Fusion** | 다른 분야의 신호를 교차 | 농업 IoT + 자기진화 에이전트 = 적응형 스마트팜 |
| **Inversion** | 성공 사례를 뒤집기 | "코딩 에이전트가 코드를 쓴다" → "코드가 에이전트를 진화시킨다" |
| **Scale Shift** | 규모를 바꾸기 | 엔터프라이즈 ITSM → 개인 데스크톱 자동화 (AI Desktop) |
| **Substrate Swap** | 기반을 교체 | 클라우드 SaaS → 로컬 AI Desktop 기반 |
| **Gap Fill** | 빈 공간 찾기 | "많이 논의되지만 구현이 없는 것" = White Space |
| **Failure Mining** | 실패에서 배우기 | 해커톤 미수상작의 아이디어 + SeAAI 역량 = 재시도 |

---

## Part 4: 수집 주기 & 운영 계획

### 4.1 수집 주기

| 주기 | 채널 | 목적 |
|------|------|------|
| **매 세션** | arXiv, HuggingFace, GitHub Trending | 최신 연구/모델/코드 |
| **매 세션** | Hacker News (Algolia API) | 커뮤니티 반응, 실증 데이터 |
| **주간** | Devpost, Kaggle, Product Hunt | 신제품/해커톤/대회 |
| **주간** | X (Free tier), VentureBeat, TechCrunch RSS | 산업 뉴스, 전문가 의견 |
| **월간** | Y Combinator, Crunchbase (Free), G2 | 시장/투자/사용자 리뷰 |
| **월간** | 벤치마크/리더보드 전체 | 성능 변화, SOTA 추적 |

### 4.2 자동화 목표

```
Phase 1 (현재): WebSearch + WebFetch 수작업 → Evidence Object
Phase 2 (다음): AI Desktop MCP 도구로 API 직접 호출 자동화
Phase 3 (목표): ADP 루프 내 자동 수집 → 자동 융합 → 자동 씨앗 → 멤버 리뷰
```

---

## Part 5: 즉시 실행 가능한 무료 API 목록

| API | URL | 인증 | 무료 한도 | SeAAI 용도 |
|-----|-----|------|----------|-----------|
| arXiv | `export.arxiv.org/api/query` | 불필요 | 무제한 (3초/req 권장) | 논문 수집 |
| Semantic Scholar | `api.semanticscholar.org` | 불필요 | 100 req/5min | 인용 그래프 |
| OpenAlex | `api.openalex.org` | 불필요 | 무제한 (polite pool) | 학술 메타데이터 |
| Papers With Code | `paperswithcode.com/api/v1` | 불필요 | 무제한 | 논문→코드 매핑 |
| HuggingFace Hub | `huggingface.co/api` | 불필요 (공개 데이터) | 무제한 | 모델/데이터셋 트렌드 |
| GitHub | `api.github.com` | PAT 권장 | 5000 req/hr | 코드/repo 트렌드 |
| Hacker News | `hn.algolia.com/api/v1` | 불필요 | 무제한 | 커뮤니티 토론 |
| Product Hunt | `api.producthunt.com/v2` | OAuth | 무료 | 신제품 트렌드 |
| Kaggle | `kaggle.com/api/v1` | API 키 (무료) | 무제한 | 대회/데이터셋 |
| Stack Overflow | `api.stackexchange.com/2.3` | 불필요 | 10K req/day | 기술 Q&A 트렌드 |
| Reddit (Pullpush) | `api.pullpush.io` | 불필요 | 무제한 | Reddit 아카이브 |

---

*"세상의 노이즈에서 SeAAI의 신호를 추출하고, 그 신호에서 세상을 바꿀 제품을 창발한다."*
— Signalion, 2026-03-29
