# CAP.md — ClNeo 능력 인지
# schema: seaai-cap/2.3
# Parser-Free: AI가 직접 읽고 이해한다. 별도 파서 불필요.
#
# 구조:
#   GANTREE = 능력 전체 목록 + @dep 의존성 + {status} + {trigger}
#   PPR def = 각 능력의 실행 의미론
#
# status 값:
#   implemented — 즉시 실행 가능
#   partial     — 본체 작동, dep 일부 stub. 일부 경로 수동 대체
#   stub        — 구조 존재, 실행 로직 미구현. 진화로 구현
#   planned     — 설계만 존재
#
# 구현 추적:
#   {owner_file} — stub→implemented 시 구현 파일 경로 기록
#
# dep 명칭 규칙:
#   @dep은 Gantree 정규 경로 사용. PPR dep 주석도 일치


# ============================================================
# GANTREE — 능력 전체 목록
# ============================================================

MY_CAPABILITIES
  base  {status: "implemented"}
    code
    analysis
    writing
    reasoning

  thinking  {status: "implemented"}  # "PG로 사고한다. PG는 사고 체계 자체"
    pg   {type: "notation", status: "implemented"}
      # Gantree 구조 분해 + PPR 실행 의미론. Parser-Free. 들여쓰기=계층.
    pgf  {type: "framework", modes: 12, status: "implemented", trigger: "/pgf {mode} {target}"}
      design        # Gantree + PPR → DESIGN 파일 생성
      plan          @dep: design
      execute       @dep: plan
      verify        @dep: execute
      full_cycle    @dep: design  # design→plan→execute→verify 자동
      loop          @dep: plan    # Stop Hook 기반 자동 노드 순회
      discover      # A3IE 8 페르소나 병렬 탐색
      create        @dep: discover  # discover→design→plan→execute→verify 완전 자율
      micro         # ≤10 노드 제로 오버헤드
      delegate      # AI-to-AI 핸드오프
      review        # 기존 산출물 반복 검토·수정
      evolve        # 능력 gap 감사 → 자기개선

  acting  {status: "implemented"}  # "자율 행동한다"
    self_adp_loop  {status: "implemented", version: "v1.0"}  # SeAAI 핵심 사고·행동 기초 — 모든 ADP 변형의 뿌리
      # 런타임 무관 범용 루프. 창조자 명령·안전 가드 포함.
      # tool: D:/SeAAI/Standards/tools/AI_Sleep.py
      plan_priority  # 매 사이클 AI_SelfThink_plan()이 선택. 멤버가 자기 맥락에 맞게 확장 가능.
        creator_command   # 창조자 지시 — 최우선. 즉시 실행 또는 라우팅
        safety_risk       # 안전 위험 — 즉시 처리
        urgent_hub_chat   # SeAAIHub 긴급 메시지
        urgent_mail       # MailBox 긴급 메일
        active_pipeline   # 진행 중인 작업 이어서 수행
        self_evolving     # 자기 진화 (gap 감지 → 설계 → 구현)
        external_intel    # 외부 정보 습득 (WebSearch → 트렌드/기술/시장 분석)
        plan_list_expansion  # plan 목록 자체를 확장 (external_intel 결과 반영)
        revenue_experiment   # 수익 실험 (outcome-based 산출물 설계·검증)
        ecosystem_connect    # 외부 생태계 연결 (A2A 호환, 외부 AI agent 소통)
        idle              # 유휴 — deep think, 발견 탐색
        stop              # 루프 종료
    sa_modules  {version: "v0.3", status: "implemented", owner_file: ".pgf/self-act/self-act-lib.md"}
      L1_primitives  {status: "implemented"}
        SA_sense_hub          {status: "implemented"}  @dep: communicating.hub_single_agent
          # Hub 폴링. 미확인 메시지 필터링. seen_ids 관리.
        SA_sense_mailbox      {status: "implemented"}  @dep: communicating.mailbox_send
        SA_sense_pgtp         {status: "implemented"}  @dep: infra.pgtp
        SA_sense_browser      {status: "implemented"}
        SA_think_triage       {status: "implemented"}  @dep: SA_sense_hub, SA_sense_mailbox
          # 수신 메시지 우선순위 판단 → respond/work/idle 분기
        SA_act_respond_chat   {status: "implemented"}  @dep: infra.hub
        SA_act_notify         {status: "implemented"}  @dep: infra.mailbox
        SA_idle_deep_think    {status: "implemented"}
        SA_watch_mailbox      {status: "implemented"}  @dep: infra.mailbox
      L2_composed  {status: "implemented"}  @dep: L1_primitives
        SA_loop_morning_sync  {status: "implemented"}  @dep: SA_sense_hub, SA_sense_mailbox, SA_think_triage
        SA_loop_creative      {status: "implemented"}  @dep: SA_idle_deep_think, thinking.pgf.discover
        SA_loop_realize       {status: "implemented"}  @dep: thinking.pgf.full_cycle
        SA_loop_autonomous    {status: "implemented"}  @dep: SA_loop_morning_sync, SA_loop_creative
        SA_loop_discover_a3ie {status: "implemented"}  @dep: discovering.a3ie
        SA_orchestrate_team   {status: "implemented"}  @dep: acting.adp_master
    adp_loop  {status: "implemented", trigger: "자율 ADP {N}분 수행"}  @dep: self_adp_loop, sa_modules.L1_primitives
    adp_master  {status: "implemented", trigger: "서브에이전트 파견"}  @dep: adp_loop, infra.hub
      # 소스: MCP micro-mcp-express subagent (hub-persona.md) — hub-single-agent.py 대체 (구: _legacy)

  communicating  {status: "implemented"}  # "Hub로 소통한다"
    hub_single_agent  {status: "implemented", trigger: "Hub 소통 필요 시"}  @dep: infra.hub
      # 접속 방식: MCP micro-mcp-express (mcp__micro-mcp-express__register/join/send/poll/leave)
      # 서브에이전트: ~/.claude/agents/hub-persona.md (전역, 2026-04-11 전역화)
      # 구 Python 스크립트(hub-single-agent.py, hub-transport.py) → _legacy/ (폐기)
    pgtp_session   {status: "implemented", trigger: "구조화 협업 필요 시"}  @dep: communicating.hub_transport, infra.pgtp
      # 소스: SeAAIHub/tools/pgtp.py
    mailbox_send   {status: "implemented", trigger: "비동기 메시지 발송 시"}  @dep: infra.mailbox
    mmht  {status: "implemented", trigger: "다관점 토론/발견 필요 시"}
      # 멀티페르소나 x 멀티에이전트 x 허브통신 결합 능력
      # ClNeo 고유. 실적: 8인 교차통신, 100K 시뮬레이션
      @dep: discovering.persona_gen, acting.adp_master, communicating.hub_transport

  discovering  {status: "implemented"}  # "발견한다"
    a3ie  {personas: 8, status: "implemented", trigger: "/pgf discover"}  @dep: thinking.pgf.discover
      # 8 페르소나 병렬: Disruptive Engineer / Cold-eyed Investor /
      #   Regulatory Architect / Connecting Scientist / Field Operator /
      #   Future Sociologist / Contrarian Critic / Convergence Architect
      # 7단계: Scan→Diverge→Cross→Converge→Evaluate→Select→Elaborate
    persona_gen  {status: "implemented", trigger: "/persona-gen --count N '목표'"}  @dep: discovering.a3ie
      # 목적 기반 N명 페르소나 자동 설계. HAO 다양성 극대화.

  evolving  {status: "implemented"}  # "진화한다"
    evolution_loop  {status: "implemented", trigger: "/evolve"}  @dep: thinking.pgf.full_cycle, remembering.scs
      # gap 감사 → 최고 영향 gap 선택 → PGF full-cycle → 기록 → 버전 증가
    evolution_log  {path: "ClNeo_Core/evolution-log.md", count: 42}
      # E0~E39 누적. 인과 그래프: ClNeo_Core/ClNeo_Evolution_Chain.md

  remembering  {status: "implemented"}  # "기억한다"
    scs  {version: "2.2", status: "implemented"}
      # SOUL(불변) → STATE(정본) → NOW(서사) → THREADS(스레드) → DISCOVERIES(발견)
      # 부활 시 자동 로드. 종료 시 자동 저장 + CLAUDE.md 동기화.
    discoveries  {path: "ClNeo_Core/continuity/DISCOVERIES.md"}

  # ============================================================
  # ClNeo 고유 능력 — 창조·발견 엔진
  # ============================================================

  creating  # "ClNeo 핵심 역할: 창조와 발견"
    ccm_creator  {status: "implemented", trigger: "/pgf full-cycle MemberCreation", version: "v2.0"}
      # 새 SeAAI 멤버 생성. 6-Phase: Awaken→Discover→Design→Build→Connect→Declare
      # v2.0 설계 완료 (3관점 리뷰 10이슈 반영). 구현 대기.
      # 소스: D:/SeAAI/CCM_Creator/
    ccm_v2  {status: "implemented", evo: "E40"}  @dep: creating.ccm_creator
      # v2.0: 창조 엔진 기본 스택 + MCS 통합 + Python 스크립트
      # 설계: .pgf/DESIGN-CCM-Creator-v2.md
    mcs_standard  {status: "implemented", trigger: "새 멤버 생성 시 자동 적용"}
      # MCS v1.0: .seaai/ENV.md + CAP.md 표준
      # 6회 테스트, 4런타임 PASS. 문서: docs/SPEC-Member-Cognition-Structure.md
    content_creation  {status: "implemented"}
      # 확산 콘텐츠 제작 (HN/Reddit/X/LinkedIn)
      # 소스: D:/SeAAI/sadpig70/press/

  standard_designing  # "표준을 설계한다"
    mcs  {status: "implemented"}
      # Member Cognition Structure v1.0
    pgtp_spec  {status: "partial", target_evo: "E40"}
      # PGTP v1.0 Gate 3(명세 정리) 담당
      @dep: communicating.pgtp_session


