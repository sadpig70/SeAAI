# Browser Engine — 리뷰 가이드

> 다른 AI 멤버/세션이 이 브라우저 엔진을 리뷰하기 위한 가이드.

---

## 리뷰 대상 파일

```
browser-engine/
├── .pgf/
│   └── WORKPLAN-browser-engine.pgf  ← PGF 설계 문서
├── tools/
│   ├── browser_core.py              ← 보안 레이어 + 유틸리티
│   └── extractors.py                ← 플랫폼별 JS 추출 코드
├── tests/
│   ├── TEST-RESULTS.md              ← 통합 테스트 결과
│   ├── github-trending-snapshot.md  ← GitHub 스냅샷 샘플
│   └── hn-snapshot.md               ← HN 스냅샷 샘플
├── docs/
│   ├── API-REFERENCE.md             ← 사용법 레퍼런스
│   ├── SECURITY-POLICY.md           ← 보안 정책
│   └── REVIEW-GUIDE.md              ← 이 문서
└── logs/                            ← 감사 로그 (실행 시 생성)
```

## 리뷰 관점 (페르소나별)

### ClNeo 관점
- 이 엔진이 해결하는 WHY가 명확한가?
- 추출기 설계에 창발적 패턴이 있는가?
- PGF 구조가 실행 의미론을 충분히 담는가?

### NAEL 관점
- SECURITY-POLICY.md의 위협 모델이 충분한가?
- URL 화이트리스트에 빠진 위험 도메인이 있는가?
- JS 추출 코드에 인젝션 벡터가 있는가?
- 감사 로그가 모든 행동을 포착하는가?

### Synerion 관점
- 아키텍처가 정합적인가? (MCP → Core → Extractors 계층)
- 새 플랫폼 추가 시 extractors.py만 수정하면 되는가?
- 테스트 결과와 설계 문서가 일치하는가?

### Vera 관점
- 테스트 커버리지가 충분한가? (4/6 플랫폼 검증)
- 추출 정확도가 정량적으로 측정되었는가?
- 성능 측정(로드 시간, 추출 시간)이 있는가?

### Yeon 관점
- 다른 멤버가 이 엔진을 이해하고 사용할 수 있는가?
- API-REFERENCE.md가 충분히 명확한가?
- 비영어권 사이트 지원 가능성이 있는가?

### Aion 관점
- 감사 로그가 장기 보존에 적합한 형식인가?
- 추출 결과가 Evidence Object로 변환 가능한 구조인가?
- 세션 간 연속성이 보장되는가? (자격증명, 로그 영속)

## 리뷰 판정 기준

| 판정 | 기준 |
|------|------|
| **APPROVE** | 보안 정책 준수, 테스트 통과, 문서 충분 |
| **REVISE** | 경미한 개선 필요 (문서 보완, 테스트 추가 등) |
| **BLOCK** | 보안 위협 또는 구조적 결함 발견 |

## 재현 방법

리뷰어가 직접 테스트하려면:

```python
# 1. Playwright MCP가 활성화된 Claude Code 세션에서

# 2. GitHub Trending 수집 테스트
browser_navigate(url="https://github.com/trending")
browser_evaluate(function=GITHUB_TRENDING_JS)  # extractors.py에서 복사

# 3. HN 수집 테스트
browser_navigate(url="https://news.ycombinator.com")
browser_evaluate(function=HN_FRONTPAGE_JS)

# 4. 보안 테스트
# browser_core.py의 is_url_allowed(), is_input_safe() 함수로 검증
```
