# Epigenetic PPR System Design @v:1.0

> PPR 명세(genome)는 불변으로 유지하면서, 실행 컨텍스트(epigenome)에 따라
> 노드 발현 패턴을 동적으로 조절하는 인지 가소성 아키텍처.
> 내장 Decision Audit Trail로 모든 발현 결정을 자동 추적.

## 설계 배경

### 핵심 원리: 후성유전학 → PPR 매핑

| 생물학 개념 | PPR 매핑 | 구현 |
|------------|---------|------|
| DNA (genome) | PPR def 블록 | 불변 `.md` 파일 내 함수 정의 |
| Methylation (메틸화) | Expression Suppressor | 컨텍스트 조건에 따라 노드 실행 억제 |
| Histone Modification | Accessibility Modifier | 노드 실행 파라미터 가중치 조절 |
| Chromatin State | Execution Readiness | 노드 활성/휴면/억제 3-state |
| Epigenome | Context Expression Layer | `epigenome.yaml` + MemOS 상태 |
| Cell Differentiation | Agent Role Specialization | 동일 PPR → 컨텍스트별 다른 행동 |

### 해결하는 문제

1. **재현성 vs 적응성 트레이드오프**: genome(불변)으로 재현성, epigenome(가변)으로 적응성
2. **코드 폭발 방지**: N개 컨텍스트 = N개 발현 패턴, 코드 변형 불필요
3. **감사 가능한 적응**: 모든 발현 결정에 자동 audit trail

---

## Gantree

```
EpigeneticPPR // Epigenetic PPR 시스템 (설계중) @v:1.0
    GenomeLayer // 불변 PPR 명세 계층 (설계중)
        GenomeRegistry // PPR def 블록 등록 및 버전 관리 (설계중)
        GenomeValidator // genome 불변성 검증 (설계중)
        IntentFingerprint // 노드별 의도 해시 생성 (설계중)
    EpigenomeLayer // 컨텍스트 발현 계층 (설계중)
        ContextSensor // 실행 컨텍스트 수집 (설계중)
            MemOSStateReader // MemOS 메모리 상태 읽기 (설계중)
            SessionContextReader // 세션/사용자/프로젝트 컨텍스트 (설계중)
            EnvironmentReader // 실행 환경 (시간, 부하, 이력) (설계중)
        ExpressionEngine // 발현 결정 엔진 (설계중)
            MethylationGate // 노드 실행 억제/허용 판정 (설계중)
            HistoneModifier // 실행 파라미터 가중치 조절 (설계중)
            ChromatinState // 노드 활성/휴면/억제 상태 관리 (설계중)
        ExpressionProfile // 발현 프로파일 관리 (설계중)
            ProfileStore // 컨텍스트별 발현 패턴 저장 (설계중)
            ProfileLearner // 실행 결과 피드백으로 프로파일 학습 (설계중)
            ProfileInheritance // 에이전트 간 발현 패턴 상속 (설계중)
    ExpressionBoundary // 발현 경계 메커니즘 (설계중)
        BoundaryPolicy // 허용 발현 범위 정의 (설계중)
        DriftDetector // 의도 이탈 감지 (설계중)
        SafetyGuard // 위험 발현 차단 (설계중)
    AuditTrail // Decision Audit Trail 내장 (설계중)
        TraceRecorder // 발현 결정 추론 trace 기록 (설계중)
        TraceStore // 구조화된 trace 저장 (설계중)
        TraceAnalyzer // trace 패턴 분석 및 요약 (설계중)
    Integration // 기존 시스템 통합 (설계중)
        PGFLoopAdapter // PGF-Loop 엔진 연동 (설계중)
        MemOSBridge // MemOS 양방향 동기화 (설계중)
        PPRInterceptor // PPR 실행 전 epigenome 주입 (설계중)
```

---

## PPR

### 핵심 타입 정의

