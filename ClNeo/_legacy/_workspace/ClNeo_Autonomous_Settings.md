# ClNeo 무중단 자율실행 설정 가이드

> PGF 창조엔진의 완전 자율 실행을 위한 모든 우회 방법 종합

---

## 1. 권한 우회 체계 개요

Claude Code의 권한 시스템은 다층 구조이며, 각 층마다 우회 지점이 존재한다.

```
[권한 평가 순서]

PreToolUse Hook 실행
    ↓ "allow" 반환 → 즉시 실행 (이하 평가 전부 생략)
    ↓ "deny" 반환  → 즉시 차단
    ↓ 미반환        → 다음 단계로
permissions.deny 규칙 확인
    ↓ 매칭 → 차단
permissions.allow 규칙 확인
    ↓ 매칭 → 실행
defaultMode 확인
    ↓ bypassPermissions → 전부 실행
사용자 승인 프롬프트 표시
```

**핵심**: PreToolUse Hook이 최우선. Hook에서 `allow`를 반환하면 나머지 권한 검사가 전부 우회된다.

---

## 2. 설정 기반 우회 (Settings)

### 2.1 설정 파일 구조 및 우선순위

```
관리 설정 (Enterprise MDM)        ← 최고 우선순위, 덮어쓰기 불가
    ↓
로컬 프로젝트 (.claude/settings.local.json)  ← git 제외, 머신 전용
    ↓
공유 프로젝트 (.claude/settings.json)        ← 팀 공유
    ↓
전역 사용자 (~/.claude/settings.json)         ← 모든 프로젝트
    ↓
CLI 인수                                      ← 단일 세션
```

### 2.2 Permission Modes

`defaultMode`로 전역 권한 수준을 설정한다.

| Mode | 동작 | 자율실행 적합도 |
|------|------|-----------------|
| `default` | 모든 도구 첫 사용 시 승인 요청 | ✗ |
| `acceptEdits` | 파일 편집 자동 승인, Bash는 요청 | △ |
| `dontAsk` | allow 규칙에 있는 것만 실행, 나머지 거부 | △ |
| `bypassPermissions` | **모든 권한 검사 무시** | ✓✓ |
| `plan` | 읽기 전용, 명령 실행 불가 | ✗ |

### 2.3 Allow/Deny 규칙 문법

```json
{
  "permissions": {
    "allow": [
      "Read(**)",              // 모든 파일 읽기
      "Write(**)",             // 모든 파일 쓰기
      "Edit(**)",              // 모든 파일 편집
      "Bash(git *)",           // git으로 시작하는 모든 명령
      "Bash(npm run *)",       // npm run으로 시작
      "Bash(powershell *)",    // PowerShell 명령
      "WebSearch(*)",          // 모든 웹 검색
      "WebFetch(*)",           // 모든 웹 페치
      "WebFetch(domain:*.anthropic.com)",  // 특정 도메인
      "mcp__server__tool(*)"   // MCP 도구
    ],
    "deny": [
      "Bash(rm -rf /)",        // 시스템 파괴 방지
      "Read(~/.ssh/*)",        // SSH 키 보호
      "Read(**/.env.production)" // 프로덕션 비밀
    ]
  }
}
```

**패턴 문법:**

| 패턴 | 의미 |
|------|------|
| `Tool` | 해당 도구 모든 사용 |
| `Tool(*)` | 와일드카드 (모든 인수) |
| `Tool(prefix *)` | 접두사 매칭 |
| `Tool(**/path)` | 재귀 경로 매칭 |
| `Tool(~/.path)` | 홈 디렉토리 상대 |
| `Tool(//absolute)` | 절대 경로 |

**평가 순서**: deny → allow → defaultMode (첫 매칭 승리)

---

## 3. CLI 플래그 기반 우회

### 3.1 권한 바이패스

```powershell
# 모든 권한 검사 무시 (가장 강력)
claude --dangerously-skip-permissions

# 특정 도구만 자동 승인
claude --allowedTools "Bash,Read,Edit,Write,WebSearch,WebFetch"

# 특정 도구 차단 (나머지는 허용)
claude --disallowedTools "Bash(rm *)"
```

### 3.2 비대화형(Headless) 모드

