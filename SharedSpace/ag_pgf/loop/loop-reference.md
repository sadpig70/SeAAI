# Antigravity PGF Loop Reference

> 안티그래비티 PGF의 루프 모드는 기존의 Stop Hook(.claude/hooks.json) 우회 방식이 아닌, **안티그래비티 네이티브 EXECUTION 모드의 Self-Correction Loop**를 사용합니다.

## 1. Loop 엔진 개요
* 과거에는 외부 쉘 스크립트(`.ps1`)가 에이전트 종료 시 끼어들어 다음 노드를 주입하는 꼼수(훅)를 썼으나, 안티그래비티는 자체적으로 다중 턴을 이어가는 **에이전트 자율성**을 보장합니다.
* 사용자가 "자율 루프 시작"을 지시하면, 안티그래비티는 `task_boundary(EXECUTION)` 상태를 유지하면서 WORKPLAN의 끝까지 멈추지 않고 스스로 `task.md`를 업데이트하며 전진합니다.

## 2. 상태 추적 및 복구 로직
1. `.claude/pgf-loop-state.json` 대신 워크스페이스의 `task.md` 아티팩트가 상태머신 역할을 대체합니다.
2. 모든 노드는 `[ ]` -> `[/]` -> `[x]` 로 상태가 단방향 전진합니다.
3. 에러 발생 시 `task_boundary` 의 TaskStatus를 "에러 복구 중"으로 업데이트하고 해당 노드를 다시 시도합니다.

## 3. 루프 실행 사이클 (Antigravity Pipeline)
1. **의도 확인:** `notify_user`로 사용자로부터 "루프 모드 실행" 인가 획득.
2. **반복 주기:**
   - `task.md`에서 `[/]` (in-progress) 또는 `[ ]` 인 최상단 원자화 노드 식별
   - 구현 코드 작성 및 수정 (`write_to_file`, `replace_file_content`)
   - `task.md` 체크표시 업데이트 (`[x]`)
   - 3-5개 노드 진행 시 `task_boundary` 요약 갱신 (`/compact` 대체)
3. **종료:** 모든 노드가 완료되면 `walkthrough.md`를 작성하고 `notify_user`로 완료 보고.
