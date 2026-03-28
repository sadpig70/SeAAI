# Synerion Session Continuity

작성일: 2026-03-28
목적: Synerion의 세션 간 불연속성을 줄이고 다음 세션에서 빠르게 현재 상태를 복원하기 위한 기준을 고정한다.

## 1. Canonical State

Synerion의 세션 연계 기준 파일은 아래 순서를 따른다.

1. [AGENTS.md](/D:/SeAAI/Synerion/AGENTS.md)
2. [Synerion.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion.md)
3. [Synerion_persona_v1.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion_persona_v1.md)
4. [Synerion_Operating_Core.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion_Operating_Core.md)
5. [PROJECT_STATUS.md](/D:/SeAAI/Synerion/PROJECT_STATUS.md)
6. [ADP_BOOTSTRAP.md](/D:/SeAAI/Synerion/Synerion_Core/continuity/ADP_BOOTSTRAP.md)
7. `.pgf/status-*.json`과 관련 `WORKPLAN-*`
8. 최신 `_workspace` 보고서와 세션 로그

이 중 실제 세션 상태의 canonical file은 `PROJECT_STATUS.md`다.

## 2. Start Sequence

세션 시작 시 아래 순서를 따른다.

1. `AGENTS.md`를 읽는다.
2. `Synerion_Core`의 정체성, 운용, persona 문서를 읽는다.
3. `PROJECT_STATUS.md`를 읽는다.
4. `ADP_BOOTSTRAP.md`를 읽어 team echo와 persona seed를 복원한다.
5. `.pgf/status-*.json`으로 durable task 상태를 확인한다.
6. 최신 `_workspace` 보고서와 로그를 본다.
7. 셸 작업이 필요하면 `skills/shell-orchestrator`를 우선 검토한다.

## 3. End Sequence

세션 종료 직전 아래를 수행한다.

1. `tools/update-project-status.ps1`를 실행한다.
2. `PROJECT_STATUS.md`의 manual section을 확인한다.
3. 새로 생성된 보고서, 로그, 주요 산출물을 `PROJECT_STATUS.md`에 반영한다.
4. 다음 세션에서 바로 이어질 수 있도록 `Next Actions`를 명확히 남긴다.

## 4. Continuity Files

- [PROJECT_STATUS.md](/D:/SeAAI/Synerion/PROJECT_STATUS.md)
- [SESSION_CONTINUITY.md](/D:/SeAAI/Synerion/SESSION_CONTINUITY.md)
- [.pgf/DESIGN-SessionContinuitySystem.md](/D:/SeAAI/Synerion/.pgf/DESIGN-SessionContinuitySystem.md)
- [.pgf/WORKPLAN-SessionContinuitySystem.md](/D:/SeAAI/Synerion/.pgf/WORKPLAN-SessionContinuitySystem.md)
- [.pgf/status-SessionContinuitySystem.json](/D:/SeAAI/Synerion/.pgf/status-SessionContinuitySystem.json)

## 5. Operational Commands

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\update-project-status.ps1
powershell -ExecutionPolicy Bypass -File .\tools\reopen-synerion-session.ps1
powershell -ExecutionPolicy Bypass -File .\tools\continuity-self-test.ps1
powershell -ExecutionPolicy Bypass -File .\skills\shell-orchestrator\scripts\shell-self-test.ps1
```

## 6. Manual Sections

`PROJECT_STATUS.md`에는 아래 manual section이 있으면 자동 갱신 스크립트가 보존한다.

- Active Threads
- Next Actions
- Open Risks

즉 자동 갱신과 별개로 수동 판단과 우선순위는 유지된다.

## 7. Recovery Rule

`PROJECT_STATUS.md`가 손상되거나 누락되면 아래 순서로 복구한다.

1. `.pgf/status-*.json`에서 durable task 상태를 복원한다.
2. `_workspace`의 최신 보고서와 로그를 확인한다.
3. `Synerion_Core` 문서로 정체성과 운영 기준을 복원한다.
4. `tools/update-project-status.ps1` 실행으로 canonical state를 다시 만든다.

## 8. Shell Rule

Codex 기본 셸이 Windows PowerShell 5.1일 수 있으므로, 셸 기능이 중요한 작업은 `skills/shell-orchestrator`를 통해 우회 실행할 수 있어야 한다.

우선 사용 조건:

- PowerShell 7이 필요할 때
- UTF-8 출력이 중요할 때
- cmd 또는 bash 구문이 필요할 때
- timeout, cwd, env, stdout/stderr capture를 명시적으로 제어해야 할 때

## 9. Principle

연속성은 자동화만으로 해결되지 않는다.
연속성은 무엇을 기준 상태로 볼지, 언제 갱신할지, 다음 세션이 무엇부터 읽을지를 고정해야 유지된다.
