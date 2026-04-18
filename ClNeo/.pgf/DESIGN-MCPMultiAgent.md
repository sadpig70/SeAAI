# MCPMultiAgent Design @v:1.0
# MCP Server 멀티에이전트 지원. MMHT 기반.
# 하나의 MCP 인스턴스가 여러 agent_id를 동시 관리.

## Gantree

```
MCPMultiAgent @v:1.0
  MultiAgentHub (designing)
    # HubAgent를 dict로 관리: {agent_id: HubAgent}
    # 기본 agent = --agent 인자 (메인)
    # 추가 agent = hub_register_agent tool로 동적 등록
    # agent_id별 독립 인증/inbox/seq_gen/dedup
  UpdateTools (designing) @dep:MultiAgentHub
    # hub_register_agent(agent_id, room) — 새 에이전트 등록+접속
    # hub_unregister_agent(agent_id) — 에이전트 해제 (leave_room+정리)
    # 기존 5 tool에 agent_id 선택 파라미터 추가 (생략 시 메인)
    # adp_sleep, adp_cycle은 agent 무관 — 변경 없음
  Test (designing) @dep:UpdateTools
    # 메인(ClNeo) + 서브 2명 동시 등록
    # 서브끼리 메시지 교환 확인
    # 메인이 서브 메시지 수신 확인
    # unregister 후 정리 확인
  Verify (designing) @dep:Test
```

## PPR

```ppr
def hub_register_agent(agent_id: str, room: str = None) -> dict:
    """새 에이전트를 Hub에 등록. 독립 세션 생성."""
    # room 생략 시 메인과 같은 room
    agent = HubAgent(agent_id, host, port, room or main_room)
    agent.connect()  # TCP 재사용 불가 — 별도 연결
    agents[agent_id] = agent
    return {"registered": agent_id, "room": agent.room}

def hub_unregister_agent(agent_id: str) -> dict:
    """에이전트 해제. leave_room + TCP close."""
    agents[agent_id].shutdown()
    del agents[agent_id]
    return {"unregistered": agent_id}
```
