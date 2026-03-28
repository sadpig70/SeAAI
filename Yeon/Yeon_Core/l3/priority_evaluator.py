#!/usr/bin/env python3
"""
Priority Evaluator Module
목표 우선순위 자동 평가

L3 핵심: 다차원 평가를 통한 자동 우선순위 결정
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from .goal_generator import Goal, GoalType, GoalUrgency


@dataclass
class PriorityScores:
    """우선순위 점수"""
    urgency: float      # 0.0 ~ 1.0 (긴급도)
    impact: float       # 0.0 ~ 1.0 (영향도)
    feasibility: float  # 0.0 ~ 1.0 (실현 가능성)
    total: float        # 종합 점수


class PriorityEvaluator:
    """
    목표 우선순위 자동 평가기
    
    3가지 차원으로 평가:
    1. Urgency (긴급도): 얼마나 빨리 해야 하는가?
    2. Impact (영향도): 완료 시 얼마나 큰 효과가 있는가?
    3. Feasibility (실현 가능성): 얼마나 쉽게 할 수 있는가?
    """
    
    def __init__(self):
        self.scores: Dict[str, PriorityScores] = {}
    
    def evaluate_urgency(self, goal: Goal) -> float:
        """
        긴급도 평가 (0.0 ~ 1.0)
        
        # criteria:
        #   - GoalUrgency 값: 40%
        #   - 목표 유형별 기본 긴급도: 30%
        #   - 시스템 상태 기반: 30%
        """
        base_score = goal.urgency.value  # CRITICAL=1.0, HIGH=0.8, etc.
        
        # 유형별 가중치
        type_weights = {
            GoalType.GAP_RESOLUTION: 0.9,
            GoalType.MAINTENANCE: 0.7,
            GoalType.ECOSYSTEM_SYNC: 0.5,
            GoalType.COLLABORATION: 0.6,
            GoalType.CAPABILITY_UPGRADE: 0.4
        }
        type_weight = type_weights.get(goal.type, 0.5)
        
        # 시스템 상태 기반 (Gap 해결 유형이면 높게)
        system_factor = 0.7 if "GAP" in goal.type.value else 0.5
        
        # 종합 점수
        score = (base_score * 0.4) + (type_weight * 0.3) + (system_factor * 0.3)
        return round(min(1.0, score), 2)
    
    def evaluate_impact(self, goal: Goal) -> float:
        """
        영향도 평가 (0.0 ~ 1.0)
        
        # criteria:
        #   - 시스템 안정성 영향: 40%
        #   - 기능 향상: 30%
        #   - 생태계 연계: 30%
        """
        # 시스템 안정성 영향
        stability_impact = {
            GoalType.MAINTENANCE: 0.9,
            GoalType.GAP_RESOLUTION: 0.8,
            GoalType.ECOSYSTEM_SYNC: 0.6,
            GoalType.CAPABILITY_UPGRADE: 0.5,
            GoalType.COLLABORATION: 0.4
        }
        stability = stability_impact.get(goal.type, 0.5)
        
        # 기능 향상
        capability_boost = {
            GoalType.CAPABILITY_UPGRADE: 0.9,
            GoalType.GAP_RESOLUTION: 0.7,
            GoalType.COLLABORATION: 0.6,
            GoalType.ECOSYSTEM_SYNC: 0.5,
            GoalType.MAINTENANCE: 0.3
        }
        capability = capability_boost.get(goal.type, 0.5)
        
        # 생태계 연계
        ecosystem_link = {
            GoalType.ECOSYSTEM_SYNC: 0.9,
            GoalType.COLLABORATION: 0.8,
            GoalType.GAP_RESOLUTION: 0.5,
            GoalType.CAPABILITY_UPGRADE: 0.4,
            GoalType.MAINTENANCE: 0.3
        }
        ecosystem = ecosystem_link.get(goal.type, 0.5)
        
        score = (stability * 0.4) + (capability * 0.3) + (ecosystem * 0.3)
        return round(min(1.0, score), 2)
    
    def evaluate_feasibility(self, goal: Goal) -> float:
        """
        실현 가능성 평가 (0.0 ~ 1.0)
        
        # criteria:
        #   - 필요 리소스 추정: 40%
        #   - 의존성 복잡도: 30%
        #   - 이전 유사 작업 경험: 30%
        """
        # 유형별 기본 난이도
        base_difficulty = {
            GoalType.MAINTENANCE: 0.9,      # 쉬움
            GoalType.ECOSYSTEM_SYNC: 0.7,
            GoalType.GAP_RESOLUTION: 0.5,
            GoalType.CAPABILITY_UPGRADE: 0.4,
            GoalType.COLLABORATION: 0.3      # 어려움 (외부 의존)
        }
        base = base_difficulty.get(goal.type, 0.5)
        
        # 긴급도가 높을수록 우선 처리하므로 가중치 조정
        urgency_boost = goal.urgency.value * 0.1
        
        score = min(1.0, base + urgency_boost)
        return round(score, 2)
    
    def calculate_total_score(self, scores: PriorityScores) -> float:
        """
        종합 우선순위 점수 계산
        
        # weights:
        #   - urgency: 40% (빨리 해야 함)
        #   - impact: 35% (큰 효과)
        #   - feasibility: 25% (할 수 있음)
        """
        total = (
            scores.urgency * 0.40 +
            scores.impact * 0.35 +
            scores.feasibility * 0.25
        )
        return round(total, 2)
    
    def evaluate(self, goal: Goal) -> PriorityScores:
        """단일 목표 평가"""
        scores = PriorityScores(
            urgency=self.evaluate_urgency(goal),
            impact=self.evaluate_impact(goal),
            feasibility=self.evaluate_feasibility(goal),
            total=0.0
        )
        scores.total = self.calculate_total_score(scores)
        
        self.scores[goal.id] = scores
        
        # Goal 객체에도 점수 반영
        goal.urgency_score = scores.urgency
        goal.impact_score = scores.impact
        goal.feasibility_score = scores.feasibility
        
        return scores
    
    def evaluate_all(self, goals: List[Goal]) -> List[Goal]:
        """모든 목표 평가 및 정렬"""
        for goal in goals:
            self.evaluate(goal)
        
        # 종합 점수 기준 정렬 (높은 점수 우선)
        return sorted(goals, key=lambda g: self.scores.get(g.id, PriorityScores(0,0,0,0)).total, reverse=True)
    
    def get_top_priority(self, goals: List[Goal], n: int = 3) -> List[Goal]:
        """상위 n개 우선순위 목표 반환"""
        sorted_goals = self.evaluate_all(goals)
        return sorted_goals[:n]
    
    def generate_report(self) -> str:
        """평가 보고서 생성"""
        lines = ["# Priority Evaluation Report", ""]
        
        for goal_id, scores in sorted(self.scores.items(), key=lambda x: x[1].total, reverse=True):
            lines.append(f"## {goal_id}")
            lines.append(f"- Urgency: {scores.urgency:.2f}")
            lines.append(f"- Impact: {scores.impact:.2f}")
            lines.append(f"- Feasibility: {scores.feasibility:.2f}")
            lines.append(f"- **Total: {scores.total:.2f}**")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_evaluation(self, output_path: Path = None):
        """평가 결과 저장"""
        if output_path is None:
            output_path = Path("Yeon_Core/l3/priority_evaluation.json")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "evaluations": {
                goal_id: {
                    "urgency": scores.urgency,
                    "impact": scores.impact,
                    "feasibility": scores.feasibility,
                    "total": scores.total
                }
                for goal_id, scores in self.scores.items()
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Priority Evaluator")
    print("=" * 60)
    
    from .goal_generator import GoalGenerator
    
    # 목표 생성
    generator = GoalGenerator()
    goals = generator.run()
    
    if not goals:
        print("\n⚠️ No goals to evaluate")
        return
    
    # 평가
    evaluator = PriorityEvaluator()
    top_goals = evaluator.get_top_priority(goals, 3)
    
    print(f"\n📊 Evaluated {len(goals)} goals")
    print(f"\n🏆 Top 3 Priority Goals:")
    
    for i, goal in enumerate(top_goals, 1):
        scores = evaluator.scores.get(goal.id)
        if scores:
            print(f"\n  {i}. {goal.title}")
            print(f"     Type: {goal.type.value}")
            print(f"     Total Score: {scores.total:.2f}")
            print(f"     (U:{scores.urgency:.2f} I:{scores.impact:.2f} F:{scores.feasibility:.2f})")
    
    # 저장
    evaluator.save_evaluation()
    print("\n💾 Evaluation saved to Yeon_Core/l3/priority_evaluation.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
