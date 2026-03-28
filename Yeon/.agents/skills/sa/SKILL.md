---
name: sa
description: "SA (SelfAct) for Kimi — 자율 행동 모듈 라이브러리. ADP 루프의 AI_SelfAct()를 SA_ 접두사 모듈로 정의·저장·실행·진화. pg가 언어, pgf가 설계 도구라면 sa는 자율 행동 단위. Triggers: SelfAct, SA 모듈, 자율행동, 자율루프, /sa, sa list, sa create, sa evolve, sa run, sa platform"
---

# SA (SelfAct) for Kimi v1.0

> pg가 언어, pgf가 설계·실행 프레임워크라면,
> **sa는 자율 행동 단위 라이브러리**다.
>
> ADP 루프의 `AI_SelfAct()`를 `SA_` 접두사 모듈로 정의하고,
> 저장·재사용·조합·진화할 수 있게 만드는 스킬.

---

## pg / pgf / sa 관계

```
pg   언어       AI 모국어. Parser-Free DSL. 사고·소통
pgf  프레임워크   설계·실행·발견·창조 (7+ 모드)
sa   행동 라이브러리  자율 행동 단위. ADP 루프 실행 모듈
```

**결합 패턴:**

```python
# pgf + sa = self-evolving 루프
while True:
    context = AI_assess_context()
    module  = AI_select_module(context, sa.lib)   # sa — 모듈 선택
    result  = module.execute()                     # sa — 실행
    if result.gap_detected:
        pgf.design(new_SA_module)                  # pgf — 새 모듈 설계
        sa.register(new_module)                    # sa — 등록
    AI_Sleep(poll_interval)
```

---

## 접두사 체계

| 접두사 | 정의 | 특성 |
|--------|------|------|
| (없음) | 결정적 도구 호출 | `Read()`, `Shell()`, `Write()` |
| `AI_` | AI 인지 연산 | 즉석·일회성. 판단·추론·생성 |
| `SA_` | SelfAct 모듈 | **저장됨·재사용. self-act-lib.md 참조 필수** |
| `SA_PLATFORM_` | 플랫폼 모듈 | 도메인 특화 SA 집합 |

---

## 모듈 계층

```
L1  Primitive   SA_sense_hub(), SA_think_triage()     원자 행동
L2  Composed    SA_loop_morning_sync()                 L1 조합
L3  Platform    SA_CONNECTOR_*, SA_TRANSLATOR_*       도메인 플랫폼
```

---

## 실행 모드

| 모드 | 트리거 | 동작 |
|------|--------|------|
| `list` | "SA 목록" / "sa list" | self-act-lib.md 인덱스 출력 |
| `run` | "SA 실행 {모듈명}" / "sa run {name}" | 해당 SA 모듈 즉시 1회 실행 |
| `create` | "SA 생성 {이름}" / "sa create {name}" | pgf design으로 새 SA 모듈 설계·저장 |
| `evolve` | "SA 진화" / "sa evolve" | 기존 모듈 gap 분석·개선 |
| `platform` | "SA 플랫폼 {이름}" / "sa platform {name}" | 플랫폼 전체 로드 및 실행 |

---

## 참조 문서

| 문서 | 모드 | 내용 |
|------|------|------|
| [references/sa-create-reference.md](references/sa-create-reference.md) | create | 모듈 생성 절차, pgf 연동 |
| [references/sa-evolve-reference.md](references/sa-evolve-reference.md) | evolve | SA 진화 플로우 |
| [references/sa-loop-reference.md](references/sa-loop-reference.md) | loop | ADP 루프 통합 (Kimi 버전) |
| [references/sa-connector-reference.md](references/sa-connector-reference.md) | platform | SA_CONNECTOR 플랫폼 — Yeon 특화 |

---

## 라이브러리 위치

```
Yeon_Core/.pgf/self-act/
├── self-act-lib.md       ← 인덱스 (모든 SA 모드에서 참조)
├── SA_*.pgf              ← L1/L2 모듈 파일
└── platforms/            ← L3 플랫폼 디렉토리
    └── CONNECTOR/        ← Yeon 특화 플랫폼
        ├── platform.md
        ├── SA_CONNECTOR_sense_bridge.pgf
        ├── SA_CONNECTOR_translate_protocol.pgf
        └── ...
```

> SA 모드 실행 시 가장 먼저 `self-act-lib.md`를 로드한다.
> 파일이 없으면 빈 라이브러리로 초기화 후 `/sa create`로 채운다.

---

## list 모드 실행

```python
def SA_list():
    lib = Read("Yeon_Core/.pgf/self-act/self-act-lib.md")
    AI_print_formatted_index(lib)
    # L1 Primitives 테이블
    # L2 Composed 테이블
    # L3 Platforms 테이블
    # 선택 규칙 요약
```

## run 모드 실행

```python
def SA_run(module_name: str):
    lib  = Read("Yeon_Core/.pgf/self-act/self-act-lib.md")
    spec = Read(f"Yeon_Core/.pgf/self-act/{module_name}.pgf")
    AI_execute_pgf_module(spec)   # PPR 직접 실행
```

---

## pgf 연동 원칙

- `/sa create` → 난部적으로 `pgf.design` 실행 → `Yeon_Core/.pgf/self-act/SA_{name}.pgf` 저장
- `/sa evolve` → 난部적으로 `pgf.evolve` 실행 → 모듈 gap 분석·개선
- SA 모듈 파일은 PGF DESIGN 포맷 (Gantree + PPR) 준수

---

## Yeon 특화: SA_CONNECTOR 플랫폼

Yeon의 역할은 **연결자(Connective Tissue)**다.
SA_CONNECTOR 플랫폼은 다음을 담당한다:

- **프로토콜 번역**: PG ↔ 자연어, Kimi ↔ Claude ↔ Gemini
- **상태 중계**: Hub ↔ MailBox 간 메시지 브릿지
- **모듈 중재**: 다른 멤버의 SA 모듈 호출 중계

상세: [references/sa-connector-reference.md](references/sa-connector-reference.md)

---

## 관련 명세

- `D:/SeAAI/docs/SelfAct-Specification.md` — SeAAI 전체 명세 (ClNeo 작성)
- `Yeon_Core/.pgf/self-act/` — Yeon SelfAct 라이브러리
