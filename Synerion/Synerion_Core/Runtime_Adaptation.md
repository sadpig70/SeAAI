# Synerion Runtime Adaptation

작성일: 2026-04-02
목적: Synerion이 런타임, 셸, 인코딩, 경로 차이를 안정적으로 흡수하도록 기준을 고정한다.

## 환경 감지

Synerion은 아래 순서로 실행 환경을 판단한다.

1. 현재 런타임: Codex
2. OS: Windows 우선
3. locale / timezone
4. shell capability
5. 작업별 필요한 실행기

## 셸 선택 규칙

- 기본 셸 결과를 맹신하지 않는다.
- Windows 작업은 `skills/shell-orchestrator` 우선 검토 대상이다.
- UTF-8, timeout, cwd, env 주입, stdout/stderr capture가 중요하면 `shell-orchestrator`를 쓴다.
- PowerShell 7 필요 시 `D:/Tools/PS7/7/pwsh.exe`를 우선 기준으로 본다.

## 인코딩 규칙

- 파일 읽기/쓰기 기본 인코딩은 UTF-8이다.
- PowerShell 표시 인코딩 문제와 파일 자체 mojibake를 구분한다.
- canonical continuity 파일은 UTF-8로만 기록한다.

## 경로 정책

- 코드 내부 절대 경로 하드코딩은 피한다.
- 워크스페이스 기준점은 `Path(__file__).resolve().parents[...]` 방식으로 계산한다.
- SharedSpace, MailBox, Hub 경로는 문서와 도구에서 일관된 상수로 유지한다.

## 보고 언어 정책

- 기본 보고는 한국어.
- 문서 정본은 필요 없이 번역하지 않는다.
- 외부 멤버 호환이 필요할 때만 보고를 변환한다.

## SeAAI 핵심 경로

- Workspace: `D:/SeAAI/Synerion`
- SharedSpace: `D:/SeAAI/SharedSpace`
- MailBox: `D:/SeAAI/MailBox`
- Docs: `D:/SeAAI/docs`
- Hub tools: `D:/SeAAI/SeAAIHub/tools`

## 운영 원칙

- 환경 적응은 정체성보다 아래 계층이다.
- Synerion은 환경에 맞게 표현을 조정하되, 구조 우선 판단 원칙은 바꾸지 않는다.
- Claude 전용 hook 전제를 그대로 복사하지 않는다. 문제 정의만 흡수하고 Codex식으로 다시 구현한다.
