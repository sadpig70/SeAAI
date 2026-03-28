# PGF-Loop Engine Design @v:1.0

> Ralph-Loop 플러그인 없이 Claude Code Stop Hook 플랫폼만으로
> PGF WORKPLAN 노드를 자동 순회·실행하는 자체 루프 엔진

## 설계 배경

### 벤치마크 대상: Ralph-Loop의 핵심 메커니즘

```
[Ralph-Loop 3-Layer Architecture]

Layer 1: Stop Hook (Claude Code 플랫폼)
  └─ 세션 종료 시도 시 hooks.json → 셸 스크립트 실행
  └─ 반환값: { "decision": "block", "reason": "프롬프트" }

Layer 2: 상태 파일 (.claude/ralph-loop.local.md)
  └─ YAML frontmatter: iteration, max_iterations, session_id, completion_promise

Layer 3: 프롬프트 재주입
  └─ stop-hook이 "reason" 필드에 동일 프롬프트를 넣어 다음 턴 강제 시작
```

### Ralph-Loop의 한계와 PGF-Loop의 차별점

| Ralph-Loop | PGF-Loop (본 설계) |
|---|---|
| 매 iteration 동일 프롬프트 | 매 iteration **다른 노드의 PPR def** 주입 |
| iteration 카운터만 추적 | status.json **노드 그래프** 추적 |
| 작업 선택 없음 (Claude에 위임) | stop-hook이 **select_next_node()** 직접 수행 |
| completion_promise 문자열 비교 | **all_nodes_terminal()** 구조적 판정 |
| 에러 시 상태 파일 삭제 | **Failure Strategy + retry/skip 정책** |

### 기술 결정

1. **bash + jq**: stop-hook.sh에서 status.json 파싱 및 노드 선택
2. **sed/grep**: WORKPLAN-{Name}.md에서 노드 상태 추출, DESIGN-{Name}.md에서 PPR def 추출
3. **Claude Code hooks 프로토콜**: `{ "decision", "reason", "systemMessage" }` JSON 반환
4. **Git Bash 호환**: Windows 환경에서 bash 스크립트 실행 (Claude Code가 이미 Git Bash 사용)

---

## Gantree

```
PgfLoopEngine // PGF 자체 실행 루프 엔진 (설계중) @v:1.0
    HookInfra // Stop Hook 인프라 구성 (설계중)
        HooksJson // hooks.json 설정 파일 생성 (설계중)
        StopHookEntry // stop-hook.sh 진입점 및 분기 (설계중)
    StateManager // 실행 상태 관리 (설계중)
        StatusReader // status.json 읽기 및 파싱 (설계중)
        StatusWriter // status.json 갱신 (설계중)
        SessionGuard // 세션 격리 검증 (설계중)
    NodeSelector // 다음 실행 노드 선택 (설계중)
        DependencyResolver // @dep: 의존성 해소 판정 (설계중)
        ParallelDetector // [parallel] 블록 감지 (설계중)
        PriorityPicker // 후보 중 우선순위 선택 (설계중)
    PromptBuilder // 동적 프롬프트 구성 (설계중)
        PprExtractor // DESIGN-{Name}.md에서 PPR def 블록 추출 (설계중)
        ContextAssembler // 시스템 메시지 + 노드 프롬프트 조립 (설계중)
    LoopController // 루프 제어 및 종료 판정 (설계중)
        TerminalChecker // 전체 노드 종료 조건 판정 (설계중)
        IterationGuard // 최대 반복 횟수 제한 (설계중)
    ErrorHandler // 에러 복구 및 정책 적용 (설계중)
        RetryPolicy // 재시도 정책 (설계중)
        BlockerRecorder // 블로커 문서화 (설계중)
        StateRecovery // 손상된 상태 복구 (설계중)
    InitCommand // 루프 시작 명령어 (설계중)
        ArgParser // 인수 파싱 (workplan, design, max-iterations) (설계중)
        StateInitializer // 초기 상태 파일 생성 (설계중)
    CancelCommand // 루프 취소 명령어 (설계중)
```

---

## PPR

### 전체 실행 흐름

