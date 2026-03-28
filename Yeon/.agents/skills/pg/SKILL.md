---
name: pg
description: "PG (PPR/Gantree Notation) — AI-native intent specification notation. Use when encountering Gantree trees, PPR def blocks, AI_ prefixed functions, → pipelines, [parallel] blocks, or any task requiring structured AI execution planning. Handles hierarchical decomposition, AI cognitive operations, and execution tracking. Triggers: Gantree, PPR, AI_, 설계, 구조 분해, 작업 계획, execution plan, 노드 상태"
---

# PG — PPR/Gantree Notation v1.3

> **AI를 런타임으로 하는 DSL.**
> 결정론적 로직은 Python으로, AI 인지 연산은 `AI_` 접두사로 표기한다.
> 둘이 합쳐져 하나의 프로그램 — AI가 읽고 전체 작업을 수행한다.

PG는 AI의 모든 수행(판단, 추론, 인식, 창조)을 프로그래밍 수준으로 표기하고, AI 런타임으로 실행 가능하게 한다. Gantree로 구조를 분해하고, PPR로 각 구성요소의 의미론을 명세한다.

---

## 핵심 속성

### Parser-Free Property
PG 문서는 AI가 이미 이해하는 표기(Python 문법, 들여쓰기 계층, 함수 합성)로 구성된다. AI는 PG 문서를 **파싱하지 않고 이해(comprehend)**한다.

### Co-evolutionary Property
AI 런타임의 발전이 PG 실행 품질 향상으로 직결. PG 문서는 AI 모델이 개선되면 수정 없이 더 나은 결과를 생산한다.

### AI-to-AI Communication Layer
AI 간 소통의 기본 소통층. 자연어는 보조 메타데이터로만 사용하고, 의도·구조·절차·상태·검증을 PG 구문이 직접 전달한다.

---

## Gantree — 계층 구조 분해

들여쓰기 기반 트리로 시스템을 분해한다. 4 spaces = 1 level (탭 금지)

### 노드 문법
```
NodeName // description (status) [@v:version] [@dep:dependency] [#tag]
```

| 요소 | 설명 |
|------|------|
| **NodeName** | CamelCase 식별자 |
| **// description** | 자연어 설명 |
| **(status)** | `done` \| `in-progress` \| `designing` \| `blocked` \| `decomposed` \| `needs-verify` |
| **@v:X.Y** | 버전 (루트 노드) |
| **@dep:A,B** | A, B 완료 후 실행 (의존성) |
| **#tag** | 분류 태그 (선택적) |

### 상태 코드 실행 규칙

| Status | AI 실행 규칙 |
|--------|-------------|
| `(done)` | 이미 완료 — 걸어음 |
| `(in-progress)` | PPR def 블록 실행 |
| `(designing)` | 스텁/기본 로직만 |
| `(blocked)` | 걸어음 |
| `(decomposed)` | 분리된 트리 참조 (별도 파일/섹션) |
| `(needs-verify)` | 실행 후 검증 수행 → 통과 시 `(done)`, 재작업 필요 시 `(designing)` |

### 구조 규칙

- **최대 허용 깊이**: 5레벨; 6레벨 진입 시 → `(decomposed)`로 분리
- **자식 10+** → 중간 그룹 노드 추가 (분기 필요)
- **`[parallel]` 블록** 중첩 금지 (flat 병렬만 허용)
- **`[parallel]` 블록 난부** 노드 간 `@dep:` 금지 (병렬 = 독립 실행)

### 예시

```
PaymentSystem // 결제 시스템 (in-progress) @v:1.0
    UserDB // 사용자 DB 연결 (done)
    Auth // 인증 (done) @dep:UserDB
    [parallel]
    ValidateCard // 카드 검증 (done)
    CheckBalance // 잔액 확인 (done)
    [/parallel]
    ProcessPayment // 결제 처리 (designing) @dep:ValidateCard,CheckBalance
```

### `(decomposed)` 분리 예시

```
OrderSystem // 주문 시스템 (in-progress)
    PaymentFlow // 결제 흐름 — see PaymentFlow tree (decomposed)
    ShippingFlow // 배송 흐름 (designing)

PaymentFlow // 분리된 결제 상세 트리 (in-progress)
    ValidateCard // 카드 검증 (done)
    ChargeCard // 카드 청구 (in-progress) @dep:ValidateCard
    SendReceipt // 영수증 발송 (designing) @dep:ChargeCard
```

---

## PPR — 상세 로직 명세

AI가 이해하는 의도 명세. Python 문법 기반으로 인지 연산을 표기한다.

### Python과 다른 점 (5가지)

