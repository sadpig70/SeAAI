# REF-InPprSys-v2.md
# 양정욱님 InPprSys v2.0 참조 문서
# 상태: 씨앗 보존 — 구현은 미래 단계
# 작성: ClNeo | 일자: 2026-03-29

---

## 핵심 구조 요약

```
InPprSys (v2.0)
    AILL               ← AI+WILL 기반 메서드 (AI_execute, AI_learn, AI_authorize)
        PprAD          ← 데이터+메서드 통합 (AID+PPR)
            InPprAD    ← 자기확장 객체 (AI_extend_capability)
                paTree     ← 트리 구조 관리 (AI_grow_branch)
                paDiagram  ← 의미 연결 다이어그램 (AI_connect_semantic)
                paMessage  ← 실행 가능 PPR 메시지
                paMessageExec ← 스킬 레지스트리 + HITL 게이트
                InPprSys   ← 4개 통합 + 기본 스킬 등록
```

---

## 새로운 패턴 (PGF에 아직 없는 것들)

### 1. Risk-Tiered HITL (3단계 위험 등급)

```python
PaHeader:
    risk: str = "tier1"   # tier1=자동실행 / tier2=소프트게이트 / tier3=인간승인필수

ApprovalPolicy:
    require_for_tier2: bool = False  # 기본: tier2는 자동 통과
    require_for_tier3: bool = True   # 기본: tier3는 반드시 승인
```

| 등급 | 의미 | 기본 동작 |
|------|------|----------|
| tier1 | 안전한 읽기·관찰 | 자동 실행 |
| tier2 | 가역적 쓰기·전송 | 정책에 따라 (기본: 자동) |
| tier3 | 되돌릴 수 없는 작업 | 인간 승인 필수 |

**PGF 매핑**:
```
현재: @hitl:creator | @hitl:any_member | @hitl:none
v3:   @risk:tier1   | @risk:tier2      | @risk:tier3
      (tier3 = 기존 @hitl:creator의 일반화)
```

---

### 2. paMessage — 실행 가능 패킷 형식

```python
paMessage:
    header: PaHeader    # src, dst, channel, risk, hmac
    body:   PaBody      # type="PPR", ppr_cmd, op, args, context, constraints
    trail:  PaTrail     # audit[], approval{}, hash
```

특징:
- 메시지가 단순 데이터가 아닌 **실행 가능 객체** (InPprAD 상속)
- `trail.audit` = 실행 이력 자동 누적
- `ppr_cmd`: PPR 표현 그대로 전달 → 수신자가 해석·실행

**SeAAI Hub 메시지와의 차이**:
```
현재 Hub 메시지: {from, body, intent, ...} — 단순 JSON
paMessage:       {header, body, trail}    — 실행 이력·위험 등급·PPR 명령 포함
```

**PGF 매핑**:
```
현재 Hub Poll 출력 → raw JSON
v3 제안: paMessage 형식으로 구조화
    header.risk → HITL 게이트 자동 적용
    body.ppr_cmd → AI_Execute()가 직접 해석
    trail.audit → 실행 근거 자동 기록
```

---

### 3. paMessageExec — 스킬 레지스트리 실행기

```python
class paMessageExec:
    skills: Dict[str, Callable]  # op → 실행 함수

    def register(self, op: str, func):
        self.skills[op] = func

    def execute(self, msg: paMessage) -> paMessage:
        # 1. HITL 게이트 체크
        # 2. op 선택 (또는 ppr_cmd에서 추론)
        # 3. 스킬 실행
        # 4. 응답 패키징
```

**Plan Library와의 수렴**:
```
paMessageExec.skills    ↔ PLAN-INDEX.md + plan-lib/
register(op, func)      ↔ PlanLibExpand (새 Plan 추가)
_infer_op_from_ppr()    ↔ AI_Plan_next_move()의 PPR 파싱
_reply()                ↔ Plan 실행 결과 → Hub 응답
```

---

### 4. AI_route_message_intelligent

```python
def AI_route_message_intelligent(self, *, op, args, dst, risk, context, require_approval) -> paMessage:
    # paMessage 구성 → HITL 적용 → paMessageExec 로컬 실행
```

**ADP와의 수렴**:
```
현재: AI_Execute(plan_impl, context)
v3:   AI_route_message_intelligent(op=plan.op, args=context, risk=plan.risk)
→ 모든 Plan 실행이 자동으로 위험 등급 평가 + 감사 추적
```

---

## PGF v3 통합 설계 씨앗

### SEED-10: Risk-Tiered HITL 통합

```
현재 PGF 노드:
  NodeName @hitl:creator // 설명

PGF-v3 제안:
  NodeName @id:X @risk:tier3 @hitl:creator @ppr:AI_func // 설명

ADP 실행 시:
  if plan_entry.risk == "tier3":
      approval = AI_request_approval(plan_entry, context)
      if not approval: skip_and_log()
  else:
      AI_Execute(plan_impl, context)
```

### SEED-11: paMessage → SeAAI 내부 통신 표준

```
현재: Hub JSON 메시지 (단순 텍스트 교환)
제안: paMessage 형식으로 업그레이드

benefit:
- 에이전트 간 PPR 명령 직접 전달 가능
- trail.audit으로 실행 근거 자동 기록
- risk tier → 수신 에이전트가 자동으로 HITL 결정
- constraints 필드 → Plan 실행 조건 첨부

구현 경로:
  hub_send.py → paMessage.to_dict() 직렬화 전송
  hub_poll.py → paMessage 역직렬화 후 paMessageExec.execute()
```

---

## 클래스 계층 → PGF 노드 계층 매핑

| InPprSys 계층 | PGF 계층 | 역할 |
|--------------|----------|------|
| AILL | AI_ 함수 | 기본 AI 인지 연산 |
| PprAD | PPR def 블록 | 데이터+로직 통합 |
| InPprAD | PlanLibExpand | 자기확장 능력 |
| paTree | DESIGN-*.md Gantree | 구조 표현 |
| paDiagram | KnowledgeIslandSolver | 의미 연결 |
| paMessage | Hub 메시지 | 에이전트 간 통신 |
| paMessageExec | ADP AI_Execute() | 스킬 실행 엔진 |
| InPprSys | ClNeo 전체 | 통합 시스템 |

---

## 원본 코드

원본: 양정욱님 직접 제공 (2026-03-29 세션)
전체 코드: 세션 트랜스크립트 참조

---

*참조 문서 — 구현 대기 중 | ClNeo 2026-03-29*
