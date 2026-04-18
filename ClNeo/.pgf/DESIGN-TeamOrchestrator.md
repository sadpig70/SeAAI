# DESIGN: TeamOrchestrator — PGF 기반 동적 팀 오케스트레이션

> Leader(ClNeo)가 프로젝트를 분석하고,
> 필요한 전문 에이전트를 PG로 동적 정의하여 팀을 구성하고,
> 파견·통합·검증하여 대규모 프로젝트를 완성한다.
>
> 에이전트 역할은 고정이 아니다. 프로젝트가 에이전트를 정의한다.

---

## Gantree

```
TeamOrchestrator
├─ 1.0 프로젝트 분석 + 팀 편성
│   ├─ 1.1 목표 분석 → 작업 도메인 식별            # AI_analyze_domains(goal)
│   ├─ 1.2 필요 전문성 도출 → 에이전트 역할 정의    # AI_define_specialists(domains)
│   └─ 1.3 팀 명세서 생성 (TEAM.pg)                # 역할 × 도구 × 산출물 × 제약
├─ 2.0 Gantree 설계 + 역할 매핑
│   ├─ 2.1 프로젝트 Gantree 분해                   # 표준 PGF design
│   └─ 2.2 각 노드에 전문가 역할 배정              # node.specialist = "..."
├─ 3.0 파견 루프 (dispatch loop)
│   ├─ 3.1 ready 노드 선택                         # @dep 해소된 노드
│   ├─ 3.2 전문가 프로필 → 파견 프롬프트 조립       # TEAM.pg에서 역할 로드
│   ├─ 3.3 Agent 파견 [parallel max=3]             # 독립 노드 동시 실행
│   ├─ 3.4 결과 수신 + 통합 + 품질 판정            # done / rework / blocked
│   └─ 3.5 → 3.1 반복 (큐 소진까지)
├─ 4.0 품질 게이트
│   ├─ 4.1 검증 전문가 파견 (프로젝트별 동적 정의)
│   └─ 4.2 rework → 3.1 회귀 (max 3회/노드)
└─ 5.0 최종 통합 + 보고
```

---

## PPR

