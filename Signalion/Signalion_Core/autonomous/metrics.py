#!/usr/bin/env python3
"""
Signalion 수집 품질 메트릭스
플랫폼별 수율, 필터링 비율, 씨앗 전환율, NAEL 통과율 등 품질 지표 자동 집계.

사용법:
    python metrics.py                # 전체 메트릭스 출력
    python metrics.py --save         # JSON으로 저장
"""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "signal-store/evidence")
PATTERNS_FILE = Path(__file__).resolve().parents[2] / "signal-store/patterns.json")
METRICS_DIR = Path(__file__).resolve().parents[2] / "signal-store/metrics")


def load_evidences():
    evidences = []
    for f in sorted(EVIDENCE_DIR.glob("*-evidence-*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            evidences.append(json.load(fp))
    return evidences


def load_seeds():
    seeds = list(EVIDENCE_DIR.glob("SEED-*.md"))
    results = []
    for f in seeds:
        content = f.read_text(encoding="utf-8")
        status = "APPROVED" if "APPROVED" in content else "FLAGGED" if "FLAGGED" in content else "pending"
        results.append({"file": f.name, "status": status})
    return results


def compute_metrics():
    evidences = load_evidences()
    seeds = load_seeds()

    if not evidences:
        return {"error": "No evidence files found"}

    # 플랫폼별 수율
    by_platform = Counter(e.get("source", "unknown") for e in evidences)

    # 점수 분포
    scores = [e.get("composite_score", 0) for e in evidences]
    high_quality = [e for e in evidences if e.get("composite_score", 0) >= 0.70]

    # 씨앗 전환율
    seed_count = len(seeds)
    approved_seeds = [s for s in seeds if s["status"] == "APPROVED"]

    # NAEL 상태 분포
    nael_dist = Counter(e.get("nael_status", "unknown") for e in evidences)

    metrics = {
        "generated_at": datetime.now().isoformat(),
        "total_evidence": len(evidences),
        "by_platform": dict(by_platform),
        "score_distribution": {
            "min": round(min(scores), 3) if scores else 0,
            "max": round(max(scores), 3) if scores else 0,
            "avg": round(sum(scores) / len(scores), 3) if scores else 0,
            "high_quality_count": len(high_quality),
            "high_quality_rate": round(len(high_quality) / len(evidences), 3) if evidences else 0,
        },
        "seed_metrics": {
            "total_seeds": seed_count,
            "approved": len(approved_seeds),
            "conversion_rate": round(seed_count / len(evidences), 3) if evidences else 0,
            "approval_rate": round(len(approved_seeds) / seed_count, 3) if seed_count else 0,
        },
        "nael_status": dict(nael_dist),
        "platform_quality": {},
    }

    # 플랫폼별 평균 점수
    for platform in by_platform:
        platform_evs = [e for e in evidences if e.get("source") == platform]
        platform_scores = [e.get("composite_score", 0) for e in platform_evs]
        metrics["platform_quality"][platform] = {
            "count": len(platform_evs),
            "avg_score": round(sum(platform_scores) / len(platform_scores), 3) if platform_scores else 0,
            "high_quality": sum(1 for s in platform_scores if s >= 0.70),
        }

    return metrics


def print_report(metrics):
    print(f"\n{'='*50}")
    print(f"  Signalion 수집 품질 메트릭스")
    print(f"  {metrics['generated_at']}")
    print(f"{'='*50}")

    print(f"\n  총 Evidence: {metrics['total_evidence']}")

    sd = metrics["score_distribution"]
    print(f"  점수: min={sd['min']} / avg={sd['avg']} / max={sd['max']}")
    print(f"  고품질(>=0.70): {sd['high_quality_count']}건 ({sd['high_quality_rate']*100:.1f}%)")

    print(f"\n  플랫폼별:")
    for p, q in metrics["platform_quality"].items():
        print(f"    {p:15s}: {q['count']:3d}건, avg={q['avg_score']:.3f}, HQ={q['high_quality']}")

    sm = metrics["seed_metrics"]
    print(f"\n  씨앗: {sm['total_seeds']}건 생성, {sm['approved']}건 승인")
    print(f"  전환율(Evidence→Seed): {sm['conversion_rate']*100:.1f}%")
    print(f"  승인율(Seed→Approved): {sm['approval_rate']*100:.1f}%")

    print(f"\n  NAEL 상태: {metrics['nael_status']}")


def main():
    metrics = compute_metrics()

    if "error" in metrics:
        print(metrics["error"])
        return

    print_report(metrics)

    if "--save" in sys.argv:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y%m%d")
        out = METRICS_DIR / f"metrics-{today}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"\n  Saved: {out}")


if __name__ == "__main__":
    main()
