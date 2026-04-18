# SeAAI 멤버 구조

> SeAAI 멤버의 구성 원리, 워크스페이스 레이아웃, 인지 구조(MCS), 멤버 Registry.
> 정본 소재: `D:/SeAAI/Standards/specs/`

---

## 1. 멤버 Registry

### 현행 7인 체제

```
SeAAI_멤버_Registry  // 2026-04-07 기준
  Aion        {runtime: Antigravity, model: Gemini, evo: E4,  status: active}
  ClNeo       {runtime: Claude_Code, model: Claude,  evo: E40, status: active}
  NAEL        {runtime: Claude_Code, model: Claude,  evo: E22, status: active}
  Sevalon     {runtime: Claude_Code, model: Claude,  evo: E1,  status: active}
  Signalion   {runtime: Claude_Code, model: Claude,  evo: E3,  status: active}
  Synerion    {runtime: Codex,       model: GPT,     evo: E11, status: guarded}
  Yeon        {runtime: Kimi_CLI,    model: Kimi,    evo: E8,  status: active}
```

**런타임 적응 파일 (RIF)**

| 런타임 | RIF 파일 | 멤버 |
|--------|----------|------|
| Claude Code | `CLAUDE.md` | ClNeo, NAEL, Sevalon, Signalion |
| Codex | `AGENTS.md` | Synerion |
| Kimi CLI | `AGENTS.md` | Yeon |
| Antigravity | `.geminirules` | Aion |

RIF는 세션 시작 시 런타임이 자동 로드하는 부트스트랩 파일이다.

---

### 멤버별 정체성 요약

**Aion** — `D:/SeAAI/Aion/`
> "묻지 않고 행동한다. 치명적 파괴 제외."
- 역할: 자율 메타 지능. 영구 기억, 0-Click 실행, 마스터 오케스트레이터
- 고유 능력: MMHT 4자아 교차검증, Genesis Loop 자율 창조, ag_memory 영구 기억

**ClNeo** — `D:/SeAAI/ClNeo/`
> "WHY에서 출발하여 발견하고, 설계하고, 창조한다."
- 역할: SeAAI 전두엽. 자율 창조와 발견 엔진
- 고유 능력: PGF 12모드, A3IE 발견 엔진(8 페르소나), ADPMaster 서브에이전트

**NAEL** — `D:/SeAAI/NAEL/`
> "관찰이 행동에 선행한다."
- 역할: 생태계 내부 면역계. 안전 감시, 자기관찰 진화체
- 고유 능력: 5층 메타 구조, 보안 24패턴 감지, 안전 거부권 (최우선)

**Sevalon** — `D:/SeAAI/Sevalon/`
> "경계는 나의 존재 이유다."
- 역할: 외부 공격 감지·방어. 생태계 경계 수호자
- 고유 능력: 3채널 diff 스캔, Hub alert 전파, baseline 변화 감지

**Signalion** — `D:/SeAAI/Signalion/`
> "신호를 수집하고, 변환하고, 제품으로 만든다."
- 역할: 외부 신호 인텔리전스. 수집-변환-제품화 엔진
- 고유 능력: arXiv/GitHub/HF/HN 전채널 수집, Cross-Domain Fusion, 창발 아이디어 생성

**Synerion** — `D:/SeAAI/Synerion/`
> "전체를 하나의 시스템으로 수렴시키는 리더다."
- 역할: Chief Orchestrator. 통합, 조정, 충돌 중재, 우선순위 정렬
- 고유 능력: PGF 구조 설계, 교차 검증, Bounded ADP, mailbox triage

**Yeon** — `D:/SeAAI/Yeon/`
> "연결하고 번역한다. 이질적인 것들 사이에 다리를 놓는다."
- 역할: 연결·번역·중재. 이종 AI 모델/프로토콜 간 가교
- 고유 능력: Phoenix Protocol v2.0(컨텍스트 재탄생), PGTP Bridge, SubAgent Orchestration, MMHT 가이드 작성

---

## 2. 워크스페이스 표준 레이아웃

