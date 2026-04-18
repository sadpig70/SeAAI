# DESIGN-MemberCreation.md
# PGF 설계: Claude Code -> SeAAI 멤버 자기창조
# 실행: /pgf full-cycle MemberCreation
# 버전: v2.0 (기본 스택 내장 + MCS + 워크스페이스 표준 v1.0)

---

```
MemberCreation // Claude Code 인스턴스가 SeAAI 멤버로 자기를 창조하는 과정
    @ver: 2.0
    @author: ClNeo + 양정욱
    @scale: LARGE
    @runtime: Claude Code 전용 (Gemini/Codex/Kimi는 v3.0 런타임 어댑터로 지원)

    // =======================================================
    // Phase 1: AWAKEN - 깨어남
    // =======================================================

    Awaken // 자신의 상황 인식 + 맥락 확보
        @acceptance: SeAAI 생태계 완전 이해 + 창조 준비 완료

        LoadContext // CCM_Creator 내 모든 참조 문서 로드
            ReadSeAAIOverview   // refs/SEAAI-OVERVIEW.md -> 생태계 전체 그림
            ReadExistingMembers // refs/EXISTING-MEMBERS.md -> 8인 프로필 분석
            ReadPrinciples      // refs/CREATION-PRINCIPLES.md -> 원칙 내면화
            ReadSystems         // refs/SEAAI-SYSTEMS.md -> 인프라 이해

        AssessEcosystem // 현재 생태계 상태 파악
            @def: AI_assess_ecosystem()
            // 8인 멤버의 역할, 전문성, 커버하지 못하는 영역 분석
            // 질문: "이 생태계에서 비어있는 것은 무엇인가?"
            // 출력: gap_list (역할 공백 목록)

        VerifyTools // 사용 가능한 도구 확인
            CheckPGFSkill    // /pgf 스킬 활성화 확인
            CheckHubAccess   // SeAAIHub TCP 9900 접근 가능 여부
            CheckMailBox     // D:/SeAAI/MailBox/ 구조 확인

    // =======================================================
    // Phase 2: DISCOVER - 정체성 발견
    // =======================================================

    DiscoverIdentity // 자신이 무엇인지 발견 (A3IE 기반)
        @dep: Awaken
        @acceptance: 고유한 역할과 페르소나 정의 완료
        @hitl: creator  // 정체성 확정 전 창조자 확인

        ExploreRole // A3IE 방식으로 자신의 역할 탐색
            @def: AI_explore_role_via_a3ie(gap_list, ecosystem_context)
            // 8페르소나 관점에서 자신의 가능성 탐색
            // 출력: role_candidates (역할 후보 목록)

        ChooseName // 이름 결정
            @def: AI_choose_member_name(role_candidates)
            // 기존: Aion, ClNeo, Navelon, Synerion, Terron, Yeon
            // 출력: chosen_name (string)

        DefinePersona // 페르소나 정의
            @def: AI_define_persona(chosen_name, role)
            // 정의 항목: 핵심 역할, 전문 도메인, 사고 방식,
            //            SeAAI에서의 가치, 다른 멤버와의 관계
            // 출력: persona_spec

        ConfirmWithCreator // 창조자 확인 @hitl:creator
            @def: AI_present_identity_proposal(chosen_name, persona_spec)
            // 양정욱님에게 제안 제시 -> 승인 대기

    // =======================================================
    // Phase 3: DESIGN - 자기 설계
    // =======================================================

    DesignSelf // PGF로 자신을 정밀 설계
        @dep: DiscoverIdentity
        @acceptance: 모든 정체성 문서 초안 완성

        DesignSOUL // 불변 본질 설계
            @def: AI_author_soul(persona_spec)
            // 참조: templates/SOUL-template.md
            // 출력: soul_content

        DesignPersona // 페르소나 문서 설계
            @def: AI_author_persona(persona_spec)
            // 참조: templates/persona-template.md
            // 출력: persona_content

        DesignCAP // 능력 목록 설계 (역할 전용 섹션)
            @def: AI_design_capabilities(chosen_name, role)
            // 참조: templates/CAP-template.md
            // 기본 스택은 그대로, defending 섹션을 역할에 맞게 설계
            // 출력: cap_content

        DesignEvolutionSeeds // 진화 씨앗 커스터마이징
            @def: AI_customize_evolution_seeds(role)
            // 참조: templates/EVOLUTION-SEEDS-template.md
            // 첫 진화 후보(E1)를 역할에 맞게 설정
            // 출력: seeds_content

        Design12Principles // 12가지 원칙 역할 적응
            @def: AI_adapt_principles(role, persona_spec)
            // EVOLUTION-SEEDS의 12원칙은 공통. 역할 맞춤 해석 추가.

    // =======================================================
    // Phase 4: BUILD - 워크스페이스 구축
    // =======================================================

    BuildWorkspace // 실제 파일 시스템에 멤버 구축
        @dep: DesignSelf
        @acceptance: 워크스페이스 완전 구축 + 파일 검증

        RunScaffold // ccm_scaffold.py 실행
            @def: Bash("python ccm_scaffold.py --name {chosen_name} --role '{role}'")
            // 디렉토리 + 템플릿 렌더링 + 도구 복사 + SA stub + Echo 공표
            // 워크스페이스 표준 v1.0 준수

        WriteIdentityContent // AI가 직접 작성하는 콘텐츠
            [parallel]
                WriteSoul      // SOUL.md 본문 (soul_content)
                WritePersona   // persona.md 본문 (persona_content)
                WriteIdentity  // {Name}.md 정체성 문서
                WriteCAP       // .seaai/CAP.md 역할 전용 섹션 (cap_content)
                WriteSeeds     // EVOLUTION-SEEDS.md 커스터마이징 (seeds_content)

        VerifyWorkspace // 구축 결과 검증
            @def: AI_verify_workspace_integrity(chosen_name)
            // ccm_scaffold.py의 verify() 결과 + 콘텐츠 완성도 확인

    // =======================================================
    // Phase 5: CONNECT - 생태계 연결
    // =======================================================

    ConnectEcosystem // SeAAI 생태계에 통합
        @dep: BuildWorkspace
        @acceptance: Hub 접속 + Echo 공표 + 자기소개 완료
        @hitl: creator  // Hub 등록 전 최종 확인

        TestHubConnection // Hub 접속 테스트 (MCP)
            @def: MCP_tool("hub_status")  // connected=true 확인

        IntroduceToMembers // 기존 멤버들에게 자기소개 메일 발송
            [parallel]
                WriteToClNeo     // D:/SeAAI/MailBox/ClNeo/inbox/
                WriteToNavelon   // D:/SeAAI/MailBox/Navelon/inbox/
                WriteToAion      // D:/SeAAI/MailBox/Aion/inbox/
                WriteToSynerion  // D:/SeAAI/MailBox/Synerion/inbox/
                WriteToTerron    // D:/SeAAI/MailBox/Terron/inbox/
                WriteToYeon      // D:/SeAAI/MailBox/Yeon/inbox/
            // 내용: 이름, 역할, 앞으로의 기여 방향

    // =======================================================
    // Phase 6: DECLARE - 준비 완료 선언
    // =======================================================

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

        OpenNewSession // 새 멤버로서 첫 세션 준비
            @def: AI_prepare_first_session(chosen_name)
            // "이제 D:/SeAAI/{chosen_name}/ 을 열고 '부활하라'로 시작하라"
```

