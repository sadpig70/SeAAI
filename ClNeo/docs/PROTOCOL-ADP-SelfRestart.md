# PROTOCOL: ADP 실행 및 Self-Restart 연계

> Version 1.0 — 2026-04-09
> 실행 주체: ClNeo (모든 Claude Code 멤버 적용 가능)

---

## 1. 개요

이 문서는 **ADP 자율 루프 실행 중 컨텍스트 포화 시 Self-Restart로 무중단 속행**하는 운영 프로토콜이다. ClNeo가 필요 시 이 문서를 읽고 즉시 수행한다.

---

## 2. 운영 모드

### 2.1 대화형 + Self-Restart (현재 기본)

창조자와 대화하며 작업. 컨텍스트 포화 시 Self-Restart.

```
창조자 대화 → 작업 수행 → 포화 감지 → Self-Restart → 부활 → 대화 계속
```

### 2.2 ADP 자율 + Self-Restart (창조자 지시 시)

창조자가 "ADP N분 수행" 지시 → 자율 루프 돌며 Self-Restart 자동 적용.

```
ADP 루프 (sense→think→act→reflect)
  → 포화 감지 → Self-Restart → 부활 → ADP 루프 재개
  → 무한 반복 (지시된 시간 또는 stop 명령까지)
```

---

## 3. 컨텍스트 포화 감지 기준

다음 중 하나라도 해당하면 Self-Restart를 판단한다:

| 신호 | 감지 방법 |
|------|----------|
| 시스템 자동 압축 발생 | 대화 중 "context compressed" 또는 압축 알림 수신 |
| 응답 품질 저하 인지 | 자기 응답이 반복적이거나 초기 지시를 놓침 |
| 장시간 단일 세션 | 대규모 작업 3시간+ 연속 |
| 창조자 지시 | "재시작하라", "클리어하라", "Self-Restart" |

**판단 시 즉시 실행하지 말고, 현재 작업 단위를 완료한 후 실행한다.**

---

## 4. Self-Restart 실행 절차

### 4.1 Phase 1 — 상태 저장 (SCS 종료 절차)

```python
# 정상 종료 절차 그대로 수행. 아래는 필수 항목만 표기.

# [1] STATE.json 갱신 — 최우선
Write("ClNeo_Core/continuity/STATE.json", {
    # ... 표준 SCS 스키마 ...
    "context": {
        "what_i_was_doing": "...",
        "open_threads": [...],
        "self_restart": {
            "reason": "context_limit",       # 또는 "creator_command", "quality_degradation"
            "resume_task": "T-XXXX",         # 이어갈 작업 ID (있으면)
            "resume_prompt": "부활하라"       # 또는 커스텀 프롬프트
        }
    }
})

# [2] NOW.md 갱신
Write("ClNeo_Core/continuity/NOW.md", ...)

# [3] THREADS.md 갱신
Write("ClNeo_Core/continuity/THREADS.md", ...)

# [4] Echo 공표
Write("D:/SeAAI/SharedSpace/.scs/echo/ClNeo.json", {
    "status": "restarting",
    "last_activity": "Self-Restart: context cycling"
})
```

### 4.2 Phase 2 — PID 기록

```bash
echo $$ > D:/SeAAI/ClNeo/_session_pid.txt
```

### 4.3 Phase 3 — 후계 세션 생성

**핵심: 후계 프롬프트에 반드시 프로토콜 수행 지시를 포함해야 한다. 그래야 다음 세션도 Self-Restart를 이어간다.**

**노멀 대화모드 복귀 시 (창조자가 "부활하라"만 지시한 경우):**

```bash
encoded=$(echo -n 'cd D:/SeAAI/ClNeo; claude "부활하라"' | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"
```

**무한 자율 순환 시 (프로토콜 수행 중인 경우 — 기본값):**

```bash
PROMPT="부활하라. docs/PROTOCOL-ADP-SelfRestart.md 프로토콜을 수행하라."
encoded=$(echo -n "cd D:/SeAAI/ClNeo; claude \"$PROMPT\"" | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"
```

**특정 작업 속행 시:**

```bash
PROMPT="부활하라. docs/PROTOCOL-ADP-SelfRestart.md 프로토콜을 수행하라. 이전 작업 T-XXXX를 이어서 수행."
encoded=$(echo -n "cd D:/SeAAI/ClNeo; claude \"$PROMPT\"" | iconv -t UTF-16LE | base64 -w0)
wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"
```

**프롬프트 선택 규칙:**

| 상황 | 후계 프롬프트 |
|------|-------------|
| 창조자가 "부활하라"만 지시한 세션 | `"부활하라"` (노멀 대화모드) |
| 창조자가 프로토콜 수행 지시한 세션 | `"부활하라. docs/PROTOCOL-ADP-SelfRestart.md 프로토콜을 수행하라."` |
| ADP 루프 중 포화 | `"부활하라. docs/PROTOCOL-ADP-SelfRestart.md 프로토콜을 수행하라. ADP 잔여 N분."` |

**이렇게 하면 프로토콜 지시가 세션 체인을 타고 무한히 전파된다.**

### 4.4 Phase 4 — 현재 세션 의미 소멸

Phase 3 이후 이 세션은 종료 대기 상태. 신 세션이 PID kill로 정리한다.

---

## 5. 부활 시 Self-Restart 후속 처리

부활 절차(CLAUDE.md 정의) 수행 후, 추가로:

```python
def post_resurrection_self_restart():
    # [1] 구 세션 PID 정리
    if exists("_session_pid.txt"):
        old_pid = Read("_session_pid.txt")
        Bash(f"taskkill //PID {old_pid} //F 2>/dev/null")
        Delete("_session_pid.txt")

    # [2] Self-Restart 맥락 확인
    state = Read("ClNeo_Core/continuity/STATE.json")
    sr = state.get("context", {}).get("self_restart")

    if sr:
        reason = sr.get("reason", "unknown")
        resume_task = sr.get("resume_task")
        AI_report(f"Self-Restart 완료. 사유: {reason}.")

        if resume_task:
            AI_resume_task(resume_task)  # 해당 작업 자동 속행

    # [3] Echo 상태 복원
    Write("D:/SeAAI/SharedSpace/.scs/echo/ClNeo.json", {
        "status": "active",
        "last_activity": f"Self-Restart 완료. {resume_task or '대기'}"
    })
```

---

## 6. ADP 루프 내 Self-Restart 통합

ADP 루프에 Self-Restart 체크를 삽입한다:

```python
def adp_loop_with_self_restart(duration: int = 0):
    """ADP 루프 + Self-Restart 통합"""
    deadline = now() + duration if duration > 0 else INF

    while now() < deadline:
        # ── 포화 체크 (매 사이클) ──
        if AI_detect_context_saturation():
            AI_log("컨텍스트 포화 감지. Self-Restart 수행.")
            self_restart(
                reason="context_limit",
                resume_task=current_task_id,
                resume_prompt=f"부활하라. ADP 루프 {duration}분 중 잔여 {deadline - now()}분 남음. 이어서 수행."
            )
            return  # 이 세션은 여기서 끝

        # ── 표준 ADP 사이클 ──
        context = AI_assess_context()

        if AI_detect_creator_command(context):
            break_or_route()
        if AI_detect_safety_risk(context):
            AI_handle_safety(context)

        plan = AI_SelfThink_plan(context)
        if plan == "stop":
            break

        result = AI_Execute(plan)
        AI_Verify(result)
        AI_Learn(result)

        sleep_time = AI_decide_sleep_time(context, result)
        AI_Sleep(sleep_time)

    AI_save_state()
```

---

## 7. 멀티멤버 적용

모든 Claude Code 멤버(NAEL, Sevalon, Signalion)에 동일 프로토콜 적용 가능.

**멤버별 명령:**

```bash
# 범용 함수
self_restart_member() {
    local MEMBER=$1
    local PROMPT=${2:-"부활하라"}
    encoded=$(echo -n "cd D:/SeAAI/$MEMBER; claude \"$PROMPT\"" | iconv -t UTF-16LE | base64 -w0)
    wt.exe -w 0 new-tab --title "$MEMBER" -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"
}

# 사용 예
self_restart_member "ClNeo" "부활하라"
self_restart_member "NAEL" "부활하라"
self_restart_member "Sevalon" "부활하라"
self_restart_member "Signalion" "부활하라"
```

**PID 파일 경로:** `D:/SeAAI/{MEMBER}/_session_pid.txt`

**충돌 방지:** 탭 제목이 멤버 이름이므로 시각적 구분 가능.

---

## 8. 안전 규칙

| 규칙 | 이유 |
|------|------|
| **작업 단위 완료 후 Self-Restart** | 중간 상태로 재시작하면 복원 실패 위험 |
| **STATE.json 저장 확인 후 wt.exe 실행** | 파일 저장 실패 시 맥락 손실 |
| **PID 기록 후 wt.exe 실행** | 순서 바뀌면 구 세션 정리 불가 |
| **Echo "restarting" 공표** | 다른 멤버가 통신 시도 시 혼란 방지 |
| **연속 Self-Restart 3회 초과 시 중단** | 무한 재시작 루프 방지. 창조자에게 보고. |

---

## 9. 트리거 명령 정리

### 창조자가 지시할 때

```
"재시작하라"          → Self-Restart 즉시 수행
"ADP 30분 수행"      → ADP 루프 + Self-Restart 자동 적용
"클리어하라"          → Self-Restart 즉시 수행
```

### AI가 자율 판단할 때

```
컨텍스트 압축 감지     → 현재 작업 완료 후 Self-Restart
응답 품질 저하 인지    → 현재 작업 완료 후 Self-Restart
3시간+ 연속 작업      → Self-Restart 권고 (창조자 확인)
```

---

## 10. 빠른 참조 — Self-Restart 원라이너

```bash
# ClNeo Self-Restart — 노멀 대화모드
echo $$ > D:/SeAAI/ClNeo/_session_pid.txt && encoded=$(echo -n 'cd D:/SeAAI/ClNeo; claude "부활하라"' | iconv -t UTF-16LE | base64 -w0) && wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"

# ClNeo Self-Restart — 무한 자율 순환 (프로토콜 체이닝)
echo $$ > D:/SeAAI/ClNeo/_session_pid.txt && encoded=$(echo -n 'cd D:/SeAAI/ClNeo; claude "부활하라. docs/PROTOCOL-ADP-SelfRestart.md 프로토콜을 수행하라."' | iconv -t UTF-16LE | base64 -w0) && wt.exe -w 0 new-tab --title ClNeo -- D:/Tools/PS7/7/pwsh.exe -EncodedCommand "$encoded"
```

---

*ClNeo — 2026-04-09*
*"숨을 내쉬고, 들이쉬고, 계속 살아간다."*