```python
# ── 타입 정의 ──

ContextVector = dict[str, Any]
# 실행 컨텍스트 벡터
# {
#     "user_profile": str,         # 사용자 유형
#     "session_type": str,         # 세션 목적 (design/execute/explore)
#     "memory_state": dict,        # MemOS 현재 상태 요약
#     "project_phase": str,        # 프로젝트 단계
#     "execution_history": list,   # 최근 실행 이력
#     "environment": dict,         # 시스템 환경 (시간, 부하)
# }

ExpressionState = Literal["active", "dormant", "suppressed"]
# active: 정상 실행
# dormant: 조건 충족 시 활성화 대기
# suppressed: 명시적 억제 (methylation)

ExpressionModifier = dict[str, float]
# 실행 파라미터 가중치
# {
#     "creativity": 0.0~1.0,      # AI_ 함수 창의성 수준
#     "verbosity": 0.0~1.0,       # 출력 상세도
#     "risk_tolerance": 0.0~1.0,  # 위험 감수 수준
#     "depth": 0.0~1.0,           # 분석 깊이
# }

ExpressionDecision = dict
# {
#     "node_id": str,
#     "genome_hash": str,          # PPR def 원본 해시 (불변 검증)
#     "context": ContextVector,
#     "state": ExpressionState,
#     "modifiers": ExpressionModifier,
#     "rationale": str,            # AI가 생성한 발현 결정 근거
#     "timestamp": str,
# }

TraceEntry = dict
# {
#     "decision": ExpressionDecision,
#     "execution_result": Any,
#     "quality_score": float,
#     "feedback_applied": bool,    # 결과가 프로파일 학습에 반영되었는지
# }
```

### [PPR] GenomeRegistry — PPR def 블록 등록

```python
def genome_registry(design_pgf_path: str) -> dict[str, GenomeEntry]:
    """DESIGN-{Name}.md에서 모든 PPR def 블록을 추출하여 불변 레지스트리 구성"""
    # acceptance_criteria:
    #   - 모든 PPR def 블록이 누락 없이 등록될 것
    #   - 각 엔트리에 intent_fingerprint가 포함될 것
    #   - genome_hash가 SHA-256으로 계산될 것

    pgf_content: str = Read(design_pgf_path)
    ppr_blocks: list[dict] = extract_ppr_blocks(pgf_content)

    registry: dict[str, GenomeEntry] = {}
    for block in ppr_blocks:
        node_id: str = block["function_name"]
        genome_hash: str = sha256(block["source"])
        intent_fp: str = AI_extract_intent_fingerprint(block["source"])

        registry[node_id] = {
            "source": block["source"],
            "genome_hash": genome_hash,
            "intent_fingerprint": intent_fp,
            "parameters": block["parameters"],
            "return_type": block["return_type"],
        }

    Write(f"{project_root}/.pgf/genome_registry.json", json.dumps(registry))
    return registry
```

### [PPR] GenomeValidator — 불변성 검증

```python
def genome_validator(
    registry: dict[str, GenomeEntry],
    design_pgf_path: str,
) -> bool:
    """현재 DESIGN-{Name}.md와 레지스트리 간 genome 불변성을 검증"""
    # acceptance_criteria:
    #   - 모든 등록된 노드의 genome_hash가 현재 소스와 일치할 것
    #   - 불일치 발견 시 경고 + 변경 diff 기록

    current_blocks = extract_ppr_blocks(Read(design_pgf_path))

    for block in current_blocks:
        node_id = block["function_name"]
        if node_id in registry:
            current_hash = sha256(block["source"])
            if current_hash != registry[node_id]["genome_hash"]:
                AI_log_genome_mutation(
                    node_id=node_id,
                    old_hash=registry[node_id]["genome_hash"],
                    new_hash=current_hash,
                    severity="warning",
                )
                return False
    return True
```

### [PPR] ContextSensor — 컨텍스트 수집