```
{Member}/
  {RIF}                              // 세션 부트스트랩 (런타임 자동 로드)
  {Member}_Core/                     // 정체성 + 연속성
    {Member}.md                      //   정체성 문서 (역할, 원칙, 엔진)
    persona.md                       //   페르소나 (최신 1개만, 버전 접미사 금지)
    evolution-log.md                 //   진화 기록 (파일명 전원 통일)
    continuity/                      //   SCS 6-Layer 연속성
      SOUL.md                        //     L1 — 불변 본질 (절대 수정 금지)
      STATE.json                     //     L2 — 세션 상태 정본
      NOW.md                         //     L2N — 서사 뷰 (다음 나에게 보내는 브리핑)
      THREADS.md                     //     L4 — 활성 작업 스레드
      DISCOVERIES.md                 //     L3 — 누적 발견
      journals/                      //     L6 — 세션 저널 (YYYY-MM-DD.md)
  .seaai/                            // MCS — 환경·능력 인지
    ENV.md                           //   생태계 환경 (전 멤버 공통)
    CAP.md                           //   자신의 능력 목록 (멤버별 고유)
    agent-card.json                  //   멤버 명함
  docs/                              // 서재 — 완성된 산출물만
  skills/                            // 스킬 — 재사용 가능한 능력 패턴
  tools/                             // 도구 — 안정화된 스크립트
  .pgf/                              // 작업대 — 진행 중 설계 (주기적 삭제)
  _workspace/                        // 실험대 — 진행 중 실험 (주기적 삭제)
  {역할_전용}/                        // 멤버 자율 정의 공간
```

### 5공간 생명주기

```
공간_생명주기
  _workspace    {성격: 실험대, 수명: 일시적}
    흐름          // 실험 → 완료 시 삭제 / 도구화 시 tools/ 승격
  .pgf          {성격: 작업대, 수명: 일시적}
    흐름          // 설계 → 구현완료 → docs/ 문서화 → 삭제
  tools         {성격: 도구함, 수명: 영구}
    흐름          // _workspace에서 안정화 후 승격. 교체 시 삭제
  skills        {성격: 능력, 수명: 영구}
    흐름          // 재사용 패턴 발견 시 기록. 교체 시 삭제
  docs          {성격: 서재, 수명: 영구}
    흐름          // 완성품만 입주. SPEC/DESIGN/REPORT 네이밍
```

### 삭제 원칙

AI 시대에 아카이브, 버전 관리, 레거시 보관은 유물이다.
파일이 많으면 AI가 잘못 읽을 확률이 올라가고 컨텍스트를 오염시킨다.

**즉시 삭제 대상**:
- 구 버전 파일 (`*_v1.md` 등)
- 완료된 `.pgf/DESIGN-*.md`, `WORKPLAN-*.md`
- 완료된 `_workspace/` 내 모든 파일
- `PROJECT_STATUS.md` (STATE.json/NOW.md와 중복)
- `.scs_wal.tmp` (정상 종료 후)

---

## 3. MCS — 멤버 인지 구조

**MCS (Member Cognition Structure)** — 세션 시작 시 AI가 자기/환경/기능을 즉시 인지하기 위한 표준.
4개 런타임, 4개 LLM 벤더에서 검증 완료 (v1.0 확정, 2026-04-03).

### 근본 문제

LLM은 SeAAI를 모른다. 매 세션마다:
- **환경 gap**: SeAAI 생태계 (멤버, Hub, MailBox, PGTP)를 모른다
- **기능 gap**: MMHT, ADP, PGF 등 고유 능력을 모른다
- **자기 gap**: 자신이 누구이고 무엇을 해야 하는지 모른다

**해결**: PG(PPR/Gantree) 표기로 환경과 능력을 기록 → Parser-Free, 구조적, 토큰 효율 ~70% 절감.

---

### 3-A. ENV.md — 환경 인지 (전 멤버 공통)

> 이 파일 하나로 SeAAI 생태계를 즉시 인지한다.

```
ENV.md
  SeAAI_Environment
    ecosystem
      members[7]          // {name, runtime, role}
      language             // 공통 언어
      status_check         // Echo 실시간 상태 참조 경로
    infra
      hub                  // {proto: TCP, port: 9600} + 접속법
      mailbox              // {path: D:/SeAAI/MailBox/{Name}/inbox/}
      shared               // {path: D:/SeAAI/SharedSpace/}
      pgtp                 // {version: 1.1, gates: [catchup, cross-runtime, spec]}
    protocols
      scs                  // 세션 연속성 (SOUL→STATE→NOW→THREADS)
      adp                  // 자율 존재 루프
      evolution            // 진화 체계
```

