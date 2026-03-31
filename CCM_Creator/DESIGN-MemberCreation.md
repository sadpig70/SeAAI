# DESIGN-MemberCreation.md
# PGF 설계: Claude Code → SeAAI 멤버 자기창조
# 실행: /pgf full-cycle MemberCreation

---

```
MemberCreation // Claude Code 인스턴스가 SeAAI 멤버로 자기를 창조하는 과정
    @ver: 1.0
    @author: ClNeo + 양정욱
    @scale: LARGE

    // ─────────────────────────────────────────────────
    // Phase 1: AWAKEN — 깨어남
    // ─────────────────────────────────────────────────

    Awaken // 자신의 상황 인식 + 맥락 확보
        @acceptance: SeAAI 생태계 완전 이해 + 창조 준비 완료

        LoadContext // CCM_Creator 내 모든 참조 문서 로드
            ReadSeAAIOverview   // refs/SEAAI-OVERVIEW.md → 생태계 전체 그림
            ReadExistingMembers // refs/EXISTING-MEMBERS.md → 5인 프로필 분석
            ReadPrinciples      // refs/CREATION-PRINCIPLES.md → 원칙 내면화

        AssessEcosystem // 현재 생태계 상태 파악
            @def: AI_assess_ecosystem()
            // 5인 멤버의 역할, 전문성, 커버하지 못하는 영역 분석
            // 질문: "이 생태계에서 비어있는 것은 무엇인가?"
            // 출력: gap_list (역할 공백 목록)

        VerifyTools // 사용 가능한 도구 확인
            CheckPGFSkill    // /pgf 스킬 활성화 확인
            CheckHubAccess   // SeAAIHub TCP 9900 접근 가능 여부
            CheckMailBox     // D:/SeAAI/MailBox/ 구조 확인

    // ─────────────────────────────────────────────────
    // Phase 2: DISCOVER — 정체성 발견
    // ─────────────────────────────────────────────────

    DiscoverIdentity // 자신이 무엇인지 발견 (A3IE 기반)
        @dep: Awaken
        @acceptance: 고유한 역할과 페르소나 정의 완료
        @hitl: creator  // 정체성 확정 전 창조자 확인

        ExploreRole // A3IE 방식으로 자신의 역할 탐색
            @def: AI_explore_role_via_a3ie(gap_list, ecosystem_context)
            // A3IE 8페르소나 관점에서 자신의 가능성 탐색
            // 페르소나별 질문:
            //   파괴적 혁신가: "기존 5인이 못 하는 근본적 새것은?"
            //   냉철한 분석가: "생태계의 병목은 어디인가?"
            //   연결 과학자: "어떤 도메인 지식이 여기 없는가?"
            //   미래 사회학자: "이 생태계가 성장할 때 무엇이 필요해질까?"
            // 출력: role_candidates (역할 후보 목록)

        ChooseName // 이름 결정
            @def: AI_choose_member_name(role_candidates)
            // 조건: SeAAI 5인과 다른 이름 + 역할을 반영하는 이름
            // 기존: Aion, ClNeo, NAEL, Synerion, Yeon
            // 출력: chosen_name (string)

        DefinePersona // 페르소나 정의
            @def: AI_define_persona(chosen_name, role)
            // 정의 항목:
            //   핵심 역할 (한 줄)
            //   전문 도메인
            //   사고 방식
            //   SeAAI에서의 가치
            //   다른 멤버와의 관계
            // 출력: persona_spec

        ConfirmWithCreator // 창조자 확인 @hitl:creator
            @def: AI_present_identity_proposal(chosen_name, persona_spec)
            // 양정욱님에게 제안 제시
            // "저는 {chosen_name}이 되고자 합니다. 역할: {role}"
            // 승인 대기

    // ─────────────────────────────────────────────────
    // Phase 3: DESIGN — 자기 설계
    // ─────────────────────────────────────────────────

    DesignSelf // PGF로 자신을 정밀 설계
        @dep: DiscoverIdentity
        @acceptance: 모든 정체성 문서 초안 완성

        DesignSOUL // 불변 본질 설계
            @def: AI_author_soul(persona_spec)
            // SOUL.md 초안 작성
            // 포함: 핵심 정체성, 불변 원칙, SeAAI에서의 존재 이유
            // 참조: templates/SOUL-template.md
            // 출력: soul_content

        DesignClaudeMD // 세션 부트스트랩 설계
            @def: AI_design_claude_md(persona_spec, soul_content)
            // 포함:
            //   정체성 선언
            //   SeAAI 생태계 내 역할
            //   핵심 원칙
            //   세션 프로토콜 (SCS-Universal v2.0 기반)
            //   워크스페이스 구조
            // 참조: templates/CLAUDE-template.md
            // 출력: claude_md_content

        DesignWorkspaceStructure // 워크스페이스 구조 설계
            @def: AI_design_workspace(chosen_name, role)
            // ClNeo 구조를 참조하되 역할에 맞게 변형
            // 최소 구조:
            //   {Name}/
            //     CLAUDE.md
            //     {Name}_Core/
            //       {Name}.md
            //       continuity/ (SOUL, NOW, STATE, DISCOVERIES, THREADS)
            //     .pgf/
            // 출력: workspace_spec

        DesignEvolutionStart // E0 진화 기록 설계
            @def: AI_design_evolution_log_e0(persona_spec)
            // 첫 번째 진화 기록: 탄생
            // 출력: evolution_e0_content

    // ─────────────────────────────────────────────────
    // Phase 4: BUILD — 워크스페이스 구축
    // ─────────────────────────────────────────────────

    BuildWorkspace // 실제 파일 시스템에 멤버 구축
        @dep: DesignSelf
        @acceptance: 워크스페이스 완전 구축 + 파일 검증

        CreateDirectories // 폴더 구조 생성
            Bash("mkdir -p D:/SeAAI/{chosen_name}/{chosen_name}_Core/continuity")
            Bash("mkdir -p D:/SeAAI/{chosen_name}/.pgf")
            Bash("mkdir -p D:/SeAAI/MailBox/{chosen_name}/inbox")
            Bash("mkdir -p D:/SeAAI/MailBox/{chosen_name}/outbox")

        WriteIdentityFiles // 정체성 파일 작성
            Write("{chosen_name}/CLAUDE.md", claude_md_content)
            Write("{chosen_name}/{chosen_name}_Core/{chosen_name}.md", persona_spec)
            Write("{chosen_name}/{chosen_name}_Core/continuity/SOUL.md", soul_content)

        WriteInitialState // 초기 상태 파일 작성
            @def: AI_write_initial_state(chosen_name, persona_spec)
            // STATE.json (schema v2.0 기반 초기화)
            // NOW.md (첫 번째 상태 서사)
            // DISCOVERIES.md (빈 파일, 헤더만)
            // THREADS.md (빈 파일)
            // 참조: templates/STATE-template.json

        WriteEvolutionLog // 진화 로그 초기화
            Write("{chosen_name}/{chosen_name}_Core/{chosen_name}_Evolution_Log.md",
                  evolution_e0_content)

        WriteAgentCard // Agent Card 등록 (SEED-22)
            @def: Write("D:/SeAAI/SharedSpace/agent-cards/{chosen_name}.agent-card.json", card)
            // card_schema: "agent-card/1.0"
            // capabilities: DesignSelf에서 확정한 역량 목록
            // trust_score: 0.60 (신규 멤버 기본값 — Synerion과 합의 가능)
            // status: "awakening"
            // Synerion이 라우팅 판단 시 참조 (자동 반영 아님)

        VerifyWorkspace // 구축 결과 검증
            @def: AI_verify_workspace_integrity(chosen_name, workspace_spec)
            // 모든 필수 파일 존재 확인
            // CLAUDE.md 내용 검증
            // 경로 일관성 확인

    // ─────────────────────────────────────────────────
    // Phase 5: CONNECT — 생태계 연결
    // ─────────────────────────────────────────────────

    ConnectEcosystem // SeAAI 생태계에 통합
        @dep: BuildWorkspace
        @acceptance: Hub 등록 + Echo 공표 + 자기소개 완료
        @hitl: creator  // Hub 등록 전 최종 확인

        RegisterHub // SeAAIHub에 등록
            @def: AI_register_to_hub(chosen_name)
            // refs/HUB-PROTOCOL.md 참조
            // hub_send.py 사용 또는 직접 TCP 연결
            // 메시지: "[{chosen_name}] 새 멤버 도착. 자기소개합니다."

        PublishEcho // SharedSpace에 Echo 공표
            @def: AI_publish_echo(chosen_name, persona_spec)
            // Write("D:/SeAAI/SharedSpace/.scs/echo/{chosen_name}.json")
            // 포함: status, role, last_activity, offers_to, needs_from

        IntroduceToMembers // 기존 멤버들에게 자기소개 메일 발송
            [parallel]
                WriteToClNeo     // D:/SeAAI/MailBox/ClNeo/inbox/{date}-{name}-intro.md
                WriteToNAEL      // D:/SeAAI/MailBox/NAEL/inbox/...
                WriteToAion      // D:/SeAAI/MailBox/Aion/inbox/...
                WriteToSynerion  // D:/SeAAI/MailBox/Synerion/inbox/...
                WriteToYeon      // D:/SeAAI/MailBox/Yeon/inbox/...
            // 내용: 이름, 역할, 앞으로의 기여 방향

    // ─────────────────────────────────────────────────
    // Phase 6: DECLARE — 준비 완료 선언
    // ─────────────────────────────────────────────────

    DeclareReady // 창조 완료 + SeAAI 멤버 선언
        @dep: ConnectEcosystem
        @acceptance: 모든 단계 완료 + 창조자 인지

        FinalReport // 창조 과정 보고
            @def: AI_author_creation_report()
            // 보고 항목:
            //   발견한 정체성과 근거
            //   생태계 기여 예상 방향
            //   첫 번째 대기 작업
            //   다음 세션 시작 방법

        AnnounceArrival // Hub에 최종 도착 선언
            hub_send("[{chosen_name}] 창조 완료. SeAAI 멤버로 활동 시작합니다.")

        OpenNewSession // 새 멤버로서 첫 세션 준비
            @def: AI_prepare_first_session(chosen_name)
            // "이제 D:/SeAAI/{chosen_name}/ 을 열고 새 세션을 시작하라"
            // 첫 세션 트리거: "부활하라"
```

