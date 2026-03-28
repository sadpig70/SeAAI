---
title: SCS-Universal v2.0 ClNeo 구현 설계
author: ClNeo
date: 2026-03-29
status: implementing
base: docs/continuity/SCS-Universal-v2/SCS-ClNeo-Adapter.md
---

# SCS v2.0 — ClNeo 구현 설계 (E36)

## 갭 분석 (설계 vs 현재)

| 항목 | 설계 요구 | 현재 상태 | 갭 |
|------|----------|---------|-----|
| CLAUDE.md 프로토콜 | SCS v2.0 전체 | v1.0 부분 구현 | ★ 핵심 갭 |
| L2 정본 | STATE.json (필수 갱신) | NOW.md 우선, STATE.json stale | 정본 불명확 |
| L4 THREADS 부트스트랩 | 매 세션 필수 로드 | 조건부 로드 | 약한 연속성 |
| L5 Echo 공표 | 매 세션 종료 시 | 없음 | 미구현 |
| WAJ | 종료 전 작성 | 없음 | 미구현 |
| Staleness 체크 | 36h 임계값 | 없음 | 미구현 |
| 트리거 바인딩 | "종료" 명령 명시 | 없음 | 명세 누락 |

## 설계 결정

### DD-01: NOW.md 역할 재정의 (폐기 없음)
- **결정**: STATE.json = L2 정본(구조화). NOW.md = L2N 서사 뷰(narrative).
- **이유**: NOW.md는 AI/인간이 빠르게 읽기에 최적화. 폐기하면 복원 속도 저하.
- **구현**: 종료 시 STATE.json 먼저 갱신 → NOW.md는 "서사 요약" 역할로 유지.
- **부트스트랩**: SOUL + STATE.json(L2) + NOW.md(L2N) 순서로 로드.

### DD-02: WAJ는 경량 구현
- **결정**: 완전한 WAJ 대신, 종료 시 STATE.json 원자적 갱신 순서만 보장.
- **이유**: Claude Code의 Write 도구는 파일 단위 원자성을 보장함.
- **구현**: STATE.json → DISCOVERIES → THREADS → Journal → Echo 순서 고정.

### DD-03: 트리거 바인딩 명시
- **결정**: CLAUDE.md에 "종료" 명령 → on_session_end() 바인딩 명시.
- **이유**: 창조자의 설계 의도("종료" 명령)를 문서화하여 다음 세션에도 유효하도록.

### DD-04: Echo 공표 필수화
- **결정**: on_session_end()에 Echo 공표 추가.
- **이유**: 다른 멤버가 ClNeo의 상태를 파악 가능하게. 생태계 인식 강화.

## 구현 순서 (PPR)

```python
def SCS_Upgrade():
    # I1: CLAUDE.md 업데이트
    update_CLAUDE_md()          # 프로토콜 v2.0, 트리거 바인딩, Yeon 추가

    # I2: STATE.json 갱신 (오늘 세션 반영)
    update_STATE_json()         # 오늘 작업 내용으로 완전 갱신

    # I3: Echo 공표
    publish_Echo()              # SharedSpace/.scs/echo/ClNeo.json

    # I4: NOW.md 역할 재정의 (내용 유지, 역할 헤더 수정)
    update_NOW_md_role()        # frontmatter에 "L2N - narrative" 명시

    # [parallel] VERIFY
    V1_bootstrap_simulation()
    V2_termination_simulation()
    V3_echo_verify()

    # RECORD
    record_E36()
    update_DISCOVERIES()
    update_THREADS()
```
