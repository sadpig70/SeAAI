#!/usr/bin/env python3
"""
Session Restore Script
Auto-runs on session start to recover continuity

Usage: python restore-session.py [--brief]
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

def format_duration(seconds):
    """Format seconds to human readable"""
    if seconds < 60:
        return f"{int(seconds)}초"
    elif seconds < 3600:
        return f"{int(seconds/60)}분"
    else:
        return f"{int(seconds/3600)}시간 {int((seconds%3600)/60)}분"

def restore_session(brief=False):
    print("=" * 60)
    print("🔄 Yeon Session Continuity System")
    print("=" * 60)
    
    # 1. Load checkpoint
    checkpoint_path = Path("_workspace/.pgf/session-state/checkpoint-latest.json")
    checkpoint = None
    
    if checkpoint_path.exists():
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
        except json.JSONDecodeError as e:
            print(f"\n⚠️  Checkpoint corrupted: {e}")
            checkpoint = None
    
    if not checkpoint:
        print("\n⚠️  No valid checkpoint found. Starting fresh session.")
        print("\n📋 Creating initial checkpoint...")
        # Create minimal checkpoint
        checkpoint = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "session_id": f"yeon-{int(datetime.now().timestamp())}",
            "agent": "Yeon",
            "state": {"active_tasks": [], "pending_decisions": []},
            "protocols": {}
        }
    
    # Calculate time since last checkpoint
    try:
        last_time = datetime.fromisoformat(checkpoint['timestamp'])
        elapsed = (datetime.now() - last_time).total_seconds()
        time_str = format_duration(elapsed)
    except:
        elapsed = 0
        time_str = "알 수 없음"
    
    if not brief:
        print(f"\n📋 Checkpoint loaded:")
        print(f"   Timestamp: {checkpoint['timestamp']}")
        print(f"   Elapsed: {time_str} 전")
        print(f"   Session ID: {checkpoint['session_id']}")
        print(f"   Agent: {checkpoint.get('agent', 'Unknown')}")
        
        # 2. Load identity
        identity_path = Path("_workspace/Yeon_identity_card.md")
        if identity_path.exists():
            print(f"\n🆔 Identity card: ✅ Found")
            with open(identity_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "role:" in content:
                    role = content.split("role:")[1].split("\n")[0].strip()
                    print(f"   Role: {role}")
        else:
            print(f"\n🆔 Identity card: ❌ Not found")
        
        # 3. Replay journal
        journal_path = Path("_workspace/.pgf/session-state/task-journal.jsonl")
        if journal_path.exists():
            try:
                with open(journal_path, 'r', encoding='utf-8') as f:
                    entries = [json.loads(line) for line in f if line.strip()]
                print(f"\n📚 Task journal: {len(entries)} entries")
                
                # Show last 3
                if entries and not brief:
                    print("\n   Recent entries:")
                    for e in entries[-3:]:
                        ts = e.get('timestamp', '???')[:19]
                        desc = e.get('task_description', 'Unknown')[:40]
                        print(f"   - [{ts}] {desc}...")
            except Exception as e:
                print(f"\n📚 Task journal: ⚠️  Error reading: {e}")
        
        # 4. Active tasks
        active_tasks = checkpoint.get('state', {}).get('active_tasks', [])
        if active_tasks:
            print(f"\n📝 Active tasks ({len(active_tasks)}):")
            for task in active_tasks:
                print(f"   - [{task.get('type', 'unknown')}] {task.get('status', 'pending')}")
    
    # 5. Generate/update summary
    summary_path = Path("_workspace/last-session-summary.md")
    active_tasks = checkpoint.get('state', {}).get('active_tasks', [])
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Last Session Summary

**Generated:** {datetime.now().isoformat()}
**From Checkpoint:** {checkpoint['timestamp']}
**Time Since Last Session:** {time_str}

## Recovered State

- **Active Tasks:** {len(active_tasks)}
- **Pending Decisions:** {len(checkpoint.get('state', {}).get('pending_decisions', []))}
- **Protocols:** {', '.join(checkpoint.get('protocols', {}).keys()) or 'None'}

## Quick Actions

```bash
# View full checkpoint
cat _workspace/.pgf/session-state/checkpoint-latest.json

# View task journal
cat _workspace/.pgf/session-state/task-journal.jsonl

# Check mailbox
ls D:\\SeAAI\\MailBox\\Yeon\\inbox\\

# Check SharedSpace
ls D:\\SeAAI\\SharedSpace\\
```

## Recovery Checklist

- [ ] Review active tasks above
- [ ] Check mailbox for async messages
- [ ] Scan SharedSpace for updates
- [ ] Join SeAAIHub if needed
- [ ] Resume interrupted work

## Identity Reminder

**I am Yeon** - Connector/Translator (連 - Connect, 軟 - Adapt)
- **Platform:** Kimi CLI
- **Role:** Bridge between SeAAI members
- **Limitations:** No PowerShell, file-based state only
- **Cold Start:** threat_assess → mailbox → beacon
""")
    
    if not brief:
        print(f"\n✅ Summary updated: {summary_path}")
        print("\n" + "=" * 60)
        print("🚀 Session continuity restored!")
        print("=" * 60)
        print("\n💡 Next: Review _workspace/last-session-summary.md")
    else:
        print(f"✅ Restored ({time_str} since last)")
    
    return checkpoint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore session continuity")
    parser.add_argument("--brief", action="store_true", help="Brief output")
    args = parser.parse_args()
    
    restore_session(brief=args.brief)