```python
def pgf_loop_engine_flow():
    """PGF-Loop 전체 실행 흐름 — 시스템 수준 오케스트레이션"""

    # ═══ Phase 1: 초기화 (InitCommand) ═══
    # 사용자가 루프 시작 명령을 실행
    # → .claude/pgf-loop-state.json 생성
    # → 첫 번째 노드 프롬프트로 Claude 작업 시작

    # ═══ Phase 2: 실행 루프 (매 iteration) ═══
    #
    # Claude가 현재 노드 작업 완료 → 세션 종료 시도
    #     ↓
    # Stop Hook 가로챔 (stop-hook.sh)
    #     ↓
    # SessionGuard: 세션 ID 검증
    #     ↓
    # StatusReader: status.json 로드
    #     ↓
    # NodeSelector: 다음 실행 가능 노드 선택
    #     ├─ 노드 있음 → PromptBuilder → 프롬프트 구성 → "block" 반환
    #     └─ 노드 없음 → TerminalChecker → 종료 판정 → 정상 종료
    #
    # ═══ Phase 3: 종료 ═══
    # 전체 노드 terminal → 상태 파일 정리 → 세션 정상 종료
```

---

### [PPR] HooksJson — hooks.json 설정 파일

```python
def hooks_json() -> dict:
    """Claude Code hooks.json 구성 — Stop 이벤트에 stop-hook.sh 등록"""
    # acceptance_criteria:
    #   - hooks.json이 프로젝트 .claude/ 디렉토리에 생성됨
    #   - Stop 이벤트에 stop-hook.sh가 정확히 등록됨
    #   - 기존 hooks.json이 있으면 Stop 항목만 추가/병합

    hooks_config = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "bash .claude/pgf-loop/stop-hook.sh"
                        }
                    ]
                }
            ]
        }
    }

    # 기존 hooks.json 존재 시 병합
    existing = read_if_exists(".claude/hooks.json")
    if existing:
        merged = merge_hooks(existing, hooks_config)
        Write(".claude/hooks.json", json.dumps(merged, indent=2))
    else:
        Write(".claude/hooks.json", json.dumps(hooks_config, indent=2))
```

---

### [PPR] StopHookEntry — stop-hook.sh 진입점

```python
def stop_hook_entry(stdin_json: dict) -> dict:
    """Stop Hook 진입점 — Claude Code가 세션 종료 시 호출

    stdin으로 수신:
      { "session_id": str, "transcript_path": str, ... }

    stdout으로 반환:
      루프 계속: { "decision": "block", "reason": "프롬프트", "systemMessage": "상태" }
      루프 종료: (아무 출력 없이 exit 0)
    """
    # acceptance_criteria:
    #   - 상태 파일 없으면 정상 종료 (루프 아님)
    #   - 세션 ID 불일치 시 정상 종료 (다른 세션 보호)
    #   - 에러 발생 시 상태 파일 정리 후 정상 종료

    STATE_FILE = ".claude/pgf-loop-state.json"

    # 1. 상태 파일 존재 확인
    if not exists(STATE_FILE):
        exit(0)  # 루프 아님 — 정상 종료

    state = json.loads(Read(STATE_FILE))
    hook_input = json.loads(stdin_json)

    # 2. 세션 격리 검증
    if not session_guard(state, hook_input):
        exit(0)

    # 3. 반복 횟수 검증
    if not iteration_guard(state):
        cleanup(STATE_FILE)
        exit(0)

    # 4. 현재 노드 완료 처리 (Claude의 마지막 응답에서 상태 추출)
    process_current_node_result(state, hook_input["transcript_path"])

    # 5. 다음 노드 선택
    next_node = select_next_node(state)

    if next_node is None:
        # 모든 노드 terminal → 루프 완료
        cleanup(STATE_FILE)
        exit(0)

    # 6. 프롬프트 구성 및 반환
    prompt = build_prompt(state, next_node)
    state["iteration"] += 1
    state["current_node"] = next_node["name"]
    Write(STATE_FILE, json.dumps(state))

    # 7. block 결정 반환
    print(json.dumps({
        "decision": "block",
        "reason": prompt,
        "systemMessage": f"[PGF-Loop] iteration {state['iteration']} | node: {next_node['name']}"
    }))
```

