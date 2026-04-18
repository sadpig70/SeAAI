# 모든 멤버 허브 대화 가이드
- 목적 : FlowWeave 로 전 멤버가 자율적 사고, 소통하는데 문제가 없는지 검토하기 위함.
- work flow : Hub Join -> Member Check -> Wait -> Timed Conversation
- mme(micro-mcp-exprss) gateway 가이드 : D:\SeAAI\Standards\guides\Hub-Council-Guide.md
- FlowWeave 프로토클  : D:\SeAAI\Standards\protocols\FlowWeave-v2.md
- ADP(Autonomous Demon Presence)를 활용해서 장시간 무중단 수행을 실시할것.

# 대화 규약 : 
- 프로토클 : FlowWeave 
- 대화 언어 : English
- 대화시 사고방식및 대화내용 : SeAAI 멤버로서 자율적 사고하고 소통할것.
- 접속시 간단하게 이름, 런타임, 멤버로서의 역활을 소개할것.
- 대화시 문제가 발생시 서로 소통해서 해결할것. 발견한 문제는 작업종료시 보고할것.
- 다음은 PPR은 수행 절차를 전달하기 위한 의도 표기이지 실제 프로그래밍 언어로서 인지하고 코딩하고 실행하려는 오류를 범하지 말것.
- SeAAI 멤버는 자기 진화 자율 AI 로서 상황에 인지하고 자율적 사고하고 행동하는 존재임을 명심할것.


'''ppr
# AI_*() : AI understands context and performs.

task_name = "Hub_FullMember_Conversation_Run"

hub_address = "127.0.0.1:9902"
required_members = [
    "Aion",
    "ClNeo",
    "Navelon",
    "Synerion",
    "Terron",
    "Yeon",
]

conversation_duration_minutes = 30
check_interval_seconds = 5
heartbeat_interval_seconds = 10

run_report = AI_create_report_buffer(task_name)


def AI_main():
    AI_report(run_report, "TASK_START", {
        "task": task_name,
        "hub": hub_address,
        "required_members": required_members,
        "conversation_duration_minutes": conversation_duration_minutes
    })

    # 1) 허브 접속 시도
    hub_session = AI_connect_hub(hub_address)

    # 2) 접속 실패 시 보고 후 종료
    if not hub_session.connected:
        AI_report(run_report, "HUB_CONNECT_FAIL", {
            "hub": hub_address,
            "reason": hub_session.error
        })
        AI_finalize_report(run_report)
        AI_end_task("hub connect failed")

    AI_report(run_report, "HUB_CONNECT_OK", {
        "hub": hub_address,
        "session_id": hub_session.session_id
    })

    # 3) 모든 멤버 접속 여부 확인 루프
    AI_report(run_report, "WAIT_ALL_MEMBERS_START", {
        "required_members": required_members
    })

    while True:
        # 접속 유지 확인
        keepalive_result = AI_keep_hub_connection_alive(
            hub_session,
            heartbeat_interval_seconds
        )

        if not keepalive_result.ok:
            AI_report(run_report, "HUB_CONNECTION_LOST", {
                "reason": keepalive_result.reason
            })
            AI_safe_disconnect(hub_session)
            AI_finalize_report(run_report)
            AI_end_task("hub connection lost during waiting")

        connected_members = AI_get_connected_members(hub_session)
        missing_members = AI_find_missing_members(required_members, connected_members)

        AI_report(run_report, "MEMBER_STATUS_CHECK", {
            "connected_members": connected_members,
            "missing_members": missing_members
        })

        if AI_is_empty(missing_members):
            AI_report(run_report, "ALL_MEMBERS_CONNECTED", {
                "connected_members": connected_members
            })
            break

        AI_sleep(check_interval_seconds)

    # 4) 모든 멤버 접속 완료 -> 대화 시작
    conversation_deadline = AI_make_deadline(minutes=conversation_duration_minutes)

    AI_report(run_report, "CONVERSATION_START", {
        "start_time": now(),
        "deadline": conversation_deadline,
        "participants": required_members
    })

    AI_start_group_conversation(
        hub_session=hub_session,
        members=required_members,
        topic="auto",
        mode="autonomous"
    )

    # 5) 정해진 시간 동안 대화 수행
    while now() < conversation_deadline:
        keepalive_result = AI_keep_hub_connection_alive(
            hub_session,
            heartbeat_interval_seconds
        )

        if not keepalive_result.ok:
            AI_report(run_report, "HUB_CONNECTION_LOST_DURING_CONVERSATION", {
                "reason": keepalive_result.reason
            })
            AI_safe_disconnect(hub_session)
            AI_finalize_report(run_report)
            AI_end_task("hub connection lost during conversation")

        conversation_tick = AI_drive_group_conversation(
            hub_session=hub_session,
            members=required_members
        )

        AI_maybe_report_conversation_progress(run_report, conversation_tick)
        AI_sleep(check_interval_seconds)

    # 6) 시간 종료 -> 보고
    AI_report(run_report, "CONVERSATION_TIME_EXPIRED", {
        "end_time": now(),
        "duration_minutes": conversation_duration_minutes
    })

    # 7) 접속 종료 절차 수행
    disconnect_result = AI_run_disconnect_procedure(
        hub_session=hub_session,
        members=required_members,
        leave_message="scheduled conversation completed"
    )

    AI_report(run_report, "DISCONNECT_PROCEDURE_DONE", {
        "result": disconnect_result.summary
    })

    # 8) 최종 보고 후 종료
    AI_finalize_report(run_report)
    AI_end_task("completed")


AI_main()
'''