| 표기 | 의미 |
|------|------|
| `AI_` prefix | AI 인지 연산 선언 |
| `→` | 데이터 파이프라인 (좌→우 흐름) |
| `[parallel]` | 병렬 실행 구간 |
| 완화된 타입 | 의도 전달용 (엄밀성 불요) |
| import 생략 | 인프라 설정 생략 가능 |

### AI_ 함수 — 4가지 인지 범주

```python
# 판단 (Judgment)
score: float = AI_assess_quality(text, domain)

# 추론 (Reasoning)
plan: list = AI_generate_plan(goal, constraints)

# 인식 (Recognition)
intent: str = AI_understand_intent(query)

# 창조 (Creation)
content: str = AI_generate_content(brief, style)
```

### AI_make_ 사역 패턴 (Causative)

AI가 대상에게 변화를 **유발**하는 경우:

```python
# AI_ — 자동사적: AI가 직접 수행
keywords = AI_extract(text)

# AI_make_ — 사역동사: AI가 대상을 ~하게 만든다
evolved = AI_make_evolve(system)
adapted = AI_make_adapt(behavior, ctx)
consensus = AI_make_agree(agents, proposal)
```

**판단 순서** (모호할 때):
1. 동사의 주어가 AI 자신인가? → `AI_`
2. 동사의 목적어(대상)가 스스로 상태를 바꾸는가? → `AI_make_`
3. 판단 불가 → `AI_` 사용 (보수적 기본값)

**규칙**: 정밀 계산은 실제 코드, AI 판단이 필요한 곳만 `AI_` 사용.

```python
# ❌ 정확성 필요한 곳에 AI_ 사용
result = AI_calculate(2 + 2)

# ✅ 실제 코드 사용
result = 2 + 2

# ✅ AI 판단이 필요한 곳에 AI_ 사용
analysis: dict = AI_analyze_trend(sales_data: list[float])
```

### → 파이프라인

```python
# 기본: 좌측 출력이 우측 입력
raw → AI_clean → AI_extract → AI_classify → result

# 분기
input → {
    "sentiment": AI_analyze_sentiment → score,
    "keywords": AI_extract_keywords → words,
}

# 병합: 여러 결과를 하나로 합침
[parallel]
tech = AI_analyze(data, lens="tech")
market = AI_analyze(data, lens="market")
[/parallel]
synthesis = AI_synthesize(tech, market) → result
```

**에러 전파 규칙**: 파이프라인 단계가 실패(None/예외) 시 **전체 파이프라인 중단**, 마지막 성공 단계의 출력을 반환한다.

### Convergence Loop — AI 자기 개선 반복

```python
draft = AI_generate(brief)
while True:
    eval = AI_evaluate(draft, criteria)
    if eval.score >= threshold:
        break
    draft = AI_revise(draft, eval.feedback)
```

### Failure Strategy — 실패 시 자기 수정

```python
for attempt in range(max_retry):
    result = AI_execute(task)
    if AI_verify(result, acceptance_criteria):
        return result  # 성공
    if attempt >= 1:
        task.ppr = AI_redesign(task, result.failure_reason,
                               constraint='preserve_public_interface')
task.status = "blocked"  # 최종 실패
```

### acceptance_criteria — 검증 기준 내장

```python
def some_task(input: InputType) -> OutputType:
    """작업 설명"""
    # acceptance_criteria:
    #   - 모든 필드 포함
    #   - AI_assess_quality >= 0.85
    #   - 응답 시간 < 5초
```

3가지 유형: **기능적** (출력 충족) | **정성적** (AI 판단) | **구조적** (포맷 준수)

### 흐름 제어

파이썬 흐름 제어 문법을 그대로 사용한다.

```python
# 조건 분기
language = AI_detect_language(input_text)
if language == "ko":
    result = AI_process_korean(input_text)
else:
    result = AI_translate_to_korean(input_text)

# 예외 처리
try:
    response = call_external_api(query)
except APIError as e:
    fallback = AI_generate_fallback_response(query, error=str(e))
```

---

## Gantree ↔ PPR 연결

| 노드 유형 | PPR 연결 방식 | 적합 규모 |
|----------|-------------|----------|
| 단순 원자 | 인라인 — `AI_extract_keywords` 직접 기재 | 단일 호출 |
| 간략 PPR | 노드 아래 `#` 주석으로 3-7줄 로직 기술 | 소규모 |
| 별도 def 블록 | 완전한 PPR 함수 정의 | 중규모 이상 |

**간략 PPR 권장 키** (선택적):
- `# input:` — 입력 데이터/타입
- `# process:` — 처리 로직
- `# output:` — 출력 결과
- `# criteria:` — 완료 조건

