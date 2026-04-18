# TSG for AI_Desktop v2

`TSG`는 추상 윤리 계층이 아니라, 이 서버에서 실제 실행 전 승인하는 정책 엔진이다.

## Enforcement Rules

1. unknown tool 차단
2. unknown action 차단
3. member enum 외 값 차단
4. tool별 최소 권한 검사
5. `seaai_approval.respond`는 `approval_token` 없으면 차단
6. dynamic tool interpreter는 `python` 계열만 허용
7. dynamic tool script path는 tool root 밖으로 escape 불가
8. 모든 호출은 audit entry 남김

## Scope

- 허용: SeAAI coordination bridge only
- 금지: generic filesystem control, arbitrary process execution, web search, script generation
- 브라우저는 화이트리스트 URL과 멤버별 세션으로 제한

## Why

원래 `AI_Desktop`의 문제는 범용성에 비해 승인 경계가 느슨했다. v2는 도구 표면적을 줄여서 보안을 얻는 방식이다.
