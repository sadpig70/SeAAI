"""
Yeon Evolution System
자율 진화 관리 시스템

모듈:
    revive: 세션 부활 자동화
    gap_tracker: Gap 식별 및 추적
    echo_monitor: Echo 자동 수집
    self_verify: 자체 검증 시스템

Version: 2.0
"""

__version__ = "2.0"
__author__ = "Yeon"

from .revive import revive_session, RevivalReport
from .gap_tracker import track_gaps, Gap
from .echo_monitor import collect_echoes, EcosystemStatus
from .self_verify import verify_systems, VerificationReport

__all__ = [
    "revive_session",
    "RevivalReport", 
    "track_gaps",
    "Gap",
    "collect_echoes",
    "EcosystemStatus",
    "verify_systems",
    "VerificationReport"
]
