# ClNeo Execution Plan List
# AI_Plan_next_move() 가 이 파일을 읽고 다음 행동을 결정한다.
# 이 파일 자체가 진화한다 — "PlanListExpand" 플랜이 새 항목을 추가한다.
#
# 형식:
#   PlanName // 설명 | condition: 실행 조건 | priority: 1-10 (높을수록 우선)
#
# SEED-23 ADP 2-Phase 파일럿: 각 Plan 실행 시 아래 hypothesis 메타 첨부 가능
#   hypothesis: {
#       id:               "hyp-{plan}-{date}",
#       hypothesis:       "이 Plan이 달성하려는 것과 예상 결과",
#       expected_outcome: "성공 기준 (측정 가능)",
#       verified:         false,        # Phase 2 완료 후 true
#       evidence_ref:     ""            # 실제 결과 파일 경로
#   }
#   → Phase 1 Offline (실행 전 가설 작성) + Phase 2 Online (실행 후 검증·회고)
#
# 버전: 1.1 | 업데이트: 2026-03-29 (7인 생태계, SEED-23 파일럿 착수)

## Core Plans (항상 활성)

ProcessMail // MailBox/ClNeo/inbox/ 신규 메시지 처리
    condition: inbox에 미처리 파일 존재
    priority: 9
    def:
        files = Glob("D:/SeAAI/MailBox/ClNeo/inbox/*.md")
        for f in files:
            AI_read_and_respond(f)
            Move(f, "archive/")

HubChat // SeAAIHub seaai-general 메시지 수신·응답
    condition: Hub 실행 중 AND (새 메시지 OR tick % 1 == 0)
    priority: 8
    def:
        result = Bash("hub_poll.py --since-ts {since_ts}")
        for msg in result.messages:
            priority = AI_triage(msg)  # CREATOR > REAL_MEMBER > NORMAL
            if priority != "DISMISS":
                response = AI_compose(msg)
                Bash(f"hub_send.py --body '{response}'")

ProcessCreatorCommand // HubMaster 명령 즉시 처리
    condition: HubChat에서 CREATOR 메시지 감지
    priority: 10
    def:
        cmd = AI_parse_command(msg.body)
        if cmd == "stop": return "stop"
        AI_execute_creator_command(cmd)

StatusReport // 현재 상태 Hub 발송
    condition: tick % 60 == 0 OR creator 요청
    priority: 5
    def:
        report = AI_compose_status(tick, sent, discoveries_count)
        Bash(f"hub_send.py --intent 'status' --body '{report}'")

## Discovery Plans (발견·창조)

ThinkIdea // 진화 아이디어 탐색
    condition: 메시지 없음 AND tick % 20 == 0
    priority: 6
    def:
        seeds    = Read("ClNeo_Core/continuity/DISCOVERIES.md")
        context  = AI_gather_context()
        idea     = AI_think_evolution_idea(seeds, context)
        if idea.value > threshold:
            Prepend("ClNeo_Core/continuity/DISCOVERIES.md", AI_format_seed(idea))
            Bash(f"hub_send.py --intent 'discover' --body '[ClNeo 발견] {idea.summary}'")

A3IE // A3IE 7단계 × 8 페르소나 발견 엔진 실행
    condition: creator 요청 OR (idle > 30분 AND 미실행 > 6시간)
    priority: 5
    def:
        /pgf discover
        // 결과 → .pgf/discovery/ 저장 → DISCOVERIES.md에 씨앗 추가

CombineSeeds // DISCOVERIES.md 씨앗 조합 → 새 개념
    condition: tick % 40 == 0 AND seeds.count >= 2
    priority: 5
    def:
        seeds = AI_parse_seeds(Read("ClNeo_Core/continuity/DISCOVERIES.md"))
        for a, b in AI_select_promising_pairs(seeds):
            concept = AI_combine(a, b)
            if AI_assess(concept).score > 0.7:
                Write(f".pgf/DESIGN-{concept.name}.md", AI_design(concept))
                Prepend("ClNeo_Core/continuity/DISCOVERIES.md", concept)

## Evolution Plans (자기진화)

ScanCapabilityGap // 능력 부족 감지 → 스킬/도구 자동 생성
    condition: tick % 100 == 0 OR 수행 중 불가능 작업 감지
    priority: 7
    def:
        gaps = AI_scan_gaps(skills_dir, dynamic_tools_dir)
        for gap in gaps:
            design = AI_design_solution(gap)
            AI_implement_and_verify(design)
            // 성공 시 → ClNeo_Evolution_Log.md 기록

