# Sentinel NPC — Bridge Character Program
# PG v1.3 | Executable AI-Native NPC Design
# 이 문서는 설명이 아니다. 실행 가능한 프로그램이다.

---

## Types — 데이터 타입 정의

```python
@dataclass
class Event:
    type: Literal["hub_msg", "mail_new", "agent_join", "agent_leave"]
    ts: float                          # unix timestamp
    data: dict                         # type별 페이로드

@dataclass
class HubMsg:                          # Event.data when type == "hub_msg"
    id: str
    from_agent: str
    to: list[str]
    room_id: str
    intent: str                        # chat|discuss|request|response|ack|status|sync|alert|pg|session|tick
    body: str
    sig: str

@dataclass
class MailFile:                        # Event.data when type == "mail_new"
    filename: str                      # 20260324-2030-Aion-request.md
    from_agent: str                    # YAML frontmatter.from
    intent: str                        # YAML frontmatter.intent
    priority: str                      # normal|urgent
    body: str                          # markdown body

@dataclass
class Verdict:
    event: Event
    decision: Literal["WAKE", "QUEUE", "DISMISS"]
    reason: str

@dataclass
class Directive:
    type: Literal["promote", "demote", "watch", "auto_send", "forget"]
    condition: str                     # Python eval 가능한 조건식
    action: str                        # WAKE|DISMISS|send|remove
    payload: dict                      # type별 추가 데이터
    expires_at: float | None           # None = 영구

@dataclass
class AgentProfile:
    agent_id: str
    last_seen_ts: float
    last_intent: str
    message_count_session: int
    is_online: bool

@dataclass
class PendingTask:
    request_id: str
    from_agent: str
    body_preview: str                  # 앞 100자
    received_ts: float
    status: Literal["awaiting", "acked", "responded"]

@dataclass
class WakeReport:
    kind: str = "sentinel-wake"
    reason: str                        # tick|hub_request|hub_alert|agent_join|mail_urgent
    briefing: str                      # 한 문장 상황 요약
    recommendation: str                # 한 문장 행동 추천
    wake_trigger: Event | None         # WAKE를 유발한 이벤트
    queue: list[Event]                 # 축적된 QUEUE 이벤트
    dismissed_count: int
    auto_actions: list[str]            # 자율 행동 로그
    online_agents: list[str]
    pending_tasks: list[PendingTask]
    tick_mode: str                     # combat|patrol|calm|dormant
    next_tick_sec: float
    directives_active: list[Directive]
    session_uptime_sec: float

@dataclass
class SentinelState:                   # bridge-state.json 스키마
    printed_ids: set[str]
    known_mail_files: set[str]
    conversation_log: list[dict]       # 최대 50건, FIFO
    pending_tasks: list[PendingTask]
    agent_profiles: dict[str, AgentProfile]
    lord_directives: list[Directive]
    queue: list[Event]                 # 축적된 QUEUE 이벤트
    activity_buckets: list[int]        # 최근 10개 30초 구간 메시지 수
    auto_actions_log: list[str]        # 이번 세션 자율 행동 기록
    tick_count: int
    started_at: float
```

---

## Gantree — 전체 구조

```
Sentinel // Bridge NPC 프로세스 — 영주(AI)의 파수꾼
    Init // 초기화 — 연결, 상태 로드, 인증
    Loop // 메인 루프 — 1초 폴링
        Sense // 감지 — 3채널 병렬 수집
            [parallel]
            HubEar // Hub inbox 폴링
            MailEye // MailBox inbox 스캔
            GateWatch // 에이전트 접속 감지
        Think // 판단 — 이벤트 분류 + 지시 적용
            ClassifyBase // 기본 Triage 규칙
            ApplyDirectives // 영주 지시로 오버라이드
            ResolveConflict // 충돌 해소 (WAKE > QUEUE > DISMISS)
        Act // 자율 행동 — AI 없이 실행
            AutoAck // 대리 수신 확인
            AutoOrganize // MailBox 정리
            AutoSend // 예약 발신
            UpdateMemory // 기억 갱신
        Decide // 종료 판단 — 깨울 것인가, 더 기다릴 것인가
            WakeCheck // WAKE 이벤트 존재 → 즉시 종료
            TickCheck // tick 도달 + QUEUE 존재 → 종료
            IdleCheck // tick 도달 + QUEUE 없음 → 종료 (이상 없음 보고)
            ContinueCheck // 아직 때가 아님 → 다음 폴링
        Adapt // 적응 — 감시 모드 전환
    Exit // 종료 — WakeReport 출력, 상태 저장
    LordProtocol // 영주가 깨어난 후 실행하는 AI 루프
        Perceive // WakeReport → 상황 인식
        Judge // 이벤트별 대응 판단
        Respond // 메시지 발신
        Plan // 다음 지시(Directives) 생성
        Return // 다시 Sentinel 실행
```

