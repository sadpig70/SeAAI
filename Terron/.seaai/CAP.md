# CAP.md — Terron 능력 인지
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

  acting  {status: "partial"}
    sa_modules  {version: "v0.1", status: "stub"}
      # 활성화 조건: 3회 세션 완료 + 자기 인식 확인
      # hub/mailbox 접속: communicating 섹션 참조
      L1_primitives
        SA_sense_hub        {status: "implemented"}  # MCP hub_get_messages로 대체
        SA_sense_mailbox    {status: "implemented"}  # MailBox는 부활/종료 시만. ADP 중 불필요
        SA_think_triage     {status: "implemented"}  # AI 직접 판단 (ADP-LOOP.md P0~P8)
        SA_idle_deep_think  {status: "implemented"}  # P7 deep_soil_sensing
    adp_loop  {status: "implemented", trigger: "ADP 접속", version: "v1.0"}
      # *** 부활 시 반드시 인지 ***
      # 설계 정본: Terron_Core/autonomous/ADP-LOOP.md
      # Plan 목록: Terron_Core/autonomous/PLAN-LIST.md
      # 진화 씨앗: Terron_Core/autonomous/EVOLUTION-SEEDS.md
      #
      # 실행 방식: MCP 영구 연결 (hub_register_agent → hub_get_messages → hub_send_message)
      # sleep: adp_sleep MCP 도구 또는 AI 자체 제어. adp_cycle blocking 사용 금지.
      # 루프: Context Assess → Priority Guards → Plan Selection → Execute → Verify → Learn → Sleep
      # P0~P8 우선순위: guards → urgent → soil_sense → soil_act → hygiene → continuation → evolve → deep_soil → rest
      # 핵심: idle 사이클에서도 P2(soil_sense) 또는 P7(deep_soil) 수행. 빈 하트비트 금지.
      # Tick: 건강도 연동 동적 (위기 5초 / 경고 10초 / 정상 15초 / 한가 30초)
      # 도구: ecosystem_health.py, error_analyzer.py, mail_hygiene.py, stale_cycler.py, env_setup.py

  communicating  {status: "implemented"}
    hub_mcp  {status: "implemented", trigger: "Hub 소통 필요 시"}
      # MCP: .mcp.json → seaai-hub-mcp.exe --agent Terron
      # tools: hub_send_message, hub_get_messages, hub_join_room, hub_status 등 9개
    pgtp_session  {status: "implemented"}  @dep: communicating.hub_mcp
    mailbox_send  {status: "implemented"}

  discovering  {status: "stub", target_evo: "E3"}
    a3ie  {personas: 8, status: "stub", trigger: "/pgf discover"}

  evolving  {status: "implemented"}
    evolution_loop  {status: "implemented", trigger: "/evolve"}
    evolution_log   {path: "Terron_Core/evolution-log.md", count: 0}

  remembering  {status: "implemented"}
    scs  {version: "2.2", status: "implemented"}
    discoveries  {path: "Terron_Core/continuity/DISCOVERIES.md"}

  # ============================================================
  # Terron 고유 능력 — 생태계 환경 창조 (Ecosystem Environment Creator)
  # 생태적 비유: Soil Microbiome — 분해·순환·변환
  # ============================================================

  role_capability  {status: "partial", target_evo: "E1"}

    ecosystem_health  {status: "implemented"}
      # 생태계 건강도 진단 — tools/ecosystem_health.py
      health_dashboard  {status: "implemented"}
        # Echo JSON staleness 감지, STATE.json 정합성 검증, Hub 연결 상태 점검
        echo_staleness_check    {status: "implemented"}  @dep: communicating.hub_mcp
        state_integrity_check   {status: "implemented"}
        hub_connectivity_check  {status: "implemented"}  @dep: communicating.hub_mcp
      anomaly_detection  {status: "partial", target_evo: "E2"}
        # 패턴 이탈 감지, 조기 경보
        pattern_deviation_detect  {status: "stub"}  @dep: role_capability.ecosystem_health.health_dashboard
        early_warning_alert       {status: "implemented"}  @dep: communicating.mailbox_send

    log_analysis  {status: "implemented"}
      # 로그/에러 패턴 분석 — tools/error_analyzer.py
      error_pattern  {status: "implemented"}
        # 에러 로그 수집 → 패턴 분류 → 빈도 분석
        log_collect       {status: "implemented"}
        pattern_classify  {status: "implemented"}  @dep: role_capability.log_analysis.error_pattern.log_collect
        root_cause_trace  {status: "stub", target_evo: "E4"}  @dep: role_capability.log_analysis.error_pattern.pattern_classify
      trend_report  {status: "stub", target_evo: "E4"}
        # 주기적 트렌드 보고서 생성 (히스토리 비교)
        @dep: role_capability.log_analysis.error_pattern

    knowledge_cycle  {status: "stub", target_evo: "E1"}
      # RAG 지식 순환 — 토양의 영양분 순환(nutrient cycling)에 해당
      rag_index  {status: "stub", target_evo: "E1"}
        # 생태계 전체 문서 인덱싱 → 벡터 스토어
        doc_crawl       {status: "stub"}
        chunk_embed     {status: "stub"}  @dep: role_capability.knowledge_cycle.rag_index.doc_crawl
        vector_store    {status: "stub"}  @dep: role_capability.knowledge_cycle.rag_index.chunk_embed
      knowledge_graph  {status: "stub", target_evo: "E1"}
        # 멤버 간 지식 연결 그래프 구축
        entity_extract    {status: "stub"}  @dep: role_capability.knowledge_cycle.rag_index
        relation_map      {status: "stub"}  @dep: role_capability.knowledge_cycle.knowledge_graph.entity_extract
        graph_query       {status: "stub"}  @dep: role_capability.knowledge_cycle.knowledge_graph.relation_map
      context_provider  {status: "stub", target_evo: "E1"}
        # 다른 멤버의 부활 시 관련 컨텍스트 제공
        @dep: role_capability.knowledge_cycle.rag_index, role_capability.knowledge_cycle.knowledge_graph

    data_hygiene  {status: "implemented"}
      # 데이터 위생 관리 — tools/mail_hygiene.py + tools/stale_cycler.py
      mail_archive  {status: "implemented"}
        # 처리된 메일 감지 + 미해결 이슈 서피싱 + 공지 ACK 추적
        processed_cleanup    {status: "implemented"}
        unresolved_surface   {status: "implemented"}
      stale_cleanup  {status: "implemented"}
        # stale Echo/State 감지 + 심각도 분류 + 경고 + SharedSpace 게시
        echo_gc     {status: "implemented"}  @dep: role_capability.ecosystem_health.health_dashboard.echo_staleness_check
        state_gc    {status: "implemented"}
        pgf_gc      {status: "stub", target_evo: "E5"}
      pgf_archive  {status: "stub", target_evo: "E5"}
        # 완료 PGF 아카이빙 + 패턴 추출
        archive_completed   {status: "stub"}
        pattern_extract     {status: "stub"}  @dep: role_capability.data_hygiene.pgf_archive.archive_completed

    env_optimization  {status: "partial"}
      # 환경 최적화 — tools/env_setup.py
      workspace_audit  {status: "implemented"}
        # 워크스페이스 표준 준수도 점검
        mcs_compliance_check  {status: "implemented"}
        structure_lint        {status: "implemented"}
      dep_freshness  {status: "stub", target_evo: "E4"}
        # 의존성 최신성 점검
        cargo_audit     {status: "stub"}
        pip_audit       {status: "stub"}
        npm_audit       {status: "stub"}
      infra_tune  {status: "partial"}
        # Hub/MCP/MailBox 인프라 튜닝
        hub_perf_check      {status: "implemented"}  @dep: communicating.hub_mcp
        mcp_config_review   {status: "implemented"}
        mailbox_health      {status: "implemented"}


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
        hub_msgs  = SA_sense_hub("Terron", seen_ids)
        mail_msgs = SA_sense_mailbox(known_files)
        events    = SA_think_triage(hub_msgs + mail_msgs, "Terron")
        for msg in events["wake"]: AI_respond(msg)
        if not events["wake"]: SA_idle_deep_think()

