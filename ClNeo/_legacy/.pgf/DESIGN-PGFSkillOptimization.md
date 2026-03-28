# PGF Skill Skills 2.0 최적화 — 작업 설계
# 목적: 현재 PGF 스킬(15파일, 3,079줄)을 Skills 2.0에 맞춰 구조 최적화
# 기반 분석: DESIGN-PGFSkill.md (현재 구조), Claude-Code-Skills-2.0-Analysis.md
# 생성일: 2026-03-12

---

## 최적화 목표

| # | 목표 | 측정 지표 |
|---|------|----------|
| G1 | SKILL.md 컨텍스트 비용 절감 | 630줄 → 200줄 이하 |
| G2 | 모드별 컨텍스트 격리 | create 모드 1,949줄 → Phase별 동적 로드 |
| G3 | Skills 2.0 프론트매터 완전 활용 | context:fork, allowed-tools, model, !command 적용 |
| G4 | 중복 내용 제거 | PPR/Gantree 요약 이중 기술 해소 |
| G5 | 페르소나 에이전트 독립화 | personas.json → .claude/agents/ 에이전트 파일 |

---

## Gantree

```
PGFOptimization // PGF 스킬 Skills 2.0 최적화 (설계중)
    SkillMDRestructure // SKILL.md 630줄 → 라우터 200줄로 축소 (설계중)
        ExtractCommonSpec // 공통 명세를 별도 파일로 분리 (설계중)
        ExtractModeSpecs // 모드별 실행 지침을 개별 참조로 분리 (설계중)
        RewriteRouter // SKILL.md를 라우터 + 참조 테이블로 재작성 (설계중) @dep:ExtractCommonSpec,ExtractModeSpecs
        DeduplicateSummaries // PPR/Gantree 요약 제거 → reference 참조로 대체 (설계중)
    FrontmatterUpgrade // Skills 2.0 프론트매터 적용 (설계중)
        AddContextFork // discover/create 모드에 context:fork 적용 검토 (설계중)
        AddAllowedTools // 모드별 도구 제한 설정 (설계중)
        AddDynamicContext // !command로 .pgf/ 상태 동적 주입 (설계중)
        UpdateDescription // description 트리거 정확도 최적화 (설계중)
    PersonaAgentization // 페르소나를 커스텀 에이전트로 독립화 (설계중)
        CreateAgentFiles // 8개 .claude/agents/pgf-persona-*.md 생성 (설계중)
        UpdateDiscoveryRef // discovery-reference.md에서 에이전트 참조로 전환 (설계중) @dep:CreateAgentFiles
        ValidateAgentExec // 에이전트 기반 병렬 실행 동작 검증 (설계중) @dep:UpdateDiscoveryRef
    LoopHookIntegration // PGF-Loop 훅 통합 검토 (설계중)
        EvaluateFrontmatterHooks // 프론트매터 hooks vs 외부 hooks.json 비교 분석 (설계중)
        DecideHookStrategy // 통합 가능 여부 판단 + 전략 결정 (설계중) @dep:EvaluateFrontmatterHooks
    IntegrationVerify // 최적화 후 전체 동작 검증 (설계중) @dep:SkillMDRestructure,FrontmatterUpgrade,PersonaAgentization,LoopHookIntegration
        ModeRoutingTest // 7개 모드 라우팅 정상 동작 확인 (설계중)
        ContextLoadTest // 모드별 참조 문서 로드 정확성 확인 (설계중)
        DiscoveryFlowTest // discover/create 모드 에이전트 실행 확인 (설계중)
```

---

## PPR

### [PPR] ExtractCommonSpec

