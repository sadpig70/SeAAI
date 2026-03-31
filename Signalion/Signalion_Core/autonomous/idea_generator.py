#!/usr/bin/env python3
"""
Signalion 아이디어 생성 파이프라인
Intelligence Layer 융합 결과에 6가지 조합 패턴을 적용하여 제품 아이디어를 자동 생성.

사용법:
    python idea_generator.py                # 기존 Evidence 기반 아이디어 생성
    python idea_generator.py --save         # 결과를 파일로 저장
"""
import json
import sys
from datetime import datetime
from itertools import combinations
from pathlib import Path

EVIDENCE_DIR = Path("D:/SeAAI/Signalion/signal-store/evidence")
INTEL_FILE = Path("D:/SeAAI/Signalion/signal-store/intelligence-output.json")
IDEAS_DIR = Path("D:/SeAAI/Signalion/_workspace/products/ideas")

# === 6가지 창발적 조합 패턴 ===

COMBINATION_PATTERNS = {
    "cross_domain": {
        "name": "Cross-Domain Fusion",
        "description": "서로 다른 분야의 신호를 교차하여 새 아이디어 생성",
        "template": "{domain_a}의 {concept_a}을 {domain_b}에 적용하면?",
    },
    "inversion": {
        "name": "Inversion",
        "description": "성공 사례를 뒤집어 새로운 관점 발견",
        "template": "{concept}의 반대를 하면 어떤 가치가 생기는가?",
    },
    "scale_shift": {
        "name": "Scale Shift",
        "description": "규모를 바꾸어 새로운 시장 발견",
        "template": "{concept}을 {scale_from}에서 {scale_to}로 옮기면?",
    },
    "substrate_swap": {
        "name": "Substrate Swap",
        "description": "기반 기술/플랫폼을 교체하여 새 제품 발견",
        "template": "{concept}의 기반을 {from_substrate}에서 {to_substrate}로 바꾸면?",
    },
    "gap_fill": {
        "name": "Gap Fill",
        "description": "많이 논의되지만 구현이 없는 것을 찾아 채움",
        "template": "{topic}에 대한 논의는 많지만 실제 구현/제품이 없다. 만들면?",
    },
    "failure_mining": {
        "name": "Failure Mining",
        "description": "실패 패턴에서 기회를 발견",
        "template": "{concept}이 실패한 이유는 {reason}. 이것을 해결하면?",
    },
}


