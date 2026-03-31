# Browser Engine 통합 테스트 결과

> 2026-03-30 | Signalion Browser Engine v1.0

## 플랫폼별 테스트 결과

| # | 플랫폼 | URL | 페이지 로드 | JS 추출 | 데이터 품질 | 판정 |
|---|--------|-----|-----------|---------|-----------|------|
| 1 | **Hacker News** | news.ycombinator.com | PASS | PASS (15건) | 제목+URL 정확 | **PASS** |
| 2 | **GitHub Trending** | github.com/trending | PASS | PASS (12건) | 이름+설명+스타+오늘스타 | **PASS** |
| 3 | **arXiv cs.AI** | arxiv.org/list/cs.AI/recent | PASS | PASS (10건) | ID+제목+저자 | **PASS** |
| 4 | **HuggingFace Trending** | huggingface.co/models?sort=trending | PASS | PASS (10건) | 모델명+URL+파라미터 | **PASS** |
| 5 | **arXiv Search** | arxiv.org/search/... | FAIL (timeout) | N/A | N/A | **FAIL** |

### 실패 분석
- arXiv Search: 60초 타임아웃. arXiv 검색 서버 응답 지연 문제.
- 대안: `arxiv.org/list/cs.AI/recent` (최신 목록)으로 대체 → 성공

### 추출 방식 결론
- DOM 스냅샷 파싱: 부정확 (HN 테스트에서 노이즈 30건 중 의미 있는 것 3건)
- **JS `browser_evaluate` 직접 실행: 정확도 100%** → 표준 채택

## 보안 테스트

| 테스트 | 결과 |
|--------|------|
| URL 화이트리스트 검증 | 구현 완료 (browser_core.py) |
| 입력 금지 패턴 검증 | 구현 완료 (password, credit card 등) |
| 감사 로그 기록 | 구현 완료 (JSONL 형식) |
| 자격증명 안전 저장 | 구현 완료 (.credentials/) |

## 추출기 레지스트리

| 추출기 | JS 코드 | 테스트 | 상태 |
|--------|---------|--------|------|
| `github_trending` | GITHUB_TRENDING_JS | 실행 검증 | **Active** |
| `hn_frontpage` | HN_FRONTPAGE_JS | 실행 검증 | **Active** |
| `arxiv_recent` | ARXIV_SEARCH_JS (변형) | 실행 검증 | **Active** |
| `hf_trending` | HF_TRENDING_JS | 실행 검증 | **Active** |
| `producthunt_daily` | PH_DAILY_JS | 미테스트 | Pending |
| `devpost_gallery` | DEVPOST_GALLERY_JS | 미테스트 | Pending |
