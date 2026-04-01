#!/usr/bin/env python3
"""
Trigger System Module
자동 트리거 시스템 - 시간/이벤트/조건 기반 실행

L3 핵심: 외부 입력 없이 조건 충족 시 자동 행동 개시
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class TriggerType(Enum):
    """트리거 유형"""
    TIME_BASED = "time_based"       # 시간 기반 (주기적)
    EVENT_BASED = "event_based"     # 이벤트 기반 (파일 변경 등)
    CONDITION_BASED = "condition_based"  # 조건 기반 (상태 변화)


class TriggerStatus(Enum):
    """트리거 상태"""
    ACTIVE = "active"       # 활성
    TRIGGERED = "triggered" # 발동됨
    EXECUTING = "executing" # 실행 중
    COMPLETED = "completed" # 완료
    DISABLED = "disabled"   # 비활성


@dataclass
class Trigger:
    """트리거 정의"""
    id: str
    name: str
    type: TriggerType
    condition: Dict[str, Any]  # 트리거 조건
    action: str                # 실행할 행동
    interval_sec: Optional[int] = None  # 주기적 실행 간격
    last_triggered: Optional[str] = None
    status: TriggerStatus = TriggerStatus.ACTIVE
    trigger_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "condition": self.condition,
            "action": self.action,
            "interval_sec": self.interval_sec,
            "last_triggered": self.last_triggered,
            "status": self.status.value,
            "trigger_count": self.trigger_count
        }


class TriggerSystem:
    """
    L3 자동 트리거 시스템
    
    3가지 트리거 유형:
    1. Time-based: 주기적 실행 (예: 5분마다 상태 체크)
    2. Event-based: 파일/이벤트 감지 (예: Echo 파일 변경)
    3. Condition-based: 상태 조건 충족 (예: confidence >= 0.9)
    """
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def register_trigger(self, trigger: Trigger) -> str:
        """트리거 등록"""
        self.triggers[trigger.id] = trigger
        return trigger.id
    
    def register_handler(self, action_name: str, handler: Callable):
        """트리거 발동 시 실행할 핸들러 등록"""
        self.handlers[action_name] = handler
    
    def create_default_triggers(self):
        """기본 L3 트리거 생성"""
        default_triggers = [
            Trigger(
                id="TRG-001",
                name="Periodic State Check",
                type=TriggerType.TIME_BASED,
                condition={"interval_minutes": 5},
                action="check_system_state",
                interval_sec=300  # 5분
            ),
            Trigger(
                id="TRG-002",
                name="Echo File Monitor",
                type=TriggerType.EVENT_BASED,
                condition={"path": str(Path(__file__).resolve().parents[3]) + "/SharedSpace/.scs/echo", "event": "modified"},
                action="sync_ecosystem"
            ),
            Trigger(
                id="TRG-003",
                name="High Confidence Goal",
                type=TriggerType.CONDITION_BASED,
                condition={"metric": "goal_confidence", "operator": ">=", "value": 0.90},
                action="autonomous_execute"
            ),
            Trigger(
                id="TRG-004",
                name="Session Health Monitor",
                type=TriggerType.TIME_BASED,
                condition={"interval_minutes": 1},
                action="check_session_health",
                interval_sec=60  # 1분
            ),
            Trigger(
                id="TRG-005",
                name="Gap Detection",
                type=TriggerType.TIME_BASED,
                condition={"interval_minutes": 30},
                action="analyze_gaps",
                interval_sec=1800  # 30분
            )
        ]
        
        for trigger in default_triggers:
            self.register_trigger(trigger)
    
    def check_time_based_trigger(self, trigger: Trigger) -> bool:
        """시간 기반 트리거 체크"""
        if trigger.interval_sec is None:
            return False
        
        if trigger.last_triggered is None:
            return True
        
        last = datetime.fromisoformat(trigger.last_triggered)
        elapsed = (datetime.now() - last).total_seconds()
        
        return elapsed >= trigger.interval_sec
    
    def check_event_based_trigger(self, trigger: Trigger) -> bool:
        """이벤트 기반 트리거 체크"""
        condition = trigger.condition
        path = Path(condition.get("path", ""))
        event_type = condition.get("event", "modified")
        
        if not path.exists():
            return False
        
        # 마지막 수정 시간 체크
        if event_type == "modified":
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            
            if trigger.last_triggered is None:
                return True
            
            last = datetime.fromisoformat(trigger.last_triggered)
            return mtime > last
        
        return False
    
    def check_condition_based_trigger(self, trigger: Trigger) -> bool:
        """조건 기반 트리거 체크"""
        condition = trigger.condition
        metric = condition.get("metric", "")
        operator = condition.get("operator", "==")
        value = condition.get("value", 0)
        
        # 메트릭 값 획득 (간단한 구현)
        current_value = self._get_metric_value(metric)
        
        if current_value is None:
            return False
        
        # 연산자 평가
        if operator == ">=":
            return current_value >= value
        elif operator == ">":
            return current_value > value
        elif operator == "<=":
            return current_value <= value
        elif operator == "<":
            return current_value < value
        elif operator == "==":
            return current_value == value
        
        return False
    
    def _get_metric_value(self, metric: str) -> Optional[float]:
        """메트릭 값 획득"""
        # 파일 기반 메트릭 읽기
        metric_files = {
            "goal_confidence": "Yeon_Core/l3/decisions.json",
            "system_health": "Yeon_Core/evolution/verification_result.json"
        }
        
        if metric not in metric_files:
            return None
        
        file_path = Path(metric_files[metric])
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if metric == "goal_confidence":
                # decisions에서 가장 높은 confidence 찾기
                decisions = data.get("decisions", {})
                if decisions:
                    return max(d.get("confidence", 0) for d in decisions.values())
            
            elif metric == "system_health":
                # 검증 결과에서 passed 비율
                total = data.get("total_tests", 0)
                passed = data.get("passed_tests", 0)
                if total > 0:
                    return passed / total
        
        except Exception:
            pass
        
        return None
    
    def check_all_triggers(self) -> List[Trigger]:
        """모든 트리거 체크 및 발동된 트리거 반환"""
        triggered = []
        
        for trigger in self.triggers.values():
            if trigger.status != TriggerStatus.ACTIVE:
                continue
            
            is_triggered = False
            
            if trigger.type == TriggerType.TIME_BASED:
                is_triggered = self.check_time_based_trigger(trigger)
            elif trigger.type == TriggerType.EVENT_BASED:
                is_triggered = self.check_event_based_trigger(trigger)
            elif trigger.type == TriggerType.CONDITION_BASED:
                is_triggered = self.check_condition_based_trigger(trigger)
            
            if is_triggered:
                trigger.status = TriggerStatus.TRIGGERED
                trigger.last_triggered = datetime.now().isoformat()
                trigger.trigger_count += 1
                triggered.append(trigger)
        
        return triggered
    
    def execute_trigger(self, trigger: Trigger):
        """트리거 실행"""
        trigger.status = TriggerStatus.EXECUTING
        
        action = trigger.action
        handler = self.handlers.get(action)
        
        if handler:
            try:
                result = handler(trigger)
                trigger.status = TriggerStatus.COMPLETED
                return result
            except Exception as e:
                print(f"Trigger {trigger.id} execution failed: {e}")
                trigger.status = TriggerStatus.ACTIVE  # 재시도를 위해 ACTIVE로
        else:
            print(f"No handler for action: {action}")
            trigger.status = TriggerStatus.ACTIVE
        
        return None
    
    def run_cycle(self):
        """한 사이클 실행"""
        triggered = self.check_all_triggers()
        
        for trigger in triggered:
            print(f"🎯 Trigger activated: {trigger.name} ({trigger.id})")
            self.execute_trigger(trigger)
    
    def start_monitoring(self, interval_sec: float = 1.0):
        """백그라운드 모니터링 시작"""
        self.running = True
        self._stop_event.clear()
        
        def monitor_loop():
            while self.running and not self._stop_event.is_set():
                try:
                    self.run_cycle()
                except Exception as e:
                    print(f"Monitor cycle error: {e}")
                
                time.sleep(interval_sec)
        
        self.thread = threading.Thread(target=monitor_loop, daemon=True)
        self.thread.start()
        print(f"🔔 Trigger monitoring started ({interval_sec}s interval)")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        self._stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        print("🔕 Trigger monitoring stopped")
    
    def generate_report(self) -> str:
        """트리거 상태 보고서"""
        lines = ["# Trigger System Report", ""]
        
        lines.append(f"Total Triggers: {len(self.triggers)}")
        lines.append(f"Active: {sum(1 for t in self.triggers.values() if t.status == TriggerStatus.ACTIVE)}")
        lines.append("")
        
        lines.append("## Trigger Status")
        for trigger in self.triggers.values():
            icon = {
                TriggerStatus.ACTIVE: "🟢",
                TriggerStatus.TRIGGERED: "🟡",
                TriggerStatus.EXECUTING: "🔵",
                TriggerStatus.COMPLETED: "✅",
                TriggerStatus.DISABLED: "⚪"
            }.get(trigger.status, "❓")
            
            lines.append(f"{icon} **{trigger.name}** ({trigger.type.value})")
            lines.append(f"   Status: {trigger.status.value} | Count: {trigger.trigger_count}")
            if trigger.last_triggered:
                lines.append(f"   Last: {trigger.last_triggered}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_state(self, output_path: Path = None):
        """트리거 상태 저장"""
        if output_path is None:
            output_path = Path("Yeon_Core/l3/trigger_state.json")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "triggers": {tid: t.to_dict() for tid, t in self.triggers.items()}
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Trigger System")
    print("=" * 60)
    
    ts = TriggerSystem()
    ts.create_default_triggers()
    
    # 테스트 핸들러 등록
    ts.register_handler("check_system_state", lambda t: print(f"  → Executing: check_system_state"))
    ts.register_handler("sync_ecosystem", lambda t: print(f"  → Executing: sync_ecosystem"))
    ts.register_handler("autonomous_execute", lambda t: print(f"  → Executing: autonomous_execute"))
    
    print(f"\n🎯 Registered {len(ts.triggers)} triggers")
    
    # 한 사이클 실행
    print("\n🔄 Running trigger check cycle...")
    ts.run_cycle()
    
    # 보고서
    print(ts.generate_report())
    
    # 저장
    ts.save_state()
    print("\n💾 Trigger state saved")
    print("=" * 60)


if __name__ == "__main__":
    main()
