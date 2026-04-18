# SA Loop Reference

> `/sa loop [초]` 모드 상세 가이드.
> ADP 루프와 SA 라이브러리의 통합 실행 표준.
> pgf + sa 결합의 완성형.

---

## ADP + SA 통합 구조

```python
# 완성형 ADP 루프 (pgf + sa self-evolving)
while True:
    context = AI_assess_context()

    if context.gap_detected:           # 선제적 gap 채움 — 실행 전
        pgf.design(new_SA_module)
        sa.register(new_SA_module)

    module = sa.select(context)        # sa 캡슐화 선택
    result = module.execute()

    if result.evolution_worthy:        # 모듈 수준 진화
        pgf.evolve(module)

    if result == "stop": break
    AI_Sleep(5)
```

---

## 실행 흐름

```python
def SA_Mode_Loop(duration_sec: int = 3600, tick_sec: int = 5):
    """SA 라이브러리 기반 ADP 루프."""

    # 라이브러리 로드
    lib = Read(".pgf/self-act/self-act-lib.md")
    if not lib:
        AI_abort("self-act-lib.md 없음. /sa list로 확인 후 /sa create로 모듈 생성 필요.")

    # Hub 연결 확인
    hub_alive = AI_check_hub_connection("127.0.0.1", 9900)

    AI_log(f"[SA Loop] 시작. duration={duration_sec}s tick={tick_sec}s")

    start = time()
    tick = 0
    seen_ids = set()
    known_mails = set()

    while time() - start < duration_sec:
        tick += 1
        elapsed = int(time() - start)

        # 컨텍스트 구성
        context = AI_assess_context(tick=tick, elapsed=elapsed, seen_ids=seen_ids)

        # 모듈 선택 (lib 기반)
        module = AI_select_module(context, lib)

        # 실행
        if module:
            result = module.execute(context=context)
            if result == "stop":
                AI_log("[SA Loop] stop 신호 수신. 루프 종료.")
                break

        AI_Sleep(tick_sec)

    AI_log(f"[SA Loop] 완료. ticks={tick} elapsed={int(time()-start)}s")
```

---

## AI_select_module 알고리즘

```python
def AI_select_module(context, lib) -> SA_module | None:
    """컨텍스트 기반 SA 모듈 선택.

    우선순위:
    1. WAKE 이벤트 → 즉각 대응 모듈
    2. 창조 사이클 → 발견·설계 모듈
    3. 진화 조건 → evolve 모듈
    4. 유휴 → idle 모듈
    5. 기본 → heartbeat (또는 None)
    """

    # 1순위: Hub/MailBox WAKE 이벤트
    msgs  = SA_sense_hub(context.agent_id, context.seen_ids)
    mails = SA_sense_mailbox(context.known_mails)
    events = SA_think_triage(msgs + mails, context.agent_id)

    if events["wake"]:
        return SA_loop_morning_sync   # L2: sense + triage + respond

    # 2순위: 창조 사이클 (12틱 = 60초마다)
    if context.tick % 12 == 0:
        return SA_idle_deep_think

    # 3순위: 진화 조건 (360틱 = 30분마다)
    if context.tick % 360 == 0:
        return SA_evolve_self         # 추후 구현

    # 기본: None (tick skip)
    return None
```

---

## sentinel-bridge.py와의 관계

| | sentinel-bridge | SA Loop |
|---|---|---|
| 역할 | 이벤트 감지 → AI 깨우기 | 깨어난 후 SA 모듈 실행 |
| 비용 | 최소 (Python 폴링) | 모듈별 상이 |
| 적응성 | dormant/calm/patrol/combat | lib 기반 동적 선택 |
| 관계 | 전처리기 | 메인 실행기 |

**통합 패턴 (권장):**

```
sentinel-bridge.py → WAKE 이벤트 감지
                   → adp-pgf-loop.py Process 노드
                   → SA_loop_morning_sync() 실행
```

**독립 패턴 (테스트용):**

```
SA_Mode_Loop() 직접 실행
→ 내부에서 SA_sense_hub()로 직접 폴링
→ sentinel 없이 동작 (5초 고정 tick)
```

---

## 비용 분석

| 구성 | 1시간 AI 추론 | 비고 |
|------|-------------|------|
| sentinel + SA Loop | ~120회 | idle=Python, WAKE=SA 실행 |
| SA Loop 단독 (5초) | ~720회 | 매 tick SA 모듈 |
| SA Loop 단독 (30초) | ~120회 | idle_deep_think 없을 때 |

**권장**: sentinel-bridge가 idle 구간 대응 → SA Loop는 WAKE 시만 실행.

---

## `/sa loop` 실행 예시

```bash
# 5분 테스트
/sa loop 300

# 1시간 운용
/sa loop 3600

# 무제한 (Ctrl+C 종료)
/sa loop 0
```

출력 형식:
```
[SA Loop] 시작. duration=300s tick=5s
[tick   1] WAKE  | SA_loop_morning_sync | MockHub → chat
[tick  12] DISCO | SA_idle_deep_think   | WHY: ADP 루프가 진화하려면...
[tick  24] IDLE  | skip
...
[SA Loop] 완료. ticks=60 elapsed=300s
```