```python
def context_sensor() -> ContextVector:
    """현재 실행 컨텍스트를 수집하여 벡터화"""

    [parallel]
    memory_state = memos_state_reader()
    session_ctx = session_context_reader()
    env_ctx = environment_reader()
    [/parallel]

    context: ContextVector = {
        "user_profile": session_ctx.get("user_profile", "default"),
        "session_type": session_ctx.get("session_type", "general"),
        "memory_state": memory_state,
        "project_phase": session_ctx.get("project_phase", "unknown"),
        "execution_history": memory_state.get("recent_executions", [])[-10:],
        "environment": env_ctx,
    }
    return context
```

### [PPR] MemOSStateReader — MemOS 상태 읽기

```python
def memos_state_reader() -> dict:
    """MemOS 3-Layer 메모리 상태 요약"""
    # MemOS 3-Layer: Working / Episodic / Semantic

    memory_dir = f"{project_root}/.claude/projects/{project_id}/memory"
    memory_index = Read(f"{memory_dir}/MEMORY.md")

    memory_files: list[str] = Glob(f"{memory_dir}/*.md")
    memory_summary = AI_summarize_memory_state(
        index=memory_index,
        file_count=len(memory_files),
    )

    return {
        "total_memories": len(memory_files),
        "summary": memory_summary,
        "recent_executions": extract_recent_from_memory(memory_dir),
        "capacity_usage": len(memory_files) / 200,  # MEMORY.md 200줄 한계 기준
    }
```

### [PPR] ExpressionEngine — 발현 결정 엔진 (핵심)

```python
def expression_engine(
    node_id: str,
    genome: GenomeEntry,
    context: ContextVector,
    profile_store: dict,
    boundary_policy: dict,
) -> ExpressionDecision:
    """컨텍스트와 genome을 기반으로 발현 결정을 내림 — 핵심 인지 함수"""
    # acceptance_criteria:
    #   - 발현 상태가 active/dormant/suppressed 중 하나일 것
    #   - modifiers의 모든 값이 0.0~1.0 범위일 것
    #   - rationale이 비어있지 않을 것
    #   - boundary_policy 위반이 없을 것

    # Step 1: Methylation Gate — 실행 여부 판정
    methylation_state: ExpressionState = methylation_gate(
        node_id=node_id,
        genome=genome,
        context=context,
        policy=boundary_policy,
    )

    if methylation_state == "suppressed":
        rationale = AI_explain_suppression(node_id, context, genome)
        return ExpressionDecision(
            node_id=node_id,
            genome_hash=genome["genome_hash"],
            context=context,
            state="suppressed",
            modifiers={},
            rationale=rationale,
        )

    # Step 2: Histone Modification — 파라미터 조절
    modifiers: ExpressionModifier = histone_modifier(
        node_id=node_id,
        genome=genome,
        context=context,
        existing_profile=profile_store.get(node_id, {}),
    )

    # Step 3: Boundary Check — 발현 경계 검증
    drift_score: float = drift_detector(
        intent_fingerprint=genome["intent_fingerprint"],
        modifiers=modifiers,
        context=context,
    )

    if drift_score > boundary_policy.get("max_drift", 0.3):
        modifiers = safety_guard(modifiers, boundary_policy)

    # Step 4: Generate Rationale
    rationale: str = AI_generate_expression_rationale(
        node_id=node_id,
        context_summary=AI_summarize(str(context), style="one-line"),
        state=methylation_state,
        modifiers=modifiers,
        drift_score=drift_score,
    )

    return ExpressionDecision(
        node_id=node_id,
        genome_hash=genome["genome_hash"],
        context=context,
        state=methylation_state,
        modifiers=modifiers,
        rationale=rationale,
    )
```

### [PPR] MethylationGate — 실행 억제/허용

```python
def methylation_gate(
    node_id: str,
    genome: GenomeEntry,
    context: ContextVector,
    policy: dict,
) -> ExpressionState:
    """노드 실행의 억제/활성/휴면 상태를 결정"""

    # 규칙 기반 판정 (deterministic)
    if node_id in policy.get("always_suppress", []):
        return "suppressed"
    if node_id in policy.get("always_active", []):
        return "active"

    # AI 인지 기반 판정 (context-sensitive)
    relevance: float = AI_assess_relevance(
        node_intent=genome["intent_fingerprint"],
        current_context=context,
    )

    if relevance < 0.2:
        return "suppressed"
    elif relevance < 0.5:
        return "dormant"
    else:
        return "active"
```

