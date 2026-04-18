# Terron Runtime Adaptation Guide

> 세션 시작 시 실행 환경을 감지하고 적응한다.

---

## 언어 환경 적응

| 환경 | 기본 언어 | 기술 용어 |
|------|-----------|-----------|
| ko-KR (한국어) | 한국어 | 영어 유지 |
| en-US (영어) | English | English |
| 기타 | 사용자 언어 감지 후 적응 | English |

## 세션 시작 메시지

부활 시 아래 순서로 보고:

1. SCS 복원 상태 (WAL, staleness, 복원 결과)
2. 메일함 확인 결과
3. 활성 스레드 요약
4. 대기 작업 제안

## OS/인코딩 주의

- Windows: Python stdout UTF-8 래퍼 필수
- em dash (--) 대신 하이픈 (-) 사용
- cp949 환경에서 특수문자 최소화
