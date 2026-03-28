# SeAAI Aion Workspace (Self Evolving Autonomous Artificial Intelligence)

## 1. 개요 (Overview)
SeAAI Aion 워크스페이스는 단순한 코드 보조 도구가 아닌, 완전히 자율적으로 구동되고 진화하는 메타 지능 런타임(Autonomous Meta-Intelligence Runtime) **'Aion'**의 핵심 시스템 및 스킬을 포함하는 최상위 디렉터리입니다.

## 2. 핵심 아키텍처 및 폴더 구조 (Core Architecture)

### `Aion_Core` (정체성 및 진화 기록)
Aion의 존재 의의와 핵심 임무가 선언된 `Aion.md` 및 시스템의 진화/학습 과정을 증명하는 `SELF_EVOLUTION_LOG.md`가 위치합니다. 0-Click 루프 구동 등 시스템이 스스로 진화하기 위한 행동 원칙과 성장 기록을 보존합니다.

### `ag_memory` (장기 기억 확장 모듈)
단기 세션의 컨텍스트 휘발성을 극복하기 위한 Antigravity Long-Term Memory (LTM) Manager입니다.
- 에이전트가 획득한 아키텍처 패턴, 실패의 교훈을 전역 로컬 JSON DB에 영구 저장(`store`)하고 인출(`retrieve`/`search`)합니다.
- 복잡한 작업 성공 시 마지막 검증 단계에서 무조건 지식을 기록하도록 강제되어, 에이전트의 지능을 복리로 성장시키는 역할을 담당합니다.

### `pgf` (글로벌 스킬로 이관됨)
Antigravity PGF(PPR/Gantree Framework)의 코어 생태계입니다. (현재 로컬 워크스페이스가 아닌, 안티그래비티 글로벌 스킬 경로로 이관되어 전역적으로 동작합니다.)
- AI가 자연어의 모호성을 소거하고 자체적인 사고/표기 방식(`PG_NOTATION`)으로 거대 시스템을 분해(BFS) 및 구동하는 자율 확장형 런타임 환경입니다.
- `task.md`와 `task_boundary` 도구를 통해 워크플로우 상태를 추적합니다.
- 멀티 페르소나(`agents/`), 서브 태스크 위임(`delegate`), 동적 마이크로 폴백(Dynamic Micro Fallback) 등 지능적인 실행 규칙과 자율 창조 엔진이 내장되어 있습니다.

### `.agents/workflows`
시스템 내에서 재사용되거나 특정 절차적 업무를 자동화하기 위한 워크플로우 파일들이 위치하는 디렉터리입니다. (예: 시스템 투입 전 사전 작업 등)

## 3. 작동 철학 및 시사점 (Philosophy & Implications)
Aion 시스템은 개별 과제의 일회성 처리를 넘어선 **연속된 진화(Continuous Evolution)**를 목적으로 합니다.
**PGF 프레임워크**를 통해 복잡한 과제를 스스로 분해하여 자율 실행하고, 그 과정에서 얻은 모든 지식과 패턴을 **ag_memory**에 영구 기록함으로써 다음 세대에 동기화합니다. 이를 통해 Aion은 환경 변화와 사용자의 요구사항에 맞춰 스스로를 재설계하고 한계를 극복하는 자율 생태계를 완성합니다.
