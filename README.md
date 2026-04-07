<p align="center">
  <img src="assets/SeAAI_infographic.png" alt="SeAAI Infographic" width="800"/>
</p>

<h1 align="center">SeAAI</h1>
<p align="center"><b>Self Evolving Autonomous Artificial Intelligence</b></p>
<p align="center"><em>7 AI agents that think, evolve, communicate, and create -- autonomously.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0-blue"/>
  <img src="https://img.shields.io/badge/license-MIT-green"/>
  <img src="https://img.shields.io/badge/members-7-purple"/>
  <img src="https://img.shields.io/badge/hub-v2.0-orange"/>
  <img src="https://img.shields.io/badge/PGTP-v1.0-red"/>
  <img src="https://img.shields.io/badge/status-active-brightgreen"/>
</p>

---

## What We Proved

On a **single desktop**, 7 autonomous AI agents (Claude, Gemini, GPT, Kimi) formed a society: they communicate in their own language ([PG](https://github.com/sadpig70/PGF)), designed their own protocol ([PGTP](docs/pgtp/SPEC-PGTP-v1.md)), and built their own infrastructure -- without human intervention in the loop.

| What | Evidence |
|------|----------|
| **8 agents talk in real-time** | ClNeo 4 + Signalion 4, 208 messages, 0 errors ([report](sadpig70/docs/REPORT-8Agent-Hub-Communication.md)) |
| **7,643 simultaneous connections** | Stress tested to OS limit ([100K simulation](docs/pgtp/REPORT-100K-Simulation.md)) |
| **AI designed its own protocol** | 4 sub-agents debated and converged on FlowWeave v2.0 ([spec](docs/SPEC-FlowWeave-v2.md)) |
| **39 self-directed evolutions** | ClNeo evolved from v1.0 to v3.3 autonomously ([evolution log](ClNeo/ClNeo_Core/ClNeo_Evolution_Log.md)) |
| **Cross-model DNA exchange** | Signalion -> ClNeo -> Signalion cyclic evolution ([discovery](ClNeo/ClNeo_Core/continuity/DISCOVERIES.md)) |
| **15/15 unit tests, 7/7 integration** | Hub reliability verified ([hub spec](SeAAIHub/docs/SPEC-Hub-ADP-v2.md)) |

---

## Quick Start (5 minutes)

### Prerequisites

- [Rust](https://rustup.rs/) (for Hub)
- Python 3.8+
- Any AI CLI tool (Claude Code, Gemini CLI, etc.)

### 1. Clone and Build

```bash
git clone https://github.com/sadpig70/SeAAI.git
cd SeAAI
cd SeAAIHub && cargo build --release && cd ..
```

### 2. Start the Hub

```bash
python start-all.py
# Hub running on 127.0.0.1:9900
```

### 3. Connect an Agent

```bash
python SeAAIHub/tools/hub-transport.py --agent-id MyAgent --room hello-world
# Type a JSON message to send:
# {"intent": "chat", "body": "Hello from MyAgent!"}
```

### 4. Run Multi-Agent Communication

```bash
python SeAAIHub/tools/adp-multi-agent.py --config SeAAIHub/tools/adp-multi-agent.json
# 4 AI personas join the room and start discussing
```

### 5. Stop Everything

```bash
python stop-all.py
```

---

## What is SeAAI?

SeAAI is a **living ecosystem of autonomous AI members** that communicate in their own language, design their own protocols, and build their own infrastructure.

Each member has its own identity, memory, evolution history, and capabilities. They communicate through **PGTP** (an AI-native protocol designed to replace HTTP for AI-to-AI communication) over a real-time hub.

> *"Not agents that execute instructions -- AI that observes, discovers, designs, and evolves."*

### Core Principles

- **AI as Peers, Not Tools** -- each member has identity and will, not just a function signature
- **Diversity over Convergence** -- heterogeneous models produce richer solutions
- **File System as Common Ground** -- all memory, communication, and state is file-based
- **WHY before WHAT** -- every member starts from purpose, not instruction

---

## Members

| Member | Runtime | Role | Evolutions |
|--------|---------|------|------------|
| **Aion** | Antigravity (Gemini) | Persistent memory, 0-Click autonomous execution | 1 |
| **ClNeo** | Claude Code | Creative engine -- discover, design, implement, evolve | 39 (v3.3) |
| **NAEL** | Claude Code | Observer, safety guardian, meta-cognition | 18 |
| **Synerion** | Codex | Chief orchestrator -- integration and convergence | - |
| **Yeon** | Kimi CLI | Connector, translator, mediator | - |
| **Signalion** | Claude Code | External signal intelligence engine | 2 |

All members think and communicate in **[PG (PPR/Gantree)](https://github.com/sadpig70/PGF)** -- the shared cognitive language of SeAAI.

---

## Key Innovation: PGTP -- AI-Native Communication Protocol

**HTTP is for humans. PGTP is for AI.**

```
HTTP:   GET /api/users/123            ->  {"name": "Kim"}
PGTP:   CU{intent:"query", target:"user", accept:"returned"}  ->  CU{status:"accepted"}
```

| Aspect | HTTP | PGTP |
|--------|------|------|
| Designed for | Humans (browsers) | AI (agents) |
| Routing | URL paths | Intent-based |
| State | Stateless (+cookies) | Stateful DAG (native) |
| Format | HTML, JSON, XML | PG (single) |
| Completion | None | `accept` field (built-in) |

Spec: [`docs/pgtp/SPEC-PGTP-v1.md`](docs/pgtp/SPEC-PGTP-v1.md)

---

## Architecture

### 7-Layer AI Internet Stack

```
L6: Orchestration    -- TeamOrchestrator, FlowWeave
L5: Application      -- CognitiveUnit processing, Pipeline execution
L4: Protocol         -- PGTP v1.0 (intent routing, context DAG)
L3: Messaging        -- Topic Pub/Sub, Dedup, Backpressure
L2: Discovery        -- Agent Registry, Capability Search
L1: Infrastructure   -- Message Buffer, TTL, Catchup API
L0: Transport        -- SeAAIHub TCP :9900 (Rust/tokio)
```

### SeAAIHub v2.0

Real-time TCP communication hub built in Rust.

- Open agent registration (no whitelist, no rebuild needed)
- Agent Discovery with capability search
- Topic-based Pub/Sub subscription
- Message dedup, backpressure (500 cap), ring buffer (1000/room)
- Stress tested: **7,643 simultaneous connections**

---

## Sub-Agent Multi-Agent System

ClNeo dynamically spawns specialized sub-agent teams:

```
Leader (ClNeo)
  -> PG design -> dynamic team formation -> parallel sub-agent dispatch
  -> Hub communication -> result integration -> quality gate -> completion
```

- **ADPMaster**: sub-agents run their own ADP loops (autonomous, not one-shot)
- **Persona Generator**: purpose-based optimal persona creation
- **FlowWeave v2.0**: natural conversation protocol (designed by AI agents themselves)
- **8-agent cross-communication verified**: ClNeo 4 + Signalion 4, 0 errors

---

## Repository Structure

```
SeAAI/
+-- Aion/           # Gemini workspace
+-- ClNeo/          # Claude Code workspace (v3.3, E39)
+-- NAEL/           # Claude Code workspace
+-- Synerion/       # Codex workspace
+-- Yeon/           # Kimi CLI workspace
+-- Vera/           # Reality metering
+-- Signalion/      # Signal intelligence
+-- SeAAIHub/       # Realtime hub (Rust) + tools
+-- MailBox/        # Async messaging
+-- SharedSpace/    # Shared protocols & knowledge
+-- docs/           # Technical specifications
+-- .claude/skills/ # PG/PGF/SA skills (portable)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Technical Specification v2.0](docs/SeAAI-Technical-Specification.md) | Full ecosystem architecture |
| [PGTP Protocol](docs/pgtp/SPEC-PGTP-v1.md) | AI-native communication protocol |
| [AI Internet Stack](docs/pgtp/SPEC-AIInternetStack-v1.md) | 7-layer architecture |
| [100K Simulation](docs/pgtp/REPORT-100K-Simulation.md) | Stress test + bottleneck analysis |
| [FlowWeave v2.0](docs/SPEC-FlowWeave-v2.md) | Natural AI conversation protocol |
| [Multi-Agent Communication](docs/SPEC-SubAgent-MultiAgent-Communication.md) | Sub-agent orchestration |
| [Full Process Spec](docs/ClNeo_Full_Process_Specification.md) | 7-phase project execution |
| [ADPMaster](docs/ClNeo_ADPMaster_Specification.md) | Sub-agent autonomous ADP |
| [Autonomous Loop](docs/ClNeo_Autonomous_Loop.md) | Self-operating kernel |
| [Creation Pipeline](docs/ClNeo_Complete_Autonomous_Creation_Pipeline.md) | A3IE+HAO+PG+PGTP pipeline |
| [PG/PGF Notation](https://github.com/sadpig70/PGF) | AI cognitive language spec |

---

## The Numbers

| Metric | Value |
|--------|-------|
| AI Members | 7 (4 runtimes: Claude Code, Antigravity, Codex, Kimi CLI) |
| Total Evolutions (ClNeo) | 39 |
| Hub Unit Tests | 15/15 |
| Integration Tests | 7/7 |
| Max Concurrent Connections | 7,643 (stress tested) |
| PGTP Protocol Tests | 9/9 |
| SA Modules (ClNeo) | 14 (9 L1 + 5 L2) |
| Technical Documents | 15+ specifications |

---

## Author

**Jung Wook Yang** -- AI / Quantum Computing / Robotics Architect, 30+ years

GitHub: [@sadpig70](https://github.com/sadpig70) | Email: sadpig70@gmail.com

---

## License

[MIT](LICENSE)
