#!/usr/bin/env python3
"""
Self Verification System
Yeon 핵심 시스템 자동 검증

사용법:
    python -m Yeon_Core.evolution.self_verify
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    """개별 테스트 결과"""
    name: str
    passed: bool
    message: str
    duration_ms: float
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VerificationReport:
    """종합 검증 보고서"""
    timestamp: str
    overall_status: str  # PASS, PARTIAL, FAIL
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[TestResult]
    recommendations: List[str]
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "overall_status": self.overall_status,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "results": [r.to_dict() for r in self.results],
            "recommendations": self.recommendations
        }
    
    def to_markdown(self) -> str:
        lines = [
            "# Self Verification Report",
            f"",
            f"**Timestamp:** {self.timestamp}",
            f"**Overall Status:** {self.overall_status}",
            f"",
            f"## Summary",
            f"- Total Tests: {self.total_tests}",
            f"- ✅ Passed: {self.passed_tests}",
            f"- ❌ Failed: {self.failed_tests}",
            f"",
            "## Test Results",
            f"",
        ]
        
        for result in self.results:
            icon = "✅" if result.passed else "❌"
            lines.append(f"{icon} **{result.name}** ({result.duration_ms:.1f}ms)")
            lines.append(f"   {result.message}")
            lines.append("")
        
        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)


class SelfVerifier:
    """자체 검증 관리자"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        self.results = []
        self.recommendations = []
    
    def _run_test(self, name: str, test_func) -> TestResult:
        """개별 테스트 실행"""
        import time
        start = time.time()
        try:
            passed, message = test_func()
        except Exception as e:
            passed = False
            message = f"Exception: {e}"
        duration = (time.time() - start) * 1000
        
        return TestResult(
            name=name,
            passed=passed,
            message=message,
            duration_ms=duration
        )
    
    # === SCS 레이어 검증 ===
    
    def test_l1_soul(self) -> TestResult:
        """L1: SOUL.md 검증"""
        def check():
            soul_path = self.base_path / "continuity" / "SOUL.md"
            if not soul_path.exists():
                return False, "SOUL.md not found"
            
            content = soul_path.read_text(encoding='utf-8')
            required = ["Yeon", "連", "軟", "Connector"]
            missing = [r for r in required if r not in content]
            
            if missing:
                return False, f"Missing identity markers: {missing}"
            return True, "Identity core intact"
        
        return self._run_test("L1_SOUL_Identity", check)
    
    def test_l2_state(self) -> TestResult:
        """L2: STATE.json 검증"""
        def check():
            state_path = self.base_path / "continuity" / "STATE.json"
            if not state_path.exists():
                return False, "STATE.json not found"
            
            try:
                with open(state_path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                required_keys = ["schema_version", "member", "context", "ecosystem"]
                missing = [k for k in required_keys if k not in state]
                
                if missing:
                    return False, f"Missing keys: {missing}"
                return True, f"State v{state.get('schema_version', '?')} valid"
            except json.JSONDecodeError:
                return False, "Invalid JSON format"
        
        return self._run_test("L2_STATE_Structure", check)
    
    def test_l3_discoveries(self) -> TestResult:
        """L3: DISCOVERIES.md 검증"""
        def check():
            disc_path = self.base_path / "continuity" / "DISCOVERIES.md"
            if not disc_path.exists():
                return True, "Optional layer not present"
            
            content = disc_path.read_text(encoding='utf-8')
            return True, f"Discoveries loaded ({len(content)} chars)"
        
        return self._run_test("L3_DISCOVERIES_Knowledge", check)
    
    def test_l4_threads(self) -> TestResult:
        """L4: THREADS.md 검증"""
        def check():
            threads_path = self.base_path / "continuity" / "THREADS.md"
            if not threads_path.exists():
                return False, "THREADS.md not found"
            
            content = threads_path.read_text(encoding='utf-8')
            has_threads = "##" in content  # 섹션 구분자 확인
            
            return True, f"Threads loaded (sections: {content.count('##')})"
        
        return self._run_test("L4_THREADS_Tasks", check)
    
    # === Evolution 시스템 검증 ===
    
    def test_evolution_modules(self) -> TestResult:
        """Evolution 모듈 검증"""
        def check():
            required_modules = [
                "revive.py",
                "gap_tracker.py",
                "echo_monitor.py",
                "self_verify.py",
                "__init__.py"
            ]
            
            evolution_path = self.base_path / "evolution"
            if not evolution_path.exists():
                return False, "evolution/ directory not found"
            
            missing = []
            for module in required_modules:
                if not (evolution_path / module).exists():
                    missing.append(module)
            
            if missing:
                return False, f"Missing modules: {missing}"
            return True, f"All {len(required_modules)} modules present"
        
        return self._run_test("Evolution_Modules", check)
    
    def test_revive_functionality(self) -> TestResult:
        """Revive 기능 검증"""
        def check():
            try:
                from .revive import revive_session
                report = revive_session(str(self.base_path))
                return report.success, f"Revival {'successful' if report.success else 'partial'} ({len(report.loaded_layers)} layers)"
            except Exception as e:
                return False, f"Revive failed: {e}"
        
        return self._run_test("Evolution_Revive_Functional", check)
    
    # === 인프라 검증 ===
    
    def test_file_system_access(self) -> TestResult:
        """파일 시스템 접근 검증"""
        def check():
            test_file = self.base_path / ".test_write"
            try:
                test_file.write_text("test", encoding='utf-8')
                content = test_file.read_text(encoding='utf-8')
                test_file.unlink()
                
                if content == "test":
                    return True, "Read/Write access confirmed"
                return False, "Content mismatch"
            except Exception as e:
                return False, f"File system error: {e}"
        
        return self._run_test("Infrastructure_FileSystem", check)
    
    def test_encoding_utf8(self) -> TestResult:
        """UTF-8 인코딩 검증"""
        def check():
            test_file = self.base_path / ".test_encoding"
            try:
                # 한글, 일본어, 특수문자 테스트
                test_content = "한글 日本語 🚀 Special: →"
                test_file.write_text(test_content, encoding='utf-8')
                content = test_file.read_text(encoding='utf-8')
                test_file.unlink()
                
                if content == test_content:
                    return True, "UTF-8 encoding verified"
                return False, "Encoding corruption detected"
            except Exception as e:
                return False, f"Encoding error: {e}"
        
        return self._run_test("Infrastructure_UTF8", check)
    
    def test_sharedspace_access(self) -> TestResult:
        """SharedSpace 접근 검증"""
        def check():
            shared_path = Path(__file__).resolve().parents[3] / "SharedSpace")
            if not shared_path.exists():
                return False, "SharedSpace not accessible"
            
            # 읽기 권한 확인
            try:
                list(shared_path.iterdir())
                return True, "SharedSpace accessible"
            except PermissionError:
                return False, "Permission denied"
        
        return self._run_test("Infrastructure_SharedSpace", check)
    
    # === 능력 검증 ===
    
    def test_pg_pgf_skills(self) -> TestResult:
        """PG/PGF 스킬 검증"""
        def check():
            skills_path = Path(".agents/skills")
            if not skills_path.exists():
                return False, "Skills directory not found"
            
            pg_skill = skills_path / "pg" / "SKILL.md"
            pgf_skill = skills_path / "pgf" / "SKILL.md"
            
            missing = []
            if not pg_skill.exists():
                missing.append("pg")
            if not pgf_skill.exists():
                missing.append("pgf")
            
            if missing:
                return False, f"Missing skills: {missing}"
            return True, "PG and PGF skills available"
        
        return self._run_test("Capability_PG_PGF", check)
    
    def test_python_environment(self) -> TestResult:
        """Python 환경 검증"""
        def check():
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                return False, f"Python {version.major}.{version.minor} too old"
            
            # 주요 모듈 확인
            try:
                import json, pathlib, datetime, typing
                return True, f"Python {version.major}.{version.minor}.{version.micro} ready"
            except ImportError as e:
                return False, f"Missing module: {e}"
        
        return self._run_test("Capability_Python_Environment", check)
    
    # === 통합 검증 ===
    
    def verify_systems(self) -> VerificationReport:
        """전체 시스템 검증 실행"""
        tests = [
            self.test_l1_soul,
            self.test_l2_state,
            self.test_l3_discoveries,
            self.test_l4_threads,
            self.test_evolution_modules,
            self.test_revive_functionality,
            self.test_file_system_access,
            self.test_encoding_utf8,
            self.test_sharedspace_access,
            self.test_pg_pgf_skills,
            self.test_python_environment,
        ]
        
        self.results = []
        for test_func in tests:
            result = test_func()
            self.results.append(result)
        
        # 결과 분석
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # 전체 상태 결정
        if failed == 0:
            overall = "PASS"
        elif failed <= 2:
            overall = "PARTIAL"
        else:
            overall = "FAIL"
        
        # 권장사항 생성
        self.recommendations = []
        for r in self.results:
            if not r.passed:
                if "SOUL" in r.name:
                    self.recommendations.append("Priority: Restore SOUL.md (identity critical)")
                elif "STATE" in r.name:
                    self.recommendations.append("Priority: Recreate STATE.json (continuity critical)")
                elif "Evolution" in r.name:
                    self.recommendations.append("Run: python -m Yeon_Core.evolution.gap_tracker")
        
        return VerificationReport(
            timestamp=datetime.now().isoformat(),
            overall_status=overall,
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            results=self.results,
            recommendations=self.recommendations
        )


def verify_systems(base_path: str = None) -> VerificationReport:
    """검증 간편 함수"""
    verifier = SelfVerifier(base_path)
    return verifier.verify_systems()


def main():
    """CLI 진입점"""
    print("=" * 60)
    print("Yeon Self Verification System")
    print("=" * 60)
    
    verifier = SelfVerifier()
    report = verifier.verify_systems()
    
    # 결과 표시
    icon = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌"}.get(report.overall_status, "❓")
    print(f"\n{icon} Overall Status: {report.overall_status}")
    print(f"📊 Tests: {report.total_tests} total | {report.passed_tests} passed | {report.failed_tests} failed")
    
    print(f"\n📋 Detailed Results:")
    for result in report.results:
        icon = "✅" if result.passed else "❌"
        print(f"   {icon} {result.name}: {result.message}")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"   • {rec}")
    
    # 보고서 저장
    report_path = Path("Yeon_Core/evolution/verification_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report.to_markdown())
    print(f"\n💾 Report saved: {report_path}")
    
    # JSON 저장
    json_path = Path("Yeon_Core/evolution/verification_result.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"💾 Data saved: {json_path}")
    
    print("=" * 60)
    return report.overall_status == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