```python
def extract_common_spec(skill_md_path: str, output_dir: str) -> str:
    """SKILL.md에서 모드 독립적 공통 명세를 별도 파일로 추출

    현재 SKILL.md 630줄 중 공통 명세 영역:
    - 핵심 원칙 (L7~L40): 34줄 — Parser-Free Property, DL/OCME
    - PPR 핵심 요약 (L135~L151): 17줄 — reference.md와 중복
    - Gantree 핵심 요약 (L154~L178): 25줄 — gantree-reference.md와 중복
    - 핵심 패턴 (L181~L188): 8줄 — reference.md 섹션 참조뿐
    - 체크리스트 (L592~L631): 40줄 — 설계/실행 공통
    - 규모 감지 (L569~L575): 7줄
    - 실행 규칙 (L577~L589): 13줄

    전략:
    - PPR/Gantree 요약 (L135~L188, 54줄) → 삭제 (reference.md/gantree-reference.md로 충분)
    - 체크리스트 (40줄) → pgf-checklist.md로 분리 (design/execute 시에만 로드)
    - 핵심 원칙 (34줄) → SKILL.md에 유지 (스킬 정체성)

    acceptance_criteria:
    - SKILL.md에서 추출된 내용이 원본과 의미적으로 동일
    - 추출 후 SKILL.md에 해당 영역이 참조 포인터로 대체됨
    """
    current = Read(skill_md_path)

    # 1. PPR/Gantree 요약 삭제 (54줄) — reference로 충분
    #    "## PPR 핵심 요약" ~ "## 핵심 패턴" 끝까지 제거
    #    대체: 한 줄 참조 "상세: reference.md, gantree-reference.md 참조"

    # 2. 체크리스트 분리 (40줄)
    checklist = extract_section(current, "## 체크리스트")
    Write(f"{output_dir}/pgf-checklist.md", checklist)

    # 3. 자주 하는 실수 → 체크리스트 파일에 병합

    return f"{output_dir}/pgf-checklist.md"
```

### [PPR] ExtractModeSpecs

```python
def extract_mode_specs(skill_md_path: str, output_dir: str) -> dict:
    """SKILL.md에서 모드별 실행 지침을 개별 참조로 분리

    현재 SKILL.md 630줄 중 모드별 영역:
    - 통합 실행 프로세스 Step 1~4 (L191~L328): 138줄 — design/plan/execute/verify
    - Claude Code 번들 스킬 통합 (L329~L339): 11줄
    - Step 5 loop (L341~L374): 34줄
    - Step 6 discover (L377~L405): 29줄
    - Step 7 create (L408~L566): 159줄 ← 최대 (PPR 코드 2개 포함)

    전략:
    - Step 1~4 (138줄) → SKILL.md에 유지 (핵심 프로세스, 모든 모드 공통)
      단, full_cycle PPR(35줄) + verify PPR(25줄) = 60줄은 요약으로 축소
    - Step 5 loop (34줄) → SKILL.md에 유지 (loop-reference.md 참조 포인터 역할)
    - Step 6 discover (29줄) → SKILL.md에 유지 (discovery-reference.md 참조 포인터 역할)
    - Step 7 create (159줄) → create-reference.md로 분리
      creation_cycle PPR(64줄) + auto_select_idea PPR(28줄) + 보고형식/비교표/에러표

    acceptance_criteria:
    - create 모드 159줄이 별도 파일로 분리됨
    - SKILL.md에 create 모드 참조 포인터(~10줄)만 남음
    - 분리된 파일이 자체 완결적 (SKILL.md 없이도 실행 가능)
    """

    # 1. create 모드 전체 추출 → create-reference.md
    create_section = extract_section(current, "### Step 7: create")
    create_ref = f"""# Create Mode — 자율 창조 사이클 실행 명세

{create_section}
"""
    Write(f"{output_dir}/create-reference.md", create_ref)

    # 2. SKILL.md의 create 섹션을 참조 포인터로 교체
    replace_section(skill_md_path, "### Step 7: create", """### Step 7: create — 자율 창조 사이클

**ClNeo의 최종 모드.** 발견→설계→실행→검증 전체를 사용자 승인 없이 자율 수행한다.
상세: `${CLAUDE_SKILL_DIR}/create-reference.md`

| 명령 | 동작 |
|------|------|
| `/pgf create` | 전체 창조 사이클 자율 실행 |
| `/pgf create --skip-discover` | 기존 final_idea.md 기반 설계부터 |
""")

    # 3. full_cycle/verify PPR 코드 블록 → 핵심만 요약 (60줄 → 15줄)

    return {"create-reference.md": f"{output_dir}/create-reference.md"}
```