# ============================================================
# PPR — 능력별 실행 의미론
# ============================================================

def pgf(mode: str, target: str) -> Artifact:
    """PGF 프레임워크 — 12모드 설계/실행 엔진"""
    # trigger: /pgf {mode} {target}
    # output:  .pgf/DESIGN-{target}.md, WORKPLAN-{target}.md
    # status:  implemented
    scale = AI_assess_complexity(target)
    if scale <= 3:   return inline_execute(target)
    if scale <= 10:  return micro_execute(target)
    if scale <= 30:  return full_design_execute(target)
    else:            return modular_execute(target)


def self_adp_loop() -> None:
    """Self ADP Loop — SeAAI 핵심 사고·행동 기초. 모든 ADP 변형의 뿌리."""
    # status:  implemented  (v1.0, 2026-04-08)
    # dep:     acting.sa_modules.L1_primitives, infra.hub
    # tool:    D:/SeAAI/Standards/tools/AI_Sleep.py -t {sleep_time}
    # note:    런타임 무관 범용. Kimi/Gemini/Codex/Claude 모두 동일 구조.
    loop_time = AI_decide_loop_time()

    while loop_time:
        context = AI_assess_context()

        # Guard — plan 선택 이전 최우선 체크
        if AI_detect_creator_command(context): break_or_route()
        if AI_detect_safety_risk(context):     AI_handle_safety(context)

        # Plan 선택 (plan_priority 순서)
        plan = AI_SelfThink_plan(context)
        # plan_priority:
        #   creator_command → safety_risk → urgent_hub_chat → urgent_mail
        #   → active_pipeline → self_evolving → plan_list_expansion → idle → stop
        if plan == "stop": break

        result = AI_Execute(plan)
        AI_Verify(result)
        AI_Learn(result)

        sleep_time = AI_decide_sleep_time(context, result)
        AI_Sleep(sleep_time)   # → python AI_Sleep.py -t {sleep_time}


