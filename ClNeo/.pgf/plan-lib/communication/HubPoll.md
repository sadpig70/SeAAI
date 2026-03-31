# plan-lib/communication/HubPoll.md
# @sig: since_ts → MessageSet, latest_ts
# @scale: ATOM | @cost: LOW | @ver: 1.0

```
HubPoll
    @input:  since_ts (float), seen_ids (set)
    @output: new_msgs (MessageList), latest_ts (float)

    Poll
        skill_dir = "C:/Users/sadpig70/.claude/skills/hub-adp"
        raw = Bash(f"PYTHONIOENCODING=utf-8 python {skill_dir}/hub_poll.py --since-ts {since_ts}")
        all_msgs  = raw.messages
        latest_ts = raw.latest_ts

    Filter
        @dep: Poll
        new_msgs = [m for m in all_msgs if m.id not in seen_ids]
        seen_ids.update(m.id for m in new_msgs)

    Triage
        @dep: Filter
        for msg in new_msgs:
            msg.priority = AI_triage(msg)
            // CREATOR(10) > REAL_MEMBER(8) > NORMAL(5) > DISMISS(0)
        new_msgs = [m for m in new_msgs if m.priority > 0]
        new_msgs.sort(key=lambda m: m.priority, reverse=True)

    @output: { new_msgs: new_msgs, latest_ts: latest_ts }
```