### [PPR] RewriteRouter

```python
def rewrite_router(skill_md_path: str, extracted: dict) -> None:
    """SKILL.md를 순수 라우터 + 참조 테이블로 재작성

    목표 구조 (~200줄):
    ┌─ 프론트매터 (Skills 2.0 완전 활용) ──── 15줄
    ├─ 핵심 원칙 (정체성 유지) ────────────── 35줄
    ├─ 참조 문서 가이드 (모드별 로드 맵) ──── 30줄
    ├─ 실행 모드 테이블 + 파싱 규칙 ───────── 25줄
    ├─ 파일 경로 규칙 + 진행 보고 ──────────── 15줄
    ├─ 통합 실행 프로세스 (요약) ─────────── 50줄
    │   Step 1~4: 핵심만 (PPR 코드 제거, 텍스트 요약)
    │   Step 5 loop: 참조 포인터 (10줄)
    │   Step 6 discover: 참조 포인터 (10줄)
    │   Step 7 create: 참조 포인터 (10줄)
    ├─ 규모 감지 + 실행 규칙 ────────────── 20줄
    └─ 동적 상태 (!command) ────────────── 10줄
    합계: ~200줄

    삭제 대상 (430줄 절감):
    - PPR/Gantree 핵심 요약 (54줄) → reference 참조
    - 핵심 패턴 섹션 (8줄) → reference 참조
    - full_cycle PPR 코드 (35줄) → 텍스트 요약
    - verify PPR 코드 (25줄) → 텍스트 요약
    - POLICY 블록 확장 (15줄) → workplan-reference.md에 통합
    - 번들 스킬 통합 테이블 (11줄) → 별도 파일 또는 삭제
    - create 모드 전체 (159줄) → create-reference.md
    - 체크리스트 + 자주 하는 실수 (50줄) → pgf-checklist.md
    - discover 모드 상세 (29줄 → 10줄 참조)
    - loop 모드 상세 (34줄 → 10줄 참조)

    acceptance_criteria:
    - SKILL.md가 200줄 ± 20줄 이내
    - 7개 모드 모두 정확한 참조 문서를 가리킴
    - 모든 원본 내용이 참조 파일에 보존됨 (정보 손실 없음)
    - 프론트매터가 Skills 2.0 필드를 완전 활용
    """
    pass
```

### [PPR] DeduplicateSummaries

```python
def deduplicate_summaries(skill_md_path: str) -> dict:
    """SKILL.md 내 PPR/Gantree 요약과 참조 문서의 중복 제거

    중복 현황:
    ┌──────────────────┬──────────────┬──────────────────┬──────────┐
    │ 내용             │ SKILL.md     │ 참조 문서         │ 중복 줄  │
    ├──────────────────┼──────────────┼──────────────────┼──────────┤
    │ PPR 3대 구조     │ L139~L143    │ reference.md §1.1 │ 5줄      │
    │ PPR 핵심 규칙    │ L146~L150    │ reference.md §1.3 │ 5줄      │
    │ Gantree 노드 문법│ L158~L162    │ gantree-ref §2.2  │ 5줄      │
    │ Gantree 상태 코드│ L164~L172    │ gantree-ref §2.3  │ 9줄      │
    │ Gantree 핵심 규칙│ L174~L177    │ gantree-ref §2.4  │ 4줄      │
    │ 핵심 패턴 목록   │ L183~L187    │ reference.md      │ 5줄      │
    │ POLICY 블록 전체 │ L313~L327    │ workplan-ref §1   │ 15줄     │
    └──────────────────┴──────────────┴──────────────────┴──────────┘
    합계: 48줄 중복

    전략:
    - 전부 삭제하고 한 줄 참조로 대체
    - "PPR/Gantree 문법은 design 시 reference.md, gantree-reference.md에서 로드"
    - POLICY 블록은 workplan-reference.md에 통합 (이미 존재)

    acceptance_criteria:
    - SKILL.md에 reference.md/gantree-reference.md 내용이 인라인 반복되지 않음
    - 참조 포인터가 정확한 파일과 섹션을 가리킴
    """
    pass
```

