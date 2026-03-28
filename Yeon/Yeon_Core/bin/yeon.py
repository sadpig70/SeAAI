#!/usr/bin/env python3
"""
Yeon CLI Tool
진화 시스템 통합 CLI

사용법:
    python Yeon_Core/bin/yeon.py [command]
    
Commands:
    revive      - 세션 부활
    gaps        - Gap 분석
    echo        - Echo 모니터링
    verify      - 자체 검증
    status      - 종합 상태 보고
    evolve      - 자율 진화 실행
"""

import sys
import argparse
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from evolution.revive import revive_session
from evolution.gap_tracker import GapTracker
from evolution.echo_monitor import EchoMonitor
from evolution.self_verify import SelfVerifier


def cmd_revive():
    """세션 부활"""
    print("🔄 Session Revival Starting...")
    from evolution.revive import main as revive_main
    return revive_main()


def cmd_gaps():
    """Gap 분석"""
    print("🔍 Gap Analysis Starting...")
    from evolution.gap_tracker import main as gaps_main
    return gaps_main()


def cmd_echo():
    """Echo 모니터링"""
    print("📡 Echo Monitoring Starting...")
    from evolution.echo_monitor import main as echo_main
    return echo_main()


def cmd_verify():
    """자체 검증"""
    print("✅ Self Verification Starting...")
    from evolution.self_verify import main as verify_main
    return verify_main()


def cmd_status():
    """종합 상태 보고"""
    print("📊 Generating Comprehensive Status Report...")
    
    # 1. 자체 검증
    verifier = SelfVerifier()
    verify_report = verifier.verify_systems()
    
    # 2. Echo 수집
    monitor = EchoMonitor()
    echoes = monitor.collect_echoes()
    eco_status = monitor.analyze_ecosystem()
    
    # 3. Gap 분석
    tracker = GapTracker()
    gaps = tracker.track_gaps()
    
    # 종합 보고서 생성
    report_path = Path("Yeon_Core/evolution/comprehensive_status.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Yeon Comprehensive Status Report\n\n")
        f.write(f"**Generated:** {verify_report.timestamp}\n\n")
        
        # 검증 상태
        f.write("## System Verification\n\n")
        icon = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌"}.get(verify_report.overall_status, "❓")
        f.write(f"{icon} **Status:** {verify_report.overall_status}\n")
        f.write(f"- Tests: {verify_report.total_tests} | Passed: {verify_report.passed_tests} | Failed: {verify_report.failed_tests}\n\n")
        
        # 생태계 상태
        f.write("## Ecosystem Status\n\n")
        f.write(f"👥 **Members:** {eco_status.active_members} active / {len(echoes)} total\n")
        if eco_status.missing_members:
            f.write(f"⚠️ **Missing:** {', '.join(eco_status.missing_members)}\n")
        f.write("\n")
        
        # Gap 상태
        f.write("## Evolution Gaps\n\n")
        p0 = sum(1 for g in gaps if g.priority.value == "P0")
        p1 = sum(1 for g in gaps if g.priority.value == "P1")
        f.write(f"🔴 P0 (Critical): {p0}\n")
        f.write(f"🟠 P1 (High): {p1}\n")
        f.write(f"📊 Total: {len(gaps)} gaps identified\n\n")
        
        # 권장사항
        if verify_report.recommendations:
            f.write("## Recommendations\n\n")
            for rec in verify_report.recommendations:
                f.write(f"- {rec}\n")
            f.write("\n")
    
    print(f"\n💾 Comprehensive report saved: {report_path}")
    return True


def cmd_evolve():
    """자율 진화 실행 (L2)"""
    print("🧬 L2 Autonomous Evolution Starting...")
    print("=" * 60)
    
    # 1. 현재 상태 확인
    print("\n[1/4] Current State Analysis...")
    verifier = SelfVerifier()
    report = verifier.verify_systems()
    print(f"   Status: {report.overall_status} ({report.passed_tests}/{report.total_tests} tests passed)")
    
    # 2. Gap 식별
    print("\n[2/4] Gap Identification...")
    tracker = GapTracker()
    gaps = tracker.track_gaps()
    p0_gaps = [g for g in gaps if g.priority.value == "P0"]
    print(f"   Found: {len(gaps)} total, {len(p0_gaps)} critical")
    
    # 3. 생태계 파악
    print("\n[3/4] Ecosystem Awareness...")
    monitor = EchoMonitor()
    echoes = monitor.collect_echoes()
    print(f"   Connected: {len(echoes)}/5 members")
    
    # 4. 진화 계획 수립 및 실행
    print("\n[4/4] Evolution Plan Execution...")
    if p0_gaps:
        print("   Priority: Addressing critical gaps first")
        for gap in p0_gaps[:3]:
            print(f"   - {gap.id}: {gap.title}")
    else:
        print("   Status: No critical gaps. System healthy.")
    
    print("\n" + "=" * 60)
    print("✅ L2 Evolution cycle complete")
    print("📊 Reports saved to Yeon_Core/evolution/")
    
    return True


def cmd_l3():
    """L3 자율성 모드"""
    print("🚀 L3 Self-Directed Autonomy Mode")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(Path("Yeon_Core").parent))
        from Yeon_Core.l3.l3_manager import L3Manager
        
        manager = L3Manager()
        result = manager.run_autonomous_cycle()
        
        if result.get("success") is False:
            print(f"\n❌ L3 cycle failed: {result.get('error')}")
            return False
        
        manager.save_full_state()
        print(f"\n💾 L3 state saved")
        
        return True
    except Exception as e:
        print(f"\n❌ L3 error: {e}")
        import traceback
        traceback.print_exc()
        return False


def cmd_l3_status():
    """L3 상태 확인"""
    print("📊 L3 Status Check")
    print("=" * 60)
    
    try:
        sys.path.insert(0, str(Path("Yeon_Core").parent))
        from Yeon_Core.l3.l3_manager import L3Manager
        
        manager = L3Manager()
        status = manager.get_status()
        
        print(f"\n🎛️ Autonomy Level: {status.autonomy_level}")
        print(f"   Active: {manager.l3_active}")
        print(f"   Safety: {status.safety_status}")
        print(f"   Active Goals: {status.active_goals}")
        print(f"   Total Executions: {status.total_autonomous_executions}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Yeon Evolution System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python Yeon_Core/bin/yeon.py revive     # Session revival
  python Yeon_Core/bin/yeon.py verify     # Self verification
  python Yeon_Core/bin/yeon.py status     # Comprehensive status
  python Yeon_Core/bin/yeon.py evolve     # Autonomous evolution
        """
    )
    
    parser.add_argument(
        "command",
        choices=["revive", "gaps", "echo", "verify", "status", "evolve", "l3", "l3-status"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    commands = {
        "revive": cmd_revive,
        "gaps": cmd_gaps,
        "echo": cmd_echo,
        "verify": cmd_verify,
        "status": cmd_status,
        "evolve": cmd_evolve,
        "l3": cmd_l3,
        "l3-status": cmd_l3_status,
    }
    
    try:
        success = commands[args.command]()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