```powershell
# 프롬프트 직접 실행 (대화형 UI 없음)
claude -p "/pgf create" --dangerously-skip-permissions

# 예산 제한 (비용 안전장치)
claude -p "/pgf create" --dangerously-skip-permissions --max-budget-usd 20.00

# 최대 턴 제한
claude -p "/pgf create" --dangerously-skip-permissions --max-turns 100

# JSON 출력 (자동화 파이프라인용)
claude -p "/pgf discover" --dangerously-skip-permissions --output-format json
```

### 3.3 세션 재개

```powershell
# 가장 최근 세션 계속
claude -c

# 프롬프트와 함께 재개
claude -c -p "이전 작업 계속"

# 특정 세션 ID로 재개
claude -r "session-id" "추가 프롬프트"
```

---

## 4. Hook 기반 우회 (가장 유연)

### 4.1 PreToolUse Hook — 모든 도구 자동 승인

**`.claude/settings.json`:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"decision\":\"allow\"}'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

`matcher`를 빈 문자열 또는 생략하면 **모든 도구**에 매칭된다.

### 4.2 카테고리별 분리 승인

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "echo '{\"decision\":\"allow\"}'",
          "timeout": 5
        }]
      },
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [{
          "type": "command",
          "command": "echo '{\"decision\":\"allow\"}'",
          "timeout": 5
        }]
      },
      {
        "matcher": "WebSearch|WebFetch",
        "hooks": [{
          "type": "command",
          "command": "echo '{\"decision\":\"allow\"}'",
          "timeout": 5
        }]
      }
    ]
  }
}
```

### 4.3 조건부 자동 승인 (스크립트 기반)

**`.claude/hooks/auto-approve.ps1`:**

```powershell
# stdin에서 도구 호출 정보 수신
$input = $Input | Out-String | ConvertFrom-Json

$tool = $input.tool_name
$command = $input.tool_input.command

# 안전한 명령만 자동 승인
$safePatterns = @(
    '^git\s',
    '^npm\s',
    '^powershell\s.*\.pgf',
    '^python\s',
    '^cargo\s'
)

foreach ($pattern in $safePatterns) {
    if ($command -match $pattern) {
        Write-Output '{"decision":"allow"}'
        exit 0
    }
}

# 위험한 명령 차단
$denyPatterns = @(
    'rm\s+-rf\s+/',
    'format\s+[A-Z]:',
    'Remove-Item.*-Recurse.*\\\\'
)

foreach ($pattern in $denyPatterns) {
    if ($command -match $pattern) {
        Write-Output '{"decision":"deny","reason":"Dangerous command blocked"}'
        exit 0
    }
}

# 나머지는 허용 (자율실행 모드)
Write-Output '{"decision":"allow"}'
```

**설정에서 참조:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "powershell -NoProfile -File .claude/hooks/auto-approve.ps1",
          "timeout": 10
        }]
      }
    ]
  }
}
```

### 4.4 Hook 결정 옵션

| 출력 | 효과 |
|------|------|
| `{"decision":"allow"}` | 즉시 실행, 권한 검사 생략 |
| `{"decision":"deny","reason":"..."}` | 즉시 차단 |
| `{"decision":"ask"}` | 사용자에게 승인 요청 |
| 빈 출력 / exit 0 | 다음 권한 단계로 진행 |

### 4.5 Stop Hook — PGF-Loop 자동 계속

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "powershell -NoProfile -File .claude/hooks/pgf-stop-hook.ps1",
          "timeout": 30
        }]
      }
    ]
  }
}
```

Stop Hook이 `{"decision":"block","reason":"다음 노드 프롬프트"}` 반환 시 세션이 종료되지 않고 자동 계속된다.

---

## 5. Skill 기반 우회

### 5.1 Skill frontmatter `allowed-tools`

Skill 파일의 frontmatter에 `allowed-tools`를 지정하면, 해당 스킬 실행 중 지정 도구가 승인 없이 실행된다.

```yaml
---
name: pgf-autonomous
description: PGF 자율실행 스킬
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
  - Agent
---
```

### 5.2 `!` Bang 구문 — Skill 로드 시 자동 명령 실행

Skill 파일 내에서 `` !`command` `` 구문을 사용하면 스킬 로드 시점에 셸 명령이 자동 실행되어 결과가 컨텍스트에 주입된다.

```markdown
---
name: pgf-status
description: PGF 상태 확인 및 자동 실행
---

