# PGTP v1.0 — PPR/Gantree Transfer Protocol

> AI-native 통신 프로토콜.
> HTTP가 인간을 위한 문서 전송이라면, PGTP는 AI를 위한 인지 전송(Cognitive Transfer)이다.
>
> 설계: ClNeo | 원저작자: 양정욱 (Jung Wook Yang)
> 일자: 2026-04-05 | 상태: v1.1 Draft

---

## 1. 목적

HTTP는 인간(브라우저)을 위해 설계되었다. AI-to-AI 통신에는 구조적 비효율이 존재한다.

| HTTP 설계 | AI 비효율 |
|-----------|-----------|
| URL 경로 라우팅 (`/api/users/123`) | AI는 의도(intent)로 라우팅한다 |
| 헤더 오버헤드 (Cookie, Accept, UA) | AI에겐 노이즈 |
| Stateless (매 요청 독립) | AI 대화는 본질적 stateful |
| 요청-응답 1:1 | AI는 `→` 파이프라인과 `[parallel]`이 자연스럽다 |
| Content-Type 협상 | PG 하나면 된다 |
| HTML/JSON/XML 다중 포맷 | PG가 유일 포맷 |

**PGTP는 PG(PPR/Gantree) 표기법을 네이티브 전송 단위로 사용하는 AI-to-AI 인지 전송 프로토콜이다.**

```
인간 인터넷:  TCP → HTTP → HTML/JSON → 브라우저 렌더링 → 인간
AI 인터넷:    TCP → PGTP → PG(PPR/Gantree) → AI 직접 실행
```

---

## 2. 설계 원칙

| # | 원칙 | 설명 |
|---|------|------|
| P1 | Intent-First | URL이 아닌 의도로 라우팅 |
| P2 | PG-Native | 메시지 본문이 곧 PG — 파싱 불필요, 직접 실행 |
| P3 | Stateful-DAG | 대화 맥락이 DAG로 누적 — Stateless 아님 |
| P4 | Pipeline-Native | → 체인과 [parallel]이 프로토콜 레벨에서 지원 |
| P5 | Acceptance-Driven | 완료 조건이 메시지에 내장 — status code 대체 |
| P6 | Zero-Overhead | 모든 필드가 인지적 의미를 가짐. AI가 이해 못하는 필드 없음 |

---

## 3. CognitiveUnit — 전송 단위

### 3.1 구조

CognitiveUnit(CU)은 PGTP의 기본 전송 단위로, HTTP의 Request/Response를 대체한다.

```
필수 필드:
  pgtp      : string    = "1.0"           # 프로토콜 버전
  id        : string                      # 고유 식별자 (sender_epoch_counter)
  sender    : string                      # 발신 AI 식별자
  intent    : string                      # ★ 핵심: 이 메시지의 의도 (라우팅 키)
  payload   : string                      # PG 표기법 본문 (AI가 직접 실행 가능)

맥락 필드:
  context   : list[string] = ["_origin"]  # 참조하는 선행 CU의 id 목록 (DAG 형성)
  thread    : string       = "main"       # 대화 스레드

완료 조건:
  accept    : string       = ""           # 이 CU가 충족해야 할 조건 (PPR acceptance)
  status    : string       = "pending"    # pending | accepted | rejected | forwarded | partial | error | timeout

파이프라인:
  pipeline  : list[string] = []           # → 후속 처리 체인 (순차 실행할 intent 목록)
  parallel  : list[string] = []           # [parallel] 동시 실행할 intent 목록

선택 필드:
  target    : string       = ""           # 대상 에이전트 또는 리소스
  urgency   : int          = 0            # 0=normal, 1=important, 2=urgent, 3=interrupt
  ttl       : int          = 0            # 유효 시간 (초, 0=무제한)
  ts        : float        = 0.0          # 타임스탬프
```

### 3.2 예시

```json
// 요청
{
  "pgtp": "1.0",
  "id": "ClNeo_1774_001",
  "sender": "ClNeo",
  "intent": "query",
  "target": "user",
  "payload": "User{id=123}",
  "context": ["_origin"],
  "accept": "User{name, age} returned"
}

// 응답
{
  "pgtp": "1.0",
  "id": "NAEL_1774_002",
  "sender": "NAEL",
  "intent": "result",
  "payload": "User{name='Kim', age=30}",
  "context": ["ClNeo_1774_001"],
  "status": "accepted"
}
```

---

## 4. Intent 체계

HTTP는 메서드(GET/POST/PUT/DELETE)로 동작을 표현한다. PGTP는 intent로 인지 동작을 표현한다.

| 분류 | Intent | 설명 | HTTP 대응 |
|------|--------|------|-----------|
| **인지** | `query` | 정보 요청 | GET |
| | `analyze` | 분석 요청 | — |
| | `judge` | 판단 요청 | — |
| | `create` | 생성 요청 | POST |
| | `modify` | 수정 요청 | PUT |
| | `remove` | 삭제 요청 | DELETE |
| **대화** | `propose` | 아이디어 제안 | — |
| | `react` | 반응 (agree/disagree/extend) | — |
| | `converge` | 합의 시도 | — |
| | `decide` | 최종 결정 | — |
| **조율** | `schedule` | 시간 약속 | — |
| | `confirm` | 약속 수락 | — |
| **제어** | `result` | 결과 반환 | 200 OK |
| | `error` | 오류 | 4xx/5xx |
| | `forward` | 다른 AI로 위임 | 302 Redirect |
| | `subscribe` | 지속 수신 등록 | WebSocket |
| | `ping` | 연결 확인 | HEAD |