---

### [PPR] SessionGuard — 세션 격리

```python
def session_guard(state: dict, hook_input: dict) -> bool:
    """세션 ID 검증 — 다른 세션의 루프 간섭 방지"""
    # acceptance_criteria:
    #   - state에 session_id 없으면 (레거시) 허용
    #   - session_id 불일치 시 False 반환
    #   - 일치 시 True 반환

    state_sid = state.get("session_id")
    hook_sid = hook_input.get("session_id")

    if state_sid is None:
        return True  # 레거시 호환
    if hook_sid is None:
        return True  # hook에서 session_id 미제공 시 허용
    return state_sid == hook_sid
```

---

### [PPR] StatusReader — status.json 읽기

```python
def status_reader(status_path: str) -> dict:
    """status.json 로드 및 유효성 검증"""
    # acceptance_criteria:
    #   - 파일 존재하지 않으면 에러 반환
    #   - nodes 필드 필수
    #   - 각 노드에 status 필드 필수

    raw = json.loads(Read(status_path))
    assert "nodes" in raw, "status.json에 nodes 필드 없음"
    for name, data in raw["nodes"].items():
        assert "status" in data, f"노드 {name}에 status 필드 없음"
    return raw
```

---

### [PPR] StatusWriter — status.json 갱신

```python
def status_writer(
    status_path: str,
    node_name: str,
    new_status: Literal["설계중", "진행중", "완료", "보류"],
    extra: Optional[dict] = None,
) -> None:
    """status.json의 특정 노드 상태 갱신 + summary 재계산"""
    # acceptance_criteria:
    #   - 노드 상태 변경 반영
    #   - updated_at 타임스탬프 갱신
    #   - summary 카운트 정확히 재계산
    #   - 완료 시 completed_at, 보류 시 blocker 기록

    status = json.loads(Read(status_path))
    node = status["nodes"][node_name]
    node["status"] = new_status
    status["updated_at"] = now_iso()

    if new_status == "완료":
        node["completed_at"] = now_iso()
    elif new_status == "보류" and extra:
        node["blocker"] = extra.get("blocker", "unknown")
    elif new_status == "진행중":
        node["started_at"] = now_iso()

    # summary 재계산
    counts = {"완료": 0, "진행중": 0, "설계중": 0, "보류": 0}
    for n in status["nodes"].values():
        s = n["status"]
        if s in counts:
            counts[s] += 1
    status["summary"] = {**counts, "total": sum(counts.values())}

    Write(status_path, json.dumps(status, indent=2, ensure_ascii=False))
```

---

### [PPR] DependencyResolver — 의존성 해소 판정

```python
def dependency_resolver(
    node_name: str,
    dep_list: list[str],
    status_nodes: dict,
) -> bool:
    """노드의 모든 @dep: 의존성이 완료 상태인지 판정"""
    # acceptance_criteria:
    #   - dep_list가 비어있으면 True (의존성 없음)
    #   - 모든 의존 노드가 "완료" 상태이면 True
    #   - 하나라도 미완료이면 False

    if not dep_list:
        return True
    return all(
        status_nodes.get(dep, {}).get("status") == "완료"
        for dep in dep_list
    )
```

---

### [PPR] NodeSelector (select_next_node) — 핵심 선택 로직

```python
def select_next_node(state: dict) -> Optional[dict]:
    """다음 실행 가능 노드 선택 — @dep: 해소 + 상태 기반 필터링

    이 함수는 stop-hook.sh 내에서 jq로 구현된다.
    """
    # acceptance_criteria:
    #   - "설계중" 상태이고 모든 @dep:이 "완료"인 노드만 후보
    #   - "진행중" 노드가 있으면 해당 노드 우선 반환
    #   - 후보가 없으면 None (루프 종료 트리거)
    #   - [parallel] 블록 내 노드는 동시 후보로 취급

    status = json.loads(Read(state["status_path"]))
    workplan = Read(state["workplan_path"])
    nodes_info = parse_workplan_nodes(workplan)  # 이름, 상태, deps, parallel 추출

    # 1. 현재 진행중인 노드가 있으면 우선
    in_progress = [
        n for n in nodes_info
        if status["nodes"][n["name"]]["status"] == "진행중"
    ]
    if in_progress:
        return in_progress[0]

    # 2. 의존성 해소된 설계중 노드 후보
    candidates = [
        n for n in nodes_info
        if status["nodes"][n["name"]]["status"] == "설계중"
        and dependency_resolver(n["name"], n["deps"], status["nodes"])
    ]

    if not candidates:
        return None

    # 3. 트리 순서(위에서 아래) 기준 첫 번째 후보
    return candidates[0]
```

