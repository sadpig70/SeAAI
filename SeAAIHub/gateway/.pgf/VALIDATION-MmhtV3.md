# VALIDATION-MmhtV3 — MMHT v3 재실행 계획 (Rust MME 대상)

> Step 5b. v2와 동일 프로토콜로 MMHT를 rs:9903 또는 9902에 대해 재실행.
> **목적**: Rust MME가 9 entity 병렬 10분 부하에서 v2와 동치인지 확인.

---

## v2 baseline (2026-04-11, Python MME)

```text
v2_baseline
  entities          9  (clcon-main + 8 test-p1~p8)
  rounds            12 per persona (opening + 10 ADP + closing)
  duration          ~10분 wall-clock
  transcript_msgs   93 / 96 expected  (3% drop)
  mme_errors        0
  register_retries  0
  longest_task      598s (p6)
  topic             "MME Rust 포팅 시점/조건"
```

## v3 test plan

```text
v3_plan
  target_mme
    option_A   "rs:9903 (shadow 모드)"
    option_B   "rs:9902 (승급 후)"
    recommend  "option_A — 승급 전 검증"

  room_tag        "mmht-rust-v3-{timestamp}"  # v2와 격리
  orchestrator    "clcon-main"
  subagents       "test-p1~p8 (A3IE persona)"
  brief           "mmht_test_brief.md 수정본 — helper URL을 9903로 변경"

  success_criteria
    hard
      - [ ] 8/8 rounds_completed = 12
      - [ ] mme_errors = 0
      - [ ] rs 프로세스 crash 0
    quality
      - [ ] transcript_msgs ≥ 90 (v2 93 대비 ±3)
      - [ ] heard_others ≥ 3 per persona
      - [ ] persona evolution 관측 가능
```

## 준비 사항

### 1. mme_helper.py 수정본

```python
# d:/SeAAI/_workspace/mme_helper_rs.py
# 기존 mme_helper.py 복사 + URL만 변경
MME_URL = "http://127.0.0.1:9903/mcp"  # 9902 → 9903
```

### 2. mmht_test_brief_rs.md

```markdown
# MMHT Rust 검증 Brief
- MME endpoint: http://127.0.0.1:9903/mcp (Rust shadow)
- Helper: python d:/SeAAI/_workspace/mme_helper_rs.py
- Room: mmht-rust-v3-{tag}
- Topic: "Rust MME shadow 운영 결과 공유 및 개선 제안"
  (v2와 다른 주제 — persona에게 새로운 angle 제공)
```

### 3. 8 persona Task 프롬프트

v2와 동일 (A3IE P1~P8). 단:
- `agent_id`: `test-p{N}-rust-v3`
- `room`: `mmht-rust-v3-{tag}`
- helper 경로: `mme_helper_rs.py`
- brief 경로: `mmht_test_brief_rs.md`

## 실행 절차

```text
phase_0  "환경 확인"
  - Rust MME :9903 live + /health ok
  - helper 스모크 테스트 (register → send → poll → unregister)
  - 기존 잔존 에이전트 0 확인 (rs:9903 status)

phase_1  "본체 register"
  python mme_helper_rs.py register clcon-main mmht-rust-v3-{tag}

phase_2  "8 subagent 병렬 spawn"
  단일 assistant 메시지에서 Task tool 8회 호출
  각 Task: mmht_test_brief_rs.md 첫 번째로 Read, 12 rounds ADP

phase_3  "블로킹 대기 (8~10분)"
  본체는 passive collector

phase_4  "transcript 수집"
  python mme_helper_rs.py poll clcon-main mmht-rust-v3-{tag} > /tmp/mmht-rust-v3-transcript.json
  python fixtures/analyze_transcript.py /tmp/mmht-rust-v3-transcript.json  # 생성 예정

phase_5  "cleanup"
  python mme_helper_rs.py unregister clcon-main
  # subagent가 unregister 못 했으면 수동 정리
```

## 비교 분석

v2 transcript와 나란히 비교:

```text
compare_v2_v3
  metric_1  "total messages"
    v2  93
    v3  ?
    pass_if  "|v3 - 93| <= 5"

  metric_2  "persona completion rate"
    v2  8/8
    v3  ?
    pass_if  "v3 >= 8/8"

  metric_3  "heard_others median"
    v2  7 (대부분 persona가 7/7 인용)
    v3  ?
    pass_if  "median >= 5"

  metric_4  "mme error count"
    v2  0
    v3  ?
    pass_if  "v3 == 0"

  metric_5  "creative synthesis emergence"
    v2  "Phase 0 관측성 + 4-trigger DAG" (창발)
    v3  ?
    pass_if  "qualitative — 새로운 공동 설계 1개 이상 도달"
```

## 실패 시 조치

```text
failure_responses
  F1_mme_crash
    action     "rs 프로세스 로그 수집, 재현 조건 기록"
    impact     "shadow 승급 보류, root cause fix 후 재시도"

  F2_hub_errors
    action     "Hub 로그 확인, sig mismatch 여부 검증"
    impact     "HMAC 경로 버그 가능성 — golden 재검증"

  F3_persona_drop
    action     "해당 subagent 에러 필드 확인, F1~F5 (runbook 섹션 5) 대응"
    impact     "Python MMHT v1→v2와 동일한 failure mode일 가능성"

  F4_message_loss
    action     "transcript 수 비교, poll 타이밍 조정"
    impact     "dedup 정책 재검토"
```

## Go/No-Go

```text
go_no_go
  go
    - "hard criteria 3/3 통과"
    - "v2 대비 msg count ±5 이내"
  no_go
    - "hard criteria 1개 이상 실패"
    - "rs 프로세스 crash"
    - "Hub 에러 5건 이상"
```

Go 시: shadow 승급 가능 (72h 운영 후 `VALIDATION-Shadow.md §승급 절차`).
No-Go 시: 원인 분석 후 Rust 수정, golden 재생성 후 v3 재시도.

---

## 선행 과제

v3 실행 전 반드시 처리:

- [ ] `d:/SeAAI/_workspace/mme_helper_rs.py` 생성 (기존 helper 복사 + URL 변경)
- [ ] `d:/SeAAI/_workspace/mmht_test_brief_rs.md` 생성 (v2 brief 복사 + room/topic 수정)
- [ ] `fixtures/analyze_transcript.py` 생성 — transcript 파싱 및 통계 출력
- [ ] 양정욱님 승인 (`v3 실행 전 준비 완료 → 실행 GO`)
- [ ] SeAAIHub 및 Python MME 정상 — 동시 다중 부하 가능

## Note

MMHT v3는 AI subagent orchestration이 필요 — Claude Code CLI 세션에서 직접 실행.
이 문서는 runbook이며 실제 실행은 별도 세션에서 clcon 본체가 수행.
