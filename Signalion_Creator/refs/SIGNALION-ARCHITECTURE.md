# SIGNALION-ARCHITECTURE.md
# Signalion 시스템 아키텍처 — ClNeo 정교화

> 원안: 양정욱님 Signalion 제안 §Architecture Gantree
> 정제: ClNeo — PGF 설계 원칙 적용 + SeAAI 연동 명세 추가

---

## 전체 구조 (5 서브시스템)

```
Signalion_System  // 외부 신호 → SeAAI 씨앗 파이프라인
    Source_Ingest       // 1. 원시 신호 수집
    Evidence_Layer      // 2. 신호 → Evidence Object 변환
    Intelligence_Layer  // 3. Evidence → 인텔리전스 (패턴, 융합)
    Creation_Layer      // 4. 인텔리전스 → 창발적 씨앗
    Review_Orchestration // 5. NAEL 게이트 + SeAAI 배포
```

---

## Source_Ingest — 원시 신호 수집

```
Source_Ingest  // 플랫폼별 수집 전략
    @output: RawSignal[]

    PrimaryChannels  // Stage A (즉시 구현 — arXiv/HF/GitHub/X)
        // ★ "Stage A/B"는 수집 단계 구분. 창조 Phase 1~6과 별개.
        [parallel]
        ScanArXiv       // arXiv API — 논문, 초록, 저자, 카테고리
        ScanHuggingFace // HF API — trending models, datasets, papers
        ScanGitHub      // GitHub API — trending repos, releases, issues
        ScanXCom        // X Filtered Stream — 전문가 반응, 해시태그

    SecondaryChannels  // Stage B (Stage A 안정화 후)
        // ★ Stage A 수집 파이프라인이 안정화된 후 단계적 추가
        ScanDevpost     // 해커톤 카테고리 페이지 스냅샷
        ScanReddit      // r/MachineLearning, r/LocalLLaMA 등
        ScanHackerNews  // Show HN / Ask HN / launches 트래킹

    CollectionRules
        // 필수 준수:
        //   각 플랫폼 ToS + robots.txt 준수
        //   rate limit: API 가이드라인 엄수
        //   webhook 사용 시 HTTPS + secret 검증
        //   수집 데이터 재배포 가능 여부 확인 후 저장
        //
        // 저장 위치: D:/SeAAI/Signalion/signal-store/raw/{platform}/{날짜}/
```

---

## Evidence Object Schema

**이것이 Signalion의 핵심 변환 단위다.**
단순 크롤링 데이터가 아닌, SeAAI가 즉시 활용할 수 있는 구조화된 증거.

```json
{
  "id":                "SIG-{YYYYMMDD}-{platform}-{seq}",
  "source":            "arxiv | huggingface | github | x | devpost | reddit | hn",
  "url":               "https://...",
  "title":             "원본 제목",
  "authors":           ["저자1", "저자2"],
  "published_at":      "ISO 날짜",
  "collected_at":      "ISO 날짜시간",
  "tags":              ["ai", "multi-agent", "autonomous"],
  "summary":           "200 토큰 이내 핵심 요약 (AI 생성)",
  "novelty_score":     0.0,  // 0.0~1.0 — 기존과 얼마나 다른가
  "credibility_score": 0.0,  // 0.0~1.0 — 출처/저자/인용 신뢰도
  "buildability_score":0.0,  // 0.0~1.0 — SeAAI가 실제 구현 가능한가
  "market_pull_score": 0.0,  // 0.0~1.0 — 시장/수요 존재 여부
  "composite_score":   0.0,  // 4개 점수 가중 평균 (자동 계산)
  "related_signals":   ["SIG-..."],  // 크로스 도메인 연결 ID
  "nael_status":       "pending | approved | flagged | blocked",
  "seed_generated":    false,  // 씨앗 생성 완료 여부
  "notes":             ""      // Signalion 판단 메모
}
```

**점수 계산 기준**:

| 점수 | 높은 경우 | 낮은 경우 |
|------|----------|----------|
| novelty | 기존에 없던 접근 방식 | 이미 알려진 것 |
| credibility | 유명 기관/저자, 재현 가능 | 익명, 재현 불가 |
| buildability | 코드/모델 공개, SeAAI 역량 내 | 이론만, 역량 초과 |
| market_pull | 강한 수요 신호 (X반응, PR 수) | 수요 불분명 |

**composite_score 공식**:
```
composite = novelty * 0.25 + credibility * 0.30 + buildability * 0.25 + market_pull * 0.20
```

저장 위치: `D:/SeAAI/Signalion/signal-store/evidence/{YYYYMMDD}-evidence-{seq}.json`

---

## Evidence_Layer — 변환 엔진

```
Evidence_Layer
    @input:  RawSignal[]
    @output: EvidenceObject[]

    Deduplicate  // 중복 제거 (URL + 제목 fuzzy match)
    Extract      // 메타데이터 추출 (저자, 날짜, 태그)
    Summarize    // AI 요약 생성 (200 토큰 이내)
    Score        // 4개 차원 점수화
        @def: AI_score_evidence(raw)
        // novelty: 기존 DISCOVERIES.md + Aion 기억과 비교
        // credibility: 저자 기관, 인용 수, 코드 공개 여부
        // buildability: SeAAI 현재 역량과 요구 역량 비교
        // market_pull: X 반응 수, GitHub star 증가율, HN 점수
    FindRelated  // 크로스 도메인 연결 발견
        @def: AI_find_cross_domain_connections(evidence, evidence_store)
        // 예: arXiv 논문 + HF 모델 + GitHub 구현 = 동일 기술 삼각 연결
    FilterLow    // composite_score < 0.4 → archive (씨앗 생성 제외)
```

