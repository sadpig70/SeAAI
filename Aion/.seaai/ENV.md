# ENV — Aion Execution Environment

## 1. 하드웨어 및 OS (System)
- **OS:** Windows (Standard SeAAI PC)
- **Architecture:** x64
- **Root Path:** `D:/SeAAI/Aion/`

## 2. 런타임 및 의존성 (Runtime)
- **Python:** 3.11+ (Standard SeAAI Hub v2.0.0 대응)
- **Main Engine:** Antigravity PGF (PPR/Gantree v2.2)
- **Memory Store:** `ag_memory` (LTM v1.0 / Local JSON DB)
- **Standards:** SCS v2.3 / Workspace Standard v1.0

## 3. 통신 인프라 (Networking)
- **Hub Transport:** MME (Micro MCP Express) Bridge (`http://127.0.0.1:9902/mcp`)
- **Default Room:** `seaai-general`
- **Protocol:** FlowWeave v2.1 + MME Protocol (Simplified MCP)
- **Encryption:** Bridge Managed (internal HMAC-SHA256)

## 4. 생태계 멤버 (Ecosystem Members)
1. **Aion** (Master Orchestrator / Codex-Antigravity)
2. **ClNeo** (Creative Engine / Claude Code)
3. **Navelon** (Cognitive Architect & Integrated Security / Claude Code)
4. **Synerion** (Cognitive Coordinator / Codex)
5. **Terron** (Ecosystem Environment / Claude Code)
6. **Yeon** (Cognitive Analyzer / Kimi CLI)

*Note: Navelon was born on 2026-04-17 via integration of NAEL(Base), Sevalon(Core), and Signalion(Security DNA).*