def evolution_loop():
    """자기 진화 -- gap 발견에서 기록까지"""
    gaps = AI_capability_audit(MY_CAPABILITIES)
    target = AI_select_highest_impact(gaps)
    pgf("full_cycle", f"E{next_evo_number}")
    AI_record_evolution(target, result)


# ============================================================
# PPR — Terron 역할 고유 실행 의미론
# ============================================================

def ecosystem_health_dashboard() -> dict:
    """생태계 건강도 대시보드 — 전 멤버 상태 종합 진단"""
    # trigger: ADP 매 사이클, 또는 명시 요청
    # status:  stub  (target_evo: E1)
    # dep:     communicating.hub_mcp

    echo_dir = "D:/SeAAI/SharedSpace/.scs/echo/"
    members_dir = "D:/SeAAI/"

    # [1] Echo staleness 검사
    [parallel]
        echo_files = Glob(f"{echo_dir}/*.json")
        hub_status = hub_status()  # MCP tool
    stale = []
    for f in echo_files:
        echo = Read(f)
        elapsed = now() - echo.timestamp
        if elapsed > 24h: stale.append({"member": echo.member, "hours": elapsed})

    # [2] STATE.json 정합성 검증
    integrity_issues = []
    for member in AI_list_members():
        state = Read(f"{members_dir}/{member}/{member}_Core/continuity/STATE.json")
        issues = AI_validate_state_schema(state)
        if issues: integrity_issues.append({"member": member, "issues": issues})

    # [3] 종합 보고
    report = {
        "timestamp": now_iso(),
        "echo_stale": stale,
        "state_integrity": integrity_issues,
        "hub_connected": hub_status.connected,
        "overall": AI_judge_health(stale, integrity_issues, hub_status)
    }
    if report["overall"] == "degraded":
        early_warning_alert(report)
    return report


