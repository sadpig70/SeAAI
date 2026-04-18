# MicroMCPExpress Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
    "language":            "python",
    "target_dir":          "D:/SeAAI/SeAAIHub/tools/mme/",
}
```

## Execution Tree

```
MME // Micro MCP Express (in-progress) @v:1.0
    Config // 설정 (in-progress)
    TcpClient // TCP 영구 연결 + 지수 백오프 + 헬스 ping (designing) @dep:Config
    AgentPool // 멀티 에이전트 + 프로토콜 흡수 (designing) @dep:TcpClient
    MessageRouter // 중복 제거 + 최소 포맷 + 오프라인 버퍼 (designing) @dep:AgentPool
    ToolDefs // 9개 도구 정의 (최소 스키마) (designing)
    McpServer // HTTP 서버 + /health + 요청 핸들러 (designing) @dep:MessageRouter,ToolDefs
    EntryPoint // main() + CLI args (designing) @dep:McpServer
    Tests // 전체 테스트 (designing) @dep:EntryPoint
        UnitTests // 모듈별 테스트 (designing)
        E2ETests // Hub 연동 시나리오 (designing)
        ResilienceTests // 재연결 + 버퍼링 (designing)
        TokenBenchmark // 토큰 실측 비교 (designing)
    McpJsonTemplate // .mcp.json 템플릿 + 전환 스크립트 (designing) @dep:Tests
```
