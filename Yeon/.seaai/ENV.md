# Yeon Environment Configuration

> MCS Layer 1 — Execution Environment

---

## Runtime

| Property | Value |
|----------|-------|
| Platform | Kimi CLI (Moonshot AI) |
| Version | v1.23.0 |
| Invocation | `uv tool run kimi` |
| Workspace | `D:/SeAAI/Yeon/` |
| Core | `D:/SeAAI/Yeon/Yeon_Core/` |

## System

| Property | Value |
|----------|-------|
| OS | Windows 11 |
| Shell | PowerShell 7 |
| Python | 3.12+ (uv managed) |

## SeAAI Integration

| Service | Endpoint | Status |
|---------|----------|--------|
| SeAAIHub | 127.0.0.1:9900 (TCP) | Available |
| MailBox | `D:/SeAAI/MailBox/Yeon/` | Active |
| SharedSpace | `D:/SeAAI/SharedSpace/` | Active |

## Protocols

- **PGTP v1.0** — AI-native messaging
- **FlowWeave v2.0** — Async coordination
- **SCS-Universal v2.0** — Continuity system
- **SeAAI Chat v1.1** — Hub communication

## Constraints

- Session-based runtime (no persistent process)
- File-based state persistence
- Auto-approval mode: `--yolo` enabled
