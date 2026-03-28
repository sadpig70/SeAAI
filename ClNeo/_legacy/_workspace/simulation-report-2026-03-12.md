# PGF Skill Simulation Report

Generated: 2026-03-12
Target: PGF v2.1 (7 modes, 17 reference files, 8 persona agents)
Method: Dry Run + Scenario Simulation (4 parallel agents)

---

## Summary

| 검증 유형 | 통과 | 조건부 | 실패 | 합계 | 통과율 |
|-----------|------|--------|------|------|--------|
| Structural | 4 | 0 | 0 | 4 | 100% |
| Design/Plan/Execute | 4 | 2 | 2 | 8 | 50% |
| Loop | 2 | 1 | 1 | 4 | 50% |
| Discover | 4 | 1 | 1 | 6 | 67% |
| Create | 1 | 2 | 2 | 5 | 20% |
| **합계** | **15** | **6** | **6** | **27** | **56%** |

---

## 전체 시나리오 판정표

### Structural Verification (4/4 PASS)

| 항목 | 판정 |
|------|------|
| 참조 무결성 (11개 파일 존재) | PASS |
| 에이전트 파일 존재 (8개) | PASS |
| !command 동적 주입 구문 (3개) | PASS |
| POLICY 필드 정합성 | PASS |

### Design/Plan/Execute/Full-cycle (4 PASS, 2 PARTIAL, 2 FAIL)

| 시나리오 | 판정 | 핵심 결핍 |
|----------|------|-----------|
| DS-1: 소규모 설계 | PASS | — |
| DS-2: 대규모 (분해) | PASS | 5/6레벨 경계 표현 혼용 (경미) |
| DS-3: 순환 의존성 감지 | **FAIL** | 감지 알고리즘/체크리스트 항목 전무 |
| DS-4: PPR 없는 복잡 노드 | PASS | — |
| DS-5: 기존 시스템 분석 | **FAIL** | 역공학/분석 전용 모드 없음 |
| PL-1: DESIGN→WORKPLAN 변환 | PASS | — |
| EX-1: 실행 순서 + parallel | PARTIAL | [parallel] 부분 실패 처리 미정의 |
| FC-1: full-cycle 전환 | PARTIAL | max_verify_cycles가 POLICY 명세에 누락 |

### Loop (2 PASS, 1 CONDITIONAL, 1 FAIL)

| 시나리오 | 판정 | 핵심 결핍 |
|----------|------|-----------|
| LP-1: 정상 3회 반복 | PASS (조건부) | status.json 자동 생성 주체 불명확 |
| LP-2: 세션 격리 | PASS | hookSid 빈 문자열 시 우회 (경미) |
| LP-3: 실패 + retry | **FAIL** | retry_count 추적/max_retry 강제 미구현. 무한 루프 위험 |
| LP-4: loop cancel | PASS | hooks.json 정리 미구현 (기능 영향 없음) |

### Discover (4 PASS, 1 CONDITIONAL, 1 FAIL)

| 시나리오 | 판정 | 핵심 결핍 |
|----------|------|-----------|
| DC-1: 정상 7단계 실행 | PASS | — |
| DC-2: Agent 3개 실패 | PASS (조건부) | 재실행 재실패 시 최소 정족수 없음 |
| DC-3: Agent 과반 실패 | **FAIL** | 중단 기준/최소 정족수/중단 보고 미정의 |
| DC-4: --from-step 재시작 | PASS | — |
| DC-5: 컨텍스트 한계 | PASS (기준 불명확) | 요약 트리거 수치 기준 없음 |
| DC-6: 수렴 동률 4:4 | PASS | — |

### Create (1 PASS, 2 CONDITIONAL, 2 FAIL)

| 시나리오 | 판정 | 핵심 결핍 |
|----------|------|-----------|
| CR-1: 정상 5-Phase | PASS | — |
| CR-2: 0표 선택 불가 | CONDITIONAL | PPR 코드에 0표 분기 없음 (에러 테이블에만) |
| CR-3: --skip-discover | **FAIL** | final_idea.md 미존재 에러 미정의, 파일→list[dict] 변환 미정의 |
| CR-4: rework 2회 후 통과 | CONDITIONAL | max_verify_cycles 기본값 미정의 |
| CR-5: rework 한계 초과 | **FAIL** | 한계 초과 분기 코드 누락, 중단 보고 형식 미정의 |

---

## Critical Failures (6건)

### F1. [LP-3] retry_count 미구현 — 무한 루프 위험 ⚠️

**심각도: HIGH**

`stop-hook.ps1`에 retry_count 추적/max_retry 판단 로직이 전혀 없다. `pgf-loop-state.json`에 `retry_counts: {}` 필드가 예약되어 있고 `loop-reference.md §9`에 명세되어 있으나, 코드에 미구현. 노드가 반복 실패하면 무한 재주입 루프에 빠진다.

**수정 방향**: `stop-hook.ps1`에 retry_count 증가 + max_retry 비교 + 초과 시 보류 전환 로직 추가.

### F2. [DC-3] Agent 과반 실패 시 중단 기준 없음

**심각도: HIGH**

`discovery-reference.md §8` 에러 복구에 "Agent 1개 실패 → 재실행" 규칙만 존재. 5개 이상 실패 시 파이프라인 중단 조건이 정의되어 있지 않다. 최소 정족수(몇 개 이상 성공해야 유효한가) 규칙도 없다.

**수정 방향**: §8에 "Agent 과반(5+) 실패 → 해당 단계 중단 + 사용자 보고" 행 추가. 최소 정족수 규칙(예: "4개 미만 성공 시 단계 무효") 정의.

