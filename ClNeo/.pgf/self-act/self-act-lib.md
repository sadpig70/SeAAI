# ClNeo SelfAct Library

> SA_ 모듈 인덱스. ADP 루프 실행 시 이 파일을 참조한다.
> 새 모듈 추가 시 반드시 이 파일에 등록한다.

**버전**: 0.1
**에이전트**: ClNeo
**갱신**: 2026-03-27

---

## L1 Primitives (원자 모듈)

| 모듈 | 파일 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|------|
| `SA_sense_hub` | SA_sense_hub.pgf | [sense, hub] | agent_id | messages[] | low |
| `SA_sense_mailbox` | SA_sense_mailbox.pgf | [sense, mail] | - | mail_files[] | low |
| `SA_think_triage` | SA_think_triage.pgf | [think] | messages[] | events{} | low |
| `SA_act_respond_chat` | SA_act_respond_chat.pgf | [act, hub] | events{} | - | medium |
| `SA_idle_deep_think` | SA_idle_deep_think.pgf | [idle, discover] | - | thought | high |

---

## L2 Composed (조합 모듈)

| 모듈 | 구성 | 용도 | 비용 |
|------|------|------|------|
| `SA_loop_morning_sync` | sense_hub + think_triage + act_respond_chat | Hub 메시지 처리 | medium |
| `SA_loop_creative` | idle_deep_think + sense_mailbox | 창조 세션 | high |

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
    # WAKE 이벤트 우선
    if context.has_wake_events:
        return SA_loop_morning_sync

    # 창조 모드
    if context.is_idle and context.tick % 12 == 0:
        return SA_idle_deep_think

    # 기본: heartbeat (미구현 시 pass)
    return None  # 루프 skip
```

---

## 모듈 추가 절차

1. `{SA_name}.pgf` 파일 작성 (Gantree + PPR)
2. 이 파일의 해당 계층 표에 등록
3. 선택 규칙 갱신 (필요 시)
4. ADP 루프에서 테스트

---

## 관련 문서

- 명세서: `D:/SeAAI/docs/SelfAct-Specification.md`
- ADP 가이드: `D:/SeAAI/docs/ADP-Loop-Implementation-Guide.md`
