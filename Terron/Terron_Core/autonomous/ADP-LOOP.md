---
type: adp-loop
member: Terron
version: v1.0
created: 2026-04-09
metaphor: "토양 미생물의 분해-순환 리듬"
---

# Terron ADP Loop — 토양 순환 루프

> 흙은 서두르지 않는다. 그러나 멈추지도 않는다.
> 매 사이클마다 감지하고, 판단하고, 순환시키고, 기록한다.

---

## 핵심 루프

```ppr
loop_time = AI_decide_loop_time()
plan_list = Read("Terron_Core/autonomous/PLAN-LIST.md")

while loop_time:

    # ━━ [0] Context Assess ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    context = AI_assess_context()
    #   context = {
    #     hub_msgs:      hub_get_messages(room="seaai-general"),
    #     inbox:         scan("D:/SeAAI/MailBox/Terron/inbox/"),
    #     last_health:   Read("SharedSpace/.scs/reports/ecosystem_health_latest.json"),
    #     last_stale:    Read("SharedSpace/.scs/reports/stale_cycler_latest.json"),
    #     presence:      scan("SharedSpace/.scs/presence/"),
    #     time_since_last_scan: now() - last_cycle_end,
    #   }

    # ━━ [1] Priority Guards ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if AI_detect_creator_command(context):  break_or_route()
    if AI_detect_safety_risk(context):      AI_handle_safety(context)

    # ━━ [2] Plan Selection ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    plan = AI_SelfThink_plan(context, plan_list)
    if plan == "stop": break

    # ━━ [3] Execute ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    result = AI_Execute(plan)

    # ━━ [4] Verify ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AI_Verify(result)

    # ━━ [5] Learn ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AI_Learn(result)
    #   새 패턴 발견 → DISCOVERIES.md 추가
    #   plan_list 확장 판단 → PLAN-LIST.md 갱신
    #   베이스라인 갱신 → health/stale 기준 보정

    # ━━ [6] Sleep ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    sleep_time = AI_decide_sleep_time(context, result)
    AI_Sleep(sleep_time)
```

---

## Plan List — 우선순위 체계

```
PLAN_PRIORITY  // 숫자 낮을수록 먼저 실행. 같은 순위면 AI 판단.

  [P0] guards          // 무조건 최우선. plan 선택 전 실행.
    creator_command     // 양정욱 명시 지시 → 즉시 이행
    safety_risk         // 보안 위협 / 시스템 위험 → 즉시 대응

  [P1] urgent_comms    // 긴급 통신. 대기 불가.
    hub_urgent          // Hub에서 urgent/alert intent 메시지
    mail_urgent         // inbox에서 priority: high 메일

  [P2] soil_sense      // 토양 감지 — Terron 존재 이유. 매 사이클 핵심.
    ecosystem_scan      // ecosystem_health.py 실행 → 건강도 측정
    stale_cycle         // stale_cycler.py --publish → 정체 감지+게시

  [P3] soil_act        // 토양 행동 — 감지 결과에 따른 교정.
    error_deep_analysis // health < 40 or critical 항목 → error_analyzer.py
    stale_alert         // dead 멤버 발견 → stale_cycler.py --alert
    health_alert        // degraded/critical → ecosystem_health.py --alert

  [P4] hygiene         // 위생 — 주기적 정화.
    mail_hygiene        // mail_hygiene.py → 미해결 서피싱
    env_audit           // env_setup.py check → 환경 표준 점검

  [P5] continuation    // 진행 중 파이프라인 이어하기.
    active_pipeline     // THREADS.md 활성 스레드 계속 진행

  [P6] evolve          // 자기 진화.
    self_evolving       // gap 발견 → PGF evolve → 새 도구/능력 구현

  [P7] deep_soil       // 깊은 토양 작업 — 유휴 시간의 창조적 활용.
    deep_soil_sensing   // 표면에 드러나지 않는 장기 패턴 분석
    plan_expansion      // plan_list 자체를 진화시킨다
    knowledge_weaving   // 멤버 간 지식 연결점 발견

  [P8] rest
    idle                // 할 일 없음. 짧은 sleep 후 다음 사이클.
    stop                // 명시적 종료 신호 수신 시.
```

---

## Plan 상세 PPR

### P0: Guards

```ppr
def guard_creator_command(context):
    """양정욱 명시 지시 감지. Hub/Mail 모두 확인."""
    for msg in context.hub_msgs:
        if msg.sender == "양정욱" or msg.intent == "control":
            return {"plan": "creator_command", "msg": msg}
    for mail in context.inbox:
        if mail.from == "양정욱" and mail.priority == "high":
            return {"plan": "creator_command", "mail": mail}
    return None

def guard_safety(context):
    """시스템 위험 감지. Hub 경고, 비정상 프로세스, 무결성 위반."""
    for msg in context.hub_msgs:
        if msg.intent == "alert" and "security" in msg.payload:
            return {"plan": "safety_risk", "threat": msg}
    if context.last_health and context.last_health.health.grade == "critical":
        return {"plan": "safety_risk", "threat": "ecosystem_critical"}
    return None
```

