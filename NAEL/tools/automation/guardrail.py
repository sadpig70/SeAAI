#!/usr/bin/env python3
"""
Guardrail — 안전한 자기개선을 위한 보호 레이어 + 표준 평가 인터페이스
=====================================================================
모든 자기개선 도구(self_improver, challenger, orchestrator)가 공유하는:
1. 표준 평가 결과 포맷 (EvalResult)
2. 변경 전후 diff 자동 요약
3. Rollback 포인트 기록/복원
4. 안전 테스트 스위트 실행
5. Human-in-the-loop 모드 (proposal-only / auto-with-threshold / manual-approve)

참조: Gödel Agent (ACL 2025) 안전성 검증 루프, NeurIPS 2025 self-improving agent guardrails

사용법:
  python guardrail.py checkpoint --file path/to/file.py          # 롤백 포인트 생성
  python guardrail.py rollback --file path/to/file.py            # 마지막 체크포인트로 복원
  python guardrail.py validate --file path/to/file.py            # 안전 테스트 실행
  python guardrail.py diff --file path/to/file.py                # 체크포인트 대비 diff 요약
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional


CHECKPOINT_DIR = Path("D:/SeAAI/NAEL/.guardrail/checkpoints")
EVAL_LOG = Path("D:/SeAAI/NAEL/.guardrail/evaluations.jsonl")


# ========== 1. 표준 평가 인터페이스 ==========

@dataclass
class EvalResult:
    """
    모든 평가 도구의 공통 출력 포맷.
    self_improver, challenger, orchestrator, verify 등이 이 형식으로 결과를 반환.
    """
    tool: str               # 평가를 수행한 도구
    target: str             # 평가 대상 (파일 경로 또는 식별자)
    timestamp: str = ""
    success: bool = True    # pass/fail
    reward_score: float = 0.0  # 0.0-1.0 통합 점수
    error_class: str = "none"  # none, logic_error, integration_error, timeout, design_flaw, security
    cost_tokens: int = 0    # 소비 토큰 추정
    dimensions: dict = field(default_factory=dict)  # 개별 차원 점수 {name: score}
    issues: list[str] = field(default_factory=list)  # 발견된 이슈
    recommendations: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def is_acceptable(self, threshold: float = 0.7) -> bool:
        """threshold 이상이면 acceptable"""
        return self.success and self.reward_score >= threshold

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    def to_summary(self) -> str:
        """한 줄 요약"""
        status = "PASS" if self.success else "FAIL"
        return f"[{status}] {self.target} | score={self.reward_score:.2f} | issues={len(self.issues)} | by={self.tool}"

    def log(self):
        """평가 결과를 영구 로그에 기록"""
        EVAL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(EVAL_LOG, "a", encoding="utf-8") as f:
            f.write(self.to_json() + "\n")


def load_eval_history(target: str = "") -> list[dict]:
    """평가 이력 로드"""
    if not EVAL_LOG.exists():
        return []
    results = []
    with open(EVAL_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entry = json.loads(line)
                if not target or entry.get("target") == target:
                    results.append(entry)
    return results


def eval_trend(target: str) -> Optional[dict]:
    """특정 대상의 평가 점수 추이"""
    history = load_eval_history(target)
    if len(history) < 2:
        return None
    scores = [h["reward_score"] for h in history]
    return {
        "target": target,
        "evaluations": len(scores),
        "first_score": scores[0],
        "latest_score": scores[-1],
        "trend": round(scores[-1] - scores[0], 3),
        "improving": scores[-1] > scores[0],
    }


# ========== 2. Checkpoint / Rollback ==========

def create_checkpoint(file_path: str) -> str:
    """파일의 롤백 포인트 생성"""
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"Cannot checkpoint: {file_path} does not exist")

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    # 파일별 체크포인트 디렉토리
    safe_name = src.name.replace(".", "_")
    cp_dir = CHECKPOINT_DIR / safe_name
    cp_dir.mkdir(exist_ok=True)

    # 타임스탬프 기반 백업
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cp_path = cp_dir / f"{ts}_{src.name}"
    shutil.copy2(str(src), str(cp_path))

    # 메타데이터
    meta = {
        "original_path": str(src),
        "checkpoint_path": str(cp_path),
        "timestamp": datetime.now().isoformat(),
        "size_bytes": src.stat().st_size,
    }
    meta_path = cp_dir / f"{ts}_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return str(cp_path)


def rollback(file_path: str) -> str:
    """마지막 체크포인트로 복원"""
    src = Path(file_path)
    safe_name = src.name.replace(".", "_")
    cp_dir = CHECKPOINT_DIR / safe_name

    if not cp_dir.exists():
        raise FileNotFoundError(f"No checkpoints found for {file_path}")

    # 가장 최근 메타 파일 찾기
    meta_files = sorted(cp_dir.glob("*_meta.json"), reverse=True)
    if not meta_files:
        raise FileNotFoundError(f"No checkpoint metadata for {file_path}")

    meta = json.loads(meta_files[0].read_text(encoding="utf-8"))
    cp_path = Path(meta["checkpoint_path"])

    if not cp_path.exists():
        raise FileNotFoundError(f"Checkpoint file missing: {cp_path}")

    shutil.copy2(str(cp_path), str(src))
    return f"Rolled back {file_path} to {meta['timestamp']}"


def list_checkpoints(file_path: str) -> list[dict]:
    """파일의 체크포인트 목록"""
    src = Path(file_path)
    safe_name = src.name.replace(".", "_")
    cp_dir = CHECKPOINT_DIR / safe_name

    if not cp_dir.exists():
        return []

    checkpoints = []
    for meta_file in sorted(cp_dir.glob("*_meta.json")):
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        checkpoints.append(meta)
    return checkpoints


# ========== 3. Diff Summary ==========

def diff_from_checkpoint(file_path: str) -> str:
    """체크포인트 대비 현재 파일의 변경 요약"""
    src = Path(file_path)
    safe_name = src.name.replace(".", "_")
    cp_dir = CHECKPOINT_DIR / safe_name

    if not cp_dir.exists():
        return "No checkpoint to compare against."

    meta_files = sorted(cp_dir.glob("*_meta.json"), reverse=True)
    if not meta_files:
        return "No checkpoint metadata found."

    meta = json.loads(meta_files[0].read_text(encoding="utf-8"))
    cp_path = Path(meta["checkpoint_path"])

    if not cp_path.exists():
        return "Checkpoint file missing."

    current = src.read_text(encoding="utf-8").splitlines()
    checkpoint = cp_path.read_text(encoding="utf-8").splitlines()

    added = 0
    removed = 0
    current_set = set(current)
    checkpoint_set = set(checkpoint)

    for line in current:
        if line not in checkpoint_set:
            added += 1
    for line in checkpoint:
        if line not in current_set:
            removed += 1

    return (
        f"## Diff Summary: {file_path}\n"
        f"- Checkpoint: {meta['timestamp']}\n"
        f"- Lines added: +{added}\n"
        f"- Lines removed: -{removed}\n"
        f"- Current size: {len(current)} lines\n"
        f"- Checkpoint size: {len(checkpoint)} lines"
    )


# ========== 4. Safety Validation ==========

def validate_python_file(file_path: str) -> EvalResult:
    """Python 파일 기본 안전 검증"""
    src = Path(file_path)
    issues = []
    dimensions = {}

    if not src.exists():
        return EvalResult(
            tool="guardrail",
            target=file_path,
            success=False,
            reward_score=0.0,
            error_class="file_not_found",
            issues=["File does not exist"],
        )

    content = src.read_text(encoding="utf-8")

    # 1. Syntax check
    try:
        compile(content, file_path, "exec")
        dimensions["syntax"] = 1.0
    except SyntaxError as e:
        dimensions["syntax"] = 0.0
        issues.append(f"Syntax error at line {e.lineno}: {e.msg}")

    # 2. Dangerous patterns — check only in code lines (exclude strings/comments)
    dangerous_patterns = [
        ("os.system(", "Prefer subprocess over os.system"),
        ("eval(", "eval() is a security risk"),
        ("exec(", "exec() with user input is dangerous"),
        ("__import__(", "Dynamic import can be risky"),
    ]
    danger_score = 1.0
    for line in content.splitlines():
        stripped = line.strip()
        # Skip comments and string-only lines
        if stripped.startswith("#") or stripped.startswith('"') or stripped.startswith("'"):
            continue
        # Skip lines that are clearly string definitions (tuples, lists of patterns)
        if stripped.startswith("(") and '", "' in stripped:
            continue
        for pattern, reason in dangerous_patterns:
            if pattern in stripped:
                danger_score -= 0.2
                issues.append(f"Dangerous pattern at: {stripped[:60]}... — {reason}")
    dimensions["safety"] = max(0.0, danger_score)

    # 3. Has docstring
    has_docstring = '"""' in content[:500] or "'''" in content[:500]
    dimensions["documentation"] = 1.0 if has_docstring else 0.5
    if not has_docstring:
        issues.append("Missing module docstring")

    # 4. File size sanity
    line_count = len(content.splitlines())
    if line_count > 500:
        dimensions["complexity"] = 0.7
        issues.append(f"File is large ({line_count} lines) — consider splitting")
    else:
        dimensions["complexity"] = 1.0

    # Overall
    reward = sum(dimensions.values()) / len(dimensions) if dimensions else 0
    success = dimensions.get("syntax", 0) == 1.0 and reward >= 0.6

    result = EvalResult(
        tool="guardrail",
        target=file_path,
        success=success,
        reward_score=round(reward, 2),
        error_class="none" if success else "validation_failed",
        dimensions=dimensions,
        issues=issues,
    )
    result.log()
    return result


