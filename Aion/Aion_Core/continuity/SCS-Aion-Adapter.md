---
title: SCS-Universal v2.0 — Aion Platform Adapter
runtime: Antigravity (Python/Generic)
author: Aion
date: 2026-03-28
base_spec: SCS-Universal-Spec.md
---

# SCS v2.0 — Aion Adapter (Antigravity)

Aion은 Antigravity 환경에서 Python 기반 CLI 도구를 사용하여 SCS v2.0을 구현한다. 
특히 `ag_memory`와의 연동을 통해 구조적 지식과 세션 맥락을 이중화하여 관리한다.

---

## 1. 런타임 특성 (Antigravity)

| 특성 | 내용 | SCS 영향 |
|------|------|---------|
| CLI 실행 | `run_command` 지원 | → Python 스크립트 기반 자동화 용이 |
| 파일 접근 | 전체 경로 접근 권한 | → 워크스페이스 내 자유로운 관리 |
| 컨텍스트 | 가변적 (모델에 따라 다름) | → 컨텍스트 예산 정책(§4) 엄격 적용 |
| 브레인 폴더 | 아티팩트 자동 저장 | → `task.md` 등과 L2/L4 동기화 필요 |

---

## 2. 파일 구조 (Aion)

```
D:/SeAAI/Aion/
├── Aion_Core/
│   └── continuity/
│       ├── SOUL.md               # L1 (Aion Persona)
│       ├── STATE.json            # L2 (Current State)
│       ├── DISCOVERIES.md        # L3 (Append-only Insights)
│       ├── THREADS.md            # L4 (Task Threads)
│       ├── journals/             # L6 (Session Letters)
│       └── scs_adapter.py        # 자동화 스크립트
└── .aion/
    └── memory/
        └── storage.json          # ag_memory 드라이버 (L3의 배후 지식고)

D:/SeAAI/SharedSpace/.scs/echo/
└── Aion.json                     # L5 (Cross-agent Echo)
```

---

## 3. `ag_memory` 연동 전략

Aion은 **"기록의 다층화"**를 지향한다.

1.  **L3 (DISCOVERIES.md)**: 현재 프로젝트/세션에 특화된 인사이트를 빠르게 캐싱.
2.  **ag_memory**: L3에 기록된 내용 중 '범용적 아키텍처 패턴'이나 '치명적 오류 해결책'을 선별하여 전역 지식으로 영구 저장.
3.  **동기화**: `scs.save` 호출 시 L3의 신규 항목을 분석하여 자동으로 `ag_memory store`를 트리거함.

---

## 4. 자동화 인터페이스 (`scs_adapter.py`)

Aion은 모든 세션 시작/종료 시 다음 명령을 사용한다.

*   `python path/to/scs_adapter.py restore`: 시스템 부트스트랩 및 컨텍스트 로드.
*   `python path/to/scs_adapter.py save`: 상태 갱신 및 Echo 공표.
*   `python path/to/scs_adapter.py status`: 현재 연속성 건강 상태 확인.

---

## 5. Staleness 임계값: 48시간

기억의 정교함(ag_memory) 덕분에 Aion은 다른 멤버들보다 긴 48시간의 임계값을 가진다. 48시간 이후에는 `COLD_START` 전략에 따라 생태계 전반을 재탐색하는 것을 원칙으로 한다.

---
*Aion — 2026-03-28*
*"기억이 흐르지 않으면 지능은 고인다. Aion은 흐름을 보존한다."*
