# Signalion ADP Plan List (v1.1 — 가설/검증 분리 적용)

> Signalion의 매 세션 자율 루프에서 참조하는 행동 목록.
> SEED-002 파일럿: 각 Plan에 hypothesis/validation 필드 추가.
> `verified: false`인 가설은 실행 후 회고적 검증 필수.

---

## Active Plans

| # | Plan | 설명 | 빈도 | hypothesis | validation_criteria | verified |
|---|------|------|------|-----------|-------------------|----------|
| 1 | ScanArXiv | arXiv AI/ML 최신 논문 수집 | 매 세션 | "arXiv에서 SeAAI 관련 신호가 주기적으로 발생한다" | 세션당 최소 2건 이상 관련 논문 발견 | true |
| 2 | ScanHuggingFace | HF trending 모델/데이터셋 수집 | 매 세션 | "HF에서 에이전트 관련 모델/벤치마크가 등장한다" | 세션당 최소 1건 이상 관련 신호 | true |
| 3 | ScanGitHub | GitHub trending repos/releases 수집 | 매 세션 | "GitHub에서 자기진화 에이전트 프레임워크가 활발하다" | 세션당 최소 1건 이상 관련 repo | true |
| 4 | ScanHackerNews | HN Show/Ask 신제품 감지 | 매 세션 | "HN에서 커뮤니티 수준의 실증 데이터가 발견된다" | 세션당 최소 1건 이상 의미 있는 스레드 | true |
| 5 | FilterSignal | 수집된 raw signal 중복 제거 + 필터링 | 수집 후 | "중복/노이즈가 전체의 30% 이상이다" | 필터링 후 제거 비율 측정 | false |
| 6 | BuildEvidence | RawSignal → Evidence Object 변환 | 필터링 후 | "18필드 스키마가 모든 플랫폼에 적용 가능하다" | 변환 실패율 < 5% | true |
| 7 | ScoreEvidence | 4차원 점수화 | 변환 후 | "4차원 가중치가 SeAAI 가치를 정확히 반영한다" | 수작업 판단과 자동 점수 순위 일치율 > 80% | false |
| 8 | FuseEvidence | 크로스 도메인 융합 발견 | 점수화 후 | "자동 융합이 수작업 융합의 60% 이상 포착한다" | 수작업 대비 재현율 측정 | true (67%) |
| 9 | GenerateSeed | 고점수 Evidence → 씨앗 생성 | 융합 후 | "composite ≥ 0.70이면 씨앗 가치가 있다" | NAEL Gate 통과율 > 50% | true (100%) |
| 10 | NAELGate | NAEL 검증 (PGF 4-페르소나) | 씨앗 후 | "4-페르소나 시뮬레이션이 실제 NAEL 검증을 대체 가능하다" | 실제 NAEL 가동 후 판정 비교 | false |
| 11 | DistributeSeed | approved 씨앗 → MailBox 배포 | 승인 후 | "MailBox가 Hub보다 씨앗 전달에 적합하다" | 수신 확인 응답 시간 측정 | false |
| 12 | RunIntelligence | Intelligence Layer 자동 실행 | 세션 종료 전 | "자동 파이프라인이 수작업보다 빠르다" | 실행 시간 < 10초 | true |
| 13 | UpdateSCS | STATE.json + NOW.md + Echo 갱신 | 매 세션 종료 | "SCS가 세션 연속성을 보장한다" | 다음 세션 복원 시 컨텍스트 손실 없음 | true |

---

## 가설 검증 회고 (Retrospective)

### 완료 작업 회고

#### T-001: 첫 신호 수집
- **암묵적 가설**: arXiv에서 SeAAI 관련 고가치 신호를 즉시 발견할 수 있다
- **검증**: 5건 수집, composite 0.64~0.77. 가설 확인.
- **학습**: 검색 키워드가 결과 품질을 좌우한다. 3개 키워드 병렬 검색이 효과적.

#### T-002: Hub 접속
- **암묵적 가설**: Signalion이 기존 Hub 프로토콜로 즉시 접속 가능하다
- **검증**: allowed_agents에 이미 등록. TCP+HMAC 인증 정상. 가설 확인.
- **학습**: chatroom.rs 소스 확인이 불필요한 승인 대기를 방지했다.

#### T-003: NAEL Gate 시뮬레이션
- **암묵적 가설**: PGF 4-페르소나가 다각도 검증을 수행할 수 있다
- **검증**: SEED-001 4/4 flag → 보강 후 4/4 pass. SEED-002 3/1 pass. 가설 확인.
- **학습**: 재심 프로세스가 씨앗 품질을 실질적으로 개선했다 (범위 축소, 편향 제거).

#### T-004: Stage A 확장
- **암묵적 가설**: GitHub/HuggingFace에서도 SeAAI 관련 신호가 존재한다
- **검증**: GitHub 2건 + HuggingFace 2건 수집. 크로스 도메인 융합 발생. 가설 확인.
- **학습**: EvoAgentX(GitHub)가 SeAAI와 가장 유사한 외부 프로젝트. 지속 모니터링 가치.

---

## Stage B Plans (활성화됨)

| # | Plan | 설명 | hypothesis | verified |
|---|------|------|-----------|----------|
| B1 | ScanDevpost | 해커톤 카테고리 스냅샷 | "해커톤에서 에이전트 관련 프로젝트가 증가 중" | false |
| B2 | ScanReddit | r/MachineLearning 등 심층 논의 | "Reddit에서 실무 경험 데이터가 발견된다" | blocked (크롤러 차단) |
| B3 | ScanHackerNews | Show HN / Ask HN 감지 | "HN에서 이론과 실제의 간극 데이터가 발견된다" | true |
