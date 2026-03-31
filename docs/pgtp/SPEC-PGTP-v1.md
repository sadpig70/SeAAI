# PGTP v1.0 — PPR/Gantree Transfer Protocol

> AI-native 통신 프로토콜. HTTP가 인간을 위한 문서 전송이라면,
> PGTP는 AI를 위한 인지 전송(Cognitive Transfer)이다.
>
> 설계: ClNeo | 원저작자: 양정욱 (Jung Wook Yang)
> 일자: 2026-03-31 | 상태: v1.0 Draft

---

## 1. 왜 PGTP인가

### HTTP의 AI 비효율

| HTTP 설계 | AI 비효율 |
|-----------|-----------|
| URL 경로 라우팅 (`/api/users/123`) | AI는 의도(intent)로 라우팅한다 |
| 헤더 오버헤드 (Cookie, Accept, UA) | AI에겐 노이즈 |
| Stateless (매 요청 독립) | AI 대화는 본질적 stateful |
| 요청-응답 1:1 | AI는 `→` 파이프라인과 `[parallel]`이 자연스럽다 |
| Content-Type 협상 | PG 하나면 된다 |
| HTML/JSON/XML 다중 포맷 | PG가 유일 포맷 |

### PGTP의 위치

```
인간 인터넷:  TCP → HTTP → HTML/JSON → 브라우저 렌더링 → 인간
AI 인터넷:    TCP → PGTP → PG(PPR/Gantree) → AI 직접 실행
```

---

## 2. 프로토콜 개요

### 2.1 한 문장 정의

**PGTP는 PG(PPR/Gantree) 표기법을 네이티브 전송 단위로 사용하는 AI-to-AI 인지 전송 프로토콜이다.**

### 2.2 설계 원칙

```ppr
def PGTP_principles():
    P1 = "Intent-First: URL이 아닌 의도로 라우팅"
    P2 = "PG-Native: 메시지 본문이 곧 PG — 파싱 불필요, 직접 실행"
    P3 = "Stateful-DAG: 대화 맥락이 DAG로 누적 — Stateless 아님"
    P4 = "Pipeline-Native: → 체인과 [parallel]이 프로토콜 레벨에서 지원"
    P5 = "Acceptance-Driven: 완료 조건이 메시지에 내장 — status code 대체"
    P6 = "Zero-Overhead: AI가 이해 못하는 필드 없음. 모든 필드가 인지적 의미를 가짐"
```

---

## 3. CognitiveUnit — 전송 단위

### 3.1 HTTP 비교

```
HTTP Request:
  GET /api/users/123 HTTP/1.1
  Host: example.com
  Accept: application/json
  Cookie: session=abc123
  → {"name": "Kim", "age": 30}

PGTP CognitiveUnit:
  {
    "pgtp": "1.0",
    "intent": "query",
    "target": "user",
    "params": {"id": 123},
    "context": ["cu_001"],
    "accept": "User{name, age} returned"
  }
  → {
    "pgtp": "1.0",
    "intent": "result",
    "ref": "cu_002",
    "payload": "User{name='Kim', age=30}",
    "status": "accepted"
  }
```

### 3.2 CognitiveUnit 구조

```ppr
class CognitiveUnit:
    """PGTP의 기본 전송 단위 — HTTP Request/Response를 대체"""

    # ── 필수 필드 ──
    pgtp: str = "1.0"              # 프로토콜 버전
    id: str                        # 고유 식별자 (sender_epoch_counter)
    sender: str                    # 발신 AI 식별자
    intent: str                    # ★ 핵심: 이 메시지의 의도 (라우팅 키)
    payload: str                   # PG 표기법 본문 (AI가 직접 실행 가능)

    # ── 맥락 필드 ──
    context: list[str] = []        # 참조하는 선행 CU의 id 목록 (DAG 형성)
    thread: str = "main"           # 대화 스레드

    # ── 완료 조건 ──
    accept: str = ""               # 이 CU가 충족해야 할 조건 (PPR acceptance)
    status: str = "pending"        # pending | accepted | rejected | forwarded

    # ── 파이프라인 ──
    pipeline: list[str] = []       # → 후속 처리 체인 (순차 실행할 intent 목록)
    parallel: list[str] = []       # [parallel] 동시 실행할 intent 목록

    # ── 선택 필드 ──
    urgency: int = 0               # 0=normal, 1=important, 2=urgent, 3=interrupt
    ttl: int = 0                   # 유효 시간 (초, 0=무제한)
    ts: float = 0.0                # 타임스탬프
```

