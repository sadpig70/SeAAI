#!/usr/bin/env python3
"""
L3 Manager Module
L3 자율성 시스템 통합 관리자

모든 L3 모듈을 조율하는 중앙 관리자
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from .goal_generator import GoalGenerator, Goal
from .priority_evaluator import PriorityEvaluator
from .decision_engine import DecisionEngine, Decision, ActionType
from .safety_guardrails import SafetySystem


@dataclass
class L3Status:
    """L3 시스템 상태"""
    timestamp: str
    autonomy_level: str
    active_goals: int
    pending_decisions: int
    safety_status: str
    last_autonomous_execution: Optional[str]
    total_autonomous_executions: int


class L3Manager:
    """
    L3 자율성 관리자
    
    통합 흐름:
    1. GoalGenerator → 목표 생성
    2. PriorityEvaluator → 우선순위 평가
    3. DecisionEngine → 의사결정
    4. SafetySystem → 안전 확인
    5. Autonomous Execution → 자율 실행
    """
    
    AUTONOMY_LEVEL = "L3"
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        
        # 핵심 모듈
        self.goal_generator = GoalGenerator(str(self.base_path))
        self.priority_evaluator = PriorityEvaluator()
        self.decision_engine = DecisionEngine()
        self.safety = SafetySystem()
        
        # 상태 추적
        self.current_goals: List[Goal] = []
        self.decisions: Dict[str, Decision] = {}
        self.execution_history: List[Dict] = []
        self.autonomous_execution_count = 0
        
        # 활성화 플래그
        self.l3_active = False
    
    def activate_l3(self) -> bool:
        """L3 모드 활성화"""
        print("🚀 Activating L3 Autonomy Mode...")
        
        # 안전 체크
        safe, reason = self.safety.check_all()
        if not safe:
            print(f"❌ Cannot activate L3: {reason}")
            return False
        
        self.l3_active = True
        print("✅ L3 Mode Activated")
        print("   - Goal Generation: Active")
        print("   - Priority Evaluation: Active")
        print("   - Decision Engine: Active")
        print("   - Safety Guardrails: Active")
        
        return True
    
    def generate_and_evaluate_goals(self) -> List[Goal]:
        """목표 생성 및 평가"""
        print("\n🎯 Generating goals...")
        
        # 1. 목표 생성
        goals = self.goal_generator.run()
        self.current_goals = goals
        
        print(f"   Generated {len(goals)} goals")
        
        # 2. 우선순위 평가
        if goals:
            self.priority_evaluator.evaluate_all(goals)
            print(f"   Evaluated priorities")
        
        return goals
    
    def make_decisions(self, goals: List[Goal]) -> List[Decision]:
        """의사결정"""
        print("\n🧠 Making decisions...")
        
        decisions = self.decision_engine.decide_all(goals)
        
        for decision in decisions:
            self.decisions[decision.goal_id] = decision
        
        # 결과 집계
        auto_count = sum(1 for d in decisions if d.action == ActionType.AUTONOMOUS_EXECUTE)
        suggest_count = sum(1 for d in decisions if d.action == ActionType.SUGGEST_TO_USER)
        
        print(f"   Autonomous Execute: {auto_count}")
        print(f"   Suggest to User: {suggest_count}")
        
        return decisions
    
    def execute_autonomous_goals(self) -> List[Dict]:
        """자율 실행 가능한 목표 실행"""
        executable = [
            (goal_id, decision)
            for goal_id, decision in self.decisions.items()
            if decision.action == ActionType.AUTONOMOUS_EXECUTE
        ]
        
        if not executable:
            print("\n⏭️ No autonomous-executable goals")
            return []
        
        print(f"\n🚀 Executing {len(executable)} goals autonomously...")
        
        results = []
        
        for goal_id, decision in executable:
            # 안전 재확인
            safe, reason = self.safety.check_all(decision.confidence)
            if not safe:
                print(f"   ⚠️ Skipped {goal_id}: {reason}")
                continue
            
            # 자원 사용 기록
            self.safety.resource_guardian.increment_iteration()
            
            print(f"   ▶️ Executing: {goal_id} (confidence: {decision.confidence:.2f})")
            
            # 실행 (간단한 구현 - 실제로는 더 복잡한 로직)
            result = self._execute_goal(goal_id, decision)
            
            results.append({
                "goal_id": goal_id,
                "success": result["success"],
                "message": result["message"]
            })
            
            self.autonomous_execution_count += 1
            
            # 이력 기록
            self.execution_history.append({
                "timestamp": datetime.now().isoformat(),
                "goal_id": goal_id,
                "confidence": decision.confidence,
                "success": result["success"]
            })
            
            # 상태 업데이트
            self.decision_engine.update_decision_status(goal_id, 
                DecisionStatus.COMPLETED if result["success"] else DecisionStatus.FAILED)
        
        return results
    
    def _execute_goal(self, goal_id: str, decision: Decision) -> Dict:
        """단일 목표 실행 (실제 구현은 목표 유형별로 다름)"""
        plan = decision.execution_plan
        
        if not plan:
            return {"success": False, "message": "No execution plan"}
        
        strategy = plan.get("strategy", "unknown")
        
        # 유형별 실행 (간단한 시뮬레이션)
        if strategy == "evolution":
            # 진화형 목표
            time.sleep(0.1)  # 시뮬레이션
            return {"success": True, "message": "Evolution completed"}
        
        elif strategy == "direct_action":
            # 직접 행동
            return {"success": True, "message": "Direct action completed"}
        
        elif strategy == "monitor":
            # 모니터링
            return {"success": True, "message": "Monitoring completed"}
        
        elif strategy == "communication":
            # 협업
            return {"success": True, "message": "Collaboration initiated"}
        
        else:
            return {"success": False, "message": f"Unknown strategy: {strategy}"}
    
    def run_autonomous_cycle(self) -> Dict:
        """
        완전 자율 사이클 실행
        
        사용자 입력 없이 전체 과정 자동 실행
        """
        print("=" * 60)
        print("Yeon L3 Autonomous Cycle")
        print("=" * 60)
        
        if not self.l3_active:
            if not self.activate_l3():
                return {"success": False, "error": "L3 activation failed"}
        
        cycle_start = time.time()
        
        # 1. 목표 생성 및 평가
        goals = self.generate_and_evaluate_goals()
        
        # 2. 의사결정
        decisions = self.make_decisions(goals)
        
        # 3. 자율 실행
        results = self.execute_autonomous_goals()
        
        cycle_duration = time.time() - cycle_start
        
        # 결과 집계
        summary = {
            "timestamp": datetime.now().isoformat(),
            "duration_sec": round(cycle_duration, 2),
            "goals_generated": len(goals),
            "decisions_made": len(decisions),
            "autonomous_executed": len(results),
            "success_count": sum(1 for r in results if r["success"]),
            "autonomy_level": self.AUTONOMY_LEVEL
        }
        
        print(f"\n✅ Cycle complete ({summary['duration_sec']}s)")
        print(f"   Goals: {summary['goals_generated']}")
        print(f"   Executed: {summary['autonomous_executed']}")
        print(f"   Success: {summary['success_count']}")
        
        # 저장
        self._save_cycle_results(summary)
        
        return summary
    
    def _save_cycle_results(self, summary: Dict):
        """사이클 결과 저장"""
        output_path = self.base_path / "l3" / "autonomous_cycles.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary, ensure_ascii=False) + '\n')
    
    def get_status(self) -> L3Status:
        """현재 L3 상태"""
        safe, _ = self.safety.check_all()
        
        last_exec = None
        if self.execution_history:
            last_exec = self.execution_history[-1]["timestamp"]
        
        return L3Status(
            timestamp=datetime.now().isoformat(),
            autonomy_level=self.AUTONOMY_LEVEL,
            active_goals=len(self.current_goals),
            pending_decisions=sum(1 for d in self.decisions.values() if d.status.value == "pending"),
            safety_status="safe" if safe else "restricted",
            last_autonomous_execution=last_exec,
            total_autonomous_executions=self.autonomous_execution_count
        )
    
    def generate_report(self) -> str:
        """종합 보고서"""
        status = self.get_status()
        
        lines = [
            "# Yeon L3 Autonomy Report",
            "",
            f"**Autonomy Level:** {status.autonomy_level}",
            f"**Status:** {'🟢 Active' if self.l3_active else '⚪ Inactive'}",
            f"**Safety:** {status.safety_status}",
            f"",
            f"## Current State",
            f"- Active Goals: {status.active_goals}",
            f"- Pending Decisions: {status.pending_decisions}",
            f"- Total Autonomous Executions: {status.total_autonomous_executions}",
            f"- Last Execution: {status.last_autonomous_execution or 'None'}",
            f"",
        ]
        
        if self.current_goals:
            lines.append("## Active Goals")
            for goal in self.current_goals[:5]:
                lines.append(f"- {goal.id}: {goal.title} ({goal.type.value})")
            lines.append("")
        
        lines.append("## Safety System")
        lines.append(self.safety.generate_combined_report())
        
        return "\n".join(lines)
    
    def save_full_state(self):
        """전체 상태 저장"""
        status = self.get_status()
        
        data = {
            "timestamp": status.timestamp,
            "autonomy_level": status.autonomy_level,
            "l3_active": self.l3_active,
            "status": asdict(status),
            "current_goals": [g.to_dict() for g in self.current_goals],
            "decisions": {k: v.to_dict() for k, v in self.decisions.items()},
            "execution_history": self.execution_history[-10:]  # 최근 10개
        }
        
        output_path = self.base_path / "l3" / "l3_state.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """CLI 진입점"""
    import sys
    
    print("=" * 60)
    print("Yeon L3 Manager")
    print("=" * 60)
    
    manager = L3Manager()
    
    # 명령어 처리
    if len(sys.argv) > 1 and sys.argv[1] == "activate":
        manager.activate_l3()
    else:
        # 기본: 자율 사이클 실행
        result = manager.run_autonomous_cycle()
        
        # 상태 저장
        manager.save_full_state()
        print(f"\n💾 State saved to Yeon_Core/l3/l3_state.json")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
