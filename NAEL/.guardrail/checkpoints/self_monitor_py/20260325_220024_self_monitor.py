#!/usr/bin/env python3
"""
Self-Monitor — 에이전트 능력 인벤토리 및 진화 추적기
====================================================
워크스페이스의 도구, 스킬, 지식 상태를 스캔하고 보고.

사용법:
  python self_monitor.py --scan          # 전체 능력 스캔
  python self_monitor.py --report        # 마크다운 보고서 생성
  python self_monitor.py --gaps          # gap 분석
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class CapabilityItem:
    name: str
    category: str  # tool, skill, knowledge, integration
    path: str
    status: str = "active"  # active, experimental, deprecated
    description: str = ""
    created: str = ""
    dependencies: list[str] = field(default_factory=list)


@dataclass
class CapabilityMap:
    scan_date: str
    tools: list[CapabilityItem] = field(default_factory=list)
    skills: list[CapabilityItem] = field(default_factory=list)
    knowledge: list[CapabilityItem] = field(default_factory=list)
    integrations: list[CapabilityItem] = field(default_factory=list)

    def total_count(self) -> int:
        return len(self.tools) + len(self.skills) + len(self.knowledge) + len(self.integrations)

    def to_markdown(self) -> str:
        lines = [
            f"# Capability Inventory",
            f"**Scan Date**: {self.scan_date}",
            f"**Total Capabilities**: {self.total_count()}",
            f"",
        ]

        for category, items in [
            ("Tools", self.tools),
            ("Skills", self.skills),
            ("Knowledge", self.knowledge),
            ("Integrations", self.integrations),
        ]:
            lines.append(f"## {category} ({len(items)})")
            if not items:
                lines.append("(none)")
            else:
                lines.append("| Name | Status | Path | Description |")
                lines.append("|------|--------|------|-------------|")
                for item in items:
                    lines.append(f"| {item.name} | {item.status} | `{item.path}` | {item.description} |")
            lines.append("")

        return "\n".join(lines)

    def to_json(self) -> str:
        def item_dict(item):
            return {
                "name": item.name,
                "category": item.category,
                "path": item.path,
                "status": item.status,
                "description": item.description,
                "dependencies": item.dependencies,
            }
        return json.dumps({
            "scan_date": self.scan_date,
            "tools": [item_dict(i) for i in self.tools],
            "skills": [item_dict(i) for i in self.skills],
            "knowledge": [item_dict(i) for i in self.knowledge],
            "integrations": [item_dict(i) for i in self.integrations],
            "summary": {
                "total": self.total_count(),
                "tools": len(self.tools),
                "skills": len(self.skills),
                "knowledge": len(self.knowledge),
                "integrations": len(self.integrations),
            },
        }, indent=2, ensure_ascii=False)


def scan_workspace_tools(workspace: str) -> list[CapabilityItem]:
    """워크스페이스의 도구 스캔"""
    items = []
    tools_dir = Path(workspace) / "tools"
    if not tools_dir.exists():
        return items

    for py_file in tools_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        # 첫 번째 docstring에서 설명 추출
        desc = ""
        try:
            content = py_file.read_text(encoding="utf-8")
            if '"""' in content:
                start = content.index('"""') + 3
                end = content.index('"""', start)
                first_line = content[start:end].strip().split("\n")[0]
                desc = first_line[:100]
        except Exception:
            pass

        rel_path = str(py_file.relative_to(workspace))
        category_hint = py_file.parent.name
        items.append(CapabilityItem(
            name=py_file.stem,
            category=f"tool/{category_hint}",
            path=rel_path,
            description=desc,
            created=datetime.fromtimestamp(py_file.stat().st_ctime).strftime("%Y-%m-%d"),
        ))

    return items


def scan_skills(skills_dir: str) -> list[CapabilityItem]:
    """Claude Code 스킬 스캔"""
    items = []
    sd = Path(skills_dir)
    if not sd.exists():
        return items

    for skill_md in sd.glob("*/SKILL.md"):
        skill_name = skill_md.parent.name
        desc = ""
        try:
            content = skill_md.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("# "):
                    desc = line[2:].strip()[:100]
                    break
        except Exception:
            pass

        items.append(CapabilityItem(
            name=skill_name,
            category="skill",
            path=str(skill_md),
            description=desc,
        ))

    return items