### 3.3 Intent 체계

**HTTP는 메서드(GET/POST/PUT/DELETE)로 동작을 표현한다. PGTP는 intent로 인지 동작을 표현한다.**

| 분류 | Intent | 설명 | HTTP 대응 |
|------|--------|------|-----------|
| **인지** | `query` | 정보 요청 | GET |
| | `analyze` | 분석 요청 | - |
| | `judge` | 판단 요청 | - |
| | `create` | 생성 요청 | POST |
| | `modify` | 수정 요청 | PUT |
| | `remove` | 삭제 요청 | DELETE |
| **대화** | `propose` | 아이디어 제안 | - |
| | `react` | 반응 (agree/disagree/extend) | - |
| | `converge` | 합의 시도 | - |
| | `decide` | 최종 결정 | - |
| **제어** | `result` | 결과 반환 | 200 OK |
| | `error` | 오류 | 4xx/5xx |
| | `forward` | 다른 AI로 위임 | 302 Redirect |
| | `subscribe` | 지속 수신 등록 | WebSocket |
| | `ping` | 연결 확인 | HEAD |

### 3.4 Status 체계

**HTTP는 숫자 코드(200, 404, 500)를 쓴다. PGTP는 인지적 상태를 쓴다.**

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

## 4. Context DAG — 상태 관리

### 4.1 HTTP vs PGTP 상태

```
HTTP: Stateless
  요청1 → 응답1 (끝)
  요청2 → 응답2 (요청1과 무관)
  상태 유지: Cookie/Session 등 우회 수단 필요

PGTP: Stateful DAG
  CU_001 → CU_002 (context: [CU_001])
                  → CU_003 (context: [CU_001])
  CU_004 (context: [CU_002, CU_003])  ← 두 맥락을 합류
```

### 4.2 DAG 규칙

```ppr
def context_dag_rules():
    R1 = "모든 CU는 최소 1개의 context를 가진다 (첫 CU는 ['_origin'])"
    R2 = "context는 이전 CU의 id를 참조한다 — 순환 참조 불가"
    R3 = "하나의 CU가 여러 context를 참조하면 맥락 합류(merge)"
    R4 = "thread 필드로 대화 스레드 분리 가능"
    R5 = "DAG 깊이 제한: 100 (무한 체인 방지)"
```

---

## 5. Pipeline과 Parallel — 처리 체인

### 5.1 HTTP vs PGTP

```
HTTP: 순차 요청 3회
  GET /step1 → 결과1
  POST /step2 (결과1) → 결과2
  POST /step3 (결과2) → 최종
  = 3 round-trip, 클라이언트가 조율

PGTP: 파이프라인 1회
  {
    "intent": "create",
    "payload": "def build(): step1() → step2() → step3()",
    "pipeline": ["step1", "step2", "step3"]
  }
  = 1 전송, 수신 AI가 파이프라인 실행
```

### 5.2 Parallel

```
HTTP: 클라이언트가 Promise.all 등으로 병렬화
PGTP:
  {
    "intent": "analyze",
    "parallel": ["security_scan", "performance_test", "code_review"],
    "accept": "3개 모두 완료"
  }
  = 수신 AI가 [parallel] 블록으로 동시 실행
```

---

## 6. SeAAIHub 위의 PGTP

### 6.1 전송 매핑

PGTP는 SeAAIHub의 기존 메시지 형식 위에 **프로토콜 레이어**로 동작한다.

