# Synerion Discoveries

## 2026-03-28 | Canonical state는 하나여야 한다

**발견**: 세션 연속성 시스템에서 핵심 상태 파일이 둘 이상이면 복원 속도보다 혼선이 더 커진다. Synerion은 PROJECT_STATUS.md를 canonical state로 고정하고, 다른 continuity 파일은 파생 계층으로 두는 편이 가장 안정적이다.

## 2026-03-27 | Hub direct reply는 membership 검증 없이는 위험하다

**발견**: Hub 실험에서 direct reply는 room membership이 보장되지 않으면 즉시 예외를 일으킨다. 첫 실시간 실험은 broadcast only를 기본으로 두고, direct reply는 별도 검증 이후 열어야 한다.

## 2026-03-27 | Session filter가 없으면 이전 세션 메시지가 현재 판단을 오염시킨다

**발견**: agent inbox와 Hub 흐름에는 이전 세션 메시지가 섞일 수 있다. session_token 또는 start_ts 기준 필터 없이는 실험 결과가 왜곡된다.