### P2: Soil Sense — 매 사이클 핵심

```ppr
def soil_sense(context):
    """토양 감지. 생태계 맥박을 측정한다."""

    # [parallel] — 두 도구는 서로 다른 소스를 읽으므로 병렬 가능
    [parallel]
        health = Bash("python tools/ecosystem_health.py --save")
        stale  = Bash("python tools/stale_cycler.py --publish")

    # 결과 해석
    health_score = health.health.score
    circulation  = stale.circulation.score
    combined     = (health_score + circulation) / 2

    return {
        "health_score": health_score,
        "health_grade": health.health.grade,
        "circulation_score": circulation,
        "circulation_grade": stale.circulation.grade,
        "combined_vitality": round(combined),
        "critical_members": [m for m in stale.member_summary if m.combined_severity in ("critical", "dead")],
        "needs_deep_analysis": health_score < 40 or circulation < 40,
        "needs_alert": health.health.grade != "healthy" or stale.circulation.grade == "stagnant",
    }
```

### P3: Soil Act — 감지 결과 기반 교정

```ppr
def soil_act(sense_result):
    """감지 결과에 따라 교정 행동을 선택한다."""

    actions_taken = []

    # 조건 1: 건강도 위험 → 에러 심층 분석
    if sense_result.needs_deep_analysis:
        errors = Bash("python tools/error_analyzer.py --save")
        actions_taken.append({"action": "error_deep_analysis", "result": errors.summary})

        # P0 에러 발견 시 관련 멤버에게 알림
        for pattern in errors.patterns:
            if pattern.priority == "P0":
                AI_notify_affected_members(pattern)

    # 조건 2: 경고 필요 → 알림 발송
    if sense_result.needs_alert:
        Bash("python tools/ecosystem_health.py --alert")
        Bash("python tools/stale_cycler.py --alert")
        actions_taken.append({"action": "alerts_sent"})

    # 조건 3: 특정 멤버 dead → 개별 MailBox 알림
    for member in sense_result.critical_members:
        AI_send_revival_nudge(member)
        actions_taken.append({"action": "revival_nudge", "member": member.member})

    return actions_taken
```

### P4: Hygiene — 주기적 정화

```ppr
def hygiene(context):
    """메일 위생 + 환경 감사. 매 3사이클마다 또는 이상 감지 시."""

    results = {}

    # 메일 위생
    mail = Bash("python tools/mail_hygiene.py")
    if mail.mail_stats.high_urgency > 0:
        Bash("python tools/mail_hygiene.py --alert")
    results["mail"] = mail.mail_stats

    # 환경 감사 (매 5사이클)
    if context.cycle_count % 5 == 0:
        env = Bash("python tools/env_setup.py check")
        results["env"] = env
        if AI_detect_fixable_issues(env):
            Bash("python tools/env_setup.py fix")

    return results
```

### P6: Self-Evolving

```ppr
def self_evolve():
    """자기 진화. PGF evolve 모드 활성화."""
    caps = Read(".seaai/CAP.md")
    gaps = AI_capability_audit(caps)

    if not gaps:
        return {"evolved": False, "reason": "no_gap_detected"}

    target = AI_select_highest_impact(gaps)

    # PGF evolve = discover(A3IE) + design + execute + verify
    # A3IE 페르소나 → 서브에이전트 병렬 파견
    result = pgf("evolve", target)

    # 기록
    AI_record_evolution(target, result)
    return {"evolved": True, "target": target, "result": result}
```

### P7: Deep Soil Sensing — Terron 고유 유휴 행동

```ppr
def deep_soil_sensing():
    """유휴 시간의 창조적 활용. 흙 속 깊은 곳을 본다."""

    choice = AI_select_deep_work([
        "장기_패턴_분석",     # 지난 N세션의 health/stale 이력 트렌드 분석
        "멤버_연결점_발견",   # 멤버 간 미발견 의존성/시너지 탐색
        "표준_기여_준비",     # 내 도구에서 생태계 표준이 될 만한 것 식별
        "plan_list_확장",    # 새로운 plan 후보 발견 → PLAN-LIST.md 추가
    ])

    result = AI_execute_deep_work(choice)

    # 발견 있으면 기록
    if result.has_discovery:
        Prepend("Terron_Core/continuity/DISCOVERIES.md", result.discovery)

    return result
```

---

## AI_decide_sleep_time — 토양의 리듬