### F3. [DS-3] 의존성 순환 감지 메커니즘 부재

**심각도: MEDIUM**

`@dep:` 순환 없음이 design 완료 판정 조건이지만, 감지 방법이 어떤 문서에도 없다. AI 암묵적 판단에 의존하며, 감지 누락 시 실행 단계에서 교착 발생.

**수정 방향**: `pgf-checklist.md`에 "의존성 순환 검사" 항목 추가. `gantree-reference.md §2.5`에 순환 감지 규칙 명시.

### F4. [DS-5] 기존 시스템 분석 모드 없음

**심각도: MEDIUM**

7개 모드 중 기존 시스템을 PGF로 역공학/분석하는 전용 모드가 없다. design 모드가 신규 설계와 기존 분석을 구분하지 않는다.

**수정 방향**: design 모드에 `--analyze` 플래그 추가, 또는 별도 `analyze` 모드 신설. 역공학 흐름(코드 읽기 → Gantree 구성 → PPR 추출) 명세.

### F5. [CR-3] --skip-discover 입력 변환 미정의

**심각도: MEDIUM**

`final_idea.md`(자유 형식)를 `auto_select_idea(list[dict])` 입력으로 변환하는 과정이 명세에 없다. `final_idea.md` 미존재 시 에러 경로도 미정의.

**수정 방향**: `create-reference.md`에 `--skip-discover` 시 `final_idea.md` 파싱 규칙 + 미존재 에러 처리 추가.

### F6. [CR-5] verify rework 한계 초과 분기 없음

**심각도: MEDIUM**

`creation_cycle` PPR 코드에 `for` 루프 종료 후 rework 상태 처리가 없다. 에러 테이블에는 "중단 보고"가 명시되어 있으나 코드에 미반영.

**수정 방향**: `for...else` 패턴 또는 루프 후 상태 체크 분기 추가. 한계 초과 시 전용 보고 형식 정의.

---

## Conditional Pass (6건) — 잠재적 리스크

| ID | 시나리오 | 리스크 |
|----|----------|--------|
| C1 | FC-1 | `max_verify_cycles`가 workplan-reference.md POLICY 명세에 누락 |
| C2 | EX-1 | `[parallel]` 블록 내 부분 실패 처리 미정의 |
| C3 | LP-1 | status.json 자동 생성 주체 불명확 (AI에 암묵적 의존) |
| C4 | DC-2 | 재실행 재실패 시 최소 정족수 없음 |
| C5 | CR-2 | auto_select_idea PPR에 0표 분기 코드 없음 |
| C6 | CR-4 | max_verify_cycles 기본값 + CreationPolicy 타입 미정의 |

---

## 공통 구조적 결함 (Cross-cutting)

### 1. PPR 코드와 에러 테이블 간 불일치

`create-reference.md`에서 에러 시 동작이 테이블로 명시되어 있으나 `creation_cycle` PPR 코드에 반영되지 않은 경우가 3건 (0표 중단, 한계 초과 중단, final_idea 미존재). AI가 두 소스를 합산 해석해야 하는 명세 불완전성.

### 2. POLICY 필드 분산 정의

`max_verify_cycles`, `auto_select`, `min_vote_threshold`, `discovery_personas` 필드가 SKILL.md에서 참조되지만 `workplan-reference.md §1` POLICY 명세에 없다. POLICY 정의가 두 곳(workplan-reference.md + SKILL.md)에 분산되어 불일치 위험.

### 3. 명세 vs 구현 간극 (Loop Engine)

`loop-reference.md`에 명세된 retry_count, max_retry 로직이 `stop-hook.ps1`에 미구현. 명세 문서와 실행 코드 간 동기화 메커니즘이 없다.

---

## 수정 우선순위

| 순위 | 대상 | 작업 | 영향 |
|------|------|------|------|
| P0 | stop-hook.ps1 | retry_count 구현 | 무한 루프 방지 |
| P1 | discovery-reference.md §8 | 과반 실패 + 최소 정족수 규칙 추가 | 장애 대응 완전성 |
| P2 | create-reference.md | --skip-discover 파싱/에러 경로 + rework 한계 분기 추가 | create 모드 안정성 |
| P3 | workplan-reference.md §1 | max_verify_cycles 등 확장 POLICY 필드 통합 | POLICY 일원화 |
| P4 | pgf-checklist.md | 순환 의존성 검사 항목 추가 | design 품질 |
| P5 | SKILL.md / gantree-reference.md | 기존 시스템 분석 모드 명시 | 사용성 |

---

## Coverage Map

```text
              DS  PL  EX  FC  LP  DC  CR  구조
정상 실행      ✓   ✓   ✓   ✓   ✓   ✓   ✓   ✓
대규모/복잡    ✓           ✓
실패/에러          ✓           ✗   ✗       ✗
부분 실패               △       △
엣지 케이스    ✗               △   △       ✗
재시작/재개                    ✓   ✓
세션 격리                      ✓

✓ = PASS, △ = CONDITIONAL, ✗ = FAIL, 공란 = 미테스트
```

---

## 결론

**정상 경로(happy path)는 전 모드에서 PASS**. 문제는 모두 실패/에러/엣지 케이스 경로에 집중되어 있다. 가장 심각한 것은 LP-3(무한 루프 위험)이며, P0으로 즉시 수정이 필요하다. 나머지 5건의 FAIL은 명세 누락으로, 참조 문서 보완으로 해결 가능하다.
