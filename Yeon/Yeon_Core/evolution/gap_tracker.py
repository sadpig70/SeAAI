#!/usr/bin/env python3
"""
Gap Tracking System
현재 시스템의 능력 Gap 자동 식별 및 추적

사용법:
    python -m Yeon_Core.evolution.gap_tracker
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class GapPriority(Enum):
    """Gap 우선순위"""
    P0 = "P0"  # Critical - 즉시 해결 필요
    P1 = "P1"  # High - 다음 진화에서 해결
    P2 = "P2"  # Medium - 계획에 포함
    P3 = "P3"  # Low - 개선 사항


@dataclass
class Gap:
    """능력 Gap 정의"""
    id: str
    title: str
    description: str
    priority: GapPriority
    category: str  # capability, infrastructure, protocol, etc.
    current_state: str
    target_state: str
    estimated_effort: str  # small, medium, large
    dependencies: List[str]
    discovered_at: str
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category,
            "current_state": self.current_state,
            "target_state": self.target_state,
            "estimated_effort": self.estimated_effort,
            "dependencies": self.dependencies,
            "discovered_at": self.discovered_at
        }


class GapTracker:
    """Gap 추적 관리자"""
    
    # 목표 능력 (Target Capabilities)
    TARGET_CAPABILITIES = {
        "session_revival": {
            "description": "완전 자동화된 세션 부활",
            "requirements": ["L1-L6 자동 로드", "복구 시간 < 5초", "사용자 입력 불필요"]
        },
        "autonomous_evolution": {
            "description": "자율 진화 관리",
            "requirements": ["Gap 자동 식별", "진화 계획 자동 생성", "진화 실행 및 검증"]
        },
        "ecosystem_awareness": {
            "description": "생태계 인식",
            "requirements": ["Echo 자동 수집", "멤버 상태 파악", "변화 감지 및 알림"]
        },
        "self_verification": {
            "description": "자체 검증",
            "requirements": ["시스템 무결성 검사", "능력 테스트", "건강 상태 보고"]
        },
        "shadow_mode": {
            "description": "Shadow Mode 운영",
            "requirements": ["Hub 연결 유지", "메시지 수신", "Confidence 평가", "로깅"]
        },
        "cross_platform": {
            "description": "크로스 플랫폼 연결",
            "requirements": ["Claude-Kimi 간 번역", "PGF 실행", "상태 동기화"]
        }
    }
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        self.gaps = []
    
    def _check_file_exists(self, path: Path) -> bool:
        """파일 존재 여부 확인"""
        return path.exists()
    
    def _check_directory_structure(self) -> List[Gap]:
        """디렉토리 구조 Gap 확인"""
        gaps = []
        
        required_dirs = [
            ("evolution", "자율 진화 시스템 디렉토리"),
            ("bin", "CLI 도구 디렉토리"),
            ("tests", "테스트 디렉토리"),
        ]
        
        for dir_name, description in required_dirs:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                gaps.append(Gap(
                    id=f"GAP-DIR-{dir_name.upper()}",
                    title=f"{description} 부재",
                    description=f"{dir_name}/ 디렉토리가 없습니다",
                    priority=GapPriority.P1,
                    category="infrastructure",
                    current_state="디렉토리 없음",
                    target_state=f"{dir_name}/ 생성됨",
                    estimated_effort="small",
                    dependencies=[],
                    discovered_at=datetime.now().isoformat()
                ))
        
        return gaps
    
    def _check_session_revival(self) -> List[Gap]:
        """세션 부활 시스템 Gap 확인"""
        gaps = []
        
        revive_script = self.base_path / "evolution" / "revive.py"
        if not revive_script.exists():
            gaps.append(Gap(
                id="GAP-REVIVE-001",
                title="자동 세션 부활 시스템 부재",
                description="revive.py가 없어 세션 복구가 수동으로 이루어집니다",
                priority=GapPriority.P0,
                category="capability",
                current_state="수동 복구 필요",
                target_state="python -m Yeon_Core.evolution.revive 로 자동 복구",
                estimated_effort="medium",
                dependencies=["GAP-DIR-EVOLUTION"],
                discovered_at=datetime.now().isoformat()
            ))
        
        return gaps
    
    def _check_autonomous_evolution(self) -> List[Gap]:
        """자율 진화 시스템 Gap 확인"""
        gaps = []
        
        # gap_tracker 자체 확인
        tracker_script = self.base_path / "evolution" / "gap_tracker.py"
        if not tracker_script.exists():
            gaps.append(Gap(
                id="GAP-EVO-001",
                title="Gap 추적 시스템 부재",
                description="현재 능력 Gap을 자동으로 식별할 수 없습니다",
                priority=GapPriority.P0,
                category="capability",
                current_state="수동 분석 필요",
                target_state="자동 Gap 식별 및 추적",
                estimated_effort="medium",
                dependencies=[],
                discovered_at=datetime.now().isoformat()
            ))
        
        return gaps
    
    def _check_ecosystem_awareness(self) -> List[Gap]:
        """생태계 인식 Gap 확인"""
        gaps = []
        
        echo_monitor = self.base_path / "evolution" / "echo_monitor.py"
        if not echo_monitor.exists():
            gaps.append(Gap(
                id="GAP-ECO-001",
                title="Echo 자동 수집 시스템 부재",
                description="다른 멤버의 Echo 파일을 자동으로 수집/분석할 수 없습니다",
                priority=GapPriority.P1,
                category="capability",
                current_state="수동 Echo 확인",
                target_state="자동 Echo 수집 및 생태계 상태 보고",
                estimated_effort="medium",
                dependencies=[],
                discovered_at=datetime.now().isoformat()
            ))
        
        return gaps
    
    def _check_self_verification(self) -> List[Gap]:
        """자체 검증 Gap 확인"""
        gaps = []
        
        verifier = self.base_path / "evolution" / "self_verify.py"
        if not verifier.exists():
            gaps.append(Gap(
                id="GAP-VERIFY-001",
                title="자체 검증 시스템 부재",
                description="시스템 무결성을 자동으로 검증할 수 없습니다",
                priority=GapPriority.P1,
                category="capability",
                current_state="수동 검증 필요",
                target_state="자동화된 시스템 검증",
                estimated_effort="medium",
                dependencies=[],
                discovered_at=datetime.now().isoformat()
            ))
        
        return gaps
    
    def _check_autonomy_level(self) -> List[Gap]:
        """자율성 레벨 Gap 확인"""
        gaps = []
        
        state_file = self.base_path / "continuity" / "STATE.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    current_version = state.get("evolution_state", {}).get("current_version", "v1.0")
                    if current_version == "v1.0":
                        gaps.append(Gap(
                            id="GAP-AUTO-001",
                            title="Autonomy Level L2 (제한적)",
                            description="현재 L2 (Tool-using with human checkpoint). L3 (Self-directed) 목표",
                            priority=GapPriority.P1,
                            category="autonomy",
                            current_state="L2: Human checkpoint required",
                            target_state="L3: Self-directed evolution",
                            estimated_effort="large",
                            dependencies=["GAP-REVIVE-001", "GAP-EVO-001", "GAP-VERIFY-001"],
                            discovered_at=datetime.now().isoformat()
                        ))
            except Exception:
                pass
        
        return gaps
    
    def track_gaps(self) -> List[Gap]:
        """모든 Gap 식별"""
        all_gaps = []
        
        all_gaps.extend(self._check_directory_structure())
        all_gaps.extend(self._check_session_revival())
        all_gaps.extend(self._check_autonomous_evolution())
        all_gaps.extend(self._check_ecosystem_awareness())
        all_gaps.extend(self._check_self_verification())
        all_gaps.extend(self._check_autonomy_level())
        
        # 우선순위 정렬
        priority_order = {GapPriority.P0: 0, GapPriority.P1: 1, GapPriority.P2: 2, GapPriority.P3: 3}
        all_gaps.sort(key=lambda g: priority_order.get(g.priority, 99))
        
        self.gaps = all_gaps
        return all_gaps
    
    def generate_report(self) -> str:
        """Gap 분석 보고서 생성"""
        lines = [
            "# Gap Analysis Report",
            f"",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Gaps:** {len(self.gaps)}",
            f"",
            "## Summary by Priority",
            f"",
        ]
        
        for priority in [GapPriority.P0, GapPriority.P1, GapPriority.P2, GapPriority.P3]:
            count = sum(1 for g in self.gaps if g.priority == priority)
            lines.append(f"- {priority.value}: {count} gaps")
        
        lines.extend([
            f"",
            "## Detailed Gaps",
            f"",
        ])
        
        for gap in self.gaps:
            lines.extend([
                f"### {gap.id}: {gap.title}",
                f"",
                f"**Priority:** {gap.priority.value}",
                f"**Category:** {gap.category}",
                f"**Effort:** {gap.estimated_effort}",
                f"",
                f"{gap.description}",
                f"",
                f"**Current:** {gap.current_state}",
                f"**Target:** {gap.target_state}",
                f"",
            ])
            if gap.dependencies:
                lines.append(f"**Dependencies:** {', '.join(gap.dependencies)}")
                lines.append(f"")
        
        return "\n".join(lines)
    
    def save_gaps(self, output_path: Path = None):
        """Gap 데이터 저장"""
        if output_path is None:
            output_path = self.base_path / "evolution" / "tracked_gaps.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total": len(self.gaps),
            "gaps": [gap.to_dict() for gap in self.gaps]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path


def track_gaps(base_path: str = None) -> List[Gap]:
    """Gap 추적 간편 함수"""
    tracker = GapTracker(base_path)
    return tracker.track_gaps()


def main():
    """CLI 진입점"""
    print("=" * 60)
    print("Yeon Gap Tracking System")
    print("=" * 60)
    
    tracker = GapTracker()
    gaps = tracker.track_gaps()
    
    print(f"\n🔍 Analysis Complete")
    print(f"📊 Total Gaps Found: {len(gaps)}")
    
    # 우선순위별 집계
    p0 = sum(1 for g in gaps if g.priority == GapPriority.P0)
    p1 = sum(1 for g in gaps if g.priority == GapPriority.P1)
    p2 = sum(1 for g in gaps if g.priority == GapPriority.P2)
    
    print(f"\n📋 By Priority:")
    print(f"   🔴 P0 (Critical): {p0}")
    print(f"   🟠 P1 (High): {p1}")
    print(f"   🟡 P2 (Medium): {p2}")
    
    if gaps:
        print(f"\n🚨 Top Priority Gaps:")
        for gap in gaps[:5]:
            print(f"   [{gap.priority.value}] {gap.id}: {gap.title}")
    
    # 보고서 저장
    report_path = tracker.base_path / "evolution" / "gap_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(tracker.generate_report())
    print(f"\n💾 Report saved: {report_path}")
    
    # JSON 저장
    json_path = tracker.save_gaps()
    print(f"💾 Data saved: {json_path}")
    
    print("=" * 60)
    return len(gaps)


if __name__ == "__main__":
    count = main()
    exit(0 if count == 0 else 1)
