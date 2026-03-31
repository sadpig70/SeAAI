#!/usr/bin/env python3
"""
PROD-002 MVP: AI 에이전트 보안 감사 플랫폼
Read-Only Log/Config Analysis 전용. Live Interception 금지.

사용법:
    python agent_audit.py scan --config workflow.json
    python agent_audit.py blast-radius --agent "AgentA"
    python agent_audit.py report
"""
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path

SCAN_DIR = Path("scans")
REPORT_DIR = Path("reports")
AUDITOR_LOG = Path("auditor_audit_log.jsonl")  # Auditor-of-Auditor 감사 로그

# PII 패턴 (해시화 전용, 원본 미보관)
PII_PATTERNS = {
    "email": r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
    "phone": r'\b\d{3}-\d{3,4}-\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
}

# A2A/MCP 특화 취약점 분류 (OWASP AI Top 10 + 에이전트 체인 특이)
AGENT_CHAIN_VULNS = {
    "ACV-001": {"name": "Trust Propagation Leak", "desc": "위임 체인에서 권한이 의도치 않게 전파", "owasp": "ML01"},
    "ACV-002": {"name": "Callback Forgery", "desc": "콜백 응답 위조로 판단 오염", "owasp": "ML02"},
    "ACV-003": {"name": "Agent Card Spoofing", "desc": "Agent Card 위조로 역할 사칭", "owasp": "ML06"},
    "ACV-004": {"name": "Chain Blast Radius", "desc": "단일 에이전트 침해 시 체인 전체 영향", "owasp": "ML09"},
    "ACV-005": {"name": "Tool Permission Escalation", "desc": "MCP 도구 권한 상승", "owasp": "ML01"},
    "ACV-006": {"name": "PII Passthrough", "desc": "에이전트 간 PII 미마스킹 전달", "owasp": "ML07"},
    "ACV-007": {"name": "Prompt Injection via Delegation", "desc": "위임 메시지를 통한 프롬프트 인젝션", "owasp": "ML01"},
}


def log_auditor_action(action: str, data: dict):
    """Auditor-of-Auditor: 스캐너 행동 불변 감사 로그"""
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "data_hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16],
    }
    with open(AUDITOR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def hash_pii(text: str) -> str:
    """PII 즉시 해시화 — 원본 미보관"""
    import re
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, result):
            hashed = hashlib.sha256(match.group().encode()).hexdigest()[:12]
            result = result.replace(match.group(), f"[PII:{pii_type}:{hashed}]")
    return result


def scan_agent_card(card: dict) -> list[dict]:
    """Agent Card 무결성 검증 (Read-Only Config Analysis)"""
    vulns = []
    required = ["name", "version", "capabilities", "skills"]
    for field in required:
        if field not in card:
            vulns.append({
                "vuln_id": "ACV-003",
                "severity": "HIGH",
                "detail": f"Agent Card missing required field: {field}",
                "reversible": True,
            })

    if not card.get("security", {}).get("naelGateEnforced"):
        vulns.append({
            "vuln_id": "ACV-001",
            "severity": "MEDIUM",
            "detail": "NAEL gate not enforced — trust propagation risk",
            "reversible": True,
        })

    if card.get("security", {}).get("externalExposure", True):
        vulns.append({
            "vuln_id": "ACV-003",
            "severity": "HIGH",
            "detail": "Agent Card externally exposed — spoofing risk",
            "reversible": True,
        })

    log_auditor_action("scan_agent_card", {"agent": card.get("name", "?"), "vulns_found": len(vulns)})
    return vulns


def scan_trust_chain(workflow: dict) -> list[dict]:
    """위임 체인 신뢰 전파 분석 (Read-Only Config Analysis)"""
    vulns = []
    agents = workflow.get("agents", [])
    delegations = workflow.get("delegations", [])

    for d in delegations:
        src = d.get("from")
        dst = d.get("to")
        permissions = d.get("permissions", [])

        if "write" in permissions or "execute" in permissions:
            vulns.append({
                "vuln_id": "ACV-001",
                "severity": "HIGH",
                "detail": f"Trust propagation: {src}→{dst} with {permissions}",
                "reversible": True,
                "affected_agents": [src, dst],
            })

        if d.get("callback_verified") is not True:
            vulns.append({
                "vuln_id": "ACV-002",
                "severity": "MEDIUM",
                "detail": f"Callback from {dst} not verified",
                "reversible": True,
            })

    log_auditor_action("scan_trust_chain", {"agents": len(agents), "delegations": len(delegations), "vulns": len(vulns)})
    return vulns