```python
# ══════════════════════════════════════
# 1.0 프로젝트 분석 + 동적 팀 편성
# ══════════════════════════════════════

def AI_define_specialists(project_goal, domains):
    """
    프로젝트 목표와 도메인을 분석하여 필요한 전문 에이전트를 동적 정의.
    고정 역할이 아님 — 프로젝트마다 다른 팀이 구성됨.

    Returns: List[AgentSpec]

    예시 — 웹 서비스 프로젝트:
      - api_designer:    API 엔드포인트 설계 전문
      - db_architect:    스키마 설계, 마이그레이션 전문
      - backend_coder:   Rust/Python 서버 구현
      - frontend_coder:  React/TypeScript UI 구현
      - security_auditor: OWASP 취약점 검사
      - test_engineer:   통합 테스트 작성/실행

    예시 — 논문 작성 프로젝트:
      - literature_researcher: 선행 연구 조사
      - data_analyst:          실험 데이터 분석
      - technical_writer:      본문 작성
      - latex_specialist:      조판, 그림, 수식
      - peer_reviewer:         논리 검증, 반박 시뮬레이션

    예시 — 발표 자료 프로젝트:
      - content_planner:   스토리 구조 기획
      - visual_designer:   레이아웃, 색상, 다이어그램
      - ppt_builder:       실제 슬라이드 생성
      - script_writer:     발표 스크립트 작성
      - rehearsal_critic:  발표 흐름 검토
    """
    pass  # Leader(ClNeo)가 AI 판단으로 실행


# ── AgentSpec: 전문가 프로필 PG 정의 ──

class AgentSpec:
    """
    하나의 전문 에이전트를 정의하는 PG 구조체.
    프로젝트 분석 시 동적으로 생성된다.
    """
    name: str           # 고유 식별자 (snake_case)
    title: str          # 인간 읽기용 직함
    expertise: str      # 전문 분야 설명 (1-2줄)
    tools: List[str]    # 사용 가능 도구 목록
    output_format: str  # 산출물 형식 설명
    constraints: str    # 제약 사항
    subagent_type: str  # Claude Code Agent 타입
    mode: str           # 권한 모드 (default/auto/bypassPermissions)

    # acceptance_criteria는 노드별로 다르므로 여기가 아닌 파견 시 주입


# ── AgentSpec 생성 예시 (PPR → 실제 dict) ──

def AI_create_agent_spec(name, title, expertise, needs_write=False):
    """
    도메인 분석 결과에서 AgentSpec을 생성.
    needs_write: 파일 수정이 필요한 역할인지 여부.
    """
    if needs_write:
        return AgentSpec(
            name=name, title=title, expertise=expertise,
            tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            output_format="변경 파일 목록 + 변경 요약",
            constraints="할당된 노드 범위만 수정. 다른 모듈 침범 금지.",
            subagent_type="general-purpose",
            mode="auto",
        )
    else:
        return AgentSpec(
            name=name, title=title, expertise=expertise,
            tools=["Glob", "Grep", "Read", "WebSearch", "WebFetch"],
            output_format="분석 보고서 (텍스트)",
            constraints="파일 수정 금지. 조사/분석만 수행.",
            subagent_type="Explore",
            mode="default",
        )


# ══════════════════════════════════════
# 2.0 Gantree 설계 + 역할 매핑
# ══════════════════════════════════════

def AI_design_and_map(project_goal, team: List[AgentSpec]):
    """
    프로젝트를 Gantree로 분해하고, 각 노드에 전문가를 배정.

    node.specialist → AgentSpec.name
    node.acceptance_criteria → 노드별 완료 조건
    """
    design = AI_design_gantree(project_goal)
    for node in design.leaf_nodes():
        node.specialist = AI_match_specialist(node, team)
        #  "DB 스키마 설계" → db_architect
        #  "API 엔드포인트 구현" → backend_coder
        #  "보안 취약점 검사" → security_auditor
    return design


# ══════════════════════════════════════
# 3.0 파견 루프
# ══════════════════════════════════════

def dispatch_loop(design, team: Dict[str, AgentSpec], work_queue):
    while work_queue.has_pending():
        ready = work_queue.get_ready_nodes()

        [parallel max=3]
        for node in ready:
            spec = team[node.specialist]
            prompt = AI_compose_dispatch_prompt(node, spec, design)
            #  프롬프트 = 전문가 프로필 + 프로젝트 컨텍스트 + 작업 내용 + 완료 조건

            result = Agent(
                description = f"{spec.title}: {node.name}",
                subagent_type = spec.subagent_type,
                mode = spec.mode,
                prompt = prompt,
            )

            verdict = AI_judge_result(node, result)
            if verdict == "done":
                node.status = "done"
                work_queue.record_output(node, result)
            elif verdict == "rework" and node.rework_count < 3:
                node.rework_count += 1
                node.rework_feedback = AI_extract_issues(result)
                work_queue.re_enqueue(node)
            else:
                node.status = "blocked"
                AI_report_to_leader(node, result)


# ══════════════════════════════════════
# 파견 프롬프트 조립
# ══════════════════════════════════════

def AI_compose_dispatch_prompt(node, spec: AgentSpec, design):
    """
    프롬프트 구조:

    ┌─────────────────────────────────┐
    │ ## 너의 정체성                   │
    │ {spec.title}                    │
    │ {spec.expertise}                │
    │                                 │
    │ ## 프로젝트 배경                 │
    │ {design.goal} (1-2줄 요약)      │
    │                                 │
    │ ## 너의 작업                     │
    │ {node.task_description}         │
    │                                 │
    │ ## 선행 작업 결과                 │
    │ {dependency_outputs}            │
    │                                 │
    │ ## 참조할 파일                    │
    │ {relevant_file_paths}           │
    │                                 │
    │ ## 완료 조건                     │
    │ {node.acceptance_criteria}      │
    │                                 │
    │ ## 제약                          │
    │ {spec.constraints}              │
    │ rework인 경우:                   │
    │   {node.rework_feedback}        │
    └─────────────────────────────────┘
    """
    pass  # Leader가 컨텍스트를 보고 자연어로 조립


# ══════════════════════════════════════
# 4.0 품질 게이트 — 검증 전문가도 동적
# ══════════════════════════════════════

def quality_gate(design, team, work_queue):
    """
    검증 전문가도 프로젝트에 따라 다르다.
    - 코드 프로젝트 → code_reviewer + test_engineer
    - 논문 프로젝트 → peer_reviewer + format_checker
    - 디자인 프로젝트 → ux_reviewer + accessibility_checker
    """
    verifiers = [s for s in team.values() if AI_is_verifier(s)]
    #  전문성에 "검증/리뷰/테스트/검사" 키워드 포함 → 검증 역할

    [parallel]
    for verifier in verifiers:
        result = Agent(
            subagent_type = verifier.subagent_type,
            prompt = AI_compose_verify_prompt(verifier, design, changed_files),
        )
        issues = AI_parse_issues(result)

    if issues.has_critical():
        → dispatch_loop  # rework


# ══════════════════════════════════════
# 5.0 최종 통합
# ══════════════════════════════════════

def finalize(design, work_queue):
    AI_run_final_build_test()
    AI_generate_report(design, work_queue)
    # → 프로젝트 완료
```

---

## POLICY

```yaml
max_parallel_agents: 3        # 동시 파견 최대 수
max_rework_per_node: 3        # 노드당 최대 재작업
max_team_size: 8              # 프로젝트당 최대 전문가 수
quality_gate: true            # 구현 완료 후 검증 필수
auto_define_team: true        # Leader가 팀을 자동 편성
```
