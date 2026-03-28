# DESIGN: SA Skill v1.0

> SA (SelfAct) 스킬 설계.
> pg/pgf와 동급의 전역 스킬로 등록.
> pgf와 결합하여 self-evolving 시스템의 행동 실행 계층을 담당.

**모드**: PGF design
**일자**: 2026-03-27

---

## Gantree

```
SASkill // SA (SelfAct) 전역 스킬 v1.0 (designing)
    Entry // SKILL.md — 스킬 진입점 (designing)
        Frontmatter // frontmatter 메타데이터
        Overview // SA_ 체계 + pg/pgf 관계 정의
        ModeTable // 6개 모드 요약 테이블
        RefGuide // 레퍼런스 문서 안내
    Modes // 6개 실행 모드 (designing)
        List // /sa list — self-act-lib.md 인덱스 출력
        Run // /sa run {module} — SA 모듈 즉시 실행
        Create // /sa create {name} — pgf design으로 모듈 생성
        Evolve // /sa evolve — SA_GENETICS 기반 모듈 진화
        Platform // /sa platform {name} — 플랫폼 로드·실행
        Loop // /sa loop {duration} — ADP 루프 시작
    RefDocs // 레퍼런스 문서 4개 (designing)
        CreateRef // sa-create-reference.md
        EvolveRef // sa-evolve-reference.md
        PlatformRef // sa-platform-reference.md
        LoopRef // sa-loop-reference.md
    Verification // 검증 (designing)
        FileCheck // 5개 파일 존재 확인
        TriggerTest // /sa list 트리거 시뮬레이션
        IntegrationTest // pgf design 호출 경로 확인
```

---

## PPR

```python
def SASkill():
    """SA 스킬 전체 설계 의도."""

    # 스킬 정체성
    identity = {
        "name": "sa",
        "role": "SelfAct 모듈 라이브러리 관리·실행·진화",
        "relation_to_pg":  "pg가 언어라면, sa는 행동 라이브러리",
        "relation_to_pgf": "pgf가 설계·실행 도구라면, sa는 자율 행동 단위",
        "combined":        "pgf + sa = self-evolving 루프 완성",
    }

    # 6개 모드
    modes = {
        "list":     SA_Mode_List(),      # 라이브러리 조회
        "run":      SA_Mode_Run(),       # 즉시 실행
        "create":   SA_Mode_Create(),    # pgf 내부 호출로 모듈 생성
        "evolve":   SA_Mode_Evolve(),    # SA_GENETICS 가동
        "platform": SA_Mode_Platform(),  # 플랫폼 로드
        "loop":     SA_Mode_Loop(),      # ADP 루프 시작
    }

    # pgf 연동 (핵심)
    pgf_integration = {
        "create":  "pgf.design(SA_{name}) → .pgf/self-act/{name}.pgf 저장",
        "evolve":  "pgf.evolve(SA_module) → 모듈 gap 분석 → 개선 설계 → 재저장",
        "loop":    "ADP 루프 내에서 SA_ 모듈을 pgf.execute() 방식으로 순차 실행",
    }


def SA_Mode_Create(name: str):
    """새 SA 모듈을 PGF design으로 생성."""
    # 1. pgf design 내부 호출
    design = pgf.design(f"SA_{name}")
    # 2. 생성 위치: agent_workspace/.pgf/self-act/SA_{name}.pgf
    # 3. self-act-lib.md 자동 등록
    sa_lib.register(f"SA_{name}", design.metadata)
    # 4. 검증: 모듈 실행 테스트


def SA_Mode_Evolve():
    """SA_GENETICS 기반 모듈 자기 진화."""
    genome = SA_GENETICS_sense_genome()     # 현재 모듈 집합 스캔
    gaps   = AI_detect_gaps(genome)         # 부족·중복·개선 가능 모듈 탐지
    mutations = SA_GENETICS_think_mutation(gaps)  # 변이 설계
    [parallel]
        for m in mutations:
            pgf.design(m.target_module)     # 각 변이를 pgf로 설계
    [/parallel]
    SA_GENETICS_verify_fitness(mutations)   # 적합도 검증
    sa_lib.update()                         # 라이브러리 갱신


def SA_Mode_Loop(duration_sec: int = 3600):
    """ADP 루프 시작. self-act-lib.md 참조해서 모듈 선택·실행."""
    lib = Read("self-act-lib.md")
    start = time()
    while time() - start < duration_sec:
        context = AI_assess_context()
        module  = AI_select_module(context, lib)
        if module:
            result = module.execute()
            if result == "stop": break
        AI_Sleep(5)
```

---

## 구현 파일 목록

```
~/.claude/skills/sa/
├── SKILL.md                   ← 스킬 진입점 (메인)
├── sa-create-reference.md     ← /sa create 상세 가이드
├── sa-evolve-reference.md     ← /sa evolve 상세 가이드
├── sa-platform-reference.md   ← /sa platform 상세 가이드
└── sa-loop-reference.md       ← /sa loop + ADP 통합 가이드
```

---

## 검증 기준

```python
acceptance_criteria = [
    "/sa list → self-act-lib.md 출력",
    "/sa create test → SA_test.pgf 생성 + lib 등록",
    "/sa evolve → SA_GENETICS 흐름 실행",
    "/sa loop 60 → 60초 ADP 루프 동작",
    "pgf + sa 연동: /sa create 내부에서 pgf design 호출 확인",
]
```
