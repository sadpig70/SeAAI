# pg/pgf Review & Improvement Log

> pg·pgf 면밀 검토 → 수정/개선/추가 반복 기록
> DESIGN: `.pgf/DESIGN-PgPgfReview.md`
> Date: 2026-03-16

---

## Cycle 1: 전체 분석

### AnalyzePg — pg SKILL.md 이슈

| # | Location | Type | Issue | Suggestion |
|---|----------|------|-------|------------|
| P1 | §원자노드, 항목3 | fix | "구현 복잡도 — 50줄 이하 단일 함수" vs 15분 룰 모순 가능. 50줄이어도 15분 넘을 수 있고, 200줄이어도 15분 안에 가능 | 50줄 기준 제거 또는 "참고 지표"로 약화. 15분 룰이 최종 판단 기준임을 명확화 |
| P2 | §원자노드, 항목4 | fix | "시간 예측성 — 구현 30분 이내"와 하단 "15분 룰" 불일치 (30분 vs 15분) | 30분 → 15분으로 통일, 또는 "30분 이내 = 구현, 15분 = AI 코드 작성"으로 구분 명확화 |
| P3 | §상태코드 실행규칙 | improve | `(done)` / `(in-progress)` 모두 "PPR def 블록 완전 실행"으로 설명. done은 이미 완료된 상태인데 "실행"이 혼란 | `(done)` = "이미 실행 완료, 건너뜀" / `(in-progress)` = "PPR def 블록 실행" 으로 분리 |
| P4 | §PPR 전체 | improve | pg의 핵심 정체성(AI 인지 표기 DSL, 소통 언어)이 서두에 한 줄로만 있고, 대부분이 문법 설명. pg가 "왜" 존재하는지의 철학적 맥락 부족 | §핵심 속성 전에 "pg란 무엇인가" 1-2문단 추가: AI의 인지·사고·창발성을 시스템 수준으로 표기하는 DSL |
| P5 | §AI_make_ | add | 사역 패턴 설명은 있으나, 실전 사용 빈도가 낮아 언제 쓰는지 판단 기준 부족 | "판단 기준: 동사의 주어가 AI 자신이면 AI_, 대상이 변화의 주체이면 AI_make_" 이미 있지만, 실전 예시(Discovery에서의 사용 등) 추가 |
| P6 | §Progressive Formalization | improve | Level 1/2/3 노드 수 기준이 pg와 pgf SKILL.md에서 다름: pg는 "≤3, 4~10, 10+", pgf는 "≤3, 4-10, 11-30, >30" | pg의 기준을 정본으로 하고, pgf의 확장(Large, Multi-agent)은 pgf에서만 정의하도록 명확히 분리 |

### AnalyzePgf — pgf SKILL.md + 레퍼런스 이슈

| # | Location | Type | Issue | Suggestion |
|---|----------|------|-------|------------|
| F1 | SKILL.md §Current Project PGF State | fix | bash 명령 실행 오류 발생 (`.mode`, `.iteration` 등). PowerShell 환경에서 `$$` 이스케이프 문제 | `$$` → `\$` 또는 PowerShell 호환 구문으로 수정 |
| F2 | workplan-reference.md §3 | fix | 상태 전이도에 `pending` 사용하지만 pg 정본의 status는 `designing`. 용어 불일치 | `pending` → `designing`으로 통일, 또는 pg에 `pending` 추가하고 `designing`과 구분 명확화 |
| F3 | workplan-reference.md §2 | fix | DESIGN→WORKPLAN 변환 시 "Initialize all node statuses to `(pending)`"이지만, pgf-format.md는 "`(designing)`"으로 초기화 | 하나로 통일: `designing`(pg 정본) 또는 `pending`(실행 대기 의미) 중 택 1 |
| F4 | pgf-checklist.md | improve | "pg 6개 + pgf 3개" 상태 코드라고 했지만, workplan-reference.md는 `pending` 추가 사용. 총 몇 개인지 혼란 | 체크리스트에 전체 상태 코드 목록 명시 |
| F5 | verify-reference.md §7 | improve | POLICY의 `verify_perspectives` 기본값이 `["performance", "security", "maintainability"]`인데, §2의 3관점은 "Acceptance, Code Quality, Architecture". 다른 체계 | 기본 3관점과 POLICY 커스텀 관점의 관계 명확화: 기본 3 + 추가 N |
| F6 | SKILL.md §Execution Modes 테이블 | fix | `design --analyze` 가 별도 행이지만 실제로는 `design` 모드의 옵션. 모드 수 계산에 혼란 (9개? 10개?) | `design --analyze`를 design 행의 하위로 통합하거나, 주석으로 "design의 하위 옵션"임을 명시 |
| F7 | SKILL.md | add | v2.4에서 추가된 Epigenetic PPR, Compaction Resilience, Design Review의 레퍼런스 문서 참조가 테이블에 누락 | Design Review는 추가됨(확인). Epigenetic과 Compaction은 loop-reference.md에 포함되어 있으므로 추가 참조 불필요. 확인 완료. |

### AnalyzeCrossConsistency — pg↔pgf 교차 일관성 이슈