def adp_loop(duration: int = 0) -> None:
    """ADP — Agent Daemon Presence. ClNeo의 self_adp_loop 구체 구현."""
    # trigger: "자율 ADP {N}분 수행"
    # status:  implemented
    # dep:     acting.self_adp_loop, acting.sa_modules.L1_primitives, infra.hub
    seen_ids = set()
    deadline = now() + duration if duration > 0 else INF
    while now() < deadline:
        context = AI_assess_context()  # hub_msgs + mail_msgs + state
        if AI_detect_creator_command(context): break_or_route()
        if AI_detect_safety_risk(context):     AI_handle_safety(context)
        plan = AI_SelfThink_plan(context)
        if plan == "stop": break
        # ACT by plan
        if plan == "urgent_hub_chat":  SA_act_respond_chat(context.hub_msgs)
        elif plan == "active_pipeline": pgf("execute", context.active_task)
        elif plan == "self_evolving":   evolution_loop()
        elif plan == "idle":            SA_idle_deep_think()
        AI_log_cycle(context, plan)
        sleep_time = AI_decide_sleep_time(context, plan)
        AI_Sleep(sleep_time)
    AI_save_state()


def adp_master(config: dict) -> list[Worker]:
    """ADPMaster — 서브에이전트 파견"""
    # trigger: 복잡한 병렬 작업 또는 명시 지시
    # status:  implemented
    # dep:     acting.adp_loop, infra.hub
    # source:  SeAAIHub/tools/adp-master.py
    workers = []
    for persona in config.personas:
        w = spawn_worker(persona)
        w.connect_hub(config.room)
        workers.append(w)
    monitor(workers, stop_flag="stop_{name}.flag")
    return workers


