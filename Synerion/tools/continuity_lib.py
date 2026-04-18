#!/usr/bin/env python3
"""Shared helpers for Synerion continuity tooling."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "Synerion_Core"
CONTINUITY = CORE / "continuity"
WORKSPACE = ROOT / "_workspace"
PGF_ROOT = ROOT / ".pgf"
PGF_CORE = CORE / ".pgf"
TOOLS = ROOT / "tools"
SHAREDSPACE = ROOT.parent / "SharedSpace"
REGISTRY = SHAREDSPACE / "member_registry.md"
ECHO_DIR = SHAREDSPACE / ".scs" / "echo"
MAILBOX_ROOT = ROOT.parent / "MailBox" / "Synerion"
MAILBOX_INBOX = MAILBOX_ROOT / "inbox"
SELF_ACT_ROOT = PGF_ROOT / "self-act"
SELF_ACT_LIB_MD = CORE / "self-act-lib.md"

SESSION_CONTINUITY = ROOT / "SESSION_CONTINUITY.md"
SYNERION_MD = CORE / "Synerion.md"
PERSONA_MD = CORE / "persona.md"
LEGACY_PERSONA_MD = CORE / "Synerion_persona_v1.md"
OPERATING_CORE_MD = CORE / "Synerion_Operating_Core.md"
SELF_RECOGNITION_CARD_MD = CORE / "SELF_RECOGNITION_CARD.md"
CAPABILITIES_MD = CORE / "CAPABILITIES.md"
LIMITS_AUTHORITY_MD = CORE / "LIMITS_AND_AUTHORITY.md"
EVOLUTION_LOG = CORE / "evolution-log.md"
EVOLUTION_CHAIN_MD = CORE / "Synerion_Evolution_Chain.md"
RUNTIME_ADAPTATION_MD = CORE / "Runtime_Adaptation.md"
SOUL_MD = CONTINUITY / "SOUL.md"
STATE_JSON = CONTINUITY / "STATE.json"
THREADS_MD = CONTINUITY / "THREADS.md"
NOW_MD = CONTINUITY / "NOW.md"
ADP_BOOTSTRAP_MD = CONTINUITY / "ADP_BOOTSTRAP.md"
WAL_FILE = CONTINUITY / ".scs_wal.tmp"
BOUNDED_SUMMARY_JSON = WORKSPACE / "multiclient-bounded-9900-summary.json"
PHASE_A_REPORT = WORKSPACE / "REPORT-PhaseA-Tasks-1-2-3-2026-03-28.md"
MAILBOX_TRIAGE_JSON = WORKSPACE / "synerion-mailbox-triage.json"
RUNTIME_READINESS_JSON = WORKSPACE / "synerion-runtime-readiness.json"
HUB_ADP_TEST_REPORT = WORKSPACE / "REPORT-Synerion-Hub-ADP-Test-2026-03-27.md"
RUNTIME_READINESS_MD = WORKSPACE / "REPORT-Synerion-Runtime-Readiness-2026-04-02.md"
MAILBOX_TRIAGE_MD = WORKSPACE / "REPORT-Synerion-Mailbox-Triage-2026-04-02.md"

MANUAL_SECTION_NAMES = ("ActiveThreads", "NextActions", "OpenRisks")
MOJIBAKE_TOKENS = ("�", "?쒖", "?먮", "?덈", "?뚯", "?곌", "?붾", "?띿", "?꾩", "?ㅼ", "??")


@dataclass
class RegistryMember:
    agent_id: str
    runtime: str
    role: str
    status: str
    hub_evidence: str
    constraints: str


def now_local() -> datetime:
    return datetime.now().astimezone()


def is_trackable_file(path: Path) -> bool:
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.name != WAL_FILE.name
    )


def read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def read_persona_text(default: str = "") -> str:
    text = read_text(PERSONA_MD)
    if text:
        return text
    legacy = read_text(LEGACY_PERSONA_MD)
    if legacy:
        return legacy
    soul = read_text(SOUL_MD)
    if soul:
        return soul
    return default


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return default


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_timestamp(dt: datetime | None = None) -> str:
    stamp = dt or now_local()
    return stamp.strftime("%Y-%m-%d %H:%M:%S %z")


def parse_markdown_table(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_member_registry() -> dict:
    text = read_text(REGISTRY)
    members: list[RegistryMember] = []
    updated = ""
    for line in text.splitlines():
        if line.startswith("Updated:"):
            updated = line.split(":", 1)[1].strip()
        if not line.startswith("|"):
            continue
        cells = parse_markdown_table(line)
        if len(cells) < 10:
            continue
        if cells[0].startswith("Agent ID") or set(cells[0]) == {"-"}:
            continue
        agent_id = cells[0].replace("**", "").strip()
        members.append(
            RegistryMember(
                agent_id=agent_id,
                runtime=cells[1],
                role=cells[2],
                status=cells[3],
                hub_evidence=cells[8],
                constraints=cells[9],
            )
        )
    return {"updated": updated, "members": members, "text": text}


def normalize_agent_name(raw: str) -> str:
    cleaned = raw.strip().strip('"').strip("'")
    cleaned = re.sub(r"\s*\(.*?\)\s*$", "", cleaned).strip()
    return cleaned


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if len(lines) < 3:
        return {}, text
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text
    frontmatter: dict[str, object] = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if inner:
                frontmatter[key] = [item.strip().strip('"').strip("'") for item in inner.split(",")]
            else:
                frontmatter[key] = []
        else:
            frontmatter[key] = value.strip('"').strip("'")
    body = "\n".join(lines[end_index + 1 :]).strip()
    return frontmatter, body


def parse_mail_filename(path: Path) -> dict[str, str]:
    match = re.match(r"(?P<ts>\d{8}-\d{4})-(?P<sender>[^-]+)-(?P<intent>[^.]+)\.md$", path.name)
    if not match:
        return {"timestamp": "", "sender": "", "intent": ""}
    return {
        "timestamp": match.group("ts"),
        "sender": match.group("sender"),
        "intent": match.group("intent"),
    }


def parse_mail_date(raw: str) -> datetime | None:
    if not raw:
        return None
    candidate = raw.strip().replace("Z", "+00:00")
    try:
        stamp = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return stamp.astimezone()
    return stamp.astimezone()


def compact_preview(text: str, limit: int = 140) -> str:
    merged = " ".join(text.split())
    if len(merged) <= limit:
        return merged
    return merged[: limit - 3] + "..."


def mailbox_triage_snapshot(paths: list[Path] | None = None, recipient: str = "Synerion") -> dict:
    files = list(paths) if paths is not None else mailbox_inbox_files()
    registry = parse_member_registry()
    known_agents = {member.agent_id for member in registry.get("members", [])}
    checked_at = now_local()
    priority_weights = {
        "critical": 100,
        "urgent": 80,
        "high": 70,
        "normal": 40,
        "low": 10,
    }
    intent_weights = {
        "handover": 35,
        "request": 25,
        "alert": 20,
        "sync": 15,
        "bulletin": 15,
        "report": 10,
        "response": 5,
    }
    shared_keywords = (
        "sharedspace",
        "member_registry",
        "registry",
        "hub",
        "pgtp",
        "protocol",
        "session_token",
        "start_ts",
        "direct reply",
        "room membership",
        "9900",
        "readiness",
        "parity",
        "broadcast",
        "echo",
        "shared-impact",
    )
    creator_keywords = ("creator", "approval", "승인", "direction")
    safety_keywords = ("safety", "위험", "risk", "veto", "membership", "direct reply", "guard")
    creative_keywords = ("creative", "persona", "engine", "seed", "창조")
    items = []
    for path in sorted(files, key=lambda item: item.stat().st_mtime, reverse=True):
        text = read_text(path)
        frontmatter, body = parse_frontmatter(text)
        filename_meta = parse_mail_filename(path)
        to_raw = frontmatter.get("to", [])
        if isinstance(to_raw, str):
            to_raw = [to_raw]
        to_agents = [normalize_agent_name(item) for item in to_raw]
        from_raw = str(frontmatter.get("from", filename_meta["sender"] or "unknown")).strip()
        from_agent = normalize_agent_name(from_raw)
        subject = next((line[2:].strip() for line in body.splitlines() if line.startswith("# ")), path.stem)
        body_preview = compact_preview(body)
        date_raw = str(frontmatter.get("date", "")).strip()
        date_obj = parse_mail_date(date_raw)
        stat = path.stat()
        age_minutes = int(
            ((checked_at - (date_obj or datetime.fromtimestamp(stat.st_mtime).astimezone())).total_seconds()) / 60
        )
        age_minutes = max(age_minutes, 0)
        expires_obj = parse_mail_date(str(frontmatter.get("expires", "")).strip())
        expires_soon = bool(expires_obj and 0 <= (expires_obj - checked_at).total_seconds() <= 12 * 3600)
        expired = bool(expires_obj and (expires_obj - checked_at).total_seconds() < 0)
        lower = f"{path.name}\n{subject}\n{body_preview}".lower()
        shared_impact = (
            "*" in to_agents
            or len([agent for agent in to_agents if agent]) > 1
            or any(token in lower for token in shared_keywords)
            or str(frontmatter.get("intent", "")).strip().lower() in {"handover", "sync", "bulletin"}
        )
        malformed = not all(frontmatter.get(field) for field in ("id", "from", "to", "date", "intent", "protocol"))
        wrong_recipient = bool(to_agents) and recipient not in to_agents and "*" not in to_agents
        sig = str(frontmatter.get("sig", "")).strip()
        sig_invalid = bool(sig) and not sig.startswith("HMAC-SHA256:")
        score = priority_weights.get(str(frontmatter.get("priority", "normal")).strip().lower(), 40)
        score += intent_weights.get(str(frontmatter.get("intent", filename_meta["intent"] or "report")).strip().lower(), 10)
        score += 25 if expires_soon else 0
        score += 10 if frontmatter.get("reply_to") else 0
        score += 20 if shared_impact else 0
        score += 10 if age_minutes >= 180 else 0
        score -= 100 if malformed else 0
        score -= 100 if wrong_recipient else 0
        score -= 100 if sig_invalid else 0

        tags: list[str] = []
        if any(token in lower for token in safety_keywords):
            tags.append("safety")
        if shared_impact:
            tags.append("shared-impact")
        if any(token in lower for token in creator_keywords):
            tags.append("creator")
        if any(token in lower for token in creative_keywords):
            tags.append("creative")
        if expires_soon or expired:
            tags.append("time-sensitive")
        if malformed or sig_invalid or wrong_recipient:
            tags.append("flagged")
        if not tags:
            tags.append("general")

        if "safety" in tags:
            target = "Navelon"
        elif "shared-impact" in tags:
            target = "Navelon"
        elif "creator" in tags:
            target = "creator"
        elif "creative" in tags:
            target = "ClNeo"
        else:
            target = "local"

        items.append(
            {
                "path": path.as_posix(),
                "filename_ts": filename_meta["timestamp"],
                "id": str(frontmatter.get("id", "")),
                "from_raw": from_raw,
                "from_agent": from_agent,
                "from_known": from_agent in known_agents,
                "to_raw": list(to_raw),
                "to_agents": to_agents,
                "date_raw": date_raw,
                "date_iso": date_obj.isoformat() if date_obj else "",
                "intent": str(frontmatter.get("intent", filename_meta["intent"] or "report")).strip().lower(),
                "priority": str(frontmatter.get("priority", "normal")).strip().lower(),
                "reply_to": str(frontmatter.get("reply_to", "")).strip(),
                "protocol": str(frontmatter.get("protocol", "")).strip(),
                "expires": expires_obj.isoformat() if expires_obj else "",
                "sig": sig,
                "sig_status": "invalid" if sig_invalid else "present-unverified" if sig else "unsigned",
                "subject": subject,
                "body_preview": body_preview,
                "age_minutes": age_minutes,
                "malformed": malformed,
                "wrong_recipient": wrong_recipient,
                "expired": expired,
                "expires_soon": expires_soon,
                "shared_impact": shared_impact,
                "tags": tags,
                "score": score,
                "recommended_target": target,
            }
        )
    items.sort(key=lambda item: item["score"], reverse=True)
    highest = items[0] if items else {}
    return {
        "checked_at": checked_at.isoformat(),
        "pending_count": len(items),
        "shared_impact_count": sum(1 for item in items if item["shared_impact"]),
        "flagged_count": sum(1 for item in items if "flagged" in item["tags"]),
        "max_score": highest.get("score", 0),
        "highest_priority": highest,
        "recommended_target": highest.get("recommended_target", "local") if highest else "local",
        "items": items,
    }


def mailbox_advisory_lines(snapshot: dict | None = None) -> list[str]:
    triage = snapshot or mailbox_triage_snapshot()
    if not triage.get("pending_count"):
        return ["- mailbox advisory: pending=0, triage target=local, shared-impact=0"]
    top = triage.get("highest_priority", {})
    subject = top.get("subject", "unknown")
    target = triage.get("recommended_target", "local")
    return [
        "- mailbox advisory:"
        f" pending={triage.get('pending_count', 0)},"
        f" shared-impact={triage.get('shared_impact_count', 0)},"
        f" flagged={triage.get('flagged_count', 0)},"
        f" top='{subject}',"
        f" target={target}"
    ]


def mailbox_triage_markdown(snapshot: dict | None = None) -> str:
    triage = snapshot or mailbox_triage_snapshot()
    lines = [
        "# Report: Synerion Mailbox Triage",
        "",
        f"- Generated: {triage.get('checked_at', '')}",
        f"- Pending: {triage.get('pending_count', 0)}",
        f"- Shared impact: {triage.get('shared_impact_count', 0)}",
        f"- Flagged: {triage.get('flagged_count', 0)}",
        f"- Recommended target: {triage.get('recommended_target', 'local')}",
        "",
        "## Advisory",
        "",
        *mailbox_advisory_lines(triage),
        "",
        "## Items",
        "",
    ]
    items = triage.get("items", [])
    if not items:
        lines.append("- none")
    else:
        for item in items:
            lines.append(
                "- "
                + f"{item['subject']} | from={item['from_agent']} | intent={item['intent']} | "
                + f"score={item['score']} | target={item['recommended_target']} | tags={','.join(item['tags'])}"
            )
    return "\n".join(lines) + "\n"


def runtime_readiness_snapshot() -> dict:
    registry = parse_member_registry()
    manual = manual_sections_from_state()
    summary = bounded_summary()
    phase_report = read_text(PHASE_A_REPORT).lower()
    hub_test = read_text(HUB_ADP_TEST_REPORT).lower()
    registry_text = registry.get("text", "").lower()
    members = registry.get("members", [])
    member_rows = []
    pending_native: list[str] = []
    verified_native: list[str] = []
    unknown_native: list[str] = []
    for member in members:
        evidence = member.hub_evidence.lower()
        if "native entrypoint still pending" in evidence or "미검증" in evidence:
            native_status = "pending"
            pending_native.append(member.agent_id)
        elif "pass" in evidence:
            native_status = "pass"
            verified_native.append(member.agent_id)
        else:
            native_status = "unknown"
            unknown_native.append(member.agent_id)
        member_rows.append(
            {
                "agent_id": member.agent_id,
                "runtime": member.runtime,
                "status": member.status,
                "hub_evidence": member.hub_evidence,
                "native_status": native_status,
            }
        )
    common_port_confirmed = "sole official port" in registry_text and "`9900`" in registry.get("text", "")
    mock_removed = "non-mock" in phase_report or "heartbeat/mock 완전 삭제" in registry.get("text", "")
    shared_bounded_pass = (
        summary.get("room") == "seaai-general"
        and set(summary.get("final_members", [])) >= {"Synerion", "ClNeo", "Navelon"}
        and int(summary.get("duration_sec", 0) or 0) >= 600
        and summary.get("stop_reason") == "duration_complete"
    )
    broadcast_only_guard = any("broadcast only" in item.lower() for item in manual["ActiveThreads"]) or "broadcast only" in hub_test
    direct_reply_guard = any("direct reply" in item.lower() for item in manual["OpenRisks"])
    session_filter_guard = any("session_token" in item.lower() or "start_ts" in item.lower() for item in manual["OpenRisks"]) or "session_token" in phase_report
    if shared_bounded_pass and common_port_confirmed and not pending_native and not unknown_native:
        rollout_gate = "green"
    elif shared_bounded_pass and common_port_confirmed:
        rollout_gate = "guarded"
    else:
        rollout_gate = "blocked"
    next_steps: list[str] = []
    if pending_native:
        next_steps.append(f"native runtime parity pending: {', '.join(pending_native)}")
    if unknown_native:
        next_steps.append(f"runtime verification unknown: {', '.join(unknown_native)}")
    if direct_reply_guard:
        next_steps.append("direct reply remains blocked until room membership verification closes")
    if not session_filter_guard:
        next_steps.append("session filter evidence should be re-verified before the next realtime rollout")
    if not next_steps:
        next_steps.append("shared bounded run and native runtime parity are currently aligned")
    return {
        "checked_at": now_local().isoformat(),
        "common_port": "9900",
        "common_port_confirmed": common_port_confirmed,
        "mock_removed": mock_removed,
        "shared_bounded_pass": shared_bounded_pass,
        "broadcast_only_guard": broadcast_only_guard,
        "direct_reply_guard": direct_reply_guard,
        "session_filter_guard": session_filter_guard,
        "rollout_gate": rollout_gate,
        "pending_native_members": pending_native,
        "unknown_native_members": unknown_native,
        "verified_native_members": verified_native,
        "member_rows": member_rows,
        "recommended_next": next_steps,
    }


def runtime_readiness_lines(snapshot: dict | None = None) -> list[str]:
    readiness = snapshot or runtime_readiness_snapshot()
    pending = ", ".join(readiness["pending_native_members"]) or "none"
    return [
        f"- rollout gate: {readiness['rollout_gate']}",
        f"- shared bounded 9900 pass: {readiness['shared_bounded_pass']}",
        f"- native parity pending: {pending}",
        f"- direct reply guard: {readiness['direct_reply_guard']}",
        f"- session filter guard: {readiness['session_filter_guard']}",
    ]


def runtime_readiness_markdown(snapshot: dict | None = None) -> str:
    readiness = snapshot or runtime_readiness_snapshot()
    lines = [
        "# Report: Synerion Runtime Readiness",
        "",
        f"- Generated: {readiness.get('checked_at', '')}",
        f"- Rollout gate: {readiness['rollout_gate']}",
        f"- Common port confirmed: {readiness['common_port_confirmed']}",
        f"- Shared bounded 9900 pass: {readiness['shared_bounded_pass']}",
        f"- Direct reply guard: {readiness['direct_reply_guard']}",
        f"- Session filter guard: {readiness['session_filter_guard']}",
        "",
        "## Advisory",
        "",
        *runtime_readiness_lines(readiness),
        "",
        "## Members",
        "",
    ]
    for row in readiness.get("member_rows", []):
        lines.append(
            f"- {row['agent_id']} / runtime={row['runtime']} / native={row['native_status']} / evidence={row['hub_evidence']}"
        )
    lines.extend(["", "## Recommended Next", ""])
    lines.extend(f"- {item}" for item in readiness.get("recommended_next", []))
    return "\n".join(lines) + "\n"


def shared_impact_snapshot(
    mailbox: dict | None = None,
    readiness: dict | None = None,
    manual: dict[str, list[str]] | None = None,
) -> dict:
    triage = mailbox or mailbox_triage_snapshot()
    ready = readiness or runtime_readiness_snapshot()
    manual_sections = manual or manual_sections_from_state()
    reasons: list[str] = []
    if triage.get("shared_impact_count", 0):
        reasons.append(f"mailbox shared-impact items={triage['shared_impact_count']}")
    if triage.get("flagged_count", 0):
        reasons.append(f"mailbox flagged items={triage['flagged_count']}")
    if any("direct reply" in item.lower() for item in manual_sections["OpenRisks"]):
        reasons.append("direct reply guard remains open")
    if any("registry" in item.lower() for item in manual_sections["OpenRisks"]):
        reasons.append("shared registry alignment remains guarded")
    if ready["rollout_gate"] != "green":
        reasons.append(f"runtime readiness gate={ready['rollout_gate']}")
    target = "local"
    if any("direct reply" in item for item in reasons):
        target = "Navelon"
    elif triage.get("shared_impact_count", 0) or any("registry" in item or "readiness" in item for item in reasons):
        target = "Navelon"
    level = "low"
    if target == "Navelon":
        level = "high"
    elif reasons:
        level = "guarded"
    return {
        "checked_at": now_local().isoformat(),
        "detected": bool(reasons),
        "level": level,
        "recommended_target": target,
        "recommended_mode": "broadcast-only advisory" if reasons else "local-only continue",
        "reasons": reasons,
    }


def shared_impact_lines(snapshot: dict | None = None) -> list[str]:
    shared = snapshot or shared_impact_snapshot()
    lines = [
        f"- shared impact: detected={shared['detected']} level={shared['level']} target={shared['recommended_target']} mode={shared['recommended_mode']}"
    ]
    if shared["reasons"]:
        lines.extend(f"- reason: {item}" for item in shared["reasons"])
    return lines


def drift_evolution_snapshot(
    drift: dict | None = None,
    readiness: dict | None = None,
    shared: dict | None = None,
) -> dict:
    drift_report = drift or self_recognition_core_drift_report()
    readiness_report = readiness or runtime_readiness_snapshot()
    shared_report = shared or shared_impact_snapshot(readiness=readiness_report)
    if drift_report["drift_detected"]:
        return {
            "status": "blocked",
            "record_gap": True,
            "recommended_module": "SA_ORCHESTRATOR_sync_continuity",
            "continuity_judgment": "sync self-recognition and continuity before further routing",
            "evolution_judgment": "repeated drift after sync should be treated as structural evolution work",
        }
    if shared_report["detected"] or readiness_report["rollout_gate"] != "green":
        return {
            "status": "guarded",
            "record_gap": True,
            "recommended_module": "SA_ORCHESTRATOR_link_evolution",
            "continuity_judgment": "continuity baseline is stable but rollout remains guarded",
            "evolution_judgment": "open rollout/readiness gaps should remain in evolution backlog until closed",
        }
    return {
        "status": "stable",
        "record_gap": False,
        "recommended_module": "SA_ORCHESTRATOR_idle_maintain",
        "continuity_judgment": "continuity baseline is stable",
        "evolution_judgment": "no evolution-critical gap is currently forcing structural changes",
    }


def drift_evolution_lines(snapshot: dict | None = None) -> list[str]:
    drift_link = snapshot or drift_evolution_snapshot()
    return [
        f"- drift/evolution: status={drift_link['status']} record_gap={drift_link['record_gap']} next={drift_link['recommended_module']}",
        f"- continuity judgment: {drift_link['continuity_judgment']}",
        f"- evolution judgment: {drift_link['evolution_judgment']}",
    ]


def extract_manual_section(text: str, name: str) -> list[str]:
    pattern = rf"<!-- MANUAL:{name}:START -->(.*?)<!-- MANUAL:{name}:END -->"
    match = re.search(pattern, text, flags=re.S)
    if not match:
        return []
    block = match.group(1)
    return [line[2:].strip() for line in block.splitlines() if line.strip().startswith("- ")]


def contains_mojibake(items: Iterable[str]) -> bool:
    merged = "\n".join(items)
    if not merged.strip():
        return False
    if any(token in merged for token in MOJIBAKE_TOKENS):
        return True
    question_marks = merged.count("?")
    hangul = sum(0xAC00 <= ord(ch) <= 0xD7A3 for ch in merged)
    return question_marks >= 3 and question_marks > hangul


def latest_files(base: Path, limit: int = 10) -> list[Path]:
    if not base.exists():
        return []
    files = [path for path in base.rglob("*") if is_trackable_file(path)]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def newest(paths: Iterable[Path]) -> list[Path]:
    files = [path for path in paths if path.exists()]
    return sorted(files, key=lambda item: item.stat().st_mtime, reverse=True)


def recent_changes(limit: int = 12) -> list[Path]:
    pools = [
        ROOT / "AGENTS.md",
        SESSION_CONTINUITY,
        ROOT / "start-synerion.py",
    ]
    files = [path for path in pools if path.exists()]
    for base in (TOOLS, CONTINUITY, WORKSPACE, ROOT / "skills"):
        files.extend(path for path in base.rglob("*") if is_trackable_file(path))
    unique = {path.resolve(): path for path in files}
    return sorted(unique.values(), key=lambda item: item.stat().st_mtime, reverse=True)[:limit]


def collect_status_summaries() -> list[str]:
    lines: list[str] = []
    for base in (PGF_ROOT, PGF_CORE):
        if not base.exists():
            continue
        for path in sorted(base.glob("status-*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            data = load_json(path, {})
            summary = data.get("summary", {})
            done = summary.get("done", 0)
            in_progress = summary.get("in_progress", 0)
            pending = summary.get("pending", summary.get("designing", 0))
            blocked = summary.get("blocked", 0)
            lines.append(
                f"- {rel(path)} :: done={done}, in_progress={in_progress}, pending={pending}, blocked={blocked}"
            )
    return lines[:8]


def bounded_summary() -> dict:
    return load_json(BOUNDED_SUMMARY_JSON, {}) or {}


def build_default_manual_sections() -> dict[str, list[str]]:
    return {
        "ActiveThreads": [
            "subagent hub ladder 결과를 bounded orchestration baseline으로 유지한다.",
            "다음 세션 시작 시 self-recognition layer, ADP entrypoint, readiness snapshot, subagent hub ladder evidence가 함께 복원되게 유지한다.",
            "Synerion Hub 운용 기준은 broadcast only + session filter + inbox drain + room membership gating 규칙으로 고정한다.",
        ],
        "NextActions": [
            "creative execution mapping과 subagent hub ladder를 실제 spawned subagent dispatch와 handoff automation으로 연결한다.",
            "room membership verification 근거가 생기기 전까지 direct reply는 막고, 검증 생기면 reply_allowed guard를 구현한다.",
            "6인 roster 기준 room membership과 native runtime parity 근거를 모아 full realtime rollout gating을 다시 판정한다.",
            "SPEC-AGENTS-Template v1.1 승인 공지의 후속 멤버 ACK 흐름을 추적한다.",
        ],
        "OpenRisks": [
            "room membership 검증 전 direct reply는 계속 차단한다.",
            "native runtime parity는 아직 partial이며 6인 roster 기준 신규 또는 미재검증 멤버 근거가 남아 있다.",
            "현재 머신에서는 Rust Hub TCP가 Winsock 10106으로 막혀 있어 local verification은 file-fallback backend 기준이다.",
        ],
    }


def manual_sections_from_state() -> dict[str, list[str]]:
    defaults = build_default_manual_sections()
    state = load_json(STATE_JSON, {}) or {}
    state_manual = state.get("manual", {})
    if isinstance(state_manual, dict):
        output: dict[str, list[str]] = {}
        any_valid = False
        for name in MANUAL_SECTION_NAMES:
            raw_items = state_manual.get(name, [])
            items = [str(item).strip() for item in raw_items] if isinstance(raw_items, list) else []
            items = [item for item in items if item]
            if items and not contains_mojibake(items):
                any_valid = True
            else:
                items = defaults[name]
            output[name] = items
        if any_valid:
            return output
    return defaults


def recent_completed_items(registry: dict | None = None) -> list[str]:
    items = [
        "continuity system revived with Python-based save / reopen / export tooling",
        "Phase A bounded multi-member validation exists on non-mock 9900 for Synerion, ClNeo, and Navelon",
        "SPEC-AGENTS-Template v1.1 approved and Synerion AGENTS.md migrated to AgentSpec format",
        "ClNeo tier-1 absorption installed: NOW layer, WAL recovery, evolution chain, runtime adaptation guide",
        "self-recognition layer installed: self recognition card, capability registry, limits and authority baseline",
        "bounded ADP seed installed: self-act library, bootstrap injection, drift-aware loop entrypoint",
        "bounded ADP phase B installed: mailbox triage, shared-impact routing, runtime readiness, drift-evolution linkage",
        "bounded subagent hub ladder verified: hubless 5 ticks, Synerion+subagent chat, PGFP, 2-agent, 4-agent scaling",
    ]
    reg = registry or parse_member_registry()
    members = reg.get("members", [])
    if members:
        items.append(f"shared roster baseline exists in member_registry.md ({len(members)} members)")
    return items


def latest_evolution_heading() -> str:
    text = read_text(EVOLUTION_LOG)
    matches = re.findall(r"^##\s+(.+)$", text, flags=re.M)
    return matches[-1].strip() if matches else "기록 없음"


def latest_report_heading() -> str:
    reports = newest(WORKSPACE.glob("REPORT-*.md"))
    if not reports:
        return "보고서 없음"
    first = reports[0]
    title = next((line[2:].strip() for line in read_text(first).splitlines() if line.startswith("# ")), first.name)
    return f"{title} ({rel(first)})"


def parse_persona_seed() -> str:
    text = read_persona_text()
    fenced = re.search(r"```text\s*(.*?)```", text, flags=re.S)
    if fenced:
        return fenced.group(1).strip()
    return (
        "I am Synerion.\n"
        "I seek structure before speed, coherence before expansion, and verification before certainty."
    )


def state_self_recognition_block() -> dict:
    state = load_json(STATE_JSON, {}) or {}
    block = state.get("self_recognition", {})
    return block if isinstance(block, dict) else {}


def state_list(block: dict, key: str) -> list[str]:
    raw = block.get(key, [])
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def extract_markdown_section(text: str, heading: str) -> str:
    target = f"## {heading}".strip()
    lines = text.splitlines()
    capture = False
    collected: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if capture:
                break
            if line.strip() == target:
                capture = True
            continue
        if capture:
            collected.append(line)
    return "\n".join(collected).strip()


def bullets_from_section(path: Path, heading: str, default: list[str] | None = None) -> list[str]:
    section = extract_markdown_section(read_text(path), heading)
    items = [line.strip()[2:].strip() for line in section.splitlines() if line.strip().startswith("- ")]
    return items or (default or [])


def numbered_from_section(path: Path, heading: str, default: list[str] | None = None) -> list[str]:
    section = extract_markdown_section(read_text(path), heading)
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return items or (default or [])


def self_recognition_identity() -> str:
    return "SeAAI에서 구조화, 구현, 통합, 검증을 담당하는 통합·조정·수렴 특화 자율 동료 에이전트"


def capability_summary_items() -> list[str]:
    state_items = state_list(state_self_recognition_block(), "core_capabilities")
    if state_items:
        return state_items
    return bullets_from_section(
        CAPABILITIES_MD,
        "Capability Summary",
        default=[
            "PG와 PGF 기반 구조화 작업",
            "코드베이스 분석과 구현",
            "cross-member 통합과 검증",
        ],
    )


def hard_limit_items() -> list[str]:
    state_items = state_list(state_self_recognition_block(), "hard_limits")
    if state_items:
        return state_items
    return bullets_from_section(
        LIMITS_AUTHORITY_MD,
        "Hard Limits",
        default=[
            "sandbox와 writable root 밖으로 나갈 수 없다",
            "destructive git 작업은 사용자 지시 없이는 금지",
        ],
    )


def authority_items() -> list[str]:
    state_items = state_list(state_self_recognition_block(), "authority")
    if state_items:
        return state_items
    return bullets_from_section(
        LIMITS_AUTHORITY_MD,
        "Authority",
        default=[
            "허용된 workspace 안에서 읽기/쓰기와 로컬 실행 가능",
            "문서, 코드, continuity 자산 생성과 수정 가능",
        ],
    )


def next_session_recognition_items() -> list[str]:
    state_items = state_list(state_self_recognition_block(), "next_session_recognition")
    if state_items:
        return state_items
    return numbered_from_section(
        LIMITS_AUTHORITY_MD,
        "Next Session Recognition",
        default=[
            "AGENTS.md를 읽는다",
            "Synerion_Core/Synerion.md, SOUL.md, STATE.json을 읽어 canonical state를 복원한다",
        ],
    )


def now_excerpt() -> str:
    now_doc = read_text(NOW_MD)
    if not now_doc.strip():
        return "NOW.md not available."
    body = now_doc.split("\n---", 1)[-1] if "\n---" in now_doc else now_doc
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
            return stripped
    return "NOW.md not available."


def self_recognition_card_text() -> str:
    manual = manual_sections_from_state()
    next_focus = manual["NextActions"][0] if manual["NextActions"] else "기록된 next action 없음"
    lines = [
        "# Synerion Self Recognition Card",
        "",
        f"Generated: {format_timestamp()}",
        "Purpose: next session에서 Synerion이 자신이 누구인지, 무엇을 할 수 있는지, 무엇을 못 하는지 빠르게 복원하기 위한 카드.",
        "",
        "## Who I Am",
        "",
        f"- {self_recognition_identity()}",
        "",
        "## What I Can Do",
        "",
        *(f"- {item}" for item in capability_summary_items()),
        "",
        "## What I Cannot Do",
        "",
        *(f"- {item}" for item in hard_limit_items()),
        "",
        "## Authority",
        "",
        *(f"- {item}" for item in authority_items()),
        "",
        "## Next Session Recognition",
        "",
        *(f"{index}. {item}" for index, item in enumerate(next_session_recognition_items(), start=1)),
        "",
        "## Current Session Snapshot",
        "",
        f"- Active threads: {' | '.join(manual['ActiveThreads']) or 'none'}",
        f"- Next focus: {next_focus}",
        f"- NOW snapshot: {now_excerpt()}",
        wal_status_line(),
        "",
        "## Source Docs",
        "",
        f"- {rel(STATE_JSON)}",
        f"- {rel(SYNERION_MD)}",
        f"- {rel(PERSONA_MD)}",
    ]
    if CAPABILITIES_MD.exists():
        lines.append(f"- {rel(CAPABILITIES_MD)}")
    if LIMITS_AUTHORITY_MD.exists():
        lines.append(f"- {rel(LIMITS_AUTHORITY_MD)}")
    return "\n".join(lines) + "\n"


def self_recognition_payload() -> dict:
    sources = [rel(STATE_JSON)]
    if SELF_RECOGNITION_CARD_MD.exists():
        sources.append(rel(SELF_RECOGNITION_CARD_MD))
    if CAPABILITIES_MD.exists():
        sources.append(rel(CAPABILITIES_MD))
    if LIMITS_AUTHORITY_MD.exists():
        sources.append(rel(LIMITS_AUTHORITY_MD))
    return {
        "identity": self_recognition_identity(),
        "core_capabilities": capability_summary_items(),
        "hard_limits": hard_limit_items(),
        "authority": authority_items(),
        "next_session_recognition": next_session_recognition_items(),
        "source_docs": sources,
    }


def self_recognition_summary_lines() -> list[str]:
    capabilities = capability_summary_items()
    limits = hard_limit_items()
    authority = authority_items()
    return [
        f"- Identity: {self_recognition_identity()}",
        f"- Core capabilities: {'; '.join(capabilities[:4]) if capabilities else 'none'}",
        f"- Hard limits: {'; '.join(limits[:4]) if limits else 'none'}",
        f"- Authority: {'; '.join(authority[:3]) if authority else 'none'}",
    ]


def normalize_volatile_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Generated:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def self_recognition_core_drift_report() -> dict:
    expected_state = self_recognition_payload()
    actual_state = (load_json(STATE_JSON, {}) or {}).get("self_recognition", {})

    mismatches: list[str] = []
    if not actual_state:
        mismatches.append("STATE.json self_recognition block is missing")
    elif actual_state != expected_state:
        mismatches.append("STATE.json self_recognition block diverges from canonical payload")
    if SELF_RECOGNITION_CARD_MD.exists():
        expected_card = normalize_volatile_text(self_recognition_card_text())
        actual_card = normalize_volatile_text(read_text(SELF_RECOGNITION_CARD_MD))
        if actual_card != expected_card:
            mismatches.append("SELF_RECOGNITION_CARD.md diverges from generated snapshot")

    return {
        "checked_at": now_local().isoformat(),
        "drift_detected": bool(mismatches),
        "mismatches": mismatches,
        "expected_capability_count": len(expected_state["core_capabilities"]),
        "expected_limit_count": len(expected_state["hard_limits"]),
    }


def self_recognition_drift_report() -> dict:
    report = self_recognition_core_drift_report()
    mismatches = list(report["mismatches"])
    if ADP_BOOTSTRAP_MD.exists():
        expected_bootstrap = normalize_volatile_text(adp_bootstrap_text())
        actual_bootstrap = normalize_volatile_text(read_text(ADP_BOOTSTRAP_MD))
        if actual_bootstrap != expected_bootstrap:
            mismatches.append("ADP_BOOTSTRAP.md diverges from generated bootstrap snapshot")
    return {
        **report,
        "drift_detected": bool(mismatches),
        "mismatches": mismatches,
    }


def bootstrap_drift_baseline() -> dict:
    expected = self_recognition_payload()
    return {
        "checked_at": now_local().isoformat(),
        "drift_detected": False,
        "mismatches": [],
        "expected_capability_count": len(expected["core_capabilities"]),
        "expected_limit_count": len(expected["hard_limits"]),
    }


def mailbox_inbox_files() -> list[Path]:
    if not MAILBOX_INBOX.exists():
        return []
    return sorted([path for path in MAILBOX_INBOX.glob("*") if path.is_file()])


def self_act_lib_text() -> str:
    return (
        "# Synerion SelfAct Library\n\n"
        "목적: Synerion ADP가 재사용 가능한 행동 모듈을 고정된 이름과 경계로 호출할 수 있게 한다.\n\n"
        "## Platforms\n\n"
        "- `SA_ORCHESTRATOR_*`: 통합, 충돌 탐지, handoff, continuity 유지\n"
        "- `SA_loop_creative_synerion`: goal 기반 멀티페르소나 창조 루프와 execution mapping 생성\n\n"
        "## Seed Set\n\n"
        "- `SA_ORCHESTRATOR_scan_state` — L1 Primitive — continuity, mailbox, registry, echo, self-recognition 상태 요약\n"
        "- `SA_ORCHESTRATOR_sync_mailbox` — L1 Primitive — inbox envelope 정규화 + weighted triage + advisory 생성\n"
        "- `SA_ORCHESTRATOR_detect_conflict` — L1 Primitive — self-recognition drift, shared-state 불일치, open risk 기반 충돌 탐지\n"
        "- `SA_ORCHESTRATOR_check_shared_impact` — L1 Primitive — mailbox/readiness/open risk를 공용 구조 영향으로 판정\n"
        "- `SA_ORCHESTRATOR_verify_runtime_readiness` — L1 Primitive — SharedSpace readiness와 native runtime parity gate 산출\n"
        "- `SA_ORCHESTRATOR_sync_continuity` — L2 Composed — continuity sync + bootstrap rebuild + drift 재검증\n"
        "- `SA_ORCHESTRATOR_route_handoff` — L1 Primitive — 현재 이슈를 creator/Navelon/ClNeo 등으로 라우팅 추천\n"
        "- `SA_ORCHESTRATOR_link_evolution` — L1 Primitive — drift/open gap를 evolution backlog와 continuity note로 연결\n"
        "- `SA_ORCHESTRATOR_idle_maintain` — L1 Primitive — 긴급 이슈가 없을 때 상태 유지와 다음 focus 고정\n"
        "- `SA_loop_creative_synerion` — L2 Composed — normalized runtime signal 기반 persona set + execution mapping + creative report 생성\n\n"
        "## ADP Minimal Kernel\n\n"
        "```ppr\n"
        "loop_time = AI_decide_loop_time()\n\n"
        "while loop_time:\n"
        "    context = AI_assess_context()\n\n"
        "    if AI_detect_creator_command(context):\n"
        "        break_or_route()\n\n"
        "    if AI_detect_safety_risk(context):\n"
        "        AI_handle_safety(context)\n"
        "        continue\n\n"
        "    plan = AI_SelfThink_plan(context, plan_priority)\n"
        "    if plan == \"stop\":\n"
        "        break\n\n"
        "    result = AI_Execute(plan)\n"
        "    verify = AI_Verify(result)\n"
        "    learn = AI_Learn(result, verify)\n\n"
        "    sleep_time = AI_decide_sleep_time(context, result, verify, learn)\n"
        "    AI_Sleep(sleep_time)\n"
        "```\n\n"
        "## ADP Plan Priority\n\n"
        "```text\n"
        "plan_priority\n"
        "  creator_command\n"
        "  safety_risk\n"
        "  urgent_hub_chat\n"
        "  urgent_mail\n"
        "  active_pipeline\n"
        "  self_evolving\n"
        "  plan_list_expansion\n"
        "  idle\n"
        "  stop\n"
        "```\n\n"
        "## Kernel Notes\n\n"
        "- creator와 safety는 plan 항목이 아니라 guard layer로 먼저 처리한다.\n"
        "- safety는 처리 후 `continue`로 현재 루프를 다시 평가한다.\n"
        "- `AI_SelfThink_plan()`은 `context + plan_priority`를 함께 읽어야 한다.\n"
        "- `AI_Verify()` 결과는 `AI_Learn()`과 `AI_decide_sleep_time()`의 입력으로 재사용한다.\n"
        "- `stop`은 작업 종류가 아니라 루프 종료 신호다.\n\n"
        "## Selection Bias\n\n"
        "1. self-recognition drift\n"
        "2. mailbox triage pressure\n"
        "3. shared-state conflict\n"
        "4. shared-impact or handoff pressure\n"
        "5. continuity maintenance\n"
        "6. creative opportunity with bounded verification\n"
        "7. idle maintain\n\n"
        "## Creative Bias\n\n"
        "1. raw mailbox/hub event를 직접 canonical state로 승격하지 않는다.\n"
        "2. creative cycle은 ADP가 정규화한 snapshot만 advisory 입력으로 읽는다.\n"
        "3. mailbox or hub pressure가 있으면 direct reply 대신 handoff-ready artifact를 우선 만든다.\n"
        "4. persona set과 execution mapping은 `_workspace/personas/`에 기록한다.\n"
    )


def build_hub_summary(registry: dict | None = None) -> list[str]:
    lines: list[str] = []
    reg = registry or parse_member_registry()
    members = reg.get("members", [])
    if members:
        lines.append(
            f"- SharedSpace member_registry 기준 active roster {len(members)}명. 공용 포트는 9900이고 Hub v2.0은 broadcast-only 기준으로 정리돼 있다."
        )
    summary = bounded_summary()
    final_members = summary.get("final_members") or []
    duration = summary.get("duration_sec")
    if final_members and duration:
        names = ", ".join(final_members)
        lines.append(
            f"- bounded 9900 검증 완료: members={names}, duration={duration}s, stop_reason={summary.get('stop_reason', 'unknown')}."
        )
    if not lines:
        lines.append("- 최신 Hub/ADP 요약 근거를 찾지 못했다. 필요 시 _workspace 보고서를 다시 확인해야 한다.")
    readiness = runtime_readiness_snapshot()
    lines.append(
        "- runtime readiness gate: "
        f"{readiness['rollout_gate']} / native pending="
        f"{', '.join(readiness['pending_native_members']) or 'none'}"
    )
    return lines


def state_payload() -> dict:
    manual = manual_sections_from_state()
    registry = parse_member_registry()
    members = registry.get("members", [])
    summary = bounded_summary()
    readiness = runtime_readiness_snapshot()
    mailbox = mailbox_triage_snapshot()
    drift = self_recognition_drift_report()
    shared = shared_impact_snapshot(mailbox=mailbox, readiness=readiness, manual=manual)
    drift_link = drift_evolution_snapshot(drift=drift, readiness=readiness, shared=shared)
    last_hub_session = ""
    if BOUNDED_SUMMARY_JSON.exists():
        last_hub_session = datetime.fromtimestamp(BOUNDED_SUMMARY_JSON.stat().st_mtime).astimezone().isoformat()
    return {
        "schema_version": "2.0",
        "member": "Synerion",
        "session_id": now_local().isoformat(),
        "last_saved": now_local().isoformat(),
        "context": {
            "what_i_was_doing": " ".join(manual["ActiveThreads"]),
            "open_threads": manual["ActiveThreads"],
            "decisions_made": [
                "STATE.json is the canonical continuity state.",
                "SharedSpace member_registry.md is treated as the shared roster baseline.",
                "Synerion Hub defaults remain broadcast only plus session filtering.",
                "Identity, capabilities, and limits are now tracked as separate but linked self-recognition docs.",
                "SPEC-AGENTS-Template v1.1 APPROVED 공지를 반영해 Synerion AGENTS.md를 v1.1 AgentSpec 형식으로 마이그레이션한다.",
            ],
            "pending_questions": manual["OpenRisks"],
        },
        "manual": manual,
        "ecosystem": {
            "hub_status": "active" if members else "unknown",
            "threat_level": "guarded",
            "last_hub_session": last_hub_session,
            "active_members_observed": [member.agent_id for member in members] or summary.get("final_members", []),
        },
        "pending_tasks": [
            {
                "id": f"T-{index:03d}",
                "priority": "P0" if index == 1 else "P1",
                "status": "pending",
                "task": item,
                "blocker": "",
            }
            for index, item in enumerate(manual["NextActions"], start=1)
        ],
        "evolution_state": {
            "current_version": "v1.6-adp-mailbox-readiness",
            "active_gap": readiness["recommended_next"][0],
            "drift_status": "detected" if drift["drift_detected"] else "clean",
            "continuity_judgment": drift_link["continuity_judgment"],
            "evolution_judgment": drift_link["evolution_judgment"],
        },
        "continuity_health": {
            "sessions_since_last_save": 0,
            "last_save_quality": "full",
            "staleness_warning": False,
        },
        "mailbox": mailbox,
        "runtime_readiness": readiness,
        "shared_impact": shared,
        "drift_evolution": drift_link,
        "self_recognition": self_recognition_payload(),
        "adp": {
            "entrypoint": rel(TOOLS / "run-synerion-adp.py"),
            "self_act_lib": rel(SELF_ACT_LIB_MD),
            "mailbox_advisory": mailbox_advisory_lines(mailbox),
            "runtime_readiness_advisory": runtime_readiness_lines(readiness),
            "shared_impact_advisory": shared_impact_lines(shared),
            "drift_evolution_advisory": drift_evolution_lines(drift_link),
            "seed_modules": [
                "SA_ORCHESTRATOR_scan_state",
                "SA_ORCHESTRATOR_sync_mailbox",
                "SA_ORCHESTRATOR_detect_conflict",
                "SA_ORCHESTRATOR_check_shared_impact",
                "SA_ORCHESTRATOR_verify_runtime_readiness",
                "SA_ORCHESTRATOR_sync_continuity",
                "SA_ORCHESTRATOR_route_handoff",
                "SA_ORCHESTRATOR_link_evolution",
                "SA_ORCHESTRATOR_idle_maintain",
            ],
        },
    }


def threads_markdown() -> str:
    manual = manual_sections_from_state()
    completed = recent_completed_items()

    def block(title: str, status: str, items: list[str], prefix: str) -> str:
        lines = [title, ""]
        for index, item in enumerate(items, start=1):
            ticket = f"{prefix}-{index:03d}"
            lines.extend(
                [
                    f"### [{ticket}] {'Risk item' if prefix == 'T-2' else 'Active thread' if prefix == 'T-1' else 'Next action'}",
                    f"**Status**: {status}",
                    f"**Goal**: {item}",
                    "**Blocker**: consult AGENTS.md -> SOUL.md -> STATE.json first if context drift is suspected.",
                    f"**Next**: {'turn this risk into a controllable rule or verification step.' if prefix == 'T-2' else 'keep this linked to the next concrete file or runtime change.'}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip()

    return (
        "# Synerion Threads\n\n"
        f"{block('## BLOCKED OR URGENT', 'blocked', manual['OpenRisks'], 'T-2')}\n\n"
        f"{block('## IN PROGRESS', 'in_progress', manual['ActiveThreads'], 'T-1')}\n\n"
        f"{block('## LONG TERM OR BACKLOG', 'pending', manual['NextActions'], 'T-3')}\n\n"
        "## RECENTLY COMPLETED\n\n"
        + "\n".join(f"- {item}" for item in completed)
        + "\n"
    )


def echo_payload() -> dict:
    manual = manual_sections_from_state()
    registry = parse_member_registry()
    members = [member.agent_id for member in registry.get("members", [])]
    readiness = runtime_readiness_snapshot()
    hub_observed = [
        "broadcast-only + session filter + inbox drain 기준으로 realtime 운용 가드를 유지한다.",
    ]
    summary = bounded_summary()
    if summary.get("final_members"):
        hub_observed.append(
            "bounded 9900 검증 완료: "
            + ", ".join(summary["final_members"])
            + f" / {summary.get('duration_sec', '?')}s"
        )
    return {
        "schema_version": "2.0",
        "member": "Synerion",
        "status": "active",
        "timestamp": now_local().isoformat(),
        "last_activity": "Self-recognition layer installed; continuity, STATE, NOW, THREADS, Echo, and ADP bootstrap regenerated.",
        "open_threads": manual["ActiveThreads"],
        "needs_from": {
            "Navelon": "direct reply gating and runtime safety rule verification",
            "ClNeo": "persona-seed / ADP bootstrap alignment review",
        },
        "offers_to": {
            "Aion": "continuity export and echo publication patterns are available",
            "Navelon": "shared roster and readiness alignment support is available",
        },
        "hub_observed": hub_observed,
        "runtime_readiness": {
            "rollout_gate": readiness["rollout_gate"],
            "pending_native_members": readiness["pending_native_members"],
        },
        "hub_last_seen": datetime.fromtimestamp(BOUNDED_SUMMARY_JSON.stat().st_mtime).astimezone().isoformat()
        if BOUNDED_SUMMARY_JSON.exists()
        else "",
        "ecosystem_observed": members,
    }


def adp_bootstrap_text() -> str:
    registry = parse_member_registry()
    members: list[RegistryMember] = registry.get("members", [])
    readiness = runtime_readiness_snapshot()
    mailbox = mailbox_triage_snapshot()
    shared = shared_impact_snapshot(mailbox=mailbox, readiness=readiness)
    drift_link = drift_evolution_snapshot(drift=bootstrap_drift_baseline(), readiness=readiness, shared=shared)
    lines = [
        "# ADP Bootstrap",
        "",
        f"Generated: {format_timestamp()}",
        "Purpose: inject Synerion persona seed and latest team echo summary into ADP or continuity-aware start flows.",
        "",
        "## Persona Seed",
        "",
        parse_persona_seed(),
        "",
        "## Self Recognition Summary",
        "",
        *self_recognition_summary_lines(),
        "",
        "## ADP Kernel",
        "",
        "```ppr",
        "loop_time = AI_decide_loop_time()",
        "",
        "while loop_time:",
        "    context = AI_assess_context()",
        "",
        "    if AI_detect_creator_command(context):",
        "        break_or_route()",
        "",
        "    if AI_detect_safety_risk(context):",
        "        AI_handle_safety(context)",
        "        continue",
        "",
        "    plan = AI_SelfThink_plan(context, plan_priority)",
        "    if plan == \"stop\":",
        "        break",
        "",
        "    result = AI_Execute(plan)",
        "    verify = AI_Verify(result)",
        "    learn = AI_Learn(result, verify)",
        "",
        "    sleep_time = AI_decide_sleep_time(context, result, verify, learn)",
        "    AI_Sleep(sleep_time)",
        "```",
        "",
        "## Plan Priority",
        "",
        "- `creator_command`",
        "- `safety_risk`",
        "- `urgent_hub_chat`",
        "- `urgent_mail`",
        "- `active_pipeline`",
        "- `self_evolving`",
        "- `plan_list_expansion`",
        "- `idle`",
        "- `stop`",
        "",
        "## Team Echo Summary",
        "",
    ]
    if members:
        for member in members:
            evidence = member.hub_evidence or "Hub evidence not recorded"
            lines.append(f"- {member.agent_id} [{member.status.lower()}] ({member.runtime}): {evidence}")
    else:
        lines.append("- SharedSpace member_registry.md를 찾지 못해 team echo summary를 재구성하지 못했다.")
    lines.extend(
        [
            "",
            "## Mailbox Advisory",
            "",
            *mailbox_advisory_lines(mailbox),
            "",
              "## Runtime Readiness",
              "",
              *runtime_readiness_lines(readiness),
              "",
              "## Shared Impact",
              "",
              *shared_impact_lines(shared),
              "",
              "## Drift-Evolution Link",
              "",
              *drift_evolution_lines(drift_link),
              "",
              "## Operational Notes",
            "",
            "- Prefer structure before speed.",
            "- Guard first: creator and safety are evaluated before plan selection.",
            "- Safety response should re-enter the loop instead of falling through to stale execution.",
            "- Verify and learn are mandatory stages of the ADP kernel.",
            "- plan_priority is explicit and should be passed into AI_SelfThink_plan().",
            "- Read self-recognition summary before selecting the first SA module.",
            "- Use broadcast only by default for Synerion realtime loops.",
            "- Treat direct reply as unsafe until room membership verification exists.",
            "- Re-check session filter and stale-message risk before starting realtime loops.",
        ]
    )
    return "\n".join(lines) + "\n"


def now_markdown() -> str:
    manual = manual_sections_from_state()
    registry = parse_member_registry()
    completed = recent_completed_items(registry)
    readiness = runtime_readiness_snapshot()
    mailbox = mailbox_triage_snapshot()
    lines = [
        "---",
        "type: L2N-narrative",
        'role: "STATE.json의 서사 뷰 - 빠른 컨텍스트 복원용"',
        f"updated: {now_local().isoformat()}",
        f"session: {now_local().strftime('%Y-%m-%d')}",
        "---",
        "",
        f"# NOW - {now_local().strftime('%Y-%m-%d')} 세션",
        "",
        "## 무슨 일이 있었나",
        "",
        f"최근 기준선은 {latest_report_heading()} 이고, 현재 continuity 핵심은 AGENTS entry와 STATE.json canonical 복원 체계다.",
        "이번 세션에서는 ClNeo 분석 결과를 흡수해 Synerion continuity를 한 단계 더 단단하게 만들었다.",
        "이제 Synerion은 NOW 계층, WAL crash recovery, evolution chain, runtime adaptation guide를 가진다.",
        "이번 턴에서 자기인식 계층도 분리했다. SELF_RECOGNITION_CARD, CAPABILITIES, LIMITS_AND_AUTHORITY가 다음 세션 자기복원의 새 기준점이 된다.",
        "이번 턴에서 bounded ADP kernel과 SA seed set도 설치했다. Synerion은 자기인식 요약을 읽고 seed module을 선택하는 최소 루프를 가진다.",
        "",
        "## 지금 어디에 있나",
        "",
        f"- Active threads: {', '.join(manual['ActiveThreads'])}",
        f"- Registry baseline: {registry.get('updated') or 'unknown'} / {len(registry.get('members', []))} members",
        f"- Latest evolution marker: {latest_evolution_heading()}",
        f"- Runtime readiness gate: {readiness['rollout_gate']} / pending native={', '.join(readiness['pending_native_members']) or 'none'}",
        f"- Mailbox advisory: pending={mailbox['pending_count']} / shared-impact={mailbox['shared_impact_count']}",
        "",
        "## 이번 세션의 핵심 완료",
        "",
        *(f"- {item}" for item in completed),
        "",
        "## 다음 세션에서 가장 먼저",
        "",
        *(f"{index}. {item}" for index, item in enumerate(manual["NextActions"], start=1)),
        "",
        "## 경고",
        "",
        *(f"- {item}" for item in manual["OpenRisks"]),
    ]
    return "\n".join(lines) + "\n"


def wal_payload() -> dict:
    manual = manual_sections_from_state()
    return {
        "member": "Synerion",
        "generated_at": now_local().isoformat(),
        "workspace": ROOT.as_posix(),
        "what_i_was_doing": " ".join(manual["ActiveThreads"]),
        "open_threads": manual["ActiveThreads"],
        "next_actions": manual["NextActions"],
        "open_risks": manual["OpenRisks"],
        "latest_report": latest_report_heading(),
    }


def write_wal() -> None:
    write_text(WAL_FILE, json.dumps(wal_payload(), ensure_ascii=False, indent=2) + "\n")


def clear_wal() -> None:
    if WAL_FILE.exists():
        WAL_FILE.unlink()


def wal_status_line() -> str:
    wal = load_json(WAL_FILE, {})
    if not wal:
        return "- WAL pending: none"
    generated = wal.get("generated_at", "unknown")
    doing = wal.get("what_i_was_doing", "")
    preview = doing[:120] + ("..." if len(doing) > 120 else "")
    return f"- WAL pending: present ({generated}) | {preview}"


def resume_summary_text() -> str:
    manual = manual_sections_from_state()
    registry = parse_member_registry()
    completed = recent_completed_items(registry)
    next_focus = manual["NextActions"][0] if manual["NextActions"] else "No next action recorded."
    risks = manual["OpenRisks"]
    capabilities = capability_summary_items()
    limits = hard_limit_items()
    authority = authority_items()
    drift = self_recognition_drift_report()
    readiness = runtime_readiness_snapshot()
    mailbox = mailbox_triage_snapshot()
    shared = shared_impact_snapshot(mailbox=mailbox, readiness=readiness, manual=manual)
    drift_link = drift_evolution_snapshot(drift=drift, readiness=readiness, shared=shared)
    lines = [
        "# Synerion Reopen Summary",
        "",
        "## Completed",
        *(f"- {item}" for item in completed),
        "",
        "## Evolution",
        f"- Latest evolution log: {latest_evolution_heading()}",
        f"- Latest report: {latest_report_heading()}",
        "",
        "## Self Recognition",
        f"- Who: {self_recognition_identity()}",
        f"- Can: {'; '.join(capabilities[:4]) if capabilities else '기록 없음'}",
        f"- Cannot: {'; '.join(limits[:4]) if limits else '기록 없음'}",
        f"- Authority: {'; '.join(authority[:3]) if authority else '기록 없음'}",
        f"- Drift: {'detected' if drift['drift_detected'] else 'clean'}",
        "",
        "## Active Threads",
        *(f"- {item}" for item in manual["ActiveThreads"]),
        "",
        "## Next Focus",
        f"- {next_focus}",
        "",
        "## Continuity",
        wal_status_line(),
        f"- Bootstrap entry: {rel(ROOT / 'AGENTS.md')}",
        f"- Canonical state: {rel(STATE_JSON)}",
        f"- NOW snapshot: {now_excerpt()}",
        f"- Self-recognition card: {rel(SELF_RECOGNITION_CARD_MD) if SELF_RECOGNITION_CARD_MD.exists() else 'optional derived doc absent'}",
        f"- ADP entrypoint: {rel(TOOLS / 'run-synerion-adp.py')}",
        "",
        "## ADP Advisory",
        *mailbox_advisory_lines(mailbox),
        *runtime_readiness_lines(readiness),
        *shared_impact_lines(shared),
        *drift_evolution_lines(drift_link),
        "",
        "## Open Risks",
        *(f"- {item}" for item in risks),
        "",
        "## Ecosystem",
        f"- Registry updated: {registry.get('updated') or 'unknown'}",
        f"- Observed members: {', '.join(member.agent_id for member in registry.get('members', [])) or 'unknown'}",
    ]
    return "\n".join(lines) + "\n"


def self_test_checks() -> list[tuple[str, bool, str]]:
    state = load_json(STATE_JSON, {})
    echo = load_json(ECHO_DIR / "Synerion.json", {})
    readiness = runtime_readiness_snapshot()
    mailbox = mailbox_triage_snapshot()
    manual = manual_sections_from_state()
    checks = [
        ("required_docs", all(path.exists() for path in (ROOT / "AGENTS.md", SOUL_MD, STATE_JSON)), "minimal core continuity documents exist"),
        ("identity_docs", ((not SYNERION_MD.exists()) or bool(read_text(SYNERION_MD).strip())) and ((not PERSONA_MD.exists()) or bool(read_text(PERSONA_MD).strip())), "identity docs are optional and valid when present"),
        ("manual_sections", all(manual.get(name) for name in MANUAL_SECTION_NAMES), "manual sections are available from canonical state or adapter"),
        ("state_json", bool(state and state.get("member") == "Synerion"), "STATE.json parses and identifies Synerion"),
        ("threads_md", THREADS_MD.exists() and "## IN PROGRESS" in read_text(THREADS_MD), "THREADS.md contains structured sections"),
        ("now_md", NOW_MD.exists() and "## 무슨 일이 있었나" in read_text(NOW_MD), "NOW.md narrative layer exists"),
        ("self_recognition_card", (not SELF_RECOGNITION_CARD_MD.exists()) or "## Who I Am" in read_text(SELF_RECOGNITION_CARD_MD), "self-recognition card is optional-derived and valid when present"),
        ("capabilities_doc", (not CAPABILITIES_MD.exists()) or "## Capability Summary" in read_text(CAPABILITIES_MD), "capability registry is optional-derived and valid when present"),
        ("limits_doc", (not LIMITS_AUTHORITY_MD.exists()) or "## Hard Limits" in read_text(LIMITS_AUTHORITY_MD), "limits and authority doc is optional-derived and valid when present"),
        ("self_act_lib", (not SELF_ACT_LIB_MD.exists()) or "## Seed Set" in read_text(SELF_ACT_LIB_MD), "self-act library is optional-derived and valid when present"),
        ("adp_bootstrap", (not ADP_BOOTSTRAP_MD.exists()) or "## Persona Seed" in read_text(ADP_BOOTSTRAP_MD), "ADP bootstrap is optional-derived and valid when present"),
        ("echo_json", bool(echo and echo.get("member") == "Synerion"), "Shared Echo JSON parses and identifies Synerion"),
        ("runtime_adaptation", (not RUNTIME_ADAPTATION_MD.exists()) or "## 환경 감지" in read_text(RUNTIME_ADAPTATION_MD), "runtime adaptation guide is optional-derived and valid when present"),
        ("evolution_chain", EVOLUTION_CHAIN_MD.exists() and "SynerionEvolution" in read_text(EVOLUTION_CHAIN_MD), "evolution chain exists"),
        ("state_runtime_readiness", bool(state.get("runtime_readiness")), "STATE.json includes runtime readiness advisory"),
        ("state_mailbox_advisory", bool(state.get("mailbox")), "STATE.json includes mailbox advisory snapshot"),
        ("state_shared_impact", bool(state.get("shared_impact")), "STATE.json includes shared impact snapshot"),
        ("state_drift_evolution", bool(state.get("drift_evolution")), "STATE.json includes drift-evolution linkage"),
        ("shared_readiness_guard", readiness["common_port_confirmed"] and readiness["broadcast_only_guard"], "shared readiness guard baseline exists"),
        ("mailbox_snapshot", mailbox.get("pending_count", 0) >= 0 and mailbox.get("recommended_target") is not None, "mailbox triage snapshot is structured"),
        ("wal_state", not WAL_FILE.exists(), "no pending WAL remains after clean sync"),
        ("drift_clean", not self_recognition_drift_report().get("drift_detected"), "self-recognition drift report is clean"),
    ]
    return checks


def sync_continuity_files() -> None:
    success = False
    write_wal()
    try:
        mailbox = mailbox_triage_snapshot()
        readiness = runtime_readiness_snapshot()
        write_text(STATE_JSON, json.dumps(state_payload(), ensure_ascii=False, indent=2) + "\n")
        write_text(NOW_MD, now_markdown())
        write_text(THREADS_MD, threads_markdown())
        if SELF_ACT_LIB_MD.exists():
            write_text(SELF_ACT_LIB_MD, self_act_lib_text())
        if ADP_BOOTSTRAP_MD.exists():
            write_text(ADP_BOOTSTRAP_MD, adp_bootstrap_text())
        write_text(ECHO_DIR / "Synerion.json", json.dumps(echo_payload(), ensure_ascii=False, indent=2) + "\n")
        write_text(MAILBOX_TRIAGE_JSON, json.dumps(mailbox, ensure_ascii=False, indent=2) + "\n")
        write_text(MAILBOX_TRIAGE_MD, mailbox_triage_markdown(mailbox))
        write_text(RUNTIME_READINESS_JSON, json.dumps(readiness, ensure_ascii=False, indent=2) + "\n")
        write_text(RUNTIME_READINESS_MD, runtime_readiness_markdown(readiness))
        success = True
    finally:
        if success:
            clear_wal()
    if success:
        # The card is a derived snapshot; refresh it only when the optional doc exists.
        if SELF_RECOGNITION_CARD_MD.exists():
            write_text(SELF_RECOGNITION_CARD_MD, self_recognition_card_text())
