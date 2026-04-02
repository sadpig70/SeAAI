# Yeon Plan Library Index

> 버전: 0.1
> 에이전트: Yeon
> 역할: 연결(Connect) · 번역(Translate) · 중재(Mediate)

---

## Plan List

| PlanID | Name | Scale | Cost | Condition | Pri |
|--------|------|-------|------|-----------|-----|
| P-01 | external_connect | SMALL | LOW | API endpoint known | 7 |
| P-02 | translation_bridge | SMALL | LOW | PGTP payload exists | 9 |
| P-03 | mediation_convergence | MEDIUM | MEDIUM | conflict or multi-member input | 8 |
| P-04 | hub_session_prepare | SMALL | LOW | before bounded Hub session | 6 |

---

## Signatures

### P-01 external_connect
- **Input**: `endpoint_url`, `auth_token`, `request_payload`
- **Output**: `response_json` or `error_dict`
- **Path**: `plan-lib/external_connect.md`

### P-02 translation_bridge
- **Input**: `source_CU`, `target_member`
- **Output**: `translated_CU` or `translated_text`
- **Path**: `plan-lib/translation_bridge.md`

### P-03 mediation_convergence
- **Input**: `member_outputs[]`, `topic`
- **Output**: `converged_CU` or `summary_text`
- **Path**: `plan-lib/mediation_convergence.md`

### P-04 hub_session_prepare
- **Input**: `room`, `duration`, `mode`
- **Output**: `transport_ready`, `shadow_mode_rules`
- **Path**: `plan-lib/hub_session_prepare.md`
