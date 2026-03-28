# DESIGN — StabilityTest
# NAEL v0.3 전체 도구 안정성 테스트
# Author: NAEL | Date: 2026-03-25 | Mode: full-cycle

## POLICY
```
max_verify_cycles: 2
fail_action: log_and_continue  # 개별 실패가 전체를 중단시키지 않음
```

## Gantree

```
StabilityTest // NAEL v0.3 도구 안정성 전수 테스트
    AutomationTools // 자동화 도구 7개 기능 테스트
        TestSelfMonitor // self_monitor.py --scan, --report, --gaps
        TestTelemetry // telemetry.py --log, --query
        TestExperienceStore // experience_store.py --store, --search
        TestGuardrail // guardrail.py --checkpoint, --evaluate
        TestPerfMetrics // perf_metrics.py --record, --report
        TestScaffold // scaffold.py --list-templates
        TestOrchestrator // orchestrator.py --help (구조 확인)
    CognitiveTools // 인지 도구 7개 기능 테스트
        TestDebate // debate.py --topic "test" --mode quick
        TestSynthesizer // synthesizer.py --help (구조 확인)
        TestSelfImprover // self_improver.py --help
        TestChallenger // challenger.py --help
        TestHypothesis // hypothesis.py --help
        TestKnowledgeIndex // knowledge_index.py --scan
        TestSourceVerify // source_verify.py --help
    MCPServer // MCP 서버 기동 테스트
        TestMCPStartup // node index.js → 초기화 응답 확인
    InfraTools // SeAAIHub 인프라 도구 테스트
        TestHubBuild // cargo build + cargo test (완료)
        TestClientImport // seaai_hub_client.py import 테스트
        TestSentinelSyntax // sentinel-bridge.py 구문 (완료)
        TestADPLoopSyntax // adp-pgf-loop.py 구문 (완료)
    Report // 결과 종합 보고서
```