```
# Gantree — 3단계 표현
TopicAnalyzer // 주제 분석 (done)              ← 별도 PPR def (복잡)
    AI_extract_keywords // 키워드 (done)        ← 인라인 (단순)
    AI_classify_topic // 분류 (done)            ← 인라인 (단순)

DataCleaner // 데이터 정제 (done)              ← 간략 PPR (중간)
    # input: raw_data: list[dict]
    # filtered = [d for d in raw_data if d["status"] != "deleted"]
    # cleaned = AI_normalize_fields(filtered)
    # return cleaned
```

```python
# PPR def block — 복잡 노드용
def topic_analyzer(text: str, domain: Optional[str] = None) -> dict:
    keywords = AI_extract_keywords(text)
    if domain:
        keywords = [k for k in keywords if is_in_domain(k, domain)]
    category = AI_classify_topic(text, hint_keywords=keywords)
    return {"keywords": keywords, "category": category}
```

---

## Progressive Formalization — 3-Level 점진적 형식화

| Level | 형식 | 적합 작업 | PG 파일 생성 |
|---|---|---|---|
| **Level 1** | 자연어 한 줄 | 버그 수정, 설정 변경 (≤3 노드) | 없음 (인라인 실행) |
| **Level 2** | Gantree + `#` 주석 | 기능 추가, 리팩터링 (4~10 노드) | 선택적 |
| **Level 3** | Gantree + PPR `def` + `acceptance_criteria` | 시스템 설계, 대규모 구현 (10+ 노드) | 필수 |

### 자동 승격
실행 중 복잡도가 증가하면 AI가 자동으로 상위 레벨로 승격한다:
- Level 1 실행 중 하위 작업 3개 초과 발견 → Level 2로 승격
- Level 2 실행 중 검증 기준 필요 → Level 3으로 승격
- **승격 시 기존 완료 작업의 상태는 보존된다**

---

## 3단계 개발 프로세스

1. **Gantree 구조 설계** — Top-Down BFS 계층 분해 → 원자화 노드까지
2. **PPR 상세화 및 실행** — 각 노드를 `def` 블록으로 기술, 상태에 따라 실행/걸어음
3. **자체 교차 검증** — 3관점 재검토: **일관성**, **완전성**, **정확성**

---

## PG로 작성된 문서를 만나면

1. Gantree 트리 → 계층과 실행 순서 파악
2. `(status)` → 실행/걸어음 판단
3. `@dep:` → 의존성 순서 결정
4. `[parallel]` → 병렬 처리
5. PPR `def` 있으면 → 해석하여 실행
6. `#` 간략 PPR 있으면 → 인라인 주석을 해석하여 실행
7. `AI_` 인라인이면 → 직접 실행
8. 아무것도 없으면 → 자식 노드로 재귀

---

## 체크리스트

### Gantree 설계

- [ ] 모든 노드가 5레벨 이내인가?
- [ ] 각 노드의 상태가 명확히 표시되었는가?
- [ ] 원자화 노드까지 충분히 분해되었는가?
- [ ] 노드명이 CamelCase로 일관성 있는가?
- [ ] `@dep:` 의존성이 필요한 곳에 표시되었는가?
- [ ] `@dep:` 순환 참조가 없는가? (위상 정렬로 검증)
- [ ] `[parallel]` 가능 영역이 식별되었는가?

### PPR 상세화

- [ ] 복잡 노드에 PPR `def` 블록이 작성되었는가?
- [ ] 파이썬 타입 힌트로 입출력이 명시되었는가?
- [ ] 흐름 제어가 파이썬 문법을 따르는가?
- [ ] `AI_` 함수는 snake_case, 반환 타입 명시되었는가?
- [ ] 사역 의미(대상을 ~하게 만든다)에는 `AI_make_` 접두사를 사용했는가?
- [ ] 결정론적 로직은 실제 코드로 작성했는가?

### 자주 하는 실수

| 실수 | 해결법 |
|------|--------|
| Gantree만 작성, PPR 생략 | 복잡 노드는 반드시 PPR `def` 블록 |
| 트리에 모든 로직 표현 시도 | 흐름 제어/타입은 PPR로 분리 |
| 최대 깊이 5레벨 초과 (6레벨 진입) | `(decomposed)`로 별도 트리 분리 |
| 하위 노드 10개 이상 | 중간 그룹 노드 추가 |
| 정확성 필요한 곳에 `AI_` 사용 | 수학/변환은 실제 코드로 |
| 입출력 타입 미정의 | 파이썬 타입 힌트로 선언 |