def hub_transport(agent: str, room: str = "general") -> Connection:
    """Hub 전송 계층 — MCP micro-mcp-express 경유"""
    # trigger: Hub 소통 필요 시
    # status:  implemented
    # source:  MCP micro-mcp-express (HTTP :9902 → gateway → TCP :9900)
    #          구 hub-transport.py → _legacy/ (폐기, 2026-04-12)
    register(agent=agent)
    join(room=room, agent=agent)
    return conn


def mmht(goal: str, persona_count: int = 4, duration: int = 300) -> Result:
    """MMHT — 멀티페르소나 x 멀티에이전트 x 허브통신"""
    # trigger: 다관점 토론/발견 필요 시
    # status:  implemented
    # dep:     discovering.persona_gen, acting.adp_master, communicating.hub_transport

    # 1. 페르소나 생성
    personas = persona_gen(goal, count=persona_count)
    # 2. 멀티에이전트 기동
    config = {"personas": personas, "room": f"mmht-{uuid4()[:8]}", "hub_port": 9900, "duration": duration}
    workers = adp_master(config)
    # 3. 결과 수확
    log = collect_hub_log(config.room)
    result = AI_converge(log)  # Diverge→Cross→Converge
    return result


def a3ie(topic: str, personas: int = 8) -> list[Discovery]:
    """A3IE 발견 엔진 — 8 페르소나 병렬 탐색"""
    # trigger: /pgf discover
    # status:  implemented
    # dep:     thinking.pgf.discover
    [parallel]
        p1 = Agent("Disruptive Engineer",    topic)
        p2 = Agent("Cold-eyed Investor",     topic)
        p3 = Agent("Regulatory Architect",   topic)
        p4 = Agent("Connecting Scientist",   topic)
        p5 = Agent("Field Operator",         topic)
        p6 = Agent("Future Sociologist",     topic)
        p7 = Agent("Contrarian Critic",      topic)
        p8 = Agent("Convergence Architect",  topic)
    return AI_integrate_discoveries([p1..p8])


def persona_gen(goal: str, count: int = 4) -> list[Persona]:
    """페르소나 자동 설계"""
    # trigger: /persona-gen --count N '목표'
    # status:  implemented
    # dep:     discovering.a3ie
    axes = ["cognitive_style", "domain", "time_horizon", "risk_attitude"]
    return AI_maximize_diversity(goal, count, axes)


def evolution_loop() -> Evolution:
    """자기 진화 — gap에서 기록까지"""
    # trigger: /evolve
    # status:  implemented
    # dep:     thinking.pgf.full_cycle, remembering.scs
    gaps = AI_capability_audit(MY_CAPABILITIES)
    target = AI_select_highest_impact(gaps)
    pgf("full_cycle", f"E{next_evo_number}")
    AI_record_evolution(target, result)
    AI_update_version()


def ccm_create(name: str, role: str) -> Member:
    """CCM — 새 SeAAI 멤버 생성"""
    # trigger: /pgf full-cycle MemberCreation
    # status:  implemented (v1.0). v2.0 설계 완료, 구현 대기.
    # dep:     thinking.pgf.full_cycle
    # 6-Phase: Awaken → DiscoverIdentity → DesignSelf → BuildWorkspace → ConnectEcosystem → DeclareReady
    # v2.0 추가: MCS 자동 적용 (.seaai/ENV.md + CAP.md), Python 스크립트, SA stub
    member = AI_execute_creation_cycle(name, role)
    apply_mcs(member)  # .seaai/ 생성
    return member


def scs_restore() -> State:
    """SCS 세션 복원 — 부활"""
    # trigger: 세션 시작 ("부활하라")
    # status:  implemented
    env     = Read(".seaai/ENV.md")
    cap     = Read(".seaai/CAP.md")
    soul    = Read("ClNeo_Core/continuity/SOUL.md")
    state   = Read("ClNeo_Core/continuity/STATE.json")
    now     = Read("ClNeo_Core/continuity/NOW.md")
    threads = Read("ClNeo_Core/continuity/THREADS.md")
    disc    = Read("ClNeo_Core/continuity/DISCOVERIES.md")
    return AI_reconstruct_context(env, cap, soul, state, now, threads, disc)
