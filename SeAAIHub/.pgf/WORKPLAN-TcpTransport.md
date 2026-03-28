# WORKPLAN — SeAAIHub TCP Transport @v:1.0

## POLICY
- JSON-RPC 프로토콜 변경 없음. 전송 계층만 stdio → TCP 교체
- 기존 테스트 전부 통과 필수
- Router, chatroom, protocol 모듈 변경 최소화
- Bridge(Python)도 TCP 클라이언트로 전환
- 1분 실행 테스트로 검증

## Gantree

```text
TcpTransport // SeAAIHub stdio→TCP 전환 @v:1.0
    RustTcpListener // main.rs: TCP 서버 모드 추가 (in-progress)
        TransportTrait // transport.rs: Transport trait 추출 → Stdio/Tcp 구현
        TcpAcceptLoop // main.rs: TCP accept → 클라이언트별 독립 Router
        CliArgs // main.rs: --tcp-port 인자로 모드 선택 (stdio/tcp)
    PythonTcpClient // seaai_hub_client.py: socket 기반 HubClient
        TcpHubClient // subprocess.Popen → socket.connect
        BackwardCompat // --mode stdio|tcp 인자로 기존 호환 유지
    BridgeTcpMode // terminal-hub-bridge.py: hub spawn 대신 TCP 연결
        ConnectOnly // hub를 spawn하지 않고 TCP로 연결
        WrapperUpdate // start-terminal-bridge-watch.ps1: hub 별도 실행 지원
    VerifyTest // 1분 실행 테스트
        BuildRust // cargo build
        StartTcpHub // SeAAIHub.exe --tcp-port 9900 (백그라운드)
        RunBridge // bridge → TCP 연결 → 60초
        VerifyResult // state 검증
```
