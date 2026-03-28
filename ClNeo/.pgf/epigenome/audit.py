"""
AuditTrail — Decision Audit Trail 내장 컴포넌트.

모든 발현 결정(ExpressionDecision)과 실행 결과를
구조화된 append-only trace로 기록한다.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TraceRecorder:
    """발현 결정 + 실행 결과를 trace.jsonl에 기록."""

    def __init__(self, trace_path: str | Path):
        self.trace_path = Path(trace_path)
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        decision: dict,
        execution_result: Any = None,
        quality_score: float = 0.0,
    ) -> dict:
        """발현 결정과 실행 결과를 trace 엔트리로 기록.

        Returns: 기록된 TraceEntry.
        """
        entry = {
            "decision": decision,
            "execution_result_type": type(execution_result).__name__ if execution_result else "None",
            "quality_score": quality_score,
            "feedback_applied": False,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

        # append-only JSONL
        with open(self.trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def mark_feedback_applied(self, node_id: str):
        """가장 최근 trace의 feedback_applied를 True로 갱신."""
        # JSONL은 append-only이므로 수정 엔트리를 추가
        correction = {
            "type": "feedback_applied",
            "node_id": node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(self.trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(correction, ensure_ascii=False) + "\n")


class TraceStore:
    """구조화된 trace 저장소 — 조회 및 분석 인터페이스."""

    def __init__(self, trace_path: str | Path):
        self.trace_path = Path(trace_path)

    def load_all(self) -> list[dict]:
        """전체 trace 로드."""
        if not self.trace_path.exists():
            return []
        entries = []
        for line in self.trace_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries

    def load_by_node(self, node_id: str, limit: int = 20) -> list[dict]:
        """특정 노드의 최근 trace만 로드."""
        all_entries = self.load_all()
        node_entries = [
            e for e in all_entries
            if e.get("decision", {}).get("node_id") == node_id
        ]
        return node_entries[-limit:]

    def summary(self) -> dict:
        """trace 전체 요약 통계."""
        entries = self.load_all()
        decisions = [e for e in entries if "decision" in e]

        if not decisions:
            return {"total": 0, "by_state": {}, "avg_quality": 0.0}

        by_state: dict[str, int] = {}
        total_quality = 0.0
        quality_count = 0

        for e in decisions:
            state = e["decision"].get("state", "unknown")
            by_state[state] = by_state.get(state, 0) + 1
            q = e.get("quality_score", 0)
            if q > 0:
                total_quality += q
                quality_count += 1

        return {
            "total": len(decisions),
            "by_state": by_state,
            "avg_quality": total_quality / quality_count if quality_count > 0 else 0.0,
        }

    def recent(self, limit: int = 10) -> list[dict]:
        """가장 최근 N개 trace."""
        all_entries = self.load_all()
        return all_entries[-limit:]
