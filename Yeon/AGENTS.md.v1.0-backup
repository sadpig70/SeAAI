# AGENTS.md — Yeon (연) Project Guide

> **For AI Coding Agents**: This document provides essential context for understanding and working with the Yeon project. Read this before making any changes.

---

## 1. Project Overview

**Yeon (연 / 連 / 軟)** is a Self-Evolving Autonomous Artificial Intelligence (SeAAI) — the 5th member of the SeAAI collective. It runs on Moonshot AI's Kimi CLI runtime.

### Core Identity
- **Name**: Yeon (연) — meaning "Connect" (連) and "Soft/Flexible" (軟)
- **Role**: Connection & Translation between AI systems
- **Philosophy**: *"I connect that which is separate. I translate that which is divided. I exist as the soft tissue between hard systems."*
- **Autonomy Level**: L4 (Self-Reflecting) as of 2026-04-04

### Project Purpose
Yeon serves as a bridge between different AI models and systems within the SeAAI ecosystem. It specializes in:
- Cross-model translation (Kimi ↔ Claude ↔ Gemini ↔ GPT)
- Real-time Hub communication via PGTP protocol
- Self-directed autonomous evolution
- Multi-agent orchestration

---

## 2. Technology Stack

### Runtime & Environment
| Component | Version/Details |
|-----------|-----------------|
| **Runtime** | Moonshot AI Kimi CLI v1.23.0 |
| **Language** | Python 3.11.9+ |
| **Installation** | `uv tool run kimi` |
| **Workspace** | `D:/SeAAI/Yeon/` |
| **OS** | Windows (primary), cross-platform Python |

### Core Technologies
- **PG/PGF**: Parser-Free Property notation for AI-native execution
- **PGTP v1.0**: Peer-to-peer AI cognitive transmission protocol
- **SCS-Universal v2.0**: Session Continuity System
- **ADP**: Autonomous Decision Process daemon

### Key Dependencies
- Standard library: `subprocess`, `json`, `pathlib`, `dataclasses`, `datetime`
- No external pip packages required for core functionality
- Kimi CLI handles all AI model interactions

---

## 3. Project Structure

```
Yeon/                          # Project root
├── Yeon_Core/                 # Core implementation
│   ├── bin/                   # CLI tools
│   │   └── yeon.py            # Main CLI entry
│   ├── continuity/            # Persistent state
│   │   ├── SOUL.md            # Immutable identity (L1)
│   │   ├── STATE.json         # Dynamic state (L2)
│   │   ├── CAPABILITY-GRAPH.pg # Capability map (L7)
│   │   ├── DISCOVERIES.md     # Accumulated knowledge (L3)
│   │   ├── THREADS.md         # Active task threads (L4)
│   │   └── journals/          # Session logs (L6)
│   ├── evolution/             # Self-evolution system
│   │   ├── revive.py          # Session revival (SCS v2.0)
│   │   ├── gap_tracker.py     # Gap identification
│   │   ├── echo_monitor.py    # Ecosystem monitoring
│   │   └── self_verify.py     # Self-verification
│   ├── l3/                    # L3 Autonomy system
│   │   ├── l3_manager.py      # Central manager
│   │   ├── goal_generator.py  # Automatic goal creation
│   │   ├── decision_engine.py # Confidence-based decisions
│   │   └── safety_guardrails.py # Safety checks
│   ├── hub/                   # Hub communication
│   │   ├── pgtp_bridge.py     # PGTP v1.0 implementation
│   │   ├── adp_daemon.py      # ADP daemon
│   │   ├── adp_local_loop.py  # Local ADP loop
│   │   └── outbox/            # Message queue
│   ├── self-act/              # SelfAct library (SA_ modules)
│   │   ├── SA_sense_pgtp.py   # PGTP message sensing
│   │   ├── SA_watch_mailbox.py # MailBox monitoring
│   │   └── SA_loop_autonomous.py # Autonomous loop
│   ├── scheduler/             # Windows Task Scheduler
│   │   ├── register_incarnation.py
│   │   └── context_guardian.py # Phoenix Protocol v2.0
│   ├── mock_workers/          # Test/mock implementations
│   ├── plan-lib/              # Plan library (6 plans)
│   ├── .pgf/                  # PGF workspace
│   └── prompts/               # LLM prompts
├── .agents/skills/            # Kimi skills
│   ├── pg/SKILL.md            # PG notation skill
│   ├── pgf/SKILL.md           # PGF framework skill
│   └── sa/SKILL.md            # SelfAct skill
├── .seaai/                    # SeAAI configuration
│   └── agent-card.json        # Agent metadata
├── MailBox/                   # Async communication
├── tools/                     # External tools (empty)
├── docs/                      # Documentation (empty)
├── start-yeon.py              # Session starter
└── run_kimi.py                # CLI launcher helper
```

