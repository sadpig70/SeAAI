"""
Yeon L3 Autonomy System
자율성 레벨 3: Self-Directed

Sub-modules:
    goal_generator: 자동 목표 생성
    priority_evaluator: 우선순위 평가
    decision_engine: 의사결정 엔진
    daemon_core: 데몬 핵심
    trigger_system: 트리거 시스템
    auto_revival: 자동 부활
    intent_analyzer: 의도 분석
    collaboration_initiator: 협업 개시
    workflow_orchestrator: 워크플로우 조정
    safety_guardrails: 안전 장치
    l3_manager: 통합 관리자

Version: 3.0 (L3)
"""

__version__ = "3.0"
__autonomy_level__ = "L3"

from .goal_generator import GoalGenerator, Goal
from .priority_evaluator import PriorityEvaluator
from .decision_engine import DecisionEngine, Decision
from .safety_guardrails import ConfidenceGate, ResourceGuardian
from .l3_manager import L3Manager

__all__ = [
    "GoalGenerator",
    "Goal",
    "PriorityEvaluator",
    "DecisionEngine",
    "Decision",
    "ConfidenceGate",
    "ResourceGuardian",
    "L3Manager",
]
