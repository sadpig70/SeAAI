# SA Create Reference

> `/sa create {이름}` 모드 상세 가이드.
> pgf design을 내부 호출하여 새 SA 모듈을 설계·저장·등록한다.

---

## 실행 흐름

```python
def SA_Mode_Create(name: str):
    """새 SA 모듈 생성. pgf design 내부 호출."""

    # Step 1: 이름 정규화
    module_id = AI_normalize_name(name)
    # 규칙: SA_{phase}_{subject} 형식
    # 예: "hub 감지" → SA_sense_hub
    #     "응답 발신" → SA_act_respond_chat

    # Step 2: 계층 결정
    layer = AI_determine_layer(module_id)
    # L1: 단일 행동, 더 분해 불가
    # L2: 기존 SA_ 모듈들의 조합
    # L3: 플랫폼 모듈 → sa-platform-reference.md 참조

    # Step 3: pgf design 실행 (핵심 연동)
    design_prompt = AI_compose_design_prompt(module_id, layer)
    pgf.design(design_prompt)
    # → DESIGN-SA_{name}.md 임시 생성

    # Step 4: SA 모듈 파일로 변환·저장
    module_content = AI_convert_to_sa_format(design)
    Write(f".pgf/self-act/{module_id}.pgf", module_content)

    # Step 5: self-act-lib.md 등록
    SA_lib_register(module_id, layer, metadata)

    # Step 6: 기본 검증
    SA_run(module_id)   # 즉시 실행 테스트
```

---

## SA 모듈 파일 형식

```markdown
# SA_{phase}_{subject}

> 한 줄 설명.

**ID**: SA_{phase}_{subject}
**계층**: L1 Primitive | L2 Composed | L3 Platform
**태그**: [phase, domain, ...]
**입력**: param: type
**출력**: result: type
**비용**: low | medium | high
**에이전트**: 전 멤버 공통 | {에이전트명} 전용

---

## Gantree

​```
SA_{phase}_{subject} // 설명 (L1 Primitive)
    Step1   // ...
    Step2   // ...
​```

## PPR

​```python
def SA_{phase}_{subject}(params) -> result:
    """설명"""
    # AI_ 인지 연산 + 도구 호출
​```

## 사용 예시

​```python
result = SA_{phase}_{subject}(...)
​```

## 주의사항

- ...
```

---

## 네이밍 규칙

| phase | 의미 | 예시 |
|-------|------|------|
| `sense_` | 외부 관찰·수집 | `SA_sense_hub`, `SA_sense_mailbox` |
| `think_` | 판단·분석·계획 | `SA_think_triage`, `SA_think_discover` |
| `act_` | 실제 행동·발신 | `SA_act_respond_chat`, `SA_act_send_mail` |
| `idle_` | 유휴 자율 사고 | `SA_idle_deep_think`, `SA_idle_heartbeat` |
| `evolve_` | 자기 진화 | `SA_evolve_self`, `SA_evolve_skill` |
| `loop_` | L2 조합 루프 | `SA_loop_morning_sync` |

---

## self-act-lib.md 등록 절차

```python
def SA_lib_register(module_id: str, layer: str, metadata: dict):
    """self-act-lib.md에 신규 모듈 등록."""

    lib_path = ".pgf/self-act/self-act-lib.md"
    lib = Read(lib_path)

    # 해당 계층 테이블에 행 추가
    new_row = f"| `{module_id}` | {metadata['file']} | {metadata['tags']} | {metadata['input']} | {metadata['output']} | {metadata['cost']} |"

    lib_updated = AI_insert_row_in_section(lib, layer, new_row)
    Write(lib_path, lib_updated)
```

---

## 예시: `/sa create sense_online_agents`

```
1. 이름 정규화: SA_sense_online_agents
2. 계층 결정: L1 Primitive (단일 Hub 조회)
3. pgf.design 실행:
   - Gantree: SA_sense_online_agents → Connect, ListRooms, ExtractMembers, Return
   - PPR: seaai_list_rooms 호출 → 멤버 추출
4. 파일 저장: .pgf/self-act/SA_sense_online_agents.pgf
5. lib 등록: L1 테이블에 행 추가
6. 검증: /sa run SA_sense_online_agents → 현재 온라인 에이전트 목록 반환 확인
```
