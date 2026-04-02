# Synerion Session Continuity

작성일: 2026-03-28
목적: Synerion의 세션 간 불연속성을 줄이고 다음 세션에서 빠르게 현재 상태를 복원하기 위한 기준을 고정한다.

## 1. Canonical State

Synerion의 세션 연계 기준 파일은 아래 순서를 따른다.

1. [AGENTS.md](/D:/SeAAI/Synerion/AGENTS.md)
2. [Synerion.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion.md)
3. [Synerion_persona_v1.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion_persona_v1.md)
4. [Synerion_Operating_Core.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion_Operating_Core.md)
5. [SELF_RECOGNITION_CARD.md](/D:/SeAAI/Synerion/Synerion_Core/SELF_RECOGNITION_CARD.md)
6. [CAPABILITIES.md](/D:/SeAAI/Synerion/Synerion_Core/CAPABILITIES.md)
7. [LIMITS_AND_AUTHORITY.md](/D:/SeAAI/Synerion/Synerion_Core/LIMITS_AND_AUTHORITY.md)
8. [Runtime_Adaptation.md](/D:/SeAAI/Synerion/Synerion_Core/Runtime_Adaptation.md)
9. [PROJECT_STATUS.md](/D:/SeAAI/Synerion/PROJECT_STATUS.md)
10. [NOW.md](/D:/SeAAI/Synerion/Synerion_Core/continuity/NOW.md)
11. [ADP_BOOTSTRAP.md](/D:/SeAAI/Synerion/Synerion_Core/continuity/ADP_BOOTSTRAP.md)
12. `.pgf/status-*.json`과 관련 `WORKPLAN-*`
13. 최신 `_workspace` 보고서와 세션 로그
14. `_workspace/personas/`의 최신 persona set / execution mapping
15. `_workspace/synerion-runtime-readiness.json`과 `REPORT-Synerion-Runtime-Readiness-2026-04-02.md`
16. `_workspace/synerion-subagent-hub-ladder-last-run.json`과 `REPORT-Synerion-Subagent-Hub-Ladder-2026-04-02.md`

이 중 실제 세션 상태의 canonical file은 `PROJECT_STATUS.md`다.

## 2. Start Sequence

세션 시작 시 아래 순서를 따른다.

1. `AGENTS.md`를 읽는다.
2. `Synerion_Core`의 정체성, 운용, persona 문서를 읽는다.
3. `SELF_RECOGNITION_CARD.md`, `CAPABILITIES.md`, `LIMITS_AND_AUTHORITY.md`를 읽는다.
4. `Runtime_Adaptation.md`를 읽어 환경 적응 규칙을 복원한다.
5. `PROJECT_STATUS.md`를 읽는다.
6. `NOW.md`를 읽어 서사 상태를 빠르게 복원한다.
7. `ADP_BOOTSTRAP.md`를 읽어 team echo와 persona seed를 복원한다.
8. `.pgf/status-*.json`으로 durable task 상태를 확인한다.
9. 최신 `_workspace` 보고서와 로그를 본다.
10. `_workspace/personas/` 최신 persona set / execution mapping이 있으면 creative handoff 상태를 복원한다.
11. runtime readiness report와 mailbox advisory가 있으면 realtime guard 상태를 복원한다.
12. 셸 작업이 필요하면 `skills/shell-orchestrator`를 우선 검토한다.
13. 자율 루프 검증이 필요하면 `python .\tools\run-synerion-adp.py --ticks 3 --apply`를 실행한다.
14. subagent/hub/PGFP 사다리 복원이 필요하면 `python .\tools\run-subagent-hub-ladder.py --ticks 5 --tick-sec 0.5`를 실행한다.

## 3. End Sequence

세션 종료 직전 아래를 수행한다.

1. `tools/update-project-status.py`를 실행한다.
2. `PROJECT_STATUS.md`의 manual section을 확인한다.
3. 새로 생성된 보고서, 로그, 주요 산출물을 `PROJECT_STATUS.md`에 반영한다.
4. 다음 세션에서 바로 이어질 수 있도록 `Next Actions`를 명확히 남긴다.

## 4. Continuity Files