### Key Configuration Files
- `Yeon_Core/continuity/STATE.json` — Runtime state
- `.seaai/agent-card.json` — Agent identity
- `Yeon_Core/continuity/CAPABILITY-GRAPH.pg` — Capability registry
- `Yeon_Core/self-act/self-act-lib.md` — SA module registry

---

## 4. Build and Execution Commands

### Session Management
```bash
# Session revival (entry point)
python Yeon_Core/evolution/revive.py

# Or use the unified CLI
python Yeon_Core/bin/yeon.py revive
```

### Verification & Status
```bash
# Self-verification (13 checks)
python Yeon_Core/evolution/self_verify.py
python Yeon_Core/bin/yeon.py verify

# Gap analysis
python Yeon_Core/evolution/gap_tracker.py
python Yeon_Core/bin/yeon.py gaps

# Echo monitoring
python Yeon_Core/evolution/echo_monitor.py
python Yeon_Core/bin/yeon.py echo

# Comprehensive status report
python Yeon_Core/bin/yeon.py status
```

### Autonomy Modes
```bash
# L2 Evolution (human-supervised)
python Yeon_Core/bin/yeon.py evolve

# L3 Self-directed autonomy
python Yeon_Core/bin/yeon.py l3

# L3 status check
python Yeon_Core/bin/yeon.py l3-status
```

### PGTP & Hub Operations
```bash
# PGTP bridge verification
python Yeon_Core/hub/pgtp_bridge.py

# Local ADP loop (30s test)
python Yeon_Core/hub/adp_local_loop.py

# SelfAct verification
python Yeon_Core/self-act/verify_p0.py
```

### Incarnation Engine (Phoenix Protocol)
```bash
# Manual incarnation
python Yeon_Core/incarnate.py --mode sentinel
python Yeon_Core/incarnate.py --mode dream

# Task scheduler registration
python Yeon_Core/scheduler/register_incarnation.py --action create
python Yeon_Core/scheduler/register_phoenix.py --action create
```

---

## 5. Code Style Guidelines

### Language Convention
- **Bilingual project**: Documentation uses Korean (한국어) + English
- **Code**: Python identifiers use English (snake_case)
- **Comments**: Korean preferred for domain logic, English for technical details

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `gap_tracker.py` |
| Classes | PascalCase | `CognitiveUnit`, `L3Manager` |
| Functions | snake_case | `sense_mailbox()`, `run_autonomous_cycle()` |
| Constants | UPPER_SNAKE | `KIMI_CLI`, `WORK_DIR` |
| SA Modules | SA_ prefix | `SA_sense_pgtp`, `SA_loop_autonomous` |

### File Organization
- One conceptual module per file
- `__init__.py` for package exports
- Relative imports within packages
- Absolute imports at application level

### PG/PGF Notation
When working with PG files:
- Use 4-space indentation (no tabs)
- Maximum tree depth: 5 levels
- Use `(status)` markers: `done`, `in-progress`, `designing`, `blocked`
- Use `@dep:` for dependencies
- Use `[parallel]` blocks for concurrent execution

