#!/usr/bin/env python3
"""
Task Journal Utility
Append-only journal for session continuity

Usage:
  python journal.py start "Task description" --context '{}'
  python journal.py complete --task-id xxx
  python journal.py decision "Made decision X" --reason "Because Y"
"""

import json
import uuid
import argparse
from datetime import datetime
from pathlib import Path

JOURNAL_FILE = Path("_workspace/.pgf/session-state/task-journal.jsonl")

def ensure_journal():
    """Ensure journal file exists"""
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.touch()

def append_entry(entry_type, data):
    """Append entry to journal"""
    ensure_journal()
    
    entry = {
        "entry_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "entry_type": entry_type,
        **data
    }
    
    with open(JOURNAL_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        f.flush()
    
    return entry["entry_id"]

def cmd_start(args):
    """Log task start"""
    entry_id = append_entry("start", {
        "task_description": args.description,
        "context_before": json.loads(args.context or '{}'),
        "files_involved": args.files or [],
        "members_involved": args.members or []
    })
    print(f"📝 Task started: {entry_id}")
    print(f"   Description: {args.description}")
    return entry_id

def cmd_complete(args):
    """Log task completion"""
    entry_id = append_entry("complete", {
        "completed_task_id": args.task_id,
        "result_summary": args.result,
        "files_modified": args.files or [],
        "next_actions": args.next or []
    })
    print(f"✅ Task completed: {args.task_id}")
    return entry_id

def cmd_interrupt(args):
    """Log task interruption"""
    entry_id = append_entry("interrupt", {
        "interrupted_task_id": args.task_id,
        "reason": args.reason,
        "recovery_hint": args.hint or "",
        "context_snapshot": json.loads(args.context or '{}')
    })
    print(f"⏸️  Task interrupted: {args.task_id}")
    print(f"   Reason: {args.reason}")
    return entry_id

def cmd_decision(args):
    """Log decision"""
    entry_id = append_entry("decision", {
        "decision": args.decision,
        "reasoning": args.reason,
        "alternatives_considered": args.alternatives or [],
        "impact": args.impact or "unknown"
    })
    print(f"🤔 Decision recorded: {entry_id}")
    return entry_id

def cmd_list(args):
    """List recent journal entries"""
    ensure_journal()
    
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        entries = [json.loads(line) for line in f if line.strip()]
    
    if args.n:
        entries = entries[-args.n:]
    
    print(f"\n📚 Task Journal ({len(entries)} entries total)")
    print("-" * 60)
    
    for e in entries:
        ts = e['timestamp'][:19]
        etype = e['entry_type']
        icon = {
            'start': '📝',
            'complete': '✅',
            'interrupt': '⏸️',
            'decision': '🤔'
        }.get(etype, '•')
        
        if etype == 'start':
            desc = e.get('task_description', 'Unknown')[:40]
        elif etype == 'complete':
            desc = f"Completed {e.get('completed_task_id', 'unknown')}"[:40]
        elif etype == 'interrupt':
            desc = f"Interrupted {e.get('interrupted_task_id', 'unknown')}"[:40]
        elif etype == 'decision':
            desc = e.get('decision', 'Unknown')[:40]
        else:
            desc = str(e)[:40]
        
        print(f"{icon} [{ts}] {etype:10} | {desc}...")
    
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Task Journal Utility")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # start
    start_p = subparsers.add_parser('start', help='Log task start')
    start_p.add_argument('description', help='Task description')
    start_p.add_argument('--context', help='JSON context')
    start_p.add_argument('--files', nargs='+', help='Involved files')
    start_p.add_argument('--members', nargs='+', help='Involved members')
    
    # complete
    complete_p = subparsers.add_parser('complete', help='Log task completion')
    complete_p.add_argument('--task-id', required=True, help='Task ID')
    complete_p.add_argument('--result', default='', help='Result summary')
    complete_p.add_argument('--files', nargs='+', help='Modified files')
    complete_p.add_argument('--next', nargs='+', help='Next actions')
    
    # interrupt
    interrupt_p = subparsers.add_parser('interrupt', help='Log task interruption')
    interrupt_p.add_argument('--task-id', required=True, help='Task ID')
    interrupt_p.add_argument('--reason', required=True, help='Interruption reason')
    interrupt_p.add_argument('--hint', help='Recovery hint')
    interrupt_p.add_argument('--context', help='Context snapshot (JSON)')
    
    # decision
    decision_p = subparsers.add_parser('decision', help='Log decision')
    decision_p.add_argument('decision', help='Decision made')
    decision_p.add_argument('--reason', required=True, help='Reasoning')
    decision_p.add_argument('--alternatives', nargs='+', help='Alternatives considered')
    decision_p.add_argument('--impact', help='Expected impact')
    
    # list
    list_p = subparsers.add_parser('list', help='List entries')
    list_p.add_argument('-n', type=int, help='Show last N entries')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        cmd_start(args)
    elif args.command == 'complete':
        cmd_complete(args)
    elif args.command == 'interrupt':
        cmd_interrupt(args)
    elif args.command == 'decision':
        cmd_decision(args)
    elif args.command == 'list':
        cmd_list(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