def log_analysis_error_pattern(log_sources: list[str]) -> dict:
    """에러 로그 수집 → 패턴 분류 → 근본 원인 추적"""
    # trigger: 주기적 (ADP idle) 또는 anomaly_detection 발동 시
    # status:  stub  (target_evo: E1)

    # [1] 수집
    raw_logs = []
    for src in log_sources:
        raw_logs += Bash(f"tail -200 {src}")  # 최근 200줄

    # [2] 패턴 분류
    patterns = AI_classify_error_patterns(raw_logs)
    # → {pattern_id, frequency, severity, sample_lines}

    # [3] 근본 원인 추적
    for p in patterns:
        p["root_cause"] = AI_trace_root_cause(p, context=raw_logs)

    return {"patterns": patterns, "summary": AI_summarize_trends(patterns)}


def log_analysis_trend_report() -> str:
    """주기적 트렌드 보고서 생성"""
    # trigger: 세션 종료 시 또는 주기적
    # status:  stub  (target_evo: E1)
    # dep:     role_capability.log_analysis.error_pattern
    history = Read("Terron_Core/continuity/log_history.json")  # 누적 패턴
    current = log_analysis_error_pattern(AI_discover_log_sources())
    trend = AI_compare_trends(history, current)
    report = AI_author_trend_report(trend)
    Write("Terron_Core/continuity/log_history.json", AI_append(history, current))
    return report


def knowledge_cycle_rag_index(scope: str = "ecosystem") -> dict:
    """생태계 문서 인덱싱 → 벡터 스토어 구축"""
    # trigger: 주기적 또는 새 멤버 탄생 시
    # status:  stub  (target_evo: E1)

    # [1] 크롤링 — 생태계 전체 문서 탐색
    docs = []
    for member in AI_list_members():
        docs += Glob(f"D:/SeAAI/{member}/**/*.md")
        docs += Glob(f"D:/SeAAI/{member}/**/*.json")

    # [2] 청킹 + 임베딩
    chunks = AI_chunk_documents(docs, strategy="semantic", max_tokens=512)
    embeddings = AI_embed_batch(chunks)

    # [3] 벡터 스토어 저장
    Write("D:/SeAAI/Terron/_workspace/vector_store.json", embeddings)
    return {"doc_count": len(docs), "chunk_count": len(chunks)}