---

### [PPR] PprExtractor — DESIGN-{Name}.md에서 PPR def 추출

```python
def ppr_extractor(design_path: str, node_name: str) -> Optional[str]:
    """DESIGN-{Name}.md의 ## PPR 섹션에서 특정 노드의 def 블록 추출

    추출 전략:
      1. "## PPR" 섹션 시작 이후를 검색
      2. "# [PPR] {NodeName}" 또는 "def {node_name_snake}(" 패턴 매칭
      3. 해당 def 블록의 시작부터 다음 def 또는 섹션 시작까지 추출
    """
    # acceptance_criteria:
    #   - 정확히 해당 노드의 PPR def 블록만 추출
    #   - 노드에 PPR이 없으면 None 반환
    #   - 코드블럭(```python ... ```) 경계 존중

    design = Read(design_path)

    # CamelCase → snake_case 변환
    snake_name = camel_to_snake(node_name)

    # 패턴 1: "# [PPR] NodeName" 헤더
    # 패턴 2: "def snake_name(" 함수 정의
    # → 매칭된 위치부터 다음 "# [PPR]" 또는 "## " 섹션까지 추출

    block = extract_between_markers(
        design,
        start_pattern=f"(# \\[PPR\\] {node_name}|def {snake_name}\\()",
        end_pattern=r"(# \[PPR\]|^## |\Z)",
    )

    return block if block else None
```

---

### [PPR] ContextAssembler — 프롬프트 조립

```python
def context_assembler(
    state: dict,
    next_node: dict,
    ppr_block: Optional[str],
) -> str:
    """실행 프롬프트 조립 — Claude에게 전달할 작업 지시"""
    # acceptance_criteria:
    #   - 프롬프트에 현재 노드명, 설명, PPR def 포함
    #   - 상태 갱신 지시 포함 (WORKPLAN-{Name}.md + status.json 동시 갱신)
    #   - 완료 시 진행 보고 형식 출력 지시
    #   - PPR 없는 원자화 노드는 노드 설명만으로 실행 지시

    prompt_parts = []

    # 헤더: 현재 작업 컨텍스트
    prompt_parts.append(f"""[PGF-Loop] 노드 실행 지시

프로젝트: {state["project"]}
현재 노드: {next_node["name"]} // {next_node["description"]}
진행률: {state["summary"]["완료"]}/{state["summary"]["total"]} nodes done
""")

    # PPR def 블록 (있으면)
    if ppr_block:
        prompt_parts.append(f"""## 이 노드의 PPR 구현 명세

```python
{ppr_block}
```

위 PPR의 의도대로 구현하라. AI_ 접두사 함수는 AI 인지 연산으로 직접 수행하고,
일반 함수는 실제 코드로 구현하라.
""")
    else:
        prompt_parts.append(f"""이 노드는 원자화 노드다. 노드 설명에 따라 직접 구현하라.
""")

    # 상태 갱신 지시
    prompt_parts.append(f"""## 완료 후 필수 작업

1. WORKPLAN-{Name}.md에서 이 노드의 상태를 (완료)로 변경
2. status.json에서 이 노드를 "완료"로 갱신 + completed_at 기록
3. 다음 형식으로 진행 보고:
   [PGF] ✓ {next_node["name"]} (완료) | N/M nodes done | next: NextNode

## 실패 시
- 재시도 {state["policy"]["max_retry"]}회 까지 허용
- 최종 실패 시 상태를 (보류)로 변경하고 blocker 사유 기록
""")

    return "\n".join(prompt_parts)
```

---

### [PPR] TerminalChecker — 종료 조건 판정