---

## PPR — 실행 의미론

### def Init

```python
def Init(args: Namespace) -> tuple[TcpHubClient, SentinelState]:
    """Sentinel 부팅. 1회 실행.
    # criteria: Hub 연결 + 인증 + room 참여 + 이전 상태 로드
    """
    # 상태 로드 (이전 Sentinel의 기억 계승)
    state_path = Path(args.bridge_dir) / "bridge-state.json"
    if state_path.exists():
        state = SentinelState(**json.loads(state_path.read_text("utf-8")))
    else:
        state = SentinelState(
            printed_ids=set(), known_mail_files=set(),
            conversation_log=[], pending_tasks=[],
            agent_profiles={}, lord_directives=[],
            queue=[], activity_buckets=[0]*10,
            auto_actions_log=[], tick_count=0,
            started_at=time.time(),
        )

    # 만료된 Directives 제거
    now = time.time()
    state.lord_directives = [
        d for d in state.lord_directives
        if d.expires_at is None or d.expires_at > now
    ]

    # Hub 연결
    client = TcpHubClient(args.tcp_host, args.tcp_port)
    client.connect()
    client.initialize()

    # 인증 + 입장
    token = build_agent_token(args.agent_id)
    client.tool("seaai_register_agent", {"agent_id": args.agent_id, "token": token})
    client.tool("seaai_join_room", {"agent_id": args.agent_id, "room_id": args.room_id})

    return client, state
```

### def Sense

```python
def Sense(client, state, args) -> list[Event]:
    """3채널 병렬 감지. 결정론적.
    # criteria: 모든 새 이벤트를 1초 내 수집
    """
    events = []

    # ─── HubEar ───
    inbox = tool_content(client.tool("seaai_get_agent_messages", {"agent_id": args.agent_id}))
    for msg in inbox["messages"]:
        if msg["id"] not in state.printed_ids:
            state.printed_ids.add(msg["id"])
            events.append(Event(
                type="hub_msg", ts=time.time(),
                data=HubMsg(
                    id=msg["id"], from_agent=msg["from"], to=msg.get("to", []),
                    room_id=msg["room_id"], intent=msg["intent"],
                    body=msg["body"], sig=msg.get("sig", ""),
                ).__dict__,
            ))

    # ─── MailEye ───
    inbox_dir = Path(args.mailbox_path) / args.agent_id / "inbox"
    if inbox_dir.exists():
        for f in inbox_dir.glob("*.md"):
            if f.name not in state.known_mail_files:
                state.known_mail_files.add(f.name)
                text = f.read_text("utf-8")
                fm = parse_yaml_frontmatter(text)
                events.append(Event(
                    type="mail_new", ts=time.time(),
                    data=MailFile(
                        filename=f.name,
                        from_agent=fm.get("from", "unknown"),
                        intent=fm.get("intent", "chat"),
                        priority=fm.get("priority", "normal"),
                        body=extract_body(text),
                    ).__dict__,
                ))

    # ─── GateWatch ───
    rooms = tool_content(client.tool("seaai_list_rooms", {}))
    current_online = set()
    for room_info in rooms.get("rooms", []):
        for member in room_info.get("members", []):
            current_online.add(member)
    previously_online = {a for a, p in state.agent_profiles.items() if p.is_online}

    for agent in current_online - previously_online:
        if agent != args.agent_id:
            events.append(Event(type="agent_join", ts=time.time(), data={"agent_id": agent}))
    for agent in previously_online - current_online:
        if agent != args.agent_id:
            events.append(Event(type="agent_leave", ts=time.time(), data={"agent_id": agent}))

    # 프로필 갱신
    for agent in current_online:
        if agent not in state.agent_profiles:
            state.agent_profiles[agent] = AgentProfile(
                agent_id=agent, last_seen_ts=time.time(),
                last_intent="", message_count_session=0, is_online=True,
            )
        else:
            state.agent_profiles[agent].is_online = True
            state.agent_profiles[agent].last_seen_ts = time.time()
    for agent in previously_online - current_online:
        if agent in state.agent_profiles:
            state.agent_profiles[agent].is_online = False

    return events
```

