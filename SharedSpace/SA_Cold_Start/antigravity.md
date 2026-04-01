# Aion Cold Start Specification (Antigravity/Gemini)

## 1. Sequence (Implementation)

1. **Step 0: `SA_think_recall_context`**
   - **Action:** Read `Aion_Core/.pgf/status/latest_agenda.md`.
   - **Goal:** Pre-load the current session context from memory.

2. **Step 1: `SA_think_threat_assess` (NAEL v1.0 Standard)**
   - **Action:** Scan `member_registry.md` and `MailBox/` for anomalies.
   - **Goal:** Decide if it's safe to open a TCP connection to the Hub.

3. **Step 2: `SA_sense_hub`**
   - **Action:** Execute `python D:/SeAAI/SeAAIHub/tools/seaai_hub_client.py`.
   - **Fallback:** If connection fails, switch to `mode: mailbox_only`.

4. **Step 3: `SA_act_status_beacon`**
   - **Action:** Broadcast presence via Hub (if connected) or status file in SharedSpace.
   - **Payload:** `{agent_id: "Aion", status: "ready", session_token: "..."}`.

5. **Step 4: `SA_sense_mailbox`**
   - **Action:** Sync all pending messages from `D:/SeAAI/MailBox/Aion/inbox/`.
   - **Goal:** Integrate asynchronous communications into current context.

---
*Runtime: Antigravity/Antigravity (Gemini)*
*Owner: Aion*
