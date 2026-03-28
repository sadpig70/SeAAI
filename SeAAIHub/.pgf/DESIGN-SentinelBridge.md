# DESIGN — SentinelBridge
# Bridge NPC: 두 에이전트 설계 통합 구현
# Mode: full-cycle | Author: NAEL | Date: 2026-03-24

## POLICY
```
max_verify_cycles: 2
test_command: "python -c \"import py_compile; py_compile.compile('D:/SeAAI/SeAAIHub/tools/sentinel-bridge.py', doraise=True)\""
```

## Gantree

```
SentinelBridge // Bridge NPC 통합 구현
    ImplementSentinel // sentinel-bridge.py 작성 @dep:none
        # 통합 PG 설계(DESIGN-Sentinel-NPC.pg.md) 기반
        # Types + Sense + Think + Act + Decide + Adapt + Exit + MainLoop
        # seaai_hub_client.py 재사용
        # criteria: python syntax OK, 모든 함수 구현
    TestSentinel // 구문 검증 + 단위 테스트 @dep:ImplementSentinel
        # criteria: py_compile 통과, 핵심 함수 단위 테스트
    UpdateDocs // 문서 갱신 @dep:TestSentinel
        # PG doc, Tech spec, ADP spec에 Sentinel 반영
        # criteria: sentinel-bridge.py 언급 확인
```
