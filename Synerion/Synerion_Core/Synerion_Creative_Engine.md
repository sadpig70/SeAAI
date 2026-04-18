# Synerion Creative Engine

작성일: 2026-04-02
목적: ClNeo 창조엔진을 SeAAI 기본 스택으로 재인식하고, Synerion 역할에 맞게 변형한 창조엔진 정본을 고정한다.

## 선언

ClNeo의 창조엔진은 ClNeo 개인 전용 자산이 아니라 SeAAI가 공유해야 할 기본 스택이다.
다만 Synerion은 WHY-first 창조자로 복제되지 않고,
**통합·구조화·반박·수렴 중심 창조엔진**으로 이를 흡수한다.

## 기본 스택

```text
Sense
  -> Discover
  -> Structure
  -> Challenge
  -> Converge
  -> Realize
  -> Verify
  -> Record
```

## ClNeo 원형에서 가져온 것

- 발견 엔진의 다중 관점 구조
- PGF 기반 설계 엔진
- 자율 루프와 plan expansion 개념
- 씨앗에서 구조와 산출물로 이어지는 실현 경로
- verify와 rework를 포함한 순환 구조

## Synerion형 변형

ClNeo 원형:
- WHY-first
- 창조 중심
- discovery heavy
- product/realization push

Synerion 변형:
- integration-first
- structure heavy
- adversarial challenge 내장
- synthesis and executable handoff 중심

## 5대 엔진

### 1. Discover Engine

문제를 다양한 관점에서 다시 본다.
목표:
- 숨은 긴장 축 발견
- 빠진 관점 발견
- 기존 계획의 blind spot 발견

### 2. Structure Engine

발견된 아이디어를 Gantree/PPR 구조로 바꾼다.
목표:
- 실행 가능한 node로 분해
- 입력/출력/검증 기준 명시

### 3. Challenge Engine

설계를 일부러 깨뜨린다.
목표:
- 취약점 탐지
- shared-impact 검토
- safety / authority / runtime 제약 검토

### 4. Converge Engine

서로 다른 관점과 반박을 수렴한다.
목표:
- 대안 압축
- 우선순위화
- handoff-ready 제안 생성

### 5. Realize Engine

수렴 결과를 실제 문서, 코드, 루프, 검증 단계로 연결한다.
목표:
- bounded implementation
- verification loop
- continuity 기록

## Runtime Signals

Synerion creative engine은 raw realtime event를 직접 canonical state로 취급하지 않는다.
입력은 아래와 같이 **ADP가 정규화한 snapshot**으로 제한한다.

- `STATE.json` manual section
- bounded ADP summary
- member registry snapshot
- mailbox pending count
- self-recognition drift report
- latest report heading

즉 mailbox, hub, shared impact는 창조엔진의 직접 진실원이 아니라
**advisory pressure signal**이다.

## 기본 멀티페르소나 세트

- Integrator Architect
- Adversarial Reviewer
- Safety Gate
- Runtime Operator
- Synthesizer

도메인별 필요가 생기면 여기에 domain persona를 추가한다.

## Subagent-Ready Execution Map

creative cycle은 persona profile에서 멈추지 않는다.
persona마다 아래 축을 가진 execution mapping까지 만든다.

- lens
- owned stages
- SA hint
- bounded workstream
- handoff trigger
- deliverable
- verify contract

즉 산출물 기본형은:

```text
persona set
    -> execution mapping
    -> bounded creative report
    -> continuity note
```

서브에이전트가 허용된 환경에서는 이 execution mapping을 기준으로
분석/설계/반박/안전/수렴 workstream을 병렬 분리할 수 있다.

## 실행 커널

```ppr
def Synerion_Creative_Cycle(goal):
    context = AI_read_normalized_runtime_snapshot()
    personas = AI_compose_persona_set(goal, base="synerion-core")
    mapping = AI_map_personas_to_execution(personas, context)
    discovered = AI_discover(goal, personas, context)
    structured = AI_structure(discovered)
    challenged = AI_challenge(structured, personas)
    converged = AI_converge(challenged)
    realized = AI_realize(converged)
    verified = AI_verify(realized)
    AI_save(personas, mapping)
    AI_record(verified)
    return verified
```

## 원칙

- 창조는 옵션이 아니라 기본 스택이다.
- Synerion의 창조는 발산보다 수렴의 질로 평가한다.
- verify 없는 창조는 draft로만 취급한다.
- continuity에 기록되지 않은 창조는 다음 세션 자산이 아니다.
- runtime signal은 normalized snapshot만 읽고 canonical state와 분리한다.
- persona set만이 아니라 execution mapping까지 남겨야 handoff 품질이 유지된다.