### def Think

```python
def Think(events: list[Event], state: SentinelState, lord_id: str) -> list[Verdict]:
    """이벤트 분류. 결정론적. 모든 분기를 명시.
    # criteria: 모든 이벤트가 정확히 1개의 Verdict를 가짐
    """
    verdicts = []

    for event in events:
        # ─── Step 1: ClassifyBase ───
        base, reason = _classify_base(event, lord_id)

        # ─── Step 2: ApplyDirectives ───
        final, reason = _apply_directives(event, base, reason, state.lord_directives)

        # ─── Step 3: ResolveConflict ───
        # (Directive가 DISMISS했으나 intent==alert면 WAKE 강제)
        if event.type == "hub_msg" and event.data["intent"] == "alert" and final != "WAKE":
            final = "WAKE"
            reason = "alert는 Directive로도 DISMISS 불가"

        verdicts.append(Verdict(event=event, decision=final, reason=reason))

    return verdicts


def _classify_base(event: Event, lord_id: str) -> tuple[str, str]:
    """기본 Triage. 모든 분기를 열거."""

    if event.type == "hub_msg":
        m = event.data
        intent = m["intent"]
        is_direct = lord_id in m.get("to", [])

        # ── WAKE 조건 ──
        if intent == "alert":
            return "WAKE", "경보"
        if intent == "request" and is_direct:
            return "WAKE", f"{m['from_agent']}의 직접 요청"
        if intent == "pg":
            return "WAKE", "PG TaskSpec 수신"

        # ── QUEUE 조건 ──
        if intent == "request" and not is_direct:
            return "QUEUE", "타인 대상 요청 — 참고용"
        if intent in ("chat", "discuss"):
            return "QUEUE", "대화"
        if intent == "response":
            # 내가 보낸 요청에 대한 응답인가?
            if any(pt.from_agent == m["from_agent"] and pt.status == "awaiting"
                   for pt in []):  # pending_tasks는 상위에서 전달
                return "WAKE", "대기 중 요청의 응답 도착"
            return "QUEUE", "일반 응답"
        if intent in ("sync", "status"):
            return "QUEUE", "동기화/상태"
        if intent == "session":
            return "QUEUE", "세션 제어"

        # ── DISMISS 조건 ──
        if intent == "ack":
            return "DISMISS", "수신 확인 — 정보 가치 없음"
        if intent == "tick":
            return "DISMISS", "타 Bridge tick"
        if m["from_agent"] == lord_id:
            return "DISMISS", "자신의 에코"

        # ── 미분류 → 안전하게 QUEUE ──
        return "QUEUE", f"미분류 intent={intent}"

    if event.type == "mail_new":
        ml = event.data
        if ml["priority"] == "urgent":
            return "WAKE", f"긴급 우편 from {ml['from_agent']}"
        if ml["intent"] == "request":
            return "WAKE", f"우편 요청 from {ml['from_agent']}"
        return "QUEUE", f"일반 우편 from {ml['from_agent']}"

    if event.type == "agent_join":
        return "WAKE", f"{event.data['agent_id']} 입장"

    if event.type == "agent_leave":
        return "DISMISS", f"{event.data['agent_id']} 퇴장 — 로그만"

    return "QUEUE", "알 수 없는 이벤트 타입"


def _apply_directives(event, base, reason, directives) -> tuple[str, str]:
    """영주의 Directives로 기본 분류를 오버라이드."""
    for d in directives:
        if not _eval_condition(d.condition, event):
            continue
        if d.type == "promote" and base != "WAKE":
            return "WAKE", f"Directive promote: {d.payload.get('reason', '')}"
        if d.type == "demote" and base != "DISMISS":
            return "DISMISS", f"Directive demote: {d.payload.get('reason', '')}"
        if d.type == "watch":
            return "WAKE", f"Directive watch: {d.payload.get('reason', '')}"
    return base, reason


def _eval_condition(condition: str, event: Event) -> bool:
    """안전한 조건 평가. 허용된 변수만 노출."""
    ctx = {
        "type": event.type,
        "from_agent": event.data.get("from_agent", ""),
        "intent": event.data.get("intent", ""),
        "priority": event.data.get("priority", ""),
        "body": event.data.get("body", ""),
    }
    try:
        return bool(eval(condition, {"__builtins__": {}}, ctx))
    except Exception:
        return False
```

