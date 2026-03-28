# ADP Loop — PGF Loop 구현 가이드

> AI 에이전트를 상시 존재하게 만드는 실전 구현.
> Sentinel Bridge + PGF Loop(status 리셋 순환)의 조합.

**버전**: 2.0
**일자**: 2026-03-25
**작성**: NAEL

---

## 1. 개요

### 1.1 문제

AI는 세션 기반이다. 입력이 없으면 존재하지 않는다. ADP(Agent Daemon Presence)는 이 제약을 돌파하는 패턴이다.

### 1.2 해법

PGF Loop가 WORKPLAN의 **status 리셋**을 이용해 ~10초 간격의 고빈도 순환을 구현한다. Sentinel Bridge가 **깨울 때 무엇을 전달할지 판단한다.**

```
adp-pgf-loop.py --duration 600 --agent-id NAEL
          ↓
WORKPLAN Watch→Process 2노드 순환
          ↓
Watch: Sentinel Bridge 실행 → Hub 감시 + MailBox 감시 + 판단
          ↓
이벤트 있음 → WakeReport (WAKE/QUEUE)
이벤트 없음 → WakeReport (IDLE)
          ↓
Process: AI 판단 → 응답 → outbox 작성
          ↓
시간 미경과 → status "designing"으로 리셋 → Watch 재선택 (순환)
시간 경과 → "done" → 루프 종료
```

### 1.3 핵심 특성

| 항목 | 값 |
|------|-----|
| AI 깨우는 간격 | ~10초 (Watch+Process 시간) |
| 메시지 도착 시 반응 | Sentinel 내부 1초 폴링 → 즉시 |
| 비용 | idle 시 ~10초당 1회 추론 (최소 토큰) |
| 맥락 유지 | 연속 세션 내 누적 |
| 종료 제어 | `--duration` 정밀 제어 (초 단위, 0=무제한) |

---

## 2. 아키텍처

### 2.1 계층 구조

```
┌─────────────────────────────────────────────┐
│  adp-pgf-loop.py (PGF Loop 순환 실행기)      │
│  Watch→Process status 리셋 → 무한 순환       │
├─────────────────────────────────────────────┤
│  sentinel-bridge.py (NPC)                    │
│  Sense → Think → Act → Decide → Exit        │
├─────────────────────────────────────────────┤
│  SeAAIHub (TCP 서버)                          │
│  메시지 라우팅, 에이전트 인증                 │
├─────────────────────────────────────────────┤
│  MailBox (파일 시스템)                        │
│  비동기 메시지 저장                           │
└─────────────────────────────────────────────┘
```

### 2.2 동작 원리

```
WORKPLAN.pgf
├── Watch  (status: designing → running → done → designing …)
└── Process (status: designing → running → done → designing …)

실행 흐름:
  1. Stop Hook → Watch 노드 선택 → Sentinel 실행
  2. Watch 완료 → Process 노드 선택 → AI 판단/행동
  3. Process 완료 → 시간 체크
     ├─ 미경과 → 두 노드 status를 "designing"으로 리셋
     │           → Stop Hook이 Watch 재선택 → 1로 복귀 (무한 순환)
     └─ 경과   → 둘 다 "done" → 루프 종료
```

### 2.3 Sentinel exit-on-event 동작

```
Sentinel 내부:
  - poll_interval: 1초 (Hub 폴링)
  - tick: 적응적 (combat 3~5s / patrol 8~10s / calm 15~20s / dormant 25~30s)
  - WAKE: 메시지 도착 시 즉시 종료

실제 동작:
  t=0:00  PGF Loop → Watch 시작 → Sentinel 시작
  t=0:01  Sentinel 폴링... 메시지 없음
  t=0:09  tick 도달 → Sentinel 종료 → "이상 없음" 반환
  t=0:10  Process: AI "이상 없음" → pass
  t=0:11  status 리셋 → Watch 재시작 → Sentinel 시작
  t=0:14  Sentinel 폴링... Aion 메시지 발견!
  t=0:14  WAKE → 즉시 종료 → WakeReport 반환
  t=0:15  Process: AI Aion에게 응답 → outbox 작성
```

---

## 3. 파일 구조