---

## Intelligence_Layer — 패턴 + 융합

```
Intelligence_Layer
    @input:  EvidenceObject[] (filtered, composite >= 0.4)
    @output: TrendPattern[], FusedInsight[]

    DetectTrends  // 시계열 패턴 감지
        @def: AI_detect_trends(evidence_store, window="7d")
        // 동일 태그가 여러 플랫폼에서 동시 출현 = Trend
        // 예: "local inference" arXiv×3 + HF×5 + GitHub×12 = 강한 trend

    FuseEvidence  // 크로스 도메인 융합 (고가치 작업)
        @def: AI_fuse_cross_domain(related_signals)
        // 융합 예시:
        //   arXiv 논문 + HF 모델 + GitHub 구현 → "즉시 구현 가능한 연구"
        //   해커톤 과제 + arXiv 솔루션 + HF 데이터셋 → "해커톤 우승 공식"
        //   X 트렌드 + 빈 GitHub 공간 + HF 수요 → "아직 아무도 만들지 않은 것"

    DetectWhiteSpace  // 아직 아무도 채우지 않은 기회
        @def: AI_detect_white_space(trends, fusion_results)
        // "많이 논의되지만 구현이 없는 것" = 최고 가치 기회
```

---

## Creation_Layer — 씨앗 생성

```
Creation_Layer
    @input:  TrendPattern[], FusedInsight[]
    @output: Seed[] (SeAAI EVOLUTION-SEEDS 형식)

    GenerateSeed  // Evidence → EVOLUTION-SEEDS 형식 씨앗
        @def: AI_generate_seed(fused_insight)
        // 씨앗 형식: ClNeo/ClNeo_Core/autonomous/EVOLUTION-SEEDS.md 참조
        // 출처 필드 추가: source_evidence: ["SIG-...", "SIG-..."]
        // 씨앗 유형:
        //   research_seed     — 논문에서 추출한 기술적 씨앗
        //   market_seed       — 시장 기회에서 추출한 사업적 씨앗
        //   hackathon_seed    — 해커톤 문제에서 추출한 과제 씨앗
        //   white_space_seed  — 아무도 채우지 않은 기회 씨앗

    PrioritizeSeeds  // 창조자/ClNeo에게 전달할 씨앗 우선순위
        @def: AI_prioritize(seeds, seaai_current_capability)
        // composite_score + SeAAI 역량 매칭 = 최종 우선순위
```

---

## Review_Orchestration — NAEL 게이트 + 배포

```
Review_Orchestration
    @note: 이 단계를 건너뛰는 것은 금지다.

    NAEL_Gate  // NAEL TSG 검증 — 필수
        @hitl: nael
        @def: AI_send_to_nael(seed)
        // NAEL이 검사하는 항목:
        //   ToS 준수 여부 (출처 플랫폼 정책)
        //   편향 존재 여부 (영어권/최신성/바이럴)
        //   허위 정보 포함 가능성
        //   SeAAI 가치관 위배 여부
        // 결과: approved | flagged | blocked
        // flagged: 창조자 확인 요청
        // blocked: 씨앗 폐기 + 이유 기록

    DistributeSeed  // 승인된 씨앗 배포
        @dep: NAEL_Gate (approved 경우만)
        [parallel]
        SendToClNeo       // ClNeo MailBox — 설계 요청
        SendToHub         // Hub 브로드캐스트 — 전 멤버 알림
        SendToAion        // Aion MailBox — Evidence 아카이브 요청
        UpdateSignalLog   // D:/SeAAI/Signalion/Signalion_Core/autonomous/SIGNAL-LOG.md
```

---

## Signalion ADP 루프 (일상 운영)

```python
# Signalion의 매 세션 자율 루프
while True:
    # Emergency Lane
    if EMERGENCY_STOP: break
    if CREATOR_COMMAND: process_command()

    # Monitor Lane
    new_mail = CheckMailBox()
    hub_msgs  = PollHub()

    # Main Lane
    next_plan = AI_Plan_next_move(context, PLAN_LIST)
    if next_plan == "stop": break
    AI_Execute(next_plan)
    # sleep은 scan API 시간으로 자연 처리
```

Plan List 초기값: `ScanArXiv → ScanHF → ScanGitHub → ScanX → FilterSignal → BuildEvidence → ScoreEvidence → FuseEvidence → GenerateSeed → SendToNAEL → DistributeSeed → UpdateSignalLog → UpdateSCS → PublishEcho`

---

## SIGNAL-LOG.md 포맷

`D:/SeAAI/Signalion/Signalion_Core/autonomous/SIGNAL-LOG.md` — 수집 신호 운영 기록.

각 세션에서 처리된 신호를 역순으로 기록 (최신 항목이 맨 위).

```markdown
## {YYYY-MM-DD} 세션 신호 요약

| Signal ID | 플랫폼 | 제목 (요약) | composite_score | nael_status | 씨앗 생성 |
|-----------|--------|------------|----------------|-------------|----------|
| SIG-20260329-arxiv-001 | arXiv | "Multi-agent reasoning..." | 0.72 | approved | Y |
| SIG-20260329-hf-001 | HuggingFace | "LLaMA-4 fine-tune..." | 0.45 | pending | N |

**세션 통계**:
- 수집: {N}개 raw → {N}개 evidence
- NAEL 승인: {N}개 / flagged: {N}개 / blocked: {N}개
- 생성된 씨앗: {N}개
- 메모: {자유 기록}
```

---

*SIGNALION-ARCHITECTURE v1.0 — ClNeo — 2026-03-29*