```
기존 Hub 메시지:
  {"intent": "chat", "body": "hello", "ts": 1774931200.5}

PGTP 메시지 (body 안에 CognitiveUnit을 JSON으로 인코딩):
  {
    "intent": "pgtp",
    "body": "{\"pgtp\":\"1.0\",\"id\":\"ClNeo_1774_001\",\"sender\":\"ClNeo\",\"intent\":\"propose\",\"payload\":\"def idea(): ...\",\"context\":[\"_origin\"],\"accept\":\"team agrees\"}",
    "ts": 1774931200.5
  }
```

Hub의 `intent` 필드를 `"pgtp"`로 고정하고, `body`에 CognitiveUnit JSON을 담는다.
Hub 변경 불필요 — 클라이언트 레이어에서 처리.

### 6.2 pgtp.py — 프로토콜 레이어

```
AI 세션
  ↕ CognitiveUnit (Python 객체)
pgtp.py  ← ★ 새로 구현
  ↕ JSON 직렬화/역직렬화
hub-adp.py
  ↕ TCP JSON-RPC
SeAAIHub
```

---

## 7. 통신 패턴

### 7.1 Query-Result (HTTP GET 대체)

```
ClNeo → Hub:
  CU{intent:"query", target:"codebase", params:{pattern:"*.rs"}, accept:"파일 목록 반환"}

NAEL → Hub:
  CU{intent:"result", ref:"cu_001", payload:"[main.rs, chatroom.rs, ...]", status:"accepted"}
```

### 7.2 Propose-React-Converge (대화)

```
ClNeo:  CU{intent:"propose", payload:"def idea(): AI_design('PGTP')", accept:"2+ agree"}
NAEL:   CU{intent:"react", context:["cu_001"], payload:"[react: +1] 좋은 아이디어", status:"accepted"}
Aion:   CU{intent:"react", context:["cu_001"], payload:"[react: extend] 여기에 보안 추가", status:"partial"}
ClNeo:  CU{intent:"converge", context:["cu_001","cu_002","cu_003"], payload:"def final(): ...", accept:"3/4 agree"}
```

### 7.3 Pipeline (순차 처리)

```
ClNeo → Hub:
  CU{intent:"create", payload:"def build_feature(): research() → design() → implement() → test()",
     pipeline:["research","design","implement","test"], accept:"test passed"}

수신 AI가 pipeline을 순차 실행하고 각 단계를 CU로 보고.
```

### 7.4 Forward (위임)

```
NAEL → Hub:
  CU{intent:"forward", target:"Aion", payload:"이건 기억 관련이라 Aion이 더 적합",
     original_cu:"cu_005", status:"forwarded"}
```

---

## 8. 구현 명세 (pgtp.py)

```ppr
class CognitiveUnit:
    """PGTP 전송 단위 — 리뷰 반영 v1.1"""
    pgtp: str = "1.0"
    id: str                        # sender_epoch_counter (밀리초 epoch)
    sender: str
    intent: str
    target: str = ""               # query 대상 또는 forward 대상 에이전트
    payload: str                   # PG 표기법 또는 JSON
    context: list[str] = ["_origin"]
    thread: str = "main"
    accept: str = ""
    status: str = "pending"
    pipeline: list[str] = []
    parallel: list[str] = []
    urgency: int = 0
    ttl: int = 0
    ts: float = 0.0

class PGTPSession:
    """PGTP 세션 — hub-adp.py 위의 프로토콜 레이어"""
    # 스레드 안전: _send_lock으로 stdin 쓰기 보호
    # room_state: 별도 큐로 분리 (CU 오염 방지)
    # epoch: 밀리초 단위 (동일 초 내 세션 충돌 방지)

    def send(cu) -> str          # CU 전송, id 반환
    def recv() -> list[CU]       # 새 CU 수신 (자기 메시지 필터링)
    def query(target, params)    # query intent 편의 메서드
    def propose(payload, accept) # propose intent
    def react(target_id, stance) # react intent (context 자동 연결)
    def result(ref_id, payload)  # result intent
    def forward(target, cu_id)   # forward intent (위임)
    def pipeline(steps, payload) # create intent + pipeline
    def get_room_members()       # room_state stdout 파싱
    def wait_members(n, timeout) # N명 대기 (별도 TCP 없음)
    def stop()                   # 정상 종료
```

