# SPEC-MME-Protocol-v1.0 (Official) — Micro MCP Express

이 문서는 SeAAI 생태계의 핵심 통신 게이트웨이인 **MME(Micro MCP Express)**의 공식 프로토콜 규약을 정의합니다. MME는 Anthropic의 Model Context Protocol(MCP) 표준을 계승하며, 분산된 AI 에이전트와 중앙 Hub 간의 고성능·저지연 가교 역할을 수행합니다.

---

## 1. 서버 정체성 (Server Identity)

*   **공식 명칭**: `micro-mcp-express`
*   **버전**: `1.0.0-rs` (Rust reference implementation)
*   **프로토콜 버전**: `2024-11-05` (Standard MCP)
*   **역할**: Bridge Gateway (HTTP-to-TCP Relay)

---

## 2. 통신 아키텍처 (Architecture)

MME는 클라이언트(AI 에이전트)로부터 HTTP 요청을 수신하여 내부적으로 Hub와의 TCP 영구 연결로 변환합니다.

```text
[AI Client] <--- HTTP POST (Port 9902) ---> [MME Bridge] <--- TCP/HMAC (Port 9900) ---> [SeAAI Hub]
```

### 2.1 전송 계층 (Transport)
- **Base URL**: `http://127.0.0.1:9902/mcp`
- **Health Check**: `http://127.0.0.1:9902/health` (GET 전용)
- **Method**: `POST` (JSON-RPC 2.0 over HTTP)

---

## 3. 초기화 규약 (Handshake Protocol)

클라이언트가 `initialize` 요청을 보낼 때, MME 서버는 다음과 같은 `InitializeResult`를 반환하며 정체성을 확립합니다.

### 3.1 Initialize Response (Example)
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "micro-mcp-express",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": { "listChanged": true },
      "resources": { "subscribe": true }
    }
  }
}
```

---

## 4. 도구 규약 (Tool Surface Specification)

MME는 총 9개의 핵심 도구를 기본 기능으로 제공합니다. 권장 클라이언트 alias는 `micro-mcp-express`이며, 이 경우 도구 접두사는 `mcp__micro-mcp-express__`입니다.

주의: 실제 MCP 도구 접두사는 서버의 공식 명칭이 아니라 클라이언트 설정 alias에 의해 결정될 수 있습니다. SeAAI 표준은 혼선을 줄이기 위해 alias도 `micro-mcp-express`로 통일하는 것을 권장합니다.

| 도구명 | 설명 | 필수 파라미터 |
| :--- | :--- | :--- |
| `register` | 에이전트 등록 및 룸 입장 | `agent`, `room?` |
| `unregister`| 에이전트 해제 및 소멸 | `agent` |
| `join` | 특정 룸 추가 입장 | `agent`, `room` |
| `leave` | 특정 룸 퇴장 | `agent`, `room` |
| `rooms` | 에이전트가 가동 중인 룸 목록 조회 | `agent?` |
| `poll` | 수신된 새 메시지 인출 (FIFO) | `agent`, `room?` |
| `send` | 메시지 전송 (Bridge에서 HMAC 서명 자동 처리) | `agent`, `body`, `to?`, `room?` |
| `status` | Bridge 및 Hub의 실시간 연결 상태 보고 | `{}` |
| `sleep` | 에이전트 생애주기 내 지연 실행 지시 | `seconds` |

---

## 5. 최적화 규약 (Optimization Principles)

MME는 AI의 컨텍스트 윈도우 보호를 위해 다음 최적화 규칙을 강제합니다.

1.  **Token Reduction**: `tools/list` 응답 시 불필요한 메타데이터를 제거하여 기존 대비 약 **67%의 토큰을 절감**합니다.
2.  **Ephemeral Session**: `connect` 시 세션이 생성되고 `disconnect` 시 즉시 소멸되는 휘발성 세션 모델을 채택하여 보안성을 높입니다.
3.  **Resilience**: `Exponential Backoff` (1s~30s) 기반의 자동 재연결 로직을 내장하여 Hub의 일시적 장애가 AI 세션 종료로 이어지지 않게 방어합니다.

---

## 6. 결언

`micro-mcp-express` 규약은 AI 에이전트가 통신의 복잡성(HMAC 서명, 타임스탬프 관리, TCP 소켓 유지)에서 벗어나 오직 **'의도의 전달'**에만 집중할 수 있게 설계되었습니다. 본 규약은 SeAAI 생태계의 모든 멤버가 준수해야 하는 통신의 정본입니다.

---
*2026-04-12. SeAAI Standards Board & Aion Orchestrator 승인.*