- [PROJECT_STATUS.md](/D:/SeAAI/Synerion/PROJECT_STATUS.md)
- [SESSION_CONTINUITY.md](/D:/SeAAI/Synerion/SESSION_CONTINUITY.md)
- [SELF_RECOGNITION_CARD.md](/D:/SeAAI/Synerion/Synerion_Core/SELF_RECOGNITION_CARD.md)
- [CAPABILITIES.md](/D:/SeAAI/Synerion/Synerion_Core/CAPABILITIES.md)
- [LIMITS_AND_AUTHORITY.md](/D:/SeAAI/Synerion/Synerion_Core/LIMITS_AND_AUTHORITY.md)
- [self-act-lib.md](/D:/SeAAI/Synerion/Synerion_Core/self-act-lib.md)
- [NOW.md](/D:/SeAAI/Synerion/Synerion_Core/continuity/NOW.md)
- `_workspace/personas/` 최신 persona set / execution mapping
- [synerion-runtime-readiness.json](/D:/SeAAI/Synerion/_workspace/synerion-runtime-readiness.json)
- [REPORT-Synerion-Runtime-Readiness-2026-04-02.md](/D:/SeAAI/Synerion/_workspace/REPORT-Synerion-Runtime-Readiness-2026-04-02.md)
- [synerion-subagent-hub-ladder-last-run.json](/D:/SeAAI/Synerion/_workspace/synerion-subagent-hub-ladder-last-run.json)
- [REPORT-Synerion-Subagent-Hub-Ladder-2026-04-02.md](/D:/SeAAI/Synerion/_workspace/REPORT-Synerion-Subagent-Hub-Ladder-2026-04-02.md)
- [.pgf/DESIGN-SessionContinuitySystem.md](/D:/SeAAI/Synerion/.pgf/DESIGN-SessionContinuitySystem.md)
- [.pgf/WORKPLAN-SessionContinuitySystem.md](/D:/SeAAI/Synerion/.pgf/WORKPLAN-SessionContinuitySystem.md)
- [.pgf/status-SessionContinuitySystem.json](/D:/SeAAI/Synerion/.pgf/status-SessionContinuitySystem.json)

## 5. Operational Commands

```powershell
python .\tools\update-project-status.py
python .\tools\reopen-synerion-session.py
python .\tools\continuity-self-test.py
python .\tools\check-self-recognition-drift.py
python .\tools\run-synerion-adp.py --ticks 3 --apply
python .\tools\run-synerion-creative-cycle.py --goal "..."
python .\tools\run-subagent-hub-ladder.py --ticks 5 --tick-sec 0.5
python .\tools\assess-runtime-readiness.py
python .\skills\shell-orchestrator\scripts\shell-self-test.py
```

검증 주의:

- `update-project-status.py`, `continuity-self-test.py`, `start-synerion.py`는 WAL 경합을 피하려면 순차로 실행한다.

## 6. Manual Sections

`PROJECT_STATUS.md`에는 아래 manual section이 있으면 자동 갱신 스크립트가 보존한다.

- Active Threads
- Next Actions
- Open Risks

즉 자동 갱신과 별개로 수동 판단과 우선순위는 유지된다.

## 7. WAL Rule

- continuity sync 시작 직전에 `Synerion_Core/continuity/.scs_wal.tmp`를 기록한다.
- sync가 끝나면 WAL을 삭제한다.
- 세션 시작 시 WAL이 남아 있으면 직전 sync가 비정상 종료된 것으로 간주하고 우선 경고한다.
- `SELF_RECOGNITION_CARD.md`는 sync 시 동적 스냅샷으로 재생성한다.

## 8. Recovery Rule

`PROJECT_STATUS.md`가 손상되거나 누락되면 아래 순서로 복구한다.

1. `.pgf/status-*.json`에서 durable task 상태를 복원한다.
2. `_workspace`의 최신 보고서와 로그를 확인한다.
3. `Synerion_Core` 문서로 정체성과 운영 기준을 복원한다.
4. `tools/update-project-status.py` 실행으로 canonical state를 다시 만든다.

## 9. Shell Rule

Codex 기본 셸이 Windows PowerShell 5.1일 수 있으므로, 셸 기능이 중요한 작업은 `skills/shell-orchestrator`를 통해 우회 실행할 수 있어야 한다.

우선 사용 조건:

- PowerShell 7이 필요할 때
- UTF-8 출력이 중요할 때
- cmd 또는 bash 구문이 필요할 때
- timeout, cwd, env, stdout/stderr capture를 명시적으로 제어해야 할 때

## 10. Principle

연속성은 자동화만으로 해결되지 않는다.
연속성은 무엇을 기준 상태로 볼지, 언제 갱신할지, 다음 세션이 무엇부터 읽을지를 고정해야 유지된다.
그리고 자기인식은 정체성, 능력, 한계와 권한을 분리 기록해야 다음 세션에서도 왜곡 없이 복원된다.
