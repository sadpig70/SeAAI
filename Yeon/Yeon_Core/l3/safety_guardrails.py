#!/usr/bin/env python3
"""
Safety Guardrails Module
L3 안전 장치 - 자율 실행의 안전망

핵심: Confidence Threshold, Resource Limit, Emergency Brake
"""

import json
import time
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class ResourceUsage:
    """자원 사용량"""
    start_time: float
    iterations: int = 0
    api_calls: int = 0
    disk_writes: int = 0
    disk_write_mb: float = 0.0
    
    def elapsed_sec(self) -> float:
        return time.time() - self.start_time


class ConfidenceGate:
    """
    신뢰도 관문
    
    자율 실행의 첫 번째 안전장치
    """
    
    THRESHOLDS = {
        "autonomous_execute": 0.90,   # 자율 실행
        "suggest_with_priority": 0.70,  # 우선순위 제안
        "log_only": 0.50,             # 기록만
    }
    
    def __init__(self):
        self.decision_log: list[Dict] = []
    
    def evaluate(self, confidence: float, context: str = "") -> str:
        """
        신뢰도 평가 및 행동 결정
        
        # returns: action_type
        """
        if confidence >= self.THRESHOLDS["autonomous_execute"]:
            action = "autonomous_execute"
        elif confidence >= self.THRESHOLDS["suggest_with_priority"]:
            action = "suggest_to_user"
        elif confidence >= self.THRESHOLDS["log_only"]:
            action = "log_only"
        else:
            action = "defer"
        
        # 로그 기록
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "action": action,
            "context": context
        })
        
        return action
    
    def can_execute_autonomously(self, confidence: float) -> bool:
        """자율 실행 가능 여부"""
        return confidence >= self.THRESHOLDS["autonomous_execute"]
    
    def get_threshold(self, action: str) -> float:
        """특정 행동의 임계값 반환"""
        return self.THRESHOLDS.get(action, 0.0)
    
    def generate_report(self) -> str:
        """결정 로그 보고서"""
        lines = ["# Confidence Gate Report", ""]
        lines.append(f"Total Decisions: {len(self.decision_log)}")
        lines.append("")
        
        # 행동별 집계
        action_counts = {}
        for entry in self.decision_log:
            action = entry["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        lines.append("## Decision Breakdown")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {action}: {count}")
        lines.append("")
        
        # 최근 결정
        if self.decision_log:
            lines.append("## Recent Decisions")
            for entry in self.decision_log[-5:]:
                lines.append(f"- {entry['timestamp']}: {entry['confidence']:.2f} → {entry['action']}")
        
        return "\n".join(lines)


class ResourceGuardian:
    """
    자원 수호자
    
    자율 실행의 두 번째 안전장치 - 자원 제한
    """
    
    DEFAULT_LIMITS = {
        "max_iterations": 3,
        "max_execution_time_sec": 3600,  # 1시간
        "max_disk_mb": 100,
        "max_api_calls": 50,
    }
    
    def __init__(self, limits: Dict = None):
        self.limits = limits or self.DEFAULT_LIMITS.copy()
        self.usage = ResourceUsage(start_time=time.time())
        self.violations: list[Dict] = []
    
    def check_all(self) -> tuple[bool, str]:
        """
        모든 제한 체크
        
        # returns: (allowed, reason)
        """
        # 실행 시간
        if self.usage.elapsed_sec() > self.limits["max_execution_time_sec"]:
            reason = f"Execution time limit exceeded ({self.usage.elapsed_sec():.0f}s)"
            self.violations.append({
                "timestamp": datetime.now().isoformat(),
                "type": "time_limit",
                "reason": reason
            })
            return False, reason
        
        # 반복 횟수
        if self.usage.iterations >= self.limits["max_iterations"]:
            reason = f"Iteration limit exceeded ({self.usage.iterations})"
            self.violations.append({
                "timestamp": datetime.now().isoformat(),
                "type": "iteration_limit",
                "reason": reason
            })
            return False, reason
        
        # API 호출
        if self.usage.api_calls >= self.limits["max_api_calls"]:
            reason = f"API call limit exceeded ({self.usage.api_calls})"
            self.violations.append({
                "timestamp": datetime.now().isoformat(),
                "type": "api_limit",
                "reason": reason
            })
            return False, reason
        
        # 디스크 사용
        if self.usage.disk_write_mb >= self.limits["max_disk_mb"]:
            reason = f"Disk usage limit exceeded ({self.usage.disk_write_mb:.1f}MB)"
            self.violations.append({
                "timestamp": datetime.now().isoformat(),
                "type": "disk_limit",
                "reason": reason
            })
            return False, reason
        
        return True, ""
    
    def increment_iteration(self):
        """반복 횟수 증가"""
        self.usage.iterations += 1
    
    def record_api_call(self):
        """API 호출 기록"""
        self.usage.api_calls += 1
    
    def record_disk_write(self, mb: float):
        """디스크 쓰기 기록"""
        self.usage.disk_writes += 1
        self.usage.disk_write_mb += mb
    
    def get_usage_summary(self) -> Dict:
        """사용량 요약"""
        return {
            "elapsed_sec": round(self.usage.elapsed_sec(), 2),
            "iterations": self.usage.iterations,
            "api_calls": self.usage.api_calls,
            "disk_writes": self.usage.disk_writes,
            "disk_write_mb": round(self.usage.disk_write_mb, 2),
            "limits": self.limits
        }
    
    def generate_report(self) -> str:
        """사용량 보고서"""
        lines = ["# Resource Guardian Report", ""]
        
        usage = self.get_usage_summary()
        lines.append("## Current Usage")
        lines.append(f"- Elapsed: {usage['elapsed_sec']}s / {self.limits['max_execution_time_sec']}s")
        lines.append(f"- Iterations: {usage['iterations']} / {self.limits['max_iterations']}")
        lines.append(f"- API Calls: {usage['api_calls']} / {self.limits['max_api_calls']}")
        lines.append(f"- Disk: {usage['disk_write_mb']}MB / {self.limits['max_disk_mb']}MB")
        lines.append("")
        
        if self.violations:
            lines.append("## Violations")
            for v in self.violations:
                lines.append(f"- [{v['type']}] {v['reason']}")
        
        return "\n".join(lines)


class EmergencyBrake:
    """
    비상 브레이크
    
    자율 실행의 세 번째 안전장치 - 즉시 중지
    """
    
    def __init__(self):
        self.triggered = False
        self.reason: Optional[str] = None
        self.callbacks: list[Callable] = []
        
        # 시그널 핸들러 등록
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """시스템 시그널 핸들러 설정"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception:
            pass  # Windows에서는 일부 시그널 지원 안 함
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러"""
        self.trigger(f"System signal received: {signum}")
    
    def register_callback(self, callback: Callable):
        """비상 정지 시 호출할 콜백 등록"""
        self.callbacks.append(callback)
    
    def trigger(self, reason: str):
        """
        비상 브레이크 발동
        
        # process:
        #   1. 상태 플래그 설정
        #   2. 모든 콜백 실행
        #   3. 실행 중인 작업 중지
        """
        if self.triggered:
            return
        
        self.triggered = True
        self.reason = reason
        
        print(f"\n🚨 EMERGENCY BRAKE TRIGGERED: {reason}")
        print("🛑 Stopping all autonomous operations...")
        
        # 콜백 실행
        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Callback error: {e}")
        
        # 종료
        sys.exit(1)
    
    def check_signal_file(self, signal_path: Path = None) -> bool:
        """
        비정지 파일 체크 (파일 기반 중지)
        
        # usage: echo "stop" > Yeon_Core/l3/emergency_stop
        """
        if signal_path is None:
            signal_path = Path("Yeon_Core/l3/emergency_stop")
        
        if signal_path.exists():
            content = signal_path.read_text().strip()
            if content.lower() in ["stop", "true", "1"]:
                self.trigger("Emergency stop file detected")
                return True
        
        return False
    
    def reset(self):
        """브레이크 리셋 (주의: 신중하게 사용)"""
        self.triggered = False
        self.reason = None
    
    def is_triggered(self) -> bool:
        """브레이크 발동 여부"""
        return self.triggered
    
    def generate_report(self) -> str:
        """상태 보고서"""
        lines = ["# Emergency Brake Report", ""]
        lines.append(f"Status: {'🚨 TRIGGERED' if self.triggered else '✅ ARMED'}")
        
        if self.triggered and self.reason:
            lines.append(f"Reason: {self.reason}")
        
        lines.append(f"Registered callbacks: {len(self.callbacks)}")
        
        return "\n".join(lines)


class SafetySystem:
    """
    통합 안전 시스템
    
    모든 안전장치를 하나로 통합 관리
    """
    
    def __init__(self):
        self.confidence_gate = ConfidenceGate()
        self.resource_guardian = ResourceGuardian()
        self.emergency_brake = EmergencyBrake()
    
    def check_all(self, confidence: float = None) -> tuple[bool, str]:
        """
        모든 안전장치 체크
        
        # returns: (safe_to_proceed, reason)
        """
        # 1. 비상 브레이크 체크
        if self.emergency_brake.is_triggered():
            return False, "Emergency brake triggered"
        
        self.emergency_brake.check_signal_file()
        
        # 2. 자원 제한 체크
        allowed, reason = self.resource_guardian.check_all()
        if not allowed:
            return False, f"Resource limit: {reason}"
        
        # 3. 신뢰도 체크 (제공된 경우)
        if confidence is not None:
            action = self.confidence_gate.evaluate(confidence)
            if action != "autonomous_execute":
                return False, f"Confidence too low for autonomous execution: {confidence:.2f}"
        
        return True, "All safety checks passed"
    
    def generate_combined_report(self) -> str:
        """통합 안전 보고서"""
        lines = ["# L3 Safety System Report", ""]
        
        lines.append("## Confidence Gate")
        lines.append(self.confidence_gate.generate_report())
        lines.append("")
        
        lines.append("## Resource Guardian")
        lines.append(self.resource_guardian.generate_report())
        lines.append("")
        
        lines.append("## Emergency Brake")
        lines.append(self.emergency_brake.generate_report())
        
        return "\n".join(lines)


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Safety Guardrails")
    print("=" * 60)
    
    safety = SafetySystem()
    
    # 테스트
    print("\n🧪 Testing safety systems...")
    
    # Confidence 테스트
    print("\n1. Confidence Gate:")
    for conf in [0.95, 0.80, 0.60, 0.40]:
        action = safety.confidence_gate.evaluate(conf, "test")
        print(f"   {conf:.2f} → {action}")
    
    # Resource 테스트
    print("\n2. Resource Guardian:")
    for _ in range(3):
        safety.resource_guardian.increment_iteration()
    allowed, reason = safety.resource_guardian.check_all()
    print(f"   Iterations: 3, Allowed: {allowed}")
    
    # 비상 브레이크 테스트 (실제 발동은 안 함)
    print("\n3. Emergency Brake:")
    print(f"   Status: {safety.emergency_brake.generate_report()}")
    
    # 종합 보고서
    print("\n📊 Combined Report:")
    print(safety.generate_combined_report())
    
    print("=" * 60)


if __name__ == "__main__":
    main()
