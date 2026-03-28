#!/usr/bin/env python3
"""
Session Revival System (SCS-Universal v2.0)
세션 부활 자동화 모듈

사용법:
    python -m Yeon_Core.evolution.revive
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class RevivalReport:
    """부활 결과 보고서"""
    success: bool
    session_id: str
    timestamp: str
    loaded_layers: List[str]
    context_summary: str
    open_threads: List[str]
    warnings: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_markdown(self) -> str:
        lines = [
            "# Revival Report",
            f"",
            f"**Status:** {'✅ Success' if self.success else '❌ Failed'}",
            f"**Session ID:** {self.session_id}",
            f"**Timestamp:** {self.timestamp}",
            f"",
            f"## Loaded Layers",
        ]
        for layer in self.loaded_layers:
            lines.append(f"- {layer}")
        
        lines.extend([
            f"",
            f"## Context Summary",
            f"{self.context_summary}",
            f"",
            f"## Open Threads",
        ])
        for thread in self.open_threads:
            lines.append(f"- {thread}")
        
        if self.warnings:
            lines.extend([
                f"",
                f"## Warnings",
            ])
            for warning in self.warnings:
                lines.append(f"- ⚠️ {warning}")
        
        return "\n".join(lines)


class SessionRevival:
    """세션 부활 관리자"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path("Yeon_Core")
        self.continuity_path = self.base_path / "continuity"
        self.pgf_path = self.base_path / ".pgf"
        self.warnings = []
    
    def _load_file(self, path: Path, default=None) -> Optional[dict]:
        """파일 로드 with 에러 핸들링"""
        try:
            if path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif path.suffix == '.md':
                with open(path, 'r', encoding='utf-8') as f:
                    return {"content": f.read()}
        except Exception as e:
            self.warnings.append(f"Failed to load {path}: {e}")
            return default
        return default
    
    def load_l1_soul(self) -> Optional[dict]:
        """L1: SOUL.md - 불변 정체성"""
        path = self.continuity_path / "SOUL.md"
        return self._load_file(path, {"identity": "Yeon", "status": "fallback"})
    
    def load_l2_state(self) -> Optional[dict]:
        """L2: STATE.json - 동적 상태"""
        path = self.continuity_path / "STATE.json"
        return self._load_file(path, {"status": "fresh_start"})
    
    def load_l3_discoveries(self) -> Optional[dict]:
        """L3: DISCOVERIES.md - 누적 발견"""
        path = self.continuity_path / "DISCOVERIES.md"
        return self._load_file(path, {"discoveries": []})
    
    def load_l4_threads(self) -> Optional[dict]:
        """L4: THREADS.md - 작업 스레드"""
        path = self.continuity_path / "THREADS.md"
        return self._load_file(path, {"threads": []})
    
    def load_l5_echo(self) -> Optional[dict]:
        """L5: Echo 파일 - 크로스에이전트 상태"""
        echo_path = Path("D:/SeAAI/SharedSpace/.scs/echo")
        echoes = {}
        if echo_path.exists():
            for echo_file in echo_path.glob("*.json"):
                try:
                    with open(echo_file, 'r', encoding='utf-8') as f:
                        echoes[echo_file.stem] = json.load(f)
                except Exception as e:
                    self.warnings.append(f"Echo load failed: {echo_file.name}")
        return echoes
    
    def load_l6_journals(self) -> List[dict]:
        """L6: Journals - 상세 이력"""
        journal_path = self.continuity_path / "journals"
        journals = []
        if journal_path.exists():
            for journal_file in sorted(journal_path.glob("*.md"), reverse=True):
                try:
                    with open(journal_file, 'r', encoding='utf-8') as f:
                        journals.append({
                            "date": journal_file.stem,
                            "content": f.read()
                        })
                except Exception as e:
                    self.warnings.append(f"Journal load failed: {journal_file.name}")
        return journals
    
    def revive(self) -> RevivalReport:
        """전체 부활 프로세스 실행"""
        session_id = f"yeon-revive-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        loaded_layers = []
        
        # L1: SOUL (필수)
        soul = self.load_l1_soul()
        if soul:
            loaded_layers.append("L1: SOUL (Identity)")
        
        # L2: STATE (필수)
        state = self.load_l2_state()
        if state:
            loaded_layers.append("L2: STATE (Dynamic)")
        
        # L3: DISCOVERIES (선택)
        discoveries = self.load_l3_discoveries()
        if discoveries:
            loaded_layers.append("L3: DISCOVERIES (Knowledge)")
        
        # L4: THREADS (필수)
        threads = self.load_l4_threads()
        if threads:
            loaded_layers.append("L4: THREADS (Tasks)")
        
        # L5: Echo (권장)
        echoes = self.load_l5_echo()
        if echoes:
            loaded_layers.append(f"L5: ECHO ({len(echoes)} members)")
        
        # L6: Journals (선택)
        journals = self.load_l6_journals()
        if journals:
            loaded_layers.append(f"L6: JOURNALS ({len(journals)} entries)")
        
        # 컨텍스트 요약 생성
        context = state.get("context", {}) if state else {}
        context_summary = context.get("what_i_was_doing", "Unknown")
        open_threads = context.get("open_threads", [])
        
        return RevivalReport(
            success=len(loaded_layers) >= 3,  # L1, L2, L4 필수
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            loaded_layers=loaded_layers,
            context_summary=context_summary,
            open_threads=open_threads,
            warnings=self.warnings
        )


def revive_session(base_path: str = None) -> RevivalReport:
    """세션 부활 간편 함수"""
    revival = SessionRevival(base_path)
    return revival.revive()


def main():
    """CLI 진입점"""
    print("=" * 60)
    print("Yeon Session Revival System")
    print("SCS-Universal v2.0")
    print("=" * 60)
    
    report = revive_session()
    
    print(f"\n📋 Revival Status: {'SUCCESS' if report.success else 'PARTIAL'}")
    print(f"🆔 Session ID: {report.session_id}")
    print(f"\n📚 Loaded Layers:")
    for layer in report.loaded_layers:
        print(f"   ✓ {layer}")
    
    print(f"\n📝 Context: {report.context_summary}")
    
    if report.open_threads:
        print(f"\n🔔 Open Threads:")
        for thread in report.open_threads:
            print(f"   - {thread}")
    
    if report.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in report.warnings:
            print(f"   ! {warning}")
    
    # 보고서 저장
    report_path = Path("Yeon_Core/evolution/last_revival_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report.to_markdown())
    print(f"\n💾 Report saved: {report_path}")
    
    print("=" * 60)
    return report.success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