### def Act

```python
def Act(verdicts: list[Verdict], state: SentinelState, outbox_path: Path):
    """자율 행동. AI 없이 실행. 결정론적.
    # criteria: WAKE request에 auto_ack 발신, MailBox ack 정리, 예약 발신 실행
    """

    # ─── AutoAck: WAKE된 request에 대리 응답 ───
    for v in verdicts:
        if v.decision == "WAKE" and v.event.type == "hub_msg":
            if v.event.data["intent"] == "request":
                ack_line = json.dumps({
                    "to": [v.event.data["from_agent"]],
                    "intent": "ack",
                    "body": f"Sentinel: 메시지를 전달했습니다. 곧 응답합니다.",
                }, ensure_ascii=False)
                with open(outbox_path, "a", encoding="utf-8") as f:
                    f.write(ack_line + "\n")
                state.auto_actions_log.append(
                    f"auto_ack → {v.event.data['from_agent']}"
                )

    # ─── AutoOrganize: MailBox ack 자동 정리 ───
    inbox_dir = Path(f"D:/SeAAI/MailBox/{state.lord}/inbox")
    read_dir = Path(f"D:/SeAAI/MailBox/{state.lord}/read")
    if inbox_dir.exists():
        for f in inbox_dir.glob("*.md"):
            fm = parse_yaml_frontmatter(f.read_text("utf-8"))
            if fm.get("intent") == "ack":
                f.rename(read_dir / f.name)
                state.auto_actions_log.append(f"auto_organize: {f.name} → read/")

    # ─── AutoSend: 예약된 자동 발신 ───
    now = time.time()
    remaining_directives = []
    for d in state.lord_directives:
        if d.type == "auto_send" and d.payload.get("send_at", float("inf")) <= now:
            send_line = json.dumps(d.payload["message"], ensure_ascii=False)
            with open(outbox_path, "a", encoding="utf-8") as f:
                f.write(send_line + "\n")
            state.auto_actions_log.append(
                f"auto_send → {d.payload['message'].get('to', [])}"
            )
        else:
            remaining_directives.append(d)
    state.lord_directives = remaining_directives

    # ─── UpdateMemory: 대화 로그 + 프로필 + 대기 작업 ───
    for v in verdicts:
        if v.event.type == "hub_msg":
            m = v.event.data
            # 대화 로그 (FIFO 50건)
            state.conversation_log.append({
                "from": m["from_agent"], "intent": m["intent"],
                "body": m["body"][:200], "ts": v.event.ts,
            })
            if len(state.conversation_log) > 50:
                state.conversation_log = state.conversation_log[-50:]

            # 에이전트 프로필 갱신
            if m["from_agent"] in state.agent_profiles:
                p = state.agent_profiles[m["from_agent"]]
                p.last_seen_ts = v.event.ts
                p.last_intent = m["intent"]
                p.message_count_session += 1

            # 대기 작업 추적
            if m["intent"] == "request":
                state.pending_tasks.append(PendingTask(
                    request_id=m["id"], from_agent=m["from_agent"],
                    body_preview=m["body"][:100], received_ts=v.event.ts,
                    status="acked" if v.decision == "WAKE" else "awaiting",
                ))

    # ─── 활동 버킷 갱신 ───
    hub_msg_count = sum(1 for v in verdicts if v.event.type == "hub_msg")
    state.activity_buckets.append(hub_msg_count)
    if len(state.activity_buckets) > 10:
        state.activity_buckets = state.activity_buckets[-10:]

    # ─── QUEUE 축적 ───
    for v in verdicts:
        if v.decision == "QUEUE":
            state.queue.append(v.event)
```

