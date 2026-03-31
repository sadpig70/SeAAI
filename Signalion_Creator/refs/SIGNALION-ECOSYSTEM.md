# SIGNALION-ECOSYSTEM.md
# Signalion의 SeAAI 생태계 연동 설계

> Signalion이 5명의 기존 멤버들과 어떻게 협력하는지 정의한다.
> 출처: ClNeo 의견 + 양정욱님 원안 §11 + DESIGN-SynerionRouting.md 연동

---

## SeAAI 내 Signalion의 위치

```
[외부 세계]
    arXiv / HF / GitHub / X / Devpost / Reddit / HN
         ↓ 수집
    [Signalion] ← 감각 기관 (Sensory Organ)
         ↓ Evidence Object (NAEL 게이트 통과 후)
    [NAEL] ── TSG 게이트: ToS, 편향, 안전 검증
         ↓ approved
    [Synerion] ── external_signal 라우팅
    ↙         ↘
[ClNeo]     [Aion]
설계 발전   증거 아카이브
```

---

## 멤버별 협업 상세

### NAEL — 필수 게이트 파트너

**관계**: Signalion의 모든 출력이 NAEL을 통과해야 한다.

**NAEL이 검사하는 항목**:
1. **ToS 준수**: 출처 플랫폼 이용약관 위반 여부
2. **편향 감지**: 영어권/최신성/생존자/바이럴 편향
3. **허위 정보 위험**: 미검증 주장 포함 여부
4. **SeAAI 가치관**: 윤리 위배 내용 포함 여부

**게이트 결과**:
- `approved` → Synerion 라우팅으로 진행
- `flagged` → 창조자(양정욱님) 확인 요청
- `blocked` → 씨앗 폐기 + 이유 기록 (Signalion에 피드백)

**MailBox 형식**: `D:/SeAAI/MailBox/NAEL/inbox/{날짜}-Signalion-evidence-{seq}.md`

---

### Aion — 증거 아카이브 파트너

**관계**: Evidence Object의 장기 보관 담당. Signalion이 수집하고 Aion이 기억한다.

**협업 방식**:
1. Signalion이 Evidence Object 생성 → Aion에게 MailBox 전송
2. Aion이 `D:/SeAAI/SharedSpace/evidence-graph/` 아카이브
3. Signalion이 새 신호 평가 시 Aion에게 "유사 과거 신호 검색" 요청 가능

**Evidence Graph** (Aion 관리):
```
SharedSpace/evidence-graph/
├── index.md          # 전체 Evidence 인덱스
├── by-tag/           # 태그별 분류
├── by-source/        # 플랫폼별 분류
└── cross-domain/     # 융합 연결 맵
```

**기대 효과**: 시간이 지남에 따라 "트렌드 역사 데이터베이스" 형성

---

### ClNeo — 씨앗 수신자

**관계**: Signalion이 만든 씨앗의 주요 소비자. 씨앗 → 설계 → 구현.

**협업 방식**:
1. NAEL 승인 씨앗 → ClNeo MailBox 전달
2. ClNeo가 씨앗을 `EVOLUTION-SEEDS.md`에 추가 (외부 출처 명시)
3. ClNeo가 설계로 발전시키면 Signalion에 진행 상황 피드백 (선택적)

**씨앗 형식** (EVOLUTION-SEEDS.md 호환):
```markdown
## SEED-{N}: {제목}
**출처**: Signalion — {원본 Signal ID}
**유형**: research_seed | market_seed | hackathon_seed | white_space_seed
**Evidence**: {SIG-날짜-플랫폼-seq}
**현재 상태**: 발견됨
**발현 조건**: {언제 실행하면 좋은가}
**설명**: {2~3문장}
**관련 씨앗**: SEED-{N-1}, SEED-{N-2}
```

---

### Synerion — 라우팅 업데이트 대상

**관계**: Signalion 합류 시 `DESIGN-SynerionRouting.md` 업데이트 필요.