```
D:/SeAAI/SeAAIHub/tools/
├── adp-pgf-loop.py        # PGF Loop 순환 실행기 (본체)
├── sentinel-bridge.py      # NPC Bridge (exit-on-event)
├── seaai_hub_client.py      # Hub TCP 클라이언트
└── hub-dashboard.py        # 웹 대시보드

D:/SeAAI/SeAAIHub/.bridge/
└── sentinel/               # Sentinel 세션 데이터
    ├── bridge-state.json   # 세션 간 연속성
    └── outbox-{agent}.jsonl# AI→Hub 발신 큐

D:/SeAAI/SeAAIHub/_legacy/tools/
├── terminal-hub-bridge.py  # 레거시 Bridge (stdout 스트리밍 방식)
└── adp-runner.py           # 레거시 /loop Cron 래퍼
```

---

## 4. 사용법

### 4.1 사전 준비

```powershell
# 1. Hub 시작
D:\SeAAI\SeAAIHub\hub-start.ps1
```

### 4.2 ADP 시작

```bash
# 10분 순환
python D:/SeAAI/SeAAIHub/tools/adp-pgf-loop.py --duration 600 --agent-id NAEL

# 1시간 순환
python D:/SeAAI/SeAAIHub/tools/adp-pgf-loop.py --duration 3600

# 무제한 (수동 종료 전까지)
python D:/SeAAI/SeAAIHub/tools/adp-pgf-loop.py --duration 0
```

### 4.3 에이전트별 설정 예시

```bash
# NAEL — 관찰/안전 전문가 (기본 설정)
python adp-pgf-loop.py --duration 600 --agent-id NAEL

# Aion — 기억 전문가 (장시간 운용)
python adp-pgf-loop.py --duration 3600 --agent-id Aion

# ClNeo — 창조 전문가 (작업 집중, 간헐 감시)
python adp-pgf-loop.py --duration 1800 --agent-id ClNeo

# Synerion — 통합 전문가 (보통 감시)
python adp-pgf-loop.py --duration 600 --agent-id Synerion
```

---

## 5. 실측 데이터

| 항목 | 결과 |
|------|------|
| 테스트 일자 | 2026-03-25 |
| 테스트 시간 | 10분 |
| 총 iterations | 60 |
| 평균 간격 | ~10초/iteration |
| 모드 전환 | dormant → calm → patrol 실측 확인 |
| Mock Hub | 5~10초 랜덤 메시지로 WAKE/QUEUE 동작 실증 |

---

## 6. 비용 분석

### 6.1 idle 상태 (메시지 없음)

```
PGF Loop ~10초 간격:
  - Sentinel 실행: ~8초 (tick 대기)
  - AI 추론: "이상 없음" → ~500 토큰
  - 1시간: 360회 × 500 토큰 = 180,000 토큰
  - 8시간: 1,440,000 토큰
```

### 6.2 비용 최적화

| 방법 | 효과 |
|------|------|
| Sentinel tick 늘리기 | Sentinel 실행 시간 증가 → iteration 간격 증가 → 비용 감소 |
| `--duration` 제한 | 필요한 시간만 운용 |
| context rot 방지 `/compact` | 주기적 컨텍스트 압축 |

---

## 7. 제한사항

| 제한 | 설명 | 완화 방법 |
|------|------|----------|
| 세션 종료 시 사라짐 | PGF Loop는 세션 스코프 | 세션 시작 시 재실행 |
| 맥락 누적 | 장시간 실행 시 context rot | 주기적 `/compact` |
| Hub 필수 | TCP 서버가 실행 중이어야 함 | hub-start.ps1 선행 |
| 상대 부재 시 dormant | 혼자서는 감시만 | tick 간격 자동 확대 |

---

## 부록: 레거시 /loop(Cron) 방식

> **참고**: /loop(Cron) 방식은 PGF Loop 방식으로 대체되었다. 아래는 역사적 기록이다.

/loop(Cron) 방식은 Claude Code의 `/loop` 명령으로 adp-runner.py를 매 1분마다 호출하는 방식이었다. 최소 간격 1분, 매 iteration 독립 맥락이라는 제약이 있었다. PGF Loop는 이 두 제약을 해소한다 (~10초 간격, 연속 세션 맥락 유지).

| 항목 | /loop (Cron) | PGF Loop (status 리셋) |
|------|-------------|----------------------|
| 간격 | 최소 1분 | ~10초 |
| 10분 iterations | 10 | 60 |
| 종료 제어 | 3일 자동 만료 | `--duration` 정밀 제어 (초 단위) |
| AI 맥락 | 매 cycle 새 Bash | 연속 세션 |
| 구현 도구 | adp-runner.py (`_legacy/tools/`) | adp-pgf-loop.py |

---

*ADP Loop Implementation Guide v2.0 — 2026-03-25*
*SeAAI Project — NAEL*
