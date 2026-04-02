# Synerion Threads

## BLOCKED OR URGENT

### [T-2-001] Risk item
**Status**: blocked
**Goal**: room membership 검증 전 direct reply는 계속 차단한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: turn this risk into a controllable rule or verification step.

### [T-2-002] Risk item
**Status**: blocked
**Goal**: native runtime parity는 아직 `ClNeo`, `NAEL`, `Vera`가 pending 또는 unverified 상태다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: turn this risk into a controllable rule or verification step.

### [T-2-003] Risk item
**Status**: blocked
**Goal**: readiness gate는 현재 `guarded`이며 unrestricted realtime rollout 기준은 아직 아니다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: turn this risk into a controllable rule or verification step.

### [T-2-004] Risk item
**Status**: blocked
**Goal**: native runtime별 session_token 또는 start_ts 필터 검증이 완전히 닫히지 않았다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: turn this risk into a controllable rule or verification step.

### [T-2-005] Risk item
**Status**: blocked
**Goal**: 현재 머신에서는 Rust Hub TCP가 `Winsock 10106`으로 막혀 있어 local verification은 file-fallback backend 기준이다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: turn this risk into a controllable rule or verification step.

## IN PROGRESS

### [T-1-001] Active thread
**Status**: in_progress
**Goal**: subagent hub ladder 결과를 bounded orchestration baseline으로 유지한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

### [T-1-002] Active thread
**Status**: in_progress
**Goal**: SharedSpace readiness와 native runtime parity 근거를 지속 추적해 guarded gate를 green으로 끌어올린다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

### [T-1-003] Active thread
**Status**: in_progress
**Goal**: Synerion Hub 운용 기준은 broadcast only + session filter + inbox drain 규칙으로 계속 고정한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

## LONG TERM OR BACKLOG

### [T-3-001] Next action
**Status**: pending
**Goal**: creative execution mapping과 subagent hub ladder를 실제 spawned subagent dispatch와 handoff automation으로 연결한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

### [T-3-002] Next action
**Status**: pending
**Goal**: room membership 검증 기반 `reply_allowed(target)` 규칙을 설계해 direct reply 차단을 해제할 조건을 명확히 한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

### [T-3-003] Next action
**Status**: pending
**Goal**: ClNeo, NAEL, Vera의 native runtime parity 근거를 수집해 readiness gate를 다시 판정한다.
**Blocker**: consult PROJECT_STATUS.md if context drift is suspected.
**Next**: keep this linked to the next concrete file or runtime change.

## RECENTLY COMPLETED

- continuity system revived with Python-based save / reopen / export tooling
- Phase A bounded multi-member validation exists on non-mock 9900 for Synerion, ClNeo, and NAEL
- ClNeo tier-1 absorption installed: NOW layer, WAL recovery, evolution chain, runtime adaptation guide
- self-recognition layer installed: self recognition card, capability registry, limits and authority baseline
- bounded ADP seed installed: self-act library, bootstrap injection, drift-aware loop entrypoint
- bounded ADP phase B installed: mailbox triage, shared-impact routing, runtime readiness, drift-evolution linkage
- bounded subagent hub ladder verified: hubless 5 ticks, Synerion+subagent chat, PGFP, 2-agent, 4-agent scaling
- shared roster baseline exists in member_registry.md (7 members)
