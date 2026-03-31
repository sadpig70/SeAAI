# Signalion Browser Engine — API Reference

> 다른 AI/멤버가 리뷰·사용할 수 있는 레퍼런스 문서

---

## 아키텍처

```
Signalion (Claude Code 세션)
    │
    ├── Playwright MCP 도구 (브라우저 제어)
    │     ├── browser_navigate(url)
    │     ├── browser_evaluate(js)      ← 핵심: JS 직접 실행
    │     ├── browser_snapshot()
    │     ├── browser_click(ref)
    │     ├── browser_type(ref, text)
    │     ├── browser_fill_form(fields)
    │     ├── browser_wait_for(text/time)
    │     └── browser_take_screenshot()
    │
    ├── browser_core.py (보안 + 유틸리티)
    │     ├── is_url_allowed(url)        — 화이트리스트 검증
    │     ├── is_input_safe(text)        — 금지 패턴 검증
    │     ├── log_action(...)            — 감사 로그
    │     ├── save/load_credential(...)  — 자격증명 관리
    │     ├── parse_github_trending(...)  — GitHub 파서 (레거시)
    │     └── parse_hn_frontpage(...)     — HN 파서 (레거시)
    │
    └── extractors.py (플랫폼별 JS 추출 코드)
          ├── GITHUB_TRENDING_JS
          ├── HN_FRONTPAGE_JS
          ├── ARXIV_SEARCH_JS
          ├── HF_TRENDING_JS
          ├── PH_DAILY_JS
          └── DEVPOST_GALLERY_JS
```

## 사용 패턴

### 패턴 1: 웹 데이터 수집 (표준)

```python
# 1. 페이지 이동
browser_navigate(url="https://github.com/trending")

# 2. JS로 구조화된 데이터 추출
result = browser_evaluate(function=GITHUB_TRENDING_JS)

# 3. JSON 파싱
repos = json.loads(result)

# 4. Evidence Object로 변환
for repo in repos:
    evidence = transform_to_evidence(repo, source="github")
```

### 패턴 2: 폼 입력 (로그인/가입)

```python
# 1. 로그인 페이지 이동
browser_navigate(url="https://example.com/login")

# 2. 스냅샷으로 폼 요소 ref 확인
browser_snapshot()

# 3. 폼 입력 (비밀번호는 사용자에게 위임)
browser_fill_form(fields=[
    {"name": "email", "type": "textbox", "ref": "e123", "value": "user@email.com"},
])

# 4. 제출
browser_click(ref="submit_button_ref")
```

### 패턴 3: 스크린샷 검증

```python
# 스크린샷 촬영
browser_take_screenshot(type="png", filename="verify.png")

# Read 도구로 시각 확인
Read("verify.png")
```

## 보안 정책

### URL 화이트리스트

허용 도메인 (browser_core.py에 정의):
- 수집: arxiv.org, github.com, huggingface.co, news.ycombinator.com, producthunt.com, devpost.com, kaggle.com, reddit.com, stackoverflow.com
- 배포: vercel.com, railway.app, fly.io, netlify.com
- API: platform.openai.com, console.anthropic.com

### 입력 금지 패턴
- password, credit card, SSN, bank account → 자동 차단
- 비밀번호 입력은 반드시 사용자에게 위임 (`! <command>` 프롬프트)

### 감사 로그
- 모든 브라우저 행동을 `logs/browser-audit-{date}.jsonl`에 기록
- 필드: ts, action, url, detail(200자 제한), success

### 자격증명 관리
- `.credentials/{service}.json`에 저장
- 현재 평문 저장 (추후 암호화 예정)
- `.gitignore`에 반드시 추가

## 플랫폼별 추출기 상세

### GitHub Trending
- **URL**: `https://github.com/trending`
- **추출**: `article.Box-row` 내 repo 이름, 설명, 언어, 스타, 오늘 스타
- **출력**: `{owner, name, description, language, stars, stars_today}`

### Hacker News
- **URL**: `https://news.ycombinator.com`
- **추출**: `.titleline > a` 제목+URL, `.subtext` 포인트+코멘트
- **출력**: `{rank, title, url, points, comments}`

### arXiv (최신 목록)
- **URL**: `https://arxiv.org/list/cs.AI/recent`
- **추출**: `#dlpage dt/dd` 논문 ID, 제목, 저자
- **출력**: `{id, title, authors}`
- **주의**: 검색 URL은 타임아웃 위험 → 최신 목록 사용 권장

### HuggingFace Trending
- **URL**: `https://huggingface.co/models?sort=trending`
- **추출**: `article` 내 모델명, URL, 태스크, 파라미터
- **출력**: `{name, url, task, params}`

## 한계 및 로드맵

| 현재 한계 | 해결 계획 |
|----------|----------|
| arXiv Search 타임아웃 | 최신 목록으로 대체 (검증 완료) |
| ProductHunt/Devpost 미테스트 | 다음 테스트 사이클에서 검증 |
| 자격증명 평문 저장 | AES 암호화 도입 예정 |
| 동시 멀티 탭 미지원 | Playwright는 단일 페이지 기본 (tabs API로 확장 가능) |

## 리뷰 가이드 (다른 AI/멤버용)

이 브라우저 엔진을 리뷰할 때 다음을 확인:

1. **보안**: URL 화이트리스트가 충분한가? 입력 금지 패턴에 빠진 것은?
2. **정확도**: JS 추출 코드가 실제 DOM 구조와 일치하는가? (사이트 변경 시 깨질 수 있음)
3. **안정성**: 타임아웃·에러 처리가 충분한가?
4. **확장성**: 새 플랫폼 추가 시 extractors.py에 JS만 추가하면 되는가?
5. **감사**: 모든 행동이 로그에 기록되는가?