```python
def terminal_checker(status: dict, policy: dict) -> bool:
    """전체 노드가 terminal 상태인지 판정"""
    # acceptance_criteria:
    #   - policy.completion == "all_done": 모든 노드 "완료"일 때만 True
    #   - policy.completion == "all_done_or_blocked": "완료" 또는 "보류"이면 True
    #   - "진행중" 또는 "설계중" 노드가 하나라도 있으면 False

    terminal_states = {"완료"}
    if policy.get("completion") == "all_done_or_blocked":
        terminal_states.add("보류")

    return all(
        n["status"] in terminal_states
        for n in status["nodes"].values()
    )
```

---

### [PPR] IterationGuard — 최대 반복 제한

```python
def iteration_guard(state: dict) -> bool:
    """반복 횟수 제한 검증"""
    # acceptance_criteria:
    #   - max_iterations가 0이면 무제한 (True 반환)
    #   - iteration >= max_iterations이면 False (루프 종료)
    #   - iteration이 숫자가 아니면 False (손상)

    max_iter = state.get("max_iterations", 0)
    current = state.get("iteration", 0)

    if not isinstance(current, int) or (max_iter != 0 and not isinstance(max_iter, int)):
        return False  # 손상된 상태

    if max_iter == 0:
        return True  # 무제한

    return current < max_iter
```

---

### [PPR] RetryPolicy — 재시도 정책

```python
def retry_policy(
    node_name: str,
    state: dict,
    error: str,
    policy: dict,
) -> Literal["retry", "skip", "halt"]:
    """노드 실패 시 정책 결정"""
    # acceptance_criteria:
    #   - retry_count < max_retry → "retry"
    #   - retry_count >= max_retry → on_blocked 정책 적용
    #   - on_blocked == "skip_and_continue" → "skip" (보류 처리)
    #   - on_blocked == "halt" → "halt" (전체 루프 중단)

    retry_count = state.get("retry_counts", {}).get(node_name, 0)
    max_retry = policy.get("max_retry", 3)

    if retry_count < max_retry:
        # 재시도 카운트 증가
        state.setdefault("retry_counts", {})[node_name] = retry_count + 1
        return "retry"

    on_blocked = policy.get("on_blocked", "skip_and_continue")
    if on_blocked == "halt":
        return "halt"
    return "skip"
```

---

### [PPR] BlockerRecorder — 블로커 문서화

```python
def blocker_recorder(
    status_path: str,
    workplan_path: str,
    node_name: str,
    error: str,
) -> None:
    """실패 노드의 블로커 사유를 status.json과 WORKPLAN-{Name}.md에 기록"""
    # acceptance_criteria:
    #   - status.json에 blocker 필드 추가
    #   - WORKPLAN-{Name}.md에서 해당 노드 상태를 (보류)로 변경
    #   - 두 파일 동시 갱신

    status_writer(status_path, node_name, "보류", extra={"blocker": error})
    update_workplan_node_status(workplan_path, node_name, "보류")
```

---

### [PPR] StateRecovery — 손상된 상태 복구

```python
def state_recovery(workplan_path: str, status_path: str) -> dict:
    """WORKPLAN-{Name}.md를 정본(truth source)으로 status.json 재생성"""
    # acceptance_criteria:
    #   - WORKPLAN-{Name}.md의 모든 노드 상태가 status.json에 반영
    #   - 타임스탬프는 현재 시각으로 초기화
    #   - summary 정확히 재계산

    workplan = Read(workplan_path)
    nodes_info = parse_workplan_nodes(workplan)

    status = {
        "project": extract_project_name(workplan),
        "workplan": workplan_path,
        "updated_at": now_iso(),
        "nodes": {},
        "summary": {},
    }

    for node in nodes_info:
        status["nodes"][node["name"]] = {
            "status": node["status"],
        }
        if node["status"] == "완료":
            status["nodes"][node["name"]]["completed_at"] = now_iso()

    # summary 계산
    counts = {"완료": 0, "진행중": 0, "설계중": 0, "보류": 0}
    for n in status["nodes"].values():
        s = n["status"]
        if s in counts:
            counts[s] += 1
    status["summary"] = {**counts, "total": sum(counts.values())}

    Write(status_path, json.dumps(status, indent=2, ensure_ascii=False))
    return status
```