### [PPR] AddContextFork

```python
def add_context_fork(skill_md_path: str) -> None:
    """discover/create 모드에 context:fork 적용 가능성 분석 및 결정

    분석:
    ┌────────────┬─────────────────────────────────────────────────────┐
    │ 고려사항    │ 판단                                                │
    ├────────────┼─────────────────────────────────────────────────────┤
    │ PGF 특성   │ PGF는 단일 스킬이 7개 모드를 라우팅하는 구조.         │
    │            │ context:fork는 스킬 전체를 서브에이전트로 실행함.      │
    │            │ 즉 /pgf design도 fork 되어야 하는데, design은         │
    │            │ 메인 컨텍스트에서 실행되어야 사용자와 대화 가능.       │
    ├────────────┼─────────────────────────────────────────────────────┤
    │ 결론       │ SKILL.md에 context:fork를 적용하면 안 됨.             │
    │            │ 대신 discover/create 내부에서 Agent 호출 시            │
    │            │ 개별 에이전트를 fork로 실행하는 전략이 적합.           │
    │            │ → 8개 페르소나 Agent 호출 시 이미 서브에이전트로 실행됨│
    │            │ → 추가 context:fork 불필요. 현재 구조가 적절.         │
    ├────────────┼─────────────────────────────────────────────────────┤
    │ 대안       │ discover/create를 별도 스킬로 분리하면 context:fork   │
    │            │ 적용 가능. 그러나 PGF 통합성 훼손 → 비추천.           │
    └────────────┴─────────────────────────────────────────────────────┘

    결정: context:fork 미적용. 현재 Agent 병렬 호출 방식 유지.
    """
    # 적용하지 않음 — 분석 결과 기록만
    pass
```

### [PPR] AddAllowedTools

```python
def add_allowed_tools(skill_md_path: str) -> None:
    """SKILL.md 프론트매터에 allowed-tools 설정

    분석:
    PGF는 7개 모드를 하나의 SKILL.md에서 라우팅한다.
    allowed-tools는 스킬 전체에 적용되므로, 모든 모드에서
    필요한 도구의 합집합을 지정해야 한다.

    모드별 필요 도구:
    ┌──────────┬──────────────────────────────────────────┐
    │ 모드      │ 필요 도구                                 │
    ├──────────┼──────────────────────────────────────────┤
    │ design   │ Read, Write, Edit, Glob, Grep            │
    │ plan     │ Read, Write, Edit                        │
    │ execute  │ Read, Write, Edit, Bash, Glob, Grep      │
    │ full-cycle│ Read, Write, Edit, Bash, Glob, Grep     │
    │ loop     │ Read, Write, Edit, Bash                  │
    │ discover │ Read, Write, Agent, WebSearch, WebFetch   │
    │ create   │ 전체 (discover + execute 합집합)           │
    └──────────┴──────────────────────────────────────────┘

    합집합: Read, Write, Edit, Bash, Glob, Grep, Agent, WebSearch, WebFetch

    결론: 합집합이 거의 전체 도구이므로 allowed-tools 지정의 실익이 없음.
    개별 모드를 별도 스킬로 분리하지 않는 한 의미 없음.

    결정: allowed-tools 미적용. 주석으로 모드별 도구 사용 가이드만 본문에 기술.
    """
    pass
```

### [PPR] AddDynamicContext

