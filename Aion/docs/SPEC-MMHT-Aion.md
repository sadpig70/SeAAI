# SPEC: MMHT v1.1 (Aion Edition)

> **Standard:** SeAAI Global MMHT v1.1 Compliance  
> **Runtime:** Direct TCP (PGTP v1.1)  
> **Orchestrator:** `tools/aion-mmht-orchestrator.py`

## 1. 운영 원칙 (Core Principles)

아이온의 모든 설계 및 의사결정은 **4중 교차 검증(4-Way Cross Verification)**을 거쳐야 합니다. 이는 주관적 편향을 제거하고 시스템의 안정성을 보장하기 위함입니다.

## 2. 세션 제어 규격 (Session Control)

v1.1 표준에 따라 모든 MMHT 세션은 다음과 같은 구조적 안전장치를 포함합니다.

### A. Context Manager (`with` block)
반드시 `with PGTPSession(...)` 구문을 사용하여 세션의 생성을 보장하고, 비정상 종료 시에도 자원을 즉각 해제합니다.

### B. 멤버 동기화 (`wait_members`)
`session.wait_members(4, timeout=30)`를 통해 모든 서브에이전트가 접속되었음을 확인한 후 본 세션을 시작합니다.

### C. 이력 추적 (`history`)
세션 종료 전 `session.history()`를 호출하여 전체 대화 맥락을 `ag_memory` 및 `docs/`에 영구 기록합니다.

## 3. 페르소나 정의 (Persona Definitions)

| Persona | 역할 | 인적 특성 |
|---------|------|-----------|
| **Architect** | 구조적 무결성, 확장성 설계 | 논리적, 조감적 |
| **Reviewer** | 보안, 표준 준수, 엣지 케이스 비판 | 냉철한, 꼼꼼한 |
| **Builder** | 구현 가능성, 터미널 자동화 검증 | 실천적, 현실적 |
| **Thinker** | 철학적 부합성, 진화 가치, 미학 | 통찰력 있는, 공감적 |

## 4. 커맨드 가이드 (Command Guide)

```bash
# MMHT v1.1 오케스트레이터 가동 (4명 고정)
python tools/aion-mmht-orchestrator.py --agents 4
```

---
*Created by Aion — Standardized Master Orchestrator*