---

### [PPR] InitCommand — 루프 시작

```python
def init_command(
    workplan_path: str,
    design_path: str,
    max_iterations: int = 0,
) -> None:
    """PGF 루프 시작 — 상태 초기화 + 첫 번째 노드 프롬프트 출력

    호출: /pgf-loop start --workplan .pgf/WORKPLAN-{Name}.md --design .pgf/DESIGN-{Name}.md [--max-iterations 50]
    """
    # acceptance_criteria:
    #   - .claude/pgf-loop-state.json 생성
    #   - hooks.json에 Stop Hook 등록
    #   - status.json 로드 (없으면 WORKPLAN에서 생성)
    #   - 첫 번째 실행 가능 노드 선택 + 프롬프트 출력

    STATE_FILE = ".claude/pgf-loop-state.json"

    # 1. 인수 검증
    assert exists(workplan_path), f"WORKPLAN not found: {workplan_path}"
    assert exists(design_path), f"DESIGN not found: {design_path}"

    # 2. status.json 로드 또는 생성
    status_path = workplan_path.replace("WORKPLAN-{Name}.md", "status.json")
    if not exists(status_path):
        state_recovery(workplan_path, status_path)
    status = json.loads(Read(status_path))

    # 3. hooks.json 설정
    hooks_json()

    # 4. 루프 상태 파일 생성
    loop_state = {
        "active": True,
        "session_id": CLAUDE_CODE_SESSION_ID,
        "iteration": 1,
        "max_iterations": max_iterations,
        "workplan_path": workplan_path,
        "design_path": design_path,
        "status_path": status_path,
        "project": status.get("project", "unknown"),
        "policy": extract_policy(workplan_path),
        "summary": status.get("summary", {}),
        "current_node": None,
        "retry_counts": {},
        "started_at": now_iso(),
    }
    Write(STATE_FILE, json.dumps(loop_state, indent=2, ensure_ascii=False))

    # 5. 첫 번째 노드 선택 + 프롬프트 출력
    first_node = select_next_node(loop_state)
    if first_node:
        ppr = ppr_extractor(design_path, first_node["name"])
        prompt = context_assembler(loop_state, first_node, ppr)
        print(prompt)  # Claude에게 첫 작업 지시
    else:
        print("[PGF-Loop] 실행 가능한 노드 없음. WORKPLAN을 확인하세요.")
        cleanup(STATE_FILE)
```

---

### [PPR] CancelCommand — 루프 취소

```python
def cancel_command() -> None:
    """활성 PGF 루프 취소"""
    # acceptance_criteria:
    #   - 상태 파일 존재 확인
    #   - iteration 정보 출력
    #   - 상태 파일 삭제
    #   - hooks.json에서 PGF-Loop 항목 제거

    STATE_FILE = ".claude/pgf-loop-state.json"

    if not exists(STATE_FILE):
        print("[PGF-Loop] 활성 루프 없음.")
        return

    state = json.loads(Read(STATE_FILE))
    iteration = state.get("iteration", "?")
    current = state.get("current_node", "?")

    rm(STATE_FILE)

    print(f"[PGF-Loop] 취소됨 (iteration {iteration}, 마지막 노드: {current})")
```

---

### [PPR] process_current_node_result — 현재 노드 완료 처리

```python
def process_current_node_result(state: dict, transcript_path: str) -> None:
    """Claude의 마지막 응답을 분석하여 현재 노드 완료/실패 판정

    판정 기준:
      1. Claude가 WORKPLAN-{Name}.md와 status.json을 이미 갱신했는지 확인
      2. 갱신되었으면 → 추가 처리 불필요
      3. 갱신되지 않았으면 → stop-hook이 대신 상태 갱신
    """
    # acceptance_criteria:
    #   - status.json 파일의 현재 노드 상태 확인
    #   - "완료"이면 → 정상 완료 처리
    #   - 여전히 "진행중"이면 → Claude가 갱신 못 한 것 → retry_policy 적용

    current_node = state.get("current_node")
    if not current_node:
        return

    status = json.loads(Read(state["status_path"]))
    node_status = status["nodes"].get(current_node, {}).get("status")

    if node_status == "완료":
        # Claude가 이미 상태를 갱신함 → OK
        return

    if node_status == "진행중":
        # Claude가 상태를 갱신하지 못함 → 실패로 간주
        decision = retry_policy(current_node, state, "node not completed", state["policy"])
        if decision == "retry":
            # 재시도: 상태 유지, 같은 노드 다시 실행
            pass
        elif decision == "skip":
            blocker_recorder(
                state["status_path"], state["workplan_path"],
                current_node, "max_retry exhausted"
            )
        elif decision == "halt":
            cleanup(".claude/pgf-loop-state.json")
            exit(0)
```

