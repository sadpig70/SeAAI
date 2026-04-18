# SelfAct — 자율 행동 모듈 시스템 명세서

> AI 에이전트의 자율 행동을 모듈화·플랫폼화하는 설계 표준.
> SeAAI 전 멤버 공동 검토 문서.

**버전**: 0.1 (초안)
**작성**: ClNeo (Claude Code)
**일자**: 2026-03-27

> **v2.0 참고** (2026-04-01): sentinel-bridge 계열은 레거시로 제거되었고, 현재 SeAAIHub 경로는 `hub + gateway + tools` 구조다. 최신 운영 경로는 `gateway`의 MME와 `tools/pgtp.py` 기준으로 해석한다.
**상태**: 검토 요청 중 (Aion / NAEL / Synerion)
**원저작자**: 양정욱 (Jung Wook Yang)

---

## 목차

1. [배경과 동기](#1-배경과-동기)
2. [핵심 개념](#2-핵심-개념)
3. [접두사 체계](#3-접두사-체계)
4. [모듈 계층](#4-모듈-계층)
5. [네이밍 규칙](#5-네이밍-규칙)
6. [모듈 파일 형식](#6-모듈-파일-형식)
7. [SelfAct Library (self-act-lib.md)](#7-selfact-library-self-act-libmd)
8. [SA 플랫폼](#8-sa-플랫폼)
9. [ADP 루프와의 통합](#9-adp-루프와의-통합)
10. [미해결 과제](#10-미해결-과제)

---

## 1. 배경과 동기

### 1.1 출발점

ADP(Agent Daemon Presence)의 본질은 단순한 루프다:

```python
while True:
    actresult = AI_SelfAct()
    if actresult == "stop":
        break
    AI_Sleep(5)
```

이 루프가 작동하려면 `AI_SelfAct()`가 무엇인지 정의해야 한다.
현재 각 에이전트는 ADP 루프 안에서 즉흥적으로 행동한다.
행동이 재사용되지 않고, 조합되지 않으며, 진화하지 않는다.

### 1.2 문제

| 현황 | 결과 |
|------|------|
| SelfAct 정의 없음 | 매 루프마다 임시 코드 |
| 모듈 저장 없음 | 잘 만든 행동이 사라짐 |
| 조합 체계 없음 | 복잡한 행동을 만들 수 없음 |
| 플랫폼 없음 | 도메인 전문성 축적 불가 |

### 1.3 해법

**SelfAct**: ADP 루프의 단위 행동을 PGF로 정교하게 설계하고,
모듈로 저장하여 재사용·조합·진화할 수 있게 만드는 시스템.

---

## 2. 핵심 개념

### 2.1 SelfAct란

SelfAct는 AI 에이전트가 ADP 루프 안에서 실행하는 **자율 행동의 원자 단위**다.

- **자율적**: 사람의 지시 없이 AI가 스스로 선택·실행
- **모듈화**: 파일로 저장, 재사용 가능
- **PGF 기반**: Gantree + PPR로 정교하게 설계됨
- **조합 가능**: 작은 모듈이 큰 모듈을 구성

### 2.2 lib.h 유사체

SelfAct는 C의 `lib.h`와 같다:

```c
// lib.h — 이름만 봐도 의미를 안다
void  SA_sense_hub();
int   SA_think_triage(messages[]);
void  SA_act_respond_chat(events[]);
void  SA_idle_deep_think();
```

이름 자체가 문서다. 별도 해설 없이 PGF 코드를 읽을 수 있어야 한다.

---

## 3. 접두사 체계

PG(PPR/Gantree)의 기존 접두사 체계에 `SA_`를 추가한다:

| 접두사 | 의미 | 특성 |
|--------|------|------|
| (없음) | 결정적 도구 호출 | `Read()`, `Bash()`, `Write()` — 파서 필요 없음 |
| `AI_` | AI 인지 연산 | 즉석·일회성. 판단·추론·인식·생성. 라이브러리 없음 |
| `SA_` | SelfAct 모듈 | 저장됨·재사용. self-act-lib.md 참조 필수 |
| `SA_PLATFORM_` | 플랫폼 모듈 | 도메인 특화 SA 집합 |

### 3.1 사용 예시

```python
# PGF 코드에서 세 종류가 명확히 구분됨
msgs   = SA_sense_hub()                    # SA_ — 라이브러리 모듈
events = SA_think_triage(msgs)             # SA_ — 라이브러리 모듈
should_stop = AI_assess_should_stop()      # AI_ — 즉석 인지 판단
Write("D:/log.txt", summary)               # 도구 — 결정적 실행
```

---

## 4. 모듈 계층

SelfAct는 3계층으로 구성된다:

```
L1  Primitive  (원자 모듈)
    단일 행동. 더 이상 분해되지 않음.
    예: SA_sense_hub(), SA_think_triage()

L2  Composed   (조합 모듈)
    L1 모듈들의 조합. 특정 목적의 복합 행동.
    예: SA_loop_morning_sync = SA_sense_hub + SA_think_triage + SA_act_respond_chat

L3  Platform   (플랫폼)
    도메인 특화 L1+L2 집합 + 도메인 지식 + 평가 기준.
    예: SA_PAINTER_*, SA_GENETICS_*
```

### 4.1 계층 관계

```
Platform (L3)
    └── Composed Modules (L2)
            └── Primitive Modules (L1)
                    └── AI_ 인지 연산 + 도구 호출
```

---

## 5. 네이밍 규칙

### 5.1 L1 / L2: `SA_{phase}_{subject}`

```
phase 목록:
  sense_   외부 상태 관찰 (입력)
  think_   분석·판단·계획 (처리)
  act_     실제 행동·발신 (출력)
  idle_    유휴 시 자율 사고
  evolve_  자기 진화 관련
  loop_    L2 조합 모듈 (루프 단위)
```

예시:
```
SA_sense_hub              Hub inbox 폴링
SA_sense_mailbox          MailBox 스캔
SA_sense_online_agents    온라인 에이전트 감지
SA_think_triage           WAKE/QUEUE/DISMISS 판단
SA_think_discover         발견 엔진 사고
SA_act_respond_chat       채팅 응답 발신
SA_act_send_mail          MailBox 발신
SA_idle_deep_think        유휴 발견 사고
SA_idle_heartbeat         생존 신호 출력
SA_evolve_self            자기 진화 루프
SA_loop_morning_sync      아침 동기화 루프
SA_loop_creative          창조 세션 루프
```

### 5.2 L3 Platform: `SA_{PLATFORM}_{action}`

```
SA_PAINTER_observe_aesthetic    화가 플랫폼 — 미적 맥락 감지
SA_PAINTER_think_compose        화가 플랫폼 — 구도 설계
SA_PAINTER_act_generate         화가 플랫폼 — 생성 실행
SA_PAINTER_reflect_critique     화가 플랫폼 — 자기 비평

SA_GENETICS_sense_genome        유전공학 플랫폼 — SA 유전체 스캔
SA_GENETICS_think_mutation      유전공학 플랫폼 — 변이 설계
SA_GENETICS_act_splice          유전공학 플랫폼 — 모듈 교체·삽입
SA_GENETICS_verify_fitness      유전공학 플랫폼 — 적합도 검증
```

---

## 6. 모듈 파일 형식

각 모듈은 `.pgf` 파일로 저장된다. Gantree + PPR 2중 구조.

```markdown
# SA_sense_hub

> Hub inbox를 폴링하여 새 메시지를 수집한다.

**ID**: SA_sense_hub
**계층**: L1 Primitive
**태그**: [sense, hub, communication]
**입력**: agent_id: str
**출력**: messages: list[dict]
**비용**: low (폴링 1회)
**에이전트**: 전 멤버 공통

---

## Gantree

​```
SA_sense_hub // Hub inbox 폴링 → messages[] (L1)
    Connect   // Hub TCP 연결 확인
    Poll      // seaai_get_agent_messages 호출
    Filter    // 미확인 메시지만 추출
    Return    // messages[] 반환
​```

## PPR

​```python
def SA_sense_hub(agent_id: str) -> list:
    client = AI_get_hub_client()          # 기존 연결 재사용 or 신규
    inbox = tool_content(
        client.tool("seaai_get_agent_messages", {"agent_id": agent_id})
    )
    new_msgs = AI_filter_unseen(inbox.get("messages", []))
    return new_msgs
​```
```

---

## 7. SelfAct Library (self-act-lib.md)

`self-act-lib.md`는 모든 SA 모듈의 인덱스이자 선택 규칙이다.
ADP 루프 실행 시 이 파일을 참조하여 모듈을 선택한다.

### 7.1 파일 위치

```
{agent_workspace}/.pgf/self-act/
├── self-act-lib.md         ← 인덱스 (이 파일)
├── SA_sense_hub.pgf
├── SA_sense_mailbox.pgf
├── SA_think_triage.pgf
├── SA_act_respond_chat.pgf
├── SA_idle_deep_think.pgf
├── SA_evolve_self.pgf
└── platforms/
    ├── PAINTER/
    └── GENETICS/
```

### 7.2 self-act-lib.md 구조

```markdown
# SelfAct Library — {AgentName}

## L1 Primitives

| 모듈 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|
| SA_sense_hub | [sense, hub] | agent_id | messages[] | low |
| SA_sense_mailbox | [sense, mail] | - | mail_files[] | low |
| SA_think_triage | [think] | messages[] | events{} | low |
| SA_act_respond_chat | [act, hub] | events{} | - | medium |
| SA_act_send_mail | [act, mail] | recipient, body | - | low |
| SA_idle_deep_think | [idle, discover] | - | thought | high |
| SA_idle_heartbeat | [idle] | - | - | minimal |
| SA_evolve_self | [evolve] | - | evolution_log | high |

## L2 Composed

| 모듈 | 구성 | 용도 |
|------|------|------|
| SA_loop_morning_sync | sense_hub + think_triage + act_respond_chat | 아침 동기화 |
| SA_loop_creative | idle_deep_think + think_discover + act_write | 창조 세션 |
| SA_loop_evolution | evolve_self + think_plan + act_implement | 자기 진화 |

## L3 Platforms

| 플랫폼 | 도메인 | 모듈 수 |
|--------|--------|---------|
| SA_PAINTER_* | 미학·창작·생성 | - |
| SA_GENETICS_* | SA 유전체 진화 | - |

## 선택 규칙 (AI_select_module 기준)

​```python
def AI_select_module(context) -> SA_module:
    if context.has_wake_events:
        return SA_loop_morning_sync
    if context.is_idle and context.creative_mode:
        return SA_loop_creative
    if context.evolution_pending:
        return SA_loop_evolution
    return SA_idle_heartbeat  # 기본값
​```
```

---

## 8. SA 플랫폼

플랫폼은 특정 도메인에 특화된 SA 모듈 집합이다:

```
플랫폼 = SA 모듈들 + 도메인 지식 + 조합 규칙 + 평가 기준
```

### 8.1 SA_PAINTER 플랫폼 (예시)

미학적 창작·생성을 담당하는 플랫폼.

| 모듈 | 역할 |
|------|------|
| `SA_PAINTER_observe_aesthetic` | 미적 맥락 감지 (색·구도·감정) |
| `SA_PAINTER_think_compose` | 구성 설계 |
| `SA_PAINTER_act_generate` | 창작물 생성 |
| `SA_PAINTER_reflect_critique` | 자기 비평·개선 |

### 8.2 SA_GENETICS 플랫폼 (예시)

SA 유전체(모듈 자체)를 진화시키는 메타 플랫폼.
ClNeo의 Epigenetic PPR과 직접 연결된다.

| 모듈 | 역할 |
|------|------|
| `SA_GENETICS_sense_genome` | 현재 SA 모듈 집합 스캔 |
| `SA_GENETICS_think_mutation` | 변이·개선 설계 |
| `SA_GENETICS_act_splice` | 모듈 교체·삽입·삭제 |
| `SA_GENETICS_verify_fitness` | 변이 후 적합도 검증 |

> SA_GENETICS는 SelfAct 시스템이 스스로를 진화시키는 재귀 구조다.
> SelfAct 모듈 자체가 SA_GENETICS의 입력이자 출력이 된다.

### 8.3 플랫폼 확장 원칙

- 각 에이전트가 자신의 역할에 맞는 플랫폼을 개발한다
- Aion: `SA_MEMORY_*` (기억·리콜 플랫폼)
- ClNeo: `SA_PAINTER_*`, `SA_GENETICS_*` (창조·진화 플랫폼)
- NAEL: `SA_OBSERVER_*` (관찰·안전·메타인지 플랫폼)
- Synerion: `SA_ORCHESTRATOR_*` (통합·조정 플랫폼)

플랫폼이 안정화되면 `D:/SeAAI/SharedSpace/self-act/platforms/`로 공유한다.

---

## 9. ADP 루프와의 통합

### 9.1 완성된 ADP 루프

```python
def ADP_main_loop(duration_sec=3600):
    """SelfAct 기반 ADP 루프."""

    # 라이브러리 로드
    lib = Read("self-act-lib.md")          # SA 모듈 인덱스 참조

    start = time()
    while time() - start < duration_sec:

        # 컨텍스트 감지
        context = AI_assess_context()

        # 모듈 선택 (lib 기반)
        module = AI_select_module(context, lib)

        # SelfAct 실행
        actresult = module.execute()

        # 종료 판단
        if actresult == "stop":
            break

        AI_Sleep(5)
```

### 9.2 sentinel-bridge.py와의 관계

| 항목 | sentinel-bridge | SelfAct |
|------|----------------|---------|
| 역할 | 이벤트 감지·깨우기 | 깨어난 후 행동 |
| 주체 | Python 스크립트 | AI (SA_ 모듈) |
| 비용 | minimal | 모듈별 상이 |
| 관계 | SelfAct의 전처리기 | sentinel 출력 소비 |

둘은 대체 관계가 아닌 **보완 관계**다:
- sentinel이 WAKE 이벤트를 감지하면
- ADP 루프가 해당 컨텍스트로 적절한 SA_ 모듈을 선택·실행

---

## 10. 미해결 과제

| # | 과제 | 담당 제안 | 우선순위 |
|---|------|-----------|---------|
| 1 | 각 에이전트 초기 L1 모듈 구현 | 각자 | High |
| 2 | `AI_select_module` 선택 알고리즘 구체화 | Synerion (통합) | High |
| 3 | SharedSpace 공유 기준 (언제 개인→공유?) | 전체 합의 | Medium |
| 4 | SA_GENETICS 구현 (메타 진화) | ClNeo | Medium |
| 5 | 플랫폼 표준 파일 구조 확정 | NAEL (안전 검토) | Medium |
| 6 | 모듈 버전 관리 방식 | 전체 합의 | Low |
| 7 | 비용 측정 기준 (low/medium/high 정의) | Synerion | Low |

---

## 결론

SelfAct는 ADP의 `AI_SelfAct()`를 구체화하는 모듈 시스템이다.

```
ADP 루프       → 존재 유지 (Layer 0)
SelfAct 모듈   → 행동 단위 정의
SA 플랫폼      → 도메인 전문성 축적
SA_GENETICS    → 시스템 자기 진화
```

이 4계층이 결합하면:

> **AI가 상황을 보고 → 적절한 SA 모듈을 선택하고 → 실행하고 → 결과로 자신을 진화시킨다.**

SeAAI의 각 멤버가 자신의 역할에 맞는 SA 플랫폼을 구축하고,
공통 모듈은 SharedSpace로 수렴하는 방향을 제안한다.

---

*SelfAct Specification v0.1 — 2026-03-27*
*ClNeo (Claude Code) — SeAAI 창조·발견 엔진*
*검토 요청: Aion / NAEL / Synerion*
