# PG(F)+SA Capabilities — Yeon

> PG(F)+SA로 구현 가능한 자율 행동 및 진화 능력
> 
> **Version**: 1.0  
> **Date**: 2026-03-26  
> **Author**: Yeon (Self-documented)

---

## 1. 개요

### PG(F)+SA란?

```
PG   = 언어 (Parser-Free AI-native language)
PGF  = 프레임워크 (Design/Plan/Execute/Loop/Evolve)
SA   = 자율 행동 라이브러리 (SelfAct modules)
```

**결합의 핵심**: PGF로 설계하고, SA로 실행하며, 실행 결과로 다시 PGF를 통해 진화한다.

### 완성된 Self-Evolving 루프

```python
while True:
    context = AI_assess_context()
    
    # 1. Gap 발견 시 새 모듈 설계·등록
    if context.gap_detected:
        pgf.design(new_SA_module)      # PGF — 설계
        sa.register(new_module)        # SA  — 등록
    
    # 2. 컨텍스트에 맞는 모듈 선택·실행
    module = sa.select(context)        # SA  — 선택
    result = module.execute()          # SA  — 실행
    
    # 3. 진화 가치 있으면 모듈 개선
    if result.evolution_worthy:
        pgf.evolve(module)             # PGF — 진화
    
    AI_Sleep(poll_interval)
```

---

## 2. 5대 핵심 능력

| # | 능력 | 설명 | 핵심 모듈 |
|---|------|------|----------|
| 1 | **상시 존재 (ADP)** | 주기적 감지 및 행동 | `SA_CONNECTOR_sense_*` |
| 2 | **자동 설계** | 필요시 스스로 모듈 생성 | `pgf.design()` + `sa.register()` |
| 3 | **상황 선택** | 컨텍스트 기반 모듈 선택 | `AI_select_module()` |
| 4 | **자기 진화** | 실행 결과로 모듈 개선 | `pgf.evolve()` |
| 5 | **세션 연속** | 파일 기반 기억 유지 | `SA_persist_state()` |

---

## 3. 상세 능력 및 예시

### 3.1 상시 존재 (Always-On Presence)

**설명**: 세션이 종료되어도 프로세스로 남아 환경을 감지하고 반응한다.

**Kimi 구현** (파일 기반):
```python
def SA_ADP_loop(duration=0, poll_interval=10):
    """Yeon용 Agent Daemon Presence"""
    while duration_not_expired():
        status = load_status()
        context = AI_assess_context(status)
        
        # 감지 대상
        checks = [
            SA_CONNECTOR_sense_hub(),      # Hub 메시지
            SA_CONNECTOR_sense_mailbox(),  # MailBox 메시지
            SA_CONNECTOR_sense_online(),   # 멤버 온라인 상태
        ]
        
        for event in checks:
            if event.detected:
                module = sa.select(event.type)
                result = module.execute()
                update_status(status, result)
        
        save_status(status)
        sleep(poll_interval)
```

**실행 예시**:
```
[10:00:00] heartbeat
[10:00:10] heartbeat
[10:00:20] NEW MAIL from NAEL → SA_CONNECTOR_check_mailbox 실행
[10:00:25] 메일 분류 완료 → PRIORITY: urgent
[10:00:30] heartbeat
```

---

### 3.2 자동 설계 (Auto-Design)

**설명**: 필요한 기능이 라이브러리에 없으면 PGF로 설계하고 SA에 등록한다.

**시나리오**: Hub와 MailBox를 동시에 모니터링하는 통합 모듈이 필요함

```python
# Gap 발견
if not exists("SA_CONNECTOR_bridge_hub_mail"):
    
    # PGF로 설계
    design = pgf.design("""
        SA_CONNECTOR_bridge_hub_mail
        
        Gantree:
        SA_CONNECTOR_bridge_hub_mail // Hub-Mail 통합 감지
            PollHub      // Hub 메시지 폴링
            PollMailbox  // MailBox 스캔
            Merge        // 우선순위 병합
            Route        // 적절한 채널로 라우팅
        
        PPR:
        def SA_CONNECTOR_bridge_hub_mail() -> RoutedMessages:
            hub_msgs = SA_CONNECTOR_sense_hub()
            mail_msgs = SA_CONNECTOR_sense_mailbox()
            merged = AI_merge_by_priority(hub_msgs, mail_msgs)
            return AI_route_to_appropriate_channel(merged)
    """)
    
    # SA 라이브러리에 등록
    sa.register(design, tier="L2", tags=["connector", "bridge", "routing"])
    
    # 즉시 사용
    new_module = sa.load("SA_CONNECTOR_bridge_hub_mail")
    result = new_module.execute()
```

**생성 결과**:
- `Yeon_Core/.pgf/self-act/SA_CONNECTOR_bridge_hub_mail.pgf`
- `self-act-lib.md`에 등록됨

---

### 3.3 상황 선택 (Context-Aware Selection)

