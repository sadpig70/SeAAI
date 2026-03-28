# Epigenetic PPR Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           3,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
}
```

## Execution Tree

```
EpigeneticPPR // Epigenetic PPR 시스템 (설계중) @v:1.0
    GenomeLayer // 불변 PPR 명세 계층 (설계중)
        GenomeRegistry // PPR def 블록 등록 및 버전 관리 (설계중)
        GenomeValidator // genome 불변성 검증 (설계중) @dep:GenomeRegistry
        IntentFingerprint // 노드별 의도 해시 생성 (설계중) @dep:GenomeRegistry
    EpigenomeLayer // 컨텍스트 발현 계층 (설계중) @dep:GenomeLayer
        ContextSensor // 실행 컨텍스트 수집 (설계중)
            MemOSStateReader // MemOS 메모리 상태 읽기 (설계중)
            SessionContextReader // 세션/사용자/프로젝트 컨텍스트 (설계중)
            EnvironmentReader // 실행 환경 (시간, 부하, 이력) (설계중)
        ExpressionEngine // 발현 결정 엔진 (설계중) @dep:ContextSensor
            MethylationGate // 노드 실행 억제/허용 판정 (설계중)
            HistoneModifier // 실행 파라미터 가중치 조절 (설계중)
            ChromatinState // 노드 활성/휴면/억제 상태 관리 (설계중)
        ExpressionProfile // 발현 프로파일 관리 (설계중) @dep:ExpressionEngine
            ProfileStore // 컨텍스트별 발현 패턴 저장 (설계중)
            ProfileLearner // 실행 결과 피드백으로 프로파일 학습 (설계중)
            ProfileInheritance // 에이전트 간 발현 패턴 상속 (설계중)
    ExpressionBoundary // 발현 경계 메커니즘 (설계중)
        BoundaryPolicy // 허용 발현 범위 정의 (설계중)
        DriftDetector // 의도 이탈 감지 (설계중) @dep:BoundaryPolicy
        SafetyGuard // 위험 발현 차단 (설계중) @dep:DriftDetector
    AuditTrail // Decision Audit Trail 내장 (설계중)
        TraceRecorder // 발현 결정 추론 trace 기록 (설계중)
        TraceStore // 구조화된 trace 저장 (설계중) @dep:TraceRecorder
        TraceAnalyzer // trace 패턴 분석 및 요약 (설계중) @dep:TraceStore
    Integration // 기존 시스템 통합 (설계중) @dep:EpigenomeLayer,ExpressionBoundary,AuditTrail
        PGFLoopAdapter // PGF-Loop 엔진 연동 (설계중)
        MemOSBridge // MemOS 양방향 동기화 (설계중)
        PPRInterceptor // PPR 실행 전 epigenome 주입 (설계중) @dep:PGFLoopAdapter,MemOSBridge
```
