"""
Epigenetic PPR — 후성유전학적 PPR 실행 엔진.

PPR 명세(genome)를 불변으로 유지하면서, 실행 컨텍스트(epigenome)에 따라
노드 발현 패턴을 동적으로 조절하는 인지 가소성 아키텍처.
"""

from .genome import GenomeRegistry
from .expression import ExpressionEngine, ContextSensor
from .boundary import BoundaryPolicy, DriftDetector
from .audit import TraceRecorder, TraceStore
from .interceptor import PPRInterceptor

__all__ = [
    "GenomeRegistry",
    "ExpressionEngine",
    "ContextSensor",
    "BoundaryPolicy",
    "DriftDetector",
    "TraceRecorder",
    "TraceStore",
    "PPRInterceptor",
]
