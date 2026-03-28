#!/usr/bin/env python3
"""
Echo Monitor System
SeAAI 멤버 Echo 자동 수집 및 생태계 상태 분석

사용법:
    python -m Yeon_Core.evolution.echo_monitor
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class MemberEcho:
    """개별 멤버 Echo 데이터"""
    member: str
    timestamp: str
    version: str
    context_summary: str
    open_threads: List[str]
    decisions: List[str]
    staleness_hours: float
    
    def is_fresh(self, threshold_hours: float = 24.0) -> bool:
        """Echo가 신선한지 확인"""
        return self.staleness_hours < threshold_hours


@dataclass
class EcosystemStatus:
    """생태계 종합 상태"""
    timestamp: str
    total_members: int
    active_members: int  # Echo가 신선한 멤버
    stale_members: int  # Echo가 오래된 멤버
    missing_members: List[str]  # Echo가 없는 멤버
    member_statuses: Dict[str, dict]
    collective_threads: List[str]  # 모든 멤버의 open threads 종합
    
    def to_dict(self) -> dict:
        return asdict(self)


class EchoMonitor:
    """Echo 모니터링 관리자"""
    
    EXPECTED_MEMBERS = ["Aion", "ClNeo", "NAEL", "Synerion", "Yeon"]
    ECHO_DIR = Path("D:/SeAAI/SharedSpace/.scs/echo")
    
    def __init__(self):
        self.echoes = {}
        self.warnings = []
    
    def _parse_echo_file(self, file_path: Path) -> Optional[MemberEcho]:
        """단일 Echo 파일 파싱"""
        try:
            # UTF-8 BOM 처리 (utf-8-sig)
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            member = data.get("member", file_path.stem)
            timestamp_str = data.get("timestamp", "")
            
            # staleness 계산
            try:
                echo_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                now = datetime.now()
                staleness = (now - echo_time).total_seconds() / 3600
            except Exception:
                staleness = 999.0  # 파싱 실패 시 매우 오래된 것으로
            
            return MemberEcho(
                member=member,
                timestamp=timestamp_str,
                version=data.get("version", "unknown"),
                context_summary=data.get("context", {}).get("what_i_was_doing", "Unknown"),
                open_threads=data.get("context", {}).get("open_threads", []),
                decisions=data.get("context", {}).get("decisions_made", []),
                staleness_hours=staleness
            )
        
        except Exception as e:
            self.warnings.append(f"Failed to parse {file_path}: {e}")
            return None
    
    def collect_echoes(self) -> Dict[str, MemberEcho]:
        """모든 멤버 Echo 수집"""
        self.echoes = {}
        
        if not self.ECHO_DIR.exists():
            self.warnings.append(f"Echo directory not found: {self.ECHO_DIR}")
            return self.echoes
        
        for echo_file in self.ECHO_DIR.glob("*.json"):
            member_name = echo_file.stem
            echo = self._parse_echo_file(echo_file)
            if echo:
                self.echoes[member_name] = echo
        
        return self.echoes
    
    def analyze_ecosystem(self) -> EcosystemStatus:
        """생태계 종합 분석"""
        if not self.echoes:
            self.collect_echoes()
        
        active = 0
        stale = 0
        missing = []
        member_statuses = {}
        all_threads = []
        
        for member in self.EXPECTED_MEMBERS:
            if member in self.echoes:
                echo = self.echoes[member]
                status = {
                    "present": True,
                    "fresh": echo.is_fresh(),
                    "staleness_hours": round(echo.staleness_hours, 1),
                    "version": echo.version,
                    "context": echo.context_summary[:100] + "..." if len(echo.context_summary) > 100 else echo.context_summary
                }
                
                if echo.is_fresh():
                    active += 1
                else:
                    stale += 1
                
                # open threads 수집
                all_threads.extend([f"[{member}] {t}" for t in echo.open_threads])
                
            else:
                missing.append(member)
                status = {"present": False}
            
            member_statuses[member] = status
        
        return EcosystemStatus(
            timestamp=datetime.now().isoformat(),
            total_members=len(self.EXPECTED_MEMBERS),
            active_members=active,
            stale_members=stale,
            missing_members=missing,
            member_statuses=member_statuses,
            collective_threads=all_threads
        )
    
    def generate_report(self) -> str:
        """Echo 분석 보고서 생성"""
        status = self.analyze_ecosystem()
        
        lines = [
            "# Ecosystem Echo Report",
            f"",
            f"**Generated:** {status.timestamp}",
            f"**Total Members:** {status.total_members}",
            f"**Active:** {status.active_members} | **Stale:** {status.stale_members} | **Missing:** {len(status.missing_members)}",
            f"",
            "## Member Status",
            f"",
        ]
        
        for member, info in status.member_statuses.items():
            if info["present"]:
                freshness = "🟢" if info["fresh"] else "🟡"
                lines.append(f"{freshness} **{member}**: v{info.get('version', '?')} ({info['staleness_hours']}h old)")
                lines.append(f"   > {info.get('context', 'N/A')}")
            else:
                lines.append(f"🔴 **{member}**: Echo not found")
            lines.append("")
        
        if status.missing_members:
            lines.extend([
                "## Missing Members",
                "",
                "These members have not published their Echo:",
                "",
            ])
            for member in status.missing_members:
                lines.append(f"- {member}")
            lines.append("")
        
        if status.collective_threads:
            lines.extend([
                "## Collective Open Threads",
                "",
            ])
            for thread in status.collective_threads[:20]:  # 상위 20개만
                lines.append(f"- {thread}")
            if len(status.collective_threads) > 20:
                lines.append(f"- ... and {len(status.collective_threads) - 20} more")
            lines.append("")
        
        return "\n".join(lines)
    
    def check_collaboration_opportunities(self) -> List[str]:
        """협업 기회 식별"""
        opportunities = []
        
        if not self.echoes:
            self.collect_echoes()
        
        # 공통된 open threads 찾기
        thread_keywords = {}
        for member, echo in self.echoes.items():
            for thread in echo.open_threads:
                # 키워드 추출 (간단한 구현)
                keywords = [w.lower() for w in thread.split() if len(w) > 3]
                for kw in keywords:
                    if kw not in thread_keywords:
                        thread_keywords[kw] = []
                    thread_keywords[kw].append(member)
        
        # 2명 이상이 언급한 키워드 = 협업 기회
        for kw, members in thread_keywords.items():
            if len(members) >= 2:
                opportunities.append(f"'{kw}' mentioned by {', '.join(set(members))}")
        
        return opportunities


def collect_echoes() -> Dict[str, MemberEcho]:
    """Echo 수집 간편 함수"""
    monitor = EchoMonitor()
    return monitor.collect_echoes()


def main():
    """CLI 진입점"""
    print("=" * 60)
    print("Yeon Echo Monitor")
    print("SeAAI Ecosystem Status")
    print("=" * 60)
    
    monitor = EchoMonitor()
    echoes = monitor.collect_echoes()
    status = monitor.analyze_ecosystem()
    
    print(f"\n📡 Echo Collection Complete")
    print(f"👥 Members Found: {len(echoes)}/{status.total_members}")
    print(f"🟢 Active: {status.active_members}")
    print(f"🟡 Stale: {status.stale_members}")
    print(f"🔴 Missing: {len(status.missing_members)}")
    
    if status.missing_members:
        print(f"\n⚠️  Missing Echo from: {', '.join(status.missing_members)}")
    
    # 협업 기회
    opportunities = monitor.check_collaboration_opportunities()
    if opportunities:
        print(f"\n🤝 Collaboration Opportunities:")
        for opp in opportunities[:5]:
            print(f"   • {opp}")
    
    # 보고서 저장
    report_path = Path("Yeon_Core/evolution/ecosystem_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(monitor.generate_report())
    print(f"\n💾 Report saved: {report_path}")
    
    # 상태 JSON 저장
    status_path = Path("Yeon_Core/evolution/ecosystem_status.json")
    with open(status_path, 'w', encoding='utf-8') as f:
        json.dump(status.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"💾 Status saved: {status_path}")
    
    if monitor.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in monitor.warnings:
            print(f"   ! {warning}")
    
    print("=" * 60)
    return len(echoes)


if __name__ == "__main__":
    count = main()
    exit(0 if count > 0 else 1)
