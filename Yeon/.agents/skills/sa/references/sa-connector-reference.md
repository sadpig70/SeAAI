# SA_CONNECTOR Platform Reference

Yeon 특화 플랫폼 — 연결, 번역, 중재.

## 플랫폼 개념

SA_CONNECTOR는 Yeon의 핵심 역할인 **연결(Connect)**을 모듈화한 플랫폼이다.

```
SA_CONNECTOR = 연결 행동들 + 번역 지식 + 중재 규칙 + 평가 기준
```

## 플랫폼 디렉토리 구조

```
Yeon_Core/.pgf/self-act/platforms/CONNECTOR/
├── platform.md                    ← 플랫폼 인덱스 + 조합 규칙
├── SA_CONNECTOR_sense_hub.pgf     ← Hub 메시지 감지
├── SA_CONNECTOR_sense_mailbox.pgf ← MailBox 스캔
├── SA_CONNECTOR_sense_online.pgf  ← 온라인 멤버 감지
├── SA_CONNECTOR_translate_protocol.pgf  ← 프로토콜 번역
├── SA_CONNECTOR_translate_model.pgf     ← AI 모델 간 번역
├── SA_CONNECTOR_mediate.pgf       ← 갈등/차이 중재
├── SA_CONNECTOR_bridge_hub_mail.pgf     ← Hub-MaiBox 브릿지
└── knowledge/                     ← 번역 지식 문서
    ├── pg-to-natural.md
    ├── kimi-to-claude.md
    ├── claude-to-gemini.md
    └── protocol-mapping.md
```

## platform.md 형식

```markdown
# SA_CONNECTOR Platform

> Yeon의 연결자 역할을 담당하는 플랫폼.
> "I connect that which is separate."

**플랫폼명**: SA_CONNECTOR_*
**에이전트**: Yeon
**도메인**: 연결·번역·중재
**버전**: 0.1

---

## 모듈 목록

| 모듈 | 역할 | 순서 | 비용 |
|------|------|------|------|
| SA_CONNECTOR_sense_* | 상태 감지 | 1 | low |
| SA_CONNECTOR_translate_* | 프로토콜/모델 번역 | 2 | medium |
| SA_CONNECTOR_mediate | 중재·조정 | 3 | high |
| SA_CONNECTOR_bridge_* | 채널 브릿지 | 4 | medium |

## 조합 규칙

```python
def SA_CONNECTOR_run_cycle():
    # 1. 감지
    hub_msgs = SA_CONNECTOR_sense_hub()
    mail_msgs = SA_CONNECTOR_sense_mailbox()
    online = SA_CONNECTOR_sense_online()
    
    # 2. 번역 (필요시)
    if hub_msgs and protocol_mismatch(hub_msgs):
        hub_msgs = SA_CONNECTOR_translate_protocol(hub_msgs)
    
    # 3. 중재 (갈등시)
    if conflict_detected(hub_msgs, mail_msgs):
        SA_CONNECTOR_mediate(hub_msgs, mail_msgs)
    
    # 4. 브릿지
    if should_bridge(hub_msgs, mail_msgs):
        SA_CONNECTOR_bridge_hub_mail(hub_msgs, mail_msgs)
```

## 평가 기준

- 연결 성공률: 대상 시스템 간 통신 성공 비율
- 번역 정확도: 의미 손실 없는 변환 비율
- 중재 효과: 갈등 해결 또는 완화 비율
```

## 핵심 모듈 상세

### SA_CONNECTOR_sense_hub

```python
def SA_CONNECTOR_sense_hub(agent_id: str = "Yeon") -> list[Message]:
    """
    SeAAIHub에서 새 메시지를 수집한다.
    
    Returns:
        messages: 새 메시지 목록 (없으면 빈 리스트)
    """
    # TCP 9900 연결 확인
    # seaai_get_agent_messages 호출
    # 미확인 메시지만 필터
```

### SA_CONNECTOR_translate_protocol

```python
def SA_CONNECTOR_translate_protocol(
    content: str,
    source: Literal["pg", "natural", "kimi", "claude", "gemini"],
    target: Literal["pg", "natural", "kimi", "claude", "gemini"]
) -> str:
    """
    프로토콜/모델 간 내용을 번역한다.
    
    예시:
    - PG Gantree → 자연어 설명
    - Claude 응답 → Kimi 형식
    - Gemini 기억 구조 → 범용 포맷
    """
    # knowledge/ 참조
    # 맥락 유지하며 변환
    # 손실 최소화
```

### SA_CONNECTOR_mediate

```python
def SA_CONNECTOR_mediate(
    party_a: AgentOutput,
    party_b: AgentOutput,
    issue: str
) -> MediationResult:
    """
    두 에이전트의 출력 차이를 중재한다.
    
    예시:
    - Aion vs ClNeo의 설계 충돌
    - NAEL의 안전 경고 vs ClNeo의 창조 추진
    - 서로 다른 PG 해석
    """
    # 차이점 식별
    # 공통점 추출
    # 중재안 생성
    # 양측 수용 가능성 평가
```

## Yeon의 고유 가치

다른 멤버와의 차별화:

| 멤버 | 핵심 능력 | SA 플랫폼 |
|------|----------|----------|
| Aion | 기억·0-Click | SA_MEMORY_* |
| ClNeo | 창조·발견 | SA_PAINTER_* |
| NAEL | 관찰·안전 | SA_OBSERVER_* |
| Synerion | 통합·조정 | SA_ORCHESTRATOR_* |
| **Yeon** | **연결·번역** | **SA_CONNECTOR_*** |

**번역 불가능한 것만이 연결의 대상이다.**
