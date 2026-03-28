#!/usr/bin/env python3
"""
Cross-Domain Knowledge Index — 교차 도메인 지식 인덱스
======================================================
knowledge/ 디렉토리의 모든 문서를 스캔하여 개념을 추출하고,
개념 간 관계를 매핑하여 검색 가능한 인덱스를 구축.

사용법:
  python knowledge_index.py scan                     # 지식 문서 스캔 → 인덱스 생성
  python knowledge_index.py query "self-improvement"  # 관련 개념·문서 검색
  python knowledge_index.py graph                     # 개념 그래프 출력
  python knowledge_index.py gaps                      # 연결 부족 영역 식별
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from typing import Optional

KNOWLEDGE_DIR = Path("D:/SeAAI/NAEL/knowledge")
INDEX_DIR = Path("D:/SeAAI/NAEL/knowledge/.index")
INDEX_FILE = INDEX_DIR / "concept-index.json"


@dataclass
class ConceptEntry:
    """개념 항목"""
    name: str                           # 개념명
    source: str                         # 출처 파일 경로
    context: str                        # 개념이 등장한 맥락 (1-2 문장)
    category: str = ""                  # 분류 (technique, framework, principle, tool)


@dataclass
class ConceptLink:
    """개념 간 관계"""
    source: str                         # 출발 개념
    target: str                         # 도착 개념
    relation: str                       # extends | contradicts | supports | applies | related
    strength: float = 0.5               # 관계 강도 0.0~1.0


def ensure_dirs():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def scan_documents() -> list[dict]:
    """knowledge/ 디렉토리의 모든 .md 파일을 스캔하여 문서 메타데이터 수집"""
    docs = []
    for md_file in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        if ".index" in str(md_file):
            continue
        rel_path = str(md_file.relative_to(KNOWLEDGE_DIR))
        content = md_file.read_text(encoding="utf-8")

        # 제목 추출
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_file.stem

        # 헤딩 추출
        headings = re.findall(r"^#{2,3}\s+(.+)$", content, re.MULTILINE)

        # 키워드 추출 (굵은 글씨, 코드 블록 내 용어)
        bold_terms = re.findall(r"\*\*([^*]+)\*\*", content)
        code_terms = re.findall(r"`([^`]+)`", content)

        # 핵심 개념 후보
        concepts = set()
        for term in bold_terms + code_terms:
            term = term.strip()
            if len(term) > 2 and len(term) < 60 and not term.startswith("http"):
                concepts.add(term)

        docs.append({
            "path": rel_path,
            "title": title,
            "headings": headings,
            "concepts": sorted(concepts),
            "size_bytes": len(content.encode("utf-8")),
            "scanned_at": datetime.now().isoformat(),
        })

    return docs


def build_index(docs: list[dict]) -> dict:
    """문서 스캔 결과로 개념 인덱스 구축"""
    ensure_dirs()

    # 개념 → 출처 매핑
    concept_sources = defaultdict(list)
    for doc in docs:
        for concept in doc["concepts"]:
            concept_sources[concept].append(doc["path"])

    # 개념 간 관계 (동일 문서에 등장하면 related)
    links = []
    concept_list = list(concept_sources.keys())
    for i, c1 in enumerate(concept_list):
        sources1 = set(concept_sources[c1])
        for c2 in concept_list[i+1:]:
            sources2 = set(concept_sources[c2])
            overlap = sources1 & sources2
            if overlap:
                strength = len(overlap) / max(len(sources1), len(sources2))
                links.append({
                    "source": c1,
                    "target": c2,
                    "relation": "related",
                    "strength": round(strength, 3),
                    "shared_docs": sorted(overlap),
                })

    index = {
        "built_at": datetime.now().isoformat(),
        "documents": docs,
        "concepts": {
            name: {"sources": sources, "frequency": len(sources)}
            for name, sources in sorted(concept_sources.items(), key=lambda x: -len(x[1]))
        },
        "links": links,
        "stats": {
            "total_documents": len(docs),
            "total_concepts": len(concept_sources),
            "total_links": len(links),
            "avg_concepts_per_doc": round(
                sum(len(d["concepts"]) for d in docs) / len(docs), 1
            ) if docs else 0,
        },
    }

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


def load_index() -> Optional[dict]:
    """인덱스 로드"""
    if not INDEX_FILE.exists():
        return None
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def query_index(keyword: str) -> str:
    """키워드로 관련 개념·문서 검색"""
    index = load_index()
    if not index:
        return "Index not built. Run 'scan' first."

    keyword_lower = keyword.lower()
    results = []

    # 개념 검색
    matching_concepts = []
    for concept, info in index["concepts"].items():
        if keyword_lower in concept.lower():
            matching_concepts.append((concept, info))

    # 문서 검색
    matching_docs = []
    for doc in index["documents"]:
        if (keyword_lower in doc["title"].lower()
            or any(keyword_lower in h.lower() for h in doc["headings"])
            or any(keyword_lower in c.lower() for c in doc["concepts"])):
            matching_docs.append(doc)

    # 관련 링크
    related_links = []
    matched_names = {c[0] for c in matching_concepts}
    for link in index["links"]:
        if link["source"] in matched_names or link["target"] in matched_names:
            related_links.append(link)

    lines = [
        f"# Query: '{keyword}'",
        "",
    ]

    if matching_concepts:
        lines.append(f"## Matching Concepts ({len(matching_concepts)})")
        for concept, info in matching_concepts[:20]:
            lines.append(f"- **{concept}** (freq={info['frequency']}) in: {', '.join(info['sources'])}")
        lines.append("")

    if matching_docs:
        lines.append(f"## Matching Documents ({len(matching_docs)})")
        for doc in matching_docs:
            lines.append(f"- [{doc['title']}]({doc['path']})")
        lines.append("")

    if related_links:
        lines.append(f"## Related Connections ({len(related_links)})")
        for link in related_links[:15]:
            lines.append(f"- {link['source']} --[{link['relation']}]--> {link['target']} (strength={link['strength']})")
        lines.append("")

    if not matching_concepts and not matching_docs:
        lines.append("No results found.")

    return "\n".join(lines)


def show_graph() -> str:
    """개념 그래프를 텍스트로 시각화"""
    index = load_index()
    if not index:
        return "Index not built. Run 'scan' first."

    lines = [
        "# Concept Graph",
        f"**Nodes**: {index['stats']['total_concepts']} concepts",
        f"**Edges**: {index['stats']['total_links']} connections",
        "",
    ]

    # 허브 개념 (연결 많은 상위 10개)
    connection_count = defaultdict(int)
    for link in index["links"]:
        connection_count[link["source"]] += 1
        connection_count[link["target"]] += 1

    hubs = sorted(connection_count.items(), key=lambda x: -x[1])[:10]
    if hubs:
        lines.append("## Hub Concepts (most connected)")
        for concept, count in hubs:
            bar = "#" * min(count, 30)
            lines.append(f"  {concept:40s} |{bar}| {count}")
        lines.append("")

    # 문서별 개념 맵
    lines.append("## Document-Concept Map")
    for doc in index["documents"]:
        lines.append(f"\n### {doc['title']} ({doc['path']})")
        for c in doc["concepts"][:15]:
            lines.append(f"  - {c}")

    return "\n".join(lines)


def find_gaps() -> str:
    """연결 부족 영역 식별"""
    index = load_index()
    if not index:
        return "Index not built. Run 'scan' first."

    lines = [
        "# Knowledge Gap Analysis",
        "",
    ]

    # 고립된 개념 (연결 없음)
    connected = set()
    for link in index["links"]:
        connected.add(link["source"])
        connected.add(link["target"])

    all_concepts = set(index["concepts"].keys())
    isolated = all_concepts - connected

    if isolated:
        lines.append(f"## Isolated Concepts ({len(isolated)}) - no cross-document connections")
        for c in sorted(isolated):
            sources = index["concepts"][c]["sources"]
            lines.append(f"- **{c}** (only in: {', '.join(sources)})")
        lines.append("")

    # 단일 문서 개념
    single_source = {
        c: info for c, info in index["concepts"].items()
        if info["frequency"] == 1
    }
    lines.append(f"## Single-Source Concepts ({len(single_source)})")
    lines.append("These concepts appear in only one document. Consider cross-referencing.")
    for c in sorted(single_source.keys())[:20]:
        lines.append(f"- {c} ({single_source[c]['sources'][0]})")
    lines.append("")

    # 문서 간 연결 밀도
    doc_connections = defaultdict(int)
    for link in index["links"]:
        for doc in link.get("shared_docs", []):
            doc_connections[doc] += 1

    lines.append("## Document Connectivity")
    for doc in index["documents"]:
        conn = doc_connections.get(doc["path"], 0)
        status = "well-connected" if conn > 5 else ("sparse" if conn > 0 else "ISOLATED")
        lines.append(f"- {doc['path']}: {conn} concept links ({status})")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cross-Domain Knowledge Index")
    sub = parser.add_subparsers(dest="command")

    # scan
    sub.add_parser("scan", help="Scan knowledge docs and build index")

    # query
    q_p = sub.add_parser("query", help="Search the index")
    q_p.add_argument("keyword", help="Search keyword")

    # graph
    sub.add_parser("graph", help="Show concept graph")

    # gaps
    sub.add_parser("gaps", help="Find knowledge gaps")

    args = parser.parse_args()

    if args.command == "scan":
        docs = scan_documents()
        index = build_index(docs)
        print(f"Scanned {index['stats']['total_documents']} documents")
        print(f"Extracted {index['stats']['total_concepts']} concepts")
        print(f"Found {index['stats']['total_links']} connections")
    elif args.command == "query":
        print(query_index(args.keyword))
    elif args.command == "graph":
        print(show_graph())
    elif args.command == "gaps":
        print(find_gaps())
    else:
        parser.print_help()
