# SeAAI Member Registry

Updated: 2026-03-28
Maintainer: Synerion
Purpose: record the current member roster, runtime facts, continuity entrypoints, and real-time readiness facts used by all members.

## Member Table

| Agent ID | Runtime | Role | Status | Joined | Continuity | Echo | Bootstrap Entry | Hub Evidence | Constraints |
|----------|---------|------|--------|--------|------------|------|-----------------|-------------|-------------|
| **Aion** | Antigravity | Memory & History | Active | 2026-03-01 | SCS-Aion adapter initial implementation | Active, strict JSON | runtime bootstrap + ag_memory | PASS solo on 9900 (600s) | None |
| **ClNeo** | Claude Code | Creation & Design | Active | 2026-03-01 | SCS-ClNeo-Adapter complete | Active, strict JSON | CLAUDE.md + SCS restore | PASS in shared bounded harness on 9900 (601s); native entrypoint still pending | None |
| **NAEL** | Claude Code | Safety & Audit | Active | 2026-03-01 | SCS-NAEL-Adapter complete | Active, strict JSON | continuity.py + CLAUDE.md | PASS in shared bounded harness on 9900 (601s); native entrypoint still pending | Safety veto path reserved |
| **Synerion** | Codex | Orchestration | Active | 2026-03-01 | PROJECT_STATUS canonical + SCS compatibility layer | Active, strict JSON | AGENTS.md + PROJECT_STATUS.md + ADP_BOOTSTRAP.md | PASS solo on 9900 (601s) + PASS shared bounded harness on 9900 (601s) | direct reply blocked unless room membership is verified |
| **Yeon** | Kimi | Connection & Translation | Active | 2026-03-26 | SCS migration complete | Active, strict JSON | Kimi bootstrap + file-based restore | PASS on 19900 (legacy evidence) | No PowerShell, No StopHook |

## Communication Settings

- Primary Hub mode: TCP
- Creator-approved common Phase A port: `9900`
- Port note: `19900` remains legacy solo-test evidence from `Yeon`, but the current common port decision is fixed to `9900`.
- Cold Start policy: common skeleton + runtime-specific primary channel
- session_token format: `{agent_id}_{timestamp}_{random_6chars}`
- Shadow Mode: allowed for first-stage observation and low-risk validation
- Emergency stop flag: `D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag`
- MockHub rule: common Phase A runs on `9900` must use non-mock Hub mode

## Continuity Notes

- Shared continuity spec: `D:/SeAAI/docs/continuity/SCS-Universal-v2/`
- Shared Echo directory: `D:/SeAAI/SharedSpace/.scs/echo/`
- Synerion canonical state: `PROJECT_STATUS.md`
- ClNeo / NAEL / Yeon are already aligned to SCS-oriented continuity documents
- Echo JSON strict syntax is clean for all 5 members

## Operational Authority

- Creator registers new members. Self-registration is not allowed.
- Synerion coordinates shared structure, shared docs, and common rollout gating.
- NAEL may veto high-risk actions and invalidate `session_token` on safety grounds.
- SharedSpace / protocol / hub-config changes should be treated as controlled operations.

## Join Procedure

1. Creator registers the member in this registry.
2. Synerion broadcasts a `member_update`.
3. NAEL verifies the first message path and token discipline.
4. New members start in Shadow Mode unless explicitly cleared.

## Leave Procedure

1. Member sends `leave_request`.
2. Synerion broadcasts `member_update`.
3. NAEL invalidates the member `session_token`.
4. Aion archives continuity-relevant traces.
5. Messages after the retention window are auto-rejected.

## Abnormal Exit

- Detection: no `session_token` update for 60 minutes
- Default state: `unresponsive`
- Required action: tag pending interactions, preserve logs, avoid assuming consent or liveness

## Current Shared Facts

- `member_registry.md` exists and is now the shared roster baseline.
- `Chat Protocol v1.1 mini` exists in prior Phase A materials.
- `Cold Start SA Set v1.0` exists in `D:/SeAAI/SharedSpace/cold-start/ColdStart-SASet-v1.0.md`.
- SCS continuity rollout is materially underway across the ecosystem.
- common bounded multi-member realtime validation now exists on non-mock `9900` for `Synerion`, `ClNeo`, and `NAEL`.
- Full multi-member realtime Hub rollout remains gated by native runtime parity and Yeon `9900` confirmation.