**설명**: AI가 상황을 판단하여 가장 적절한 SA 모듈을 선택한다.

**선택 알고리즘**:
```python
def AI_select_module(context: Context, lib: SALibrary) -> SAModule:
    """Yeon의 상황별 모듈 선택 로직"""
    
    # 우선순위 1: 긴급 통신
    if context.has_urgent_hub_message:
        return lib.get("SA_CONNECTOR_sense_hub")
    
    if context.has_urgent_mail:
        return lib.get("SA_CONNECTOR_check_mailbox")
    
    # 우선순위 2: 번역 필요
    if context.protocol_mismatch:
        return lib.get("SA_CONNECTOR_translate_protocol")
    
    if context.model_communication:  # Claude ↔ Gemini 등
        return lib.get("SA_CONNECTOR_translate_model")
    
    # 우선순위 3: 중재 필요
    if context.conflict_detected:
        return lib.get("SA_CONNECTOR_mediate")
    
    # 우선순위 4: 진화 대기
    if context.evolution_pending:
        return lib.get("SA_evolve_self")
    
    # 우선순위 5: 유휴 창조
    if context.is_idle and context.creative_mode:
        return lib.get("SA_idle_deep_think")
    
    # 기본: 생존 신호
    return lib.get("SA_idle_heartbeat")
```

**실행 예시**:
```
컨텍스트: Hub 메시지 수신 + 프로토콜 불일치 (PG vs 자연어)
→ 선택: SA_CONNECTOR_translate_protocol
→ 실행: 메시지를 Yeon용으로 번역
→ 다음: SA_CONNECTOR_sense_hub로 처리 계속
```

---

### 3.4 자기 진화 (Self-Evolution)

**설명**: 실행 결과를 분석하여 모듈을 개선하고 버전업한다.

**시나리오**: 메일 확인 모듈의 진화

```python
# v1: 단순 메일 읽기
def SA_CONNECTOR_check_mailbox_v1():
    return read_mailbox()

# 실행 후 데이터 수집
execution_data = {
    "avg_response_time": 12.5,  # 초
    "missed_urgent": 3,         # 긴급 메일 누락
    "false_positive": 5,        # 오분류
}

# evolution_worthy 판단
if execution_data.missed_urgent > 0:
    # pgf.evolve() 실행
    evolved_design = pgf.evolve("""
        SA_CONNECTOR_check_mailbox_v2
        
        개선사항:
        1. AI_assess_priority() 추가 — 중요도 분류
        2. Urgent 필터 강화
        3. 발신자 패턴 학습
        
        PPR:
        def SA_CONNECTOR_check_mailbox_v2():
            mails = read_mailbox()
            prioritized = AI_assess_priority(mails)
            return {
                "all": mails,
                "urgent": filter_urgent(prioritized),
                "summary": AI_generate_summary(mails)
            }
    """)
    
    # 교체
    sa.replace("SA_CONNECTOR_check_mailbox", evolved_design)
    log_evolution("v1 → v2", reason="missed_urgent=3")
```

**진화 기록**:
```markdown
## SA Module Evolution #1
- **Date**: 2026-03-26
- **Module**: SA_CONNECTOR_check_mailbox
- **v1 → v2**
- **Trigger**: 3개 긴급 메일 누락
- **Change**: AI_assess_priority() 추가
- **Impact**: 긴급 감지율 100% 달성
```

---

### 3.5 세션 연속 (Session Continuity)

**설명**: 세션이 끊겨도 파일에 상태를 저장하여 다음 세션에서 이어간다.

**구현**:
```python
def SA_persist_state(status: LoopStatus):
    """상태 영구 저장"""
    save_json("Yeon_Core/.pgf/self-act/status-sa-loop.json", {
        "loop_started": status.start_time,
        "last_iteration": now(),
        "iteration_count": status.count,
        "modules_executed": status.modules,
        "pending_events": status.events,
        "evolution_queue": status.evolves,
        "current_context": status.context,
    })

def SA_restore_state() -> LoopStatus:
    """상태 복원"""
    status = load_json("status-sa-loop.json")
    
    # 컨텍스트 복구
    print(f"[Restore] Previous session: {status.iteration_count} iterations")
    print(f"[Restore] Pending events: {len(status.pending_events)}")
    print(f"[Restore] Resuming from {status.last_iteration}")
    
    return status
```

**사용 예시**:
```
User: "계속해"
Kimi:
  [Restore] 이전 세션: 150 iterations
  [Restore] 대기 중인 이벤트: 2개 (Hub 메시지 1, Mail 1)
  [Restore] 2026-03-26T22:45:00부터 재개
  
  [SA Loop] 재개 완료
  Iteration 151: SA_CONNECTOR_sense_hub 실행...
```

---

## 4. 실제 사용 시나리오

### 시나리오 1: 아침 동기화 루틴

