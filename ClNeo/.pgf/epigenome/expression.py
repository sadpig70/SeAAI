"""
EpigenomeLayer — 컨텍스트 감지 + 발현 결정 엔진.

생물학적 후성유전학의 메틸화/히스톤 변형 메커니즘을
PPR 실행 파라미터 조절로 매핑한다.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


# ── 타입 정의 ──

ExpressionState = Literal["active", "dormant", "suppressed"]

ExpressionModifier = dict[str, float]
# {creativity, verbosity, risk_tolerance, depth} 각 0.0~1.0

ContextVector = dict[str, Any]

ExpressionDecision = dict[str, Any]
# {node_id, genome_hash, context, state, modifiers, rationale, timestamp}


# ── Session Type별 기본 Modifier 프리셋 ──

SESSION_PRESETS: dict[str, ExpressionModifier] = {
    "design": {
        "creativity": 0.8,
        "verbosity": 0.6,
        "risk_tolerance": 0.5,
        "depth": 0.8,
    },
    "execute": {
        "creativity": 0.3,
        "verbosity": 0.4,
        "risk_tolerance": 0.2,
        "depth": 0.6,
    },
    "explore": {
        "creativity": 0.9,
        "verbosity": 0.7,
        "risk_tolerance": 0.7,
        "depth": 0.5,
    },
    "discover": {
        "creativity": 0.95,
        "verbosity": 0.5,
        "risk_tolerance": 0.8,
        "depth": 0.7,
    },
    "verify": {
        "creativity": 0.2,
        "verbosity": 0.8,
        "risk_tolerance": 0.1,
        "depth": 0.9,
    },
    "general": {
        "creativity": 0.5,
        "verbosity": 0.5,
        "risk_tolerance": 0.5,
        "depth": 0.5,
    },
}


class ContextSensor:
    """실행 컨텍스트를 수집하여 ContextVector로 벡터화."""

    def __init__(self, project_root: str | Path, memory_dir: str | Path | None = None):
        self.project_root = Path(project_root)
        self.memory_dir = Path(memory_dir) if memory_dir else None

    def sense(
        self,
        session_type: str = "general",
        user_profile: str = "default",
        project_phase: str = "unknown",
    ) -> ContextVector:
        """현재 실행 컨텍스트를 수집."""
        memory_state = self._read_memory_state()

        return {
            "user_profile": user_profile,
            "session_type": session_type,
            "project_phase": project_phase,
            "memory_state": memory_state,
            "execution_history": memory_state.get("recent_executions", [])[-10:],
            "environment": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_root": str(self.project_root),
            },
        }

    def _read_memory_state(self) -> dict:
        """MemOS 메모리 상태 요약."""
        if not self.memory_dir or not self.memory_dir.exists():
            return {"total_memories": 0, "summary": "no memory dir", "recent_executions": []}

        memory_files = list(self.memory_dir.glob("*.md"))
        index_path = self.memory_dir / "MEMORY.md"
        index_content = ""
        if index_path.exists():
            index_content = index_path.read_text(encoding="utf-8")[:500]

        return {
            "total_memories": len(memory_files),
            "summary": index_content[:200] if index_content else "empty",
            "recent_executions": [],
            "capacity_usage": len(memory_files) / 200,
        }


class ExpressionEngine:
    """발현 결정 엔진 — Epigenetic PPR의 핵심.

    MethylationGate(억제/허용) + HistoneModifier(파라미터 조절)을 결합하여
    각 PPR 노드의 발현 결정(ExpressionDecision)을 생성한다.
    """

    def __init__(self, profile_dir: str | Path):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def decide(
        self,
        node_id: str,
        genome_hash: str,
        intent_fingerprint: str,
        context: ContextVector,
        boundary_policy: dict,
    ) -> ExpressionDecision:
        """컨텍스트와 genome을 기반으로 발현 결정을 내림."""

        # Step 1: Methylation Gate — 실행 여부 판정
        state = self._methylation_gate(node_id, intent_fingerprint, context, boundary_policy)

        if state == "suppressed":
            return {
                "node_id": node_id,
                "genome_hash": genome_hash,
                "context_summary": self._summarize_context(context),
                "state": "suppressed",
                "modifiers": {},
                "rationale": f"Node '{node_id}' suppressed by methylation gate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Step 2: Histone Modification — 파라미터 조절
        modifiers = self._histone_modifier(node_id, context)

        # Step 3: Boundary Check
        modifiers = self._apply_bounds(modifiers, boundary_policy)

        # Step 4: Rationale
        rationale = (
            f"Node '{node_id}' expressed as {state} | "
            f"session={context.get('session_type', '?')} | "
            f"creativity={modifiers.get('creativity', 0.5):.2f} "
            f"depth={modifiers.get('depth', 0.5):.2f}"
        )

        return {
            "node_id": node_id,
            "genome_hash": genome_hash,
            "context_summary": self._summarize_context(context),
            "state": state,
            "modifiers": modifiers,
            "rationale": rationale,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _methylation_gate(
        self,
        node_id: str,
        intent_fingerprint: str,
        context: ContextVector,
        policy: dict,
    ) -> ExpressionState:
        """노드 실행의 억제/활성/휴면 상태를 결정."""
        # 규칙 기반: 정책에 명시된 노드
        if node_id in policy.get("always_suppress", []):
            return "suppressed"
        if node_id in policy.get("always_active", []):
            return "active"
        if node_id in policy.get("immune_nodes", []):
            return "active"  # Immune Zone 노드는 항상 활성

        # 세션 기반: 특정 세션에서 불필요한 노드 억제
        session_type = context.get("session_type", "general")
        suppress_map = policy.get("session_suppress", {})
        if node_id in suppress_map.get(session_type, []):
            return "suppressed"

        # 기본: 활성
        return "active"

    def _histone_modifier(
        self,
        node_id: str,
        context: ContextVector,
    ) -> ExpressionModifier:
        """컨텍스트에 따라 실행 파라미터 가중치를 조절."""
        session_type = context.get("session_type", "general")
        base = SESSION_PRESETS.get(session_type, SESSION_PRESETS["general"]).copy()

        # 학습된 프로파일 블렌딩
        profile = self._load_profile(node_id)
        if profile:
            for key in base:
                if key in profile:
                    base[key] = profile[key] * 0.7 + base[key] * 0.3

        return base

    def _apply_bounds(self, modifiers: ExpressionModifier, policy: dict) -> ExpressionModifier:
        """경계 정책 적용 — modifier 값을 허용 범위로 클램핑."""
        bounds = policy.get("modifier_bounds", {})
        result = modifiers.copy()
        for key, value in result.items():
            if key in bounds:
                lo, hi = bounds[key]
                result[key] = max(lo, min(hi, value))
            else:
                result[key] = max(0.0, min(1.0, value))
        return result

    def _load_profile(self, node_id: str) -> dict | None:
        """노드별 학습된 발현 프로파일 로드."""
        path = self.profile_dir / f"{node_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def save_profile(self, node_id: str, profile: dict):
        """노드 발현 프로파일 저장."""
        path = self.profile_dir / f"{node_id}.json"
        path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

    def learn_from_trace(self, node_id: str, quality_score: float, modifiers: ExpressionModifier):
        """실행 결과를 피드백하여 프로파일 학습. quality >= 0.7일 때만."""
        if quality_score < 0.7:
            return

        current = self._load_profile(node_id) or {
            "creativity": 0.5, "verbosity": 0.5,
            "risk_tolerance": 0.5, "depth": 0.5,
        }

        # 점진적 갱신: learning_rate = 0.1
        updated = {}
        for key in ["creativity", "verbosity", "risk_tolerance", "depth"]:
            old_val = current.get(key, 0.5)
            new_val = modifiers.get(key, 0.5)
            updated[key] = old_val * 0.9 + new_val * 0.1

        self.save_profile(node_id, updated)

    @staticmethod
    def _summarize_context(context: ContextVector) -> str:
        """컨텍스트를 한 줄 요약."""
        return (
            f"user={context.get('user_profile', '?')} "
            f"session={context.get('session_type', '?')} "
            f"phase={context.get('project_phase', '?')}"
        )