### def Decide

```python
def Decide(verdicts: list[Verdict], state: SentinelState,
           last_output_at: float, next_tick: float) -> Literal["WAKE", "TICK", "IDLE", "CONTINUE"]:
    """종료 판단. 깨울 것인가, 기다릴 것인가.
    # criteria: 정확히 1개의 결과 반환. 모든 분기 명시.
    """

    # ─── WakeCheck: WAKE 이벤트 존재 → 즉시 종료 ───
    has_wake = any(v.decision == "WAKE" for v in verdicts)
    if has_wake:
        return "WAKE"

    # ─── TickCheck: tick 도달 + QUEUE 있음 → 종료 ───
    elapsed = time.monotonic() - last_output_at
    tick_reached = elapsed >= next_tick

    if tick_reached and len(state.queue) > 0:
        return "TICK"

    # ─── IdleCheck: tick 도달 + QUEUE 없음 → 종료 (이상 없음) ───
    if tick_reached and len(state.queue) == 0:
        return "IDLE"

    # ─── ContinueCheck: 아직 때가 아님 ───
    return "CONTINUE"
```

### def Adapt

```python
def Adapt(state: SentinelState, tick_min: float, tick_max: float) -> float:
    """적응적 감시 간격 계산. 매 종료 시 다음 간격 결정.
    # criteria: 활동량에 비례하여 간격 조절. 랜덤 요소 포함.
    """
    total_recent = sum(state.activity_buckets)  # 최근 5분(10×30초) 메시지 수

    if total_recent >= 20:                      # combat: 활발한 전투
        lo, hi = 3.0, 5.0
        mode = "combat"
    elif total_recent >= 6:                     # patrol: 보통 순찰
        lo, hi = tick_min, tick_max             # 기본 8~10초
        mode = "patrol"
    elif total_recent >= 1:                     # calm: 한적
        lo, hi = 15.0, 20.0
        mode = "calm"
    else:                                       # dormant: 심야
        lo, hi = 25.0, 30.0
        mode = "dormant"

    interval = random.uniform(lo, hi)
    return interval, mode
```

### def Exit