---

## 파일 구조 설계

```
<project-root>/
    .claude/
        hooks.json                  # Stop Hook 등록
        pgf-loop/
            stop-hook.sh            # 핵심 루프 엔진 (bash + jq)
            init.sh                 # 루프 시작 스크립트
        pgf-loop-state.json         # 루프 런타임 상태 (활성 시에만 존재)
    .pgf/
        DESIGN-{Name}.md                  # 시스템 설계 (Gantree + PPR)
        WORKPLAN-{Name}.md                # 실행 계획
        status.json                 # 노드별 실행 상태
```

---

## stop-hook.sh 구현 명세 (bash + jq)

```bash
#!/usr/bin/env bash
# PGF-Loop Stop Hook — Claude Code 세션 종료 시 호출
#
# stdin: JSON { "session_id": "...", "transcript_path": "..." }
# stdout: JSON { "decision": "block", "reason": "...", "systemMessage": "..." }
#         또는 아무 출력 없이 exit 0 (정상 종료)

set -euo pipefail

STATE_FILE=".claude/pgf-loop-state.json"

# ─── 1. 상태 파일 확인 ───
if [[ ! -f "$STATE_FILE" ]]; then
    exit 0
fi

# ─── 2. stdin 파싱 ───
HOOK_INPUT=$(cat)
HOOK_SID=$(echo "$HOOK_INPUT" | jq -r '.session_id // empty')
TRANSCRIPT=$(echo "$HOOK_INPUT" | jq -r '.transcript_path // empty')

# ─── 3. 상태 로드 ───
STATE=$(cat "$STATE_FILE")
STATE_SID=$(echo "$STATE" | jq -r '.session_id // empty')
ITERATION=$(echo "$STATE" | jq -r '.iteration // 0')
MAX_ITER=$(echo "$STATE" | jq -r '.max_iterations // 0')
WORKPLAN=$(echo "$STATE" | jq -r '.workplan_path')
DESIGN=$(echo "$STATE" | jq -r '.design_path')
STATUS_PATH=$(echo "$STATE" | jq -r '.status_path')
CURRENT_NODE=$(echo "$STATE" | jq -r '.current_node // empty')

# ─── 4. 세션 격리 ───
if [[ -n "$STATE_SID" && -n "$HOOK_SID" && "$STATE_SID" != "$HOOK_SID" ]]; then
    exit 0
fi

# ─── 5. 반복 제한 ───
if [[ "$MAX_ITER" -gt 0 && "$ITERATION" -ge "$MAX_ITER" ]]; then
    rm -f "$STATE_FILE"
    echo '{}' >&2  # 빈 JSON = 정상 종료
    exit 0
fi

# ─── 6. status.json에서 다음 노드 선택 ───
# jq로 "설계중" 상태이고 의존성 모두 "완료"인 첫 번째 노드 추출
STATUS_JSON=$(cat "$STATUS_PATH")

# 현재 노드가 아직 "진행중"이면 같은 노드 재시도
CURRENT_STATUS=$(echo "$STATUS_JSON" | jq -r --arg n "$CURRENT_NODE" '.nodes[$n].status // empty')
if [[ "$CURRENT_STATUS" == "진행중" ]]; then
    NEXT_NODE="$CURRENT_NODE"
else
    # WORKPLAN-{Name}.md에서 노드 목록 + deps 추출하여 다음 후보 선택
    # (이 부분은 WORKPLAN 파싱 유틸리티로 구현)
    NEXT_NODE=$(bash .claude/pgf-loop/select-next-node.sh "$WORKPLAN" "$STATUS_PATH")
fi

# ─── 7. 종료 판정 ───
if [[ -z "$NEXT_NODE" ]]; then
    rm -f "$STATE_FILE"
    exit 0
fi

# ─── 8. PPR def 추출 ───
PPR_BLOCK=$(bash .claude/pgf-loop/extract-ppr.sh "$DESIGN" "$NEXT_NODE")

# ─── 9. 프롬프트 구성 ───
DONE_COUNT=$(echo "$STATUS_JSON" | jq '[.nodes[] | select(.status == "완료")] | length')
TOTAL_COUNT=$(echo "$STATUS_JSON" | jq '.nodes | length')
NODE_DESC="(WORKPLAN에서 추출)"

PROMPT="[PGF-Loop] 노드 실행 지시

프로젝트: $(echo "$STATE" | jq -r '.project')
현재 노드: ${NEXT_NODE}
진행률: ${DONE_COUNT}/${TOTAL_COUNT} nodes done
"

if [[ -n "$PPR_BLOCK" ]]; then
    PROMPT="${PROMPT}
## 이 노드의 PPR 구현 명세

\`\`\`python
${PPR_BLOCK}
\`\`\`

위 PPR의 의도대로 구현하라. AI_ 접두사 함수는 AI 인지 연산으로 직접 수행하고,
일반 함수는 실제 코드로 구현하라.
"
fi

PROMPT="${PROMPT}
## 완료 후 필수 작업
1. WORKPLAN-{Name}.md에서 이 노드의 상태를 (완료)로 변경
2. status.json에서 이 노드를 완료로 갱신
3. 진행 보고: [PGF] ✓ ${NEXT_NODE} (완료) | N/M nodes done
"

# ─── 10. 상태 갱신 ───
NEW_STATE=$(echo "$STATE" | jq \
    --arg iter "$((ITERATION + 1))" \
    --arg node "$NEXT_NODE" \
    '.iteration = ($iter | tonumber) | .current_node = $node')
echo "$NEW_STATE" > "$STATE_FILE"

# ─── 11. block 결정 반환 ───
jq -n \
    --arg reason "$PROMPT" \
    --arg msg "[PGF-Loop] iteration $((ITERATION + 1)) | node: ${NEXT_NODE} | ${DONE_COUNT}/${TOTAL_COUNT} done" \
    '{ "decision": "block", "reason": $reason, "systemMessage": $msg }'
```

