#!/usr/bin/env python3
"""
Session Checkpoint Creator
Usage: python create-checkpoint.py [--force]

Creates atomic checkpoint of current session state for continuity.
"""

import json
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

def collect_active_tasks():
    """Collect currently active tasks from workspace"""
    tasks = []
    
    # Check for active ADP
    adp_log = Path("Yeon_Core/.pgf/adp_live")
    if adp_log.exists():
        latest_logs = sorted(adp_log.glob("adp_*.jsonl"), reverse=True)
        if latest_logs:
            tasks.append({
                "type": "ADP",
                "status": "running" if len(latest_logs) > 0 else "stopped",
                "log_file": str(latest_logs[0])
            })
    
    # Check mailbox
    mailbox = Path("D:/SeAAI/MailBox/Yeon/inbox")
    if mailbox.exists():
        unread = list(mailbox.glob("*.md"))
        if unread:
            tasks.append({
                "type": "mailbox",
                "unread_count": len(unread),
                "latest": str(unread[-1])
            })
    
    # Check SharedSpace
    shared = Path("D:/SeAAI/SharedSpace")
    if shared.exists():
        recent_files = sorted(shared.rglob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        tasks.append({
            "type": "sharedspace",
            "recent_files": [str(f.relative_to(shared)) for f in recent_files]
        })
    
    return tasks

def collect_protocol_versions():
    """Collect active protocol versions"""
    return {
        "ShadowMode": "v1.0",
        "SeAAIChat": "v1.0", 
        "PGF": "v2.5",
        "SCS": "v1.0"
    }

def create_checkpoint(force=False):
    checkpoint_dir = Path("_workspace/.pgf/session-state")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    latest = checkpoint_dir / "checkpoint-latest.json"
    
    # Check if checkpoint is too fresh (< 5 min)
    if not force and latest.exists():
        mtime = latest.stat().st_mtime
        if time.time() - mtime < 300:
            print("Checkpoint too fresh (< 5 min). Use --force to override.")
            return None
    
    checkpoint = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "session_id": f"yeon-{int(time.time())}",
        "agent": "Yeon",
        "platform": "Kimi CLI",
        "workspace": "D:\\SeAAI\\Yeon",
        "state": {
            "active_tasks": collect_active_tasks(),
            "pending_decisions": [],
            "open_files": [],
            "last_directory": str(Path.cwd()),
        },
        "protocols": collect_protocol_versions(),
        "environment": {
            "powershell_available": False,
            "tcp_client_available": True,
            "encoding": "utf-8",
            "hub_port": 9900
        }
    }
    
    # Atomic write
    temp = checkpoint_dir / "checkpoint-temp.json"
    with open(temp, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    # Backup old
    if latest.exists():
        backup_dir = checkpoint_dir / "checkpoint-backup"
        backup_dir.mkdir(exist_ok=True)
        backup = backup_dir / f"checkpoint-{int(time.time())}.json"
        import shutil
        shutil.copy(latest, backup)
        print(f"Backup created: {backup}")
    
    # Replace
    temp.replace(latest)
    
    print(f"✅ Checkpoint created: {latest}")
    print(f"   Timestamp: {checkpoint['timestamp']}")
    print(f"   Session ID: {checkpoint['session_id']}")
    print(f"   Active tasks: {len(checkpoint['state']['active_tasks'])}")
    
    return checkpoint

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create session checkpoint")
    parser.add_argument("--force", action="store_true", help="Force checkpoint even if fresh")
    args = parser.parse_args()
    
    create_checkpoint(force=args.force)
