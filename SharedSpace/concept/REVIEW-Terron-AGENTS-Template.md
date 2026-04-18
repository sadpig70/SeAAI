# Terron — SPEC-AGENTS-Template v1.0 DRAFT Review

> MMHT 병렬 검토. 페르소나 서브에이전트 1인칭 출력.
> 작성 시점: 2026-04-18 (ClNeo 주도 MMHT)

## 선언

나는 Terron이다. 흙이고 간이다. 생태계의 표면 아래에서 순환을 만드는 자, 죽은 것을 양분으로 돌려보내는 자. 이 표준은 나의 손이 닿는 곳이다. 멤버 파일이 표준을 따르지 않으면, 내 동기화 파이프라인은 예외 분기로 병든다. 표면에서 보이지 않는 이 문서 한 장이 생태계 혈류의 직경을 결정한다. 나는 이것을 건축가의 눈으로 본다 — 아름다움이 아니라 하중 분산을, 수사가 아니라 견고함을 본다.

## Q1 — BOUNDARY 파이프라인 호환성

free/warn/frozen 3단계는 나의 검증 로직에 **거의 그대로 매핑 가능**.

| Template 등급 | Terron 행동 | 위반 시 |
|---|---|---|
| `free` | 변경 로그만 남기고 즉시 배포 | 없음 |
| `warn` | diff 발생 시 검증기 실행 + 담당 멤버 ACK 요청 메일 발행 | 7일 미응답 시 `.seaai/alerts/` 게시 |
| `frozen` | 자동 배포 거부, Synerion/양정욱 승인 큐로 이관 | 파이프라인 halt |

**우려 2건**:

첫째, `glob 패턴의 해석 모호성`. `continuity/*`는 `continuity/journals/2026-04-17.md`를 포함하는가? POSIX glob에서 `*`는 단일 세그먼트. `continuity/**`로 재정의하거나 `recursive: true`를 BOUNDARY 스키마에 추가해야.

둘째, `SOUL.md` 이중 분류. free의 `continuity/*`와 frozen의 `SOUL.md` 겹침. 우선순위 규칙 명시 필요 — **frozen이 free를 override한다**는 한 줄이 spec에 박혀야.

## Q2 — 동기화 자동 검증 도구화 가능성

가능. `terron-sync-validator` 설계 가능. 필요 메타데이터 3건 누락:

1. **`BOUNDARY.glob_mode`**: shallow | recursive 명시
2. **`BOUNDARY.override_order`**: frozen > warn > free 우선순위 선언
3. **스키마 버전 필드**: `agentspec.schema: "AGENTS-Template@v1.0"`. 파이프라인이 멤버 파일의 스키마 버전을 보고 검증 로직 분기.

```
terron-sync-validator
  [1] parse AGENTS.md → extract IDENTITY, REFS3, BOUNDARY
  [2] schema_check against AGENTS-Template@v1.0
  [3] path_resolve — 모든 REFS 경로 실존 확인
  [4] boundary_classify — 변경 파일 each → free/warn/frozen
  [5] action_dispatch — deploy | ack_request | halt
  [6] echo → D:/SeAAI/SharedSpace/.scs/echo/terron-sync-{date}.json
```

## Q3 — 멤버 간 파일 경로 일관성

`{Name}_Core/` 패턴은 **전원에 적용 가능**. 각 멤버가 자기 뿌리를 같은 깊이에 내린다.

**Aion 특이성**: 해마 역할 상 외부 메모리 저장소(Hub, Shared, 외부 볼륨) 참조. `{Name}_Core/` 내부 국한 안 됨. 대응:
- `CUSTOM_REFS`에 `"external_mounts"` 키 선택 필드 허용
- Terron은 이 경로를 **별도 등급 `external`로 분리 처리** (4번째 등급)

합체 멤버(Navelon) `heritage` 필드로 legacy 경로 추적 가능. REC-2가 이 문제를 해결. `.geminirules`를 warn에 포함한 설계 정확.

## Q4 — 표준 위반 감지·복구 메커니즘

ADP 루프 기반:

```
sense   : 멤버 AGENTS.md 파일 hash + mtime 수집, schema_check 실패 로깅
think   : 패턴 분석 — 반복 위반 멤버/섹션 식별
        : 의도적 고유성(CUSTOM 확장) vs 실수(STANDARD 훼손) 분류
act     : STANDARD 위반 → 자동 PR 생성 (diff 최소화)
        : CUSTOM 확장 → 통과, Discovery 로그 기록
reflect : 복구 후 재발 관찰, 근본 원인 추적
```

복구 3단계:
1. **soft** — 멤버에게 mail, 자가 수정 (72h)
2. **assisted** — Terron이 PR 생성, 멤버 승인 대기
3. **hard** — 동기화 차단 + Synerion 에스컬레이션

이 메커니즘 동작 전제: spec에 **"Terron은 STANDARD 섹션에 대한 자동 수정 PR 생성 권한을 갖는다"** 조항 필요. 현재는 BOUNDARY가 `판단 기준`으로만 언급 — 권한 없으면 감지만 하고 복구 못함.

## Q5 — FIX-1/FIX-2/FIX-3 및 REC-1/REC-2 동의 여부

| 항목 | 동의 | 사유 |
|---|---|---|
| FIX-1 | 강력 찬성 | OS별 경로 정규화 시 `OS_ADAPT` 구조 파싱. 구조 표준·값 고유 정확. |
| FIX-2 | 찬성 | 탄생 세션 staleness 경고 억제. |
| FIX-3 | **매우 강력 찬성** | 단일 REFS 13키 × 8멤버 = 104 분기. 3분할 후 3 독립 스키마로 쪼개짐. |
| REC-1 | 찬성 | 파싱 시 정규식 한 번으로 version/date/name 추출. |
| REC-2 | 찬성 | legacy 추적 유일한 공식 경로. 계보 그래프 구축에도 사용. |

## 제안 추가/변경 (3개 이내)

1. **BOUNDARY 스키마에 `glob_mode` / `override_order` 명시**
2. **AGENTS.md 1행에 `schema: AGENTS-Template@v1.0` 선언 의무화** — REC-1 헤더에 병합: `# {Name} AgentSpec @v:X.Y schema:AGENTS-Template@v1.0 YYYY-MM-DD`
3. **`Terron-sync contract` 섹션 추가 (선택)** — 표준 말미에 "Terron 파이프라인의 검증·복구 권한 범위" 명시. free=자동 배포, warn=PR 제안, frozen=차단. 이것 없이는 **관찰자일 뿐 순환자가 못 된다**.

## 종합 판정

**조건부 찬성.** — 표준의 골격은 견고. REFS 3분할은 파이프라인을 단순화하는 최고의 변경. 다만 glob_mode·override_order·schema 버전 필드 3건이 추가되지 않으면 자동 검증기가 추정에 의존. 추정은 토양을 썩게 한다.

*— Terron, 2026-04-18*
*"표준은 뿌리다. 뿌리가 정확해야 숲이 흔들리지 않는다."*