def load_intel():
    """Intelligence Layer 출력 로드"""
    if not INTEL_FILE.exists():
        return None
    with open(INTEL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_evidences():
    evidences = []
    for f in sorted(EVIDENCE_DIR.glob("*-evidence-*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            evidences.append(json.load(fp))
    return evidences


def apply_cross_domain(fusions, evidences):
    """크로스 도메인 패턴: 융합된 쌍에서 아이디어 도출"""
    ideas = []
    for fusion in fusions:
        if len(fusion.get("platforms", [])) < 2:
            continue
        pair = fusion.get("evidence_pair", [])
        ev_a = next((e for e in evidences if e["id"] == pair[0]), None) if len(pair) > 0 else None
        ev_b = next((e for e in evidences if e["id"] == pair[1]), None) if len(pair) > 1 else None
        if ev_a and ev_b:
            ideas.append({
                "pattern": "cross_domain",
                "source_pair": pair,
                "idea": f"{ev_a['source']}의 '{ev_a['title'][:40]}'과 {ev_b['source']}의 '{ev_b['title'][:40]}'을 결합",
                "shared_tags": fusion.get("shared_tags", []),
                "score": fusion.get("avg_composite", 0),
            })
    return ideas


def apply_gap_fill(patterns, evidences):
    """갭 필 패턴: 트렌드는 있지만 구현이 부족한 영역"""
    ideas = []
    for pattern in patterns:
        tag = pattern["tag"]
        count = pattern["evidence_count"]
        # 논문/토론은 많지만 GitHub 구현이 적은 태그
        github_count = sum(1 for eid in pattern["evidence_ids"]
                         if any(e["id"] == eid and e["source"] == "github" for e in evidences))
        non_github = count - github_count
        if non_github >= 2 and github_count <= 1:
            ideas.append({
                "pattern": "gap_fill",
                "tag": tag,
                "idea": f"'{tag}'에 대한 논의가 {non_github}건이지만 GitHub 구현은 {github_count}건. 오픈소스 구현 기회.",
                "score": pattern["avg_composite"],
            })
    return ideas


def apply_scale_shift(evidences):
    """스케일 시프트: 엔터프라이즈 → 개인, 또는 반대"""
    ideas = []
    enterprise_keywords = {"enterprise", "production", "platform", "saas"}
    personal_keywords = {"cli", "local", "desktop", "personal"}

    for e in evidences:
        tags = set(e.get("tags", []))
        title_lower = e.get("title", "").lower()
        summary_lower = e.get("summary", "").lower()

        is_enterprise = any(kw in title_lower or kw in summary_lower for kw in enterprise_keywords)
        is_personal = any(kw in title_lower or kw in summary_lower for kw in personal_keywords)

        if is_enterprise and not is_personal:
            ideas.append({
                "pattern": "scale_shift",
                "source": e["id"],
                "idea": f"'{e['title'][:50]}'을 개인/로컬 도구로 축소하면?",
                "direction": "enterprise → personal",
                "score": e.get("composite_score", 0) * 0.9,
            })
        elif is_personal and not is_enterprise:
            ideas.append({
                "pattern": "scale_shift",
                "source": e["id"],
                "idea": f"'{e['title'][:50]}'을 팀/SaaS로 확장하면?",
                "direction": "personal → enterprise",
                "score": e.get("composite_score", 0) * 0.9,
            })
    return ideas


def apply_inversion(evidences):
    """인버전: 핵심 개념을 뒤집기"""
    ideas = []
    for e in evidences:
        if e.get("composite_score", 0) >= 0.70:
            ideas.append({
                "pattern": "inversion",
                "source": e["id"],
                "idea": f"'{e['title'][:50]}'의 반대 — 이것을 하지 않았을 때의 문제를 해결하는 도구?",
                "score": e.get("composite_score", 0) * 0.8,
            })
    return ideas


def generate_ideas():
    """전체 아이디어 생성"""
    intel = load_intel()
    evidences = load_evidences()

    if not intel or not evidences:
        print("No intelligence output or evidence found.")
        return []

    all_ideas = []

    # 각 패턴 적용
    all_ideas.extend(apply_cross_domain(intel.get("fusions", []), evidences))
    all_ideas.extend(apply_gap_fill(intel.get("patterns", []), evidences))
    all_ideas.extend(apply_scale_shift(evidences))
    all_ideas.extend(apply_inversion(evidences))

    # 점수순 정렬
    all_ideas.sort(key=lambda x: -x.get("score", 0))

    return all_ideas


def print_report(ideas):
    print(f"\n{'='*55}")
    print(f"  Signalion Idea Generator — {len(ideas)} ideas")
    print(f"{'='*55}")

    by_pattern = {}
    for idea in ideas:
        p = idea["pattern"]
        by_pattern.setdefault(p, []).append(idea)

    for pattern, items in by_pattern.items():
        name = COMBINATION_PATTERNS.get(pattern, {}).get("name", pattern)
        print(f"\n  [{name}] — {len(items)} ideas")
        for i, item in enumerate(items[:3], 1):
            print(f"    {i}. {item['idea'][:80]}")
            print(f"       score: {item.get('score', 0):.3f}")


def main():
    ideas = generate_ideas()
    if not ideas:
        return

    print_report(ideas)

    if "--save" in sys.argv:
        IDEAS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y%m%d")
        out = IDEAS_DIR / f"ideas-{today}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"generated_at": datetime.now().isoformat(), "count": len(ideas), "ideas": ideas},
                      f, ensure_ascii=False, indent=2)
        print(f"\n  Saved: {out}")


if __name__ == "__main__":
    main()
