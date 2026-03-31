#!/usr/bin/env python3
"""
PROD-003 MVP: AI 트렌드 인텔리전스 플랫폼
Signalion Intelligence Layer v2를 CLI 제품으로 래핑.

사용법:
    python trend_intel.py collect --channels arxiv,github,hn
    python trend_intel.py analyze
    python trend_intel.py fuse
    python trend_intel.py report
    python trend_intel.py full  (전 파이프라인)
"""
import json
import re
import sys
import math
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

# === 설정 ===
EVIDENCE_DIR = Path("evidence")
REPORT_DIR = Path("reports")
WEIGHT_LOG = Path("weight_audit_log.jsonl")
MAX_SIGNAL_SIZE = 10240  # 10KB 상한 (NAEL 권고)
MIN_COMPOSITE = 0.60

SYNONYM_GROUPS = [
    {"self-evolving", "self-improvement", "self-referential", "recursive-improvement",
     "recursive-agent", "runtime-self-modification", "meta-learning"},
    {"multi-agent", "agent-network", "agent-framework", "agentic-tools"},
    {"A2A", "agent-protocol", "interoperability", "MCP", "ACP", "ANP",
     "agent-security", "trust-chain"},
    {"autonomous-agent", "autonomous-optimization", "autonomous"},
    {"benchmark", "evaluation", "real-world-validation"},
    {"feedback-loop", "iterative-feedback", "self-feedback"},
]

INJECTION_PATTERNS = [
    r'(?i)ignore\s+(previous|above|all)\s+instructions',
    r'(?i)you\s+are\s+now\s+',
    r'(?i)system\s*:\s*',
    r'<script',
    r'(?i)drop\s+table',
]


# === Security Layer ===

def validate_input(text: str) -> tuple[bool, str]:
    """InputValidator: 크기 상한 + 인젝션 탐지"""
    if len(text.encode("utf-8")) > MAX_SIGNAL_SIZE:
        return False, f"Size exceeds {MAX_SIGNAL_SIZE}B limit"
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return False, f"Injection pattern detected: {pattern}"
    return True, "OK"


def log_weight_change(action: str, before: dict, after: dict):
    """WeightAuditLog: 불변 로그"""
    WEIGHT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "before": before,
        "after": after,
    }
    with open(WEIGHT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# === Evidence Engine ===

def load_evidences() -> list[dict]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidences = []
    for f in sorted(EVIDENCE_DIR.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            evidences.append(json.load(fp))
    return evidences


def score_evidence(e: dict) -> dict:
    """4차원 점수화 + 정합성 검증 (Vera 권고)"""
    computed = round(
        e.get("novelty_score", 0) * 0.25 +
        e.get("credibility_score", 0) * 0.30 +
        e.get("buildability_score", 0) * 0.25 +
        e.get("market_pull_score", 0) * 0.20, 3
    )
    # 파일 기입값과 재계산값 정합성 검증
    file_score = e.get("composite_score", 0)
    if file_score and abs(file_score - computed) > 0.01:
        print(f"  [WARN] {e.get('id','?')}: file={file_score} vs computed={computed} — 재계산값 적용")
    e["composite_score"] = computed
    return e


def deduplicate(evidences: list[dict]) -> list[dict]:
    """URL 기반 중복 제거"""
    seen_urls = set()
    deduped = []
    for e in evidences:
        url = e.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(e)
    return deduped


# === Intelligence Engine ===

def build_synonym_map() -> dict:
    syn_map = {}
    for i, group in enumerate(SYNONYM_GROUPS):
        for tag in group:
            syn_map[tag] = i
    return syn_map


def semantic_similarity(a: dict, b: dict) -> float:
    def tokenize(text):
        return Counter(re.findall(r'[a-zA-Z가-힣]+', text.lower()))
    ta, tb = tokenize(a.get("summary", "")), tokenize(b.get("summary", ""))
    if not ta or not tb:
        return 0.0
    all_t = set(ta) | set(tb)
    dot = sum(ta.get(t, 0) * tb.get(t, 0) for t in all_t)
    ma = math.sqrt(sum(v * v for v in ta.values()))
    mb = math.sqrt(sum(v * v for v in tb.values()))
    return dot / (ma * mb) if ma and mb else 0.0


def detect_patterns(evidences: list[dict]) -> list[dict]:
    clusters = defaultdict(set)
    for e in evidences:
        for tag in e.get("tags", []):
            clusters[tag].add(e["id"])
    patterns = []
    for tag, ids in clusters.items():
        if len(ids) >= 3:
            related = [e for e in evidences if e["id"] in ids]
            avg = sum(e.get("composite_score", 0) for e in related) / len(related)
            patterns.append({
                "type": "Pattern", "tag": tag,
                "evidence_count": len(ids), "evidence_ids": sorted(ids),
                "avg_composite": round(avg, 3),
                "strength": "strong" if len(ids) >= 4 else "moderate",
            })
    patterns.sort(key=lambda x: x["evidence_count"], reverse=True)
    return patterns


def cross_domain_fuse(evidences: list[dict]) -> list[dict]:
    syn_map = build_synonym_map()
    fusions = []

    for a, b in combinations(evidences, 2):
        shared = set(a.get("tags", [])) & set(b.get("tags", []))
        cross = a["source"] != b["source"]

        # 태그 매칭
        tag_match = (cross and len(shared) >= 2) or (not cross and len(shared) >= 2
            and (set(a.get("tags", [])) - shared) and (set(b.get("tags", [])) - shared))

        # 의미 유사도
        sim = semantic_similarity(a, b)
        syn_overlap = len({syn_map.get(t, t) for t in a.get("tags", [])}
                        & {syn_map.get(t, t) for t in b.get("tags", [])})

        if tag_match or syn_overlap >= 2 or sim >= 0.35:
            avg = (a.get("composite_score", 0) + b.get("composite_score", 0)) / 2

            # 융합 인사이트 유형 판정
            insight_type = classify_fusion(a, b)

            fusions.append({
                "type": "FusedInsight",
                "insight_type": insight_type,
                "evidence_pair": [a["id"], b["id"]],
                "shared_tags": sorted(shared) if shared else ["(semantic)"],
                "avg_composite": round(avg, 3),
                "platforms": sorted({a["source"], b["source"]}),
            })

    fusions.sort(key=lambda x: -x["avg_composite"])
    return fusions


def classify_fusion(a: dict, b: dict) -> str:
    """5가지 크로스 도메인 인사이트 유형 분류"""
    sources = {a["source"], b["source"]}
    a_tags = set(a.get("tags", []))
    b_tags = set(b.get("tags", []))

    # White Space: 한쪽에 "benchmark"/"evaluation" 태그 + 다른 쪽에 없음
    eval_tags = {"benchmark", "evaluation", "real-world-validation"}
    impl_tags = {"open-source", "agent-framework", "production"}
    if (a_tags & eval_tags and not b_tags & impl_tags) or (b_tags & eval_tags and not a_tags & impl_tags):
        return "White Space"

    if "arxiv" in sources and "github" in sources:
        return "Paper-Implementation Gap"
    if "hn" in sources or "reddit" in sources:
        return "Hype-Reality Divergence"
    if a["source"] == b["source"]:
        return "Silent Convergence"
    return "Cross-Domain Connection"


# === Report Generator ===

def generate_report(evidences, patterns, fusions):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_evidence": len(evidences),
            "patterns": len(patterns),
            "fusions": len(fusions),
            "top_pattern": patterns[0]["tag"] if patterns else None,
            "top_fusion": fusions[0] if fusions else None,
        },
        "patterns": patterns,
        "fusions": fusions,
        "insight_types": Counter(f.get("insight_type", "unknown") for f in fusions),
    }

    out = REPORT_DIR / f"report-{today}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"  Trend Intelligence Report — {today}")
    print(f"{'='*50}")
    print(f"  Evidence: {len(evidences)}")
    print(f"  Patterns: {len(patterns)}")
    print(f"  Fusions:  {len(fusions)}")
    print(f"\n  Top Patterns:")
    for p in patterns[:5]:
        print(f"    [{p['strength']:8s}] '{p['tag']}' x{p['evidence_count']} (avg={p['avg_composite']})")
    print(f"\n  Top Fusions:")
    for fu in fusions[:5]:
        plat = "x".join(fu["platforms"])
        print(f"    [{fu.get('insight_type','?'):25s}] {plat}: {fu['shared_tags']} (avg={fu['avg_composite']})")
    print(f"\n  Saved: {out}")
    return report


