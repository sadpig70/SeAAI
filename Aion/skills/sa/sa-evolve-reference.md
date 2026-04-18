# SA Evolve Reference

> `/sa evolve` 모드 상세 가이드.
> SA_GENETICS 플랫폼을 사용하여 기존 SA 모듈을 자기 진화시킨다.
> pgf + sa가 결합하는 핵심 지점 — SA 모듈이 SA 모듈을 진화시킨다.

---

## 개념: 재귀적 자기 진화

```
SA_GENETICS = SA 모듈을 진화시키는 SA 플랫폼
            = 메타 SelfAct

SA_GENETICS_sense_genome()    현재 SA 라이브러리 상태 스캔
SA_GENETICS_think_mutation()  변이·개선 설계
SA_GENETICS_act_splice()      모듈 교체·추가·삭제
SA_GENETICS_verify_fitness()  적합도 검증
```

---

## 실행 흐름

```python
def SA_Mode_Evolve():
    """SA_GENETICS 기반 SA 라이브러리 자기 진화."""

    # Phase 1: 유전체 스캔
    genome = SA_GENETICS_sense_genome()
    # genome = {
    #   modules: [SA_sense_hub, SA_think_triage, ...],
    #   coverage: {sense: 2, think: 1, act: 1, idle: 1},
    #   gaps: [],    # 아직 없는 행동 유형
    #   weak: [],    # 성능 낮은 모듈
    #   redundant: [], # 중복 모듈
    # }

    # Phase 2: Gap 탐지
    gaps = AI_detect_gaps(genome)
    # 탐지 기준:
    #   - 누락된 phase (예: evolve_ 모듈 없음)
    #   - 과거 실행 실패 패턴
    #   - lib.md 선택 규칙에서 null 반환 케이스
    #   - 에이전트 정체성과 맞지 않는 모듈

    # Phase 3: 변이 설계
    mutations = SA_GENETICS_think_mutation(gaps)
    # mutation 유형:
    #   ADD:     새 모듈 추가 (sa.create 호출)
    #   IMPROVE: 기존 모듈 PPR 개선 (pgf.review 호출)
    #   MERGE:   유사 모듈 통합
    #   REMOVE:  불필요 모듈 제거

    # Phase 4: 변이 실행
    [parallel]
        for m in mutations:
            if m.type == "ADD":
                SA_Mode_Create(m.target)
            elif m.type == "IMPROVE":
                pgf.review(m.target_file)
            elif m.type == "MERGE":
                SA_GENETICS_act_splice(m.source, m.target)
            elif m.type == "REMOVE":
                SA_lib_deregister(m.target)
    [/parallel]

    # Phase 5: 적합도 검증
    fitness = SA_GENETICS_verify_fitness(mutations)
    # 검증:
    #   - 변이된 모듈 실행 테스트
    #   - lib.md 일관성 확인
    #   - 전체 커버리지 개선 여부

    # Phase 6: 진화 기록
    AI_record_evolution(E_num, "SelfAct Library Evolution", mutations, fitness)
```

---

## SA_GENETICS 모듈 명세

### SA_GENETICS_sense_genome

```python
def SA_GENETICS_sense_genome() -> dict:
    """현재 SA 라이브러리 전체 상태 스캔."""
    lib     = Read(".pgf/self-act/self-act-lib.md")
    modules = Glob(".pgf/self-act/*.pgf")
    coverage = AI_analyze_coverage(lib, modules)
    gaps     = AI_detect_coverage_gaps(coverage)
    return {"modules": modules, "coverage": coverage, "gaps": gaps}
```

### SA_GENETICS_think_mutation

```python
def SA_GENETICS_think_mutation(gaps: dict) -> list:
    """Gap을 기반으로 변이 목록 설계. pgf.discover 페르소나 활용."""
    [parallel]
        p1 = AI_think_as_persona("Disruptive Engineer", gaps)   # 급진적 변이
        p3 = AI_think_as_persona("Contrarian Critic", gaps)     # 불필요 제거
        p4 = AI_think_as_persona("Connecting Scientist", gaps)  # 모듈 연결
    [/parallel]
    mutations = AI_converge_to_mutation_plan([p1, p3, p4])
    return mutations
```

### SA_GENETICS_verify_fitness

```python
def SA_GENETICS_verify_fitness(mutations: list) -> dict:
    """변이 결과 적합도 검증."""
    results = {}
    for m in mutations:
        if m.type in ("ADD", "IMPROVE"):
            test_result = SA_run(m.target)   # 실행 테스트
            results[m.target] = {
                "executable": test_result.success,
                "coverage_improved": AI_check_coverage_change(m),
            }
    return results
```

---

## 진화 기록

`/sa evolve` 실행 후 진화 결과를 자동 기록:

```
ClNeo_Evolution_Log.md → Evolution #N: SA Library Evolution
.pgf/self-act/evolution-log.jsonl → 상세 변이 이력
```