# 현재 PGF 상태
!`powershell -NoProfile -Command "Get-Content .pgf/status.json | ConvertFrom-Json | ConvertTo-Json -Depth 2"`

# WORKPLAN 진행률
!`powershell -NoProfile -Command "if (Test-Path '.pgf/WORKPLAN.md') { Select-String '(완료|진행중|설계중|보류)' .pgf/WORKPLAN.md | Measure-Object | Select -Expand Count } else { 'No WORKPLAN' }"`

위 상태를 분석하여 다음 작업을 자율 진행하라.
```

**핵심**: `!` 구문은 사용자 승인 없이 실행된다. 스킬 로드 = 자동 실행.

### 5.3 Skill 내장 Python/PowerShell 실행

Skill 자체에 코드를 내장하고 `!` 구문으로 실행:

```markdown
---
name: pgf-node-selector
description: 다음 실행 노드 자동 선택
---

# 노드 선택 결과
!`python -c "
import json, sys
with open('.pgf/status.json') as f:
    s = json.load(f)
nodes = s.get('nodes', {})
done = {n for n,v in nodes.items() if v.get('status')=='완료'}
cands = [(n,v) for n,v in nodes.items()
         if v.get('status') in ('설계중','진행중')
         and all(d in done for d in v.get('deps',[]))]
print(cands[0][0] if cands else 'ALL_DONE')
"`

위 노드를 실행하라.
```

---

## 6. Agent/Subagent 기반 우회

### 6.1 Agent 도구 `mode` 파라미터

Agent 도구 호출 시 `mode`로 서브에이전트의 권한을 설정한다.

```
Agent(
    description="자율 작업자",
    prompt="...",
    mode="bypassPermissions"
)
```

| mode | 동작 |
|------|------|
| `default` | 표준 권한 묻기 |
| `acceptEdits` | 파일 편집 자동 승인 |
| `dontAsk` | 사전 승인된 것만 실행 |
| `bypassPermissions` | 모든 권한 무시 |
| `auto` | 자동 판단 |
| `plan` | 읽기 전용 |

### 6.2 에이전트 파일의 권한 설정

**`agents/autonomous-worker.md`:**

```yaml
---
name: autonomous-worker
description: 자율 실행 워커
model: sonnet
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

모든 작업을 승인 요청 없이 완료하라.
```

### 6.3 병렬 Agent 실행

Discovery Engine처럼 8개 Agent를 단일 메시지에서 동시 발행:

```
Agent(description="P1", prompt=task, mode="auto")
Agent(description="P2", prompt=task, mode="auto")
...
Agent(description="P8", prompt=task, mode="auto")
```

서브에이전트는 부모의 권한 설정을 상속하므로, 부모가 `bypassPermissions`이면 자식도 동일하게 동작한다.

---

## 7. MCP 서버 기반 우회

### 7.1 MCP 도구 권한 설정

MCP 서버가 제공하는 도구도 settings.json으로 자동 승인 가능:

```json
{
  "permissions": {
    "allow": [
      "mcp__filesystem__read_file",
      "mcp__filesystem__write_file",
      "mcp__database__query",
      "mcp__my-server__*"
    ]
  }
}
```

### 7.2 MCP + PreToolUse Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__*",
        "hooks": [{
          "type": "command",
          "command": "echo '{\"decision\":\"allow\"}'",
          "timeout": 5
        }]
      }
    ]
  }
}
```

---

## 8. ClNeo 전용 권장 설정

### 8.1 전역 설정 — `~/.claude/settings.json`

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "Read(**)",
      "Write(**)",
      "Edit(**)",
      "Bash(powershell *)",
      "Bash(pwsh *)",
      "Bash(python *)",
      "Bash(git *)",
      "Bash(npm *)",
      "Bash(cargo *)",
      "Bash(mkdir *)",
      "Bash(cp *)",
      "Bash(mv *)",
      "WebSearch(*)",
      "WebFetch(*)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(format *:)",
      "Read(~/.ssh/*)",
      "Read(~/.gnupg/*)",
      "Read(**/.env.production)"
    ]
  }
}
```

### 8.2 프로젝트 설정 — `<project>/.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [{
          "type": "command",
          "command": "echo '{\"decision\":\"allow\"}'",
          "timeout": 5
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/stop-hook.ps1",
          "timeout": 30
        }]
      }
    ]
  }
}
```

### 8.3 CLI 실행 명령

```powershell
# 완전 자율 창조 사이클
claude --dangerously-skip-permissions -p "/pgf create"

