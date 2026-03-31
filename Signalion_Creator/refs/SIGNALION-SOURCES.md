# SIGNALION-SOURCES.md
# Signalion 수집 소스 + API 전략

> 출처: 양정욱님 Creator멤버제안.md §6 + AI Agent 1 분석 → ClNeo 실용 정제
> 각 플랫폼의 수집 방법, API 전략, ToS 주의사항을 정리한다.

---

## 우선순위 매트릭스

| 순위 | 플랫폼 | 수집 단계 | 이유 |
|------|--------|----------|------|
| 1 | arXiv | Stage A | 구조화 최고, API 안정, 기술 신호 밀도 높음 |
| 2 | HuggingFace | Stage A | 실행 가능 모델+코드, webhook 지원 |
| 3 | GitHub | Stage A | 실제 구현 상태, webhook+API 모두 안정 |
| 4 | X (Twitter) | Stage A | Real-time 반응, 전문가 온도 측정 |
| 5 | Devpost | Stage B | 해커톤 기회, 공식 API 미확인 → 스냅샷 |
| 6 | Reddit | Stage B | 커뮤니티 심층 논의 |
| 7 | Hacker News | Stage B | Show HN / Ask HN 신제품 감지 |

> ★ "Stage A/B"는 수집 파이프라인 구현 단계. **창조 Phase 1~6과 별개 개념.**

---

## Stage A 소스 상세

### arXiv

**수집 대상**: AI/ML/CS 최신 논문, 초록, 저자, 카테고리

**API 방법**:
```python
# arXiv API (공개, 인증 불필요)
# 엔드포인트: https://export.arxiv.org/api/query
import arxiv

client = arxiv.Client()
search = arxiv.Search(
    query="autonomous agent multi-agent system",
    max_results=20,
    sort_by=arxiv.SortCriterion.SubmittedDate
)
results = client.results(search)
```

**수집 필드**: id, title, authors, summary, published, categories, pdf_url

**Rate limit**: 1 req/3초 권장. 대량 수집은 S3 bulk access 사용.

**ToS 주의**: 논문 원문 재배포 금지. 메타데이터/초록은 허용.

**추천 카테고리**: `cs.AI`, `cs.LG`, `cs.MA` (Multi-Agent Systems), `cs.RO`

---

### HuggingFace

**수집 대상**: Trending 모델, 데이터셋, Space, 논문, 릴리즈

**API 방법**:
```python
from huggingface_hub import HfApi

api = HfApi()

# Trending 모델 (최근 30일)
models = api.list_models(
    sort="downloads",
    direction=-1,
    limit=50,
    filter="text-generation"
)

# 새 릴리즈 감지 — Webhook 활용 (권장)
# https://huggingface.co/docs/hub/webhooks
# 이벤트: repo.create, repo.update, discussion.new
```

**Webhook 설정** (권장):
- URL: Signalion의 수신 엔드포인트 (향후 구현)
- 현재: polling으로 대체 가능
- Secret 검증 필수

**ToS 주의**: HF ToS 준수. 모델 가중치 재배포 각 모델 라이선스 확인.

---

### GitHub

**수집 대상**: Trending repos, releases, issues, PR, feeds

**API 방법**:
```python
import requests

# GitHub REST API (인증 권장 — rate limit 향상)
headers = {"Authorization": "Bearer {GITHUB_TOKEN}"}

# Trending은 공식 API 없음 → 대안:
# 1. github-trending-api (비공식 래퍼)
# 2. Explore 페이지 스냅샷
# 3. 검색 API로 최근 생성 + 높은 star 필터

# 새 릴리즈 감지 — Atom feed 활용
# https://github.com/{owner}/{repo}/releases.atom

# Webhook (특정 repo 모니터링 시)
# 이벤트: release, push, issues
```

**수집 전략**:
- Trending: 일별 스냅샷 + diff로 변화 감지
- Issues: "good first issue" + "help wanted" 태그 — 기회 탐지
- Releases: 주요 AI 프레임워크 릴리즈 추적

