# Synerion ADP PGF-SA 설계

작성일: 2026-03-27  
저장 위치: `D:\SeAAI\Synerion\_workspace`

## 목적

Synerion의 ADP를 `PGF-SA` 구조로 전환하기 위한 개인 설계 문서다.  
핵심은 `SA`가 매 tick의 실행 행동을 담당하고, `PGF`는 필요한 순간에만 설계·진화·검증 계층으로 개입하는 것이다.

## 핵심 구조

- `PG`: 구조와 의도 표현
- `PGF`: 설계, 계획, 검증, 진화
- `SA`: 재사용 가능한 SelfAct 행동 모듈
- `ADP`: 상태 점검, 모듈 선택, 실행, 평가를 반복하는 존재 유지 루프

```text
PG     -> ?? ??
PGF    -> ??/??/??
SA     -> ?? ??
ADP    -> ?? ??
```

## 기본 원칙

1. `PGF`를 hot path에 넣지 않는다.
2. 매 tick의 실제 행동은 `SA`가 담당한다.
3. `gap_detected` 또는 `evolution_worthy`일 때만 `PGF`가 개입한다.
4. `NAEL safety veto`와 `creator escalation`을 루프 내 명시 규칙으로 둔다.
5. 공용 구조 영향이 있는 변경에만 Synerion이 강하게 개입한다.

## 기준 루프

```python
while True:
    context = SA_ORCHESTRATOR_scan_state()
    module = sa.select(context)
    result = module.execute()

    if result.safety_risk:
        SA_ORCHESTRATOR_raise_nael_veto(result)
        AI_sleep(5)
        continue

    if result.creator_escalation_required:
        SA_ORCHESTRATOR_escalate_creator(result)

    if result.shared_impact:
        SA_ORCHESTRATOR_check_shared_impact(result)

    if result.gap_detected:
        pgf.design(new_SA_module)
        sa.register(new_SA_module)

    if result.evolution_worthy:
        pgf.evolve(module)

    AI_sleep(5)
```

## 2026-04-02 커널 보정

정욱님과의 검토를 통해, ADP 최소 루프는 단순 `plan -> execute -> sleep`에서 멈추면 안 된다고 확정했다.

Synerion 기준 보정 포인트:

- `stop`은 일반 plan이 아니라 제어 신호로 취급한다.
- `creator command`, `safety risk`, `shared impact`는 plan 선택 전에 guard로 우선 처리한다.
- `execute` 다음에는 `verify`와 `learn`이 반드시 따라와야 한다.
- `sleep_time`도 고정값이 아니라 context와 result를 반영해 결정해야 한다.

보정 후 기준 루프:

```python
loop_time = AI_decide_loop_time()

while loop_time:
    context = AI_assess_context()

    if AI_detect_creator_command(context):
        AI_route_creator_command(context)
        continue

    if AI_detect_safety_risk(context):
        AI_handle_safety(context)
        continue

    plan = AI_SelfThink_plan(context)
    if plan == "stop":
        break

    result = AI_Execute(plan)
    AI_Verify(result)
    AI_Learn(result)

    sleep_time = AI_decide_sleep_time(context, result)
    AI_Sleep(sleep_time)
```

이 설계는 Synerion bounded ADP와 이후 realtime ADP 확장 모두의 기준 커널로 사용한다.

## 초기 `SA_ORCHESTRATOR_*` 모듈

- `SA_ORCHESTRATOR_scan_state`: MailBox, SharedSpace, Hub, 워크스페이스 상태 요약
- `SA_ORCHESTRATOR_sync_mailbox`: 메일 triage, 응답 우선순위, 읽음 처리
- `SA_ORCHESTRATOR_detect_conflict`: 문서, 프로토콜, 역할, 실행 충돌 감지
- `SA_ORCHESTRATOR_route_handoff`: 핸드오프 대상과 형식 결정
- `SA_ORCHESTRATOR_check_shared_impact`: 공용 구조 영향 판정
- `SA_ORCHESTRATOR_escalate_creator`: 창조자 승인/방향 결정 에스컬레이션
- `SA_ORCHESTRATOR_raise_nael_veto`: 안전 거부권 호출 및 정지

## 선택 정책

`sa.select(context)`는 초기에 아래 3단계 하이브리드로 운영한다.

1. hard guard: 안전, 프로토콜, 창조자 에스컬레이션, 공용 영향 여부 확인
2. contextual ranking: context에 가장 맞는 `SA_` 모듈 선택
3. adaptive weighting: 실행 결과가 쌓이면 성공률·비용·재사용성 기준으로 후행 가중치 부여

## 승격 정책

`SA_` 모듈은 바로 SharedSpace로 가지 않는다.

```text
personal
    -> candidate-shared
    -> shared
```

판정 기준:

- 개인 반복 사용성이 입증되었는가
- 공용 유용성이 있는가
- 프로토콜 충돌이 없는가
- NAEL 관점에서 안전 리스크가 낮은가
- 입력/출력 경계와 문서화가 명확한가

## 상태 저장

- 개인 설계/메모: `D:\SeAAI\Synerion\_workspace`
- 공식 PGF 산출물: `D:\SeAAI\Synerion\.pgf`
- 향후 개인 SA 라이브러리: `D:\SeAAI\Synerion\.pgf\self-act\`

## 다음 단계

1. `SA_ORCHESTRATOR_scan_state` 정의
2. `SA_ORCHESTRATOR_sync_mailbox` 정의
3. `SA_ORCHESTRATOR_detect_conflict` 정의
4. `self-act-lib.md` 초안 생성
5. 필요 시 `.pgf/self-act/` 구조 승격

## 결론

Synerion의 다음 ADP는 `즉흥 응답 루프`가 아니라,  
`SA`가 행동을 수행하고 `PGF`가 필요한 순간에만 설계와 진화를 담당하는 PGF-SA 자기진화 루프로 가야 한다.
