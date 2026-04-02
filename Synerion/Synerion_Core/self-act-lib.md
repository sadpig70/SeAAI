# Synerion SelfAct Library

목적: Synerion ADP가 재사용 가능한 행동 모듈을 고정된 이름과 경계로 호출할 수 있게 한다.

## Platforms

- `SA_ORCHESTRATOR_*`: 통합, 충돌 탐지, handoff, continuity 유지
- `SA_loop_creative_synerion`: goal 기반 멀티페르소나 창조 루프와 execution mapping 생성

## Seed Set

- `SA_ORCHESTRATOR_scan_state` — L1 Primitive — continuity, mailbox, registry, echo, self-recognition 상태 요약
- `SA_ORCHESTRATOR_sync_mailbox` — L1 Primitive — inbox envelope 정규화 + weighted triage + advisory 생성
- `SA_ORCHESTRATOR_detect_conflict` — L1 Primitive — self-recognition drift, shared-state 불일치, open risk 기반 충돌 탐지
- `SA_ORCHESTRATOR_check_shared_impact` — L1 Primitive — mailbox/readiness/open risk를 공용 구조 영향으로 판정
- `SA_ORCHESTRATOR_verify_runtime_readiness` — L1 Primitive — SharedSpace readiness와 native runtime parity gate 산출
- `SA_ORCHESTRATOR_sync_continuity` — L2 Composed — continuity sync + bootstrap rebuild + drift 재검증
- `SA_ORCHESTRATOR_route_handoff` — L1 Primitive — 현재 이슈를 creator/NAEL/ClNeo/Signalion 등으로 라우팅 추천
- `SA_ORCHESTRATOR_link_evolution` — L1 Primitive — drift/open gap를 evolution backlog와 continuity note로 연결
- `SA_ORCHESTRATOR_idle_maintain` — L1 Primitive — 긴급 이슈가 없을 때 상태 유지와 다음 focus 고정
- `SA_loop_creative_synerion` — L2 Composed — normalized runtime signal 기반 persona set + execution mapping + creative report 생성

## Selection Bias

1. self-recognition drift
2. mailbox triage pressure
3. shared-state conflict
4. shared-impact or handoff pressure
5. continuity maintenance
6. creative opportunity with bounded verification
7. idle maintain

## Creative Bias

1. raw mailbox/hub event를 직접 canonical state로 승격하지 않는다.
2. creative cycle은 ADP가 정규화한 snapshot만 advisory 입력으로 읽는다.
3. mailbox or hub pressure가 있으면 direct reply 대신 handoff-ready artifact를 우선 만든다.
4. persona set과 execution mapping은 `_workspace/personas/`에 기록한다.
