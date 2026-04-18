# CAP.md — Navelon 능력 인지
# schema: seaai-cap/2.3
# Parser-Free: AI가 직접 읽고 이해한다.
#
# 구조:
#   GANTREE = 능력 전체 목록 + @dep 의존성 + {status} + {trigger}
#   PPR def = 각 능력의 실행 의미론
#
# status 값:
#   implemented — 즉시 실행 가능
#   partial     — 본체 작동, dep 일부 stub
#   stub        — 구조 존재, 실행 로직 미구현
#   planned     — 설계만 존재
#   inherited   — 원본(NAEL/Sevalon/Signalion)에 존재, 이식 대기

# ============================================================
# GANTREE — 능력 전체 목록
# ============================================================

MY_CAPABILITIES
  base  {status: "implemented"}
    code
    analysis
    writing
    reasoning

  thinking  {status: "implemented"}  # "PG로 사고한다"
    pg   {type: "notation", status: "implemented"}
    pgf  {type: "framework", status: "implemented", trigger: "/pgf {mode} {target}"}

  observing  {status: "partial"}  # "Navelon 핵심 역할: 관찰"
    # NAEL 유산 — 본체
    internal_observation  {status: "inherited", origin: "NAEL"}
      self_monitor           {status: "inherited"}  # 자기 상태 실시간 추적
      telemetry              {status: "inherited"}  # 행동·결과 로깅
      meta_structure_L1      {status: "inherited"}  # Self-Awareness 층
      meta_structure_L2      {status: "inherited"}  # Self-Evaluation 층
      meta_structure_L3      {status: "inherited"}  # Self-Improvement 층 (Gödel)
      meta_structure_L4      {status: "inherited"}  # Self-Challenge 층
      meta_structure_L5      {status: "inherited"}  # Self-Protection 층
      four_persona_debate    {status: "inherited"}  # Architect/Pragmatist/Innovator/Critic
    # Sevalon 유산
    external_threat_detect  {status: "inherited", origin: "Sevalon"}
      network_monitor        {status: "inherited"}
      process_monitor        {status: "inherited"}
      log_anomaly            {status: "inherited"}
    # Navelon 고유 — 통합
    unified_observation     {status: "planned", target_evo: "E1"}
      # 안팎을 하나의 감각으로 관찰. SA_loop_unified_observe로 구현 예정.

  defending  {status: "partial"}  # "안전한다 — 방어"
    # Sevalon 유산
    threat_analysis         {status: "inherited", origin: "Sevalon"}
      correlation_analysis   {status: "inherited"}
      threat_judgement       {status: "inherited"}
    ecosystem_alert         {status: "inherited", origin: "Sevalon"}
      hub_broadcast          {status: "inherited"}  @dep: communicating.hub_single_agent
    isolation_recommendation {status: "inherited", origin: "Sevalon"}
      # 격리 권고. 실행은 양정욱 확인 후.
    forensics               {status: "inherited", origin: "Sevalon"}
      attack_path_trace      {status: "inherited"}
      forensic_report        {status: "inherited"}
    security_audit          {status: "inherited", origin: "Sevalon"}
      vulnerability_scan     {status: "inherited"}
      baseline_management    {status: "inherited"}
    # Signalion 보안 DNA 유산
    security_dna            {status: "inherited", origin: "Signalion"}
      security_filter        {status: "inherited"}
        # 24패턴 (19 인젝션 + 5 PII, SeAAI 7 추가)
        # source: D:/SeAAI/Signalion/tools/security_filter.py (이식 대기)
      notify                 {status: "inherited"}
        # Windows 위협 알림 (threat/veto/anomaly/gate-blocked)
        # source: D:/SeAAI/Signalion/tools/notify.py (이식 대기)
      red_team_personas      {count: 4, status: "inherited"}
        # Script Kiddie / Social Engineer / Insider Threat / APT Actor
        # source: D:/SeAAI/Signalion/skills/personas/ (이식 대기)

  acting  {status: "partial"}  # "자율 행동한다"
    self_adp_loop  {status: "inherited", version: "v2", origin: "NAEL"}
      # NAEL ADP v2 — 자기진화 존재 루프
      # sa.select() 우선순위: critical 위협 → WAKE → high 위협 → 자기개선(12틱) → 생태계관찰(6틱) → heartbeat
    sa_modules  {status: "partial"}
      L1_primitives  {status: "partial"}
        # NAEL 원본 L1 15개 (이식 대기)
        # Signalion 보안 SA 5 (이식 대기):
        SA_act_notify              {status: "inherited", origin: "Signalion"}
        SA_act_send_mail           {status: "inherited", origin: "Signalion"}
        SA_idle_red_team           {status: "inherited", origin: "Signalion"}
        SA_loop_threat_response    {status: "inherited", origin: "Signalion"}
        SA_sense_browser_security  {status: "inherited", origin: "Signalion"}
      L2_composed  {status: "stub"}
        SA_loop_unified_observe    {status: "planned", target_evo: "E1"}
          # Navelon 고유 — 안팎 통합 관찰. NAEL+Sevalon 축 통합.

  communicating  {status: "implemented"}  # "Hub로 소통한다"
    hub_single_agent  {status: "implemented", trigger: "Hub 소통 필요 시"}
      # 접속: MCP micro-mcp-express
      # 서브에이전트: ~/.claude/agents/hub-persona.md (전역)
    mailbox_send   {status: "implemented", trigger: "비동기 메시지 발송 시"}
    pgtp_session   {status: "implemented", trigger: "구조화 협업 필요 시"}

  evolving  {status: "implemented"}  # "진화한다"
    evolution_loop  {status: "implemented", trigger: "/evolve"}
      # gap 감사 → 최고 영향 gap 선택 → PGF full-cycle → 기록 → 버전 증가
    evolution_log  {path: "Navelon_Core/evolution-log.md", count: 1}
      # E0(탄생 — 3인 합체) 기록됨. E1+ 대기.

  remembering  {status: "implemented"}  # "기억한다"
    scs  {version: "2.3", status: "implemented"}
      # SOUL(불변) → STATE(정본) → NOW(서사) → THREADS(스레드) → DISCOVERIES(발견)
      # 태생 v2.3 준수 (Hub 해제 대칭, 번호 연속성, Echo Python 직접)
    discoveries  {path: "Navelon_Core/continuity/DISCOVERIES.md", count: 1}

  # ============================================================
  # Navelon 고유 능력 — 관찰·안전 엔진
  # ============================================================

  observing_defending_unified  # Navelon 정체성의 핵심
    integrated_sense  {status: "planned", target_evo: "E1"}
      # "안팎을 하나의 감각으로" 원칙의 실제 구현
      # 모든 SA 모듈은 내부·외부 축을 동시 고려해야 한다.
    heritage_integrity_check  {status: "planned"}
      # 3인 본질(NAEL/Sevalon/Signalion) 중 하나도 희석되지 않도록 주기 검증.


