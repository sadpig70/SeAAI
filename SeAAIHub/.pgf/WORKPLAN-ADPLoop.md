# WORKPLAN — ADPLoop
# PGF Loop 기반 ADP — 순환 노드 무한 반복 + 시간 조건 종료
# Duration 파라미터로 수행 시간 제어

## POLICY
```
max_verify_cycles: 0
completion: all_done_or_blocked
on_blocked: skip
```

## Gantree

```
ADPLoop // PGF Loop 기반 ADP
    Watch // Sentinel 실행 → WakeReport 수신 (designing)
        # task: sentinel-bridge.py를 Bash로 실행하여 WakeReport JSON 수신
        # target: D:/SeAAI/SeAAIHub/tools/sentinel-bridge.py
        # params: --mode tcp --agent-id NAEL --room-id seaai-general --tick-min 8 --tick-max 10
        # output: WakeReport JSON (stdout)
        # criteria: WakeReport의 kind == "sentinel-wake"
    Process // WakeReport 분석 → 응답 → 루프 제어 (designing) @dep:Watch
        # task: WakeReport 분석, 필요시 outbox에 응답, 시간 체크 후 루프 제어
        # 시간 미경과: Watch와 Process의 status를 "designing"으로 리셋 → 루프 계속
        # 시간 경과: 둘 다 "done" → 루프 종료
        # criteria: status.json이 올바르게 갱신됨
```