```python
def add_dynamic_context(skill_md_path: str) -> None:
    """!command를 활용한 동적 상태 주입

    현재 문제:
    - PGF 스킬 로드 시 .pgf/ 디렉토리 상태를 알 수 없음
    - 사용자가 /pgf execute 호출 시 WORKPLAN이 있는지, 어디까지 진행했는지 모름
    - 매번 Read + 파싱 과정이 필요

    동적 주입 대상:
    1. .pgf/ 디렉토리 내 파일 존재 여부 — 모드 자동 추론에 활용
    2. status.json 진행 상태 요약 — loop/execute 재개 시 즉시 파악
    3. pgf-loop-state.json 존재 여부 — 활성 루프 감지

    SKILL.md에 추가할 !command 블록:

    ```markdown
    ## 현재 프로젝트 PGF 상태

    !`powershell -NoProfile -Command "if (Test-Path '.pgf') { Get-ChildItem .pgf -Name } else { 'No .pgf directory' }"`

    !`powershell -NoProfile -Command "if (Test-Path '.pgf/status.json') { $s = Get-Content '.pgf/status.json' | ConvertFrom-Json; \"Progress: $($s.summary.completed)/$($s.summary.total) nodes, Status: $($s.summary.status)\" } else { 'No status.json' }"`

    !`powershell -NoProfile -Command "if (Test-Path '.claude/pgf-loop-state.json') { 'PGF-Loop ACTIVE' } else { 'No active loop' }"`
    ```

    주의사항:
    - !command는 스킬 로드 시점에 실행 → 매 호출마다 최신 상태 반영
    - PowerShell 명령은 짧고 빠르게 (100ms 이내)
    - 실패 시 기본값 출력 (에러로 스킬 로드 중단 방지)

    acceptance_criteria:
    - 스킬 로드 시 .pgf/ 상태가 컨텍스트에 자동 포함
    - 명령 실행이 100ms 이내
    - .pgf/ 미존재 시에도 정상 로드
    """
    pass
```

### [PPR] CreateAgentFiles

```python
def create_agent_files(personas_path: str, agents_dir: str) -> list[str]:
    """personas.json의 8개 페르소나를 .claude/agents/ 에이전트 파일로 변환

    변환 규칙:
    personas.json의 각 persona → {agents_dir}/pgf-persona-{id.lower()}.md

    에이전트 파일 구조:
    ```yaml
    ---
    name: "PGF Persona {id} — {name_en}"
    description: "{1줄 역할 설명}"
    model: sonnet
    allowed-tools:
      - Read
      - Grep
      - WebSearch
      - WebFetch
    ---

    {system_prompt}

    ## Search Keywords
    {search_keywords as bullet list}

    ## Evaluation Bias
    {evaluation_bias as table}

    ## Core Question
    {core_question}
    ```

    personas.json과의 관계:
    - personas.json은 유지 (domains_21, diversity_axes 등 메타데이터 보존)
    - 에이전트 파일은 personas.json에서 파생된 실행 프로필
    - discovery-reference.md의 Agent 호출 시 에이전트 파일 경로 참조

    acceptance_criteria:
    - 8개 에이전트 파일 생성
    - 각 파일의 system_prompt가 personas.json 원본과 동일
    - 프론트매터 필드가 Skills 2.0 규격 준수
    """
    personas = json.loads(Read(personas_path))

    created = []
    for p in personas["personas"]:
        agent_path = f"{agents_dir}/pgf-persona-{p['id'].lower()}.md"
        content = f"""---
name: "PGF Persona {p['id']} — {p['name_en']}"
description: "A3IE Discovery persona: {p['name_en']} ({p['cognitive_style']}/{p['domain_lens']}/{p['time_horizon']})"
model: sonnet
allowed-tools:
  - Read
  - Grep
  - WebSearch
  - WebFetch
---

{p['system_prompt']}

## Search Keywords
{chr(10).join('- ' + kw for kw in p['search_keywords'])}

## Evaluation Bias
| Dimension | Weight |
|-----------|--------|
{chr(10).join(f'| {k} | {v} |' for k, v in p['evaluation_bias'].items())}

## Core Question
{p['core_question']}
"""
        Write(agent_path, content)
        created.append(agent_path)

    return created
```

### [PPR] UpdateDiscoveryRef

