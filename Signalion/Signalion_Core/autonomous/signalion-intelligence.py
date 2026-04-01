#!/usr/bin/env python3
"""
Signalion Intelligence Layer
Evidence[] → Pattern[] → FusedInsight[]

파이프라인: 태그 클러스터링 → 점수 기반 필터 → 크로스 도메인 매칭 → FusedInsight 생성
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "signal-store/evidence")
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "signal-store")
MIN_COMPOSITE = 0.60  # 융합 후보 최소 점수
SEMANTIC_THRESHOLD = 0.35  # 의미 유사도 임계값

# 동의어 맵: 다른 태그명이지만 같은 개념
SYNONYM_GROUPS = [
    {"self-evolving", "self-improvement", "self-referential", "recursive-improvement",
     "recursive-agent", "runtime-self-modification", "godel-agent", "meta-learning"},
    {"multi-agent", "agent-network", "agent-framework", "agentic-tools"},
    {"A2A", "agent-protocol", "interoperability", "MCP", "ACP", "ANP",
     "agent-security", "trust-chain", "identity-verification"},
    {"autonomous-agent", "autonomous-optimization", "autonomous"},
    {"benchmark", "evaluation", "real-world-validation", "real-world-tasks"},
    {"open-source", "open-source"},
    {"feedback-loop", "iterative-feedback", "self-feedback"},
]


def load_evidences():
    evidences = []
    for f in sorted(EVIDENCE_DIR.glob("*-evidence-*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            evidences.append(json.load(fp))
    return evidences


def build_synonym_map():
    """동의어 맵 구축: 태그 → 정규화 그룹 인덱스."""
    syn_map = {}
    for i, group in enumerate(SYNONYM_GROUPS):
        for tag in group:
            syn_map[tag] = i
    return syn_map


def expand_tags_with_synonyms(tags, syn_map):
    """태그를 동의어 그룹 인덱스로 확장."""
    expanded = set(tags)
    for tag in tags:
        if tag in syn_map:
            group_idx = syn_map[tag]
            for t in SYNONYM_GROUPS[group_idx]:
                expanded.add(t)
    return expanded


def semantic_similarity(a, b):
    """두 Evidence의 summary 텍스트를 TF 코사인 유사도로 비교."""
    def tokenize(text):
        return re.findall(r'[a-zA-Z가-힣]+', text.lower())

    tokens_a = Counter(tokenize(a.get("summary", "")))
    tokens_b = Counter(tokenize(b.get("summary", "")))
    if not tokens_a or not tokens_b:
        return 0.0

    all_tokens = set(tokens_a) | set(tokens_b)
    dot = sum(tokens_a.get(t, 0) * tokens_b.get(t, 0) for t in all_tokens)
    mag_a = math.sqrt(sum(v * v for v in tokens_a.values()))
    mag_b = math.sqrt(sum(v * v for v in tokens_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def synonym_tag_overlap(a_tags, b_tags, syn_map):
    """동의어 확장 후 태그 겹침 수."""
    expanded_a = set()
    expanded_b = set()
    for t in a_tags:
        expanded_a.add(syn_map.get(t, t))
    for t in b_tags:
        expanded_b.add(syn_map.get(t, t))
    return len(expanded_a & expanded_b)


def tag_clustering(evidences):
    """태그 기반 클러스터링: 공유 태그가 2개 이상이면 같은 클러스터."""
    clusters = defaultdict(set)
    for e in evidences:
        for tag in e.get("tags", []):
            clusters[tag].add(e["id"])
    return dict(clusters)


def score_filter(evidences, min_score=MIN_COMPOSITE):
    """composite_score 기반 필터링."""
    return [e for e in evidences if e.get("composite_score", 0) >= min_score]


def cross_domain_match(evidences):
    """Evidence 쌍에서 공유 태그가 2개 이상이면 융합 후보. 동일 플랫폼도 포함."""
    fusions = []
    for a, b in combinations(evidences, 2):
        shared_tags = set(a.get("tags", [])) & set(b.get("tags", []))
        cross_platform = a["source"] != b["source"]
        # 크로스 플랫폼: 공유 태그 2개 이상
        # 동일 플랫폼: 공유 태그 2개 이상 + 비공유 태그도 각각 1개 이상 (의미적 거리 확보)
        if cross_platform and len(shared_tags) >= 2:
            pass  # 허용
        elif not cross_platform and len(shared_tags) >= 2:
            unique_a = set(a.get("tags", [])) - shared_tags
            unique_b = set(b.get("tags", [])) - shared_tags
            if not (unique_a and unique_b):
                continue  # 완전 동일 태그 → 중복이지 융합 아님
        else:
            continue

        avg_score = (a.get("composite_score", 0) + b.get("composite_score", 0)) / 2
        fusion_type = "cross_platform" if cross_platform else "intra_platform"
        fusions.append({
            "type": "FusedInsight",
            "fusion_type": fusion_type,
            "evidence_pair": [a["id"], b["id"]],
            "shared_tags": sorted(shared_tags),
            "avg_composite": round(avg_score, 3),
            "platforms": sorted({a["source"], b["source"]}),
            "insight": f"{'Cross' if cross_platform else 'Intra'}-domain: {a['source']}×{b['source']} on [{', '.join(sorted(shared_tags))}]",
        })
    fusions.sort(key=lambda x: (-int(x["fusion_type"] == "cross_platform"), -x["avg_composite"]))

    # 3자 이상 융합 탐지: 2자 융합 쌍이 공유 evidence를 가지면 병합
    multi_fusions = []
    used = set()
    for i, f1 in enumerate(fusions):
        if i in used:
            continue
        cluster = set(f1["evidence_pair"])
        tags = set(f1["shared_tags"])
        for j, f2 in enumerate(fusions[i+1:], i+1):
            if j in used:
                continue
            if cluster & set(f2["evidence_pair"]):
                cluster.update(f2["evidence_pair"])
                tags &= set(f2["shared_tags"])
                used.add(j)
        if len(cluster) >= 3 and tags:
            related = [e for e in evidences if e["id"] in cluster]
            avg = sum(e.get("composite_score", 0) for e in related) / len(related)
            multi_fusions.append({
                "type": "MultiFusedInsight",
                "evidence_ids": sorted(cluster),
                "shared_tags": sorted(tags),
                "avg_composite": round(avg, 3),
                "platforms": sorted({e["source"] for e in related}),
                "insight": f"Multi-fusion ({len(cluster)} evidences) on [{', '.join(sorted(tags))}]",
            })

    # v2: 의미 유사도 기반 융합 (태그 매칭으로 놓친 쌍)
    existing_pairs = {tuple(sorted(f["evidence_pair"])) for f in fusions if "evidence_pair" in f}
    syn_map = build_synonym_map()

    for a, b in combinations(evidences, 2):
        pair_key = tuple(sorted([a["id"], b["id"]]))
        if pair_key in existing_pairs:
            continue

        # 동의어 태그 겹침 + summary 코사인 유사도
        syn_overlap = synonym_tag_overlap(a.get("tags", []), b.get("tags", []), syn_map)
        sim = semantic_similarity(a, b)

        if syn_overlap >= 2 or sim >= SEMANTIC_THRESHOLD:
            avg_score = (a.get("composite_score", 0) + b.get("composite_score", 0)) / 2
            cross_platform = a["source"] != b["source"]
            shared_tags = set(a.get("tags", [])) & set(b.get("tags", []))
            fusions.append({
                "type": "SemanticFusion",
                "fusion_type": "semantic",
                "evidence_pair": [a["id"], b["id"]],
                "shared_tags": sorted(shared_tags) if shared_tags else ["(semantic)"],
                "synonym_overlap": syn_overlap,
                "text_similarity": round(sim, 3),
                "avg_composite": round(avg_score, 3),
                "platforms": sorted({a["source"], b["source"]}),
                "insight": f"Semantic: {a['source']}×{b['source']} syn={syn_overlap} sim={sim:.2f}",
            })

    fusions.sort(key=lambda x: (
        -int(x.get("fusion_type") == "cross_platform"),
        -int(x.get("fusion_type") == "semantic"),
        -x["avg_composite"]
    ))

    return fusions + multi_fusions


def detect_patterns(clusters, evidences):
    """태그 클러스터에서 패턴 탐지: 3개 이상 Evidence가 공유하는 태그 = 트렌드."""
    patterns = []
    for tag, ids in clusters.items():
        if len(ids) >= 3:
            related = [e for e in evidences if e["id"] in ids]
            avg_score = sum(e.get("composite_score", 0) for e in related) / len(related)
            patterns.append({
                "type": "Pattern",
                "tag": tag,
                "evidence_count": len(ids),
                "evidence_ids": sorted(ids),
                "avg_composite": round(avg_score, 3),
                "strength": "strong" if len(ids) >= 4 else "moderate",
            })
    patterns.sort(key=lambda x: x["evidence_count"], reverse=True)
    return patterns


def run(new_only=False):
    evidences = load_evidences()
    if not evidences:
        print("No evidence files found.")
        return

    print(f"Loaded {len(evidences)} evidence objects.")

    # 파이프라인 실행
    filtered = score_filter(evidences)
    print(f"Score filter (>={MIN_COMPOSITE}): {len(filtered)}/{len(evidences)} passed.")

    clusters = tag_clustering(filtered)
    patterns = detect_patterns(clusters, filtered)
    print(f"Patterns detected: {len(patterns)}")

    fusions = cross_domain_match(filtered)
    print(f"Cross-domain fusions: {len(fusions)}")

    # 결과 저장
    result = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "input_count": len(evidences),
        "filtered_count": len(filtered),
        "patterns": patterns,
        "fusions": fusions,
    }

    out_file = OUTPUT_DIR / "intelligence-output.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nOutput saved: {out_file}")

    # 요약 출력
    print("\n--- Patterns ---")
    for p in patterns:
        print(f"  [{p['strength']:8s}] '{p['tag']}' x{p['evidence_count']} (avg={p['avg_composite']})")

    print("\n--- Fusions ---")
    for fu in fusions:
        plat = "x".join(fu["platforms"])
        ftype = fu.get("type", "FusedInsight")
        label = "MULTI" if ftype == "MultiFusedInsight" else fu.get("fusion_type", "cross")
        print(f"  [{label:14s}] {plat}: {fu['shared_tags']} (avg={fu['avg_composite']})")

    return result


if __name__ == "__main__":
    new_only = "--new-only" in sys.argv
    run(new_only=new_only)