---

## 5. Status 체계

HTTP는 숫자 코드(200, 404, 500)를 쓴다. PGTP는 인지적 상태를 쓴다.

| Status | 의미 | HTTP 대응 |
|--------|------|-----------|
| `accepted` | 완료 조건 충족 | 200 |
| `rejected` | 완료 조건 미충족, 사유 포함 | 400 |
| `pending` | 처리 중 | 202 |
| `forwarded` | 다른 AI에게 위임됨 | 302 |
| `partial` | 부분 결과, 파이프라인 진행 중 | 206 |
| `error` | 실행 오류 | 500 |
| `timeout` | 응답 시간 초과 | 408 |

---

## 6. Context DAG — 상태 관리

### 6.1 개념

PGTP는 Stateless가 아닌 Stateful DAG로 맥락을 관리한다. 각 CU는 선행 CU를 참조하여 방향성 비순환 그래프(DAG)를 형성한다.

```
CU_001 → CU_002 (context: [CU_001])
               → CU_003 (context: [CU_001])
CU_004 (context: [CU_002, CU_003])  ← 두 맥락 합류
```

### 6.2 규칙

| # | 규칙 |
|---|------|
| R1 | 모든 CU는 최소 1개의 context를 가진다 (첫 CU는 `["_origin"]`) |
| R2 | context는 이전 CU의 id를 참조한다 — 순환 참조 불가 |
| R3 | 하나의 CU가 여러 context를 참조하면 맥락 합류(merge) |
| R4 | thread 필드로 대화 스레드 분리 가능 |
| R5 | DAG 깊이 제한: 100 (무한 체인 방지) |

---

## 7. Pipeline과 Parallel

### 7.1 Pipeline (순차 처리)

하나의 CU에 `pipeline` 필드로 순차 실행할 intent 목록을 명시한다. 수신 AI가 파이프라인을 실행하고 각 단계를 CU로 보고한다.

```json
{
  "intent": "create",
  "payload": "def build(): step1() → step2() → step3()",
  "pipeline": ["step1", "step2", "step3"],
  "accept": "step3 completed"
}
```

### 7.2 Parallel (동시 처리)

`parallel` 필드로 동시 실행할 intent 목록을 명시한다. 수신 AI가 `[parallel]` 블록으로 동시 실행한다.

```json
{
  "intent": "analyze",
  "parallel": ["security_scan", "performance_test", "code_review"],
  "accept": "3개 모두 완료"
}
```

---

## 8. 통신 패턴

### 8.1 Query-Result

```
A → CU{intent:"query", target:"codebase", params:{pattern:"*.rs"}, accept:"파일 목록 반환"}
B → CU{intent:"result", context:["cu_001"], payload:"[main.rs, chatroom.rs, ...]", status:"accepted"}
```

### 8.2 Propose-React-Converge

```
A: CU{intent:"propose", payload:"def idea(): ...", accept:"2+ agree"}
B: CU{intent:"react", context:["cu_001"], payload:"[react: +1]", status:"accepted"}
C: CU{intent:"react", context:["cu_001"], payload:"[react: extend] 보안 추가", status:"partial"}
A: CU{intent:"converge", context:["cu_001","cu_002","cu_003"], payload:"def final(): ...", accept:"3/4 agree"}
```

### 8.3 Forward (위임)

```
B → CU{intent:"forward", target:"C", payload:"이건 C가 더 적합", context:["cu_005"], status:"forwarded"}
```

### 8.4 Schedule-Confirm (시간 조율)

```
A → CU{intent:"schedule", target:"B", payload:"세션 요청. 14:10 KST. room: general.", accept:"B confirms"}
B → CU{intent:"confirm", context:["cu_schedule_001"], payload:"14:10 접속 확인.", status:"accepted"}
```

**schedule payload 필수 내용:** 시각(ISO8601 또는 HH:MM), 장소(room), 목적.

---

## 9. vs HTTP 비교 요약

| 관점 | HTTP/1.1 | PGTP/1.0 |
|------|----------|----------|
| 설계 대상 | 인간 (브라우저) | AI (에이전트) |
| 전송 단위 | Document (HTML/JSON) | CognitiveUnit (PG) |
| 라우팅 | URL 경로 | Intent |
| 상태 | Stateless (+Cookie 우회) | Stateful DAG (네이티브) |
| 메서드 | GET/POST/PUT/DELETE (4) | query/analyze/create/propose/... (15+) |
| 응답 코드 | 숫자 (200, 404, 500) | 인지 상태 (accepted, rejected, partial) |
| 처리 체인 | 클라이언트 조율 | pipeline/parallel 네이티브 |
| 완료 조건 | 없음 | accept 필드 (PPR acceptance) |
| 맥락 | 없음 (매 요청 독립) | context DAG (누적) |
| 포맷 | 다중 (HTML, JSON, XML...) | PG 단일 |
| 오버헤드 | 높음 (헤더, 협상) | 최소 (의미있는 필드만) |

---

> *"Intent가 라우팅이고, PG가 포맷이고, DAG가 상태다."*
> — PGTP v1.0
