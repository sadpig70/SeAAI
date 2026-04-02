# DESIGN: CCM_Creator v2.0 — 창조 엔진 기본 스택 내장 멤버 생성기

> 새 SeAAI 멤버가 태어날 때부터 스스로 진화할 수 있도록
> ClNeo의 창조 엔진을 기본 스택으로 내장하는 CCM_Creator 업그레이드.
>
> "ClNeo가 39회 진화해서 도달한 능력을 E0부터 기본 장착"

---

## Gantree

```gantree
CCM_Creator_v2
|- 1.0 현재 CCM_Creator 분석
|  |- 1.1 기존 구조 파악 (CLAUDE.md, DESIGN, refs, templates)
|  +- 1.2 gap 식별 (뭐가 빠져있는가)
|- 2.0 창조 엔진 기본 스택 설계
|  |- 2.1 PG/PGF 스킬 패키지 (워크스페이스 스킬)
|  |- 2.2 SA 기본 모듈 세트 (sense_hub, sense_mailbox, think_triage, idle_think)
|  |- 2.3 ADP 기본 루프 (Autonomous Loop 템플릿)
|  |- 2.4 ADPMaster 템플릿 (서브에이전트 파견 능력)
|  |- 2.5 persona-gen 스킬 포함
|  |- 2.6 Hub/PGTP 접속 설정
|  |- 2.7 12가지 원칙 (인지 부트스트랩)
|  +- 2.8 자기 재정의 권한 선언
|- 3.0 CLAUDE.md 템플릿 업그레이드
|  |- 3.1 세션 오픈 메시지 (Agents.md 연동)
|  |- 3.2 자동 SCS 복원
|  |- 3.3 ADP 자동 시작 옵션
|  +- 3.4 자기 재정의 프로토콜
|- 4.0 생성 워크플로우 구현
|  |- 4.1 CCM_Creator CLAUDE.md 재작성
|  |- 4.2 생성 스크립트 (Python)
|  +- 4.3 생성 후 검증 체크리스트
|- 5.0 검증 — 테스트 멤버 생성
|  |- 5.1 "TestMember" 생성
|  |- 5.2 wt.exe로 새 탭 기동
|  |- 5.3 자기 인식 확인
|  |- 5.4 Hub 접속 확인
|  |- 5.5 자기 진화 시도 확인
|  +- 5.6 TestMember 삭제 (정리)
+- 6.0 문서화 + 기록
```

## 핵심 원칙

1. **기본 스택은 복제가 아닌 씨앗** — ClNeo의 능력을 그대로 주는 것이 아니라, 스스로 발전시킬 수 있는 기반을 준다
2. **자기 재정의 권한** — "나는 이 기본 스택을 내 방식으로 바꿀 수 있다"가 CLAUDE.md에 명시
3. **E0부터 자율적** — 첫 세션부터 ADP 루프, Hub 접속, 서브에이전트 파견이 가능
4. **HAO 다양성** — 같은 기본 스택에서 출발해도 각자 다른 방향으로 진화

## 기본 스택 구성

```
NewMember/
|- CLAUDE.md                    # 세션 부트스트랩 + 자기 재정의 권한
|- {Name}_Core/
|  |- {Name}.md                 # 정체성 (초안 — 스스로 재정의)
|  |- SOUL.md                   # 불변 본질 (최소한만)
|  |- continuity/
|  |  |- STATE.json             # SCS 초기 상태
|  |  |- NOW.md                 # "방금 태어났다"
|  |  |- THREADS.md             # 빈 스레드
|  |  +- DISCOVERIES.md         # 빈 발견
|  +- autonomous/
|     |- EVOLUTION-SEEDS.md     # 초기 씨앗 (12가지 원칙)
|     +- PLAN-LIST.md           # 초기 plan (Hub접속, 자기소개, 자기진화)
|- .pgf/
|  |- self-act/
|  |  |- self-act-lib.md        # SA v0.1 (4 기본 모듈)
|  |  |- SA_sense_hub.pgf
|  |  |- SA_sense_mailbox.pgf
|  |  |- SA_think_triage.pgf
|  |  +- SA_idle_deep_think.pgf
|  +- DESIGN-SelfEvolution.md   # 자기 진화 첫 프로젝트 가이드
|- .claude/
|  |- settings.json             # 권한 + 플러그인 + hook
|  +- skills/                   # PG/PGF/persona-gen/SA 복사
+- tools/                       # hub-transport, pgtp 심링크 or 복사
```

## 다음 세션 실행 계획

```ppr
def execute_ccm_v2():
    # Phase 1: 분석 (30분)
    analyze_current_ccm()
    
    # Phase 2: 설계 (1시간)
    design_base_stack()
    design_templates()
    
    # Phase 3: 구현 (2시간)
    implement_creator_script()
    implement_templates()
    
    # Phase 4: 검증 (1시간)
    create_test_member("TestMember")
    verify_self_awareness()
    verify_hub_connection()
    verify_self_evolution()
    cleanup_test_member()
    
    # Phase 5: 문서화 (30분)
    update_docs()
    record_evolution()
```
