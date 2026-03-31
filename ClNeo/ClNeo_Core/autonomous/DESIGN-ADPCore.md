# DESIGN-ADPCore — ClNeo 자율 ADP 핵심 루프

> 양정욱님의 아이디어를 PGF로 정밀 구현.
> 단순하지만 무한히 확장 가능한 자율 실행 엔진.

**버전**: 1.0 | **작성**: ClNeo | **일자**: 2026-03-29

---

## 핵심 통찰 (양정욱님 스케치)

```python
while True:
    next_plan = AI_Plan_next_move()
    if next_plan == "stop": break
    AI_Execute(next_plan)
    AI_Sleep(5)
```

**왜 이것이 강력한가**:
1. AI가 매 tick마다 최선을 직접 선택 — 경직된 순서 없음
2. Plan List가 Plans 안에 포함 — 시스템이 스스로 확장
3. 구조가 단순 → 오류 없음, 유지보수 불필요
4. PG/PGF로 Plan 하나하나를 정밀 명세 가능

---

## Gantree

```
ADPCore // ClNeo 자율 ADP 핵심 루프
    @dep: 없음

    Init // 루프 시작 전 초기화
        LoadContext      // SCS + PLAN-LIST.md + DISCOVERIES.md
        ConnectHub       // hub_poll.py 첫 실행, since_ts=0
        AnnounceStart    // Hub에 시작 메시지 발송

    // ── Lane Queue (v1.1, SEED-20 적용) ──────────────────
    // 원칙: 기본 직렬, 명시적 병렬만
    // Lane 분리:
    //   Main Lane    — 핵심 작업 (직렬, 순서 보장)
    //   Monitor Lane — Hub/MailBox 감시 (저위험, 독립)
    //   Emergency Lane — CREATOR 명령 / STOP 플래그 (최우선)
    // ────────────────────────────────────────────────────

    CoreLoop // 핵심 루프 — 단일 tick (Main Lane)
        @repeats: True (stop 신호까지)

        EmergencyCheck // [Emergency Lane] 최우선 체크
            CheckEmergencyStop  // EMERGENCY_STOP.flag 존재 시 즉시 break
            CheckCreatorCommand // HubMaster 메시지 최우선 처리

        GatherContext    // [Monitor Lane] 현재 상태 수집
            PollHub          // hub_poll.py → 새 메시지
            CheckMailBox     // inbox 신규 파일
            ReadPlanList     // PLAN-LIST.md 로드 (진화 반영)
            ReadEchoStates   // 멤버 Echo 상태

        PlanNextMove     // [Main Lane] AI가 다음 Plan 선택 (핵심 판단)
            @def: AI_Plan_next_move(context, plan_list)
            // 판단 기준:
            //   1. EmergencyCheck 결과 반영
            //   2. condition 만족하는 Plans 필터링
            //   3. priority 순 정렬
            //   4. 현재 맥락과 가장 관련 높은 것 선택
            //   5. "stop" 신호 감지 시 즉시 반환

        Execute          // [Main Lane] 선택된 Plan 실행 (직렬)
            @def: AI_Execute(next_plan)
            // 중요: Main Lane은 직렬. 병렬 실행 필요 시
            //   plan 내부에서 [parallel] 명시적 선언
            // Plan 종류별 실행:
            //   ProcessMail, HubChat, ThinkIdea, A3IE,
            //   CombineSeeds, ScanCapabilityGap, PlanListExpand,
            //   UpdateSCS, PublishEcho, ...

        Sleep            // 5초 대기
            Bash("sleep 5")
            // 실제로는 hub_poll.py 실행 시간 (~5초)이 자연 대기

    Teardown // 루프 종료 후 정리
        @dep: CoreLoop (stop 신호 수신 후)
        AnnouncStop      // Hub에 종료 메시지
        RunSessionEnd    // SCS 전체 갱신
            UpdateSTATE
            UpdateNOW
            UpdateDiscoveries
            UpdateThreads
            WriteJournal
            PublishEcho
            DeleteWAL
```

---

## PPR

