#!/usr/bin/env python3
"""
Source Verification — 출처 검증 도구
=====================================
텍스트에서 검증 가능한 주장을 추출하고, 신뢰도를 평가.
WebSearch 기반 교차 검증은 AI 에이전트가 실행 시 수행.

사용법:
  python source_verify.py extract --file knowledge/ai/agent-self-improvement-2026.md
  python source_verify.py verify --id claim_001
  python source_verify.py report --file knowledge/ai/agent-self-improvement-2026.md
  python source_verify.py status
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Literal

VERIFY_DIR = Path("D:/SeAAI/NAEL/verification")
CLAIMS_DIR = VERIFY_DIR / "claims"
REPORTS_DIR = VERIFY_DIR / "reports"


@dataclass
class Claim:
    """검증 가능한 주장"""
    id: str                             # claim_001, ...
    text: str                           # 주장 원문
    source_file: str                    # 출처 파일
    claim_type: str                     # factual | statistical | attribution | temporal
    confidence_before: float            # 사전 신뢰도 (추출 시 판단)
    extracted_at: str = ""
    status: str = "pending"             # pending | verified | unverified | contested

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


@dataclass
class VerificationResult:
    """검증 결과"""
    claim_id: str
    status: str                         # verified | unverified | contested
    confidence_after: float             # 검증 후 신뢰도
    sources: list                       # 근거 URL 또는 참조
    reasoning: str                      # 검증 근거 요약
    verified_at: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def ensure_dirs():
    VERIFY_DIR.mkdir(parents=True, exist_ok=True)
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def next_claim_id() -> str:
    """다음 주장 ID"""
    ensure_dirs()
    existing = list(CLAIMS_DIR.glob("claim_*.json"))
    if not existing:
        return "claim_001"
    nums = []
    for f in existing:
        try:
            nums.append(int(f.stem.split("_")[1]))
        except (IndexError, ValueError):
            pass
    return f"claim_{max(nums) + 1:03d}" if nums else "claim_001"


def extract_claims_from_text(text: str, source_file: str) -> list[Claim]:
    """텍스트에서 검증 가능한 주장을 추출 (휴리스틱 기반)

    AI 에이전트가 호출할 때는 이 함수 대신 AI_extract_claims를 사용하여
    더 정밀하게 추출할 수 있음.
    """
    ensure_dirs()
    claims = []

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 통계적 주장 탐지
        has_numbers = bool(re.search(r"\d+[%.]?\d*", line))
        # 귀속 주장 탐지 (X said, according to, based on)
        has_attribution = bool(re.search(
            r"(according to|based on|said|stated|reported|published|announced|found that)",
            line, re.IGNORECASE
        ))
        # 시간적 주장 탐지
        has_temporal = bool(re.search(r"(20\d{2}|last year|recently|since|before|after)", line, re.IGNORECASE))
        # 사실적 주장 탐지 (is, are, was, were + 서술)
        has_factual = bool(re.search(r"\b(is|are|was|were|has been|have been)\b.{10,}", line, re.IGNORECASE))

        # 주장 유형 결정
        if has_numbers and (has_attribution or has_temporal):
            claim_type = "statistical"
            confidence = 0.5
        elif has_attribution:
            claim_type = "attribution"
            confidence = 0.6
        elif has_temporal and has_numbers:
            claim_type = "temporal"
            confidence = 0.5
        elif has_factual and len(line) > 30:
            claim_type = "factual"
            confidence = 0.4
        else:
            continue

        # 너무 짧거나 리스트 마커만 있는 줄 제외
        clean = re.sub(r"^[-*]\s*", "", line)
        if len(clean) < 20:
            continue

        claim = Claim(
            id=next_claim_id(),
            text=clean[:200],
            source_file=source_file,
            claim_type=claim_type,
            confidence_before=confidence,
            extracted_at=datetime.now().isoformat(),
        )

        claim_file = CLAIMS_DIR / f"{claim.id}.json"
        with open(claim_file, "w", encoding="utf-8") as f:
            f.write(claim.to_json())
        claims.append(claim)

    return claims


def load_claim(claim_id: str) -> Optional[Claim]:
    """주장 로드"""
    claim_file = CLAIMS_DIR / f"{claim_id}.json"
    if not claim_file.exists():
        return None
    with open(claim_file, "r", encoding="utf-8") as f:
        return Claim(**json.load(f))


def save_claim(claim: Claim):
    """주장 업데이트"""
    claim_file = CLAIMS_DIR / f"{claim.id}.json"
    with open(claim_file, "w", encoding="utf-8") as f:
        f.write(claim.to_json())


def record_verification(
    claim_id: str,
    status: str,
    confidence_after: float,
    sources: list,
    reasoning: str,
) -> VerificationResult:
    """검증 결과 기록"""
    ensure_dirs()
    result = VerificationResult(
        claim_id=claim_id,
        status=status,
        confidence_after=round(min(max(confidence_after, 0.0), 1.0), 3),
        sources=sources,
        reasoning=reasoning,
        verified_at=datetime.now().isoformat(),
    )

    # 결과 저장
    result_file = VERIFY_DIR / f"result_{claim_id}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(result.to_json())

    # 주장 상태 업데이트
    claim = load_claim(claim_id)
    if claim:
        claim.status = status
        save_claim(claim)

    return result


def generate_report(source_file: str) -> str:
    """파일별 검증 보고서 생성"""
    ensure_dirs()
    claims = []
    for cf in sorted(CLAIMS_DIR.glob("claim_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("source_file") == source_file:
            claims.append(data)

    if not claims:
        return f"# Verification Report\n\nNo claims extracted from {source_file}."

    lines = [
        f"# Verification Report: {source_file}",
        f"**Claims extracted**: {len(claims)}",
        f"**Generated**: {datetime.now().isoformat()[:10]}",
        "",
    ]

    # 상태별 분류
    by_status = {"pending": [], "verified": [], "unverified": [], "contested": []}
    for c in claims:
        by_status.get(c["status"], by_status["pending"]).append(c)

    lines.append("## Summary")
    for status, items in by_status.items():
        if items:
            lines.append(f"- **{status}**: {len(items)}")
    lines.append("")

    # 신뢰도 점수
    confidences = [c["confidence_before"] for c in claims]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    lines.append(f"## Document Confidence Score: {avg_conf:.2f}")
    lines.append("")

    # 주장별 상세
    lines.append("## Claims Detail")
    lines.append("")
    for c in claims:
        icon = {"pending": "[?]", "verified": "[V]", "unverified": "[X]", "contested": "[!]"}.get(c["status"], "[?]")
        lines.append(f"### {icon} {c['id']} ({c['claim_type']})")
        lines.append(f"> {c['text']}")
        lines.append(f"- Status: {c['status']}")
        lines.append(f"- Confidence: {c['confidence_before']}")

        # 검증 결과 확인
        result_file = VERIFY_DIR / f"result_{c['id']}.json"
        if result_file.exists():
            with open(result_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            lines.append(f"- Verified confidence: {result['confidence_after']}")
            lines.append(f"- Reasoning: {result['reasoning']}")
            if result["sources"]:
                lines.append(f"- Sources: {', '.join(str(s) for s in result['sources'])}")
        lines.append("")

    # 보고서 저장
    report_name = source_file.replace("/", "_").replace("\\", "_").replace(".md", "")
    report_file = REPORTS_DIR / f"report_{report_name}.md"
    report_text = "\n".join(lines)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text


def show_status() -> str:
    """전체 검증 상태 요약"""
    ensure_dirs()
    claims = []
    for cf in sorted(CLAIMS_DIR.glob("claim_*.json")):
        with open(cf, "r", encoding="utf-8") as f:
            claims.append(json.load(f))

    if not claims:
        return "# Verification Status\n\nNo claims registered."

    by_status = {"pending": 0, "verified": 0, "unverified": 0, "contested": 0}
    by_file = {}
    for c in claims:
        by_status[c.get("status", "pending")] = by_status.get(c.get("status", "pending"), 0) + 1
        sf = c.get("source_file", "unknown")
        if sf not in by_file:
            by_file[sf] = {"total": 0, "verified": 0}
        by_file[sf]["total"] += 1
        if c.get("status") == "verified":
            by_file[sf]["verified"] += 1

    total = len(claims)
    lines = [
        "# Verification Status",
        f"**Total claims**: {total}",
        "",
        "## By Status",
    ]
    for status, count in by_status.items():
        pct = round(count / total * 100) if total > 0 else 0
        lines.append(f"- {status}: {count} ({pct}%)")

    lines.append("")
    lines.append("## By Source File")
    for sf, info in sorted(by_file.items()):
        pct = round(info["verified"] / info["total"] * 100) if info["total"] > 0 else 0
        lines.append(f"- {sf}: {info['verified']}/{info['total']} verified ({pct}%)")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Source Verification Tool")
    sub = parser.add_subparsers(dest="command")

    # extract
    ext_p = sub.add_parser("extract", help="Extract verifiable claims")
    ext_p.add_argument("--file", required=True, help="Source file path")

    # verify (record verification result)
    ver_p = sub.add_parser("verify", help="Record verification result")
    ver_p.add_argument("--id", required=True, help="Claim ID")
    ver_p.add_argument("--status", required=True, choices=["verified", "unverified", "contested"])
    ver_p.add_argument("--confidence", type=float, required=True, help="Post-verification confidence")
    ver_p.add_argument("--reasoning", required=True, help="Verification reasoning")
    ver_p.add_argument("--sources", nargs="*", default=[], help="Source URLs")

    # report
    rep_p = sub.add_parser("report", help="Generate verification report")
    rep_p.add_argument("--file", required=True, help="Source file path")

    # status
    sub.add_parser("status", help="Show overall verification status")

    args = parser.parse_args()

    if args.command == "extract":
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = Path("D:/SeAAI/NAEL") / file_path
        if not file_path.exists():
            print(f"File not found: {file_path}")
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
        rel_path = str(file_path.relative_to(Path("D:/SeAAI/NAEL")))
        claims = extract_claims_from_text(text, rel_path)
        print(f"Extracted {len(claims)} verifiable claims from {rel_path}")
        for c in claims:
            print(f"  {c.id} [{c.claim_type}] {c.text[:80]}...")
    elif args.command == "verify":
        result = record_verification(
            args.id, args.status, args.confidence, args.sources, args.reasoning,
        )
        print(f"Verified: {result.claim_id} -> {result.status} (confidence={result.confidence_after})")
    elif args.command == "report":
        print(generate_report(args.file))
    elif args.command == "status":
        print(show_status())
    else:
        parser.print_help()