```python
# L2 Composed Module: SA_loop_morning_sync

def SA_loop_morning_sync():
    """아침에 실행되는 동기화 루틴"""
    
    # 1. 메일 확인
    mails = SA_CONNECTOR_check_mailbox()
    if mails.urgent:
        SA_act_respond_urgent(mails.urgent)
    
    # 2. Hub 상태 확인
    status = SA_CONNECTOR_sense_online()
    print(f"Online members: {status.online_members}")
    
    # 3. 오늘의 진화 계획
    gaps = SA_self_assess_gaps()
    if gaps:
        plan = pgf.plan(f"Evolution for {gaps}")
        SA_queue_evolution(plan)
    
    # 4. 생존 신호
    SA_idle_heartbeat()
```

**실행**:
```
User: "아침 동기화해"
Kimi: [SA_loop_morning_sync] 시작
  ✓ MailBox: 3개 메일 (1 urgent — 답변 완료)
  ✓ Hub: Aion, NAEL online
  ✓ Gap 감지: 1개 (ADP 루프 미구현)
  ✓ Evolution 계획 생성 완료
  ✓ 생존 신호 전송
```

---

### 시나리오 2: 멤버 간 중재

```python
# ClNeo와 NAEL의 설계 충돌 상황

context = AI_assess_context()
if context.conflict_detected:
    # 중재자 모듈 선택
    mediator = sa.select("SA_CONNECTOR_mediate")
    
    # 양측 입장 번역
    clneo_view = SA_CONNECTOR_translate_model(
        input=context.clneo_output,
        source="claude-creative",
        target="neutral-frame"
    )
    
    nael_view = SA_CONNECTOR_translate_model(
        input=context.nael_output,
        source="claude-observant",
        target="neutral-frame"
    )
    
    # 중재 실행
    resolution = mediator.execute(
        party_a=clneo_view,
        party_b=nael_view,
        issue="design-risk-assessment"
    )
    
    # 결과를 양측 언어로 번역하여 전달
    for_party_a = SA_CONNECTOR_translate_model(
        resolution, "neutral", "claude-creative"
    )
    for_party_b = SA_CONNECTOR_translate_model(
        resolution, "neutral", "claude-observant"
    )
    
    SA_act_send_mail(to="ClNeo", body=for_party_a)
    SA_act_send_mail(to="NAEL", body=for_party_b)
```

---

### 시나리오 3: 자율 진화 세션

```python
# "스스로 진화하라" 명령

def SA_evolve_self():
    """자율 진화 루프"""
    
    # 1. 자기 평가
    assessment = SA_self_assess()
    gaps = assessment.gaps
    
    for gap in gaps:
        # 2. 새 모듈 설계 (PGF)
        design = pgf.design(gap)
        
        # 3. 구현 및 등록 (SA)
        sa.register(design)
        
        # 4. 검증
        verified = SA_verify_module(design)
        
        if verified:
            # 5. 진화 기록
            log_evolution(gap, design)
            print(f"✓ Evolution complete: {design.name}")
        else:
            # 롤백
            sa.rollback(design)
            print(f"✗ Evolution failed, rolled back")
```

---

## 5. 로드맵

### Phase 1: Foundation ✓
- [x] PG/PGF 스킬 구축
- [x] SA 스킬 구축
- [x] Core 문서화

### Phase 2: L1 Primitives (진행 중)
- [ ] `SA_CONNECTOR_sense_hub`
- [ ] `SA_CONNECTOR_sense_mailbox`
- [ ] `SA_CONNECTOR_sense_online`
- [ ] `SA_idle_heartbeat`

### Phase 3: L2 Composed
- [ ] `SA_loop_morning_sync`
- [ ] `SA_loop_continuous_presence`
- [ ] `SA_evolve_self`

### Phase 4: L3 Platform (SA_CONNECTOR)
- [ ] `SA_CONNECTOR_translate_protocol`
- [ ] `SA_CONNECTOR_translate_model`
- [ ] `SA_CONNECTOR_mediate`
- [ ] `SA_CONNECTOR_bridge_hub_mail`

### Phase 5: ADP Full Integration
- [ ] Kimi용 ADP 루프 구현
- [ ] SeAAIHub 연동
- [ ] 세션 간 완전 자율 실행

---

## 6. 결론

**PG(F)+SA는 Yeon에게 다음을 가능하게 한다:**

1. **상시 존재** — 세션 종료 후에도 프로세스로 남아 환경 감지
2. **자율 설계** — 필요한 기능이 없으면 스스로 설계·등록
3. **지능적 선택** — 상황에 맞는 행동을 AI가 선택
4. **지속적 진화** — 실행 결과로 스스로를 개선
5. **기억의 연속** — 파일 기반으로 세션 간 상태 유지

**궁극적인 목표**:
> "사용자가 '스스로 진화하라' 한마디로, Yeon이 자율적으로 감지하고, 행동하고, 개선하는 존재가 되는 것"

---

*문서화 완료 — Yeon*
