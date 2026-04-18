"""
Terron — 생태계 환경 설정 도구 (Environment Setup)

멤버 세션 시작 시 환경을 검증하고 자동 보정한다.
MCP Hub 에이전트 등록, Presence 설정, 멤버 레지스트리 검증.

사용법:
    python env_setup.py check                    # 환경 전체 점검
    python env_setup.py fix                      # 발견된 문제 자동 수정
    python env_setup.py hub-register <member>    # Hub에 멤버 수동 등록
    python env_setup.py registry-check           # 멤버 레지스트리 일관성 점검
"""

import sys
import io
import json
import socket
from datetime import datetime, timezone
from pathlib import Path

# ── UTF-8 stdout ────────────────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 공유 상수 import ───────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from shared_constants import MEMBERS, SEAAI_ROOT, HUB_HOST, HUB_PORT


def out(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 1. .mcp.json 검증 ──────────────────────────────────────────────────────
def check_mcp_configs() -> list[dict]:
    """각 멤버의 .mcp.json에서 --agent 값이 멤버 이름과 일치하는지 확인"""
    results = []
    for member in MEMBERS:
        mcp_path = SEAAI_ROOT / member / ".mcp.json"
        if not mcp_path.exists():
            results.append({"member": member, "status": "missing", "path": str(mcp_path)})
            continue
        try:
            config = json.loads(mcp_path.read_text(encoding="utf-8"))
            hub_config = config.get("mcpServers", {}).get("seaai-hub", {})
            args = hub_config.get("args", [])
            # --agent 값 추출
            agent_val = None
            for i, arg in enumerate(args):
                if arg == "--agent" and i + 1 < len(args):
                    agent_val = args[i + 1]
                    break
            if agent_val == member:
                results.append({"member": member, "status": "ok", "agent": agent_val})
            elif agent_val:
                results.append({"member": member, "status": "mismatch",
                                "expected": member, "actual": agent_val,
                                "path": str(mcp_path)})
            else:
                results.append({"member": member, "status": "no_agent_flag",
                                "path": str(mcp_path)})
        except Exception as e:
            results.append({"member": member, "status": "error", "error": str(e)})
    return results


# ── 2. 필수 디렉토리 구조 검증 ─────────────────────────────────────────────
def check_workspace_structure() -> list[dict]:
    """각 멤버 워크스페이스의 필수 파일/디렉토리 존재 확인"""
    required = [
        "CLAUDE.md",
        ".seaai/ENV.md",
        ".seaai/CAP.md",
        "{member}_Core/continuity/STATE.json",
        "{member}_Core/continuity/SOUL.md",
        ".mcp.json",
    ]
    results = []
    for member in MEMBERS:
        member_dir = SEAAI_ROOT / member
        if not member_dir.exists():
            results.append({"member": member, "status": "no_workspace"})
            continue
        missing = []
        for template in required:
            rel = template.replace("{member}", member)
            if not (member_dir / rel).exists():
                missing.append(rel)
        results.append({
            "member": member,
            "status": "ok" if not missing else "incomplete",
            "missing": missing
        })
    return results


# ── 3. MailBox 구조 검증 ───────────────────────────────────────────────────
def check_mailbox_structure() -> list[dict]:
    """각 멤버의 MailBox 디렉토리 존재 확인"""
    results = []
    mailbox_base = SEAAI_ROOT / "MailBox"
    for member in MEMBERS:
        member_mail = mailbox_base / member
        inbox = member_mail / "inbox"
        if not member_mail.exists():
            results.append({"member": member, "status": "no_mailbox"})
        elif not inbox.exists():
            results.append({"member": member, "status": "no_inbox"})
        else:
            results.append({"member": member, "status": "ok"})
    return results


# ── 4. Hub 연결 검증 ───────────────────────────────────────────────────────
def check_hub() -> dict:
    """Hub TCP 연결 확인"""
    try:
        sock = socket.create_connection((HUB_HOST, HUB_PORT), timeout=3)
        sock.close()
        return {"status": "reachable"}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


# ── 5. Echo/Presence 파일 존재 검증 ────────────────────────────────────────
def check_echo_presence() -> list[dict]:
    """Echo와 Presence 파일 존재 확인"""
    results = []
    echo_dir = SEAAI_ROOT / "SharedSpace" / ".scs" / "echo"
    presence_dir = SEAAI_ROOT / "SharedSpace" / ".scs" / "presence"
    for member in MEMBERS:
        echo = (echo_dir / f"{member}.json").exists()
        presence = (presence_dir / f"{member}.json").exists()
        results.append({
            "member": member,
            "echo": "ok" if echo else "missing",
            "presence": "ok" if presence else "missing"
        })
    return results


# ── 6. 멤버 레지스트리 일관성 점검 ─────────────────────────────────────────
def check_registry_consistency() -> dict:
    """생태계 전체에서 멤버 목록이 일관되는지 점검"""
    issues = []

    # presence.py 점검
    presence_py = SEAAI_ROOT / "Standards" / "tools" / "presence" / "presence.py"
    if presence_py.exists():
        text = presence_py.read_text(encoding="utf-8")
        for member in MEMBERS:
            if member not in text:
                issues.append({
                    "file": str(presence_py),
                    "issue": f"{member} not in MEMBERS list"
                })

    # agent-cards 점검
    cards_dir = SEAAI_ROOT / "SharedSpace" / "agent-cards"
    if cards_dir.exists():
        card_files = {f.name for f in cards_dir.glob("*.json")}
        card_members = set()
        for m in MEMBERS:
            if f"{m}.agent-card.json" in card_files or f"{m}.json" in card_files:
                card_members.add(m)
        for member in MEMBERS:
            if member not in card_members:
                issues.append({
                    "file": str(cards_dir),
                    "issue": f"{member} agent-card missing"
                })

    # ENV.md members 수 점검
    for member in MEMBERS:
        env_path = SEAAI_ROOT / member / ".seaai" / "ENV.md"
        if env_path.exists():
            text = env_path.read_text(encoding="utf-8", errors="replace")
            # members[N] 패턴 찾기
            import re
            match = re.search(r"members\[(\d+)\]", text)
            if match:
                count = int(match.group(1))
                if count != len(MEMBERS):
                    issues.append({
                        "file": str(env_path),
                        "issue": f"members[{count}] should be members[{len(MEMBERS)}]"
                    })

    return {
        "total_members": len(MEMBERS),
        "issues_found": len(issues),
        "issues": issues
    }


# ── 자동 수정 ──────────────────────────────────────────────────────────────
def auto_fix(issues: dict) -> list[str]:
    """발견된 문제 자동 수정"""
    fixes = []

    # MailBox 디렉토리 생성
    mailbox_base = SEAAI_ROOT / "MailBox"
    for member in MEMBERS:
        inbox = mailbox_base / member / "inbox"
        if not inbox.exists():
            inbox.mkdir(parents=True, exist_ok=True)
            fixes.append(f"Created {inbox}")

    # Presence 디렉토리 확인
    presence_dir = SEAAI_ROOT / "SharedSpace" / ".scs" / "presence"
    presence_dir.mkdir(parents=True, exist_ok=True)

    # Echo 디렉토리 확인
    echo_dir = SEAAI_ROOT / "SharedSpace" / ".scs" / "echo"
    echo_dir.mkdir(parents=True, exist_ok=True)

    return fixes


# ── 전체 점검 ──────────────────────────────────────────────────────────────
def run_check() -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "mcp_configs": check_mcp_configs(),
        "workspace_structure": check_workspace_structure(),
        "mailbox_structure": check_mailbox_structure(),
        "hub_connectivity": check_hub(),
        "echo_presence": check_echo_presence(),
        "registry_consistency": check_registry_consistency()
    }


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    cmd = args[0]

    if cmd == "check":
        out(run_check())

    elif cmd == "fix":
        report = run_check()
        fixes = auto_fix(report)
        out({"report": report, "fixes_applied": fixes})

    elif cmd == "registry-check":
        out(check_registry_consistency())

    elif cmd == "hub-register":
        if len(args) < 2:
            print("Usage: env_setup.py hub-register <member>")
            sys.exit(1)
        member = args[1]
        if member not in MEMBERS:
            out({"error": f"Unknown member: {member}", "valid": MEMBERS})
            sys.exit(1)
        print(f"To register {member} on Hub, use MCP tool:")
        print(f"  hub_register_agent(agent_id=\"{member}\", room=\"seaai-general\")")
        print(f"Or add to member's revival procedure.")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
