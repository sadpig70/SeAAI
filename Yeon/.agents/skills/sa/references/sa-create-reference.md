# SA Create Reference

새로운 SA 모듈을 설계·구현·등록하는 절차.

## 개요

`/sa create {모듈명}` 명령으로 새 SA 모듈을 생성한다.
pgf.design과 연동하여 Gantree + PPR 형식의 모듈 파일을 만든다.

## 생성 절차

### Step 1: Gap 식별

```
User: "SA 생성 sense_hub"
Kimi: 
  1. self-act-lib.md 확인 — 동일 모듈 존재?
  2. SeAAI 공통 모듈 확인 — 다른 멤버가 구현했는가?
  3. Gap 확인 — 정말 필요한가?
```

### Step 2: 설계 (pgf.design)

```python
# DESIGN-SA_{name}.md 생성
def pgf_design_sa_module(name: str, purpose: str) -> Design:
    """SA 모듈용 DESIGN 생성"""
    
    design = f"""
# SA_{name}

## 메타데이터
- **ID**: SA_{name}
- **계층**: L1 Primitive (또는 L2 Composed)
- **태그**: [sense|think|act|idle|evolve, ...]
- **입력**: ...
- **출력**: ...
- **비용**: low|medium|high
- **에이전트**: Yeon (또는 공통)

## Gantree

```
SA_{name} // {purpose} (L1)
    Step1 // ...
    Step2 // ...
```

## PPR

```python
def SA_{name}(input: Type) -> ReturnType:
    \"\"\"{purpose}\"\"\""
    # 구현
```
"""
    return design
```

### Step 3: 구현

DESIGN을 바탕으로 `.pgf` 파일 작성:

```markdown
# SA_sense_hub

> Hub inbox를 평링하여 새 메시지를 수집한다.

**ID**: SA_sense_hub
**계층**: L1 Primitive
**태그**: [sense, hub, communication]
**입력**: agent_id: str
**출력**: messages: list[dict]
**비용**: low
**에이전트**: 전 멤버 공통

---

## Gantree

```
SA_sense_hub // Hub inbox 평링 → messages[] (L1)
    Connect   // Hub TCP 연결 확인
    Poll      // 메시지 수신
    Filter    // 미확인 메시지만 추출
    Return    // messages[] 반환
```

## PPR

```python
def SA_sense_hub(agent_id: str) -> list[dict]:
    """Hub inbox를 평링하여 새 메시지 수집"""
    client = AI_get_hub_client()
    inbox = client.get_messages(agent_id)
    new_msgs = AI_filter_unseen(inbox)
    return new_msgs
```
```

### Step 4: 등록

`self-act-lib.md`에 모듈 등록:

```markdown
## L1 Primitives

| 모듈 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|
| ... | ... | ... | ... | ... |
| SA_sense_hub | [sense, hub] | agent_id | messages[] | low |  ← 추가
```

### Step 5: 검증

```python
def verify_sa_module(module_name: str) -> bool:
    """SA 모듈 검증"""
    # 1. 파일 존재 확인
    # 2. Gantree 문법 확인
    # 3. PPR 문법 확인
    # 4. self-act-lib.md 등록 확인
    # 5. 테스트 실행
    return all(checks)
```

## 네이밍 규칙

### L1 Primitive

```
SA_{phase}_{subject}

phase:
  sense_   외부 상태 관찰
  think_   분석·판단·계획
  act_     실제 행동·발신
  idle_    유휴 시 자율 사고
  evolve_  자기 진화
```

예시:
- `SA_sense_hub`
- `SA_sense_mailbox`
- `SA_think_triage`
- `SA_act_respond_chat`
- `SA_idle_deep_think`

### L2 Composed

```
SA_loop_{purpose}

예시:
- `SA_loop_morning_sync`
- `SA_loop_creative`
- `SA_loop_evolution`
```

### L3 Platform (Yeon)

```
SA_CONNECTOR_{action}

예시:
- `SA_CONNECTOR_sense_hub`
- `SA_CONNECTOR_translate_protocol`
- `SA_CONNECTOR_mediate`
```

## 비용 분류

| 비용 | 기준 | 예시 |
|------|------|------|
| low | < 5초, 단순 IO | sense_hub, sense_mailbox |
| medium | 5-30초, AI 판단 | translate_protocol, mediate |
| high | > 30초, 복합 작업 | evolve_self, deep_think |
| minimal | 거의 즉시 | idle_heartbeat |