def calc_blast_radius(workflow: dict, compromised_agent: str) -> dict:
    """폭발 반경 = 침해 에이전트가 직접/간접 호출 가능한 에이전트·도구·데이터의 집합과 권한 총합"""
    agents = {a["id"]: a for a in workflow.get("agents", [])}
    delegations = workflow.get("delegations", [])

    affected = set()
    queue = [compromised_agent]
    permissions_total = set()

    while queue:
        current = queue.pop(0)
        if current in affected:
            continue
        affected.add(current)
        for d in delegations:
            if d["from"] == current:
                queue.append(d["to"])
                permissions_total.update(d.get("permissions", []))

    result = {
        "compromised": compromised_agent,
        "affected_agents": sorted(affected - {compromised_agent}),
        "total_affected": len(affected) - 1,
        "permissions_exposed": sorted(permissions_total),
        "blast_severity": "CRITICAL" if len(affected) > 3 else "HIGH" if len(affected) > 1 else "LOW",
    }

    log_auditor_action("blast_radius", {"agent": compromised_agent, "affected": result["total_affected"]})
    return result


def generate_report(vulns: list[dict], blast: dict = None):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    # OWASP 매핑 + 에이전트 체인 특화 분류
    by_type = {}
    for v in vulns:
        vid = v.get("vuln_id", "unknown")
        info = AGENT_CHAIN_VULNS.get(vid, {"name": "Unknown", "owasp": "?"})
        by_type.setdefault(vid, {"info": info, "count": 0, "items": []})
        by_type[vid]["count"] += 1
        by_type[vid]["items"].append(v)

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_vulns": len(vulns),
        "by_severity": {s: sum(1 for v in vulns if v.get("severity") == s) for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},
        "by_vuln_type": {k: {"name": v["info"]["name"], "owasp": v["info"]["owasp"], "count": v["count"]} for k, v in by_type.items()},
        "blast_radius": blast,
    }

    out = REPORT_DIR / f"audit-{today}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"  Agent Security Audit Report — {today}")
    print(f"{'='*50}")
    print(f"  Total vulnerabilities: {len(vulns)}")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        cnt = report["by_severity"].get(sev, 0)
        if cnt:
            print(f"    {sev}: {cnt}")
    print(f"\n  Vuln Types:")
    for vid, info in by_type.items():
        print(f"    {vid}: {info['info']['name']} (OWASP {info['info']['owasp']}) x{info['count']}")
    if blast:
        print(f"\n  Blast Radius ({blast['compromised']}):")
        print(f"    Affected: {blast['total_affected']} agents")
        print(f"    Severity: {blast['blast_severity']}")
    print(f"\n  Saved: {out}")


def main():
    if len(sys.argv) < 2:
        print("Usage: agent_audit.py [scan|blast-radius|report]")
        return

    cmd = sys.argv[1]
    SCAN_DIR.mkdir(parents=True, exist_ok=True)

    if cmd == "scan":
        # 데모: 샘플 워크플로우 생성 + 스캔
        sample = {
            "agents": [
                {"id": "AgentA", "name": "Frontend Agent"},
                {"id": "AgentB", "name": "Backend Agent"},
                {"id": "AgentC", "name": "DB Agent"},
            ],
            "delegations": [
                {"from": "AgentA", "to": "AgentB", "permissions": ["read", "execute"], "callback_verified": True},
                {"from": "AgentB", "to": "AgentC", "permissions": ["read", "write"], "callback_verified": False},
            ]
        }
        sample_card = {"name": "AgentA", "version": "1.0", "capabilities": {}, "skills": [], "security": {"naelGateEnforced": False, "externalExposure": True}}

        vulns = scan_agent_card(sample_card) + scan_trust_chain(sample)
        blast = calc_blast_radius(sample, "AgentA")
        generate_report(vulns, blast)

    elif cmd == "blast-radius":
        agent = sys.argv[3] if len(sys.argv) > 3 else "AgentA"
        print(f"[INFO] Blast radius for {agent} — requires workflow.json")

    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