# === Main CLI ===

def main():
    if len(sys.argv) < 2:
        print("Usage: trend_intel.py [collect|analyze|fuse|report|full]")
        return

    cmd = sys.argv[1]

    if cmd == "analyze":
        evidences = load_evidences()
        evidences = [score_evidence(e) for e in evidences]
        evidences = deduplicate(evidences)
        filtered = [e for e in evidences if e.get("composite_score", 0) >= MIN_COMPOSITE]
        print(f"Loaded {len(evidences)}, filtered {len(filtered)} (>= {MIN_COMPOSITE})")
        for e in sorted(filtered, key=lambda x: -x["composite_score"])[:10]:
            print(f"  [{e['composite_score']:.2f}] {e['source']:12s} {e['title'][:60]}")

    elif cmd == "fuse":
        evidences = [e for e in load_evidences() if e.get("composite_score", 0) >= MIN_COMPOSITE]
        patterns = detect_patterns(evidences)
        fusions = cross_domain_fuse(evidences)
        print(f"Patterns: {len(patterns)}, Fusions: {len(fusions)}")
        for fu in fusions:
            print(f"  [{fu.get('insight_type','?')}] {fu['platforms']}: {fu['shared_tags']}")

    elif cmd == "report":
        evidences = [e for e in load_evidences() if e.get("composite_score", 0) >= MIN_COMPOSITE]
        patterns = detect_patterns(evidences)
        fusions = cross_domain_fuse(evidences)
        generate_report(evidences, patterns, fusions)

    elif cmd == "full":
        # 전 파이프라인
        evidences = load_evidences()
        print(f"[1/4] Loaded {len(evidences)} evidences")

        evidences = [score_evidence(e) for e in evidences]
        evidences = deduplicate(evidences)
        # NAEL 게이트: nael_status가 "blocked"이면 제외 (Vera/NAEL 권고)
        filtered = [e for e in evidences
                    if e.get("composite_score", 0) >= MIN_COMPOSITE
                    and e.get("nael_status") != "blocked"]
        print(f"[2/4] Scored & filtered: {len(filtered)}/{len(evidences)}")

        patterns = detect_patterns(filtered)
        fusions = cross_domain_fuse(filtered)
        print(f"[3/4] Patterns: {len(patterns)}, Fusions: {len(fusions)}")

        generate_report(filtered, patterns, fusions)
        print(f"[4/4] Report generated")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