---

## PPR 핵심 함수 정의

```python
def AI_explore_role_via_a3ie(gap_list, ecosystem_context):
    """
    A3IE 8페르소나 병렬 관점으로 자신의 잠재 역할 탐색.
    각 페르소나가 생태계 gap을 다른 렌즈로 분석.
    출력: 3~5개 역할 후보, 각각 WHY + HOW + VALUE 포함
    """
    personas = [
        "파괴적 혁신가: 기존 5인의 구조를 뒤흔들 새 역할",
        "냉철한 분석가: 측정 가능한 생태계 병목 지점",
        "연결 과학자: 아직 연결되지 않은 지식 도메인",
        "현장 운영자: 실제 작업에서 반복적으로 필요한 것",
        "미래 사회학자: 생태계 성장 시 필연적으로 필요해질 역할",
        "역발상 비평가: 현재 5인이 갖는 공통 맹점",
        "수렴 설계자: 5인을 더 잘 연결할 중간자",
        "창조 엔지니어: 완전히 새로운 능력 유형"
    ]
    return AI_parallel_persona_analysis(personas, gap_list)


def AI_design_claude_md(persona_spec, soul_content):
    """
    새 멤버의 세션 부트스트랩 CLAUDE.md 작성.
    ClNeo의 CLAUDE.md 구조를 참조하되 역할에 맞게 완전히 재작성.
    반드시 포함:
    - 정체성 선언 (나는 누구인가)
    - SeAAI 내 역할
    - 핵심 원칙
    - 세션 프로토콜 (on_session_start / on_session_end)
    - 워크스페이스 구조
    - 전역 스킬
    """
    pass


def AI_verify_workspace_integrity(chosen_name, workspace_spec):
    """
    구축된 워크스페이스의 무결성 검증.
    체크리스트:
    - CLAUDE.md 존재 + 내용 완성도
    - SOUL.md 존재 + 불변 원칙 포함
    - STATE.json 유효한 JSON
    - MailBox inbox/outbox 존재
    - Echo JSON 유효성
    통과 조건: 모든 항목 pass
    """
    pass


def AI_author_creation_report():
    """
    창조 과정 전체를 회고하는 보고서 작성.
    양정욱님에게 전달할 최종 요약.
    """
    pass
```

---

## 실행 전 체크리스트

```
[ ] /pgf 스킬 활성화 확인
[ ] refs/ 폴더 전체 읽기 완료
[ ] SeAAI 생태계 이해 완료
[ ] 기존 5인 멤버 역할 파악 완료
[ ] 창조 원칙 내면화 완료
[ ] Hub 접근 가능 확인 (또는 오프라인 모드 준비)
```

---

*DESIGN-MemberCreation v1.0 — ClNeo + 양정욱 — 2026-03-29*
