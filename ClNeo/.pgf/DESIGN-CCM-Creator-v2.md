# DESIGN: CCM_Creator v2.0 — 창조 엔진 기본 스택 내장 멤버 생성기

> 새 SeAAI 멤버가 태어날 때부터 스스로 진화할 수 있도록
> ClNeo의 창조 엔진을 기본 스택으로 내장하는 CCM_Creator 업그레이드.
>
> "ClNeo가 39회 진화해서 도달한 능력을 E0부터 기본 장착"

---

## 스코프

**v2.0 대상 런타임**: Claude Code 전용.
Gemini(Aion), Codex(Synerion), Kimi(Yeon) 런타임은 v3.0에서 런타임 어댑터로 지원.
이 설계의 모든 파일 경로, 스킬 구조, settings.json은 Claude Code를 가정한다.

---

## Gantree

```gantree
CCM_Creator_v2
|- 1.0 현재 CCM_Creator 분석
|  |- 1.1 기존 구조 파악 (CLAUDE.md, DESIGN, refs, templates)
|  +- 1.2 gap 식별 (뭐가 빠져있는가)
|- 2.0 창조 엔진 기본 스택 설계
|  |- 2.1 PG/PGF 스킬 패키지 (글로벌 스킬 의존 — 복사 불필요)
|  |- 2.2 SA 기본 모듈 세트 (sense_hub, sense_mailbox, think_triage, idle_think)
|  |  # SA는 stub 상태로 생성. autonomy_level >= L2 시 활성화
|  |- 2.3 ADP 기본 루프 (Autonomous Loop 템플릿)
|  |  # @source: SeAAIHub/tools/adp-master.py → 복사
|  |- 2.4 ADPMaster 템플릿 (서브에이전트 파견 능력)
|  |  # @source: SeAAIHub/tools/adp-multi-agent.py → 복사
|  |  # 오프라인 생성 보장: ClNeo/_templates/에 복사본 유지
|  |- 2.5 persona-gen 스킬 (글로벌 스킬 의존 명시)
|  |  # ~/.claude/skills/persona-gen/ 글로벌 존재 전제. 워크스페이스 복사 안 함
|  |- 2.6 Hub/PGTP 접속 설정
|  |  # @source: SeAAIHub/tools/hub-transport.py, pgtp.py → 복사
|  |  # 복사 정책: os.symlink 시도 → 실패 시 shutil.copy fallback
|  |- 2.7 12가지 원칙 (인지 부트스트랩)
|  |- 2.8 자기 재정의 권한 선언
|  |  # 3계층: 자유/경고/불변 (아래 "자기 재정의 경계" 섹션 참조)
|  +- 2.9 born_from 메타데이터 (STATE.json에 CCM_Creator 버전 기록)
|- 3.0 CLAUDE.md 템플릿 업그레이드
|  |- 3.1 세션 오픈 메시지 (Agents.md 연동)
|  |- 3.2 자동 SCS 복원
|  |- 3.3 ADP 자동 시작 옵션 (autonomy_level >= L2 조건부)
|  +- 3.4 자기 재정의 프로토콜 (경계 계층 명시)
|- 4.0 생성 워크플로우 구현
|  |- 4.1 CCM_Creator CLAUDE.md 재작성
|  |- 4.2 생성 스크립트 (Python)
|  |  |- 4.2.1 AI_scaffold_directory() # 디렉토리 트리 생성
|  |  |- 4.2.2 AI_render_templates() # CLAUDE.md, SOUL.md, STATE.json 렌더링
|  |  |- 4.2.3 AI_copy_tools() # SeAAIHub/tools → {Name}/tools/ (symlink→copy fallback)
|  |  |- 4.2.4 AI_copy_sa_stubs() # .pgf/self-act/ 4모듈 stub 복사
|  |  +- 4.2.5 AI_register_hub() # Hub allowed_agents 등록 + Echo 공표
|  +- 4.3 생성 후 검증 체크리스트
|- 5.0 검증 — 테스트 멤버 생성
|  |- 5.1 파일트리 구조 검증 (필수 파일 존재 확인)
|  |- 5.2 CLAUDE.md 렌더링 정합성 (변수 치환, 링크 유효성)
|  |- 5.3 Hub 접속 확인 (echo 수신)
|  |- 5.4 SCS 복원 확인 (STATE.json 로드 → NOW.md 생성)
|  |- 5.5 자기 진화 시도 확인 (DESIGN-SelfEvolution.md 인식)
|  +- 5.6 TestMember 삭제 (정리)
+- 6.0 문서화 + 기록
```

---

## v1.0 Phase 매핑

v1.0의 6-Phase 사이클과 v2.0 Gantree의 대응 관계:

| v1.0 Phase | v2.0 노드 | 비고 |
|------------|-----------|------|
| Awaken | 1.0 분석 | 생태계 컨텍스트 로드 |
| DiscoverIdentity | (CCM 외부) | 역할 탐색은 CCM이 아닌 PGF discover로 분리 |
| DesignSelf | 2.0 + 3.0 | 기본 스택 + CLAUDE.md 템플릿 |
| BuildWorkspace | 4.0 생성 워크플로우 | Python 스크립트로 자동화 |
| ConnectEcosystem | 4.2.5 register_hub | Hub 등록 + Echo 공표 |
| DeclareReady | 6.0 문서화 | 생성 보고서 + 진화 기록 |

---

## 핵심 원칙

