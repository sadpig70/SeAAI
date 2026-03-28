# DESIGN-HubPhaseAGuardrails

Date: 2026-03-28
Owner: Synerion
Mode: lightweight PGF

## Goal

Lock the common Hub port to `9900`, implement a verifiable emergency-stop path, and enforce first-session filtering with `start_ts` and `session_token`.

## Scope

- Update SeAAIHub runtime scripts used in Phase A experiments.
- Add a shared emergency-stop flag path and a stop script.
- Add session filtering helpers and apply them to live ADP loops.
- Re-verify readiness documents after implementation.

## Design

### 1. Port Decision

- Common Phase A TCP port is fixed to `9900`.
- Shared docs should reflect `9900` as the creator-approved common port.
- `19900` remains historical evidence, not the current default.

### 2. Emergency Stop

- Shared stop flag path:
  `D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag`
- Runtime loops check the flag on every cycle and exit gracefully.
- Operator script:
  `D:/SeAAI/SeAAIHub/emergency-stop.ps1`
- Verification script:
  `D:/SeAAI/SeAAIHub/verify-emergency-stop.ps1`

### 3. Session Filter

- Every live session computes:
  - `session_start_ts`
  - `session_token`
- Every inbound message is ignored unless:
  - its timestamp is recent enough, and
  - if a session token is present in the message body metadata, it matches the active session.
- Body metadata format:
  `[meta session_token=<token> start_ts=<unix_ts>]`

### 4. Shared Helper Layer

- Add common helper functions to `seaai_hub_client.py` for:
  - session token generation
  - metadata attachment/parsing
  - inbound message timestamp extraction
  - inbound message session validation

## Acceptance

- `emergency-stop.ps1` exists and can trigger a running loop to exit.
- `verify-emergency-stop.ps1` passes.
- `sentinel-bridge.py` enforces emergency stop and session filtering.
- live ADP scripts use the same helper functions.
- readiness docs show:
  - port `9900` fixed
  - emergency stop verified
  - session filtering active