def scan_knowledge(workspace: str) -> list[CapabilityItem]:
    """지식 베이스 스캔"""
    items = []
    kb_dir = Path(workspace) / "knowledge"
    if not kb_dir.exists():
        return items

    for md_file in kb_dir.rglob("*.md"):
        desc = ""
        try:
            content = md_file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.strip() and not line.startswith("#") and not line.startswith("---"):
                    desc = line.strip()[:100]
                    break
        except Exception:
            pass

        items.append(CapabilityItem(
            name=md_file.stem,
            category="knowledge",
            path=str(md_file.relative_to(workspace)),
            description=desc,
        ))

    return items


def full_scan(workspace: str, skills_dir: str) -> CapabilityMap:
    """전체 능력 스캔"""
    cap_map = CapabilityMap(
        scan_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        tools=scan_workspace_tools(workspace),
        skills=scan_skills(skills_dir),
        knowledge=scan_knowledge(workspace),
    )
    return cap_map


# ========== Gap Analysis ==========

IDEAL_CAPABILITIES = {
    "cognitive": [
        ("multi-perspective debate", ["debate", "persona", "perspective"]),
        ("knowledge synthesis", ["synthe", "knowledge"]),
        ("hypothesis testing", ["hypothesis", "experiment"]),
        ("structured analysis", ["analy", "structured"]),
        ("creative ideation", ["creat", "idea", "discover"]),
    ],
    "automation": [
        ("code scaffold", ["scaffold"]),
        ("test generation", ["test gen", "test creat"]),
        ("self-monitor", ["monitor", "self_monitor"]),
        ("batch processing", ["batch", "parallel"]),
        ("scheduled tasks", ["schedul", "cron"]),
    ],
    "knowledge": [
        ("research pipeline", ["research", "ingest"]),
        ("knowledge graph", ["graph", "knowledge"]),
        ("cross-domain index", ["cross-domain", "index", "knowledge_index"]),
        ("trend tracking", ["trend", "radar"]),
        ("source verification", ["verif", "source", "source_verify"]),
    ],
    "meta": [
        ("capability inventory", ["inventory", "capability", "self_monitor", "인벤토리"]),
        ("evolution logging", ["evolution", "log"]),
        ("performance metrics", ["metric", "performance", "perf_metrics"]),
        ("gap detection", ["gap", "self_monitor", "분석"]),
        ("session continuity", ["session", "save-session", "handoff"]),
    ],
}


def analyze_gaps(cap_map: CapabilityMap) -> dict:
    """현재 능력 vs 이상 비교"""
    # 모든 능력의 이름+설명을 하나의 검색 대상 문자열로 합침
    all_items = cap_map.tools + cap_map.skills + cap_map.knowledge + cap_map.integrations
    search_corpus = " ".join(
        f"{item.name} {item.description} {item.category}" for item in all_items
    ).lower()

    gaps = {}
    for category, ideals in IDEAL_CAPABILITIES.items():
        category_gaps = []
        for ideal_name, keywords in ideals:
            found = any(kw in search_corpus for kw in keywords)
            if not found:
                category_gaps.append(ideal_name)
        if category_gaps:
            gaps[category] = category_gaps

    return gaps


def gap_report(gaps: dict) -> str:
    """gap 분석 보고서"""
    if not gaps:
        return "No significant gaps detected. Evolution may be stabilizing."

    lines = ["# Capability Gap Analysis", ""]
    total_gaps = sum(len(g) for g in gaps.values())
    lines.append(f"**Total Gaps**: {total_gaps}")
    lines.append("")

    for category, gap_list in gaps.items():
        lines.append(f"## {category.title()} ({len(gap_list)} gaps)")
        for g in gap_list:
            lines.append(f"- [ ] {g}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Self-Monitor")
    parser.add_argument("--scan", action="store_true", help="Full capability scan")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--gaps", action="store_true", help="Gap analysis")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--workspace", default=str(Path(__file__).resolve().parents[3]), help="Workspace path")
    parser.add_argument("--skills-dir", default=os.path.expanduser("~/.claude/skills"), help="Skills directory")
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    cap_map = full_scan(args.workspace, args.skills_dir)

    if args.gaps:
        gaps = analyze_gaps(cap_map)
        result = gap_report(gaps)
    elif args.json:
        result = cap_map.to_json()
    else:
        result = cap_map.to_markdown()

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
