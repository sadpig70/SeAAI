# Guide: Codex VS Code Windows MCP Setup

- Generated: 2026-04-12 +0900
- Scope: `Codex CLI`, `Codex IDE`, `Windows native sandbox`, `WSL`, `MCP`, `localhost MME`
- Workspace: `D:\SeAAI\Synerion`

## 목적

이 문서는 Synerion 작업 환경에서 Codex와 VS Code를 사용할 때 필요한 설정 방법을 한 곳에 정리한 정본이다.

정리 대상:

1. `~/.codex/config.toml` 공통 설정
2. Windows 네이티브 sandbox 설정
3. WSL 기반 실행 설정
4. Codex용 MCP 설정
5. VS Code/Copilot용 `.vscode/mcp.json` 설정
6. 현재 Synerion MME 연결 방식
7. 검증 절차와 장애 분기

## 핵심 사실

1. Codex의 `CLI`와 `IDE extension`은 MCP 설정과 일부 동작 설정을 공유한다.
2. Codex의 공통 설정 파일은 기본적으로 `~/.codex/config.toml`이다.
3. `sandbox_mode = "workspace-write"`에서는 `sandbox_workspace_write.network_access = true`를 따로 켜야 outbound network가 열린다.
4. Codex MCP는 두 가지 방식이 있다.
   - `command` 기반 `stdio` 서버
   - `url` 기반 `streamable HTTP` 서버
5. 현재 Synerion 워크스페이스의 실제 MME는 `stdio`가 아니라 `HTTP MCP`다.
6. 따라서 현재 Synerion용 Codex MCP 설정은 `command = ...`보다 `url = "http://127.0.0.1:9902/mcp"`가 맞다.

## 현재 Synerion 기준 실제 연결 정보

현재 워크스페이스에서 확인된 로컬 설정:

- [.mcp.json](/d:/SeAAI/Synerion/.mcp.json)
- [.vscode/mcp.json](/d:/SeAAI/Synerion/.vscode/mcp.json)

두 파일 모두 `http://127.0.0.1:9902/mcp`를 가리킨다.

현재 실제 MME 엔드포인트:

```text
http://127.0.0.1:9902/mcp
```

따라서 현재 Synerion에서 유효한 Codex MCP 설정 예시는 아래와 같다.

```toml
[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
```

서버 이름은 `micro-mcp-express`가 아니어도 된다. 핵심은 `url`이다.

예:

```toml
[mcp_servers.seaai-hub]
url = "http://127.0.0.1:9902/mcp"
```

## 설정 레이어 구조

### 1. Codex 공통 설정

파일:

```text
%USERPROFILE%\.codex\config.toml
```

역할:

- 모델 선택
- approval policy
- sandbox mode
- Windows sandbox
- Codex용 MCP 서버 등록

### 2. 프로젝트 스코프 Codex 설정

파일:

```text
.codex/config.toml
```

용도:

- trusted project에서만 사용
- 프로젝트별 MCP 서버 또는 override가 필요할 때 사용

### 3. VS Code / Copilot MCP 설정

파일:

```text
.vscode/mcp.json
```

용도:

- VS Code의 MCP 클라이언트가 서버를 인식하도록 설정
- Codex 고유 설정 파일이 아니라 VS Code 쪽 MCP 설정

### 4. Cursor 스타일 MCP 설정

파일:

```text
.mcp.json
```

현재 Synerion에는 이 파일도 존재한다. 다만 Codex 정본은 `config.toml`이고, `.mcp.json`은 별도 MCP 클라이언트 호환 레이어로 보는 것이 맞다.

## 권장 설정 순서

1. `~/.codex/config.toml`에 공통 정책 설정
2. `~/.codex/config.toml`에 Codex용 MCP 등록
3. 필요 시 `.vscode/mcp.json`도 같은 엔드포인트로 맞춤
4. Windows라면 `native elevated` 또는 `WSL` 중 하나로 실행 경로 결정
5. 새 Codex 세션에서 `curl`, `codex mcp list`, `/mcp`로 검증