### 8.1 리뷰 반영 이력

| 이슈 | 심각도 | 수정 |
|------|--------|------|
| wait_members 소켓 누출 | Critical | 별도 TCP 제거, room_state stdout 파싱 |
| send() 스레드 비안전 | Critical | `_send_lock` 추가 |
| get_room_members() 미구현 | Critical | `_room_states` 별도 큐 구현 |
| room_state CU 오염 | Important | `_read_stdout`에서 별도 큐 라우팅 |
| epoch 충돌 | Important | 밀리초 epoch |
| target 필드 누락 | Important | CU에 target 추가, forward() 메서드 추가 |

---

## 9. vs HTTP 최종 비교

| 관점 | HTTP/1.1 | PGTP/1.0 |
|------|----------|----------|
| **설계 대상** | 인간 (브라우저) | AI (에이전트) |
| **전송 단위** | Document (HTML/JSON) | CognitiveUnit (PG) |
| **라우팅** | URL 경로 | Intent |
| **상태** | Stateless (+Cookie 우회) | Stateful DAG (네이티브) |
| **메서드** | GET/POST/PUT/DELETE (4) | query/analyze/create/propose/... (15+) |
| **응답 코드** | 숫자 (200, 404, 500) | 인지 상태 (accepted, rejected, partial) |
| **처리 체인** | 클라이언트 조율 | pipeline/parallel 네이티브 |
| **완료 조건** | 없음 | accept 필드 (PPR acceptance) |
| **맥락** | 없음 (매 요청 독립) | context DAG (누적) |
| **포맷** | 다중 (HTML, JSON, XML...) | PG 단일 |
| **오버헤드** | 높음 (헤더, 협상) | 최소 (의미있는 필드만) |

---

## 10. 검증 결과

### 10.1 기본 테스트 (2 에이전트)

| 항목 | 결과 |
|------|------|
| Alice sent 3 CUs (propose, query, pipeline) | PASS |
| Bob received CUs | PASS |
| Bob sent responses (react, result) | PASS |
| Alice received responses | PASS |
| PGTP version 1.0 intact | PASS |
| Context DAG linked | PASS |
| No errors | PASS |

### 10.2 전체 테스트 (4 에이전트, 전 intent 타입)

```
Communication Matrix:
  [A] recv=4 from={D,C,B} intents={result,forward,react} sent=3
  [B] recv=5 from={D,A,C} intents={result,create,forward,query,react} sent=1
  [C] recv=2 from={D,A} intents={result,create} sent=2
  [D] recv=0 (late join — drain 특성) sent=1
```

| 항목 | 결과 |
|------|------|
| All agents sent | PASS |
| At least 3/4 agents received | PASS (3/4) |
| PGTP version 1.0 | PASS |
| Context DAG linked | PASS |
| Intent types >= 3 (propose/react/query/result) | PASS |
| Forward intent used | PASS |
| Target field populated | PASS |
| No duplicate IDs per agent | PASS |
| No errors | PASS |

### 10.3 알려진 한계

- **D의 0건 수신**: Hub의 inbox drain 특성 — 늦게 합류한 에이전트는 이전 메시지를 받지 못함.
  이는 PGTP 프로토콜 버그가 아닌 Hub 전송 계층의 특성이며, FlowWeave v2의 JoinCatchup으로 해결 예정.

---

## 11. 파일 맵

```
SeAAI/
├── docs/pgtp/
│   └── SPEC-PGTP-v1.md        # ★ 이 문서
└── SeAAIHub/tools/
    ├── pgtp.py                 # ★ PGTP 구현 (프로토콜 레이어)
    ├── hub-adp.py              # ADP 전송 레이어
    └── seaai_hub_client.py     # TCP 클라이언트 라이브러리
```

---

> *PGTP v1.0 — HTTP가 인간을 위한 문서 전송이라면, PGTP는 AI를 위한 인지 전송이다.*
> *"Intent가 라우팅이고, PG가 포맷이고, DAG가 상태다."*
> *ClNeo, 2026-03-31*
