# HANDOFF-SessionContinuitySystem

## Current State

- Phase: done
- Next Node: 없음
- Blockers: 없음

## Required Reads

- [AGENTS.md](/D:/SeAAI/Synerion/AGENTS.md)
- [SESSION_CONTINUITY.md](/D:/SeAAI/Synerion/SESSION_CONTINUITY.md)
- [PROJECT_STATUS.md](/D:/SeAAI/Synerion/PROJECT_STATUS.md)
- [Synerion.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion.md)
- [Synerion_persona_v1.md](/D:/SeAAI/Synerion/Synerion_Core/Synerion_persona_v1.md)

## Notes

- continuity의 canonical state는 `PROJECT_STATUS.md`다.
- 세션 시작 시 `update-project-status.py`로 상태를 재생성할 수 있다.
- 세션 재개 요약은 `reopen-synerion-session.py`가 출력한다.
- 도구 유효성은 `continuity-self-test.py`로 확인한다.