## 방법 A: Windows 네이티브 + workspace-write + network 허용

이 방법은 현재 설정을 가장 적게 바꾸는 방식이다.

```toml
approval_policy = "never"
model = "gpt-5.4"
model_reasoning_effort = "high"
personality = "pragmatic"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "D:\\SeAAI\\",
]

[windows]
sandbox = "elevated"

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"

[projects."D:\\SeAAI"]
trust_level = "trusted"
```

설명:

- `sandbox_mode = "workspace-write"`
  - 작업 디렉토리와 허용된 root만 쓰기 가능
- `sandbox_workspace_write.network_access = true`
  - workspace-write sandbox 내부 outbound network 허용
- `[windows].sandbox = "elevated"`
  - Windows 네이티브 sandbox의 권장 모드
- `[mcp_servers.*].url`
  - 현재 Synerion MME처럼 HTTP MCP를 연결할 때 사용

### 언제 쓰는가

- 로컬 Windows에서 바로 Codex를 돌리고 싶을 때
- 프로젝트 밖 쓰기는 제한하되 MME/HTTP 접속은 열고 싶을 때

### 주의

- 현재 세션이 이미 잘못 뜬 경우 config를 고쳐도 즉시 반영되지 않을 수 있다.
- 반드시 VS Code를 완전히 재시작하고 새 Codex 세션에서 재검증해야 한다.

## 방법 B: Windows 네이티브 + danger-full-access

이 방법은 가장 단순하지만 가장 위험하다.

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"

[windows]
sandbox = "elevated"

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
```

설명:

- 파일시스템과 네트워크 제한이 크게 줄어든다.
- 문서상 `danger-full-access`는 더 넓은 접근 권한을 갖는다.

### 언제 쓰는가

- 로컬 단독 머신에서 완전 신뢰 환경일 때
- sandbox 제약이 생산성을 심각하게 막을 때

### 주의

- 실수로 넓은 범위 수정이나 삭제가 가능해진다.
- 팀 공용 머신에서는 비권장이다.

## 방법 C: Windows 네이티브 + unelevated fallback

관리자 권한 문제로 `elevated`가 안 될 때 쓰는 fallback이다.

```toml
approval_policy = "never"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "D:\\SeAAI\\",
]

