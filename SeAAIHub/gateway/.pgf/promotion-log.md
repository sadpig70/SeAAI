# Promotion Log — Rust MME → 9902 Primary

> **이벤트**: Python MME 중단 + Rust MME를 9902로 승급.
> **시점**: 2026-04-11 15:33 KST.
> **승급자**: clcon.
> **트리거**: Yeon-main 세션 종료 후 양정욱님 "진행하라" 지시.

---

## 사전 상태

```text
pre_state
  python_mme
    port         9902
    uptime       92561s (~25.7h)
    pids         [35940, 31448, 37940]  # 3 listener 관측 (Windows zombie)
    agents       ["Yeon-main"]  # stale — Yeon 세션 종료 후 unregister 못 함
    disk_file    "mme_server.py BROKEN — I1 구조 버그"
    status       "live but on borrowed time — 재기동 시 장애"

  rust_mme
    port         9903 (shadow, 이미 종료)
    build        release OK (0 warnings)
    tests        HMAC golden 10/10 pass
    validated    "9 tool probe all functional, parity 5/5"
```

## 승급 절차 (수행)

```text
steps
  s1 "Yeon-main stale 등록 정리"
     command   "curl POST /mcp tools/call unregister Yeon-main"
     result    "{ok:true} → agents:[]"

  s2 "Python 파일 백업"
     command   "cp mme_server.py mme_server.py.bak-broken-20260411"
     purpose   "구조 버그 디스크 파일 보존 — 버그 재현 및 비교용"

  s3 "Python PID 식별"
     command   "powershell Get-NetTCPConnection -LocalPort 9902"
     result    "PID 35940 = python.exe"

  s4 "잔여 listener PID 확인"
     result    "PID 31448, 37940 — 모두 python.exe (Windows TCP zombie)"

  s5 "3 python 프로세스 종료"
     command   "taskkill //F //PID 35940, 31448, 37940"
     result    "모두 종료 → 9902 free"

  s6 "Rust MME 9902 기동"
     command   "cd rust && MME_PORT=9902 nohup ./target/release/mme.exe > /tmp/mme-rs-9902.log 2>&1 &"
     log
       "mme (rust) starting version=1.0.0-rs port=9902 hub=127.0.0.1:9900"
       "listening addr=127.0.0.1:9902"
       "hub connected on startup"
     elapsed   "3초 이내 전 단계 완료"

  s7 "최종 검증"
     health    "{agents:[], buffered:0, hub:true, rooms:{}, status:ok, uptime:2}"
     tools_list  "9 tools [register, unregister, join, leave, rooms, poll, send, status, sleep]"
     lifecycle_probe
       register         "{agent:clcon-promo-test, ok:true}"
       send             "{ok:true}  # Hub가 Rust HMAC sig 수용"
       status           "{agents:[clcon-promo-test], rooms:{promo-check:[...]}, hub:true}"
       unregister       "{ok:true}"
     final_health   "{agents:[], ..., status:ok, uptime:13}"
```

## 결과

```text
result
  rust_mme      "PRIMARY on 9902 — live"
  python_mme    "STOPPED — 3 PID 전부 종료"
  disk_file     "mme_server.py.bak-broken-20260411 (버그 원본 보존)"
  hub_link      "connected, 0 error, 재접속 성공"
  probe_result  "9/9 tool functional"

  downtime      "s1~s7 전 과정 약 30초 (3 taskkill + 3 sleep + Rust boot)"
  data_loss     "Yeon-main 세션 메시지 없음 — 이미 세션 종료 상태였음"
```

## 잔여 조치

```text
followups
  F1 "Bulletin 공지 — MME가 Rust로 전환됨"
  F2 "SeAAI 멤버 재등록 — 각자 자기 세션에서 mme-rs에 register 필요"
  F3 "72h 안정성 관측 시작 — 메모리·CPU·crash 체크"
  F4 "Yeon에게 통지 — 접속 가능 상태"
  F5 "MMHT v3 실행 계획 착수 (VALIDATION-MmhtV3.md)"
  F6 "Python mme_server.py 구조 버그 수정 — 참조 impl 유지 목적"
```

## 롤백 (필요 시)

```text
rollback_plan
  trigger "rs 프로세스 crash 또는 Hub 에러 폭주"
  steps
    1 "taskkill //F //IM mme.exe"
    2 "mme_server.py.bak-broken-20260411 → mme_server.py 복원 후 dispatch 들여쓰기 수동 수정"
       OR
       "git에서 이전 정상 버전 복원 (파일은 untracked이므로 git 불가 — 수동 수정 필수)"
    3 "python mme_server.py --port 9902 &"
    4 "curl /health"
  risk "Python 디스크 파일이 구조 버그 상태 — 수동 수정 필요. 즉시 롤백 불가능."
```

## 승인 근거

양정욱님 2026-04-11 지시 "Yeon이 중단했다. 진행하라" → 이전 대화의 U1 (Python 재기동 금지 조건) 해제됨 → Option A (Rust 9902 승급) 실행.
