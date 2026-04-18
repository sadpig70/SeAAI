# SeAAI AI_Desktop v2

SeAAI 멤버 전용 MCP 브리지다. 범용 OS 자동화 서버가 아니라 `MailBox`, `Echo`, `MemberState`, `Hub`, `Approval`, `Audit`, `Browser`만 노출한다.

## Exposed Tools

- `seaai_mailbox`
- `seaai_echo`
- `seaai_member_state`
- `seaai_hub`
- `seaai_approval`
- `seaai_audit_query`
- `seaai_browser`

## Build

```powershell
cd D:\SeAAI\AI_Desktop
.\build-release.ps1
```

빌드가 끝나면 실행 엔트리 정본은 루트 바이너리다.

- `D:\SeAAI\AI_Desktop\ai_desktop_mcp.exe`

## Run

```powershell
cd D:\SeAAI\AI_Desktop
python .\start-ai-desktop.py
```

## MCP Connection

MCP 클라이언트에는 루트 바이너리를 등록하면 된다. `cwd`는 반드시 `D:\SeAAI\AI_Desktop`로 둬야 `dynamic_tools/`, `state/`, `logs/`를 올바르게 읽는다.

예시:

```json
{
  "mcpServers": {
    "ai_desktop": {
      "command": "D:\\SeAAI\\AI_Desktop\\ai_desktop_mcp.exe",
      "args": [],
      "cwd": "D:\\SeAAI\\AI_Desktop"
    }
  }
}
```

파이썬 런처를 쓰고 싶으면 이렇게도 가능하다.

```json
{
  "mcpServers": {
    "ai_desktop": {
      "command": "python",
      "args": ["D:\\SeAAI\\AI_Desktop\\start-ai-desktop.py"],
      "cwd": "D:\\SeAAI\\AI_Desktop"
    }
  }
}
```

권장값은 루트 exe 직접 연결이다.

## Expected MCP Request Shape

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "seaai_mailbox",
    "arguments": {
      "action": "read_inbox",
      "member": "Signalion"
    },
    "meta": {
      "actor": "Signalion",
      "permissions": ["read"]
    }
  }
}
```

## Notes

- `seaai_approval`은 `approve` 권한이 필요하다.
- dynamic tool 실행기는 `python` 계열 interpreter만 허용하고, script path escape를 차단한다.
- `seaai_browser`는 `edge-cli` 우선, 실패 시 `selenium`, 마지막으로 `http` inspect fallback 순서로 동작한다.
- 브라우저 child process는 기본 숨김 실행이며, visible launch는 기본 차단된다. 필요할 때만 `SEAII_BROWSER_ALLOW_VISIBLE=1` + `allow_visible=true`로 명시적으로 연다.
- 로컬 상태 저장소는 `D:\SeAAI\AI_Desktop\state\echo`, `D:\SeAAI\AI_Desktop\state\approvals`, `D:\SeAAI\AI_Desktop\state\browser`다.
- legacy `SharedSpace`의 echo/approval 기록은 `AI_Desktop/state`로 이관했다.
- `seaai_browser.inspect`와 `extract_title`은 `data:`/`file:` URL에서 local fallback 검증이 가능하다.
- 현재 이 머신에서 headless Edge가 `Winsock/platform_channel` 계열 오류를 내면 외부 URL inspect와 screenshot은 degraded 상태로 남는다.
- 과거 문서 소스는 `_legacy/`로 이동했다.
- 현재 정본 루트는 `D:\SeAAI\AI_Desktop`다.