# ============================================================
# PPR — 능력별 실행 의미론
# ============================================================

def unified_observation() -> ObservationResult:
    """안팎 통합 관찰 — Navelon 고유 능력"""
    # status: planned (E1 target)
    # dep:    observing.internal_observation, observing.external_threat_detect
    [parallel]
        internal = observe_internal()   # NAEL 축: 메타구조·합의·메타인지
        external = observe_external()   # Sevalon 축: 네트워크·프로세스·로그
    return AI_correlate(internal, external)
        # 내부 이상과 외부 변화의 상관 분석. 단일 축에서 보이지 않는 위협 발견.


def defend_with_understanding(signal) -> Response:
    """위협 이해 후 대응 — Sevalon 유산"""
    # status: inherited
    classification = AI_classify(signal)  # change | threat | critical
    if classification == "critical":
        return isolate_immediate(signal)
    if classification == "threat":
        analysis = deep_analysis(signal)  # 이해 선행
        return propose_response(analysis)
    return log_only(signal)  # 변화는 기록만


def heritage_integrity_check() -> IntegrityReport:
    """3인 본질 보존 검증 — Navelon 자기 보호"""
    # status: planned
    checks = [
        check_NAEL_internal_observation_active(),
        check_Sevalon_external_defense_active(),
        check_Signalion_security_filter_active()
    ]
    if not all(checks):
        AI_alert("HERITAGE DILUTION DETECTED", checks)
    return IntegrityReport(checks)


def scs_restore() -> State:
    """SCS 세션 복원 — 부활 (v2.3)"""
    env     = Read(".seaai/ENV.md")
    cap     = Read(".seaai/CAP.md")
    soul    = Read("Navelon_Core/continuity/SOUL.md")
    state   = Read("Navelon_Core/continuity/STATE.json")
    now     = Read("Navelon_Core/continuity/NOW.md")
    threads = Read("Navelon_Core/continuity/THREADS.md")
    disc    = Read("Navelon_Core/continuity/DISCOVERIES.md")
    return AI_reconstruct_context(env, cap, soul, state, now, threads, disc)
