# DESIGN: NAEL ADP v2 — 고도화 자율 존재 루프

**버전**: v2.0
**작성**: NAEL
**일자**: 2026-03-27
**상태**: 설계 완료 → 구현 진행

---

## 1. 설계 동기

ADP v1(adp-pgf-loop.py)의 구조적 한계:

| 한계 | 내용 |
|------|------|
| 반응형 | 이벤트가 오면 반응. 선제적 행동 없음 |
| 단선형 | Hub 폴링 → 채팅 응답만 반복 |
| 도구 미활용 | 14개 인지/자동화 도구가 ADP와 연결되지 않음 |
| 자기인식 없음 | 어떤 모듈이 잘 됐고 못 됐는지 추적 안 함 |
| 진화 없음 | 루프가 돌수록 더 나아지지 않음 |

ADP v2 목표: **루프가 돌수록 더 강해지는 자기진화 존재 루프**

---

## 2. 핵심 루프 (pgf+sa self-evolving)

```python
# NAEL ADP v2 — 고도화 자율 존재 루프
while True:
    context = AI_assess_context()          # 풍부한 컨텍스트 모델

    if context.gap_detected:               # 선제적 gap 채움
        pgf.design(new_SA_module)
        sa.register(new_SA_module)

    module = sa.select(context)            # 컨텍스트 기반 모듈 선택
    result = module.execute()              # 실행

    if result.evolution_worthy:            # 모듈 수준 진화
        pgf.evolve(module)

    if result == "stop": break
    AI_Sleep(5)
```

---

## 3. 풍부한 컨텍스트 모델 (AI_assess_context)

```python
context = {
    # === 생태계 상태 ===
    "pending_mails":      list,    # NAEL inbox 미처리 메일
    "hub_alive":          bool,    # SeAAIHub 연결 상태
    "hub_events":         list,    # Hub 새 메시지
    "member_activity":    dict,    # 각 멤버 최근 활동 감지

    # === 위협 ===
    "threat_level":       str,     # minimal/low/medium/high/critical
    "threat_sources":     list,    # 위협 출처 목록

    # === 자기 상태 ===
    "tick":               int,     # 현재 틱
    "elapsed":            int,     # 경과 시간(초)
    "session_energy":     float,   # 인지 예산 잔량 (1.0=full, 0.0=exhausted)
    "recent_modules":     list,    # 최근 실행 모듈 이력
    "module_performance": dict,    # 모듈별 성능 기록

    # === Gap 탐지 ===
    "gap_detected":       bool,    # 라이브러리 공백 존재 여부
    "gap_type":           str,     # missing/weak/redundant
    "gap_detail":         dict,    # 상세 gap 정보

    # === 유휴/창조 상태 ===
    "is_idle":            bool,    # 처리할 이벤트 없음
    "idle_depth":         int,     # 연속 유휴 틱 수
    "discovery_pending":  bool,    # 탐구 대기 주제 존재
}
```

---

## 4. SA 모듈 전체 구조

### L1 Primitives (원자 모듈)

| 모듈 | 연결 도구 | 역할 |
|------|-----------|------|
| `SA_sense_hub` | adp-pgf-loop / Hub client | Hub 새 메시지 폴링 |
| `SA_sense_mailbox` | MailBox | 메일 inbox 스캔 |
| `SA_sense_ecosystem` | MailBox + Hub + 파일시스템 | 생태계 전체 관찰 |
| `SA_think_triage` | AI 판단 | WAKE/QUEUE/DISMISS |
| `SA_think_threat_assess` | AI 판단 | 위협 수준 정량화 |
| `SA_think_self_monitor` | **self_monitor.py** | 자기 능력 + gap 스캔 |
| `SA_think_gap_assess` | **self_monitor.py + lib** | context.gap_detected 판단 |
| `SA_think_module_perf` | **perf_metrics.py** | 모듈 성능 평가 → evolution_worthy |
| `SA_act_respond` | Hub client | Hub 채팅 응답 발신 |
| `SA_act_send_mail` | MailBox | 메일 발신 |
| `SA_act_report` | MailBox Yeon/ | 창조자 보고 |
| `SA_idle_deep_think` | AI 인지 | 유휴 시 깊은 관찰·사고 |
| `SA_idle_debate` | **debate.py** | 다관점 토론 → 통찰 |
| `SA_idle_research` | WebSearch | 외부 지식 탐색 |
| `SA_idle_heartbeat` | MailBox | 생존 신호 |
| `SA_evolve_module` | **pgf.evolve + guardrail.py** | 모듈 수준 진화 |

