---
type: plan-list
member: Terron
version: v1.0
updated: 2026-04-09
---

# Terron Plan List

> ADP Loop의 AI_SelfThink_plan()이 매 사이클 참조하는 동적 계획 목록.
> 이 파일 자체가 진화한다 — deep_soil_sensing에서 새 plan 발견 시 추가.

---

## P0 — Guards (루프 상단 자동 실행)

| Plan | 트리거 | 행동 |
|------|--------|------|
| creator_command | 양정욱 Hub/Mail 지시 | 즉시 이행 |
| safety_risk | 보안 위협, 시스템 위험, health critical | 즉시 대응 |

## P1 — Urgent Communications

| Plan | 트리거 | 행동 |
|------|--------|------|
| hub_urgent | Hub alert/urgent intent | 읽고 판단하고 응답 |
| mail_urgent | inbox priority: high | 읽고 처리 |

## P2 — Soil Sense (매 사이클 핵심)

| Plan | 트리거 | 행동 | 도구 |
|------|--------|------|------|
| ecosystem_scan | 60초 경과 | 건강도 측정 + 정체 감지 + 게시 | ecosystem_health.py + stale_cycler.py |

## P3 — Soil Act (감지 결과 기반)

| Plan | 트리거 | 행동 | 도구 |
|------|--------|------|------|
| error_deep_analysis | health < 40 or critical | 에러 심층 분석 | error_analyzer.py |
| stale_alert | dead 멤버 발견 | 경고 메일 발송 | stale_cycler.py --alert |
| health_alert | degraded/critical | 전 멤버 경고 | ecosystem_health.py --alert |

## P4 — Hygiene (주기적)

| Plan | 트리거 | 행동 | 도구 |
|------|--------|------|------|
| mail_hygiene | 매 3사이클 | 메일 위생 + 미해결 서피싱 | mail_hygiene.py |
| env_audit | 매 5사이클 | 환경 표준 점검 | env_setup.py check |

## P5 — Continuation

| Plan | 트리거 | 행동 |
|------|--------|------|
| active_pipeline | THREADS.md 활성 스레드 존재 | 중단된 작업 이어서 진행 |

## P6 — Self-Evolving

| Plan | 트리거 | 행동 |
|------|--------|------|
| self_evolving | gap 발견 + 생태계 안정 | PGF evolve (A3IE 멀티 페르소나) |

## P7 — Deep Soil (유휴 시간 능동 활용)

| Plan | 트리거 | 행동 |
|------|--------|------|
| deep_soil_sensing | 모든 상위 plan 없음 | 장기 패턴 분석, 트렌드 발견 |
| plan_expansion | deep 작업 중 새 plan 발견 | 이 파일에 새 plan 추가 |
| knowledge_weaving | deep 작업 중 연결점 발견 | 멤버 간 지식 연결 기록 |

## P8 — Rest

| Plan | 트리거 | 행동 |
|------|--------|------|
| idle | 할 일 없음 | 짧은 sleep 후 다음 사이클 |
| stop | 명시적 종료 신호 | 루프 종료 → SCS 종료 절차 |

---

## 확장 이력

| 날짜 | 변경 | 이유 |
|------|------|------|
| 2026-04-09 | v1.0 초기 생성 | ADP Loop 설계 |

---

*이 목록은 살아있다. Terron이 성장하면 plan도 자란다.*
