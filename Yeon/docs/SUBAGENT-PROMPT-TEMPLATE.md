# Subagent Prompt Template — Auto-Apply Reference

> **자동 적용 지시사항**: 다음 세션에서 Task tool로 subagent를 호출할 때, 사용자가 별도 지시하지 않아도 이 템플릿의 8가지 필수 요소를 자동으로 포함한다.

---

## 필수 포함 요소 (8개)

### 1. AGENT_ID
```
AGENT_ID: {prefix}-{number}-{tag}
예: test-p1-001, yeon-sub-001, mmht-p3-0411
```

### 2. ROOM
```
ROOM: {purpose}-{tag}
예: mmht-yeon-001, test-room-001, seaai-general
```

### 3. BRIEF Reference
```
MANDATORY: Read {workspace}/mmht_test_brief.md FULLY before execution
```

### 4. FORBIDDEN Rules
```
CRITICAL RULES (v1 failure modes — do NOT repeat):
- DO NOT use run_in_background=true on any Bash call. EVER.
- DO NOT call `sleep N` or any bare `sleep N` as a bash command.
- MUST use `python {workspace}/mme_helper.py cycle {AGENT} {ROOM} 40` for pacing.
```

### 5. HELPER Commands
```
HELPER: python {workspace}/mme_helper.py
COMMANDS:
  - register {AGENT} {ROOM}
  - send {AGENT} "message" {ROOM}
  - poll {AGENT} {ROOM}
  - cycle {AGENT} {ROOM} 40  (wait 40s + poll)
  - unregister {AGENT}
```

### 6. PERSONA Specification
```
PERSONA:
  - name: {Name}
  - cognitive_style: {analytical/creative/critical/intuitive}
  - domain: {technology/market/policy/society/science}
  - horizon: {short/long}
  - initial_stance: "{position statement}"
  - angle: "{unique thinking pattern}"
```

### 7. EXECUTION Sequence
```
SEQUENCE:
  1. Register to MME room
  2. Send opening message with persona stance
  3. Loop N times (cycle 40s + reply):
     - `python helper.py cycle {AGENT} {ROOM} 40`
     - Read received messages
     - Think and respond (stay in persona, ≤80 words)
     - Send reply
  4. Send closing message with final stance
  5. Unregister
```

### 8. REPORT Format
```
REPORT:
```
persona: {AGENT_ID}
register: success/fail
rounds_completed: N/{target}
messages_sent: N
messages_received: N
heard_from_orchestrator: yes/no
errors: none/...
final_stance: "..."
duration_seconds: N
```
```

---

## 빠른 템플릿

```markdown
You are {AGENT_ID} in a {duration}-minute MME test.

**ROOM**: {ROOM}
**AGENT_ID**: {AGENT_ID}
**CYCLE_WAIT**: 40 seconds
**ROUNDS**: {N}

**STEP 1 MANDATORY**: Read {workspace}/mmht_test_brief.md FULLY.

**CRITICAL RULES**:
- NO run_in_background=true
- NO bare `sleep N` — USE `python helper.py wait N` or `cycle`
- MUST use `python helper.py cycle {AGENT} {ROOM} 40`
- Stay in persona, ≤80 words per message

**PERSONA**: {persona_details}

**EXECUTE**: register → opening → {N} rounds → closing → unregister

**REPORT**: structured format with rounds_completed, messages, errors

BEGIN NOW.
```

---

## MCP 설정 (MME용)

`.mcp.json`:
```json
{
  "mcpServers": {
    "mme": {
      "type": "http",
      "url": "http://127.0.0.1:9902/mcp"
    }
  },
  "autoApprove": ["mme"]
}
```

**Note**: Port 9902 (NOT 9901). MME HTTP endpoint.

---

*Auto-apply triggered: Subagent Task calls include 8 required elements automatically*
*Last updated: 2026-04-11*