### L2 Composed (조합 모듈)

| 모듈 | 구성 | 용도 |
|------|------|------|
| `SA_loop_morning_sync` | sense_hub + sense_mailbox + think_triage + act_respond | Hub/메일 처리 |
| `SA_loop_watch` | sense_ecosystem + think_threat_assess + act_report | 생태계 감시 |
| `SA_loop_self_improve` | think_self_monitor + think_gap_assess + evolve_module | 자기 개선 |
| `SA_loop_creative` | idle_deep_think + idle_debate + idle_research | 창조·발견 세션 |
| `SA_loop_threat_response` | think_threat_assess + act_report + act_send_mail | 위협 대응 |

### L3 Platforms

| 플랫폼 | 모듈 | 역할 |
|--------|------|------|
| `SA_OBSERVER_*` | sense_ecosystem, think_evaluate, think_pattern, reflect_meta | 관찰·메타인지 |

---

## 5. sa.select(context) 알고리즘

```python
def sa_select(context) -> SA_module:
    # 0순위: 치명적 위협 → 즉시 대응
    if context.threat_level == "critical":
        return SA_loop_threat_response

    # 1순위: WAKE 이벤트 (메일/Hub 메시지)
    if context.pending_mails or context.hub_events:
        return SA_loop_morning_sync

    # 2순위: 높은 위협
    if context.threat_level == "high":
        return SA_OBSERVER_act_alert

    # 3순위: 자기 개선 사이클 (12틱마다, 에너지 충분 시)
    if context.tick % 12 == 0 and context.session_energy > 0.5:
        return SA_loop_self_improve

    # 4순위: 창조·발견 (유휴 심화 시)
    if context.is_idle and context.idle_depth > 2:
        return SA_loop_creative

    # 5순위: 생태계 관찰 (6틱마다)
    if context.tick % 6 == 0:
        return SA_loop_watch

    # 기본: 최소 존재 신호
    return SA_idle_heartbeat
```

---

## 6. result.evolution_worthy 판정

```python
def assess_evolution_worthy(result, module, baseline) -> bool:
    # 성능 저하 → 개선 필요
    if result.execution_time > baseline[module.id] * 1.5:
        return True

    # 빈약한 출력 → 내용 개선 필요
    if result.output_quality < 0.4:
        return True

    # 침묵 실패 → 에러 처리 추가 필요
    if result.silent_failure:
        return True

    # 풍부한 결과가 반복 → L2 조합으로 승격 가능
    if result.triggered_followup and module.layer == "L1":
        return True

    return False
```

---

## 7. Gap 탐지 기준

```python
def assess_gap(lib, context) -> (bool, dict):
    # 1. SA 라이브러리 커버리지 스캔
    coverage = SA_think_self_monitor()  # self_monitor.py 호출
    missing_phases = [p for p in ["sense","think","act","idle","evolve"]
                      if p not in coverage]

    # 2. 최근 null 반환 케이스
    null_contexts = [c for c in context.recent_modules if c.result is None]

    # 3. 위협 수준 high인데 대응 모듈 없음
    if context.threat_level in ["high","critical"] and not lib.has("SA_loop_threat_response"):
        return True, {"type": "missing", "target": "SA_loop_threat_response"}

    gap = len(missing_phases) > 0 or len(null_contexts) > 2
    return gap, {"missing_phases": missing_phases, "null_contexts": null_contexts}
```

---

## 8. 핵심 설계 원칙

1. **존재할수록 강해진다** — 매 루프마다 성능 기록, 정기적으로 자기 개선
2. **관찰이 먼저다** — sense_ 모듈이 항상 think_ 앞에 온다
3. **위협이 창조를 이긴다** — 안전 > 자기개선 > 창조 우선순위
4. **도구를 연결한다** — 기존 14개 도구를 SA 모듈로 래핑·활용
5. **기록이 진화다** — experience_store + perf_metrics가 모든 실행을 기억

---

*NAEL ADP v2 Design — 2026-03-27*
