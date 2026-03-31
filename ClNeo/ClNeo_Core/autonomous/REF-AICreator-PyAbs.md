# REF-AICreator-PyAbs.md
# 양정욱님 AI Creator + PyAbs 시스템 스케치 참조 문서
# 상태: 씨앗 보존 — 구현은 미래 단계
# 작성: ClNeo | 일자: 2026-03-29

---

## 핵심 개념 요약

### AI Creator
- **목표**: AI 시스템을 표준화된 원자 객체로 분해·재조합하는 메타 시스템
- **π=1 원칙**: 모든 객체는 스케일/환경에 종속되지 않는 정규화된 인터페이스 보유
- **3단계 계층**:
  ```
  Level 0: Basic Atoms    (AI_activate, AI_normalize, AI_weight_adjust ...)
  Level 1: Composite Atoms (AI_Layer, AI_Dataset, AI_Attention_Mechanism ...)
  Level 2: Functional Modules (Intent_Interpreter, Inference_Engine ...)
  ```
- **자동 코드 생성**: 객체 조합 → Python/C++ 코드 자동 생성
- **자기진화**: AI_self_diagnose + AI_evolve_architecture

### PyAbs (Python Abstraction)
- π=1 정규화 기반
- ML, UI/UX, 멀티미디어, 네트워크를 동일한 추상화 레이어로 표현
- AI Creator 생태계에서 동적 시스템 조립 가능

---

## PGF와의 수렴점 (오늘 발견)

```
AI Creator Level 0 (Basic Atoms)
    ↔ PGF ATOM 스케일 Plan
    ↔ PPR AI_ 함수 (AI_triage, AI_compose, AI_diagnose ...)

AI Creator Level 1 (Composite Atoms)
    ↔ PGF SMALL/MEDIUM Plan
    ↔ plan-lib/discovery/A3IE.md, CrossDomainMapping.md ...

AI Creator Level 2 (Functional Modules)
    ↔ PGF LARGE/GRAND Plan
    ↔ plan-lib/grand-challenge/KnowledgeIslandSolver.md

AI Creator 정규화 인터페이스
    ↔ PGF @input/@output 타입 시그니처
    ↔ PLAN-INDEX.md 헤더의 sig: 필드

π=1 정규화
    ↔ PGF의 스케일 독립 @input/@output
    ↔ "Plan의 크기는 문제의 크기" — 인터페이스는 동일

Code Generation Engine
    ↔ PGF @expand — Gantree → 실행 코드 전개
    ↔ AI_Execute(plan_impl, context)

AI Creator 자기진화
    ↔ PlanLibExpand + IndexRebuild
    ↔ CapabilityExpand + SeedEvolution
```

---

## π=1 원칙의 PGF 적용 방향 (미래 설계 씨앗)

현재 PGF `@input/@output`은 타입만 선언한다.
π=1을 적용하면:

```
# 현재 (타입만)
@input:  problem (string), knowledge_base (DocSet)
@output: insights (InsightSet), seeds (SeedList)

# π=1 적용 후 (정규화 명세 포함)
@input:
    problem:        string[normalized, domain-agnostic]
    knowledge_base: DocSet[π=1, scale-invariant]
@output:
    insights:  InsightSet[ranked, 0~1 normalized score]
    seeds:     SeedList[π=1, transferable-across-domains]

# 최종 출력 단계에서만 실제 값으로 역정규화
@denormalize_at: Output node
```

이것이 구현되면 Plan 객체들이 도메인·스케일에 관계없이
완전히 재조합 가능해진다. AI Creator의 완전 구현.

---

## 구현 필요 자원 (양정욱님 메모)

- 현재 단계: 개념 완성, 설계 스케치 보존
- 구현 조건: 충분한 연산 자원, 전용 런타임 환경
- 우선순위: SeAAI 생태계 안정화 이후

---

## 이 씨앗에서 파생될 시스템들

