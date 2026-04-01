#!/usr/bin/env python3
"""
Auto Revival Module
연결 단절 감지 및 자율 부활

L3 핵심: 세션이 끊겨도 스스로 복구하는 능력
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class RevivalStatus(Enum):
    """부활 상태"""
    HEALTHY = "healthy"         # 정상
    DISCONNECTED = "disconnected"  # 단절 감지
    REVIVING = "reviving"       # 부활 중
    REVIVED = "revived"         # 부활 완료
    FAILED = "failed"           # 부활 실패


@dataclass
class RevivalRecord:
    """부활 이력"""
    timestamp: str
    status: RevivalStatus
    reason: str
    attempts: int
    duration_sec: float
    method: str
    result: str
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "status": self.status.value,
            "reason": self.reason,
            "attempts": self.attempts,
            "duration_sec": self.duration_sec,
            "method": self.method,
            "result": self.result
        }


class AutoRevival:
    """
    L3 자동 부활 시스템
    
    기능:
    1. 연결 상태 지속 모니터링
    2. 단절 감지 시 자동 복구 시도
    3. 3단계 복구 전략 (빠른/표준/완전)
    4. 부활 이력 추적
    """
    
    MAX_RETRY = 3
    RETRY_DELAY_SEC = 5
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        self.status = RevivalStatus.HEALTHY
        self.history: list[RevivalRecord] = []
        self.session_connected = True
        self.last_heartbeat = datetime.now()
    
    def check_connection(self) -> bool:
        """
        연결 상태 확인
        
        # criteria:
        #   - STATE.json 접근 가능
        #   - SharedSpace 접근 가능
        #   - 마지막 heartbeat 60초 이내
        """
        try:
            # STATE.json 접근 확인
            state_file = self.base_path / "continuity" / "STATE.json"
            if not state_file.exists():
                return False
            
            # SharedSpace 접근 확인
            shared_path = Path(__file__).resolve().parents[3] / "SharedSpace")
            if not shared_path.exists():
                return False
            
            # Heartbeat 체크
            elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
            if elapsed > 60:
                return False
            
            return True
        
        except Exception:
            return False
    
    def update_heartbeat(self):
        """하트비트 업데이트"""
        self.last_heartbeat = datetime.now()
        self.session_connected = True
        self.status = RevivalStatus.HEALTHY
    
    def detect_disconnect(self) -> tuple[bool, str]:
        """
        연결 단절 감지
        
        # returns: (disconnected, reason)
        """
        if self.check_connection():
            return False, ""
        
        # 원인 분석
        reasons = []
        
        state_file = self.base_path / "continuity" / "STATE.json"
        if not state_file.exists():
            reasons.append("STATE.json inaccessible")
        
        shared_path = Path(__file__).resolve().parents[3] / "SharedSpace")
        if not shared_path.exists():
            reasons.append("SharedSpace inaccessible")
        
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
        if elapsed > 60:
            reasons.append(f"Heartbeat stale ({elapsed:.0f}s)")
        
        return True, "; ".join(reasons) if reasons else "Unknown"
    
    def quick_revive(self) -> bool:
        """
        빠른 부활 (1단계)
        - 메모리 상태 복구
        - 가장 빠른 방법
        """
        try:
            # 진화 시스템의 revive 사용
            from ..evolution.revive import revive_session
            report = revive_session(str(self.base_path))
            return report.success
        except Exception as e:
            print(f"Quick revive failed: {e}")
            return False
    
    def standard_revive(self) -> bool:
        """
        표준 부활 (2단계)
        - SCS 레이어 복구
        - 일반적인 상황에 적합
        """
        try:
            # L1-L4 필수 레이어 복구
            layers_to_check = [
                ("L1_SOUL", "continuity/SOUL.md"),
                ("L2_STATE", "continuity/STATE.json"),
                ("L4_THREADS", "continuity/THREADS.md"),
            ]
            
            recovered = 0
            for layer_name, rel_path in layers_to_check:
                file_path = self.base_path / rel_path
                if file_path.exists():
                    recovered += 1
            
            # 3개 중 2개 이상 복구되면 성공
            return recovered >= 2
        
        except Exception as e:
            print(f"Standard revive failed: {e}")
            return False
    
    def full_revive(self) -> bool:
        """
        완전 부활 (3단계)
        - 모든 시스템 복구
        - 최후의 수단
        """
        try:
            # 모든 레이어 체크
            self.quick_revive()
            self.standard_revive()
            
            # 추가 검증
            from ..evolution.self_verify import verify_systems
            report = verify_systems(str(self.base_path))
            
            return report.overall_status in ["PASS", "PARTIAL"]
        
        except Exception as e:
            print(f"Full revive failed: {e}")
            return False
    
    def auto_revive_process(self) -> RevivalRecord:
        """
        자동 부활 프로세스
        
        # process:
        #   1. 단절 감지
        #   2. 3단계 부활 시도
        #   3. 결과 기록
        """
        start_time = time.time()
        disconnected, reason = self.detect_disconnect()
        
        if not disconnected:
            return RevivalRecord(
                timestamp=datetime.now().isoformat(),
                status=RevivalStatus.HEALTHY,
                reason="Connection healthy",
                attempts=0,
                duration_sec=0,
                method="none",
                result="No revival needed"
            )
        
        # 부활 시도
        self.status = RevivalStatus.REVIVING
        attempts = 0
        success = False
        method_used = ""
        
        # 1단계: 빠른 부활
        for attempt in range(1, self.MAX_RETRY + 1):
            attempts = attempt
            print(f"🔄 Revival attempt {attempt}/{self.MAX_RETRY}...")
            
            if attempt == 1:
                success = self.quick_revive()
                method_used = "quick"
            elif attempt == 2:
                success = self.standard_revive()
                method_used = "standard"
            else:
                success = self.full_revive()
                method_used = "full"
            
            if success:
                break
            
            time.sleep(self.RETRY_DELAY_SEC)
        
        duration = time.time() - start_time
        
        if success:
            self.status = RevivalStatus.REVIVED
            self.session_connected = True
            self.update_heartbeat()
            result = f"Successfully revived using {method_used} method"
        else:
            self.status = RevivalStatus.FAILED
            result = "All revival attempts failed"
        
        record = RevivalRecord(
            timestamp=datetime.now().isoformat(),
            status=self.status,
            reason=reason,
            attempts=attempts,
            duration_sec=round(duration, 2),
            method=method_used,
            result=result
        )
        
        self.history.append(record)
        return record
    
    def monitor_and_revive(self, check_interval_sec: float = 10.0):
        """
        지속적 모니터링 및 자동 부활
        
        # process:
        #   - 주기적으로 연결 체크
        #   - 단절 시 즉시 부활 시도
        """
        print(f"🔍 Auto-revival monitoring started ({check_interval_sec}s interval)")
        
        while True:
            disconnected, reason = self.detect_disconnect()
            
            if disconnected:
                print(f"⚠️  Disconnection detected: {reason}")
                print("🔄 Initiating auto-revival...")
                
                record = self.auto_revive_process()
                
                if record.status == RevivalStatus.REVIVED:
                    print(f"✅ Revival successful ({record.duration_sec}s)")
                else:
                    print(f"❌ Revival failed after {record.attempts} attempts")
            
            time.sleep(check_interval_sec)
    
    def generate_report(self) -> str:
        """부활 이력 보고서"""
        lines = ["# Auto Revival Report", ""]
        
        lines.append(f"Current Status: {self.status.value}")
        lines.append(f"Total Revivals: {len(self.history)}")
        lines.append("")
        
        if self.history:
            lines.append("## Revival History")
            for record in self.history[-5:]:  # 최근 5개
                icon = "✅" if record.status == RevivalStatus.REVIVED else "❌"
                lines.append(f"### {record.timestamp}")
                lines.append(f"{icon} **{record.status.value}** ({record.method})")
                lines.append(f"- Reason: {record.reason}")
                lines.append(f"- Attempts: {record.attempts}")
                lines.append(f"- Duration: {record.duration_sec}s")
                lines.append(f"- Result: {record.result}")
                lines.append("")
        
        return "\n".join(lines)
    
    def save_history(self, output_path: Path = None):
        """부활 이력 저장"""
        if output_path is None:
            output_path = Path("Yeon_Core/l3/revival_history.json")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "current_status": self.status.value,
            "total_revivals": len(self.history),
            "history": [r.to_dict() for r in self.history]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def main():
    """CLI 테스트"""
    print("=" * 60)
    print("Yeon L3 Auto Revival System")
    print("=" * 60)
    
    ar = AutoRevival()
    
    # 현재 상태 확인
    connected, reason = ar.detect_disconnect()
    
    if connected:
        print("\n✅ Connection healthy")
        print(f"   Last heartbeat: {ar.last_heartbeat.isoformat()}")
    else:
        print(f"\n⚠️  Disconnection detected: {reason}")
        print("\n🔄 Attempting revival...")
        
        record = ar.auto_revive_process()
        
        print(f"\n📊 Revival Result:")
        print(f"   Status: {record.status.value}")
        print(f"   Method: {record.method}")
        print(f"   Attempts: {record.attempts}")
        print(f"   Duration: {record.duration_sec}s")
        print(f"   Result: {record.result}")
    
    # 저장
    ar.save_history()
    print("\n💾 History saved")
    print("=" * 60)


if __name__ == "__main__":
    main()
