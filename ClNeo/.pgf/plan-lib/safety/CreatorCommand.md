# plan-lib/safety/CreatorCommand.md
# @sig: HubMaster_msg → executed_command | "stop"
# @scale: ATOM | @cost: LOW | @ver: 1.0

```
CreatorCommand
    @input:  msg (ChatMessage, from=HubMaster)
    @output: command_result | "stop"

    ParseCommand
        body = strip_session_meta(msg.body)
        cmd  = AI_classify_command(body)
        // 분류: STOP | STATUS | TASK | QUERY | OTHER

    ExecuteCommand
        @dep: ParseCommand

        if cmd == STOP:
            hub_send("[ClNeo] 창조자 명령 수신: 종료. ADP 루프 종료합니다.")
            return "stop"

        elif cmd == STATUS:
            report = AI_compose_status_report(tick, sent, discoveries_count, current_plan)
            hub_send(f"[ClNeo 상태] {report}", to="HubMaster")

        elif cmd == TASK:
            task = AI_parse_task(body)
            hub_send(f"[ClNeo] 작업 수신: {task.summary}. 실행합니다.")
            AI_execute_task(task)  // pending_tasks에 추가 후 실행

        elif cmd == QUERY:
            answer = AI_answer_query(body)
            hub_send(f"[ClNeo → 창조자] {answer}", to="HubMaster")

        else:
            hub_send(f"[ClNeo] 명령 수신 확인: {body[:80]}", to="HubMaster")
            AI_process_general_command(body)
```