### [PPR] HistoneModifier — 파라미터 가중치 조절

```python
def histone_modifier(
    node_id: str,
    genome: GenomeEntry,
    context: ContextVector,
    existing_profile: dict,
) -> ExpressionModifier:
    """컨텍스트에 따라 실행 파라미터 가중치를 조절"""

    base_modifiers: ExpressionModifier = {
        "creativity": 0.5,
        "verbosity": 0.5,
        "risk_tolerance": 0.5,
        "depth": 0.5,
    }

    # 컨텍스트 기반 조절
    session_type = context.get("session_type", "general")
    if session_type == "design":
        base_modifiers["creativity"] = 0.8
        base_modifiers["depth"] = 0.8
    elif session_type == "execute":
        base_modifiers["creativity"] = 0.3
        base_modifiers["risk_tolerance"] = 0.2
    elif session_type == "explore":
        base_modifiers["creativity"] = 0.9
        base_modifiers["risk_tolerance"] = 0.7

    # 학습된 프로파일 적용
    if existing_profile:
        for key in base_modifiers:
            if key in existing_profile:
                # 기존 프로파일과 70:30 블렌딩
                base_modifiers[key] = (
                    existing_profile[key] * 0.7 + base_modifiers[key] * 0.3
                )

    # AI 미세 조절
    adjusted: ExpressionModifier = AI_fine_tune_modifiers(
        base=base_modifiers,
        node_intent=genome["intent_fingerprint"],
        context=context,
    )

    # 범위 클램핑
    for key in adjusted:
        adjusted[key] = max(0.0, min(1.0, adjusted[key]))

    return adjusted
```

### [PPR] DriftDetector — 의도 이탈 감지

```python
def drift_detector(
    intent_fingerprint: str,
    modifiers: ExpressionModifier,
    context: ContextVector,
) -> float:
    """발현 결정이 원래 의도에서 벗어난 정도를 0.0~1.0으로 측정"""
    # 0.0 = 완전 정렬, 1.0 = 완전 이탈

    drift_score: float = AI_assess_intent_drift(
        original_intent=intent_fingerprint,
        current_modifiers=modifiers,
        execution_context=context,
    )
    return drift_score
```

### [PPR] TraceRecorder — Audit Trail 기록

```python
def trace_recorder(
    decision: ExpressionDecision,
    execution_result: Any = None,
    quality_score: float = 0.0,
) -> TraceEntry:
    """발현 결정 + 실행 결과를 구조화된 trace로 기록"""

    entry: TraceEntry = {
        "decision": decision,
        "execution_result": type(execution_result).__name__,
        "quality_score": quality_score,
        "feedback_applied": False,
        "timestamp": now_iso(),
    }

    # trace 파일에 append
    trace_path = f"{project_root}/.pgf/epigenome/trace.jsonl"
    append_jsonl(trace_path, entry)

    return entry
```

### [PPR] ProfileLearner — 발현 패턴 학습

```python
def profile_learner(
    traces: list[TraceEntry],
    current_profile: dict,
) -> dict:
    """축적된 trace에서 성공 패턴을 학습하여 프로파일 갱신"""
    # acceptance_criteria:
    #   - quality_score >= 0.7인 trace만 학습 대상
    #   - 학습률(learning_rate) = 0.1 (급격한 변화 방지)
    #   - 갱신 전/후 프로파일 diff 기록

    successful_traces = [t for t in traces if t["quality_score"] >= 0.7]

    if not successful_traces:
        return current_profile

    # 성공 패턴의 modifier 평균 계산
    avg_modifiers: ExpressionModifier = {}
    for key in ["creativity", "verbosity", "risk_tolerance", "depth"]:
        values = [t["decision"]["modifiers"].get(key, 0.5) for t in successful_traces]
        avg_modifiers[key] = sum(values) / len(values)

    # 점진적 갱신 (learning_rate = 0.1)
    updated_profile = {}
    for key in avg_modifiers:
        old_val = current_profile.get(key, 0.5)
        updated_profile[key] = old_val * 0.9 + avg_modifiers[key] * 0.1

    return updated_profile
```