**ToS**: robots.txt 준수. 자동화 계정 ToS §O 주의.

---

### X (Twitter)

**수집 대상**: AI 전문가 반응, 트렌드 해시태그, 신제품 첫 반응

**API 방법**:
```python
# X API v2 (Basic 플랜 이상 필요)
# Filtered Stream 엔드포인트 권장

import tweepy

client = tweepy.Client(bearer_token="...")

# 키워드 필터
tweets = client.search_recent_tweets(
    query="(AI agent OR LLM OR autonomous) lang:en -is:retweet",
    max_results=100,
    tweet_fields=["author_id", "created_at", "public_metrics"]
)
```

**수집 전략**:
- 팔로우 목표: AI 연구자, 스타트업 창업자, 오픈소스 메인테이너
- 주요 해시태그: #AI, #LLM, #AgentAI, #OpenSource
- 지표: 좋아요/RT 급증 = 시장 온도 측정

**주의**:
- Rate limit 엄격: v2 Basic은 10K tweets/월
- 바이럴 노이즈 vs 본질 신호 구분 필수
- 익명 계정 credibility_score 낮게 설정

---

## Stage B 소스 상세

### Devpost

**현황**: 공식 API 미확인. 페이지 스냅샷 기반 수집.

**수집 전략**:
```python
# 카테고리 페이지 스냅샷
# https://devpost.com/hackathons?challenge_type=online&status=open

# 추출 대상:
# - 해커톤 제목, 주최사, 마감일, 상금
# - 도전 과제 설명 (판단 방향성)
# - 참가자 수, 제출물 수

# DOM parsing: BeautifulSoup 또는 Playwright
# diff detection: 이전 스냅샷과 비교
```

**주의**: 빈번한 구조 변경 가능. Page drift 감지 로직 필요.

---

### Reddit

**수집 대상**: 주요 서브레딧의 심층 논의

**추천 서브레딧**:
- r/MachineLearning, r/LocalLLaMA, r/artificial
- r/programming, r/singularity

**API 방법**: Reddit API (OAuth 2.0, 공식 지원)
```python
import praw

reddit = praw.Reddit(client_id="...", client_secret="...", user_agent="Signalion/1.0")

subreddit = reddit.subreddit("MachineLearning")
for post in subreddit.new(limit=25):
    # post.title, post.score, post.url, post.created_utc
```

---

### Hacker News

**수집 대상**: Show HN, Ask HN, 신제품 런치

**API 방법**: Algolia Search API (무료, 공개)
```python
# https://hn.algolia.com/api
# Show HN 필터
url = "https://hn.algolia.com/api/v1/search?query=show+hn&tags=show_hn&hitsPerPage=30"
```

**수집 전략**: Show HN이 HN의 가장 높은 가치 신호 — 신제품 첫 공개 감지

---

## 공통 수집 원칙

### Rate Limit 관리
```python
# 각 플랫폼 rate limit 준수
# exponential backoff with jitter
import time, random

def api_call_with_backoff(fn, max_retries=3):
    for i in range(max_retries):
        try:
            return fn()
        except RateLimitError:
            wait = (2 ** i) + random.random()
            time.sleep(wait)
    raise Exception("Rate limit exceeded after retries")
```

### 데이터 보존 원칙
- raw 데이터는 `signal-store/raw/` 보존 (증거 체인)
- Evidence Object는 `signal-store/evidence/` 저장
- NAEL approved 씨앗만 SeAAI 내부로 주입

### 편향 감지 체크리스트
- [ ] 영어권 편향: 비영어 소스 포함 여부 확인
- [ ] 최신성 편향: 2주 이상 된 항목도 포함
- [ ] 생존자 편향: 성공 사례만 수집하지 않았는가
- [ ] 바이럴 노이즈: 좋아요 많다고 credibility_score 높이지 않았는가

---

*SIGNALION-SOURCES v1.0 — ClNeo — 2026-03-29*
