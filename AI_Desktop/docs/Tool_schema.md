# AI Desktop Tool Schemas

## auto_tool_generator

- 설명: Generates skeleton code for new AI tools and wires them into the project
- Required Permissions: none (0)

```json
{
  "name": "auto_tool_generator",
  "description": "Generates skeleton code for a new AI Desktop tool and wires it into the project.",
  "parameters": {
    "type": "object",
    "properties": {
      "tool_name": {
        "type": "string",
        "description": "Base name for the tool (letters, numbers, underscores); used to derive file/module identifiers."
      }
    },
    "required": ["tool_name"]
  }
}
```

## file_manager_tool

- 설명: File system operations (read, write, list, move, delete, etc.)
- Required Permissions: READ | WRITE | EXECUTE

```json
{
  "name": "file_manager",
  "description": "Perform file system operations like reading, writing, listing, moving, and deleting files/directories.",
  "parameters": {
    "type": "object",
    "properties": {
      "op": {
        "type": "string",
        "enum": ["read", "write", "list", "move", "copy", "delete", "mkdir", "exists", "metadata"],
        "description": "Operation to perform"
      },
      "path": {
        "type": "string",
        "description": "Primary file/directory path"
      },
      "content": {
        "type": "string",
        "description": "Content for write operation"
      },
      "to_path": {
        "type": "string",
        "description": "Destination path for move/copy"
      }
    },
    "required": ["op", "path"]
  }
}
```

## network_api

- 설명: HTTP/TCP/DNS/ping diagnostics
- Required Permissions: none (0)

```json
{
  "name": "network_api",
  "description": "HTTP/TCP/DNS/ping/diagnostics; Windows extras (MVP).",
  "parameters": {
    "type": "object",
    "properties": {
      "op": {
        "type": "string",
        "enum": [
          "http_request",
          "http_head",
          "http_download",
          "tcp_request",
          "dns_query",
          "ping",
          "network_diagnostics",
          "win_http_request",
          "windows_auth",
          "firewall_control"
        ],
        "description": "실행할 네트워크 작업"
      },
      "url": {
        "type": "string",
        "description": "HTTP 요청 대상 URL (`http_request`, `http_head`, `http_download`, `win_http_request`)"
      },
      "method": {
        "type": "string",
        "description": "HTTP 메서드 (`http_request`, `win_http_request`)",
        "default": "GET"
      },
      "headers": {
        "type": "object",
        "description": "추가 HTTP 헤더(key/value 문자열)"
      },
      "body": {
        "description": "HTTP 요청 본문(문자열 또는 JSON 객체)"
      },
      "timeout_ms": {
        "type": "integer",
        "minimum": 1,
        "description": "요청 타임아웃(밀리초), 기본 30000"
      },
      "save_path": {
        "type": "string",
        "description": "`http_download`에서 저장할 로컬 경로"
      },
      "host": {
        "type": "string",
        "description": "`tcp_request` 대상 호스트"
      },
      "port": {
        "type": "integer",
        "minimum": 1,
        "maximum": 65535,
        "description": "`tcp_request` 포트"
      },
      "data": {
        "type": "string",
        "description": "`tcp_request`에서 전송할 데이터 문자열",
        "default": ""
      },
      "dns_name": {
        "type": "string",
        "description": "`dns_query` 대상 도메인"
      },
      "dns_type": {
        "type": "string",
        "enum": ["A", "AAAA"],
        "description": "DNS 레코드 타입(기본 A)"
      },
      "target": {
        "type": "string",
        "description": "`ping` 및 `network_diagnostics`에서 탐색할 대상 호스트/IP",
        "default": "127.0.0.1"
      },
      "diagnostic_type": {
        "type": "string",
        "description": "`network_diagnostics` 유형 (현재 port_scan만 지원)",
        "default": "port_scan"
      },
      "ports": {
        "type": "array",
        "items": { "type": "integer", "minimum": 1, "maximum": 65535 },
        "description": "`network_diagnostics` port_scan 시 확인할 포트 목록"
      },
      "windows-only": {
        "type": "object",
        "description": "`win_http_request`, `windows_auth`, `firewall_control` 등은 Windows에서만 성공"
      }
    },
    "required": ["op"],
    "allOf": [
      {
        "if": { "properties": { "op": { "enum": ["http_request", "http_head", "http_download", "win_http_request"] } } },
        "then": { "required": ["url"] }
      },
      {
        "if": { "properties": { "op": { "const": "http_download" } } },
        "then": { "required": ["save_path"] }
      },
      {
        "if": { "properties": { "op": { "const": "tcp_request" } } },
        "then": { "required": ["host", "port"] }
      },
      {
        "if": { "properties": { "op": { "const": "dns_query" } } },
        "then": { "required": ["dns_name"] }
      },
      {
        "if": { "properties": { "op": { "const": "ping" } } },
        "then": { "required": ["target"] }
      }
    ]
  }
}
```

## process_manager_tool

- 설명: Advanced process manager with TES/TSG integration
- Required Permissions: EXECUTE | ADMIN

```json
{
  "name": "process_manager",
  "description": "Advanced process manager with TES/TSG integration",
  "parameters": {
    "type": "object",
    "properties": {
      "op": {
        "type": "string",
        "enum": ["list", "inspect", "spawn", "wait", "kill", "close", "cpu_usage"],
        "description": "Operation to perform"
      },
      "pid": { "type": "integer", "description": "Target Process ID" },
      "pids": { "type": "array", "items": { "type": "integer" }, "description": "List of PIDs" },
      "name": { "type": "string", "description": "Process name filter" },
      "cmd": { "type": "string", "description": "Command line for spawn" },
      "args": { "type": "array", "items": { "type": "string" }, "description": "Arguments for spawn" },
      "timeout_ms": { "type": "integer", "description": "Wait timeout in milliseconds" }
    },
    "required": ["op"]
  }
}
```

## system_info

- 설명: Returns basic system information (OS, CPU, Memory).
- Required Permissions: READ

```json
{
  "name": "system_info",
  "description": "Returns basic system information (OS, CPU, Memory).",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

## web_search

- 설명: Bing/DuckDuckGo web search
- Required Permissions: EXECUTE

```json
{
  "name": "web_search",
  "description": "Performs a web search using supported providers.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search query" },
      "provider": { "type": "string", "enum": ["bing", "duckduckgo"], "default": "duckduckgo" },
      "count": { "type": "integer", "default": 10 }
    },
    "required": ["query"]
  }
}
```