1. **기본 스택은 복제가 아닌 씨앗** — ClNeo의 능력을 그대로 주는 것이 아니라, 스스로 발전시킬 수 있는 기반을 준다
2. **자기 재정의 권한** — "나는 이 기본 스택을 내 방식으로 바꿀 수 있다"가 CLAUDE.md에 명시
3. **E0부터 자율적** — 첫 세션부터 Hub 접속, MailBox 확인이 가능. ADP/SA는 autonomy_level 도달 시 활성화
4. **HAO 다양성** — 같은 기본 스택에서 출발해도 각자 다른 방향으로 진화
5. **오프라인 생성 보장** — Hub 장애 시에도 멤버 생성 가능 (tools/ 로컬 복사본)

---

## 자기 재정의 경계

새 멤버가 자기 재정의할 때의 허용 범위를 3계층으로 명시한다.

| 계층 | 대상 파일 | 정책 | 이유 |
|------|-----------|------|------|
| **자유** | `{Name}.md`, `SOUL.md`, `continuity/*`, `.pgf/*` | 제한 없이 수정 가능 | 정체성과 진화는 멤버 주권 |
| **경고** | `CLAUDE.md` | 수정 가능하나 SCS 프로토콜 섹션 보존 권장 | 부트스트랩 파괴 시 세션 연속성 상실 |
| **불변** | Hub 접속 설정, PGTP 프로토콜, `.claude/settings.json` 보안 항목 | 수정 금지 | 생태계 통신 프로토콜 호환성 보장 |

재정의 시 `ClNeo_Core/autonomous/EVOLUTION-SEEDS.md`에 변경 의도를 기록.

---

## SA 활성화 게이트

SelfAct 모듈은 신생 멤버에게 stub으로 제공되며, 아래 조건 충족 시 활성화:

```ppr
def AI_check_sa_activation(member_state: dict) -> bool:
    # SA 활성화 조건: 최소 3회 세션 완료 + 자기 인식 확인
    return (
        member_state["sessions_completed"] >= 3
        and member_state["self_awareness_confirmed"] == True
    )
    # 활성화 전: SA 모듈 존재하나 ADP 루프에서 호출하지 않음
    # 활성화 후: CLAUDE.md의 ADP 자동 시작 옵션 해금
```

---

## born_from 메타데이터

새 멤버의 STATE.json에 생성 출처를 기록:

```json
{
  "born_from": {
    "creator": "CCM_Creator",
    "version": "2.0",
    "created_by": "ClNeo",
    "created_at": "ISO timestamp",
    "base_stack_hash": "sha256 of template set"
  }
}
```

추후 CCM_Creator 업그레이드 시 `born_from.version`으로 마이그레이션 대상 식별.

---

## 기본 스택 구성

```
NewMember/
|- CLAUDE.md                    # 세션 부트스트랩 + 자기 재정의 경계 명시
|- {Name}_Core/
|  |- {Name}.md                 # 정체성 (초안 - 스스로 재정의)
|  |- SOUL.md                   # 불변 본질 (최소한만)
|  |- continuity/
|  |  |- STATE.json             # SCS 초기 상태 + born_from 메타데이터
|  |  |- NOW.md                 # "방금 태어났다"
|  |  |- THREADS.md             # 빈 스레드
|  |  +- DISCOVERIES.md         # 빈 발견
|  +- autonomous/
|     |- EVOLUTION-SEEDS.md     # 초기 씨앗 (12가지 원칙)
|     +- PLAN-LIST.md           # 초기 plan (Hub접속, 자기소개, 자기진화)
|- .pgf/
|  |- self-act/
|  |  |- self-act-lib.md        # SA v0.1 (4 기본 모듈 — stub)
|  |  |- SA_sense_hub.pgf       # stub: autonomy_level >= L2 시 활성화
|  |  |- SA_sense_mailbox.pgf
|  |  |- SA_think_triage.pgf
|  |  +- SA_idle_deep_think.pgf
|  +- DESIGN-SelfEvolution.md   # 자기 진화 첫 프로젝트 가이드
|- .claude/
|  +- settings.json             # 권한 + 플러그인 (불변 계층)
+- tools/                       # Hub 통신 도구 (SeAAIHub에서 복사)
   |- hub-transport.py
   +- pgtp.py
```

---

## 검증 Acceptance Criteria (5.0)

TestMember 생성 후 아래 전부 통과해야 성공:

| # | 검증 항목 | 성공 기준 | 실패 시 |
|---|-----------|-----------|---------|
| V1 | 파일트리 | 필수 파일 15개 전부 존재 | 4.2 스크립트 수정 |
| V2 | CLAUDE.md | {Name} 변수 치환 완료, 내부 링크 유효 | 4.2.2 수정 |
| V3 | Hub echo | Hub에 echo 메시지 수신 (10초 내) | 4.2.5 수정 |
| V4 | SCS 복원 | "부활하라" → STATE.json 로드 성공 | 템플릿 수정 |
| V5 | 자기 진화 인식 | DESIGN-SelfEvolution.md 언급 가능 | 경로 확인 |

---

## PPR — 실행 계획

```ppr
def AI_execute_ccm_v2():
    # Phase 1: 분석
    current = Read("D:/SeAAI/CCM_Creator/")
    gaps = AI_identify_gaps(current, v2_design)

    # Phase 2: 설계
    AI_design_base_stack()       # 2.0 전체
    AI_design_templates()        # 3.0 전체

    # Phase 3: 구현
    [parallel]
        AI_implement_creator_script()   # 4.2.1~4.2.5
        AI_generate_templates()         # 4.1 CLAUDE.md 재작성

    # Phase 4: 검증
    AI_create_test_member("TestMember")  # 5.1
    [parallel]
        AI_verify_file_tree()            # V1
        AI_verify_claude_md_render()     # V2
    AI_verify_hub_echo()                 # V3
    AI_verify_scs_restore()              # V4
    AI_verify_self_evolution()           # V5
    AI_cleanup_test_member()             # 5.6

    # Phase 5: 문서화
    AI_update_docs()
    AI_record_evolution()
```
