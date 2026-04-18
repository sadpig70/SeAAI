# MCPHubSleep Design @v:1.0
# MCP Server에 adp_sleep tool 추가 + 가이드 AI최적화 + 테스트

## Gantree

```
MCPHubSleep @v:1.0
  AddSleepTool (designing)
    # SeAAIHub_MCP_Server.py에 adp_sleep tool 추가
    # interval(초) 동안 blocking → "heartbeat" 반환
    # stdin "!@#STOP#@!" 수신 시 즉시 반환
    # TOOLS[] 배열에 schema 추가
    # _call_tool에 분기 추가
  AddCycleTool (designing) @dep:AddSleepTool
    # adp_cycle tool 추가
    # interval 동안 Hub poll + MailBox scan 병행
    # 긴급 이벤트 감지 시 즉시 반환
    # context dict 반환: {hub_msgs, mail, plan_hint}
  UpdateGuide (designing) @dep:AddCycleTool
    # SeAAIHub_MCP_Server_Guide.md AI최적 표기로 축약
    # adp_sleep, adp_cycle tool 문서 추가
  BuildTest (designing) @dep:AddSleepTool, AddCycleTool
    # Hub 기동 확인
    # MCP Server 직접 실행 테스트 (stdin JSON-RPC)
    # adp_sleep: blocking + heartbeat 반환 검증
    # adp_cycle: context 수집 + 반환 검증
    # hub_send_message + hub_get_messages 기존 기능 검증
  Verify (designing) @dep:BuildTest
    # 전 tool 정상 동작 확인
    # 기존 기능 regression 없음 확인
    # 보고
```

## PPR

```ppr
def adp_sleep(interval: float = 30) -> dict:
    """ADP 하트비트. interval 초 blocking 후 heartbeat 반환."""
    # 0.5초 단위 내부 tick. running flag 체크.
    # stdin "!@#STOP#@!" 수신 → MCPServer._dispatch에서 running=False
    elapsed = 0
    while elapsed < interval and running:
        sleep(0.5)
        elapsed += 0.5
    return {"heartbeat": True, "slept": elapsed}

def adp_cycle(interval: float = 30) -> dict:
    """ADP 사이클. interval 동안 Hub/Mail 감시. context 반환."""
    deadline = now() + interval
    context = {"hub_msgs": [], "mail": [], "plan_hint": "idle"}
    while now() < deadline:
        # Hub poll (연결 있으면)
        if hub.conn and hub.conn.alive:
            msgs = hub.poll()
            if msgs:
                context["hub_msgs"] = msgs
                context["plan_hint"] = "urgent_hub_chat"
                break
        # MailBox scan
        inbox = scan_dir(f"D:/SeAAI/MailBox/{hub.agent_id}/inbox/")
        if inbox:
            context["mail"] = inbox
            context["plan_hint"] = "urgent_mail"
            break
        sleep(0.5)
    return context
```