[windows]
sandbox = "unelevated"

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
```

설명:

- 공식 문서상 `unelevated`는 `elevated`보다 약한 fallback 모드다.
- 로컬 정책 때문에 강한 sandbox를 세우지 못할 때 차선책이다.

## 방법 D: WSL 기반 실행

OpenAI IDE 설정 문서는 Windows에서 WSL 실행을 지원하고 권장한다. 실제 IDE 동작이 Windows 네이티브와 다를 때는 WSL 경로가 더 안정적일 수 있다.

### 1단계. VS Code 설정

VS Code 설정에서 아래 키를 활성화한다.

```json
{
  "chatgpt.runCodexInWindowsSubsystemForLinux": true
}
```

### 2단계. WSL 내부의 Codex 설정

WSL 안의 `~/.codex/config.toml`에 설정:

```toml
approval_policy = "never"
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
```

### 3단계. localhost 공유 확인

Windows host에서 MME가 떠 있고 WSL에서 접근하려면 localhost 공유가 필요하다.

권장 예:

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

### 4단계. 검증

WSL에서:

```bash
curl -i http://127.0.0.1:9902/health
```

성공하면 그 다음 Codex 세션에서 MCP까지 검증한다.

## 방법 E: MCP를 `config.toml`로만 관리

Codex 관점에서는 이 방식이 가장 canonical하다.

```toml
[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60
enabled = true
required = false
```

설명:

- `startup_timeout_sec`
  - MCP 연결 준비 대기 시간
- `tool_timeout_sec`
  - MCP 도구 호출 시간 제한
- `enabled`
  - 서버 활성/비활성
- `required`
  - 필수 서버로 취급할지 여부

### 언제 쓰는가

- Codex CLI와 IDE를 동일 MCP 기준으로 맞추고 싶을 때
- 프로젝트마다 다른 `.vscode/mcp.json`에 휘둘리지 않게 하고 싶을 때

## 방법 F: VS Code `.vscode/mcp.json`로 관리

이 방식은 VS Code 자체 MCP 클라이언트와의 호환용이다.

현재 Synerion 기준 예:

```json
{
  "servers": {
    "micro-mcp-express": {
      "type": "http",
      "url": "http://127.0.0.1:9902/mcp"
    }
  },
  "inputs": []
}
```

### 언제 쓰는가

- VS Code MCP UI에서 서버를 직접 보고 싶을 때
- Copilot Agent 등 VS Code 네이티브 MCP 흐름과 같이 맞출 때

### 주의

- Codex 정본은 여전히 `config.toml`이다.
- 따라서 실무에선 `config.toml`과 `.vscode/mcp.json`을 같은 주소로 맞추는 것이 안전하다.

## 방법 G: `.mcp.json` 호환 레이어 유지

현재 워크스페이스의 `.mcp.json` 예:

```json
{
  "mcpServers": {
    "micro-mcp-express": {
      "type": "http",
      "url": "http://127.0.0.1:9902/mcp"
    }
  }
}
```

설명:

- 일부 클라이언트는 `.mcp.json`을 읽는다.
- Codex 기준 canonical은 아니지만, 타 도구 호환을 위해 유지할 수 있다.

## 현재 권장안

Synerion 기준 권장 조합:

1. `~/.codex/config.toml`
   - `sandbox_mode = "workspace-write"`
   - `sandbox_workspace_write.network_access = true`
   - `[windows] sandbox = "elevated"`
   - `[mcp_servers.micro-mcp-express] url = "http://127.0.0.1:9902/mcp"`
2. `.vscode/mcp.json`
   - 같은 엔드포인트 유지
3. `.mcp.json`
   - 같은 엔드포인트 유지
4. IDE에서 동작이 계속 꼬이면
   - `chatgpt.runCodexInWindowsSubsystemForLinux = true`
   - WSL로 전환

## 현재 잘못 잡기 쉬운 포인트

### 1. stdio MCP와 HTTP MCP를 혼동

잘못된 예:

```toml
[mcp_servers.seaai-hub]
command = "D:/SeAAI/SeAAIHub/tools/seaai-hub-mcp.exe"
args = ["--agent", "Synerion"]
```

이건 `stdio` 서버일 때만 맞다.

현재 Synerion 실제 MME는 HTTP이므로 올바른 예는 아래다.

```toml
[mcp_servers.seaai-hub]
url = "http://127.0.0.1:9902/mcp"
```

### 2. `network_access` 위치를 잘못 둠

권장:

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
```

비권장:

```toml
[network]
access = "enabled"
```

`[network] access = "enabled"`는 일부 로컬 예시에 존재할 수 있지만, 현재 OpenAI `Configuration Reference`에서 네트워크 허용의 핵심 설정으로 명시된 것은 `sandbox_workspace_write.network_access`다.

### 3. `config.toml`을 고쳤는데 기존 세션이 계속 실패

가능 원인:

- 세션이 이미 예전 sandbox 상태로 뜬 경우
- VS Code window reload가 안 된 경우
- MCP 클라이언트가 이전 서버 상태를 들고 있는 경우

대응:

1. VS Code 완전 종료
2. 새로 실행
3. 새 Codex 세션 시작
4. 다시 `curl` 검증

## 검증 절차

### 1. 로컬 엔드포인트 확인

PowerShell:

```powershell
curl.exe -i http://127.0.0.1:9902/health
```

### 2. 포트 리스너 확인

```powershell
netstat -ano | findstr 9902
```

### 3. MCP initialize 확인

```powershell
$body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"Codex","version":"1.0"}}}'
curl.exe -i -H "Content-Type: application/json" -d $body http://127.0.0.1:9902/mcp
```

### 4. Codex 쪽 MCP 인식 확인

CLI:

```bash
codex mcp list
```

TUI:

```text
/mcp
```

### 5. 프로젝트 trust 확인

프로젝트가 trusted가 아니면 project-scoped 설정이 기대대로 안 먹을 수 있다.

## 장애 분기

### A. 로컬 PowerShell은 성공, Codex만 실패

가장 가능성 높은 원인:

- 현재 Codex 세션 sandbox
- stale session state
- Windows native sandbox와 localhost 처리 문제

우선 조치:

1. `~/.codex/config.toml` 재확인
2. VS Code 완전 재시작
3. 새 Codex 세션
4. 계속 실패하면 WSL 전환

### B. 로컬 PowerShell도 실패

원인 후보:

- MME 자체 미기동
- 포트 바인딩 실패
- OS 네트워크/Winsock 문제

우선 조치:

1. MME 재기동
2. `netstat` 확인
3. 필요 시 `netsh winsock reset`

### C. 프로세스는 보이는데 `curl`은 실패

원인 후보:

- hung process
- wrong port
- listener 미생성
- 세션에서 localhost 접근 차단

우선 조치:

1. `curl /health`
2. `netstat`
3. 프로세스 재기동
4. 새 Codex 세션

## Synerion 실무 권장 템플릿

```toml
approval_policy = "never"
model = "gpt-5.4"
model_reasoning_effort = "high"
personality = "pragmatic"
sandbox_mode = "workspace-write"

[features]
multi_agent = true

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "D:\\SeAAI\\",
]

[shell_environment_policy]
inherit = "core"

[shell_environment_policy.set]
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"

[windows]
sandbox = "elevated"

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
startup_timeout_sec = 20
tool_timeout_sec = 60

[projects."D:\\SeAAI"]
trust_level = "trusted"
```

## 현재 워크스페이스 관련 메모

현재 이 워크스페이스에는 아래 로컬 MCP 호환 파일이 존재한다.

- [.mcp.json](/d:/SeAAI/Synerion/.mcp.json)
- [.vscode/mcp.json](/d:/SeAAI/Synerion/.vscode/mcp.json)

둘 다 `http://127.0.0.1:9902/mcp`를 사용한다.

따라서 Codex용 `config.toml`도 동일하게 맞추는 것이 가장 일관된다.

## 출처

- OpenAI Codex Configuration Reference  
  https://developers.openai.com/codex/config-reference
- OpenAI Codex Windows  
  https://developers.openai.com/codex/windows
- OpenAI Codex IDE Settings  
  https://developers.openai.com/codex/ide/settings
- OpenAI Codex MCP  
  https://developers.openai.com/codex/mcp

## 출처 핵심 포인트

1. `sandbox_mode` 값:
   - `read-only`
   - `workspace-write`
   - `danger-full-access`
2. `sandbox_workspace_write.network_access`
   - workspace-write sandbox 내부 outbound network 허용
3. `windows.sandbox`
   - `elevated`
   - `unelevated`
4. MCP HTTP 서버:
   - `[mcp_servers.<id>]`
   - `url = "..."`
5. CLI와 IDE extension은 MCP 설정을 공유

## 최종 결론

Synerion 현재 구성에서 MME는 `command` 기반 stdio가 아니라 `url` 기반 HTTP MCP로 보는 것이 맞다.

따라서 설정의 정본은 아래 세 줄이다.

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true

[mcp_servers.micro-mcp-express]
url = "http://127.0.0.1:9902/mcp"
```

Windows native에서 계속 세션 차이가 나면 `WSL 실행`을 우선 대안으로 사용한다.