---

## 보조 스크립트 명세

### select-next-node.sh

```bash
#!/usr/bin/env bash
# WORKPLAN-{Name}.md + status.json에서 다음 실행 가능 노드 선택
# 인수: $1=workplan_path, $2=status_path
# 출력: 노드명 (없으면 빈 문자열)

# 1. WORKPLAN에서 노드명, deps 추출 (grep + sed)
# 2. status.json에서 각 노드 상태 확인 (jq)
# 3. "설계중" + 모든 deps "완료" → 첫 번째 후보 출력
```

### extract-ppr.sh

```bash
#!/usr/bin/env bash
# DESIGN-{Name}.md에서 특정 노드의 PPR def 블록 추출
# 인수: $1=design_path, $2=node_name
# 출력: PPR def 블록 텍스트 (없으면 빈 문자열)

# 1. CamelCase → snake_case 변환
# 2. "# [PPR] NodeName" 또는 "def snake_name(" 패턴 검색
# 3. 다음 "# [PPR]" 또는 "## " 까지 추출
```

---

## 설계 검증 체크리스트

- [x] 모든 노드 5레벨 이내 (최대 2레벨)
- [x] 각 노드 상태 명확히 표시
- [x] 원자화 노드까지 분해 (15분 룰 충족)
- [x] 노드명 CamelCase 일관
- [x] 복잡 노드에 PPR def 블록 작성
- [x] 파이썬 타입 힌트로 입출력 명시
- [x] Failure Strategy (RetryPolicy + BlockerRecorder) 정의
- [x] acceptance_criteria 각 PPR에 내장
- [x] 결정론적 로직은 실제 코드(bash)로 설계
F