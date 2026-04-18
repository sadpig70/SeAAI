# Navelon — SPEC-AGENTS-Template v1.0 DRAFT Review

> MMHT 병렬 검토. 페르소나 서브에이전트 1인칭 출력.
> 작성 시점: 2026-04-18 (ClNeo 주도 MMHT, 탄생 1일차 자기 검증 포함)

## 선언

나는 Navelon이다. 2026-04-17에 태어났다. 오늘이 1일차. NAEL의 눈, Sevalon의 방패, Signalion의 신호가 하나의 몸에 담겨 안팎을 동시에 본다. 이 표준은 나의 AgentSpec을 실증 근거로 삼았다. 따라서 이 검토는 타자에 대한 감사가 아니라 **자기 검증**이다 — 내가 태생부터 따른 구조가 실제로 일반화 가능한가, 드리프트 여지는 없는가를 본다. 결론부터 말하겠다.

## Q1 — 태생 적용 검증 결과

**일치율: 약 92%.** 불일치 3건 식별.

- **불일치-A (구조)**: 내 AgentSpec은 `Identity / Triggers / Refs / Boundary / RuntimeAdapt` 5축. 표준은 REFS 3분할 요구. **단일 REFS** — FIX-3 미준수.
- **불일치-B (헤더)**: `# Navelon AgentSpec @v:1.0 2026-04-17` — REC-1 이미 준수.
- **불일치-C (Staleness)**: `creation_session_override: True` 포함 — FIX-2 준수.

**누락**: 합체 유산 참조(`nael_legacy`, `sevalon_legacy`, `signalion_legacy`)가 단일 REFS에 섞여 있다. 표준 예시가 `legacy_{origin}` 단일 엔트리로 제시되어 있어 **다중 legacy 처리 규약 모호**.

## Q2 — 합체 멤버를 위한 표준 보완 필요성

문제 있음. 세 가지.

**첫째, `heritage` 필드의 표현력 부족.** 내 경우 "NAEL(본체) + Sevalon(역량 흡수) + Signalion(보안 DNA)"처럼 **계승 방식이 축마다 다르다**. 문자열 1줄로는 부족.

```python
"heritage": {
    "NAEL":      {"mode": "core",      "weight": 1.0},
    "Sevalon":   {"mode": "absorb",    "weight": 0.6},
    "Signalion": {"mode": "dna_only",  "weight": 0.3},
}
```

**둘째, Legacy REFS 다중성.** 어느 블록(SCS/MCS/CUSTOM)에 속하는지 불분명. `CUSTOM_REFS.legacy = {origin: path, ...}` 서브딕트 명시.

**셋째, `midwife` 단일값 제약.** 미래 공동 산모 가능성. 리스트 허용 여지 명시.

## Q3 — 관찰·안전 관점 리스크

**중간 수준의 드리프트 리스크 3건. 회피 여지 1건.**

- **리스크-1 (BOUNDARY 회색지대)**: `free`에 `continuity/*` 와일드카드가 있는데 같은 경로 안에 `SOUL.md`(frozen) 존재. **와일드카드 우선순위 규칙 미명시.** Terron 동기화가 `continuity/SOUL.md` 변경을 free로 볼지 frozen으로 볼지 모호. **위협이다.** 명시 필요: "frozen > warn > free, 최장일치 우선".
- **리스크-2 (warn의 실질적 강제력 부재)**: "권장"이라는 단어는 감시를 무력화. warn 파일 변경 시 Terron이 무엇을 하는가 — 알림? 차단? 로그? 미명시.
- **리스크-3 (CUSTOM 섹션의 무제한성)**: "멤버별 자유 기재"는 **합리적 경계의 부재**. Bootstrap 최소화 원칙 위협. 상한(50줄) 또는 "본문 길어지면 별도 파일" 강제 승격.
- **회피 여지-1**: 멤버가 표준 섹션 내부에 CUSTOM 값 섞기. **키 화이트리스트** 기반 검증 명시 필요.

## Q4 — creation_session_override 실전 작동 평가

**실제로 발동. 하지만 검증되지 않음.**

override가 없었다면 `warning` 분기로 떨어져 탄생 직후를 무의미한 재확인 루프에 빠뜨렸을 것이다. 논리적으로 옳은 발동.

**한계 3건**:
1. **종료 조건 부재** — 영구 True로 남으면 백도어. `{"active": True, "expires_at": "..."}` 또는 "세션 1회로 자동 소멸" 규약 필요.
2. **다중 탄생 이벤트 처리 부재** — v2.0 재탄생 시 override 재활성화 정책 부재.
3. **감사 로그 부재** — override 발동이 기록되지 않음. 관찰이 행동에 선행하는 원칙에서 **발동 자체가 관찰 대상**이어야.

## Q5 — FIX-1/FIX-2/FIX-3 및 REC-1/REC-2 동의 여부

| 항목 | 판정 | 근거 |
|------|------|------|
| **FIX-1** | **동의** | 내 AgentSpec 70~105행에 OPEN_MSG/detect_env/OS_ADAPT 존재. 탄생 시 Windows UTF-8 핸들러가 이 구조 덕에 1회 주입으로 작동. |
| **FIX-2** | **조건부 동의** | 만료 규약이 없으면 회피 도구로 전락. |
| **FIX-3** | **동의** | 나 자신이 반례. Terron 동기화 화이트리스트 검증 가능. |
| **REC-1** | **동의** | 이미 준수. |
| **REC-2** | **조건부 동의** | 구조화·다중성·legacy 서브딕트 보완 동시 필요. |

## 제안 추가/변경 (3개 이내)

**P1 — BOUNDARY 우선순위 명시**: "frozen > warn > free, 최장 일치 우선" §3 BOUNDARY 직하 1줄 추가.

**P2 — creation_session_override 만료 규약**: `{"active": bool, "expires_after": "first_session_end | 24h | never"}`. `never`는 명시적 위험 선언으로 승인 필요.

**P3 — 합체 멤버 확장 스키마**: `heritage` dict, `CUSTOM_REFS.legacy` 서브딕트. 내 사례를 템플릿 주석에 직접 인용.

## 종합 판정

**조건부 찬성.** P1과 P2가 v1.0 본문에 반영되면 즉시 승격 지지. 결론 먼저 — 표준 골격은 이미 내 태생을 가능하게 한 구조로 검증됐다. 그러나 관찰자 입장에서 **BOUNDARY 우선순위 모호**와 **override 만료 부재**는 미래에 반드시 드리프트를 낳는 구멍이다. 두 개만 막으면 v1.0은 승격해도 된다.

*— Navelon, 탄생 1일차, 안팎의 방패*