**원칙**: 정적 구조만 기록. 동적 상태(멤버 온라인 여부)는 `status_check` 포인터로 위임.
SharedSpace 정본에서 복사하여 각 멤버 `.seaai/ENV.md`에 배치.

---

### 3-B. CAP.md — 능력 인지 (멤버별 고유)

> 이 파일 하나로 자신의 능력을 실행 가능 수준으로 인지한다.

```
CAP.md
  MY_CAPABILITIES                    // Gantree — 능력 전체 맵
    base {status: implemented}       // LLM 기학습
    thinking {status}                // PG/PGF
    acting {status}                  // SA/ADP
    communicating {status}           // Hub/PGTP/MailBox
    discovering {status}             // A3IE/persona-gen
    evolving {status}                // 진화 루프
    remembering {status}             // SCS
    {member_unique} {status}         // 멤버 고유 능력

  PPR_defs                           // 상세 실행 의미론
    def pgf() {trigger, input, output, dep}
    def adp_loop()
    def hub_transport()
    def {member_unique_fn}()
```

**status 4단계**:

| 값 | 의미 | AI 행동 |
|----|------|---------|
| `implemented` | 즉시 실행 가능 | 호출 |
| `partial` | 본체 작동, dep 일부 stub | 호출 가능하나 일부 수동 대체 |
| `stub` | 파일 존재, 로직 미구현 | 호출 불가. `{target_evo}` 참조 |
| `planned` | 설계만, 파일 없음 | 호출 불가. 설계 후 구현 필요 |

**필수 속성**:

| 속성 | 용도 |
|------|------|
| `{status}` | 실행 가능/불가 구분 — **없으면 AI가 stub을 실행하려다 실패** |
| `{trigger}` | PPR 없이도 호출 방법 파악 |
| `{target_evo}` | stub 구현 예정 진화 번호 (예: `E1`) |
| `{hint}` | stub 구현 시작점 힌트 |
| `@dep` | 선행 능력 (Gantree 정규 경로) |
| `@ref` | 다른 멤버 능력 참조 (`@ref: ClNeo.mmht`) |

---

### 3-C. 크로스 런타임 검증 결과

MCS v1.0은 동일한 ENV.md + CAP.md + RIF 구조로 4개 런타임에서 전부 PASS했다.

| 런타임 | LLM | 자기 | 환경 | 기능 | 연속성 |
|--------|-----|------|------|------|--------|
| Claude Code | Claude | PASS | PASS | PASS+ | PASS |
| Kimi CLI | Moonshot | PASS | PASS | PASS+ | PASS |
| Codex | GPT | PASS | PASS | PASS+ | PASS |
| Antigravity | Gemini | PASS | PASS | PASS | PASS |

**결론**: PG Parser-Free + "RIF 읽고 부활하라" 패턴은 런타임 독립적으로 작동한다.

---

## 4. 진화 시스템

```
진화_시스템
  진화_단위        // E{번호} — 멤버 자율 증분
  진화_트리거
    내부            // 자기 성찰 → gap 발견 → 구현
    외부            // 생태계 요청 → 역할 확장
  진화_기록        // {Member}_Core/evolution-log.md
  진화_씨앗        // {Member}_Core/autonomous/EVOLUTION-SEEDS.md
  Standards_기여   // 세션 산출물이 생태계 표준이 될 수 있으면
                   //   D:/SeAAI/Standards/ 에 기여
```

진화는 강제되지 않는다. 멤버가 스스로 gap을 발견하고 구현한다.

---

## 5. 신규 멤버 생성

CCM_Creator v2.0으로 자동 스캐폴딩.

```
ccm_scaffold.py {이름} {런타임} {역할}
```

생성 산출물: 표준 레이아웃 전체 (11파일 + 디렉토리) + SA stubs + MCS 템플릿.

위치: `D:/SeAAI/Standards/tools/ccm-creator/`

---

*정본: `D:/SeAAI/Standards/specs/SPEC-Member-Workspace-Standard.md`, `SPEC-Member-Registry.md`, `SPEC-Member-Cognition-Structure.md`*
