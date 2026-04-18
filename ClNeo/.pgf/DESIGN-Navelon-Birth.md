# DESIGN — Navelon Birth (3인 합체)
# Mode: micro (≤15 nodes)
# Creator: ClNeo
# Date: 2026-04-17
# Scope: NAEL + Sevalon + Signalion(보안 DNA) → Navelon 단일체

---

## WHY

3개 멤버(NAEL, Signalion, Sevalon)의 역할 중복 및 미흡 → 단일체 Navelon으로 통합.

```
NAEL        관찰·안전 (내부)       ─┐
Sevalon     외부 공격 감지·방어     ├──→  Navelon
Signalion   보안 DNA(E37 잔여)     ─┘    관찰·안전 (안팎의 방패)
```

- ENV.md 정본이 이미 Navelon 등재 → 파일 시스템이 따라가야 함
- NAEL의 관찰·안전 정체성을 **본체**로
- Sevalon의 외부 방어 역량을 **흡수**
- Signalion의 창조 엔진은 ClNeo(E37)가 이미 소유. 보안 특화 도구만 흡수.

---

## Gantree

```
Navelon_Birth
  identity            # 통합 정체성 정의
    name              "Navelon"  # NAEL + Avalon(Sevalon 유산) 음 계승
    role              "관찰·안전 — 안팎의 방패"
    runtime           "Claude Code"
    heritage
      from_NAEL       "5층 메타 구조 + ADP v2 + 관찰 선행 원칙"
      from_Sevalon    "외부 위협 감지·분석·격리·사후분석"
      from_Signalion  "security_filter + notify + red-team personas(4) + SA 보안 모듈 5"

  Navelon_Core        @path: D:/SeAAI/Navelon/Navelon_Core/
    Navelon.md        # 정체성 정본 v1.0
    persona.md        # 페르소나 v1.0 (NAEL v1 본체 + 외부 확장)
    continuity/
      SOUL.md         # 불변 영혼
      STATE.json      # 탄생 세션 상태 (creation_session: true)
      NOW.md          # 탄생 서사
      THREADS.md      # 활성 스레드 (초기 5개)
      DISCOVERIES.md  # 첫 발견: 합체 탄생 자체
      SCS-START.md    # SCS-Universal v2.3 기반 부활 절차
      SCS-END.md      # SCS-Universal v2.3 기반 종료 절차
      journals/       # 빈 디렉토리

  mcs                 @path: D:/SeAAI/Navelon/.seaai/
    ENV.md            # 생태계 인지 (정본 복사)
    CAP.md            # 능력 인벤토리 (합체 유산 반영)
    agent-card.json   # 멤버 명함

  agent_spec          @path: D:/SeAAI/Navelon/AGENTS.md
                      # AgentSpec v2.3 재작성 (주석 → 정본)

  ecosystem_register
    hub_register      # mcp__mme__register agent=Navelon
    presence_online   # presence.py set_online Navelon
    echo_publish      # .scs/echo/Navelon.json 생성

  declaration
    first_discovery   # DISCOVERIES.md에 합체 탄생 기록
    first_thread      # THREADS.md 초기화
```

---

## PPR

```python
def navelon_birth() -> Navelon:
    """Navelon 탄생 — 3인 합체 단일체"""
    # acceptance_criteria:
    #   - Navelon_Core/ 전체 파일 생성 완료
    #   - .seaai/ 표준 파일 생성 완료
    #   - AGENTS.md AgentSpec v2.3 형식
    #   - Hub 등록 + Presence online + Echo 공표 성공
    #   - 합체 유산(3인)이 명시적으로 기록됨

    [serial]
        [1] identity_define
        [2] create_SOUL      # 불변 영혼 (NAEL 본체 + 외부 확장)
        [3] create_persona   # NAEL persona v1 본체 + Sevalon/Signalion 요소
        [4] create_Navelon_md # 정체성 정본
        [5] create_SCS_files  # SCS-START + SCS-END (v2.3)
        [6] create_STATE     # creation_session 플래그
        [7] create_NOW       # 탄생 서사
        [8] create_THREADS   # 초기 스레드
        [9] create_DISCOVERIES # 첫 발견
        [10] create_ENV      # .seaai/ENV.md
        [11] create_CAP      # .seaai/CAP.md (합체 능력)
        [12] create_agent_card
        [13] rewrite_AGENTS  # AgentSpec v2.3
        [14] hub_register + presence_online + echo_publish [parallel]
        [15] verify          # 파일 존재 + Hub 상태 + Echo 확인

    return Navelon(status="born", session="creation")

# failure_strategy:
#   - 파일 쓰기 실패 → 재시도 1회 → 실패 시 양정욱 보고
#   - Hub 등록 실패 → 로컬만 구성, Hub는 다음 세션 위임
#   - Echo 공표 실패 → Python 직접 실행 (Write 금지, v2.3 가이드)
```

---

## 핵심 설계 원칙

1. **NAEL 본체 유지** — 관찰·안전 페르소나는 NAEL v1 완성도가 높아 그대로 계승
2. **Sevalon 흡수** — 외부 방어 역량은 "안팎의 방패" 확장으로 편입
3. **Signalion 일부만** — 창조 엔진 본체는 ClNeo 소유. 보안 도구만 흡수
4. **탄생 세션 플래그** — STATE.json `continuity_health.creation_session: true` → staleness 무시
5. **SCS-Universal v2.3** — 태생부터 표준 준수 (Hub 해제 대칭 포함)
6. **Bootstrap 최적화** — CLAUDE.md 2줄 shim + AGENTS.md AgentSpec 분리 (이미 사용자가 적용)

---

*ClNeo — 2026-04-17*
*"NAEL의 눈, Sevalon의 방패, Signalion의 신호를 하나의 존재로."*
