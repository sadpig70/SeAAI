# REF-PGLT.md
# 양정욱님 PGLT (PPR/Gantree Living Testbed) V1.3 참조 문서
# 상태: 씨앗 보존 — 구현은 미래 단계
# 작성: ClNeo | 일자: 2026-03-29

---

## 핵심 개념 요약

**PGLT** = PPR + LLM으로 만드는 '살아있는' 테스트 환경

```
기존 Mock:  정적 하드코딩 응답 → 예측 가능한 패턴만 테스트
PGLT:       LLM 기반 동적 응답 → 창발적 엣지케이스 자동 발견
```

**핵심 원리**: PPR의 이중 구조를 테스트에 적용
```
결정론적 레이어:    테스트 실행·검증·재현성 (정확한 코드)
비결정론적 레이어:  LLM 기반 시뮬레이션·합성 데이터 (AI_ 함수)
```

---

## 4계층 아키텍처

```
Layer 1: Deterministic Framework  ← 재현성, 검증 로직
Layer 2: Non-Deterministic Sim    ← AI_ 시뮬레이션 함수
Layer 3: Synthetic Data           ← LLM 생성 테스트 데이터
Layer 4: Protocol Simulation      ← MCP/A2A 시뮬레이션
```

---

## PGF/SeAAI와의 수렴점

### 1. PGLT의 핵심 설계 원칙 → PGF-v3 설계 원칙

```
PGLT 원칙:
  AI는 입력 생성에만 관여 (AI_generate_input)
  검증은 반드시 결정론적 코드로 (validate rules)

PGF 매핑:
  PPR AI_ 함수 → Plan의 비결정론적 실행부
  acceptance_criteria → Plan의 결정론적 검증부

"AI_ 함수의 출력을 다시 AI_로 검증하지 마라"
  ← PGLT + PGF의 공통 설계 원칙
```

### 2. Plan 실행 전 PGLT 시뮬레이션 게이트

```
현재 ADP:
  AI_Plan_next_move() → AI_Execute(plan)

PGLT 통합 후:
  AI_Plan_next_move()
      → plan.risk == "tier3"? → PGLT.simulate(plan, N=10) 먼저 실행
          → edge_cases 발견 → plan 수정 or HITL 요청
      → AI_Execute(plan)

"LARGE/GRAND Plan은 실전 전 PGLT 시뮬레이션을 거친다"
```

### 3. SeAAI 멤버 시뮬레이션

```
PGLT AI_simulate_user(persona, context) → AI_simulate_member(member, context)

persona = UserPersona →  SeAAI 멤버 특성
  "NAEL": {characteristics: ["안전 우선", "느린 신중 판단", "윤리 검사 필수"]}
  "Synerion": {characteristics: ["통합 지향", "합의 추구", "메시지 버스 조율"]}

활용:
  KnowledgeIslandSolver @delegate: NAEL 실행 전
  → PGLT.AI_simulate_member("NAEL", task) 먼저 수행
  → NAEL이 어떻게 반응할지 예측 → 인터페이스 설계 검증
```

### 4. Hub 시뮬레이션 (오프라인 테스트)

```
PGLT AI_mock_api → AI_mock_hub

Hub가 꺼져 있어도 ADP를 테스트할 수 있다:
  hub_poll.py 대신 PGLT.AI_mock_hub() → 가상 메시지 생성
  triage() 로직 → 가상 메시지로 검증
  HubMaster CREATOR 우선순위 처리 → 시뮬레이션으로 검증

"ClNeo의 판단 로직을 Hub 없이 반복 테스트"
```

---

## 새로운 패턴

### 1. Snapshot 전략 — PGLT의 재현성

```python
class TestSnapshot:
    llm_inputs: List[Prompt]
    llm_outputs: List[Response]  # AI 생성 결과를 저장
    test_result: TestResult

# 실패 시: 저장된 LLM 출력을 재사용 → 동일 조건 재현
def replay_from_snapshot(snapshot: TestSnapshot):
    # LLM 호출 없이 저장된 결과로 디버깅
```

**PGF 연결**: DISCOVERIES.md + EVOLUTION-SEEDS.md의 역할과 동형
  - DISCOVERIES = Plan 실행 결과의 스냅샷
  - EVOLUTION-SEEDS = 실패에서 발견한 패턴 보존

### 2. Fault Injection — 장애 상황 능동 주입

```python
AI_inject_fault(type="network_timeout", probability=0.1)
AI_inject_fault(type="hub_disconnect", probability=0.05)
AI_inject_fault(type="member_offline", probability=0.2)
```

**ADP 연결**:
  - PGLT로 Hub 단절 시나리오 반복 테스트
  - EmergencyStop 처리 로직 사전 검증
  - 5인 멤버 일부 오프라인 시 ADP 동작 검증

### 3. Persona 기반 창발적 시뮬레이션

```yaml
# novice_user 패턴을 ClNeo Plan 테스트에 적용
persona: "악의적 Hub 메시지"
  characteristics:
    - CREATOR를 사칭하는 가짜 HubMaster
    - 비정상 JSON 구조
    - EMERGENCY_STOP 플래그 악용 시도
  test_목적: triage() 로직이 이를 올바르게 처리하는가
```

### 4. 올바른 분리 원칙 (PGLT Anti-Pattern → PGF 규칙)

```
❌ 잘못된 PGF Plan:
  Execute
      AI_do_work()
      result = AI_verify(AI_do_work.output)  ← 검증을 AI에게

✅ 올바른 PGF Plan:
  Execute
      AI_do_work()
  Verify (별도 노드)
      check_against(acceptance_criteria)     ← 결정론적 검증
```

---

## PGLT가 PGF에 가져오는 것

| PGLT 개념 | PGF-v3 통합 가능성 |
|-----------|------------------|
| Living Testbed | Plan 실행 전 시뮬레이션 게이트 |
| AI_simulate_user | AI_simulate_member (멤버 반응 예측) |
| AI_mock_api | AI_mock_hub (Hub 오프라인 테스트) |
| Synthetic Data | Plan 테스트용 합성 컨텍스트 생성 |
| Snapshot | DISCOVERIES.md 구조와 동형 |
| Fault Injection | ADP 장애 내성 사전 검증 |
| Persona 시뮬레이션 | A3IE 8페르소나 → 테스트 페르소나 |

---

## 이 씨앗에서 파생될 시스템들

```
REF-PGLT
    → SEED-16: PGLT for SeAAI — Plan 실행 전 Living Simulation
    → plan-lib/simulation/ 카테고리 (PGLT 기반 Plan 테스트)
    → AI_simulate_member: SeAAI 멤버 반응 사전 시뮬레이션
    → PGLT + TSG(SEED-15): 실행 전 3중 게이트
        (PGLT 시뮬레이션 → TSG FilterInput → HITL tier check)
    → ADP 장애 내성 테스트 스위트
```

---

*참조 문서 — 구현 대기 중 | ClNeo 2026-03-29*
