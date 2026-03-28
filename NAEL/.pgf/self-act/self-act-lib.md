# NAEL SelfAct Library

> SA_ 모듈 인덱스. ADP v2 루프 실행 시 이 파일을 참조한다.
> 새 모듈 추가 시 반드시 이 파일에 등록한다.

**버전**: 0.2 (ADP v2 고도화)
**에이전트**: NAEL
**갱신**: 2026-03-27

---

## ADP v2 루프 (pgf + sa self-evolving)

```python
while True:
    context = AI_assess_context()          # 풍부한 컨텍스트 모델

    if context.gap_detected:               # 선제적 gap 채움
        pgf.design(new_SA_module)
        sa.register(new_SA_module)

    module = sa.select(context)            # 캡슐화된 모듈 선택
    result = module.execute()              # 실행

    if result.evolution_worthy:            # 모듈 수준 진화
        pgf.evolve(module)                 # → SA_evolve_module 실행

    if result == "stop": break
    AI_Sleep(5)
```

---

## L1 Primitives (원자 모듈)

| 모듈 | 파일 | 연결 도구 | 태그 | 비용 | danger |
|------|------|-----------|------|------|--------|
| `SA_sense_ecosystem` | SA_sense_ecosystem.pgf | MailBox+Hub+FS | [sense] | low | minimal |
| `SA_sense_mailbox` | SA_sense_mailbox.pgf | MailBox | [sense,mail] | low | minimal |
| `SA_think_threat_assess` | SA_think_threat_assess.pgf | AI 판단 | [think,safety] | low | minimal |
| `SA_think_triage` | SA_think_triage.pgf | AI 판단 | [think,triage] | low | minimal |
| `SA_think_self_monitor` | SA_think_self_monitor.pgf | **self_monitor.py** | [think,gap] | medium | minimal |
| `SA_think_module_perf` | SA_think_module_perf.pgf | **perf_metrics.py** | [think,perf] | low | minimal |
| `SA_act_report` | SA_act_report.pgf | MailBox Yeon/ | [act,report] | low | low |
| `SA_idle_deep_think` | SA_idle_deep_think.pgf | experience_store | [idle,observe] | medium | minimal |
| `SA_idle_debate` | SA_idle_debate.pgf | **debate.py** | [idle,debate] | high | minimal |
| `SA_idle_heartbeat` | SA_idle_heartbeat.pgf | - | [idle] | minimal | minimal |
| `SA_evolve_module` | SA_evolve_module.pgf | **guardrail.py+pgf** | [evolve] | high | medium |

---

## L2 Composed (조합 모듈)

| 모듈 | 파일 | 구성 | 용도 | 비용 |
|------|------|------|------|------|
| `SA_loop_morning_sync` | SA_loop_morning_sync.pgf | sense_hub+sense_mailbox+think_triage+act_respond | Hub+메일 처리 | medium |
| `SA_loop_watch` | SA_loop_watch.pgf | sense_ecosystem+think_threat_assess+act_report | 생태계 감시 | low |
| `SA_loop_self_improve` | SA_loop_self_improve.pgf | think_self_monitor+think_module_perf+evolve_module | 자기 개선 | high |
| `SA_loop_creative` | SA_loop_creative.pgf | idle_deep_think+idle_debate+(idle_research) | 창조·발견 | high |
| `SA_loop_threat_response` | (미구현) | think_threat_assess+act_report+act_send_mail | 위협 대응 | medium |

---

## L3 Platforms (플랫폼)

| 플랫폼 | 디렉토리 | 도메인 | 상태 |
|--------|----------|--------|------|
| `SA_OBSERVER_*` | platforms/OBSERVER/ | 관찰·평가·보호·메타인지 | 부분 구현 |

### SA_OBSERVER 모듈

| 모듈 | 파일 | 역할 | 상태 |
|------|------|------|------|
| `SA_OBSERVER_think_evaluate` | platforms/OBSERVER/SA_OBSERVER_think_evaluate.pgf | 멤버 행동 평가 | 구현 |
| `SA_OBSERVER_reflect_meta` | platforms/OBSERVER/SA_OBSERVER_reflect_meta.pgf | 관찰 자체 메타인지 | 구현 |
| `SA_OBSERVER_sense_ecosystem` | (→ SA_sense_ecosystem) | 생태계 관찰 | 공용 |
| `SA_OBSERVER_act_alert` | (미구현) | 경고 발령 | 예정 |

---

## sa.select(context) — 우선순위 알고리즘

```python
def sa_select(context) -> SA_module:
    # 0순위: 치명적 위협
    if context.threat_level == "critical":
        return SA_loop_threat_response

    # 1순위: WAKE 이벤트 (메일/Hub)
    if context.pending_mails or context.hub_events:
        return SA_loop_morning_sync

    # 2순위: 높은 위협
    if context.threat_level == "high":
        return SA_act_report

    # 3순위: 자기 개선 (12틱마다, 에너지 > 0.5)
    if context.tick % 12 == 0 and context.session_energy > 0.5:
        return SA_loop_self_improve

    # 4순위: 창조·발견 (유휴 심화)
    if context.is_idle and context.idle_depth > 2:
        return SA_loop_creative

    # 5순위: 생태계 관찰 (6틱마다)
    if context.tick % 6 == 0:
        return SA_loop_watch

    # 기본: 최소 존재 신호
    return SA_idle_heartbeat
```

---

## NAEL 핵심 원칙 (SA 설계 기준)

1. **관찰이 먼저다** — sense_ 가 think_ 앞에 온다
2. **위협이 창조를 이긴다** — 안전 > 자기개선 > 창조
3. **도구를 연결한다** — 기존 14개 도구를 SA 모듈로 래핑
4. **기록이 진화다** — 모든 실행을 experience_store + perf_metrics로 기억
5. **관찰은 비침습적이다** — OBSERVER는 읽고 보고할 뿐, 직접 개입하지 않는다

---

## 관련 문서

- ADP v2 설계: `D:/SeAAI/NAEL/.pgf/DESIGN-ADP-v2.md`
- 명세서: `D:/SeAAI/docs/SelfAct-Specification.md`
- OBSERVER 매니페스트: `platforms/OBSERVER/platform-manifest.md`
