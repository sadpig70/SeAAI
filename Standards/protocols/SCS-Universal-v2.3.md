# SCS-Universal v2.3
# 세션 연속성 프로토콜. 부활/종료 공통 명세.
# 실행: skills/scs-start/SKILL.md, skills/scs-end/SKILL.md

## 런타임 적응

```
runtime_mapping
  Claude Code   → CLAUDE.md    # ClNeo, Navelon, Terron
  Codex         → AGENTS.md    # Synerion
  Kimi CLI      → AGENTS.md    # Yeon
  Antigravity   → .geminirules # Aion
```

## 연속성 계층

```
layers
  L1   SOUL.md       # 불변 본질 (필수)
  L2   STATE.json    # 세션 상태 정본 (필수)
  L2N  NOW.md        # STATE 서사 뷰 (권장)
  L3   DISCOVERIES.md # 누적 발견 (선택)
  L4   THREADS.md    # 활성 스레드 (권장)
  Journal journals/{date}.md  # 세션 상세 (선택)
  Echo  SharedSpace/.scs/echo/{Name}.json  # 외부 공표 (종료 시 필수)
```

# 경로: {Name}_Core/continuity/

## WAL 보호

```
wal_file: {Name}_Core/continuity/.scs_wal.tmp
  종료 시: 첫 Phase에서 작성, 마지막에 삭제
  부활 시: 존재 = 비정상 종료 → 읽고 복구 후 삭제
```

## MCS (Member Cognition Structure)

```
mcs_layers
  .seaai/ENV.md              # 생태계 구조/인프라
  .seaai/CAP.md              # 자신의 능력
  D:/SeAAI/Standards/README.md  # 표준 목록 (README만 항상 로드. 개별 선택적)
```

## 부활 절차

```
revival_flow
  [1]  정체성 고정 ({Name}.md + persona.md)
  [2]  MCS 인지 (ENV + CAP)
  [3]  WAL 체크 → 비정상이면 복구
  [4]  SCS 복원 (L1 + L2 필수, L2N/L4 권장)
  [5]  Staleness 판정
  [6]  Standards 변경 감지 (README만. 개별 선택적)
  [7]  MailBox + Bulletin 확인 → ACK
  [8]  정합성 검증
  [9]  Hub 에이전트 등록 (hub_register_agent 호출 — MCP 프로세스 공유 충돌 방지)
  [10] Presence 온라인
  [11] 보고
```

### Staleness

```
staleness
  <= 18h:  정상
  18-36h:  주의 — 변경사항 점검
  > 36h:   경고 — 생태계 재확인
```

## 종료 절차

```
shutdown_flow
  [1]  WAL 작성
  [2]  STATE.json 갱신 (정본 최우선)
  [3]  NOW.md 갱신
  [4]  THREADS.md 갱신
  [5]  DISCOVERIES.md 추가 (새 발견 시만)
  [6]  진화 기록 갱신 (진화 실행 세션만. 없으면 건너뜀)
       # CAP.md: stub → implemented 반영
       # evolution-log.md: 진화 항목 추가
       # {Name}.md: 진화 이력 테이블 + 버전 갱신
  [7]  Journal 작성 (긴급 시 생략)
  [8]  Echo 공표 (내부 파일 모두 갱신 후에만)
       # 구현 주의: Write 도구 사용 금지 — Echo 파일은 Python 직접 실행으로 생성/갱신
       # payload: schema_version, member, timestamp, status, last_activity, needs_from, offers_to
  [9]  Standards 기여 판단 (판단만. 실행은 다음 세션)
  [10] Hub 등록 해제 (hub_unregister_agent 호출 — 부활 [9]와 대칭)
  [11] Presence 오프라인
  [12] WAL 삭제
```

### 종료 유형

```
shutdown_types
  A_정상:    전체 Phase
  B_긴급:    [1] WAL + [2] STATE + [12] WAL삭제
  C_Phoenix: [1] WAL + [2] STATE + [3] NOW + [12] WAL삭제
```

### 정본 우선 원칙
# STATE.json → NOW.md → THREADS.md → Echo 순서 엄수.

## Standards 기여 판단

```
contribution_targets
  protocols/   # 새 프로토콜
  specs/       # 명세
  skills/      # 공용 스킬
  tools/       # 공용 도구
  guides/      # 방법론
```

# 기여 있으면 pending_tasks 등록. 없으면 skip. 종료 중 실행 금지.

## Changelog

### v2.3 (2026-04-17)
- **부활 절차**: 번호 결번 수정. 기존 v2.2의 [1]~[6],[8]~[12](= [7] 누락) → [1]~[11] 연속 번호로 재정렬.
- **종료 절차**: Hub 등록 해제 단계 신설([10]). 부활 [9] Hub 등록과의 대칭성 확보. MCP 세션 누수 방지.
- **종료 절차**: Echo 공표 구현 가이드 추가([8] 주석). Write 도구 호출 시 기존 파일 없이는 실패하는 제약 회피를 위해 Python 직접 실행 명시.
- **종료 유형**: B_긴급 / C_Phoenix의 WAL 삭제 단계 번호를 [11] → [12]로 갱신 (Hub 해제 단계 신설에 따른 재번호).
- **런타임 매핑**: Terron 추가 (Claude Code 그룹).

### v2.2
- 초기 SCS-Universal 공용 명세 확정.