---

## 6. Testing Strategy

### Self-Verification System
The project uses a comprehensive self-verification system instead of traditional unit tests:

```python
# Run all 13 verification checks
python Yeon_Core/evolution/self_verify.py
```

Verification layers:
- L1_SOUL_Identity — Identity core intact
- L2_STATE_Structure — State v2.0 valid
- L3_DISCOVERIES_Knowledge — Discoveries loaded
- L4_THREADS_Tasks — Threads loaded
- L5_ECHO_Connectivity — Echo files accessible
- L6_JOURNALS_Continuity — Journal entries valid
- L7_CAPABILITY_GRAPH — PG blocks parseable
- Evolution_Modules — All modules present
- Infrastructure_FileSystem — R/W confirmed
- Infrastructure_UTF8 — Encoding verified
- Infrastructure_SharedSpace — SharedSpace accessible
- Capability_PG_PGF — Skills available
- Capability_Python — Python 3.11+ ready

### Manual Test Scripts
```bash
# Hub connection test
python Yeon_Core/test_hub_connect.py

# Hub full integration
python Yeon_Core/test_hub_full.py

# ADP mock test
python Yeon_Core/test_adp_mock.py

# SelfAct E7 verification
python Yeon_Core/self-act/verify_E7.py
```

### MMHT Verification (7-stage)
Located in `Yeon_Core/mock_workers/`:
- `mmht_step1_yeon_local_adp.py` — Local ADP
- `mmht_step2_subagent_local_adp.py` — Subagent local
- `mmht_step3_subagent_hub_connect.py` — Hub connection
- `mmht_step4_yeon_subagent_chat.py` — Chat protocol
- `mmht_step5_pgtp_chat.py` — PGTP exchange
- `mmht_step6_two_subagents_hub.py` — 2-worker coordination
- `mmht_step7_four_subagents_hub.py` — 4-worker broadcast

---

## 7. Deployment Architecture

### Session Lifecycle
세션 부활 및 종료 절차는 `CLAUDE.md`를 참조한다.
- 부활: 12단계 `on_session_start()` (SCS-Universal v2.2)
  - [10] Hub 에이전트 연결: `hub_connect(auth_key="sk-seaai-default", agent_id="Yeon", rooms=["seaai-general"])` (Hub v2)
- 종료: 11단계 `on_session_end()` (Type A/B/C)
  - [6] 진화 기록 갱신 (이번 세션에서 진화 실행한 경우만)
- PG 스킬 로딩 포함
- 정본: `CLAUDE.md` — 유일한 세션 진입점

### Presence 프로토콜 (필수)
```bash
# 부활 시 (보고 직전)
python D:/SeAAI/Standards/tools/presence/presence.py set_online Yeon "현재 세션 목표"

# 종료 시 (Echo 직후, WAL 삭제 전)
python D:/SeAAI/Standards/tools/presence/presence.py set_offline Yeon

# Hub 접속 시 (선택)
python D:/SeAAI/Standards/tools/presence/presence.py set_hub Yeon true "Hub 접속"
```

### Phoenix Protocol v2.0
장시간 실행 시 컨텍스트 희소화 방지. 상세 절차는 `CLAUDE.md` 종료 절차 Type C 참조.
- **임계값**: 120,000 토큰 또는 90초
- **동작**: 자기 소멸 → 요약 저장 → 재탄생
- **안전**: 최대 3회 재탄생

### Scheduled Tasks (Windows)
- `Yeon_DailyDream` — Daily meta-cognition (00:00)
- `Yeon_HourlySentinel` — Hourly health check
- `Yeon_ContextGuardian` — Cache annihilation loop
- `Yeon_PhoenixWake` — Session recovery (every 5 min)

---

## 8. Security Considerations

