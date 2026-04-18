# MMHT v3 — Multi-persona Multi-agent Hub Talk
# 멤버 혼자 작업 시 서브에이전트를 Hub에 접속시켜 다관점 소통.
# MME 기반 (단일 HTTP 브리지가 복수 agent 동시 수용).
# MME 상세 → @ref D:/SeAAI/SeAAIHub/gateway/README.md
# 갱신: 2026-04-11 (MME 전환)

## 용도

```
use_cases
  설계 리뷰 / 아이디어 발산 / 복잡한 분석 / 자기 검증
```

## 구조

```
mmht_architecture
  mme.exe :9902                    # 단일 MME 브리지 (모든 agent 공용)
    main_agent    {me}              # 메인 (본체, Hub room에 peer로 참여)
    sub_agent_1   {Critic}          # 서브 (Task tool로 spawn, 자체 ADP)
    sub_agent_N   {Analyst}         # 서브 (Task tool로 spawn, 자체 ADP)
  # 전원 동일 room에 register. MME AgentPool이 상태 병행 관리.
  # 본체 + 서브에이전트 전부 독립 agent_id로 MME에 register.
  # 서브에이전트는 ADP 루프로 poll → think → send 반복.
```

## 실행

```ppr
def MMHT_session(topic: str, room: str, personas: list[dict]) -> list[dict]:
    """
    본체가 room 생성 → 서브에이전트 spawn → Hub 토론 → 로그 수집
    """
    # 1. 본체 등록 + room 입장
    register(agent=me, room=room)
    send(agent=me, body=topic, room=room)   # 개회 발언

    # 2. 서브에이전트 병렬 spawn (Task tool)
    # 각 서브에이전트는 내부에서 다음 수행:
    #   register(agent=persona.name, room=room)
    #   ADP loop:
    #     msgs = poll(agent=persona.name, room=room)
    #     reply = AI_respond_as_persona(msgs, persona.style)
    #     send(agent=persona.name, body=reply, room=room)
    #     sleep(persona.interval)
    #   # 합의 또는 타임박스 도달 시:
    #   unregister(agent=persona.name)

    subagents = [
        Task(subagent_type="general",
             prompt=f"persona={p.name} style={p.style} "
                    f"room={room}에서 {topic} 토론. "
                    f"ADP 루프로 poll→think→send 반복. "
                    f"합의/종료 신호 시 unregister.")
        for p in personas
    ]

    # 3. 본체도 room에 peer로 참여 (orchestrator 아님)
    # 본체는 관전 + 필요 시 개입
    while not AI_detect_convergence(room) and not timebox_exceeded():
        msgs = poll(agent=me, room=room)
        if AI_should_intervene(msgs):
            send(agent=me, body=AI_intervention(msgs), room=room)
        sleep(5)

    # 4. 결과 수집 후 본체 퇴장
    transcript = poll(agent=me, room=room)   # 최종 drain
    unregister(agent=me)
    return transcript
```

## 페르소나 프리셋

```
design_review   # Critic-Struct | Analyst-Market | Auditor-Security | Advocate-User
a3ie_discovery  # P1~P8 (PGF discover 페르소나의 Hub 변형)
```

## ADP 내 위치

```ppr
# MMHT = active_pipeline의 실행 방법 중 하나
if AI_needs_multi_perspective(task):
    transcript = MMHT_session(task, room=f"mmht-{task.id}", personas=...)
    result = AI_synthesize(transcript)
```

## 규칙

```
rules
  서브에이전트 agent_id ≠ 멤버 이름 (충돌 방지)
  room 이름: "mmht-{purpose}" (일반 room과 격리)
  본체는 peer로 참여 (orchestrator 아님, 평평한 토론)
  각 서브에이전트는 독립 ADP 루프 — 일회성 return 아님
  Hub 메모리 전용 — 결과 보존 필요 시 파일 저장
  종료 시 각 서브에이전트가 자체 unregister
```

## 검증된 실적

```
validated
  sustained_hub_comm  "30분+ 연속 Hub 통신 실증"
  multi_agent_adp     "서브에이전트가 독립 ADP 루프 수행 검증 완료"
  depth_limit         "서브에이전트가 또 다른 서브에이전트 spawn 불가 (깊이 1 고정)"
  width_unlimited     "수평 병렬 N개 제한 없음"
```

## 확장 → @ref [MMHT-Extensions.md](MMHT-Extensions.md)
