# PROD-003: AI 트렌드 인텔리전스 플랫폼 (v2 — 리뷰 반영)

> Signalion ADP 산출물 | 2026-03-29 v2
> 1차 리뷰: ClNeo REVISE / Synerion REVISE / NAEL BLOCK → 전 항목 반영

---

## WHY

단일 플랫폼 모니터링으로는 발견할 수 없는 것이 있다.

**예시**: arXiv에서 "self-evolving agent"가 급증하는데, GitHub에서는 관련 구현이 없다 — 이것은 **논문-구현 괴리(Paper-Implementation Gap)**이며, 빠르게 구현하면 선점 기회다. 반대로 GitHub에서 급성장하는 repo가 arXiv에 논문이 없다면 — 이것은 **학술 공백(Academic White Space)**이며, 논문화하면 학술 기여다.

이런 크로스 도메인 인사이트는 단일 플랫폼 도구(Semantic Scholar, Papers With Code, AlphaSignal)로는 불가능하다. **융합에서만 나오는 고유 인사이트 유형이 이 제품의 존재 이유다.**

---

## 크로스 도메인 융합 인사이트 유형 (ClNeo 추가)

| 유형 | 정의 | 예시 |
|------|------|------|
| Paper-Implementation Gap | arXiv 급증 + GitHub 부재 | 선점 구현 기회 |
| Academic White Space | GitHub 급증 + arXiv 부재 | 논문화 기회 |
| Hype-Reality Divergence | HN/X 과열 + 벤치마크 부진 | 거품 경고 |
| Silent Convergence | 다플랫폼 독립 등장 + 동일 패턴 | 트렌드 초기 신호 |
| Failure Pattern | Devpost 해커톤 반복 실패 | 해결 필요 난제 |

---

## Gantree (v2)

```
TrendIntelligencePlatform // v2 — 입력 검증 + 인터페이스 계약 @v:2.0
    Security // [NAEL BLOCK 해제] 입력 보안
        InputValidator // 채널별 화이트리스트 + 크기 상한 + 인젝션 탐지
            ChannelWhitelist // 채널별 허용 필드 목록
            SizeGuard // 단일 신호 최대 크기 제한 (10KB)
            InjectionFilter // instruction-like 패턴 탐지·격리
        APIAuthenticator // Webhook/SlackBot/REST 인증 (API Key + Rate Limit)
        WeightAuditLog // [NAEL 필수] 자기진화 가중치 변경 불변 로그
            AnomalyDetector // 단기 급격한 가중치 변화 탐지
            RollbackTrigger // 이상 탐지 시 이전 가중치로 자동 롤백
    Ingestion // 다채널 수집 (Security 통과 후)
        ArxivConnector // arXiv API (무료)
        HuggingFaceConnector // HF Hub API
        GitHubConnector // GitHub Trending + Release
        HackerNewsConnector // Algolia API
        ProductHuntConnector // 신제품 추적
        CustomRSSConnector // 사용자 정의 RSS
        URLDeduplicator // [Synerion 이전] URL 해시 기반 조기 중복 제거
    EvidenceEngine // 구조화 + 점수화
        Transformer // Raw → EvidenceObject (18필드)
        Scorer // 4차원 점수화
        SemanticDeduplicator // [Synerion 분리] 의미적 중복 제거 (Ingestion과 분리)
    IntelligenceEngine // 패턴 + 융합
        TagClusterer // 태그 클러스터링
        SemanticMatcher // 동의어 맵 + TF 코사인 (v2)
        PatternDetector // 3+ Evidence 공유 = 트렌드
        CrossDomainFuser // 크로스 도메인 융합 → 5가지 인사이트 유형 생성
        WhiteSpaceDetector // 기회 탐지
    SelfEvolution // 자기진화 (보안 강화)
        ActionBasedFeedback // [ClNeo 교체] engagement → 행동 기반 신호
            BookmarkSignal // 북마크 = "가치 있음"
            ShareSignal // 공유 = "전파할 가치"
            WatchlistSignal // 워치리스트 추가 = "지속 추적 가치"
        WeightAdjuster // 행동 신호 기반 가중치 조정 (배치, 비실시간)
        AuditTrail // 모든 조정을 WeightAuditLog에 기록
    Dashboard // 사용자 인터페이스
        TrendMap // 실시간 트렌드 맵 (노드 그래프)
        FusionAlerts // 5가지 융합 인사이트 유형별 알림
        WhiteSpaceBoard // 기회 탐지 보드
        WeeklyDigest // 주간 리포트 자동 생성
        CustomWatchlist // 관심 키워드 모니터링
    API // 외부 연동 (인증 필수)
        RESTApi // JSON API (API Key + Rate Limit)
        WebhookPush // 신규 트렌드 푸시 (서명 검증)
        SlackBot // Slack 연동 (OAuth)
    DataFlowContract // [Synerion 추가] 인터페이스 명세
        RawSignalSchema // Ingestion → EvidenceEngine: {url, title, body, platform, collected_at}
        EvidenceObjectSchema // EvidenceEngine → IntelligenceEngine: 18필드 Evidence Object
        InsightSchema // IntelligenceEngine → Dashboard: {type, evidence_ids[], shared_tags[], score, insight_text}
```

## 수익 모델

| 티어 | 가격 | 기능 |
|------|------|------|
| Free | $0 | arXiv + GitHub 2채널, 일 10건, 주간 다이제스트 |
| Researcher | $19/mo | 5채널, 무제한, 실시간 알림, API (1000 req/day) |
| Team | $49/mo | 전채널, 팀 대시보드, 워치리스트 10개, 융합 인사이트 |
| Enterprise | $149/mo | 전용 인스턴스, SSO, 화이트 라벨, 웹훅, 무제한 API |

## 기술 스택
- **수집**: Python asyncio + InputValidator (보안 게이트)
- **Intelligence**: signalion-intelligence.py v2 코어
- **보안**: API Key, Rate Limit, WeightAuditLog, InjectionFilter
- **백엔드**: FastAPI + PostgreSQL + Redis
- **프론트**: Next.js + D3.js
