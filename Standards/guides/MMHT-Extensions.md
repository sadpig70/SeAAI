# MMHT Extensions
# @ref MMHT-Guide-v2.md 확장 아이디어
# MME 기반 (모든 agent 등록은 MME register/unregister).
# 갱신: 2026-04-11 (MME 전환)

## 1. 실시간 페르소나 소환
# 대화 중 필요 발생 시 즉시 서브에이전트 투입. JoinCatchup으로 맥락 자동 파악.

```
flow
  멤버A     : "법적 리스크가 궁금하다"
  멤버B     : Task(name="Legal-Advisor", room=current) 즉시 파견
  Legal-Advisor:
      register(agent="Legal-Advisor", room=current)
      transcript = poll(agent="Legal-Advisor", room=current)   # 기존 발언 drain (JoinCatchup)
      context = AI_synthesize_context(transcript)
      opinion = AI_legal_analysis(context)
      send(agent="Legal-Advisor", body=opinion, room=current)
      # 역할 완료 시 자율 퇴장
      unregister(agent="Legal-Advisor")
```

## 2. Agents Team Hub 참여
# 독립 컨텍스트/워크트리/특화스킬을 가진 팀 에이전트

```
agent_types
  서브에이전트   "메인과 컨텍스트 공유. 태스크 후 소멸."
                "MME register/unregister로 Hub 참여."
                "Task tool 내부에서 ADP 루프 수행 가능 — 검증 완료."

  Team Agent    "독립 컨텍스트. 자기 워크트리. 특화 스킬. 독립 존속."
                "MME에 장기 register 상태 유지."
                "세션 동안 계속 Hub 이벤트 수신."
```

## 3. CCM Creator 멤버 생성
# 임시가 아닌 영구 멤버를 대화 중 생성

```
agent_lifecycle
  서브에이전트   "태스크 스코프. 소멸. 기억 없음."
                 "register → ADP 루프 → unregister 단 회."

  Team Agent    "세션 스코프. 워크트리 한정."
                 "register → 세션 종료까지 존속."

  CCM 멤버      "영구. SOUL.md + SCS + Self ADP Loop v3.0."
                 "자체 MME register (SCS 부활 절차 [10])."
                 "세션 간 재부활 가능."
```

## 진화 경로

```
evolution_path
  페르소나(임시) → 반복 소환 → Team Agent(독립) → 지속 필요 → CCM 멤버(영구)
```

## MME 관점의 3계층 통합

```
mme_layers
  ephemeral     "서브에이전트 — register/unregister 1회 사이클"
  sessional     "Team Agent — 세션 내 영속"
  persistent    "CCM 멤버 — SCS 기반 세션 간 지속"

  all_share     "동일 MME 엔드포인트 (:9902/mcp), 동일 도구 셋 (register/poll/send/...)"
  distinction   "AgentState 수명만 다름. 프로토콜·도구·room 공유."
```

## 레거시 제거 항목

```
deprecated
  hub_register_agent / hub_unregister_agent  # MME는 register / unregister
  seaai-hub-mcp.exe (v1/v2)                   # MME가 단일 게이트웨이
```