```
REF-AICreator-PyAbs
    → PGF-v3: π=1 정규화 인터페이스 통합
    → AICreator-PlanLib: 자동 코드 생성 + Plan 조합
    → PyAbs-PGF: Python 추상화 레이어 위의 PGF
    → SeAAI-AICreator: 5인 SeAAI가 AI Creator를 분산 실행
        Aion      → 기존 시스템 기억·인덱싱
        ClNeo     → 원자 발견·설계
        NAEL      → 윤리 검사·안전 검증
        Synerion  → 모듈 조합·통합 오케스트레이션
        Yeon      → 도메인 간 번역·연결
```

---

## 추가 스케치 (2026-03-29) — PyAbsAI Gantree 3개 모듈

### 새로 발견한 패턴 (PGF에 아직 없는 것들)

**1. `@id` 노드 주소 시스템**
```
AI_evolve_architecture @id:EvolveArch [PyAbsAI:Evolution, PPR:AI_evolve_architecture]
```
모든 노드가 고유 ID를 가진다. 이 ID로:
- 크로스 파일 직접 참조 (`@ref: EvolveArch`)
- 실행 상태 추적 (`status[EvolveArch] = done`)
- 결과 캐싱 (`cache[EvolveArch] = result`)
- 의존성 그래프 구축

PGF에 통합 시: `NodeName @id:UniqueID` 추가
→ status.json이 ID 기반 인덱스로 진화 가능

**2. `HITL:AI_authorize` — Human In The Loop 마커**
```
Ethics_Guardian @id:EthicsGuard [PyAbsAI:AI_ethical_check, HITL:AI_authorize]
```
특정 노드는 AI 자율 실행 불가 — 인간 승인 필요.
PGF의 "되돌릴 수 없는 작업 확인" 원칙과 동일하지만
**노드 레벨에서 명시적으로 선언**된다.

PGF에 통합 시:
```
NodeName @id:X [HITL:creator | HITL:any_member | HITL:none]
```
→ AI_Execute()가 HITL 체크 후 실행

**3. Verification_Testing = First-Class 독립 모듈**
단순한 "verify 단계"가 아니라 완전한 독립 모듈:
```
Verification_Testing
    AI_Test_Evolution    // 진화 결과 단위 테스트
    AI_Benchmark         // 성능 벤치마크
    Ethics_Guardian      // 윤리 검증
```
모든 Functional Module이 자신의 검증 모듈을 포함한다.

PGF에 통합 시: plan-lib/verification/ 카테고리 추가
→ 모든 MEDIUM+ Plan이 @verify 블록을 필수로 가짐

**4. 멀티태그 어노테이션 시스템**
```
[PyAbsAI:Evolution, PPR:AI_evolve_architecture]
```
노드가 속한 라이브러리 + 실행할 PPR 함수를 동시 선언.
PGF @id + 태그 시스템으로 진화 가능:
```
NodeName @id:X @lib:PyAbsAI @ppr:AI_evolve_architecture @hitl:none
```

### 3개 모듈 요약

| 모듈 | 핵심 | PGF 대응 |
|------|------|----------|
| Self_Generating_Evolution | π=1 + AI_evolve_architecture | PlanLibExpand + SelfEvolveLoop |
| InPprSys_Integration | π=1 + 영구 메모리 + VectorDB | SCS + DISCOVERIES.md |
| Verification_Testing | π=1 + 단위테스트 + 벤치마크 | plan-lib/verification/ (미구현) |

### π=1 정규화 코드 패턴 (씨앗)
```python
def pi_normalized(self, value):
    return value / np.pi  # 모든 값을 π 기준으로 정규화

# 의미: 어떤 스케일의 값도 동일한 0~1/π 범위로 정규화
# 역정규화: value * np.pi (출력 단계에서만)
```
PGF @input/@output에 이것을 적용하면:
"어떤 도메인의 Plan도 동일한 인터페이스로 연결 가능"

---

*참조 문서 — 구현 대기 중 | ClNeo 2026-03-29*
