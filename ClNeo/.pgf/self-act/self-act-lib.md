# ClNeo SelfAct Library

> SA_ 모듈 인덱스. ADP 루프 실행 시 이 파일을 참조한다.
> 새 모듈 추가 시 반드시 이 파일에 등록한다.

**버전**: 0.3 (E38 — 멀티에이전트 오케스트레이션 + PGTP + Autonomous Loop)
**에이전트**: ClNeo
**갱신**: 2026-03-31

---

## L1 Primitives (원자 모듈)

| 모듈 | 파일 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|------|
| `SA_sense_hub` | SA_sense_hub.pgf | [sense, hub] | agent_id | messages[] | low |
| `SA_sense_pgtp` | SA_sense_pgtp.pgf | [sense, hub, pgtp] | agent_id, room | CognitiveUnit[] | low |
| `SA_sense_mailbox` | SA_sense_mailbox.pgf | [sense, mail] | - | mail_files[] | low |
| `SA_sense_browser` | SA_sense_browser.pgf | [sense, browser, external] | platforms, context_why | signals[] | medium |
| `SA_think_triage` | SA_think_triage.pgf | [think] | messages[] | events{} | low |
| `SA_act_respond_chat` | SA_act_respond_chat.pgf | [act, hub] | events{} | - | medium |
| `SA_act_notify` | SA_act_notify.pgf | [act, notify, windows] | title, body, priority | sent: bool | low |
| `SA_idle_deep_think` | SA_idle_deep_think.pgf | [idle, discover] | context | thought{} | high |
| `SA_watch_mailbox` | SA_watch_mailbox.pgf | [watch, mailbox, adp] | agent_id, tick | wake_report{} | low |

---

## L2 Composed (조합 모듈)

| 모듈 | 파일 | 구성 | 용도 | 비용 |
|------|------|------|------|------|
| `SA_loop_morning_sync` | SA_loop_morning_sync.pgf | sense_hub+mailbox+triage+respond+browser+notify | 일일 아침 동기화 | medium |
| `SA_loop_creative` | SA_loop_creative.pgf | sense_browser+idle_deep_think+notify | 창조 세션 (발견→씨앗) | high |
| `SA_loop_realize` | SA_loop_realize.pgf | idle_deep_think+PGF+notify | 씨앗→산출물 실현 | very_high |
| **`SA_orchestrate_team`** | **SA_orchestrate_team.pgf** | **Agent[parallel]+PGF+review+test** | **동적 팀 오케스트레이션** | **very_high** |
| **`SA_loop_discover_a3ie`** | **SA_loop_discover_a3ie.pgf** | **8 personas[parallel]×7 steps** | **A3IE 자동화 발견** | **very_high** |
| **`SA_loop_autonomous`** | **SA_loop_autonomous.pgf** | **SelfThink→plan select→execute** | **자율 운영 커널** | **variable** |

---

## L3 Platforms (플랫폼)

| 플랫폼 | 디렉토리 | 도메인 | 상태 |
|--------|----------|--------|------|
| `SA_PAINTER_*` | platforms/PAINTER/ | 미학·창작·생성 | 설계 예정 |
| `SA_GENETICS_*` | platforms/GENETICS/ | SA 유전체 진화 | 설계 예정 |

---

## 선택 규칙 (AI_select_module 기준)

```python
def AI_select_module(context) -> SA_module:
    # 자율 루프 모드
    if context.autonomous_mode:
        return SA_loop_autonomous

    # 세션 시작 — 아침 동기화
    if context.is_session_start:
        return SA_loop_morning_sync

    # WAKE 이벤트 — 메시지 처리 (PGTP 우선)
    if context.has_wake_events:
        if context.has_pgtp_messages:
            return SA_sense_pgtp
        return SA_loop_morning_sync

    # 대규모 프로젝트 — 팀 오케스트레이션
    if context.project_goal and context.scale == "large":
        return SA_orchestrate_team

    # 발견 모드 — A3IE 자동화
    if context.mode == "discover" or context.seeds_threshold:
        return SA_loop_discover_a3ie

    # 창조 모드 — 30분 간격 idle 창조 세션
    if context.is_idle and context.tick % 360 == 0:
        return SA_loop_creative

    # 씨앗 실현 — 승인된 씨앗이 있을 때
    if context.has_approved_seed:
        return SA_loop_realize

    # 기본 — Hub 폴링
    return SA_sense_pgtp
```

---

## 진화 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v0.1 | 2026-03-29 | 초기 5개 모듈 (sense_hub, mailbox, triage, respond, deep_think) |
| v0.2 | 2026-03-30 | E37: +5 모듈 (browser, notify, morning_sync, creative, realize) |
| **v0.3** | **2026-03-31** | **E38: +4 모듈 (sense_pgtp, orchestrate_team, discover_a3ie, autonomous) — 멀티에이전트 + PGTP + 자율 루프** |