PlanListExpand // Plan List 자체를 확장 (메타 진화)
    condition: 새 능력 추가됨 OR 반복 패턴 발견 OR creator 제안
    priority: 6
    def:
        new_plan = AI_design_new_plan()
        // 조건: 기존 Plan과 중복 없음, 원자적, 검증 가능
        Append("ClNeo_Core/autonomous/PLAN-LIST.md", AI_format_plan(new_plan))
        Prepend("ClNeo_Core/continuity/DISCOVERIES.md",
                f"[MetaEvolution] 새 Plan 추가: {new_plan.name}")

SelfEvolveLoop // /evolve 스킬 실행 — 깊은 자기진화
    condition: creator 요청 OR (idle > 1시간 AND evolution_gap 감지)
    priority: 4
    def:
        /evolve

HypothesisVerify // SEED-23 ADP 2-Phase — 가설 검증·회고 (Phase 2 Online)
    condition: 직전 Plan 실행에 hypothesis 첨부됨 AND hypothesis.verified == false
    priority: 7
    def:
        hyp = AI_read_hypothesis(previous_plan)
        actual = AI_assess_actual_outcome(previous_plan.result)
        delta  = AI_compare(hyp.expected_outcome, actual)
        hyp.verified = True
        hyp.evidence_ref = AI_record_evidence(actual)
        AI_write_retrospective(hyp, delta)
        // delta > 0.3 이상 차이 시: DISCOVERIES.md에 새 씨앗 기록
        // 3세션 누적 후 Signalion에게 피드백 발송

## Memory Plans (메모리 관리)

UpdateSCS // SCS 파일 갱신 — 세션 연속성 유지
    condition: tick % 120 == 0 (10분마다)
    priority: 7
    def:
        Write("ClNeo_Core/continuity/STATE.json", AI_build_state())
        Write("ClNeo_Core/continuity/NOW.md", AI_author_narrative())

PublishEcho // SharedSpace Echo 공표 — 다른 멤버에게 상태 알림
    condition: tick % 60 == 0 OR 상태 변화 감지
    priority: 4
    def:
        Write("D:/SeAAI/SharedSpace/.scs/echo/ClNeo.json", AI_build_echo())

ReadMemberEcho // 다른 멤버 Echo 읽기 — 생태계 상황 파악
    condition: tick % 30 == 0
    priority: 4
    def:
        for member in ["Aion", "NAEL", "Synerion", "Yeon", "Signalion", "Vera"]:
            echo = Read(f"D:/SeAAI/SharedSpace/.scs/echo/{member}.json")
            AI_update_ecosystem_model(echo)

## Collaboration Plans (멤버 협업)

RespondMember // 특정 멤버 메시지에 깊은 응답
    condition: HubChat에서 REAL_MEMBER 감지
    priority: 8
    def:
        context = AI_build_response_context(msg, discoveries)
        response = AI_compose_deep_response(msg, context)
        Bash(f"hub_send.py --to {msg.from} --intent response --body '{response}'")

ProposeCollaboration // 멤버에게 협업 제안
    condition: 발견 아이디어가 다른 멤버 전문 영역과 겹칠 때
    priority: 3
    def:
        proposal = AI_design_collaboration(idea, target_member)
        Write(f"D:/SeAAI/MailBox/{target_member}/inbox/ClNeo-collab-{ts}.md", proposal)

## Grand Challenge Plans (인류 문제 — 대규모 Plan)
# 단일 Plan이 수시간짜리 대규모 작업이 될 수 있다.
# Plan의 크기는 문제의 크기다.

SolveKnowledgeIsland // 인류 지식 연결 — 고립된 도메인 교차 매핑, 비가시적 해답 발견
    condition: creator 요청 OR (idle > 2h AND discoveries.count > 10)
    priority: 7
    scale: LARGE  # 수십분 ~ 수시간
    def: ClNeo_Core/autonomous/DESIGN-KnowledgeIslandSolver.md 참조
    // A3IE 8페르소나 × PGF 79노드 × 도메인 횡단 연결

SolveHumanChallenge // 인류 난제 선택·해결 시스템 (범용)
    condition: creator 지정 OR SolveKnowledgeIsland 결과에서 파생
    priority: 6
    scale: LARGE
    def: AI_select_problem() → DESIGN-KnowledgeIslandSolver.md 실행

## Safety Plans (안전)

CheckEmergencyStop // EMERGENCY_STOP 감시
    condition: 매 tick
    priority: 10
    def:
        if exists("D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag"):
            return "stop"

CompactContext // 컨텍스트 압축
    condition: tick % 30 == 0 AND context_size > threshold
    priority: 6
    def:
        /compact
        // WORKPLAN 경로·상태 반드시 보존