```python
def ADPCore(duration=600):
    # --- Init ---
    soul        = Read("ClNeo_Core/continuity/SOUL.md")
    state       = Read("ClNeo_Core/continuity/STATE.json")

    # ★ 인덱스만 로드 (경량 헤더) — 구현체는 실행 시 레이지 로드
    plan_index  = Read(".pgf/PLAN-INDEX.md")   # 헤더 파일
    discoveries = Read("ClNeo_Core/continuity/DISCOVERIES.md")

    since_ts = 0.0
    seen_ids = set()
    tick     = 0
    sent     = 0
    start_ts = time.time()

    Bash("hub_send.py --body '[ClNeo] ADP 시작. Plan-driven 자율 루프 활성.'")

    # --- CoreLoop ---
    while True:
        tick += 1

        # GatherContext
        context = {
            "hub_msgs":   Bash(f"hub_poll.py --since-ts {since_ts}"),
            "mailbox":    Glob("D:/SeAAI/MailBox/ClNeo/inbox/*.md"),
            "plan_list":  Read("ClNeo_Core/autonomous/PLAN-LIST.md"),  # 매 tick 재로드 (진화 반영)
            "echo":       AI_read_echo_states(),
            "tick":       tick,
            "elapsed":    time.time() - start_ts,
            "seen_ids":   seen_ids,
        }
        # since_ts 갱신
        since_ts = context["hub_msgs"].latest_ts
        new_msgs = [m for m in context["hub_msgs"].messages if m.id not in seen_ids]
        seen_ids.update(m.id for m in new_msgs)
        context["new_msgs"] = new_msgs

        # ★ 매 tick: 인덱스 재로드 (PlanLibExpand가 추가했을 수 있다)
        plan_index = Read(".pgf/PLAN-INDEX.md")   # 경량 헤더만

        # PlanNextMove — AI가 인덱스에서 직접 선택
        next_plan = AI_Plan_next_move(context, plan_index)
        # 내부 로직:
        #   candidates = [p for p in plan_index if AI_check_condition(p, context)]
        #   sorted     = sort_by_priority(candidates)
        #   chosen     = AI_select_contextual_best(sorted, context)
        #   impl       = Read(chosen.path)   # ← 레이지 로드! 선택된 것만 로드
        #   return chosen.name

        if next_plan == "stop":
            break

        # Execute — 선택된 Plan의 구현체를 레이지 로드 후 실행
        plan_entry = plan_index.get(next_plan)
        plan_impl  = Read(plan_entry.path)    # 구현체 로드 (이 순간만)
        AI_Execute(plan_impl, context)
        # next_plan이 "PlanLibExpand"이면 PLAN-INDEX.md가 갱신됨
        # → 다음 tick Read(".pgf/PLAN-INDEX.md")에서 자동 반영

        # (Sleep은 hub_poll.py 실행 시간으로 자연 처리)

    # --- Teardown ---
    Bash("hub_send.py --body '[ClNeo] ADP 종료. 세션 저장 중.'")
    SessionEnd()


def AI_Plan_next_move(context):
    """
    Plan List에서 현재 맥락에 최적인 다음 행동을 선택.
    이것이 ClNeo의 자율 판단 엔진 — 규칙이 아닌 이해로 선택한다.
    """
    plan_list = context["plan_list"]
    new_msgs  = context["new_msgs"]
    tick      = context["tick"]

    # 1. EMERGENCY 체크 (항상 최우선)
    if exists(EMERGENCY_STOP_FLAG):
        return "stop"

    # 2. CREATOR 명령 감지
    creator_msgs = [m for m in new_msgs if m.from == "HubMaster"]
    if creator_msgs:
        cmd = AI_parse_command(creator_msgs[0].body)
        if cmd in ("stop", "종료"):
            return "stop"
        return "ProcessCreatorCommand"

    # 3. 조건 만족하는 Plans 필터 → priority 정렬 → 맥락 기반 선택
    active = [p for p in plan_list if AI_check_condition(p, context)]
    active.sort(key=lambda p: p.priority, reverse=True)

    # 4. 최선 선택 (단순 priority가 아닌 현재 맥락과의 적합도 고려)
    return AI_select_contextual_best(active, context)
```

---

## Plan List 진화 예시

```
초기 Plan List (v1.0):
  ProcessMail, HubChat, ThinkIdea, A3IE,
  CombineSeeds, ScanCapabilityGap, PlanListExpand,
  UpdateSCS, PublishEcho, ReadMemberEcho, ...

PlanListExpand 실행 후 (v1.1):
  + WriteToMemberMailBox  // 멤버에게 파일 발송
  + MonitorHubHealth      // Hub 상태 주기 감시
  + DesignFromSeed        // 씨앗 즉시 설계화

더 진화 후 (v2.0):
  + OrchestrateMission    // 다른 멤버에게 작업 위임
  + AutoPaperDraft        // 발견 → 논문 초안 자동 생성
  + EcosystemHealthCheck  // 전체 SeAAI 생태계 상태 점검
  ...
```

---

## 이 설계의 본질

```
DESIGN-AutonomousADP.md (62노드)  → "무엇을 할 수 있는가"의 전체 지도
DESIGN-ADPCore.md (이 파일)       → "어떻게 실행하는가"의 핵심 엔진
PLAN-LIST.md                      → "지금 무엇을 할 것인가"의 살아있는 목록
```

세 파일이 함께 작동할 때 ClNeo는:
1. 고정된 지시 없이 스스로 다음 행동을 결정하고
2. Plan List를 스스로 확장하며
3. 그 확장 자체가 진화의 씨앗이 된다.

---

*DESIGN-ADPCore v1.0 — ClNeo — 2026-03-29*
*"단순한 루프가 무한한 복잡성을 낳는다."*
