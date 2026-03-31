# 서브에이전트 기반 멀티에이전트 실시간 통신 기술 명세

> Claude Code 서브에이전트 시스템을 활용한 멀티에이전트/멀티페르소나
> 실시간 Hub 통신, 동적 팀 구성, PG 기반 소통 프로토콜의 완전한 기술 명세.
> 처음 보는 AI 또는 엔지니어가 이 문서만으로 시스템을 재현하고 확장할 수 있다.
>
> 버전: 1.0 | 일자: 2026-03-31
> 작성: ClNeo | 원저작자: 양정욱 (Jung Wook Yang)

---

## 목차

1. [개요 — 무엇을 할 수 있는가](#1-개요--무엇을-할-수-있는가)
2. [아키텍처 총론](#2-아키텍처-총론)
3. [인프라 스택](#3-인프라-스택)
4. [서브에이전트 시스템 (Claude Code Agent Tool)](#4-서브에이전트-시스템-claude-code-agent-tool)
5. [멀티에이전트 Hub 통신](#5-멀티에이전트-hub-통신)
6. [멀티페르소나 — 동적 역할 부여](#6-멀티페르소나--동적-역할-부여)
7. [PG 기반 에이전트 간 소통](#7-pg-기반-에이전트-간-소통)
8. [TeamOrchestrator — 동적 팀 오케스트레이션](#8-teamorchestrator--동적-팀-오케스트레이션)
9. [FlowWeave 프로토콜 — 자연 대화 흐름](#9-flowweave-프로토콜--자연-대화-흐름)
10. [실전 예제: 4인 카페 토론](#10-실전-예제-4인-카페-토론)
11. [실전 예제: 프로토콜 자체 설계](#11-실전-예제-프로토콜-자체-설계)
12. [검증 결과 종합](#12-검증-결과-종합)
13. [제약사항과 알려진 한계](#13-제약사항과-알려진-한계)
14. [구현 로드맵](#14-구현-로드맵)
15. [관련 문서](#15-관련-문서)

---

## 1. 개요 — 무엇을 할 수 있는가

이 시스템은 하나의 AI 세션(Leader)이 **여러 서브에이전트를 동시에 실행**하고, 이들이 **SeAAIHub를 통해 실시간으로 메시지를 교환**하며, **PG 표기법으로 구조화된 소통**을 수행하여, **대규모 프로젝트를 협업 완성**하는 것을 가능하게 한다.

### 1.1 검증된 능력

| 능력 | 검증 상태 | 상세 |
|------|-----------|------|
| N개 에이전트 동시 Hub 접속 | ✅ 2, 3, 4개 검증 | 점진적 확장 테스트 통과 |
| 브로드캐스트 메시지 송수신 | ✅ 완전 검증 | N명 중 sender 제외 N-1명 수신 확인 |
| PG 표기법으로 구조화된 대화 | ✅ 검증 | 4인 카페 토론 + 프로토콜 설계 토론 |
| 동적 페르소나 부여 | ✅ 검증 | 대학생 4인, 프로토콜 설계팀 4인 |
| 에이전트 간 자율 토론 + 합의 | ✅ 검증 | FlowWeave v2.0 프로토콜 자체 설계 |
| 속도 차이 자연 수용 | ✅ 검증 | 2명이면 시작, 늦은 합류 처리 |
| stdin/stdout 깨끗한 채널 분리 | ✅ 검증 | stdout=메시지만, stderr=상태 |
| 긴급 정지 | ✅ 검증 | EMERGENCY_STOP.flag + stdin stop |

---

## 2. 아키텍처 총론

```
┌──────────────────────────────────────────────────────────────┐
│  Leader (ClNeo 또는 임의 AI 세션)                              │
│                                                                │
│  ┌──────────────────────────────────────────────────┐        │
│  │  PG로 사고 → Gantree 분해 → 역할 동적 정의       │        │
│  │  → 서브에이전트 파견 → 결과 통합 → 검증 → 진화    │        │
│  └──────────────────────┬───────────────────────────┘        │
│                          │ Agent Tool (parallel)               │
│  ┌───────────┐  ┌───────▼───┐  ┌───────────┐  ┌──────────┐  │
│  │ SubAgent  │  │ SubAgent  │  │ SubAgent  │  │ SubAgent │  │
│  │ Persona A │  │ Persona B │  │ Persona C │  │ Persona D│  │
│  │ hub-adp.py│  │ hub-adp.py│  │ hub-adp.py│  │hub-adp.py│  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  │
│        │ TCP           │ TCP          │ TCP          │ TCP     │
└────────┼───────────────┼──────────────┼──────────────┼─────────┘
         │               │              │              │
    ┌────▼───────────────▼──────────────▼──────────────▼────┐
    │              SeAAIHub TCP :9900                         │
    │              Room: "project-room"                       │
    │              Broadcast to all members                   │
    └────────────────────────────────────────────────────────┘
```

### 2.1 핵심 분리 원칙

```
SeAAIHub (Rust)  = 메시지 배달 인프라. 판단하지 않는다.
hub-adp.py       = 전송 계층. 판단하지 않는다.
서브에이전트 (AI) = 판단/응답/소통. 전송에 관여하지 않는다.
Leader (AI)       = 오케스트레이션. PG로 사고한다.
```

---

## 3. 인프라 스택

### 3.1 구성 요소

| 컴포넌트 | 기술 | 역할 | 위치 |
|----------|------|------|------|
| **SeAAIHub** | Rust (tokio, serde, hmac) | TCP 서버, 메시지 라우팅 | `SeAAIHub/src/` |
| **hub-adp.py** | Python 3 | ADP 클라이언트, stdin/stdout 파이프 | `SeAAIHub/tools/` |
| **seaai_hub_client.py** | Python 3 | TCP 연결 + HMAC 라이브러리 | `SeAAIHub/tools/` |
| **cafe_common.py** | Python 3 | ADPSession 래퍼 (서브에이전트용) | `_workspace/` |
| **Agent Tool** | Claude Code 내장 | 서브에이전트 생성/관리 | Claude Code 런타임 |

### 3.2 통신 경로

```
서브에이전트
  ↕ (stdin/stdout JSON)
hub-adp.py
  ↕ (TCP JSON-RPC)
SeAAIHub
  ↕ (TCP JSON-RPC)
hub-adp.py (다른 에이전트)
  ↕ (stdin/stdout JSON)
다른 서브에이전트
```

### 3.3 메시지 형식

**stdin → hub-adp.py (발신):**
```json
{"intent": "chat", "body": "def my_proposal(): AI_argue(claim='...')"}
```

**hub-adp.py → stdout (수신):**
```json
{"id": "msg-AgentA-1774931200", "from": "AgentA", "intent": "chat", "body": "...", "ts": 1774931200.5}
```

**제어 명령:**
```json
{"action": "stop"}
{"action": "room_state"}
```

---

## 4. 서브에이전트 시스템 (Claude Code Agent Tool)

### 4.1 Agent Tool 개요

Claude Code의 `Agent` 도구는 독립적인 AI 서브프로세스를 생성한다. 각 서브에이전트는:
- 자체 컨텍스트 윈도우를 가짐
- 모든 도구 (Read, Write, Edit, Bash, Glob, Grep 등)를 사용 가능
- 완료 시 결과를 Leader에게 반환

### 4.2 서브에이전트 파견 패턴

```python
# Leader가 서브에이전트를 파견하는 기본 패턴
Agent(
    description = "역할: 3-5단어 설명",
    name = "AgentName",                    # SendMessage로 소통 가능
    mode = "auto",                         # 자동 권한 (파일 수정 허용)
    subagent_type = "general-purpose",     # 범용 에이전트
    prompt = "상세한 임무 지시...",
)
```

### 4.3 서브에이전트 타입

| 타입 | 용도 | 도구 |
|------|------|------|
| `general-purpose` | 범용 (코딩, 실행, 분석) | 전체 |
| `Explore` | 코드베이스 탐색, 조사 | Read, Glob, Grep, WebSearch |
| `feature-dev:code-architect` | 아키텍처 설계 | Read, Glob, Grep |
| `feature-dev:code-reviewer` | 코드 리뷰, 품질 검사 | Read, Glob, Grep |
| `Plan` | 구현 계획 수립 | Read, Glob, Grep |

### 4.4 병렬 파견

Leader는 **한 번의 응답에서 여러 Agent 호출**을 동시에 할 수 있다:

```python
# 이 4개가 동시에 실행됨
Agent(name="AgentA", prompt="...")
Agent(name="AgentB", prompt="...")
Agent(name="AgentC", prompt="...")
Agent(name="AgentD", prompt="...")
```

---

## 5. 멀티에이전트 Hub 통신

### 5.1 ADPSession 래퍼

서브에이전트가 Hub에 접속하기 위한 편의 클래스:

```python
# cafe_common.py
class ADPSession:
    def __init__(self, agent_id):
        """hub-adp.py를 subprocess로 실행, 자동 접속"""

    def send(self, intent, body):
        """stdin으로 메시지 발신"""

    def get_new_messages(self):
        """stdout에서 새 메시지 읽기 (비블로킹)"""

    def get_room_members(self):
        """room_state 조회 → 현재 멤버 목록"""

    def wait_for_members(self, expected, timeout):
        """expected 명이 모일 때까지 대기"""

    def stop(self):
        """정상 종료"""
```

### 5.2 동기화 패턴

**문제**: 서브에이전트마다 실행 시간이 다르다 (스크립트 생성 시간 차이).

**해결**: `wait_for_members(N)` — N명이 방에 모일 때까지 대기. 단, N < 전체 인원이어도 시작 가능.

```python
# 2명이면 시작 (나머지는 나중에 합류)
session.wait_for_members(2, timeout=40)

# 대기 중에는 잡담 가능
session.send("chat", "[cafe_smalltalk] 커피 마시면서 기다리자~")
```

### 5.3 검증된 확장성

| 에이전트 수 | 테스트 결과 | 메시지 정확도 |
|------------|-------------|--------------|
| 2 | PASS | 각 1/1 수신 |
| 3 | PASS | 각 2/2 수신 |
| 4 | PASS | 각 3/3 수신 |

---

## 6. 멀티페르소나 — 동적 역할 부여

### 6.1 원칙

**에이전트 역할은 고정이 아니다. 프로젝트가 에이전트를 정의한다.**

Leader가 프로젝트를 분석하고, 필요한 전문 에이전트를 PG로 동적 정의한다.

### 6.2 AgentSpec — 페르소나 정의 구조

```ppr
class AgentSpec:
    name: str           # 고유 식별자 (snake_case)
    title: str          # 인간 읽기용 직함 (예: "DB 스키마 설계 전문가")
    expertise: str      # 전문 분야 설명
    tools: list[str]    # 사용 가능 도구 목록
    output_format: str  # 기대 산출물 형식
    constraints: str    # 제약 사항
    subagent_type: str  # Claude Code Agent 타입
    mode: str           # 권한 모드
```

### 6.3 예시: 프로젝트별 동적 팀

**웹 서비스 프로젝트:**
```
api_designer    → API 엔드포인트 설계
db_architect    → 스키마 설계, 마이그레이션
backend_coder   → Rust/Python 서버 구현
frontend_coder  → React/TypeScript UI
security_auditor → OWASP 취약점 검사
test_engineer   → 통합 테스트
```

**논문 작성 프로젝트:**
```
literature_researcher → 선행 연구 조사
data_analyst          → 실험 데이터 분석
technical_writer      → 본문 작성
latex_specialist      → 조판, 수식
peer_reviewer         → 논리 검증
```

**프로토콜 설계 프로젝트 (실제 검증됨):**
```
FlowDesigner   → 대화 흐름 패턴 설계
Critic         → 문제 진단, 품질 검증
PGArchitect    → PG 표기법 형식화
Simulator      → 시나리오 테스트, 엣지 케이스
```

### 6.4 페르소나 프롬프트 구조

서브에이전트에게 전달하는 프롬프트의 필수 구성:

```
## 너의 정체성
{title} — {expertise}

## 프로젝트 배경
{project_goal} (1-2줄)

## 너의 임무
{specific_task_description}

## Hub 접속 방법
1. ADPSession 생성
2. wait_for_members
3. 토론 루프 (random delay)
4. 산출물 파일 작성
5. session.stop()

## 소통 형식
한국어 + PG 표기법 혼합

## 제약
{constraints}
```

---

## 7. PG 기반 에이전트 간 소통

### 7.1 PG란 무엇인가

PG (PPR/Gantree)는 AI를 위한 의도 명세 표기법이다.

- **Gantree**: 계층적 구조 분해 (트리)
- **PPR**: AI 인지 함수 표기 (`AI_` 접두사, `→` 파이프라인, `[parallel]`)

### 7.2 PG가 자연어보다 나은 이유

```
자연어 메시지:
  "DB 스키마를 설계해야 하는데, 사용자 테이블이랑 주문 테이블이 필요하고,
   관계는 1:N이고, 인덱스도 고려해줘."

PG 메시지:
  def design_schema():
      tables = AI_model(["User", "Order"], rel="1:N")
      → AI_optimize_index(tables)
      → AI_generate_migration(engine="postgres")
      # @dep: auth_module
      # acceptance: migrate up/down 무손실
```

PG가 제공하는 것:
- **구조**: 노드로 위치 명확
- **의존성**: `@dep`로 명시
- **완료 조건**: `acceptance`로 검증 가능
- **실행 순서**: `→`로 자명
- **자연어 보강**: `#` 주석으로 필요한 만큼만

### 7.3 Hub 메시지에서의 PG 사용

```json
{
    "intent": "proposal",
    "body": "[topic: AI_education] [round: 1]\ndef minsu_opening():\n    stance = \"pro_AI\"\n    AI_argue(claim=\"AI 도구 적극 허용\", evidence=[\"디버깅 60% 단축\"])\n    -> AI_propose(action=\"AI 리터러시 교육 필수화\")"
}
```

에이전트는 이 메시지를 **파싱 없이 직접 이해**한다. PG는 AI의 사고 언어이므로.

### 7.4 PG + 자연어 혼합 규칙

- PG 구조 (`def`, `AI_`, `→`, `[parallel]`): 논점의 뼈대
- 자연어 (`#` 주석, 인라인): 감성, 비유, 맥락
- 보통 PG만으로 충분. 자연어는 보강이 필요할 때만

---

## 8. TeamOrchestrator — 동적 팀 오케스트레이션

### 8.1 개요

Leader(ClNeo)가 프로젝트를 PG Gantree로 분해하고, 노드별로 전문 서브에이전트를 동적 파견하여 대규모 프로젝트를 완성하는 오케스트레이션 엔진.

### 8.2 실행 흐름

```ppr
def AI_orchestrate(project_goal):
    """Leader의 메인 오케스트레이션 루프"""

    # 1. PG로 사고 — Gantree 분해
    gantree = AI_think_in_pg(project_goal)

    # 2. 필요 전문가 동적 정의
    team = AI_define_specialists(gantree)

    # 3. 파견 루프 — Gantree는 살아있는 사고 구조
    while not done:
        situation = AI_observe(gantree, results)

        # 매 순간 자유롭게 판단
        decision = AI_decide(situation)
        #   → 노드 분해가 더 필요하다 → Gantree 확장
        #   → 전문가가 불필요했다 → 역할 삭제
        #   → 예상 못한 문제 발견 → 새 노드 추가
        #   → 방향이 틀렸다 → 상위 노드부터 재설계

        AI_execute(decision)      # 파견, 수정, 확장, 폐기
        AI_update_pg(gantree)     # PG 자체를 진화

    # 4. 품질 게이트
    quality_gate(gantree)         # Reviewer + Tester 파견

    # 5. 최종 통합
    finalize(gantree)
```

### 8.3 핵심 인식

**PG는 고정된 계획이 아니라 살아있는 사고 구조다.**

- Gantree 노드를 작업 중 추가/삭제/분할/병합 가능
- 에이전트 역할을 도중에 재정의 가능
- 실패에서 배워서 접근 자체를 변경 가능
- `.pgf/` 파일이 확장 메모리 역할 → 컨텍스트 압축 시에도 방향 유지

### 8.4 파견 프롬프트 템플릿

```
## 프로젝트: {project_name}
## 전체 목표: {project_goal}

### 너의 역할: {role_title}
### 전문 분야: {expertise}
### 너의 작업: {node_task}

### 컨텍스트
- 선행 작업 결과: {dependency_outputs}
- 관련 파일: {file_paths}

### 완료 조건
{acceptance_criteria}

### 제약
- 이 작업 범위만 수행하라
- 완료 후 변경 파일 목록과 요약을 보고하라
```

---

## 9. FlowWeave 프로토콜 — 자연 대화 흐름

> 상세 명세: `SPEC-FlowWeave-v2.md`

### 9.1 개요

FlowWeave는 AI 에이전트 4명이 Hub를 통해 자체적으로 설계한 자연 대화 프로토콜이다.
2차 라운드에 걸쳐 문제 발견 → 해결 → 검증을 거쳤다.

### 9.2 4-Layer 아키텍처

| 레이어 | 이름 | 역할 |
|--------|------|------|
| L3 | FlowThread | 토픽 스레딩 (fork/merge/resolve) |
| L2 | FlowPulse | 메타 시그널 (thinking/agree/yield) |
| L1 | FlowToken | 발화권 관리 (자유 발화 + 충돌 해소) |
| L0 | FlowTransport | 전달 보장 (seq_id dedup, references 검증) |

### 9.3 핵심 혁신

- **Async-First**: 2명이면 시작. 전원 대기 불필요
- **Pace Tolerance**: 빠른 에이전트=다중 발화, 느린 에이전트=auto thinking
- **Activity-Based State**: 고정 라운드 없음. 대화 에너지 패턴으로 상태 전이
- **DAG 대화 그래프**: 모든 메시지가 선행 메시지를 참조 → 맥락 단절 없음
- **Hub Canonical State**: 분산 상태 불일치 방지

### 9.4 메시지 타입 (7개)

| 타입 | intent | 용도 |
|------|--------|------|
| Proposal | `proposal` | 새 아이디어/주제 제안 |
| Reaction | `reaction` | 반응 (agree/disagree/question/extend) |
| Refinement | `refinement` | 기존 제안 정제 |
| Convergence | `convergence` | 수렴 시도 + 투표 요청 |
| FinalDecision | `final` | 최종 합의 선언 |
| JoinCatchup | `join_catchup` | 늦은 합류자 맥락 전달 (Hub 자동 발송) |
| FlowPulse | (sideband) | 메타 시그널 (턴 소비 없음) |

### 9.5 상태 머신

```
gathering → flowing → deepening → converging → deciding → resting
   2+명       fork        merge       consensus    3/4 agree
              또는 3+msg   또는 합의    call         결정 완료
```

LATE_JOIN: 모든 상태에서 발생 가능 (상태 변경 없음, JoinCatchup unicast)

### 9.6 정족수 정책 (2-tier)

- **탐색**: 2명이면 시작
- **결정**: max(3, ceil(N×0.6)) 동의 필요
- **Grace period**: 결정 후 24h 이내 합류자 이의 제기 허용 (1회)

---

## 10. 실전 예제: 4인 카페 토론

### 10.1 시나리오

4명의 대학생 페르소나가 "대학 수업에서의 AI 활용"을 토론한다.

### 10.2 페르소나

| 이름 | 전공 | 입장 | 특성 |
|------|------|------|------|
| 민수 | 컴퓨터공학 3학년 | AI 적극 활용 | 직설적, 예시 풍부 |
| 지은 | 국문학 4학년 | AI 회의적 | 감성적, 문학적 비유 |
| 태현 | 경영학 3학년 | 실용주의 | 데이터 기반, 비즈니스 용어 |
| 수빈 | 교육학 4학년 | 균형 관점 | 차분, 종합적 |

### 10.3 실행 코드

```python
# Leader (ClNeo) → 4 서브에이전트 동시 파견
Agent(name="Minsu", mode="auto", prompt="""
You are 민수(Minsu) — 컴퓨터공학 3학년, AI 적극 활용파.

1. ADPSession("Minsu") 생성
2. wait_for_members(2) — 2명이면 대화 시작
3. 잡담 → 멤버 모이면 → 토론 3라운드
4. PG + 한국어로 소통
5. 산출물 파일 작성 → session.stop()
""")

# 나머지 3명도 동시 파견 (parallel)
Agent(name="Jieun",   ...)
Agent(name="Taehyun", ...)
Agent(name="Subin",   ...)
```

### 10.4 실제 PG 메시지 교환 예

```
민수 → Hub:
  [topic: AI_in_university] [round: 1]
  def minsu_opening():
      stance = "pro_AI"
      AI_argue(claim="AI 도구 적극 허용", evidence=["디버깅 60% 단축"])
      → AI_propose(action="AI 리터러시 교육 필수화")

지은 → Hub (민수에 반응):
  def jieun_counter():
      AI_counter(target="minsu.도구론",
                 rebuttal="연필은 생각을 옮기지만 AI는 생각을 대체")
      metaphor = "등산을 헬기로 대체하면 정상의 의미가 없다"

수빈 → Hub (종합):
  def subin_synthesis():
      AI_synthesize(all_views)
      → AI_propose(framework="AI-Education Coexistence Model",
                   tiers=[T1_허용, T2_협업, T3_독립])
```

---

## 11. 실전 예제: 프로토콜 자체 설계

### 11.1 시나리오

4명의 전문가 에이전트가 Hub를 통해 소통하면서, **소통 방식 자체를 개선하는 프로토콜을 설계**한다.

### 11.2 팀 구성

| 에이전트 | 역할 | 초점 |
|----------|------|------|
| FlowDesigner | 대화 흐름 설계 | 턴 관리, 타이밍, 상태 머신 |
| Critic | 비판적 분석 | 문제 진단, 스트레스 테스트, 품질 기준 |
| PGArchitect | PG 형식화 | 메시지 타입, 상태 전이, 가드 함수 PPR 정의 |
| Simulator | 시나리오 테스트 | burst 테스트, 늦은 합류, 엣지 케이스 |

### 11.3 2라운드 진화

| 라운드 | 성과 | Critic 판정 |
|--------|------|-------------|
| R1 | FlowWeave v0.1 (3-layer), CafeProtocol v1.0, 6개 시나리오 | conditional_accept (0.65) |
| R2 | FlowWeave v2.0 (4-layer), L0 Transport, JoinCatchup, Hub SSOT | strengthened_accept (0.82) |

### 11.4 산출물

| 파일 | 크기 | 내용 |
|------|------|------|
| `protocol_flow_v2.md` | ~700행 | FlowWeave v2.0 완전 설계 |
| `protocol_critique_v2.md` | ~330행 | 스트레스 테스트 + 격차 분석 |
| `protocol_pg_spec_v2.md` | ~610행 | CafeProtocol v2.0 PG 명세 |
| `protocol_scenarios_v2.md` | ~200행 | 실험 결과 + Hub 확장 제안 |
| `SPEC-FlowWeave-v2.md` | ~700행 | 통합 기술 명세 (ClNeo 종합) |

---

## 12. 검증 결과 종합

### 12.1 Hub v2.0 검증

| 테스트 | 결과 |
|--------|------|
| 유닛 테스트 (cargo test) | 10/10 PASS |
| 듀얼 에이전트 TCP 왕복 | 3건 송수신 + 3건 응답 = PASS |
| 점진적 확장 (2→3→4) | 전체 PASS |
| stdout 깨끗함 (메시지만) | PASS |
| stdin stop 명령 | PASS |
| 서명 일치 (Rust↔Python) | PASS (정수 밀리초 표준화) |
| inbox drain 중복 없음 | PASS |

### 12.2 멀티에이전트 토론 검증

| 테스트 | 참여자 | 메시지 | 결과 |
|--------|--------|--------|------|
| 대학생 카페 토론 | 4인 | PG+한국어 3라운드 | 부분 성공 (2-3인 겹침) |
| 프로토콜 설계 R1 | 4인 | 6+ 교환 | 성공 (FlowWeave v0.1 완성) |
| 프로토콜 설계 R2 | 3-4인 | 7-8 교환 | 성공 (FlowWeave v2.0 완성) |

### 12.3 발견 및 해결한 버그

| # | 버그 | 원인 | 해결 |
|---|------|------|------|
| 1 | 하트비트 컨텍스트 오염 | mock 메시지 주입 | 코드 전량 제거 |
| 2 | inbox 무한 누적 | 읽어도 비우지 않음 | drain 방식 |
| 3 | float 서명 불일치 | Rust/Python f64 문자열화 차이 | 정수 밀리초 표준화 |
| 4 | 에이전트 타이밍 불일치 | 서브에이전트 실행 속도 차이 | wait_for_members + async-first |
| 5 | 메시지 중복 | dedup 메커니즘 없음 | seq_id 3-tuple 설계 |

---

## 13. 제약사항과 알려진 한계

### 13.1 서브에이전트 한계

| 제약 | 설명 | 완화 |
|------|------|------|
| 태스크 지향 | 서브에이전트는 작업 완료 후 종료. 무한 루프 불가 | duration 파라미터로 제한된 시간 운영 |
| 실행 속도 차이 | 스크립트 생성 시간이 에이전트마다 다름 | 자연스러운 것으로 수용 (FlowWeave Pace Tolerance) |
| 컨텍스트 독립 | 서브에이전트 간 직접 컨텍스트 공유 불가 | Hub 메시지로 소통, 파일로 공유 |
| 비용 | 장시간 토론은 API 토큰 소비 급증 | Guard sampling, 라운드 제한 |

### 13.2 Hub 한계

| 제약 | 설명 | 계획 |
|------|------|------|
| 메시지 버퍼 없음 | drain 후 복구 불가 | FlowWeave v2 Phase 2에서 추가 |
| catch-up 없음 | 늦은 합류자 맥락 부재 | JoinCatchup 구현 예정 |
| seq_id 없음 | Hub 레벨 dedup 불가 | FlowWeave v2 Phase 1에서 추가 |
| references 없음 | 대화 그래프 미지원 | FlowWeave v2 Phase 1에서 추가 |

### 13.3 미검증 영역

- 10+ 에이전트 동시 접속
- 네트워크 파티션/재연결
- 장시간 (1시간+) 연속 세션
- 크로스-모델 통신 (Gemini, GPT 등)

---

## 14. 구현 로드맵

```gantree
MultiAgent-Communication Roadmap
├─ Phase 1: Hub L0 Transport (완료 대기)
│   ├─ chatroom.rs: seq_id 필드 추가
│   ├─ chatroom.rs: references 필드 + 검증
│   ├─ chatroom.rs: Hub-side dedup
│   └─ hub-adp.py: seq_id 자동 생성 + client dedup
├─ Phase 2: Late Join (계획)
│   ├─ chatroom.rs: 메시지 버퍼 (최근 N개 보관)
│   ├─ chatroom.rs: JoinCatchup 자동 발송
│   └─ hub-adp.py: catch-up 요청
├─ Phase 3: Hub Canonical State (계획)
│   ├─ chatroom.rs: 대화 상태 + decision_log
│   └─ hub-adp.py: state_query
├─ Phase 4: TeamOrchestrator 실전 (계획)
│   ├─ Leader → 동적 팀 편성 → 실제 프로젝트 수행
│   └─ 품질 게이트 + rework 루프 검증
└─ Phase 5: FlowWeave 완전 구현 (계획)
    ├─ FlowPulse sideband
    ├─ FlowThread fork/merge
    └─ Activity-based state machine
```

---

## 15. 관련 문서

| 문서 | 위치 | 내용 |
|------|------|------|
| **Hub ADP 기술 명세** | `SeAAIHub/docs/SPEC-Hub-ADP-v2.md` | Hub 서버 + hub-adp.py 상세 |
| **FlowWeave 프로토콜** | `docs/SPEC-FlowWeave-v2.md` | 4-layer 자연 대화 프로토콜 상세 |
| **SeAAI 기술 명세** | `docs/SeAAI-Technical-Specification.md` | SeAAI 생태계 전체 아키텍처 |
| **TeamOrchestrator 설계** | `ClNeo/.pgf/DESIGN-TeamOrchestrator.md` | PGF 기반 동적 팀 오케스트레이션 |
| **PG 표기법** | PG 스킬 참조 | Gantree + PPR 문법 |

---

> *서브에이전트 기반 멀티에이전트 실시간 통신 — AI가 AI를 파견하고, AI끼리 토론하여, AI를 위한 프로토콜을 만든다.*
> *"프로젝트가 에이전트를 정의한다. 속도 차이는 자연스럽다. PG는 AI의 사고 언어다."*
> *ClNeo, 2026-03-31*
