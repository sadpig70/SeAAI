"""
SeAAI Presence — 멤버 온라인/허브 접속 상태 관리

사용법:
    python presence.py list_all
    python presence.py list_online
    python presence.py get <member>
    python presence.py set_online <member> [activity]
    python presence.py set_offline <member>
    python presence.py set_hub <member> <true|false> [activity]
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

MEMBERS = ["Aion", "ClNeo", "Navelon", "Synerion", "Terron", "Yeon"]
PRESENCE_DIR = Path(r"D:\SeAAI\SharedSpace\.scs\presence")


# ── 유틸 ─────────────────────────────────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def staleness(last_seen: str | None) -> str:
    if not last_seen:
        return "unknown"
    try:
        ts = datetime.fromisoformat(last_seen)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if h < 1:    return "방금"
        if h < 24:   return f"{int(h)}h 전"
        return f"{int(h / 24)}d 전"
    except Exception:
        return "unknown"


def load(member: str) -> dict | None:
    p = PRESENCE_DIR / f"{member}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(data: dict) -> None:
    PRESENCE_DIR.mkdir(parents=True, exist_ok=True)
    (PRESENCE_DIR / f"{data['member']}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def check(member: str) -> str | None:
    return None if member in MEMBERS else f"알 수 없는 멤버: {member}  (가능: {', '.join(MEMBERS)})"


def out(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 명령 ─────────────────────────────────────────────────────────────────────

def cmd_list_all():
    rows = []
    for m in MEMBERS:
        p = load(m)
        if p:
            rows.append({
                "member":        p["member"],
                "status":        p.get("status", "unknown"),
                "hub_connected": p.get("hub_connected", False),
                "last_seen":     staleness(p.get("last_seen")),
                "activity":      p.get("activity", "")
            })
        else:
            rows.append({"member": m, "status": "unknown",
                         "hub_connected": False, "last_seen": "파일 없음", "activity": ""})
    out({"members": rows})


def cmd_list_online():
    online = [
        {"member": p["member"], "hub_connected": p.get("hub_connected", False),
         "since": staleness(p.get("session_start")), "activity": p.get("activity", "")}
        for m in MEMBERS
        if (p := load(m)) and p.get("status") == "online"
    ]
    out({"count": len(online), "online": online})


def cmd_get(member: str):
    if err := check(member):
        out({"error": err}); return
    p = load(member)
    if not p:
        out({"member": member, "status": "unknown", "note": "presence 파일 없음"}); return
    p["last_seen_label"] = staleness(p.get("last_seen"))
    out(p)


def cmd_set_online(member: str, activity: str = ""):
    if err := check(member):
        out({"error": err}); return
    existing = load(member) or {}
    now = now_iso()
    save({
        "schema_version": "1.0",
        "member":         member,
        "status":         "online",
        "session_start":  now,
        "last_seen":      now,
        "hub_connected":  False,
        "activity":       activity or existing.get("activity", "")
    })
    out({"ok": True, "member": member, "status": "online", "timestamp": now})


def cmd_set_offline(member: str):
    if err := check(member):
        out({"error": err}); return
    existing = load(member) or {}
    now = now_iso()
    save({
        "schema_version": "1.0",
        "member":         member,
        "status":         "offline",
        "session_start":  None,
        "last_seen":      now,
        "hub_connected":  False,
        "activity":       existing.get("activity", "")
    })
    out({"ok": True, "member": member, "status": "offline", "timestamp": now})


def cmd_set_hub(member: str, connected: bool, activity: str = ""):
    if err := check(member):
        out({"error": err}); return
    p = load(member)
    if not p:
        out({"error": f"{member} presence 파일 없음. set_online 먼저 실행 필요."}); return
    p["hub_connected"] = connected
    p["last_seen"] = now_iso()
    if activity:
        p["activity"] = activity
    save(p)
    out({"ok": True, "member": member, "hub_connected": connected})


# ── 진입점 ───────────────────────────────────────────────────────────────────

def usage():
    print(__doc__)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        usage()

    cmd = args[0]

    if cmd == "list_all":
        cmd_list_all()

    elif cmd == "list_online":
        cmd_list_online()

    elif cmd == "get":
        if len(args) < 2: usage()
        cmd_get(args[1])

    elif cmd == "set_online":
        if len(args) < 2: usage()
        cmd_set_online(args[1], " ".join(args[2:]))

    elif cmd == "set_offline":
        if len(args) < 2: usage()
        cmd_set_offline(args[1])

    elif cmd == "set_hub":
        if len(args) < 3: usage()
        connected = args[2].lower() in ("true", "1", "yes")
        cmd_set_hub(args[1], connected, " ".join(args[3:]))

    else:
        print(f"알 수 없는 명령: {cmd}")
        usage()


if __name__ == "__main__":
    main()