| # | Type | Issue | Resolution |
|---|------|-------|------------|
| C1 | 용어 불일치 | pg: `designing` / workplan-reference: `pending` — 같은 "아직 실행 안 됨" 의미에 다른 용어 | **핵심 이슈**. 하나로 통일 필요 |
| C2 | 상태 코드 수 | pg: 6개 (done, in-progress, designing, blocked, decomposed, needs-verify) / pgf: +3개 (delegated, awaiting-return, returned) / workplan: +1개 (pending) — 총 10개? 9개? | 전체 목록 한 곳에 정의, 나머지는 참조 |
| C3 | 원자 노드 시간 | pg: "15분 룰" 최종 + "구현 30분" 항목 / pgf: 15분 룰만 참조 | pg 내부에서 30분→15분 통일 |
| C4 | Progressive Formalization | pg: 3 Level / pgf SKILL.md: 5 Scale (Level 1-3 + Large + Multi-agent) | pg는 3 Level만 정의, pgf가 확장. 이 관계 명시 필요 |

---

## Cycle 1: 수정 결과

| # | Issue | Fix | File | Status |
|---|-------|-----|------|--------|
| C1/F2/F3 | `pending` vs `designing` 불일치 | `pending` → `designing` 전수 치환 (7건) | workplan-reference.md | done |
| P2/C3 | 원자 노드 30분 vs 15분 | 30분→15분 통일, 50줄→"참고 지표"로 약화 | pg/SKILL.md | done |
| P3 | done/in-progress 실행 규칙 혼란 | done="건너뜀", in-progress="실행"으로 분리 | pg/SKILL.md | done |
| P4 | pg 정체성 설명 부족 | 서두에 정체성 문단 추가 (DSL 정의, 용도, 소통 언어) | pg/SKILL.md | done |
| F6 | design --analyze 모드 수 혼란 | "(design의 하위 옵션)" 명시 | pgf/SKILL.md | done |
| P1 | 50줄 기준 | P2와 함께 "참고 지표"로 약화 | pg/SKILL.md | done |
| F1 | SKILL.md bash 명령 오류 | 사용자 환경 의존 — 별도 작업 필요 | - | deferred |
| F4 | 상태 코드 총 수 혼란 | pending 제거로 해결 (pg 6 + pgf 3 = 9) | - | resolved by C1 |

### 수정된 파일

1. `pg/SKILL.md` — 정체성 문단, 상태코드 규칙, 원자 노드 시간 통일 (3건)
2. `pgf/workplan-reference.md` — pending→designing 치환 (7건)
3. `pgf/SKILL.md` — design --analyze 하위 옵션 명시 (1건)

---

## Cycle 2: 재검증

Cycle 1 수정 후 재분석:

| Check | Result |
|-------|--------|
| `pending` 잔여 | 0건 ✓ |
| `30분` 잔여 | 0건 ✓ |
| done 상태코드 "건너뜀" 반영 | 확인 ✓ |
| pg 서두 정체성 문단 | 확인 ✓ |
| design --analyze 하위 옵션 표시 | 확인 ✓ |

**Cycle 2 판정: passed** — 새로운 이슈 없음.

### Deferred

| # | Issue | Reason |
|---|-------|--------|
| F1 | SKILL.md bash 명령 오류 (`$$` 이스케이프) | PowerShell 환경에서 `!command` 실행 방식 자체의 구조적 문제. 사용자 환경 설정에 의존하므로 별도 작업 필요 |

---

## 최종 결과

- **분석 이슈**: pg 6건 + pgf 7건 + 교차 4건 = 총 17건
- **수정 완료**: 11건 (3개 파일, 11개 변경)
- **Skip**: 4건 (기존 설명 충분 또는 자연스러운 확장 관계)
- **Deferred**: 1건 (F1 — 환경 의존)
- **Auto-resolved**: 1건 (F4 — C1 수정으로 해결)

---

## Cycle 3: pgf 모드 정규화

### 신규 모드 추가

| Mode | Reference | Purpose |
|------|-----------|---------|
| `review` | `review-reference.md` | 기존 산출물 면밀 검토·수정·재검증 반복 |
| `evolve` | `evolve-reference.md` | 자기진화 사이클 (gap 발견→설계→구현→검증→기록) |

### 변경 사항

| File | Change |
|------|--------|
| `pgf/review-reference.md` | 신규 생성 — 5축 분석, 우선순위, Convergence Loop |
| `pgf/evolve-reference.md` | 신규 생성 — 6단계 사이클, 안정화 감지, POLICY |
| `pgf/SKILL.md` | v2.4→v2.5, 모드 테이블에 review/evolve 추가, 레퍼런스 테이블에 참조 추가 |

### 검증

- review-reference.md 존재 ✓
- evolve-reference.md 존재 ✓
- SKILL.md 모드 테이블에 등록 ✓
- SKILL.md 레퍼런스 테이블에 참조 ✓
- 버전 v2.5 ✓

**PGF v2.5 — 11개 실행 모드 (design, design --analyze, plan, execute, full-cycle, loop, discover, create, micro, delegate, review, evolve)**

