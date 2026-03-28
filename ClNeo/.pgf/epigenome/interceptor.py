"""
PPRInterceptor — PPR 실행 전 epigenome 주입 통합 모듈.

PGF-Loop 또는 직접 PPR 실행 시, 이 인터셉터가:
1. 컨텍스트를 감지하고
2. 발현 결정을 내리고
3. 결정에 따라 PPR을 실행하고
4. 결과를 trace에 기록하고
5. 성공 시 프로파일을 학습한다.
"""

from pathlib import Path
from typing import Any, Callable

from .genome import GenomeRegistry
from .expression import ContextSensor, ExpressionEngine
from .boundary import BoundaryPolicy, DriftDetector
from .audit import TraceRecorder, TraceStore


class PPRInterceptor:
    """Epigenetic PPR 통합 인터셉터.

    PPR 함수 실행을 가로채어 genome/epigenome 계층을 적용하고,
    모든 결정을 audit trail에 기록한다.

    Usage:
        interceptor = PPRInterceptor(project_root=".pgf/epigenome")
        interceptor.init(design_path=".pgf/DESIGN-EpigeneticPPR.md")

        result = interceptor.execute(
            node_id="content_planner",
            ppr_function=content_planner,
            args={"topic": "AI", "audience": "technical"},
            session_type="design",
        )
    """

    def __init__(self, project_root: str | Path):
        root = Path(project_root)

        self.genome = GenomeRegistry(root / "genome_registry.json")
        self.expression = ExpressionEngine(root / "profiles")
        self.policy = BoundaryPolicy(root / "boundary_policy.json")
        self.recorder = TraceRecorder(root / "trace.jsonl")
        self.store = TraceStore(root / "trace.jsonl")
        self.sensor = ContextSensor(
            project_root=root.parent,  # .pgf의 부모 = 프로젝트 루트
            memory_dir=None,  # 초기화 시 별도 설정 가능
        )
        self._initialized = False

    def init(self, design_path: str | Path, memory_dir: str | Path | None = None):
        """genome 레지스트리 빌드 및 초기화."""
        count = self.genome.build_from_design(design_path)
        if memory_dir:
            self.sensor = ContextSensor(
                project_root=Path(design_path).parent.parent,
                memory_dir=memory_dir,
            )
        self._initialized = True
        return count

    def execute(
        self,
        node_id: str,
        ppr_function: Callable | None = None,
        args: dict | None = None,
        session_type: str = "general",
        user_profile: str = "default",
        project_phase: str = "unknown",
    ) -> dict[str, Any]:
        """PPR 함수를 epigenome 컨텍스트와 함께 실행.

        Returns:
            {
                "result": Any,           # PPR 실행 결과
                "decision": dict,        # ExpressionDecision
                "quality": float,        # 품질 점수
                "state": str,            # active/dormant/suppressed
            }
        """
        if args is None:
            args = {}

        # Phase 1: Context Sensing
        context = self.sensor.sense(
            session_type=session_type,
            user_profile=user_profile,
            project_phase=project_phase,
        )

        # Phase 2: Genome Lookup
        genome_entry = self.genome.get(node_id)
        genome_hash = genome_entry["genome_hash"] if genome_entry else "unknown"
        intent_fp = genome_entry["intent_fingerprint"] if genome_entry else "unknown"

        # Phase 3: Expression Decision
        decision = self.expression.decide(
            node_id=node_id,
            genome_hash=genome_hash,
            intent_fingerprint=intent_fp,
            context=context,
            boundary_policy=self.policy.to_dict(),
        )

        # Phase 4: Gate Check
        if decision["state"] == "suppressed":
            self.recorder.record(decision)
            return {
                "result": None,
                "decision": decision,
                "quality": 0.0,
                "state": "suppressed",
            }

        # Phase 5: Drift Check
        drift = DriftDetector.compute_drift(decision.get("modifiers", {}))
        max_drift = self.policy.get("max_drift", 0.3)
        if not DriftDetector.is_safe(drift, max_drift):
            decision["rationale"] += f" [DRIFT WARNING: {drift:.2f} > {max_drift}]"

        # Phase 6: Execute PPR
        result = None
        quality = 0.0

        if ppr_function:
            # modifier를 실행 환경에 주입
            augmented_args = {
                **args,
                "_epigenome": {
                    "modifiers": decision.get("modifiers", {}),
                    "state": decision["state"],
                    "node_id": node_id,
                },
            }
            try:
                result = ppr_function(**augmented_args)
                quality = 0.8  # 기본 성공 점수
            except TypeError:
                # _epigenome 파라미터를 지원하지 않는 함수
                try:
                    result = ppr_function(**args)
                    quality = 0.7
                except Exception:
                    result = None
                    quality = 0.0
            except Exception:
                result = None
                quality = 0.0
        else:
            # 함수 없이 decision만 생성 (dry-run)
            quality = 0.5

        # Phase 7: Trace Recording
        self.recorder.record(decision, result, quality)

        # Phase 8: Profile Learning
        if quality >= 0.7 and decision.get("modifiers"):
            self.expression.learn_from_trace(
                node_id=node_id,
                quality_score=quality,
                modifiers=decision["modifiers"],
            )

        return {
            "result": result,
            "decision": decision,
            "quality": quality,
            "state": decision["state"],
        }

    def dry_run(
        self,
        node_id: str,
        session_type: str = "general",
    ) -> dict:
        """PPR 함수 없이 발현 결정만 시뮬레이션."""
        return self.execute(
            node_id=node_id,
            ppr_function=None,
            session_type=session_type,
        )

    def status(self) -> dict:
        """Epigenetic PPR 시스템 상태 요약."""
        trace_summary = self.store.summary()
        return {
            "initialized": self._initialized,
            "genome_nodes": len(self.genome.list_nodes()),
            "trace_entries": trace_summary["total"],
            "avg_quality": trace_summary["avg_quality"],
            "state_distribution": trace_summary["by_state"],
            "policy": {
                "max_drift": self.policy.get("max_drift"),
                "immune_nodes": len(self.policy.get("immune_nodes", [])),
            },
        }