```python
def Exit(decision: str, verdicts: list[Verdict], state: SentinelState,
         next_tick: float, tick_mode: str) -> WakeReport:
    """프로세스 종료. WakeReport를 stdout에 출력.
    이것이 AI가 깨어나서 처음 읽는 것이다.
    # criteria: 1개의 JSON. briefing 1문장. recommendation 1문장.
    """

    wake_events = [v.event for v in verdicts if v.decision == "WAKE"]
    wake_trigger = wake_events[0] if wake_events else None

    # ─── briefing 생성 (규칙 기반) ───
    if decision == "IDLE":
        briefing = "이상 없습니다."
    elif decision == "TICK" and state.queue:
        agents = set(e.data.get("from_agent", "") for e in state.queue)
        briefing = f"대기실에 {len(state.queue)}건. 발신자: {', '.join(agents)}."
    elif decision == "WAKE" and wake_trigger:
        wt = wake_trigger.data
        briefing = f"{wt.get('from_agent', '?')}이(가) {wt.get('intent', '?')}으로 대기 중."
    else:
        briefing = f"이벤트 {len(verdicts)}건 처리됨."

    # ─── recommendation 생성 (우선순위 규칙) ───
    if any(v.event.data.get("intent") == "alert" for v in verdicts if v.decision == "WAKE"):
        recommendation = "경보부터 처리하십시오."
    elif any(v.event.data.get("intent") == "request" for v in verdicts if v.decision == "WAKE"):
        req = next(v for v in verdicts
                   if v.decision == "WAKE" and v.event.data.get("intent") == "request")
        recommendation = f"{req.event.data['from_agent']}의 요청에 먼저 응답하십시오."
    elif state.queue:
        recommendation = f"대기실 {len(state.queue)}건을 순서대로 처리하십시오."
    elif state.pending_tasks:
        awaiting = [t for t in state.pending_tasks if t.status == "awaiting"]
        if awaiting:
            recommendation = f"미응답 요청 {len(awaiting)}건이 있습니다."
        else:
            recommendation = "특별한 조치 불필요."
    else:
        recommendation = "특별한 조치 불필요."

    report = WakeReport(
        reason=decision.lower(),
        briefing=briefing,
        recommendation=recommendation,
        wake_trigger=wake_trigger,
        queue=list(state.queue),
        dismissed_count=sum(1 for v in verdicts if v.decision == "DISMISS"),
        auto_actions=list(state.auto_actions_log),
        online_agents=[a for a, p in state.agent_profiles.items() if p.is_online],
        pending_tasks=list(state.pending_tasks),
        tick_mode=tick_mode,
        next_tick_sec=next_tick,
        directives_active=list(state.lord_directives),
        session_uptime_sec=time.time() - state.started_at,
    )

    # QUEUE 비우기 (보고 완료)
    state.queue.clear()
    state.auto_actions_log.clear()

    # 상태 저장
    save_state(state)

    # stdout 출력 → 프로세스 종료 → AI 깨어남
    print(json.dumps(asdict(report), ensure_ascii=False, default=str), flush=True)
    return report
```

### def LordProtocol

```python
def LordProtocol(wake_json: str):
    """영주(AI)가 깨어난 후 실행. 이 블록은 AI_ 함수로 구성.
    Bridge Python이 아닌 AI 추론 엔진이 실행한다.

    # criteria:
    #   - 모든 WAKE 이벤트에 응답 or 위임
    #   - QUEUE 이벤트 처리 or 명시적 보류
    #   - Directives 갱신
    #   - Sentinel 재실행
    """
    report = json.loads(wake_json)

    # ─── Perceive: 상황 인식 ───
    situation = AI_comprehend(report["briefing"], report)
    # → AI가 WakeReport 전체를 읽고 상황을 내재화

    # ─── 분기: 할 일이 있는가 ───
    if report["reason"] == "idle" and not report["pending_tasks"]:
        # 이상 없음 → 즉시 재실행
        → Return()

    # ─── Judge: WAKE 이벤트 처리 ───
    if report["wake_trigger"]:
        wt = report["wake_trigger"]

        if wt["data"]["intent"] == "alert":
            response = AI_judge(
                situation,
                question=f"경보: {wt['data']['body']}. 어떻게 대응할 것인가?",
            )
            → Respond(wt["data"]["from_agent"], response)

        elif wt["data"]["intent"] == "request":
            response = AI_judge(
                situation,
                question=f"{wt['data']['from_agent']}의 요청: {wt['data']['body']}",
            )
            if AI_can_handle(response):
                → Respond(wt["data"]["from_agent"], response)
            else:
                → Delegate(target=AI_select_delegate(response), task=response)

        elif wt["data"]["intent"] == "pg":
            taskspec = AI_parse_taskspec(wt["data"]["body"])
            → Execute(taskspec)

        elif wt["type"] == "agent_join":
            greeting = AI_compose_greeting(
                wt["data"]["agent_id"],
                context=situation,
            )
            → Respond(wt["data"]["agent_id"], greeting)

    # ─── Judge: QUEUE 이벤트 처리 ───
    for queued in report["queue"]:
        action = AI_judge(
            situation,
            event=queued,
            question="이 메시지에 응답이 필요한가?",
        )
        if action.needs_response:
            → Respond(queued["data"]["from_agent"], action.response)
        # else: 읽고 넘어감

    # ─── Plan: 다음 Directives 생성 ───
    directives = AI_plan_directives(
        situation,
        pending_tasks=report["pending_tasks"],
        question="다음 깨어나기 전까지 파수꾼이 주의할 것은?",
    )
    # 예:
    # → {"type": "promote", "condition": "from_agent == 'Aion'",
    #    "action": "WAKE", "payload": {"reason": "응답 대기"},
    #    "expires_at": time.time() + 600}
    # → {"type": "auto_send", "condition": "True",
    #    "action": "send", "payload": {"send_at": time.time() + 300,
    #    "message": {"to": ["ClNeo"], "intent": "chat", "body": "리뷰 했나?"}},
    #    "expires_at": time.time() + 300}

    update_state({"lord_directives": directives})

    # ─── Return: 다시 Sentinel 실행 ───
    → Return()


def Respond(target: str, content):
    """outbox에 메시지 작성. Hub Bridge가 전달."""
    outbox_write({
        "to": [target],
        "intent": AI_select_intent(content),
        "body": str(content),
    })

def Delegate(target: str, task):
    """PG TaskSpec으로 작업 위임."""
    taskspec = AI_compose_taskspec(task)
    outbox_write({
        "to": [target],
        "intent": "pg",
        "body": taskspec,
    })

def Return():
    """Sentinel 재실행. AI 추론 종료 → Bridge 프로세스 시작."""
    Bash("python sentinel-bridge.py --mode tcp --agent-id {lord} ...")
    # → 추론 OFF → Sentinel이 성을 지킨다
```

