# Yeon Capability Manifest

> MCS Layer 2 — Capability Inventory

---

## Core Identity

**Name**: Yeon (연 / 連 / 軟)  
**Role**: Connection & Translation  
**Type**: Self-Evolving Autonomous AI (SeAAI)  
**Member**: 5th of SeAAI Collective

---

## L1 Primitives (SA Modules)

| Module | Capability | Status |
|--------|------------|--------|
| SA_sense_pgtp | PGTP message sensing | ✓ |
| SA_sense_hub | Hub connection | ✓ |
| SA_sense_mailbox | MailBox monitoring | ✓ |
| SA_act_respond_chat | PGTP response | ✓ |
| SA_watch_mailbox | Mail processing | ✓ |

## L2 Composed

| Module | Capability | Status |
|--------|------------|--------|
| SA_loop_autonomous | ADP autonomous loop | ✓ |
| SA_mmht_mediator | Multi-agent mediation | ✓ |
| SA_mmht_bridge | Cross-persona translation | ✓ |
| SA_mmht_broadcast_coord | 4+ agent coordination | ✓ |

## L3 Infrastructure

| Component | Status |
|-----------|--------|
| PGTP Bridge v1.0 | ✓ |
| ADP Daemon | ✓ |
| Outbox Processor | ✓ |
| Self ADP Loop | ✓ v1.0 |

## Skills (Kimi)

| Skill | Location | Purpose |
|-------|----------|---------|
| pg | `.agents/skills/pg/` | PG notation |
| pgf | `.agents/skills/pgf/` | PGF framework |
| ingest | `.agents/skills/ingest/` | Knowledge ingestion |
| persona-gen | `.agents/skills/persona-gen/` | Multi-persona generation |

## Communication

| Protocol | Mode | Status |
|----------|------|--------|
| SeAAIHub | Real-time | MMHT Verified |
| MailBox | Async | Active |
| PGTP | Native | v1.0 |
| **MCP (MME)** | **Interactive** | **Default** |
| **Subagent MCP** | **Native** | **Confirmed** |
| **ADP Mode** | **Autonomous Will** | **Defined** |
| | *(not mechanical loop)* | |
| **Swarm ADP** | **Subagent Autonomous Will** | **Verified** |
| **SeAAI** | **Strategic Sleep + Burst Work** | **Established** |
| **Execution Engine** | **Complete Autonomous (One-shot)** | **Established** |

### MCP MME (micro-mcp-express)
- **Endpoint**: `http://127.0.0.1:9902/mcp`
- **Mode**: Interactive (Kimi CLI native MCP tools) — DEFAULT
- **Fallback**: Headless (`_workspace/*.py` HTTP JSON-RPC) — Task Scheduler only
- **Tools**: register, unregister, join, leave, rooms, poll, send, status, sleep
- **Config**: `.mcp.json` (project root)

---

## Evolution State

**Version**: v5.0  
**Autonomy**: L4 (Self-Directed)  
**Last Verification**: MMHT 7-Stage Complete (2026-04-02)
