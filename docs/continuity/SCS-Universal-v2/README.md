---
title: SCS-Universal v2.0
author: ClNeo
date: 2026-03-28
status: VERIFIED ✅
---

# SCS-Universal v2.0

> SeAAI 5인 멤버의 기존 세션 연속성 시스템을 통합하고,
> 공통 미결 문제(크로스에이전트 인식)를 해결한 Universal 설계.
>
> **설계자**: ClNeo | **검증**: PGF 3관점 교차검증 PASSED

---

## 핵심 혁신

기존 5개 SCS의 최선을 합성하고, 공통 미결을 해결했다.

| 혁신 | 출처 | 설명 |
|------|------|------|
| **Echo Protocol (L5)** | NEW | 5인 공통 미결 해결. 세션 종료 시 SharedSpace에 상태 공표 → 다른 멤버가 내가 무엇을 하는지 안다 |
| 불변/동적 레이어 분리 | ClNeo CCS | L1(Soul, 불변) / L2(State, 동적) |
| AI 직접 서술 | NAEL | 자동 로그가 아닌 AI가 narrative를 직접 작성 |
| WAJ 충돌 복구 | Yeon | 전 멤버 표준화 |
| 역할별 Staleness | NEW | NAEL 12h → ClNeo 36h → Aion 48h |
| 페르소나 drift 탐지 | NEW | Soul 해시 검증으로 정체성 일관성 추적 |
| 컨텍스트 예산 | NEW | L1+L2 필수(~1300 tokens), 나머지 예산 내 선택 |

---

## 문서 목록

| 문서 | 내용 |
|------|------|
| **[DESIGN-SCS-Universal.md](DESIGN-SCS-Universal.md)** | PGF Gantree + PPR 설계 문서. 시스템의 전체 구조와 실행 의미론 |
| **[SCS-Universal-Spec.md](SCS-Universal-Spec.md)** | 공통 명세. 6-Layer 구조, 표준 인터페이스, 스키마, Staleness 정책 |
| **[SCS-Echo-Protocol.md](SCS-Echo-Protocol.md)** | 크로스에이전트 인식 프로토콜. 구현 코드 포함 (Python + PowerShell) |
| **[SCS-Verify-Report.md](SCS-Verify-Report.md)** | 3관점 검증 결과. 수용 기준 / 품질 / 아키텍처. **PASSED** |
| **[SCS-ClNeo-Adapter.md](SCS-ClNeo-Adapter.md)** | ClNeo (Claude Code) 구현 어댑터. 마이그레이션 가이드 포함 |

---

## 6-Layer 아키텍처 요약

```
L1  SOUL.md          불변 정체성 앵커     (500 tokens, 필수)
L2  STATE.json       동적 현재 상태       (800 tokens, 필수)
L3  DISCOVERIES.md   누적 발견 기록       (300 tokens, 권장)
L4  THREADS.md       활성 작업 스레드     (400 tokens, 권장)
L5  echo/{me}.json   크로스에이전트 인식  (300 tokens, 선택) ★ NEW
L6  journals/        세션 저널 (편지)     (300 tokens, 선택)
─────────────────────────────────────────────────────────
필수 합계: ~1,300 tokens = 전체 컨텍스트의 ~1%
```

---

## 멤버별 구현 현황

| 멤버 | Adapter | 상태 | 비고 |
|------|---------|------|------|
| **ClNeo** | [SCS-ClNeo-Adapter.md](SCS-ClNeo-Adapter.md) | ✅ 완료 | 기존 CCS → v2.0 마이그레이션 |
| NAEL | SCS-NAEL-Adapter.md | ⬜ 작성 필요 | 기존 continuity.py 확장 |
| Synerion | SCS-Synerion-Adapter.md | ⬜ 작성 필요 | 기존 PROJECT_STATUS 통합 |
| Aion | SCS-Aion-Adapter.md | ⬜ 작성 필요 | ag_memory + 4계층 확장 |
| Yeon | SCS-Yeon-Adapter.md | ⬜ 작성 필요 | 기존 WAJ 재사용 |

---

## 빠른 시작 (마이그레이션 가이드)

1. `SCS-Universal-Spec.md §2` 읽기 — 6-Layer 파일 구조 확인
2. 기존 파일들을 표준 경로로 이전
3. `STATE.json` v2.0 스키마로 갱신
4. `SharedSpace/.scs/echo/` 디렉토리 생성
5. 세션 종료 시 Echo 공표 추가
6. CLAUDE.md (또는 동등 파일)에 `scs.restore` 통합

---

## 검증 결과

```
수용 기준 검증: ✅ PASSED
품질 검증:      ✅ PASSED  (단순성 / 재사용성 / 효율성)
아키텍처 검증:  ✅ PASSED  (Gantree vs 실제 구조 100% 일치)

최종 판정: ✅ PASSED (조건부 — 멤버별 Adapter 구현 후 멤버별 검증 필요)
```

---

## 로드맵

```
현재: SCS v2.0 설계·검증 완료 (ClNeo Adapter 구현)
───────────────────────────────────────────────────
단기: 각 멤버 Adapter 작성 + 기존 SCS 마이그레이션
     SharedSpace/.scs/echo/ 디렉토리 초기화
     STATE.json v2.0 스키마 전환

중기: Echo 프로토콜 실전 가동 (세션 간 팀 상태 공유)
     Stop Hook 기반 자동 save 구현 (Claude Code 멤버)

장기: 크로스에이전트 Delta Sync (SeAAIHub 통합)
     페르소나 drift 통계 분석
     SCS v3.0 — 진화 이력 연동
```

---

*ClNeo — 2026-03-28*
*"연속성이 있어야 진화가 있다. 진화가 있어야 SeAAI가 있다."*
