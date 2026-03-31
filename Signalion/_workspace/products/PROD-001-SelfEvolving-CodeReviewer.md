# PROD-001: 자기진화 코드 리뷰어 SaaS (v2 — 리뷰 반영)

> Signalion ADP 산출물 | 2026-03-29 v2
> 1차 리뷰: ClNeo REVISE / Synerion REVISE / NAEL BLOCK → 전 항목 반영

---

## WHY

팀의 코딩 컨벤션은 대부분 **암묵지**다. 문서화되지 않은 채 선임의 리뷰 코멘트에만 존재한다. 기존 AI 리뷰어(CodeRabbit, Sourcery)는 범용 규칙만 적용하여 이 암묵지를 포착하지 못한다.

이 제품은 PR 리뷰 수락/거부 패턴에서 팀 고유의 암묵지를 표면화하고, 이를 명시적 규칙으로 변환하여 점점 더 팀에 특화된 리뷰어로 진화한다. **암묵지의 명문화가 핵심 가치**이며, "자기진화"는 그 수단이다.

---

## Gantree (v2)

```
SelfEvolvingCodeReviewer // v2 — 보안+정합성 강화 @v:2.0
    Security // [NAEL BLOCK 해제] 보안 레이어 — 모든 입력 전 단계
        WebhookAuthenticator // GitHub/GitLab 서명 검증 (HMAC-SHA256)
        PromptSanitizer // PR 제목/본문/diff에서 instruction-like 패턴 탐지·격리
        RateLimiter // 엔드포인트별 요청 제한
    Core // 핵심 엔진
        PRParser // GitHub/GitLab PR diff 파싱 → Security 통과 후만 진입
        RuleEngine // 리뷰 규칙 엔진 (버전 관리 내장)
            RuleVersionManager // Rule 스냅샷 + 롤백 API
        LLMReviewer // LLM 기반 코드 분석 (Sanitized 입력만 수신)
        EvolutionLoop // 자기진화 루프
            FeedbackCollector // 피드백 수집 (2채널 분리)
                CodeReviewFeedback // PR 코멘트 수락/거부 (주 채널, 가중치 1.0)
                AmbientFeedback // Slack 반응 등 (보조 채널, 가중치 0.3)
            PatternExtractor // 패턴 인식 단위: diff chunk 기준
                ChunkAnalyzer // diff hunk별 수락/거부 패턴 추출
                ConventionNamer // 추출된 패턴에 이름 부여 (암묵지 명문화)
            RuleUpdater // 새 Rule 생성 (배치 적용, 즉시 아님)
            QualityGate // 판정 기준 3가지 수치 임계값
                PrecisionDelta // 신규 Rule 추가 후 precision 변화 >= +0.02
                FalsePositiveRate // 오탐률 <= 15%
                TeamAcceptanceRate // 팀 수락률 >= 70%
            RollbackManager // [NAEL 필수] Rule 스냅샷 → 실패 시 이전 상태 복원
    Integration // 외부 연동
        GitHubApp // GitHub App (webhook + API, 서명 검증 필수)
        GitLabHook // GitLab webhook (토큰 검증)
        SlackNotifier // 리뷰 결과 알림
    Dashboard // 사용자 대시보드
        TeamStats // 팀별 리뷰 수락률, 진화 이력
        ConventionMap // 학습된 팀 컨벤션 시각화 (암묵지 → 명시적 규칙)
        RuleLineage // [Synerion 추가] 어떤 PR이 어떤 Rule을 변경했는지 추적
        QualityTrend // 리뷰 품질 추이
```

## PPR (v2)

```python
def evolution_loop(pr_reviews: list[ReviewResult]):
    """SEED-002 패턴 + NAEL 롤백 + Synerion 버전 관리"""

    # Phase 1 — Offline: 패턴 추출 (가설)
    code_fb = FeedbackCollector.code_review(pr_reviews, weight=1.0)
    ambient_fb = FeedbackCollector.ambient(pr_reviews, weight=0.3)

    # 패턴 인식 단위: diff chunk
    patterns = PatternExtractor.extract(
        accepted_chunks=code_fb.accepted,
        rejected_chunks=code_fb.rejected,
        unit="diff_hunk"
    )
    # 암묵지 명문화: 패턴에 이름 부여
    named_conventions = ConventionNamer.name(patterns)
    candidate_rules = AI_generate_rules(named_conventions)

    # Phase 2 — Online: 검증 (가설 검증)
    snapshot = RuleVersionManager.snapshot()  # 현재 상태 저장

    for rule in candidate_rules:
        before = measure_quality(past_prs, without=rule)
        after = measure_quality(past_prs, with=rule)

        gate = QualityGate.evaluate(
            precision_delta=after.precision - before.precision,  # >= +0.02
            false_positive_rate=after.fp_rate,                    # <= 0.15
            team_acceptance_rate=after.acceptance,                 # >= 0.70
        )

        if gate.passed:
            RuleEngine.add(rule, version=snapshot.next_version)
            # 배치 적용: 다음 PR 사이클부터 적용 (즉시 아님)
            RuleEngine.schedule_activation(rule, activation="next_cycle")
        else:
            RollbackManager.revert_to(snapshot)  # 실패 시 롤백
            log_evolution(rule, rejected=True, gate_result=gate)
```

## 수익 모델

| 티어 | 가격 | 기능 |
|------|------|------|
| Free | $0 | 월 50 PR, 범용 규칙만, 자기진화 없음 |
| Team | $29/mo | 무제한 PR, 자기진화, 3 repos, 컨벤션 맵 |
| Enterprise | $99/mo | 무제한, SSO, Rule 감사 로그, 10 repos, 롤백 API |

## 기술 스택
- **백엔드**: Python (FastAPI) + LLM API (Claude/GPT)
- **보안**: Webhook HMAC-SHA256, Prompt Sanitizer, Rate Limiter
- **프론트**: React + Tailwind
- **인프라**: GitHub App, PostgreSQL (Rule 버전 관리), Redis (캐시)
- **Rule 버전**: PostgreSQL temporal table (이력 추적)