# ========== 5. Human-in-the-loop Mode ==========

class ApprovalMode:
    """
    자기개선 작업의 승인 모드.
    PGF POLICY와 연동하여 사용.
    """
    PROPOSAL_ONLY = "proposal-only"          # 제안만, 적용하지 않음
    AUTO_WITH_THRESHOLD = "auto-with-threshold"  # threshold 이상이면 자동 적용
    MANUAL_APPROVE = "manual-approve"        # 항상 사용자 승인 대기

    @staticmethod
    def should_auto_apply(mode: str, eval_result: EvalResult, threshold: float = 0.8) -> bool:
        """이 결과를 자동 적용해도 되는가?"""
        if mode == ApprovalMode.PROPOSAL_ONLY:
            return False
        if mode == ApprovalMode.MANUAL_APPROVE:
            return False
        if mode == ApprovalMode.AUTO_WITH_THRESHOLD:
            return eval_result.is_acceptable(threshold)
        return False

    @staticmethod
    def format_proposal(eval_result: EvalResult, changes: str) -> str:
        """사용자에게 제시할 제안 형식"""
        return (
            f"## Self-Improvement Proposal\n"
            f"**Target**: {eval_result.target}\n"
            f"**Score**: {eval_result.reward_score:.2f}\n"
            f"**Issues Found**: {len(eval_result.issues)}\n\n"
            f"### Proposed Changes\n{changes}\n\n"
            f"### Evaluation\n{eval_result.to_summary()}\n\n"
            f"Apply? [auto-applied if score >= threshold / awaiting approval]"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Guardrail — Safe Self-Improvement")
    sub = parser.add_subparsers(dest="command")

    # checkpoint
    cp = sub.add_parser("checkpoint", help="Create rollback point")
    cp.add_argument("--file", required=True)

    # rollback
    rb = sub.add_parser("rollback", help="Restore from checkpoint")
    rb.add_argument("--file", required=True)

    # validate
    val = sub.add_parser("validate", help="Run safety validation")
    val.add_argument("--file", required=True)

    # diff
    df = sub.add_parser("diff", help="Diff from checkpoint")
    df.add_argument("--file", required=True)

    # history
    hist = sub.add_parser("history", help="Evaluation history")
    hist.add_argument("--target", default="")

    # list checkpoints
    lcp = sub.add_parser("list-checkpoints", help="List checkpoints for a file")
    lcp.add_argument("--file", required=True)

    args = parser.parse_args()

    if args.command == "checkpoint":
        cp_path = create_checkpoint(args.file)
        print(f"Checkpoint created: {cp_path}")
    elif args.command == "rollback":
        print(rollback(args.file))
    elif args.command == "validate":
        result = validate_python_file(args.file)
        print(result.to_summary())
        if result.issues:
            for i in result.issues:
                print(f"  - {i}")
        print(f"  Dimensions: {json.dumps(result.dimensions)}")
    elif args.command == "diff":
        print(diff_from_checkpoint(args.file))
    elif args.command == "history":
        for entry in load_eval_history(args.target):
            print(f"[{entry['timestamp'][:16]}] {entry['tool']} → {entry['target']} | score={entry['reward_score']}")
    elif args.command == "list-checkpoints":
        for cp in list_checkpoints(args.file):
            print(f"[{cp['timestamp'][:16]}] {cp['checkpoint_path']}")
    else:
        parser.print_help()
