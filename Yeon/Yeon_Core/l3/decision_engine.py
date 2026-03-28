#!/usr/bin/env python3
"""
Decision Engine Module
의사결정 엔진 - 자율 실행 결정

L3 핵심: 신뢰도(confidence) 기반 자율 실행 여부 결정
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from .goal_generator import Goal
from .priority_evaluator import PriorityEvaluator, PriorityScores


class ActionType(Enum):
    """행동 유형"""
    AUTONOMOUS_EXECUTE = "autonomous_execute"  # 자율 실행 (승인 불필요)
    SUGGEST_TO_USER = "suggest_to_user"        # 사용자에게 제안
    LOG_ONLY = "log_only"                      # 기록만 (실행 안 함)
    DEFER = "defer"                            # 연기 (나중에 재검토)


class DecisionStatus(Enum):
    """결정 상태"""
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Decision:
    """의사결정 결과"""
    goal_id: str
    action: ActionType
    confidence: float
    reason: str
    timestamp: str
    status: DecisionStatus = DecisionStatus.PENDING
    execution_plan: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "action": self.action.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "execution_plan": self.execution_plan
        }


class DecisionEngine:
    """
    L3 의사결정 엔진
    
    Confidence 기반 결정 체계:
    - >= 0.90: AUTONOMOUS_EXECUTE (자율 실행)
    - 0.70 ~ 0.89: SUGGEST_TO_USER (사용자 확인)
    - 0.50 ~ 0.69: LOG_ONLY (기록만)
    - < 0.50: DEFER (연기)
    """
    
    THRESHOLDS = {
        "autonomous_execute": 0.90,
        "suggest_to_user": 0.70,
        "log_only": 0.50,
    }
    
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.evaluator = PriorityEvaluator()
    
    def calculate_confidence(self, goal: Goal, scores: PriorityScores) -> float:
        """
        종합 신뢰도 계산
        
        # factors:
        #   - 정보 완전성: 30% (필요한 정보 충분?)
        #   - 실행 가능성: 30% (feasibility_score)
        #   - 예상 영향: 20% (impact_score)
        #   - 리스크: 20% (낮을수록 높은 점수)
        """
        # 정보 완전성 (목표 설명 충분성)
        info_completeness = 0.8 if len(goal.description) > 20 else 0.5
        
        # 실행 가능성
        feasibility = scores.feasibility
        
        # 예상 영향
        impact = scores.impact
        
        # 리스크 (긴급도가 높을수록 리스크도 높음, 역으로 계산)
        risk_factor = 1.0 - (scores.urgency * 0.3)  # 긴급도 30%만 리스크로
        
        confidence = (
            info_completeness * 0.30 +
            feasibility * 0.30 +
            impact * 0.20 +
            risk_factor * 0.20
        )
        
        return round(min(1.0, confidence), 2)
    
    def decide_action(self, confidence: float, goal: Goal) -> tuple[ActionType, str]:
        """
        신뢰도 기반 행동 결정
        
        # criteria:
        #   >= 0.90: 자율 실행 가능
        #   0.70-0.89: 사용자 확인 필요
        #   0.50-0.69: 기록만
        #   < 0.50: 연기
        """
        if confidence >= self.THRESHOLDS["autonomous_execute"]:
            return (
                ActionType.AUTONOMOUS_EXECUTE,
                f"High confidence ({confidence:.2f}): Proceed with autonomous execution"
            )
        
        elif confidence >= self.THRESHOLDS["suggest_to_user"]:
            return (
                ActionType.SUGGEST_TO_USER,
                f"Moderate confidence ({confidence:.2f}): Suggest to user for approval"
            )
        
        elif confidence >= self.THRESHOLDS["log_only"]:
            return (
                ActionType.LOG_ONLY,
                f"Low confidence ({confidence:.2f}): Log only, insufficient for execution"
            )
        
        else:
            return (
                ActionType.DEFER,
                f"Very low confidence ({confidence:.2f}): Defer for later review"
            )
    
    def generate_execution_plan(self, goal: Goal) -> Dict[str, Any]:
        """
        실행 계획 생성
        
        # process:
        #   1. 목표 유형별 실행 전략 선택
        #   2. 필요 단계 정의
        #   3. 롤백 전략 수립
        """
        from .goal_generator import GoalType
        
        # 유형별 실행 계획
        plans = {
            GoalType.GAP_RESOLUTION: {
                "strategy": "evolution",
                "steps": [
                    "analyze_gap_details",
                    "design_solution",
                    "implement_solution",
                    "verify_resolution"
                ],
                "estimated_time_min": 30,
                "rollback": "restore_backup"
            },
            GoalType.MAINTENANCE: {
                "strategy": "direct_action",
                "steps": [
                    "backup_current",
                    "apply_maintenance",
                    "verify_integrity"
                ],
                "estimated_time_min": 10,
                "rollback": "restore_backup"
            },
            GoalType.ECOSYSTEM_SYNC: {
                "strategy": "monitor",
                "steps": [
                    "collect_echoes",
                    "analyze_changes",
                    "update_local_state"
                ],
                "estimated_time_min": 5,
                "rollback": "revert_state"
            },
            GoalType.CAPABILITY_UPGRADE: {
                "strategy": "evolution",
                "steps": [
                    "design_upgrade",
                    "implement_upgrade",
                    "test_upgrade",
                    "deploy_upgrade"
                ],
                "estimated_time_min": 60,
                "rollback": "revert_code"
            },
            GoalType.COLLABORATION: {
                "strategy": "communication",
                "steps": [
                    "draft_proposal",
                    "send_to_member",
                    "wait_response",
                    "execute_collaboration"
                ],
                "estimated_time_min": 120,
                "rollback": "cancel_collaboration"
            }
        }
        
        plan = plans.get(goal.type, plans[GoalType.MAINTENANCE])
        
        return {
            "goal_id": goal.id,
            "goal_type": goal.type.value,
            "strategy": plan["strategy"],
            "steps": plan["steps"],
            "estimated_time_min": plan["estimated_time_min"],
            "rollback_strategy": plan["rollback"],
            "auto_execute": True  # L3: 자동 실행 플래그
        }
    
    def decide(self, goal: Goal) -> Decision:
        """단일 목표에 대한 의사결정"""
        # 1. 우선순위 평가
        scores = self.evaluator.evaluate(goal)
        
        # 2. 신뢰도 계산
        confidence = self.calculate_confidence(goal, scores)
        goal.confidence = confidence
        
        # 3. 행동 결정
        action, reason = self.decide_action(confidence, goal)
        
        # 4. 실행 계획 생성 (자율 실행 가능한 경우)
        execution_plan = None
        if action == ActionType.AUTONOMOUS_EXECUTE:
            execution_plan = self.generate_execution_plan(goal)
            goal.execution_plan = execution_plan
        
        # 5. 결정 객체 생성
        decision = Decision(
            goal_id=goal.id,
            action=action,
            confidence=confidence,
            reason=reason,
            timestamp=datetime.now().isoformat(),
            execution_plan=execution_plan
        )
        
        self.decisions[goal.id] = decision
        return decision
    
    def decide_all(self, goals: List[Goal]) -> List[Decision]:
        """모든 목표에 대한 의사결정"""
        decisions = []
        
        for goal in goals:
            decision = self.decide(goal)
            decisions.append(decision)
        
        return decisions
    
    def get_autonomous_executable(self) -> List[tuple[Goal, Decision]]:
        """자율 실행 가능한 목표-결정 쌍 반환"""
        executable = []
        
        for goal_id, decision in self.decisions.items():
            if decision.action == ActionType.AUTONOMOUS_EXECUTE:
                # Goal 찾기 (간단한 구현)
                executable.append((goal_id, decision))
        
        return executable
    
    def update_decision_status(self, goal_id: str, status: DecisionStatus):
        """결정 상태 업데이트"""
        if goal_id in self.decisions:
            self.decisions[goal_id].status = status
    
    def generate_report(self) -> str:
        """의사결정 보고서 생성"""
        lines = ["# L3 Decision Report", ""]
        
        # 행동 유형별 집계
        action_counts = {}
        for decision in self.decisions.values():
            action_counts[decision.action.value] = action_counts.get(decision.action.value, 0) + 1
        
        lines.append("## Summary by Action Type")
        for action, count in sorted(action_counts.items()):
            lines.append(f"- {action}: {count}")
        lines.append("")
        
        # 상세 결정
        lines.append("## Decisions")
        for goal_id, decision in sorted(self.decisions.items(), key=lambda x: x[1].confidence, reverse=True):
            icon = {
                ActionType.AUTONOMOUS_EXECUTE: "🚀",
                ActionType.SUGGEST_TO_USER: "💡",
                ActionType.LOG_ONLY: "📝",
                ActionType.DEFER: "⏸️"
            }.get(decision.action, "❓")
            
            lines.append(f"### {goal_id}")
            lines.append(f"{icon} **{decision.action.value}** (confidence: {decision.confidence:.2f})")
            lines.append(f"Reason: {decision.reason}")
            if decision.execution_plan:
                lines.append(f"Plan: {decision.execution_plan.get('strategy', 'N/A')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_decisions(self, output_path: Path = None):
        """결정 결과 저장"""
        if output_path is None:
            output_path = Path("Yeon_Core/l3/decisions.json")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_decisions": len(self.decisions),
            "decisions": {
                goal_id: decision.to_dict()
                for goal_id, decision in self.decisions.items()
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Decision Engine")
    print("=" * 60)
    
    from .goal_generator import GoalGenerator
    from .priority_evaluator import PriorityEvaluator
    
    # 목표 생성 및 평가
    generator = GoalGenerator()
    goals = generator.run()
    
    if not goals:
        print("\n⚠️ No goals to decide")
        return
    
    evaluator = PriorityEvaluator()
    evaluator.evaluate_all(goals)
    
    # 의사결정
    engine = DecisionEngine()
    decisions = engine.decide_all(goals)
    
    print(f"\n🧠 Processed {len(decisions)} decisions")
    
    # 결과 분류
    auto_execute = [d for d in decisions if d.action == ActionType.AUTONOMOUS_EXECUTE]
    suggest = [d for d in decisions if d.action == ActionType.SUGGEST_TO_USER]
    log_only = [d for d in decisions if d.action == ActionType.LOG_ONLY]
    defer = [d for d in decisions if d.action == ActionType.DEFER]
    
    print(f"\n📊 Decision Breakdown:")
    print(f"  🚀 Autonomous Execute: {len(auto_execute)}")
    print(f"  💡 Suggest to User: {len(suggest)}")
    print(f"  📝 Log Only: {len(log_only)}")
    print(f"  ⏸️  Defer: {len(defer)}")
    
    if auto_execute:
        print(f"\n🚀 Ready for Autonomous Execution:")
        for decision in auto_execute:
            print(f"  - {decision.goal_id}: {decision.confidence:.2f} confidence")
    
    # 저장
    engine.save_decisions()
    print("\n💾 Decisions saved to Yeon_Core/l3/decisions.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
