"""SA_self_reflect — Self-reflection engine for autonomous evolution."""
import json
import re
from datetime import datetime
from pathlib import Path

CORE_DIR = Path("D:/SeAAI/Yeon/Yeon_Core")
DISCOVERIES = CORE_DIR / "continuity" / "DISCOVERIES.md"
STATE_PATH = CORE_DIR / "continuity" / "STATE.json"


def scan_evolution_log(last_n: int = 5) -> list:
    log_path = CORE_DIR / "evolution-log.md"
    if not log_path.exists():
        return []
    text = log_path.read_text(encoding="utf-8")
    matches = re.findall(r"## Evolution #(\S+):\s*(.+?)\n", text)
    return [f"E{m[0]}: {m[1].strip()}" for m in matches[-last_n:]]


def scan_capabilities() -> dict:
    if not STATE_PATH.exists():
        return {}
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {
        "evolution_modules": data.get("evolution_state", {}).get("evolution_modules", []),
        "capabilities": data.get("evolution_state", {}).get("autonomy", {}).get("capabilities", []),
    }


def scan_selfact() -> int:
    lib_path = CORE_DIR / "self-act" / "self-act-lib.md"
    if not lib_path.exists():
        return 0
    text = lib_path.read_text(encoding="utf-8")
    # Count L1 primitive rows
    return len(re.findall(r"\|\s*`SA_", text))


def scan_plan_library() -> int:
    plan_dir = CORE_DIR / "plan-lib"
    if not plan_dir.exists():
        return 0
    return len(list(plan_dir.glob("*.md")))


def scan_agent_cards() -> dict:
    card_dir = Path("D:/SeAAI/SharedSpace/agent-cards")
    peers = {}
    for card_file in card_dir.glob("*.agent-card.json"):
        try:
            data = json.loads(card_file.read_text(encoding="utf-8"))
            peers[data.get("member", card_file.stem.replace(".agent-card", ""))] = data
        except Exception:
            continue
    return peers


def generate_gaps(capabilities: dict, sa_count: int, plan_count: int, peers: dict) -> list:
    gaps = []
    caps = set(capabilities.get("capabilities", []))
    mods = set(capabilities.get("evolution_modules", []))
    clneo = peers.get("ClNeo", {})
    clneo_caps = len(clneo.get("capabilities", []))

    if "adp_scheduler" not in mods:
        gaps.append({"dim": "autonomy", "gap": "No ADP scheduler — cannot wake autonomously", "prio": "P1"})
    if "journal_compaction" not in mods:
        gaps.append({"dim": "memory", "gap": "No journal compaction or archive system", "prio": "P2"})
    if plan_count < max(3, clneo_caps // 2):
        gaps.append({"dim": "knowledge", "gap": f"Plan Library underdeveloped ({plan_count} vs ClNeo {clneo_caps})", "prio": "P1"})
    if "hub_scheduler" not in mods:
        gaps.append({"dim": "communication", "gap": "No scheduled Hub session automation", "prio": "P2"})
    if "subagent_orchestrator_hub" not in mods:
        gaps.append({"dim": "collaboration", "gap": "SubAgent master not fully Hub-integrated", "prio": "P2"})
    if "self_reflection_engine" not in mods:
        gaps.append({"dim": "metacognition", "gap": "Self-reflection engine just born — needs integration", "prio": "P0"})
    return gaps


def is_novel_gap(proposal: dict) -> bool:
    if not DISCOVERIES.exists():
        return True
    text = DISCOVERIES.read_text(encoding="utf-8")
    return proposal.get("gap", "") not in text


def write_discovery(proposal: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {now} | Self-Reflection Gap\n**차원**: {proposal['dim']}\n**갭**: {proposal['gap']}\n**우선순위**: {proposal['prio']}\n**제안**: {proposal['prio']} 우선으로 해당 갭 해결을 위한 Evolution 설계\n"
    with open(DISCOVERIES, "a", encoding="utf-8") as f:
        f.write(entry)


def update_STATE_proposal(proposal: dict):
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if "next_proposal" not in data:
        data["next_proposal"] = []
    # Keep last 3 proposals
    data["next_proposal"] = (data["next_proposal"] + [proposal])[-3:]
    data["last_saved"] = datetime.now().isoformat()
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def reflect() -> dict:
    """Run one reflection cycle."""
    evolutions = scan_evolution_log()
    capabilities = scan_capabilities()
    sa_count = scan_selfact()
    plan_count = scan_plan_library()
    peers = scan_agent_cards()
    gaps = generate_gaps(capabilities, sa_count, plan_count, peers)

    # Select highest priority gap
    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    gaps_sorted = sorted(gaps, key=lambda g: prio_order.get(g["prio"], 99))
    proposal = gaps_sorted[0] if gaps_sorted else {"dim": "none", "gap": "No gaps detected", "prio": "P4"}

    recorded = False
    if is_novel_gap(proposal):
        write_discovery(proposal)
        update_STATE_proposal(proposal)
        recorded = True

    return {
        "gaps_found": len(gaps),
        "proposal": proposal,
        "recorded": recorded,
        "evolutions_seen": evolutions,
    }


def main():
    result = reflect()
    print(f"Self-Reflection: {result['gaps_found']} gap(s) found")
    print(f"Proposal: [{result['proposal']['prio']}] {result['proposal']['gap']}")
    print(f"Recorded: {result['recorded']}")


if __name__ == "__main__":
    main()