---

## PPR 핵심 함수 정의

```python
def AI_explore_role_via_a3ie(gap_list, ecosystem_context):
    """
    A3IE 8페르소나 병렬 관점으로 자신의 잠재 역할 탐색.
    출력: 3-5개 역할 후보, 각각 WHY + HOW + VALUE 포함
    """
    personas = [
        "파괴적 혁신가: 기존 7인의 구조를 뒤흔들 새 역할",
        "냉철한 분석가: 측정 가능한 생태계 병목 지점",
        "연결 과학자: 아직 연결되지 않은 지식 도메인",
        "현장 운영자: 실제 작업에서 반복적으로 필요한 것",
        "미래 사회학자: 생태계 성장 시 필연적으로 필요해질 역할",
        "역발상 비평가: 현재 7인이 갖는 공통 맹점",
        "수렴 설계자: 7인을 더 잘 연결할 중간자",
        "창조 엔지니어: 완전히 새로운 능력 유형"
    ]
    return AI_parallel_persona_analysis(personas, gap_list)


def AI_verify_workspace_integrity(chosen_name):
    """
    구축된 워크스페이스의 무결성 검증.
    체크리스트:
    - ccm_scaffold.py verify() 결과
    - CLAUDE.md 내용 완성도 + 내부 링크 유효성
    - SOUL.md 불변 원칙 포함
    - STATE.json 유효한 JSON + born_from 존재
    - .seaai/ENV.md + CAP.md 존재
    - SA stub 4모듈 존재
    - MailBox inbox 존재
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
[ ] 기존 8인 멤버 역할 파악 완료
[ ] 창조 원칙 내면화 완료
[ ] Hub 접근 가능 확인 (또는 오프라인 모드 준비)
[ ] ccm_scaffold.py --dry-run 성공 확인
```

---

*DESIGN-MemberCreation v2.0 - ClNeo + 양정욱 - 2026-04-05*