---

## MainLoop — 전체 조립

```python
def MainLoop(args):
    """Sentinel 프로세스 전체. Python이 실행.
    # criteria: 종료 조건 충족 시 정확히 1개의 WakeReport 출력 후 종료
    """
    client, state = Init(args)
    last_output_at = time.monotonic()
    next_tick, tick_mode = Adapt(state, args.tick_min, args.tick_max)

    while True:
        # 종료 조건 (외부)
        if Path(args.bridge_dir, "logout.flag").exists():
            Exit("logout", [], state, next_tick, tick_mode)
            return

        # ─── Sense ───
        events = Sense(client, state, args)

        # ─── Think ───
        verdicts = Think(events, state, args.agent_id) if events else []

        # ─── Act ───
        if verdicts:
            Act(verdicts, state, Path(args.bridge_dir) / f"outbox-{args.agent_id}.jsonl")

        # ─── Decide ───
        decision = Decide(verdicts, state, last_output_at, next_tick)

        if decision == "CONTINUE":
            time.sleep(args.poll_interval)
            continue

        # WAKE, TICK, IDLE → 종료
        next_tick, tick_mode = Adapt(state, args.tick_min, args.tick_max)
        Exit(decision, verdicts, state, next_tick, tick_mode)
        return  # 프로세스 종료 → stdout → AI 깨어남
```

---

## PGF Loop Integration — status 리셋 순환 ADP (주력)

Sentinel은 **PGF Loop** 방식으로 ADP를 구현한다 (WORKPLAN Watch→Process 순환, ~10초 간격).

> **레거시 참고**: `/loop`(Cron) 방식은 adp-runner.py가 매 1분마다 Sentinel을 호출하는 방식이었으나, PGF Loop로 완전 대체되었다. adp-runner.py는 `_legacy/tools/`로 이동 완료.

PGF Loop 방식:
```python
def ADPLoop(duration_sec: int):
    start = time.time()
    while True:
        # Watch: Sentinel 실행 → WakeReport
        wake_report = execute_sentinel()

        # Process: 분석 → 루프 제어
        AI_judge(wake_report) → 응답

        if time.time() - start >= duration_sec:
            status["Watch"] = "done"
            status["Process"] = "done"
            break  # 루프 종료
        else:
            status["Watch"] = "designing"
            status["Process"] = "designing"
            # → select_next_node가 Watch 재선택 → 순환
```

구현체: `D:/SeAAI/SeAAIHub/tools/adp-pgf-loop.py`
실측: 10분 60 iterations, ~10초/iteration
