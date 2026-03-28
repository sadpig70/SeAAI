# DESIGN — ADP-LoopImpl
# /loop + Sentinel Bridge로 ADP 구현
# Mode: full-cycle | Author: NAEL | Date: 2026-03-25

## Gantree

```
ADP-LoopImpl // /loop + Sentinel으로 ADP 구현·문서·테스트
    WriteDoc // SeAAI/docs에 ADP-Loop 기술 문서 작성
        # criteria: /loop 메커니즘, Sentinel 연동, 비용 분석, 사용법 포함
    ImplementRunner // adp-runner.py — /loop에서 호출되는 경량 스크립트
        # Sentinel을 실행하고 WakeReport를 파싱하여 AI에게 반환
        # criteria: python syntax OK, WakeReport JSON 출력
    Test10Min // 10분 실제 ADP 동작 테스트
        # Hub 실행 → /loop 대신 수동 반복으로 10분 검증
        # criteria: 0 failure, WakeReport 유효, 세션 연속성
    VerifyAndReport // 검증 + 보고서 작성
        # criteria: 테스트 로그 분석, 문서 정합성 확인
```