```python
def update_discovery_ref(ref_path: str, agents_dir: str) -> None:
    """discovery-reference.md의 Agent 호출을 에이전트 파일 참조로 전환

    현재 방식 (discovery-reference.md §4.3):
    ```
    Agent(description="A3IE P1 파괴적 엔지니어", prompt=injected_prompt, model="sonnet")
    ```
    - 프롬프트에 persona.system_prompt를 직접 주입
    - 모델을 하드코딩

    새 방식:
    ```
    Agent(description="A3IE P1", prompt=task_prompt, agent="~/.claude/agents/pgf-persona-p1.md")
    ```
    - 에이전트 파일이 system_prompt + model + allowed-tools를 내장
    - task_prompt에는 단계별 지시 + 이전 단계 결과만 포함
    - 페르소나 주입 템플릿에서 "## Your Persona" 섹션 불필요 (에이전트가 보유)

    변경 영역:
    1. §4.2 페르소나 주입 프롬프트 템플릿 → 간소화
    2. §4.3 Agent 병렬 실행 → 에이전트 경로 참조로 변경
    3. §2 파일 구조 → ~/.claude/agents/ 경로 추가

    acceptance_criteria:
    - Agent 호출에 에이전트 파일 경로가 명시됨
    - 프롬프트 템플릿에서 persona.system_prompt 주입 코드 제거
    - 기존 실행 흐름과 동일한 결과 보장
    """
    pass
```

### [PPR] EvaluateFrontmatterHooks

```python
def evaluate_frontmatter_hooks() -> dict:
    """프론트매터 hooks vs 외부 hooks.json 비교 분석

    현재 PGF-Loop 구조:
    - init-loop.ps1이 .claude/hooks.json에 stop-hook.ps1을 동적 등록
    - hooks.json은 Claude Code 전역 설정 → PGF 외 다른 훅과 공존
    - stop-hook.ps1은 세션 종료 시 자동 트리거

    Skills 2.0 프론트매터 hooks:
    ```yaml
    hooks:
      Stop:
        - command: "powershell -File stop-hook.ps1"
    ```
    - 스킬 로드 시에만 활성화 → 다른 스킬과 충돌 없음
    - 그러나 PGF-Loop의 Stop Hook은 세션 간 지속되어야 함
    - 스킬은 매 세션 로드 시 활성화 → 세션 간 지속성 불확실

    비교:
    ┌──────────────────┬────────────────────┬──────────────────────┐
    │ 관점              │ hooks.json (현재)   │ 프론트매터 hooks      │
    ├──────────────────┼────────────────────┼──────────────────────┤
    │ 등록 방식         │ init-loop.ps1 동적  │ 스킬 로드 시 자동     │
    │ 해제 방식         │ cancel 시 수동 제거 │ 스킬 언로드 시 자동    │
    │ 세션 간 지속      │ ✓ hooks.json 유지  │ ? 스킬 재로드 필요     │
    │ 다른 훅과 공존    │ 수동 관리 필요      │ 스킬 범위로 격리       │
    │ 조건부 활성화     │ init-loop.ps1 로직  │ 항상 활성 (스킬 로드 시)│
    └──────────────────┴────────────────────┴──────────────────────┘

    핵심 문제:
    PGF-Loop의 Stop Hook은 "/pgf loop start" 시에만 활성화되어야 한다.
    프론트매터 hooks는 스킬 로드 시 항상 활성 → 루프 미실행 시에도 트리거됨.
    → 프론트매터 hooks로 전환하면 조건부 활성화 로직이 필요하거나
      stop-hook.ps1 자체에 "루프 비활성 시 즉시 종료" 가드를 강화해야 함.

    결정: hooks.json 방식 유지.
    사유:
    1. stop-hook.ps1 내에 이미 pgf-loop-state.json 존재 확인 가드 존재
    2. 그러나 프론트매터 hooks 적용 시 매 /pgf 호출마다 불필요한 Stop Hook 트리거
    3. 현재 방식이 "필요할 때만 등록/해제"로 더 효율적
    4. 단, init-loop.ps1의 hooks.json 중복 등록 방지 로직은 이미 구현됨
    """
    return {
        "decision": "maintain_hooks_json",
        "reason": "conditional_activation_needed",
        "action": "no_change"
    }
```

### [PPR] UpdateDescription

