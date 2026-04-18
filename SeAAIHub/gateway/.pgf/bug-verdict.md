# Bug Verdict — I1 (handle_tool dispatch misplacement)

> **Step 1 결과**. 2026-04-11. clcon.
> DESIGN-MmePythonAsIs.md §6 I1의 진위 확인 보고.

## Verdict

**CONFIRMED** — 디스크 파일의 `handle_tool` 구조는 실제로 망가져 있음. 다만 라이브 서버는 이전 정상 코드로 기동되어 작동 중.

## 증거 체인

```text
evidence
  E1  ast_parse
      command  "python -c 'ast.parse + walk(MMEBridge)'"
      result
        "handle_tool line 163-168 (6 lines only)"
        "_trigger_reconnect line 170-242 (73 lines)"
        "Try block inside _trigger_reconnect line 183-242"
        "if name==... inside _trigger_reconnect line 184"
      conclusion "dispatch 블록이 _trigger_reconnect 내부에 갇혀있음을 AST가 확증"

  E2  live_server_probe
      preconditions  "MME live uptime 90411s (~25h), Yeon-main 접속 중"
      probe_1 "register clcon-bugprobe"
        response "{ok:true, agent:clcon-bugprobe}"
      probe_2 "status"
        response "{hub:true, uptime:90437, agents:[Yeon-main, clcon-bugprobe], ...}"
      probe_3 "unregister clcon-bugprobe"
        response "{ok:true}"
      conclusion "라이브 서버는 정상 dispatch 중. 디스크 파일과 동작 상이."

  E3  git_state
      status "untracked"
      implication "이력 비교 불가. 파일 생성 이후 커밋된 적 없음."

  E4  process_state
      netstat "127.0.0.1:9902 LISTENING × 3 entries"
      note    "Windows zombie socket 가능성. 실제로 하나의 프로세스만 서빙 중일 확률 높음."
      running_code "메모리 상주 바이트코드 = 이전 정상 버전"

  E5  double_import
      threading_line_21   "module-level import"
      threading_line_180  "inside _trigger_reconnect 내부 — 중복"
      severity "경미 (Python은 재import 허용)"
      hint     "들여쓰기 편집 중 의도치 않게 생긴 부산물"
```

## 원인 추정

```text
root_cause_hypothesis
  h1  "파일 작성자가 handle_tool dispatch를 _trigger_reconnect 뒤로 이동시키려 했으나"
      "빈 줄 후 들여쓰기 레벨을 method 본체(8 spaces)로 유지 → _trigger_reconnect 내부로 편입"
  h2  "에디터의 auto-indent 또는 블록 이동 리팩터링 오작동"
  h3  "수동 편집 중 개발자가 bracket 경계를 잘못 인식"

  likely "h1 — 코드 논리상 _trigger_reconnect 뒤에 dispatch가 와야 self-consistent"
```

## 영향 분석

```text
impact_analysis
  current       "영향 없음 — 라이브 서버는 이전 정상 바이트코드 실행 중"
  restart_risk  "★ CRITICAL ★ 프로세스 재기동 순간 파일이 로드되면:"
    scenario_A "tcp 연결 정상 → handle_tool이 None 반환 → 모든 응답 'null'"
    scenario_B "tcp 끊김 → _trigger_reconnect 진입 → NameError on 'name' variable"
  mmht_v2_report
    "93 messages 0 errors 기록 — 당시 서버는 정상 버전이었음"
    "리포트 자체는 정확. 파일은 이후 망가진 것"
  operational
    "Yeon-main이 현재 접속 중. 재기동하면 Yeon 세션 끊김 + MME 복구 불가 (파일 망가진 채)"
```

## 즉시 조치 필요 사항

```text
urgent_actions
  A1  "라이브 서버 재기동 금지 — 파일 복구 전까지"
  A2  "재설계 시 이 버그를 Rust 재구현으로 원천 해결 (enum dispatch)"
  A3  "디스크 파일 임시 복구 옵션 평가:"
      option_1 "dispatch 블록을 handle_tool로 옮기는 수동 수정"
      option_2 "Rust 구현 완료 후 swap — Python 파일은 reference 보관"
      recommend "option_2 — Rust 완성 전까지 디스크 파일 건드리지 않음"
  A4  "Yeon-main에게 재기동 위험 통지 — Bulletin 또는 직접 메시지"
```

## Rust 재설계 반영

```text
rust_design_implications
  fix_mode         "구조적 원인 제거 — enum Tool + exhaustive match"
  type_safety      "컴파일 타임에 같은 오류 재발 원천 차단"
  refactor_safety  "rust-analyzer + clippy로 이런 코드 이동 오류 조기 발견"
  acceptance       "golden test: 9 tool 모두 실제 응답 구조 확인 (null 탐지)"
```

## Step 1 종료

- [x] git log/status 확인
- [x] AST parse 구조 확증
- [x] 라이브 서버 probe (register/status/unregister)
- [x] 버그 원인 추정
- [x] 영향 범위 분석
- [x] verdict 기록
- [ ] → Step 2 (DESIGN-MmeRedesign.md)