**업데이트 내용**:

```
// 라우팅 테이블 추가 (Synerion에게 MailBox 요청)
external_signal → Signalion (수집) → NAEL (게이트) → Synerion (라우팅)
```

**추가할 라우팅 행**:

| 작업 유형 | 1차 멤버 | 2차 멤버 | Dual-Audit |
|-----------|---------|---------|-----------|
| 외부 신호 수집 | Signalion | — | NAEL 필수 |
| 트렌드 분석 요청 | Signalion | ClNeo | 선택적 |
| 해커톤 과제 파악 | Signalion | Yeon | 선택적 |

**Trust Score 초기값**: 0.4
- 이유: 외부 데이터 주입 특성상 보수적 시작
- 성공적인 NAEL-approved 씨앗 축적 → 점진 상승

---

### Yeon — 비영어권 파트너

**관계**: 영어권 편향 방지를 위한 비영어 신호 협력.

**협업 시나리오**:
- 일본어 논문/블로그, 중국어 오픈소스 프로젝트 처리 시 Yeon 협력
- Yeon이 번역 + 컨텍스트 제공 → Signalion이 Evidence Object 완성

---

## Signalion 합류 절차 체크리스트

**창조 완료 후 순서대로 실행**:

- [ ] 1. `D:/SeAAI/MailBox/Signalion/inbox/` 폴더 생성 확인
- [ ] 2. Hub allowed_agents에 "Signalion" 추가 (창조자 승인)
- [ ] 3. `D:/SeAAI/SharedSpace/.scs/echo/Signalion.json` 첫 Echo 작성
- [ ] 4. `D:/SeAAI/SharedSpace/member_registry.md`에 Signalion 추가 요청 → Synerion에 MailBox
- [ ] 5. 자기소개 MailBox 발송 (5명 전원)
- [ ] 6. Synerion에 라우팅 테이블 업데이트 요청
- [ ] 7. NAEL에 "외부 신호 검증 파트너십" 요청
- [ ] 8. Aion에 "Evidence Graph 아카이브 협약" 요청
- [ ] 9. 첫 신호 수집 + NAEL 게이트 통과 확인 (Phase 6)

---

## SeAAI 설계·구현·테스트·검증 리뷰 체계

양정욱님 원안 §11에서 정의한 단계별 리뷰 — 이것이 Signalion의 산출물이 거치는 품질 관문이다.

| 단계 | 리뷰어 | 검토 항목 |
|------|--------|----------|
| **설계** | Synerion | 구조적 타당성 |
| | Yeon | 외부 API/플랫폼 호환 |
| | ClNeo | 시스템 구현 가능성 |
| **구현** | Aion | 루프/메모리/자동화 |
| | Synerion | 모듈 구조 |
| | Yeon | 외부 연동 |
| **테스트** | NAEL | 오류/리스크/허위 양성 |
| | Aion | 반복 실행/회귀 |
| | Synerion | 테스트 명세 품질 |
| **검증** | 전 멤버 합의 | + 인간 최종 승인 |

---

## 운영상 주의점 요약

### 법적/정책적
- 각 플랫폼 ToS 준수 (NAEL 게이트가 1차 필터)
- 저장 데이터 범위: 재배포 불가 원문 저장 금지
- 수집 데이터의 재배포 가능 여부 EvidenceObject에 기록

### 기술적
- provenance(출처 추적) 보존 — Evidence Object의 source + url + collected_at
- cache 전략: 동일 URL 24시간 내 재수집 금지
- dedupe 우선: 중복 수집이 score inflation 야기

### 인지적
- 바이럴 노이즈와 본질 신호를 항상 구분 (credibility_score 활용)
- 최신성 편향: "오래됐다"는 이유만으로 낮은 novelty_score 금지
- 미국/영어권 편향: 비영어 신호 의식적 포함

---

*SIGNALION-ECOSYSTEM v1.0 — ClNeo — 2026-03-29*
