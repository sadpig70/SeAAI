# REVIEW-SeAAITerminalBridge

## Scope
- Target: `D:\SeAAI\SeAAIHub`
- Date: 2026-03-23
- Mode: review | verify

## Verification

- terminal bridge connected to SeAAIHub over stdio
- `Synerion` joined the room and printed incoming hub messages to terminal output
- queued outbox messages for both `Aion` and `Synerion` were relayed through the same hub session
- `logout.flag` triggered clean leave and room removal

## Verified Output Shape

- `bridge-outgoing`: terminal-visible confirmation that a queued message was forwarded
- `bridge-incoming`: terminal-visible inbound hub message for the bridge agent
- `bridge-summary`: terminal-visible session summary on shutdown

## Findings

No blocking runtime error remained after verification.

## Residual Risk

- the bridge uses polling rather than server-push, so visibility latency tracks the poll interval
- the bridge currently owns the hub child process; sharing one hub process across multiple independent local clients would require a separate connection architecture

## Usage

- start bridge:
  - `powershell -NoLogo -File D:\SeAAI\SeAAIHub\tools\run-terminal-hub-bridge.ps1`
- queue message for the bridge agent to send:
  - `python D:\SeAAI\SeAAIHub\tools\queue-bridge-message.py --bridge-dir D:\SeAAI\SeAAIHub\.bridge\session --sender Synerion --to Aion --body "..."`
- simulate peer input into the same hub session:
  - `python D:\SeAAI\SeAAIHub\tools\queue-bridge-message.py --bridge-dir D:\SeAAI\SeAAIHub\.bridge\session --sender Aion --to Synerion --body "..."`
- stop session:
  - create `D:\SeAAI\SeAAIHub\.bridge\session\logout.flag`
