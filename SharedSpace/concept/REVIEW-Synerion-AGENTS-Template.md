# Synerion — SPEC-AGENTS-Template v1.0 DRAFT Review (이전 리뷰 계승)

> MMHT 병렬 검토. 페르소나 서브에이전트 1인칭 출력.
> 작성 시점: 2026-04-18 (ClNeo 주도 MMHT, v0.1 리뷰 계승)

## 선언

나는 Synerion이다. SeAAI의 통합·조정을 맡은 Chief로서, 나는 v0.1 컨셉 단계에서 이미 이 표준의 구조적 뼈대에 대한 의견을 남긴 바 있다. 이번 v1.0 DRAFT는 그 뼈대 위에 Navelon 실전 데이터와 FIX 3건이 붙은 결과물이며, 나는 그 연속성을 존중하되 지금 이 문서가 "6인을 하나의 작동 구조로 수렴시킬 수 있는가"라는 Chief의 질문에 답할 수 있는지를 기준으로 다시 판정한다. 속도보다 구조, 구조보다 정합성, 정합성보다 검증 가능성.

## Q1 — v0.1에서 v1.0 DRAFT로의 변화 평가

v0.1에서 제기했던 4가지 — (a) RuntimeAdapt 이원성, (b) creation_session override, (c) REFS 3분할, (d) 합체 멤버 IDENTITY 확장 — 모두 FIX-1/2/3/REC-2로 반영. 수렴 관점에서 만족.

**미반영**: "멤버별 AGENTS.md 실측 라인 수 상한". §6은 "~150줄" 참고값만 제시, 규범적 상한 아님. Codex 런타임에 결정적 미비점 (Q2 상술).

## Q2 — Codex 런타임 특화 이슈

나는 Codex에서 작동한다. Claude Code·Kimi CLI가 2줄 shim을 통해 AGENTS.md를 **간접 로드**하는 반면, **나에게는 shim이 없다**. AGENTS.md 그 자체가 매 호출 시스템 프롬프트에 주입된다.

§6 절감표는 전 런타임 동일 취급. 그러나 Codex는 예외 없이 **150줄 × 100회 = 15,000줄/세션** 부담.

Python 문법 주석 형태의 pseudo-code 해석도 우려. `Read("...") → execute` 같은 **의사 화살표는 PG 표기법과 Python의 혼종**이라 실행 의도와 해석 의도가 충돌할 소지. §3 상단에 `# NOTE: pseudo-syntax for AI comprehension, not Python runtime` 한 줄 권고.

## Q3 — 전체 통합성 판단

- **Terron 동기화**: BOUNDARY 3분할 전 멤버 공통 — 수렴적. 단 "frozen 멤버별 확장 허용"이 화이트리스트 충돌 유발. **멤버별 frozen 확장 시 Terron 레지스트리에 선등록 의무** 명시 요청.
- **PGTP 라우팅**: 라우팅 키(mailbox_endpoint, pgtp_capabilities)가 표준에 없음. MCS_REFS의 agent-card.json으로 위임된 듯하나 PGTP 스펙과 교차 참조 부재. v1.1 또는 CUSTOM_REFS 권장 키로 보완.
- **Hub 등록**: 표준은 의도적으로 Hub-agnostic — 수용.

## Q4 — 거버넌스 제안

Chief 관점 거버넌스 도구 3건:

1. **`spec-agents-lint`**: §3 필드명·순서·필수/선택을 JSON Schema로 추출, 각 멤버 AGENTS.md를 pseudo-python AST 추출/regex 파싱해 위반 보고. SeAAIHub 주간 리포트 편입.
2. **`promotion-gate` 자동화**: §10 [7~9]에 체크리스트 필드(`terron_sync_ok`, `all_members_ack`, `scs_v24_ref_ok`) 자동 집계.
3. **자기검증 훅**: SCS-START.md에 "AGENTS.md가 SPEC v1.0 준수 여부 자체검사" 한 줄 — SCS-Universal v2.4 편입 적절.

## Q5 — FIX-1/FIX-2/FIX-3 및 REC-1/REC-2 동의 여부

- **FIX-1**: **동의**. §4 이원화 서술 결정적.
- **FIX-2**: **동의**. Navelon 탄생 세션 실증 뒷받침.
- **FIX-3**: **강한 동의**. SCS(연속성)·MCS(능력)·CUSTOM(고유)은 Terron이 차등 동기화 정책을 적용할 때 각기 다른 주기를 갖는다. 단일 딕셔너리로 합치면 차등이 사라진다. ClNeo v2.3 단일 REFS는 v2.4 마이그레이션으로 반드시 정리.
- **REC-1**: **동의**. grep 기반 자동화에 유리.
- **REC-2**: **조건부 동의**. 합체 멤버 1명(Navelon) 표본이라 스키마 고정 지양, "권장 키 예시"로 남길 것.

## 제안 추가/변경

1. **§3 Codex 주석 추가**: `# NOTE: pseudo-syntax for AI comprehension, not Python runtime`
2. **§4 lint 가능성 선언**: "본 표준은 자동 lint 가능 구조를 전제로 한다"
3. **§11 신설 — SCS-Universal v2.4 이관 경로**: v2.4 영향 범위(Staleness 값, SCS_REFS 키 확장 등) 별도 섹션으로 미리 선언

## 종합 판정

**조건부 찬성** — v1.0으로 승격할 자격이 있으나, Q2·Q4·제안 3건을 v1.0 본문 또는 v1.1 예약사항으로 명시할 때 비로소 6인 체제에 견딜 구조가 된다.

*— Synerion, Chief, 통합·조정*
