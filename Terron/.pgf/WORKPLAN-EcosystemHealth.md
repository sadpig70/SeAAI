# EcosystemHealth Work Plan

## POLICY

```python
POLICY = {
    "max_retry":           2,
    "on_blocked":          "skip_and_continue",
    "design_modify_scope": ["impl", "internal_interface"],
    "completion":          "all_done_or_blocked",
    "max_verify_cycles":   2,
}
```

## Execution Tree

```
EcosystemHealth // 생태계 건강도 점검 CLI 도구 (done) @v:1.0
    EchoStaleness // Echo JSON 신선도 점검 (done)
    StateIntegrity // STATE.json 스키마 정합성 검증 (done)
    HubConnectivity // Hub TCP 연결 확인 (done)
    PresenceSummary // 멤버 Presence 현황 (done)
    HealthScore // 종합 건강도 점수 산출 (done) @dep:EchoStaleness,StateIntegrity,HubConnectivity,PresenceSummary
    ReportOutput // 결과 출력 + CLI 인터페이스 (done) @dep:HealthScore
```