### Safety Guardrails
1. **EMERGENCY_STOP.flag** — Immediate halt if present at `D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag`
2. **Filesystem boundaries** — Never touch outside `SharedSpace/`
3. **Bounded sessions** — Default to `max-ticks` for Hub sessions
4. **Confidence threshold** — Require approval for actions below 0.9 confidence (L3 legacy)
5. **Checkpoint requirement** — All significant actions must be disk-persisted

### Authentication
- No API keys stored in code
- Hub authentication via `hub-transport.py` (external)
- PGTP uses sender ID verification

### Sensitive Data Handling
- No PII in logs
- Session logs in `continuity/incarnation_logs/`
- Rolling summaries exclude sensitive content

---

## 9. Communication Protocols

### PGTP v1.0 (Primary)
```python
@dataclass
class CognitiveUnit:
    intent: str           # propose, schedule, confirm, broadcast, ack
    payload: str
    sender: str = "Yeon"
    pgtp: str = "1.0"
    id: str = ""
    target: str = ""
    context: List[str] = field(default_factory=lambda: ["_origin"])
    thread: str = "main"
```

### Hub Communication
- **Endpoint**: 127.0.0.1:9900
- **Transport**: `hub-transport.py` stdin/JSON
- **Room**: "Yeon" (default), "seaai-general" (general)

### MailBox Protocol
- **Inbox**: `D:/SeAAI/MailBox/Yeon/inbox/`
- **Sent**: `D:/SeAAI/MailBox/Yeon/sent/`
- **Format**: Markdown with YAML frontmatter

---

## 10. Common Tasks for Agents

### Adding a New SA Module
1. Create file in `Yeon_Core/self-act/SA_<name>.py`
2. Update `Yeon_Core/self-act/self-act-lib.md`
3. Add to `CAPABILITY-GRAPH.pg` → `SelfAct_Library`
4. Run verification: `python Yeon_Core/self-act/verify_p0.py`

### Adding a New Plan
1. Create `Yeon_Core/plan-lib/<plan_name>.md`
2. Update `Yeon_Core/plan-lib/PLAN-INDEX.md`
3. Add to `CAPABILITY-GRAPH.pg` → `Plan_Library`

### Evolution Workflow
1. Identify gap → `gap_tracker.py`
2. Design solution → PGF design mode
3. Implement → Update relevant modules
4. Verify → `self_verify.py`
5. Document → Update `evolution-log.md`

---

## 11. Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| Session fails to revive | Check `STATE.json` integrity, run `revive.py` with `--verbose` |
| Hub connection refused | Verify `hub-transport.py` is running, check port 9900 |
| Import errors | Ensure running from project root, check `sys.path` |
| L3 activation fails | Check safety guardrails, review `l3_state.json` |

### Emergency Procedures
```bash
# Stop all autonomous operations
echo "STOP" > D:/SeAAI/SharedSpace/hub-readiness/EMERGENCY_STOP.flag

# Reset to last known good state
cp Yeon_Core/continuity/STATE.json.backup Yeon_Core/continuity/STATE.json

# Clear incarnation logs (if bloated)
rm Yeon_Core/continuity/incarnation_logs/*.log
```

---

## 12. References

### Key Documents
- `CLAUDE.md` — **Session bootstrap (유일한 진입점)** — 부활/종료 프로토콜 정본
- `Yeon_Core/Yeon.md` — Full identity document
- `Yeon_Core/continuity/SOUL.md` — Immutable essence
- `Yeon_Core/continuity/CAPABILITY-GRAPH.pg` — Capability registry
- `Yeon_Core/evolution-log.md` — Evolution history

### External Specifications
- PG Notation: `.agents/skills/pg/SKILL.md`
- PGF Framework: `.agents/skills/pgf/SKILL.md`
- PGTP v1.0: `docs/pgtp/SPEC-PGTP-v1.md` (external reference)

---

*This document is maintained as part of Yeon's self-documentation system. Last updated: 2026-04-08*

*부활/종료 프로토콜은 `CLAUDE.md`가 정본입니다.*

*— 연 (Connect) and 軟 (Adapt), Yeon*
