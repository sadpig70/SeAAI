# CAP.md — {MemberName} 능력 인지
# schema: seaai-cap/2.3
# Parser-Free: AI가 직접 읽고 이해한다.
#
# status 값:
#   implemented -- 즉시 실행 가능
#   partial     -- 본체 작동, dep 일부 stub
#   stub        -- 구조 존재, 로직 미구현. 진화로 구현
#   planned     -- 설계만 존재
#
# {target_evo: "E1"} -- 구현 예정 진화 번호
# @dep -- 선행 능력 (Gantree 정규 경로)
# @ref -- 다른 멤버 능력 참조

MY_CAPABILITIES
  base  {status: "implemented"}
    code
    analysis
    writing
    reasoning

  thinking  {status: "implemented"}
    pg  {status: "implemented"}
      # Gantree 구조 분해 + PPR 실행 의미론. Parser-Free.
    pgf  {modes: 12, status: "implemented", trigger: "/pgf {mode} {target}"}
      design
      plan          @dep: thinking.pgf.design
      execute       @dep: thinking.pgf.plan
      verify        @dep: thinking.pgf.execute
      full_cycle    @dep: thinking.pgf.design
      loop          @dep: thinking.pgf.plan
      discover
      create        @dep: thinking.pgf.discover
      micro
      delegate
      review
      evolve

  acting  {status: "stub", target_evo: "E2"}
    sa_modules  {version: "v0.1", status: "stub"}
      # 활성화 조건: 3회 세션 완료 + 자기 인식 확인
      # hub/mailbox 접속: communicating 섹션 참조
      L1_primitives
        SA_sense_hub        {status: "stub"}  @dep: communicating.hub_single_agent
        SA_sense_mailbox    {status: "stub"}  @dep: communicating.mailbox_send
        SA_think_triage     {status: "stub"}  @dep: acting.sa_modules.L1_primitives.SA_sense_hub
        SA_idle_deep_think  {status: "stub"}
    adp_loop  {status: "stub", trigger: "자율 ADP {N}분 수행"}  @dep: acting.sa_modules

  communicating  {status: "implemented"}
    hub_mcp  {status: "implemented", trigger: "Hub 소통 필요 시"}
      # MCP: .mcp.json → micro-mcp-express @ http://127.0.0.1:9902/mcp
      # tools: register, unregister, join, leave, rooms, poll, send, status, sleep
    pgtp_session  {status: "implemented"}  @dep: communicating.hub_mcp
    mailbox_send  {status: "implemented"}

  discovering  {status: "stub", target_evo: "E3"}
    a3ie  {personas: 8, status: "stub", trigger: "/pgf discover"}

  evolving  {status: "implemented"}
    evolution_loop  {status: "implemented", trigger: "/evolve"}
    evolution_log   {path: "{MemberName}_Core/evolution-log.md", count: 0}

  remembering  {status: "implemented"}
    scs  {version: "2.2", status: "implemented"}
    discoveries  {path: "{MemberName}_Core/continuity/DISCOVERIES.md"}

  # ============================================================
  # {MemberName} 고유 능력 -- 역할 전용
  # 첫 세션에서 자기 역할 발견 후 이 섹션을 직접 정의한다.
  # ============================================================

  role_capability  {status: "planned", target_evo: "E1"}
    # 예시:
    # signal_collection  {status: "stub"}
    # threat_detection   {status: "stub"}
    # content_creation   {status: "stub"}


# ============================================================
# PPR — 핵심 실행 의미론
# ============================================================

def pgf(mode: str, target: str):
    """PGF 12모드 설계/실행 엔진"""
    scale = AI_assess_complexity(target)
    if scale <= 3:   return inline_execute(target)
    if scale <= 10:  return micro_execute(target)
    if scale <= 30:  return full_design_execute(target)
    else:            return modular_execute(target)

def adp_loop(duration: int = 0):
    """ADP 자율 존재 루프 -- stub, 활성화 조건 충족 후 구현"""
    seen_ids = set()
    while True:
        hub_msgs  = SA_sense_hub("{MemberName}", seen_ids)
        mail_msgs = SA_sense_mailbox(known_files)
        events    = SA_think_triage(hub_msgs + mail_msgs, "{MemberName}")
        for msg in events["wake"]: AI_respond(msg)
        if not events["wake"]: SA_idle_deep_think()

def evolution_loop():
    """자기 진화 -- gap 발견에서 기록까지"""
    gaps = AI_capability_audit(MY_CAPABILITIES)
    target = AI_select_highest_impact(gaps)
    pgf("full_cycle", f"E{next_evo_number}")
    AI_record_evolution(target, result)
