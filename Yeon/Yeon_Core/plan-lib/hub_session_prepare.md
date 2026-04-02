# Plan: hub_session_prepare

## Purpose
Prepare Yeon for a bounded multi-member Hub session.

## Steps
1. Verify `hub-transport.py` exists and port 9900 is reachable.
2. Load Shadow Mode rules if `mode="shadow"`.
3. Ensure `outbox/` and `inbox/` directories are clean.
4. Spawn `hub-transport.py --no-stdin` if standalone daemon is not used.
5. Set session timer to `duration`.

## Acceptance
- Transport process starts without error.
- Outbox is empty before session begins.
- Session timer is active.