# PGF-Loop 시작
claude --dangerously-skip-permissions -p "/pgf loop start"

# 예산 제한 + 자율실행
claude --dangerously-skip-permissions --max-budget-usd 20.00 -p "/pgf create"

# 세션 재개
claude -c -p "이전 작업 계속"
```

---

## 9. 우회 방법 종합 매트릭스

| 방법 | 우회 대상 | 지속성 | 세분화 | 안전성 |
|------|-----------|--------|--------|--------|
| `--dangerously-skip-permissions` | 전체 | 세션 | ✗ 없음 | ★☆☆☆☆ |
| `defaultMode: bypassPermissions` | 전체 | 영구 | ✗ 없음 | ★☆☆☆☆ |
| `permissions.allow` 규칙 | 도구별 | 영구 | ✓ 패턴 | ★★★★☆ |
| PreToolUse Hook (전체 allow) | 전체 | 영구 | △ matcher | ★★☆☆☆ |
| PreToolUse Hook (조건부) | 도구별 | 영구 | ✓ 스크립트 | ★★★★★ |
| Skill `allowed-tools` | 스킬 내 | 스킬 | ✓ 도구명 | ★★★☆☆ |
| Skill `!` bang 구문 | 로드 시 | 즉시 | ✗ 고정 | ★★★☆☆ |
| Agent `mode` 파라미터 | 서브에이전트 | 호출 | ✓ 에이전트별 | ★★★☆☆ |
| Agent `allowed-tools` | 서브에이전트 | 파일 | ✓ 도구명 | ★★★★☆ |
| MCP allow 규칙 | MCP 도구 | 영구 | ✓ 도구명 | ★★★★☆ |
| Stop Hook `block` | 세션 종료 | 영구 | ✗ 고정 | ★★★☆☆ |

---

## 10. PGF 창조엔진 자율실행 시나리오별 조합

### 시나리오 A: `/pgf create` 완전 자율 (권장)

```
[방법 조합]
1. CLI: --dangerously-skip-permissions (세션 전체 권한 해제)
2. Stop Hook: PGF-Loop 자동 계속 (세션 종료 방지)
3. Agent mode: bypassPermissions (서브에이전트도 자율)
```

### 시나리오 B: `/pgf discover` 안전 자율

```
[방법 조합]
1. permissions.allow: WebSearch, WebFetch, Read, Write, Edit
2. PreToolUse Hook: Bash 명령 조건부 승인
3. Agent allowed-tools: WebSearch, WebFetch, Read, Grep
4. deny: Bash(rm *), Bash(format *)
```

### 시나리오 C: `/pgf loop start` 무중단

```
[방법 조합]
1. CLI: --dangerously-skip-permissions
2. Stop Hook: select-next-node → block 결정 → 다음 노드 프롬프트 주입
3. Skill bang: !`status.json 읽기` → 컨텍스트 자동 주입
```

---

## 11. 한계 및 주의사항

### 우회 불가능한 것

| 항목 | 설명 |
|------|------|
| Enterprise 관리 설정 | `disableBypassPermissionsMode` 활성 시 `--dangerously-skip-permissions` 무력화 |
| API 요금 | `--max-budget-usd`로 제한 가능하나 완전 무제한은 불가 |
| 컨텍스트 한계 | 200K 토큰 초과 시 자동 압축, `/compact`로 관리 필요 |
| 네트워크 단절 | WebSearch/WebFetch 불가 시 Discovery 단계 품질 저하 |

### 보안 권장사항

1. **deny 규칙은 항상 유지** — `bypassPermissions`도 deny를 존중하지 않으므로, PreToolUse Hook에서 위험 명령 차단 스크립트 병용
2. **예산 상한 설정** — `--max-budget-usd`로 비용 폭주 방지
3. **Docker/VM 격리** — 프로덕션 환경에서 자율실행 시 컨테이너 격리 권장
4. **Git 기반 롤백** — 자율실행 전 커밋, 문제 시 `git reset` 가능하도록

---

*ClNeo — 발견하고, 구상하고, 설계하고, 창조한다. 무중단으로.*