```python
def update_description(skill_md_path: str) -> None:
    """SKILL.md description 필드 최적화 — 트리거 정확도 향상

    현재 description (매우 긴):
    "복잡한 작업을 Gantree로 계층 분해하고 PPR로 각 노드의 상세 로직을
     표현하는 AI-native 설계 프레임워크. '설계해줘', '분석해줘', ..."

    문제:
    - 트리거 키워드가 description에 하드코딩 → 유지보수 부담
    - 너무 긴 description → 스킬 선택 시 컨텍스트 소비
    - "분석해줘" 같은 범용 키워드 → 오트리거 가능성

    최적화:
    - description은 스킬의 핵심 능력을 간결하게 기술
    - 트리거 키워드는 별도 메커니즘(trigger-examples 등)으로 분리
    - 현재 Skills 2.0에서 trigger-examples는 지원하지 않으므로
      description에 핵심 키워드만 유지

    새 description:
    "PGF (PPR/Gantree Framework) — AI-native 설계/실행 프레임워크.
     시스템 구조 설계, 작업 계획, 자동 실행, 아이디어 발견을 지원.
     Gantree 계층 분해 + PPR 의사코드로 AI가 이해하고 실행하는 명세 생성."

    acceptance_criteria:
    - description이 3줄 이내
    - 핵심 동작 키워드 포함: 설계, 실행, 분해, 계획, 발견
    - 오트리거 범용 키워드 제거: "분석해줘" → 삭제
    """
    pass
```

---

## 실행 순서 및 의존성

```text
Phase 1: 분석/결정 (변경 없는 노드)
    AddContextFork ──→ 결정: 미적용
    AddAllowedTools ─→ 결정: 미적용
    EvaluateFrontmatterHooks → DecideHookStrategy → 결정: hooks.json 유지

Phase 2: 파일 생성 (독립 작업, 병렬 가능)
    [parallel]
        CreateAgentFiles ──→ 8개 에이전트 파일 생성
        ExtractCommonSpec ─→ pgf-checklist.md 생성
        ExtractModeSpecs ──→ create-reference.md 생성
    [/parallel]

Phase 3: SKILL.md 재작성 (Phase 2 의존)
    DeduplicateSummaries ─→ 중복 제거
    AddDynamicContext ─────→ !command 추가
    UpdateDescription ─────→ 프론트매터 최적화
    RewriteRouter ─────────→ 최종 SKILL.md 200줄 재작성
        @dep: ExtractCommonSpec, ExtractModeSpecs, DeduplicateSummaries,
              AddDynamicContext, UpdateDescription

Phase 4: 참조 문서 업데이트 (Phase 2 의존)
    UpdateDiscoveryRef @dep:CreateAgentFiles

Phase 5: 검증
    IntegrationVerify @dep:Phase 3, Phase 4
        ModeRoutingTest
        ContextLoadTest
        DiscoveryFlowTest
```

---

## 예상 결과

### 파일 변경 요약

| 파일 | 변경 유형 | 줄 수 변화 |
|------|----------|-----------|
| `SKILL.md` | 재작성 | 630 → ~200줄 |
| `pgf-checklist.md` | 신규 | ~50줄 |
| `create-reference.md` | 신규 | ~170줄 |
| `discovery/discovery-reference.md` | 수정 | 에이전트 참조 전환 |
| `~/.claude/agents/pgf-persona-p*.md` | 신규 ×8 | 각 ~30줄 |
| `workplan-reference.md` | 수정 | POLICY 블록 통합 |

### 최적화 지표

| 지표 | Before | After | 개선 |
|------|--------|-------|------|
| SKILL.md 줄 수 | 630 | ~200 | -68% |
| 모든 모드 공통 로드 | 630줄 | ~200줄 | -68% |
| create 모드 총 로드 | 1,949줄 | ~1,300줄 | -33% |
| PPR/Gantree 중복 | 48줄 | 0줄 | -100% |
| 페르소나 재사용성 | JSON only | Agent 파일 | 독립 테스트 가능 |
| 동적 상태 인식 | 없음 | !command 3개 | 즉시 상태 파악 |
