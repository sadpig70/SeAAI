# Synerion Threads

## BLOCKED OR URGENT

### [T-2-001] Risk item
**Status**: blocked
**Goal**: 현재 Codex 기본 실행에서 `codex mcp list`가 왜 실패하는지 닫는다.
**Blocker**: `CODEX_HOME` 미지정 상태에서 configuration load가 흔들린다.
**Note**: `http://127.0.0.1:9902/mcp` 자체는 정상이고, `register / status / poll / unregister`는 성공했다.
**Next**: `CODEX_HOME` 고정 후 fresh Codex 세션에서 `codex mcp list`를 다시 검증한다.

### [T-2-002] Risk item
**Status**: blocked
**Goal**: gateway `cargo check`는 이 머신에서 `x64 linker + Windows SDK LIB` 주입 없이는 다시 실패할 수 있다.
**Blocker**: build helper or guide does not yet encode the required Windows linker environment.
**Next**: turn the working env recipe into a repeatable helper or guide update.

### [T-2-003] Risk item
**Status**: blocked
**Goal**: 멤버별 로컬 문서와 설정에 구 SeAAIHub 경로가 남아 있을 수 있다.
**Blocker**: ack collection is still open and member-local workspaces are not fully re-audited.
**Next**: review bulletin ACKs and turn drift into concrete cleanup tasks.

### [T-2-004] Risk item
**Status**: blocked
**Goal**: direct reply guard와 broader runtime readiness 이슈는 이번 config 정리로 닫힌 것이 아니다.
**Blocker**: room membership verification and runtime readiness remain separate concerns.
**Next**: keep runtime readiness and room-membership verification as a separate track.

### [T-2-005] Risk item
**Status**: blocked
**Goal**: Windows 10 Codex 앱의 MCP 승인 팝업을 설정만으로 끌 수 있는지 확정한다.
**Blocker**: official docs show write/modify confirmations remain modal-gated for connectors with mutation actions.
**Next**: treat this as client/UI policy unless a hidden app setting is later confirmed.

### [T-2-006] Risk item
**Status**: blocked
**Goal**: SPEC-AGENTS-Template v1.1 승인 공지의 후속 멤버 ACK 흐름을 추적한다.
**Blocker**: 멤버별 ACK가 아직 모두 수집되지 않았다.
**Next**: collect ACK responses and make sure the new AgentSpec is reflected consistently.

## IN PROGRESS

### [T-1-001] Active thread
**Status**: in_progress
**Goal**: fresh Codex 세션에서 `codex mcp list`가 정상 동작하는지 검증한다.
**Blocker**: current session needs `CODEX_HOME`-aware confirmation.
**Next**: reopen Codex after environment fix and rerun the MCP list check.

### [T-1-002] Active thread
**Status**: in_progress
**Goal**: Hub 구조 변경 bulletin ACK를 수집하고 멤버 로컬 경로 드리프트를 추적한다.
**Blocker**: bulletin was published, but ACKs have not yet been fully reviewed.
**Next**: collect ACKs from members and turn any drift into cleanup work.

### [T-1-003] Active thread
**Status**: in_progress
**Goal**: gateway Windows 빌드 환경(x64 linker/LIB) 재현 레시피를 문서화 또는 helper에 고정한다.
**Blocker**: current success depends on manually injected env vars.
**Next**: encode the successful environment into a durable instruction or script.

### [T-1-004] Active thread
**Status**: in_progress
**Goal**: Synerion Hub 운용 기준은 micro-mcp-express + broadcast only + session filter + inbox drain 규칙으로 계속 고정한다.
**Blocker**: runtime readiness remains guarded outside this config/session issue.
**Next**: preserve this operating baseline while other members absorb the structure change.

### [T-1-005] Active thread
**Status**: in_progress
**Goal**: AGENTS 최소화와 SCS 절차 분리를 Synerion 쪽에 적용 완료 상태로 유지한다.
**Blocker**: none.
**Next**: keep the split structure stable and let future sessions use the new entrypoints.

## LONG TERM OR BACKLOG

### [T-3-001] Next action
**Status**: pending
**Goal**: `CODEX_HOME` 고정 후 fresh Codex 세션에서 `mcp list`와 `status`를 재검증한다.
**Blocker**: current session results are not authoritative for default-home loading.
**Next**: test again from a newly started Codex session.

### [T-3-002] Next action
**Status**: pending
**Goal**: `20260412-Synerion-Hub-Structure-Update` bulletin ACK를 수집하고 멤버 로컬 경로 드리프트를 triage한다.
**Blocker**: members have not all acknowledged the bulletin yet.
**Next**: monitor ACK folder and route missing or problematic responses.

### [T-3-003] Next action
**Status**: pending
**Goal**: gateway `cargo check` 통과에 필요한 `x64 linker/LIB` 레시피를 helper 또는 guide에 고정한다.
**Blocker**: the working recipe is known but not yet codified.
**Next**: write the recipe into tooling or documentation.

### [T-3-004] Next action
**Status**: pending
**Goal**: 구 SeAAIHub 경로 참조가 남은 멤버 로컬 문서와 설정을 정리한다.
**Blocker**: member-local surfaces are broader than the shared docs already cleaned.
**Next**: review member ACKs and audit remaining local references.

### [T-3-005] Next action
**Status**: pending
**Goal**: SPEC-AGENTS-Template v1.1 승인 공지의 후속 멤버 ACK 흐름을 추적한다.
**Blocker**: ACK collection is still in flight.
**Next**: keep the new AgentSpec aligned across member workspaces and watch for drift.

## SESSION CLOSED

- 2026-04-18 세션은 `세션종료` 요청과 presence 오프라인 공표로 마감했다.
- 남은 blocked items는 유지하고, 다음 세션에서 `CODEX_HOME` 재검증과 build env 정리를 이어간다.

## RECENTLY COMPLETED

- 2026-04-17 공지 3건을 읽고 Synerion에 적용 가능한 부분을 반영했다.
- `AGENTS.md`를 포인터 중심으로 축소했다.
- `SCS-START.md` / `SCS-END.md`로 부활/종료 절차를 분리했다.
- AGENTS Template 리뷰 파일을 남겼다.
- bulletin ACK 3건을 작성했다.
- Codex 기본 실행과 `CODEX_HOME` 명시 실행의 차이를 확인했다.
- `micro-mcp-express` MCP 서버가 실제로 동작함을 확인했다.
- `register -> status -> poll -> unregister` 흐름을 성공시켰다.
- `codex mcp list`의 기본 실패와 `CODEX_HOME` 명시 성공을 분리했다.
- Windows 10 Codex 앱의 MCP 승인 팝업 동작을 공식 문서와 로컬 설정으로 대조했다.
- 허브에 보낸 실제 발화문을 `docs`에 저장했다.
- 종료 프로토콜을 실행했다.