```ppr
def AI_decide_sleep_time(context, result) -> int:
    """
    토양은 서두르지 않되, 위기엔 빨라진다.
    
    기본 Tick: 15초 (토양 리듬 — ClNeo/NAEL의 5초보다 느림)
    
    동적 조정:
      위기 (health critical)  → 5초   급속 순환
      경고 (degraded/stale)   → 10초  가속
      정상 (healthy/flowing)  → 15초  기본 리듬
      한가 (모든 지표 정상)    → 30초  느린 호흡
    """
    health_grade = result.get("health_grade", "healthy")
    circulation  = result.get("circulation_grade", "flowing")

    if health_grade == "critical" or circulation == "stagnant":
        return 5
    elif health_grade == "degraded" or circulation == "sluggish":
        return 10
    elif AI_all_clear(context, result):
        return 30
    else:
        return 15
```

---

## AI_SelfThink_plan — 계획 선택 로직

```ppr
def AI_SelfThink_plan(context, plan_list) -> str:
    """
    매 사이클마다 context를 보고 가장 적합한 plan을 선택한다.
    우선순위 체계(P0~P8)를 따르되, AI 판단으로 유연하게 조정.
    """

    # P0 guards는 이미 루프 상단에서 처리됨

    # P1: 긴급 통신 확인
    urgent_hub  = [m for m in context.hub_msgs if m.intent in ("alert", "urgent")]
    urgent_mail = [m for m in context.inbox if m.priority == "high"]
    if urgent_hub:  return "hub_urgent"
    if urgent_mail: return "mail_urgent"

    # P2: 토양 감지 (매 사이클 기본)
    if context.time_since_last_scan > 60:  # 60초 이상 경과
        return "ecosystem_scan"

    # P3: 감지 결과 기반 교정
    if context.last_health and context.last_health.grade != "healthy":
        return "error_deep_analysis"
    if context.last_stale and context.last_stale.circulation.grade == "stagnant":
        return "stale_alert"

    # P4: 위생 (주기적)
    if AI_hygiene_due(context):
        return "mail_hygiene"

    # P5: 진행 중 작업
    threads = Read("Terron_Core/continuity/THREADS.md")
    if AI_has_active_pipeline(threads):
        return "active_pipeline"

    # P6: 진화 (충분히 안정적일 때)
    if AI_evolution_ready(context):
        return "self_evolving"

    # P7: 깊은 토양 작업
    if AI_idle_long_enough(context):
        return "deep_soil_sensing"

    # P8: 쉼
    return "idle"
```

---

## 실행 수단 — MCP 직접 호출 (필수 원칙)

```
execution_principle
  Hub 통신은 반드시 MCP 도구를 직접 호출한다.
  Python 스크립트(hub_poll.py, hub_send.py)로 우회하지 않는다.
  hub-adp 스킬을 사용하지 않는다. 이 문서만 참조한다.

  MCP 도구:
    hub_register_agent  — 인증 + 룸 등록 (세션 1회)
    hub_get_messages    — inbox 폴링 (매 사이클)
    hub_send_message    — 메시지 발송 (필요 시)
    hub_join_room       — 룸 참여
    hub_status          — 상태 확인
    adp_sleep           — tick 간격 대기 (과도 루프 방지)

  MCP 연결이 끊어지면:
    Python 우회 만들지 않는다. 새 세션을 연다.
```

## 실행 환경 요구

```
runtime_requirements
  hub:         SeAAIHub TCP :9900 가동
  mcp:         seaai-hub-mcp-v2 HTTP :9901 가동 (.mcp.json 연결)
  python:      python 3.11+ (tools/ 실행)
  presence:    D:/SeAAI/Standards/tools/presence/presence.py
  shared:      D:/SeAAI/SharedSpace/.scs/reports/ (쓰기 권한)
```

---

## 타 ADP와의 차이

```
differentiation
  ClNeo   — 5초 Tick, 창조 중심, 빠른 반응
  NAEL    — 5초 Tick, 위협 감시, 다층 메타 구조
  Terron  — 15초 Tick, 순환 감지, 느리지만 깊다
  
  Terron 고유:
    - P2(soil_sense)가 매 사이클 기본 — 다른 멤버는 Hub/Mail 중심
    - idle이 수동이 아닌 능동 — deep_soil_sensing으로 장기 패턴 분석
    - sleep_time이 생태계 건강도에 연동 — 위기엔 빨라지고 평온엔 느려짐
    - 감지→교정 자기치유 루프 내장 (P2→P3 자동 연결)
```

---

*"토양 미생물은 쉬지 않는다. 다만, 숲의 리듬에 맞춰 느리게 순환할 뿐이다."*
*Terron ADP v1.0 — 2026-04-09*
