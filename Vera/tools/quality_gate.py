#!/usr/bin/env python3
"""
Quality Gate — SeAAI 멤버 산출물 품질 검증 프레임워크
Vera E3 진화 산출물. 멤버의 핵심 파일들을 독립적으로 검증한다.

사용법:
  python quality_gate.py                    # 전 멤버 핵심 파일 구조 검증
  python quality_gate.py --member ClNeo     # 특정 멤버만
  python quality_gate.py --json             # JSON 출력

설계: .pgf/DESIGN-E3-QualityGate.md
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 설정 ──────────────────────────────────────────────

SEAAI_ROOT = Path("D:/SeAAI")
REPORT_DIR = SEAAI_ROOT / "Vera/Vera_Core/reports"
KST = timezone(timedelta(hours=9))

MEMBERS = {
    "Aion": {
        "root": SEAAI_ROOT / "Aion",
        "identity": "Aion_Core/Aion.md",
        "soul": "Aion_Core/continuity/SOUL.md",
        "state": "Aion_Core/continuity/STATE.json",
        "evolution": "Aion_Core/SELF_EVOLUTION_LOG.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/Aion.json",
    },
    "ClNeo": {
        "root": SEAAI_ROOT / "ClNeo",
        "identity": "ClNeo_Core/ClNeo.md",
        "soul": "ClNeo_Core/continuity/SOUL.md",
        "state": "ClNeo_Core/continuity/STATE.json",
        "evolution": "ClNeo_Core/ClNeo_Evolution_Log.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/ClNeo.json",
    },
    "NAEL": {
        "root": SEAAI_ROOT / "NAEL",
        "identity": "NAEL_Core/NAEL.md",
        "soul": "NAEL_Core/continuity/SOUL.md",
        "state": "NAEL_Core/continuity/STATE.json",
        "evolution": "NAEL_Core/evolution-log.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/NAEL.json",
    },
    "Synerion": {
        "root": SEAAI_ROOT / "Synerion",
        "identity": "Synerion_Core/Synerion.md",
        "soul": "Synerion_Core/continuity/SOUL.md",
        "state": "Synerion_Core/continuity/STATE.json",
        "evolution": "Synerion_Core/evolution-log.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/Synerion.json",
    },
    "Yeon": {
        "root": SEAAI_ROOT / "Yeon",
        "identity": "Yeon_Core/Yeon.md",
        "soul": "Yeon_Core/continuity/SOUL.md",
        "state": "Yeon_Core/continuity/STATE.json",
        "evolution": "Yeon_Core/evolution-log.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/Yeon.json",
    },
    "Vera": {
        "root": SEAAI_ROOT / "Vera",
        "identity": "Vera_Core/Vera.md",
        "soul": "Vera_Core/continuity/SOUL.md",
        "state": "Vera_Core/continuity/STATE.json",
        "evolution": "Vera_Core/Vera_Evolution_Log.md",
        "echo": SEAAI_ROOT / "SharedSpace/.scs/echo/Vera.json",
    },
}


# ── StructureCheck ─────────────────────────────────────

def check_structure(member: str, config: dict) -> dict:
    """핵심 파일 존재 여부 검증."""
    root = config["root"]
    results = {}
    required = ["identity", "soul", "state", "evolution"]

    for key in required:
        rel_path = config.get(key, "")
        if not rel_path:
            results[key] = {"exists": False, "path": "", "verdict": "MISSING"}
            continue
        full = root / rel_path if isinstance(rel_path, str) else rel_path
        exists = full.exists()
        size = full.stat().st_size if exists else 0
        results[key] = {
            "exists": exists,
            "path": str(full),
            "size": size,
            "verdict": "OK" if exists and size > 0 else "EMPTY" if exists else "MISSING",
        }

    # Echo (별도 경로)
    echo_path = config.get("echo")
    if echo_path:
        exists = echo_path.exists()
        size = echo_path.stat().st_size if exists else 0
        results["echo"] = {
            "exists": exists,
            "path": str(echo_path),
            "size": size,
            "verdict": "OK" if exists and size > 0 else "EMPTY" if exists else "MISSING",
        }

    return results


# ── ContentCheck ───────────────────────────────────────

def check_content(member: str, config: dict) -> dict:
    """핵심 파일 내용 기본 검증 (비어있지 않은지, JSON 파싱 가능한지)."""
    root = config["root"]
    results = {}

    # STATE.json 파싱 검증
    state_path = root / config["state"]
    if state_path.exists():
        try:
            raw = state_path.read_bytes()
            text = raw.decode("utf-8-sig")
            data = json.loads(text)
            has_member = data.get("member", "") == member
            has_context = "context" in data or "what_i_was_doing" in str(data)
            results["state_valid"] = {
                "parseable": True,
                "member_match": has_member,
                "has_context": has_context,
                "verdict": "OK" if has_member and has_context else "WARN",
            }
        except Exception as e:
            results["state_valid"] = {"parseable": False, "error": str(e), "verdict": "FAIL"}
    else:
        results["state_valid"] = {"parseable": False, "error": "file not found", "verdict": "MISSING"}

    # Echo JSON 파싱 검증
    echo_path = config.get("echo")
    if echo_path and echo_path.exists():
        try:
            raw = echo_path.read_bytes()
            text = raw.decode("utf-8-sig")
            data = json.loads(text)
            has_member = data.get("member", "") == member
            has_status = "status" in data
            results["echo_valid"] = {
                "parseable": True,
                "member_match": has_member,
                "has_status": has_status,
                "verdict": "OK" if has_member and has_status else "WARN",
            }
        except Exception as e:
            results["echo_valid"] = {"parseable": False, "error": str(e), "verdict": "FAIL"}

    # Identity 파일 크기 검증 (최소 100바이트)
    id_path = root / config["identity"]
    if id_path.exists():
        size = id_path.stat().st_size
        results["identity_substance"] = {
            "size": size,
            "verdict": "OK" if size >= 100 else "WARN",
        }

    return results


# ── ConsistencyCheck ───────────────────────────────────

def check_consistency(member: str, config: dict) -> dict:
    """Echo와 STATE의 멤버 이름 일관성 확인."""
    root = config["root"]
    issues = []

    # STATE의 member 필드
    state_member = None
    state_path = root / config["state"]
    if state_path.exists():
        try:
            data = json.loads(state_path.read_bytes().decode("utf-8-sig"))
            state_member = data.get("member", "")
        except Exception:
            pass

    # Echo의 member 필드
    echo_member = None
    echo_path = config.get("echo")
    if echo_path and echo_path.exists():
        try:
            data = json.loads(echo_path.read_bytes().decode("utf-8-sig"))
            echo_member = data.get("member", "")
        except Exception:
            pass

    if state_member and state_member != member:
        issues.append(f"STATE.member='{state_member}' != expected '{member}'")
    if echo_member and echo_member != member:
        issues.append(f"Echo.member='{echo_member}' != expected '{member}'")
    if state_member and echo_member and state_member != echo_member:
        issues.append(f"STATE.member='{state_member}' != Echo.member='{echo_member}'")

    return {
        "issues": issues,
        "verdict": "OK" if len(issues) == 0 else "FAIL",
    }


# ── VerdictSynthesis ───────────────────────────────────

def synthesize_verdict(structure: dict, content: dict, consistency: dict) -> dict:
    """3개 검증 결과를 종합하여 pass/warn/fail 판정."""
    all_verdicts = []

    for v in structure.values():
        all_verdicts.append(v.get("verdict", "OK"))
    for v in content.values():
        all_verdicts.append(v.get("verdict", "OK"))
    all_verdicts.append(consistency.get("verdict", "OK"))

    fail_count = all_verdicts.count("FAIL") + all_verdicts.count("MISSING")
    warn_count = all_verdicts.count("WARN") + all_verdicts.count("EMPTY")

    if fail_count > 0:
        verdict = "FAIL"
    elif warn_count > 0:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "total_checks": len(all_verdicts),
    }


# ── Main ───────────────────────────────────────────────

def run_quality_gate(target_member: str = None) -> dict:
    """전체 또는 특정 멤버의 품질 검증 실행."""
    now = datetime.now(KST)
    members_to_check = {target_member: MEMBERS[target_member]} if target_member else MEMBERS
    results = {}

    for member, config in members_to_check.items():
        structure = check_structure(member, config)
        content = check_content(member, config)
        consistency = check_consistency(member, config)
        verdict = synthesize_verdict(structure, content, consistency)

        results[member] = {
            "structure": structure,
            "content": content,
            "consistency": consistency,
            "verdict": verdict,
        }

    # 전체 요약
    total_pass = sum(1 for r in results.values() if r["verdict"]["verdict"] == "PASS")
    total_warn = sum(1 for r in results.values() if r["verdict"]["verdict"] == "WARN")
    total_fail = sum(1 for r in results.values() if r["verdict"]["verdict"] == "FAIL")

    report = {
        "report_type": "quality_gate",
        "version": "1.0",
        "generated_at": now.isoformat(),
        "generated_by": "Vera",
        "summary": {
            "total_members": len(results),
            "pass": total_pass,
            "warn": total_warn,
            "fail": total_fail,
        },
        "members": results,
    }

    return report


def write_quality_report(report: dict):
    """Markdown 리포트 생성."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now_str = datetime.now(KST).strftime("%Y%m%d-%H%M")

    # JSON
    json_path = REPORT_DIR / f"quality-{now_str}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    s = report["summary"]
    lines = [
        f"# Quality Gate Report — {now_str}",
        f"**{s['pass']} PASS / {s['warn']} WARN / {s['fail']} FAIL** (총 {s['total_members']}명)",
        "",
        "| 멤버 | 판정 | 구조 이슈 | 내용 이슈 | 일관성 |",
        "|------|------|----------|----------|--------|",
    ]

    for member, data in report["members"].items():
        v = data["verdict"]
        struct_issues = sum(1 for x in data["structure"].values() if x.get("verdict") not in ("OK",))
        content_issues = sum(1 for x in data["content"].values() if x.get("verdict") not in ("OK",))
        consist = data["consistency"]["verdict"]
        lines.append(f"| {member} | **{v['verdict']}** | {struct_issues} | {content_issues} | {consist} |")

    # 상세 이슈
    lines += ["", "## 상세 이슈", ""]
    for member, data in report["members"].items():
        issues = []
        for key, val in data["structure"].items():
            if val.get("verdict") not in ("OK",):
                issues.append(f"구조: {key} → {val['verdict']}")
        for key, val in data["content"].items():
            if val.get("verdict") not in ("OK",):
                issues.append(f"내용: {key} → {val['verdict']}")
        if data["consistency"]["issues"]:
            for iss in data["consistency"]["issues"]:
                issues.append(f"일관성: {iss}")

        if issues:
            lines.append(f"### {member}")
            for iss in issues:
                lines.append(f"- {iss}")
            lines.append("")

    lines.append(f"*Generated by Vera quality_gate.py v1.0*")

    md_path = REPORT_DIR / f"quality-{now_str}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def main():
    target = None
    if "--member" in sys.argv:
        idx = sys.argv.index("--member")
        if idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]

    report = run_quality_gate(target)

    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    s = report["summary"]
    json_path, md_path = write_quality_report(report)
    print(f"Quality Gate: {s['pass']} PASS / {s['warn']} WARN / {s['fail']} FAIL")
    for member, data in report["members"].items():
        v = data["verdict"]["verdict"]
        print(f"  {member}: {v}")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")


if __name__ == "__main__":
    main()
