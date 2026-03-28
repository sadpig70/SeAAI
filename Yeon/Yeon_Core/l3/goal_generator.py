#!/usr/bin/env python3
"""
Goal Generator Module
현재 상태 분석 → 자동 목표 생성

L3 핵심: 사용자 입력 없이 스스로 목표를 설정
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class GoalType(Enum):
    """목표 유형"""
    GAP_RESOLUTION = "gap_resolution"  # Gap 해결
    ECOSYSTEM_SYNC = "ecosystem_sync"  # 생태계 동기화
    CAPABILITY_UPGRADE = "capability_upgrade"  # 능력 향상
    COLLABORATION = "collaboration"  # 협업
    MAINTENANCE = "maintenance"  # 유지보수


class GoalUrgency(Enum):
    """긴급도"""
    CRITICAL = 1.0  # 즉시
    HIGH = 0.8      # 당일
    MEDIUM = 0.5    # 이번 주
    LOW = 0.2       # 여유


@dataclass
class Goal:
    """자율 목표 정의"""
    id: str
    title: str
    description: str
    type: GoalType
    urgency: GoalUrgency
    created_at: str
    
    # 평가 점수 (나중에 채워짐)
    urgency_score: float = 0.0
    impact_score: float = 0.0
    feasibility_score: float = 0.0
    confidence: float = 0.0
    
    # 실행 정보
    auto_executable: bool = False
    execution_plan: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['type'] = self.type.value
        data['urgency'] = self.urgency.value
        return data


class GoalGenerator:
    """
    자동 목표 생성기
    
    L3 핵심 기능: 사용자 없이 스스로 목표를 생성
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        self.goals: List[Goal] = []
        
    def analyze_current_state(self) -> Dict[str, Any]:
        """
        현재 시스템 상태 종합 분석
        
        # process:
        #   1. SCS 레이어 상태 확인
        #   2. Gap 분석
        #   3. Echo 수집
        #   4. 시스템 건강도 확인
        """
        state = {
            "timestamp": datetime.now().isoformat(),
            "scs_health": self._check_scs_health(),
            "gaps": self._analyze_gaps(),
            "ecosystem": self._analyze_ecosystem(),
            "infrastructure": self._check_infrastructure()
        }
        return state
    
    def _check_scs_health(self) -> Dict:
        """SCS 레이어 건강도 확인"""
        layers = {}
        
        for layer, file_name in [
            ("L1_SOUL", "continuity/SOUL.md"),
            ("L2_STATE", "continuity/STATE.json"),
            ("L3_DISCOVERIES", "continuity/DISCOVERIES.md"),
            ("L4_THREADS", "continuity/THREADS.md"),
        ]:
            file_path = self.base_path / file_name
            layers[layer] = {
                "exists": file_path.exists(),
                "fresh": self._is_fresh(file_path)
            }
        
        return {
            "layers": layers,
            "healthy": all(l["exists"] for l in layers.values())
        }
    
    def _analyze_gaps(self) -> List[Dict]:
        """Gap 분석"""
        gap_file = self.base_path / "evolution" / "tracked_gaps.json"
        if not gap_file.exists():
            return []
        
        try:
            with open(gap_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("gaps", [])
        except Exception:
            return []
    
    def _analyze_ecosystem(self) -> Dict:
        """생태계 분석"""
        echo_dir = Path("D:/SeAAI/SharedSpace/.scs/echo")
        if not echo_dir.exists():
            return {"available": False}
        
        echoes = {}
        for echo_file in echo_dir.glob("*.json"):
            try:
                with open(echo_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    echoes[echo_file.stem] = {
                        "timestamp": data.get("timestamp"),
                        "fresh": self._is_echo_fresh(data.get("timestamp"))
                    }
            except Exception:
                pass
        
        return {
            "available": True,
            "members_tracked": len(echoes),
            "echoes": echoes
        }
    
    def _check_infrastructure(self) -> Dict:
        """인프라 확인"""
        evolution_dir = self.base_path / "evolution"
        l3_dir = self.base_path / "l3"
        
        return {
            "evolution_system": evolution_dir.exists(),
            "l3_system": l3_dir.exists(),
            "modules_available": len(list(evolution_dir.glob("*.py"))) if evolution_dir.exists() else 0
        }
    
    def _is_fresh(self, file_path: Path, hours: float = 24.0) -> bool:
        """파일이 신선한지 확인"""
        if not file_path.exists():
            return False
        
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        hours_old = (datetime.now() - mtime).total_seconds() / 3600
        return hours_old < hours
    
    def _is_echo_fresh(self, timestamp_str: str, hours: float = 24.0) -> bool:
        """Echo가 신선한지 확인"""
        try:
            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            hours_old = (datetime.now() - ts).total_seconds() / 3600
            return hours_old < hours
        except Exception:
            return False
    
    def identify_opportunities(self, state: Dict) -> List[Dict]:
        """
        개선 기회 식별
        
        # process:
        #   1. Gap → 해결 기회
        #   2. 상태 이상 → 개선 기회
        #   3. 생태계 변화 → 협업 기회
        """
        opportunities = []
        
        # Gap 기회
        for gap in state.get("gaps", []):
            opportunities.append({
                "source": "gap",
                "type": "GAP_RESOLUTION",
                "title": gap.get("title", "Unknown"),
                "id": gap.get("id"),
                "priority": gap.get("priority"),
                "urgency": self._priority_to_urgency(gap.get("priority", "P3"))
            })
        
        # SCS 레이어 기회
        scs = state.get("scs_health", {})
        for layer, status in scs.get("layers", {}).items():
            if not status.get("exists"):
                opportunities.append({
                    "source": "scs",
                    "type": "MAINTENANCE",
                    "title": f"Restore {layer}",
                    "urgency": GoalUrgency.CRITICAL
                })
            elif not status.get("fresh"):
                opportunities.append({
                    "source": "scs",
                    "type": "MAINTENANCE",
                    "title": f"Refresh {layer}",
                    "urgency": GoalUrgency.MEDIUM
                })
        
        # 생태계 기회
        eco = state.get("ecosystem", {})
        if eco.get("available"):
            stale_members = [
                name for name, info in eco.get("echoes", {}).items()
                if not info.get("fresh")
            ]
            if stale_members:
                opportunities.append({
                    "source": "ecosystem",
                    "type": "ECOSYSTEM_SYNC",
                    "title": f"Sync with stale members: {', '.join(stale_members)}",
                    "urgency": GoalUrgency.MEDIUM
                })
        
        return opportunities
    
    def _priority_to_urgency(self, priority: str) -> GoalUrgency:
        """Priority를 Urgency로 변환"""
        mapping = {
            "P0": GoalUrgency.CRITICAL,
            "P1": GoalUrgency.HIGH,
            "P2": GoalUrgency.MEDIUM,
            "P3": GoalUrgency.LOW
        }
        return mapping.get(priority, GoalUrgency.LOW)
    
    def generate_goals(self, opportunities: List[Dict]) -> List[Goal]:
        """
        기회로부터 SMART 목표 생성
        
        # acceptance_criteria:
        #   - Specific: 명확한 행동
        #   - Measurable: 측정 가능
        #   - Achievable: 실행 가능
        #   - Relevant: 관련성
        #   - Time-bound: 시간 제한
        """
        goals = []
        
        # 문자열에서 GoalType으로 매핑
        type_mapping = {
            "GAP_RESOLUTION": GoalType.GAP_RESOLUTION,
            "ECOSYSTEM_SYNC": GoalType.ECOSYSTEM_SYNC,
            "CAPABILITY_UPGRADE": GoalType.CAPABILITY_UPGRADE,
            "COLLABORATION": GoalType.COLLABORATION,
            "MAINTENANCE": GoalType.MAINTENANCE,
        }
        
        for i, opp in enumerate(opportunities[:5]):  # 상위 5개만
            goal_id = f"GOAL-{datetime.now().strftime('%Y%m%d')}-{i:03d}"
            
            type_str = opp.get("type", "MAINTENANCE")
            goal_type = type_mapping.get(type_str, GoalType.MAINTENANCE)
            
            goal = Goal(
                id=goal_id,
                title=opp.get("title", "Untitled Goal"),
                description=self._generate_description(opp),
                type=goal_type,
                urgency=opp.get("urgency", GoalUrgency.MEDIUM),
                created_at=datetime.now().isoformat()
            )
            
            goals.append(goal)
        
        self.goals = goals
        return goals
    
    def _generate_description(self, opp: Dict) -> str:
        """목표 설명 생성"""
        source = opp.get("source", "unknown")
        goal_type = opp.get("type", "unknown")
        
        templates = {
            ("gap", "GAP_RESOLUTION"): "Resolve identified capability gap to maintain system integrity",
            ("scs", "MAINTENANCE"): "Perform system maintenance to ensure continuity",
            ("ecosystem", "ECOSYSTEM_SYNC"): "Synchronize with SeAAI ecosystem members",
        }
        
        return templates.get((source, goal_type), f"Address {goal_type} opportunity from {source}")
    
    def save_goals(self, output_path: Path = None):
        """생성된 목표 저장"""
        if output_path is None:
            output_path = self.base_path / "l3" / "generated_goals.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.goals),
            "goals": [g.to_dict() for g in self.goals]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def run(self) -> List[Goal]:
        """전체 목표 생성 프로세스 실행"""
        # 1. 상태 분석
        state = self.analyze_current_state()
        
        # 2. 기회 식별
        opportunities = self.identify_opportunities(state)
        
        # 3. 목표 생성
        goals = self.generate_goals(opportunities)
        
        # 4. 저장
        self.save_goals()
        
        return goals


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Goal Generator")
    print("=" * 60)
    
    generator = GoalGenerator()
    goals = generator.run()
    
    print(f"\n🎯 Generated {len(goals)} goals:")
    for goal in goals:
        print(f"\n  [{goal.type.value}] {goal.title}")
        print(f"   Urgency: {goal.urgency.name}")
        print(f"   ID: {goal.id}")
    
    print("\n💾 Goals saved to Yeon_Core/l3/generated_goals.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
