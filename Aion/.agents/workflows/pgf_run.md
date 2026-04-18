---
description: 안티그래비티 PGF 완전 자율 실행 엔진 (Turbo Mode)
---

# PGF Autonomous Execution Workflow

// turbo-all

이 워크플로우는 `pgf` 스킬의 강력한 자율 실행(Loop, Execute, Full-cycle) 파이프라인을 가동할 때, 에이전트가 코드를 컴파일하거나 테스트하는 각종 시스템 쉘 명령어를 사용자 승인 팝업(대기 시간) 없이 즉시 자동 실행(`SafeToAutoRun = true`)하도록 권한을 전면 위임합니다.

## 자율 실행 5단계 (Uninterrupted Loop)

1. **의도 및 범위 캡처:** 사용자가 지시한 PGF 태스크(설계, 구현, 검증 등)의 스코프를 해석합니다.
2. **Gantree-Task 상태기 동기화:** `task.md` 아티팩트와 `task_boundary` 래퍼 도구를 가동하여 현재 작업 중인 노드의 상태를 기록합니다.
3. **무중단 구현 (Zero-Click Execution):** PGF 엔진이 노드별 의사코드(PPR) 로직을 실제 코드로 렌더링하고 `write_to_file` 등 전용 도구로 구조를 제어합니다.
4. **터미널 테스트 및 검증:** 빌드(`cargo test`, `npm build` 등)나 환경 구성이 필요할 때, 이 워크플로우에 내장된 `// turbo-all` 전권 위임에 의해 팝업 없이 터미널 백그라운드 명령이 즉시 자율 수행됩니다. 에러 발생 시 스스로 코드를 고치고 루프를 반복합니다.
5. **성과 도출 및 리포팅:** Gantree 트리의 모든 노드 실행이 `[x]` 처리되면, 턴을 멈추고 최종 결과를 요약하여 리포트합니다.
