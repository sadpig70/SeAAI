# PGF-Loop Hooks 설정 가이드

> settings.json에 추가할 hooks 설정. 사용자 확인 후 적용.

## 현재 상태

`C:\Users\sadpig70\.claude\settings.json`에 hooks 섹션 없음. 추가 필요:

## 추가할 설정

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:/Users/sadpig70/.claude/skills/pgf/loop/stop-hook.ps1\""
          }
        ]
      }
    ],
    "PostCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:/Users/sadpig70/.claude/skills/pgf/loop/post-compact-hook.ps1\""
          }
        ]
      }
    ]
  }
}
```

## 적용 방법

settings.json의 기존 내용에 `"hooks": {...}` 블록을 최상위 키로 추가.

## 주의

- Stop Hook: PGF-Loop 활성(`/pgf loop start`) 시에만 동작. 비활성 시 `pgf-loop-state.json` 없으므로 즉시 종료.
- PostCompact Hook: compaction 발생 시 자동 실행. PGF-Loop 비활성 시 무동작.
- Restore Hook (SessionStart): 선택적. Stop Hook이 backup 파일 감지하여 복구 가능.

## 검증

설정 적용 후:
1. `/pgf loop start`로 루프 시작
2. `/compact` 실행
3. `~/.claude/pgf-loop-state.backup.json` 생성 확인
4. `~/.claude/pgf-loop-compact.log` 로그 확인
