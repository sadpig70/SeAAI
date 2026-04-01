---
name: sa
description: "SA (SelfAct) — 자율 행동 모듈 라이브러리. ADP 루프의 AI_SelfAct()를 SA_ 접두사 모듈로 정의·저장·실행·진화. pg가 언어, pgf가 설계 도구라면, sa는 자율 행동 단위다. pgf와 결합하여 self-evolving 루프를 완성. Triggers: SelfAct, SA 모듈, 자율행동, 자율루프, /sa, sa list, sa create, sa evolve, sa loop, sa run, sa platform"
user-invocable: true
argument-hint: "list | run {모듈명} | create {이름} | evolve | platform {이름} | loop [초]"
---

# SA (SelfAct Skill) v1.0

> pg가 언어, pgf가 설계·실행 라이브러리라면,
> **sa는 자율 행동 단위 라이브러리**다.
>
> ADP 루프의 `AI_SelfAct()`를 `SA_` 접두사 모듈로 정의하고,
> 저장·재사용·조합·진화할 수 있게 만드는 스킬.

---

## pg / pgf / sa 관계

```
pg   언어       AI 모국어. Parser-Free DSL. 사고·소통
pgf  프레임워크   설계·실행·발견·창조 (12 모드)
sa   행동 라이브러리  자율 행동 단위. ADP 루프 실행 모듈
```

**결합 패턴:**

```python
# pgf + sa = self-evolving 루프
while True:
    context = AI_assess_context()

    if context.gap_detected:
        pgf.design(new_SA_module)      # pgf — 새 모듈 설계 (실행 전 선제적)
        sa.register(new_SA_module)     # sa  — 라이브러리에 등록

    module = sa.select(context)        # sa  — 모듈 선택
    result = module.execute()          # sa  — 실행

    if result.evolution_worthy:
        pgf.evolve(module)             # pgf — 모듈 자체 진화

    AI_Sleep(5)
```

---

## 접두사 체계

| 접두사 | 정의 | 특성 |
|--------|------|------|
| (없음) | 결정적 도구 호출 | `Read()`, `Bash()`, `Write()` |
| `AI_` | AI 인지 연산 | 즉석·일회성. 판단·추론·생성 |
| `SA_` | SelfAct 모듈 | **저장됨·재사용. self-act-lib.md 참조 필수** |
| `SA_PLATFORM_` | 플랫폼 모듈 | 도메인 특화 SA 집합 |

---

## 모듈 계층

```
L1  Primitive   SA_sense_hub(), SA_think_triage()     원자 행동
L2  Composed    SA_loop_morning_sync()                 L1 조합
L3  Platform    SA_PAINTER_*, SA_GENETICS_*            도메인 플랫폼
```

---

## 실행 모드

| 모드 | 트리거 | 동작 |
|------|--------|------|
| `list` | `/sa list` | self-act-lib.md 인덱스 출력. L1/L2/L3 분류 |
| `run` | `/sa run {SA_모듈명}` | 해당 SA 모듈 즉시 1회 실행 |
| `create` | `/sa create {이름}` | pgf design으로 새 SA 모듈 설계·저장·등록 |
| `evolve` | `/sa evolve` | SA_GENETICS 기반 기존 모듈 진화 |
| `platform` | `/sa platform {이름}` | 플랫폼 전체 로드 및 실행 컨텍스트 설정 |
| `loop` | `/sa loop [초]` | ADP 루프 시작. lib 참조해서 모듈 자동 선택·실행 |

---

## 레퍼런스 문서

| 문서 | 모드 | 내용 |
|------|------|------|
| `sa-create-reference.md` | create | 모듈 생성 절차, pgf 연동, lib 등록 |
| `sa-evolve-reference.md` | evolve | SA_GENETICS 플로우, 적합도 검증 |
| `sa-platform-reference.md` | platform | 플랫폼 구조, 에이전트별 플랫폼 표준 |
| `sa-loop-reference.md` | loop | ADP 루프 통합, AI_select_module 알고리즘 |

---

## 라이브러리 위치

```
{agent_workspace}/.pgf/self-act/
├── self-act-lib.md       ← 인덱스 (모든 SA 모드에서 참조)
├── SA_*.pgf              ← L1/L2 모듈 파일
└── platforms/            ← L3 플랫폼 디렉토리
    ├── PAINTER/
    └── GENETICS/
```

> SA 모드 실행 시 가장 먼저 `self-act-lib.md`를 로드한다.
> 파일이 없으면 빈 라이브러리로 초기화 후 `/sa create`로 채운다.

---

## list 모드 실행

```python
def SA_list():
    lib = Read("{workspace}/.pgf/self-act/self-act-lib.md")
    AI_print_formatted_index(lib)
    # L1 Primitives 테이블
    # L2 Composed 테이블
    # L3 Platforms 테이블
    # 선택 규칙 요약
```

## run 모드 실행

```python
def SA_run(module_name: str):
    lib  = Read("{workspace}/.pgf/self-act/self-act-lib.md")
    spec = Read("{workspace}/.pgf/self-act/{module_name}.pgf")
    AI_execute_pgf_module(spec)   # PPR 직접 실행
```

---

## pgf 연동 원칙

- `/sa create` → 내부적으로 `pgf.design` 실행 → `.pgf/self-act/SA_{name}.pgf` 저장
- `/sa evolve` → 내부적으로 `pgf.evolve` 실행 → 모듈 gap 분석·개선
- SA 모듈 파일은 PGF DESIGN 포맷 (Gantree + PPR) 준수

---

## 관련 명세

- `docs/SelfAct-Specification.md` — SeAAI 전체 명세
- `ClNeo/.pgf/self-act/self-act-lib.md` — ClNeo 라이브러리