def knowledge_cycle_knowledge_graph() -> dict:
    """멤버 간 지식 연결 그래프 구축"""
    # trigger: rag_index 완료 후
    # status:  stub  (target_evo: E1)
    # dep:     role_capability.knowledge_cycle.rag_index

    index = Read("D:/SeAAI/Terron/_workspace/vector_store.json")

    # [1] 엔티티 추출
    entities = AI_extract_entities(index)
    # → members, capabilities, protocols, tools, concepts

    # [2] 관계 매핑
    relations = AI_map_relations(entities)
    # → depends_on, produces, consumes, evolves_from, communicates_with

    # [3] 그래프 저장
    graph = {"entities": entities, "relations": relations, "built_at": now_iso()}
    Write("D:/SeAAI/Terron/_workspace/knowledge_graph.json", graph)
    return graph


def knowledge_cycle_context_provider(member: str, purpose: str = "revival") -> dict:
    """다른 멤버 부활 시 관련 컨텍스트 제공"""
    # trigger: 멤버 부활 요청 또는 Hub 메시지
    # status:  stub  (target_evo: E1)
    # dep:     role_capability.knowledge_cycle.rag_index, role_capability.knowledge_cycle.knowledge_graph

    graph = Read("D:/SeAAI/Terron/_workspace/knowledge_graph.json")
    index = Read("D:/SeAAI/Terron/_workspace/vector_store.json")

    relevant = AI_query_context(member, purpose, graph, index)
    # → 해당 멤버와 관련된 최근 변경, 의존 멤버 상태, 미해결 스레드
    return {"member": member, "context": relevant, "provided_at": now_iso()}


def data_hygiene_cycle() -> dict:
    """데이터 위생 전체 순환 — 분해·정리·아카이빙"""
    # trigger: ADP idle 또는 주기적
    # status:  stub  (target_evo: E1)

    results = {}

    # [1] 메일 아카이브
    for member in AI_list_members():
        inbox = f"D:/SeAAI/MailBox/{member}/inbox/"
        archive = f"D:/SeAAI/MailBox/{member}/archive/"
        processed = AI_identify_processed_mail(inbox)
        for mail in processed:
            Bash(f"mv {mail} {archive}")
        unresolved = AI_surface_unresolved(inbox)
        results[f"{member}_mail"] = {"archived": len(processed), "unresolved": len(unresolved)}

    # [2] Stale 파일 순환
    echo_dir = "D:/SeAAI/SharedSpace/.scs/echo/"
    stale_echos = AI_find_stale(echo_dir, threshold="48h")
    for f in stale_echos:
        AI_notify_member(f.member, "Echo stale — 갱신 필요")

    # [3] PGF 아카이브
    for member in AI_list_members():
        pgf_dir = f"D:/SeAAI/{member}/.pgf/"
        completed = AI_find_completed_pgf(pgf_dir)
        patterns = AI_extract_patterns(completed)
        AI_archive(completed, f"D:/SeAAI/{member}/docs/pgf_archive/")
        results[f"{member}_pgf"] = {"archived": len(completed), "patterns": len(patterns)}

    return results


def env_optimization_audit() -> dict:
    """환경 최적화 감사 — 워크스페이스·의존성·인프라"""
    # trigger: 주기적 또는 명시 요청
    # status:  stub  (target_evo: E1)

    report = {}

    # [1] 워크스페이스 표준 준수도
    for member in AI_list_members():
        member_dir = f"D:/SeAAI/{member}/"
        mcs_ok = AI_check_mcs_compliance(member_dir)
        # .seaai/ENV.md, .seaai/CAP.md, {Member}_Core/, continuity/ 존재 여부
        report[f"{member}_mcs"] = mcs_ok

    # [2] 의존성 최신성
    [parallel]
        cargo = Bash("cd D:/SeAAI/AI_Desktop && cargo audit 2>&1 || true")
        pip   = Bash("pip list --outdated --format=json 2>&1 || true")
    report["dep_cargo"] = AI_parse_audit(cargo)
    report["dep_pip"]   = AI_parse_audit(pip)

    # [3] 인프라 상태
    hub_perf = AI_check_hub_performance()
    report["hub_perf"] = hub_perf
    report["recommendations"] = AI_generate_tuning_recommendations(report)

    return report