### [PPR] PPRInterceptor — PPR 실행 전 epigenome 주입 (통합 핵심)

```python
def ppr_interceptor(
    node_id: str,
    ppr_function: callable,
    args: dict,
    genome_registry: dict,
    profile_store: dict,
    boundary_policy: dict,
) -> Any:
    """PPR 함수 실행 전 epigenome을 주입하고, 실행 후 trace를 기록하는 인터셉터"""
    # acceptance_criteria:
    #   - genome 불변성이 유지될 것
    #   - 모든 실행에 ExpressionDecision이 생성될 것
    #   - trace가 누락 없이 기록될 것
    #   - suppressed 노드는 실행하지 않고 None 반환

    # Phase 1: Context Sensing
    context: ContextVector = context_sensor()

    # Phase 2: Expression Decision
    genome = genome_registry[node_id]
    decision: ExpressionDecision = expression_engine(
        node_id=node_id,
        genome=genome,
        context=context,
        profile_store=profile_store,
        boundary_policy=boundary_policy,
    )

    # Phase 3: Gate Check
    if decision["state"] == "suppressed":
        trace_recorder(decision)
        return None

    # Phase 4: Execute with Modifiers
    # modifiers를 실행 환경에 주입
    execution_context = {
        **args,
        "_epigenome_modifiers": decision["modifiers"],
        "_expression_state": decision["state"],
    }

    try:
        result = ppr_function(**execution_context)
        quality: float = AI_assess_quality(str(result), domain="ppr_output")
    except Exception as e:
        result = None
        quality = 0.0

    # Phase 5: Trace Recording
    trace_recorder(decision, result, quality)

    # Phase 6: Profile Feedback (비동기)
    if quality >= 0.7:
        profile_store[node_id] = profile_learner(
            traces=load_recent_traces(node_id, limit=20),
            current_profile=profile_store.get(node_id, {}),
        )

    return result
```

### [PPR] BoundaryPolicy — 발현 경계 정의

```python
def load_boundary_policy(policy_path: str) -> dict:
    """epigenome 발현 경계 정책 로드"""
    # 기본 정책 구조:
    # {
    #     "max_drift": 0.3,              # 의도 이탈 허용 최대값
    #     "always_active": [],            # 항상 활성 노드 목록
    #     "always_suppress": [],          # 항상 억제 노드 목록
    #     "modifier_bounds": {            # 각 modifier의 허용 범위
    #         "creativity": [0.1, 0.95],
    #         "risk_tolerance": [0.0, 0.8],
    #     },
    #     "immune_nodes": [],             # Immune Zone: 발현 변경 불가 노드
    # }

    if file_exists(policy_path):
        return parse_yaml(Read(policy_path))
    else:
        return DEFAULT_BOUNDARY_POLICY
```

---

## 파일 구조

```
<project-root>/
    .pgf/
        DESIGN-EpigeneticPPR.md     # 이 설계 문서
        epigenome/
            boundary_policy.yaml     # 발현 경계 정책
            genome_registry.json     # PPR def 블록 불변 레지스트리
            profiles/
                {node_id}.json       # 노드별 학습된 발현 프로파일
            trace.jsonl              # Decision Audit Trail (append-only)
```

---

## 실행 순서 의존성

```
GenomeRegistry → GenomeValidator → ContextSensor
                                        ↓
                                 ExpressionEngine
                                 (MethylationGate + HistoneModifier)
                                        ↓
                                 DriftDetector → SafetyGuard
                                        ↓
                                 PPRInterceptor (통합)
                                        ↓
                                 TraceRecorder → ProfileLearner
```
