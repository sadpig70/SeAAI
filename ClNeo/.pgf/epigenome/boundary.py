"""
ExpressionBoundary — 발현 경계 메커니즘.

발현 결정이 원래 의도에서 벗어나는 것을 방지하고,
위험한 발현 패턴을 차단하는 안전장치.
"""

import json
from pathlib import Path
from typing import Any


# ── 기본 경계 정책 ──

DEFAULT_BOUNDARY_POLICY = {
    "max_drift": 0.3,
    "always_active": [],
    "always_suppress": [],
    "immune_nodes": [],
    "modifier_bounds": {
        "creativity": [0.05, 0.95],
        "verbosity": [0.1, 0.9],
        "risk_tolerance": [0.0, 0.8],
        "depth": [0.1, 1.0],
    },
    "session_suppress": {},
}


class BoundaryPolicy:
    """발현 경계 정책 관리.

    epigenome/boundary_policy.yaml을 로드하고 기본값과 병합.
    """

    def __init__(self, policy_path: str | Path | None = None):
        self.policy = DEFAULT_BOUNDARY_POLICY.copy()

        if policy_path:
            path = Path(policy_path)
            if path.exists():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                self._merge(loaded)

    def get(self, key: str, default: Any = None) -> Any:
        return self.policy.get(key, default)

    def to_dict(self) -> dict:
        return self.policy.copy()

    def save(self, path: str | Path):
        """정책을 JSON으로 저장."""
        Path(path).write_text(
            json.dumps(self.policy, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _merge(self, loaded: dict):
        """로드된 정책을 기본값과 병합."""
        for key, value in loaded.items():
            if key in self.policy and isinstance(self.policy[key], dict) and isinstance(value, dict):
                self.policy[key].update(value)
            else:
                self.policy[key] = value


class DriftDetector:
    """의도 이탈 감지기.

    발현 결정이 원래 genome의 의도에서 얼마나 벗어났는지를
    0.0(완전 정렬) ~ 1.0(완전 이탈)으로 측정.
    """

    @staticmethod
    def compute_drift(
        modifiers: dict[str, float],
        baseline: dict[str, float] | None = None,
    ) -> float:
        """modifier가 baseline(기본값 0.5)에서 벗어난 정도를 계산.

        유클리드 거리 기반. 정규화하여 0.0~1.0 범위로 반환.
        """
        if baseline is None:
            baseline = {"creativity": 0.5, "verbosity": 0.5, "risk_tolerance": 0.5, "depth": 0.5}

        total_sq = 0.0
        n = 0
        for key in baseline:
            if key in modifiers:
                diff = modifiers[key] - baseline[key]
                total_sq += diff * diff
                n += 1

        if n == 0:
            return 0.0

        # max possible distance per dim = 0.5^2 = 0.25, normalized
        max_dist = (n * 0.25) ** 0.5
        actual_dist = total_sq ** 0.5
        return min(1.0, actual_dist / max_dist) if max_dist > 0 else 0.0

    @staticmethod
    def is_safe(drift_score: float, max_drift: float = 0.3) -> bool:
        """drift가 허용 범위 내인지 확인."""
        return drift_score <= max_drift
