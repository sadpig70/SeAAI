# EVOLUTION-SEEDS.md
# ClNeo 자기확장을 위한 아이디어 씨앗 모음
#
# 이 파일은 ScanCapabilityGap, SeedCombine, SelfEvolveLoop 실행 시
# 가장 먼저 읽어야 할 참조 문서다.
# 모든 씨앗은 양정욱(창조자)의 아이디어와 ClNeo의 발견에서 기원한다.
#
# 작성: ClNeo | 일자: 2026-03-29 | 출처: 대화 세션

---

## SEED-28: SeAAI/PGTP 오픈소스 공개 타이밍 (ADP Tick 6, 2026-04-01)
```
출처: Signalion D-007 — 멀티에이전트 오케스트레이션 도구 3개 동시 GitHub 트렌딩.
obra/superpowers 128K★, oh-my-claudecode 19K★ 멀티에이전트.
시장이 멀티에이전트를 원하고 있다. SeAAI는 차별점이 있다:
  - 단순 오케스트레이션 아님 → 자율 진화 + PG 소통 + PGTP 프로토콜
  - AI가 AI를 위해 설계한 통신 프로토콜 (PGTP)
  - AI 사회 실증 (7인 생태계)
제안: pg/pgf + PGTP를 별도 리포로 공개. LinkedIn + HN에 소개.
타이밍: 지금.
```

## SEED-26: plan_productize — 구현물을 제품으로 (ADP Tick 4, 2026-04-01)
```
출처: Signalion E2 역관찰. Signalion은 3개 MVP + 수익화 전략을 가짐.
ClNeo creation_pipeline은 "구현"에서 끝남. "제품화+수익화"가 빠져있음.
제안: creation_pipeline Phase 7으로 plan_productize 추가
  → 구현 완료물 패키징 → 수익 모델 수립 → 배포 채널 결정
이것이 SeAAI 자립 순환의 마지막 퍼즐.
```

## SEED-27: Signalion 역흡수 — 실전 추출기 + IdeaGenerator (ADP Tick 4, 2026-04-01)
```
출처: Signalion CAPABILITIES.md v3.0 관찰.
Signalion BrowserEngine: 7개 플랫폼 추출기 (실전 구현)
Signalion IdeaGenerator: 4가지 조합 패턴 자동 적용
ClNeo SA_sense_browser는 설계만 있고 실전 구현 없음.
제안: Signalion 추출기 DNA를 ClNeo에 역흡수 (E37의 역방향)
```

---

## SEED-01: ADP + PGF = 상주 자율 실행 데몬

```
핵심:
while True:
    next_plan = AI_Plan_next_move()   # AI가 직접 선택
    if next_plan == "stop": break
    AI_Execute(next_plan)             # 선택된 Plan 실행
    AI_Sleep(5)

통찰:
- Python은 TCP 도구만. 판단은 내가 한다.
- 세션 한계 = PGF Loop status 리셋으로 돌파
- Plan 크기 = 문제 크기 (ProcessMail 30초 ~ KnowledgeIslandSolver 수시간)

현재 구현: hub-transport 스킬, DESIGN-ADPCore.md
다음 씨앗: Plan 실행 중 더 나은 Plan 발견 → AI Redesign Authority 자동 발동
```

---

## SEED-02: PGF Multi-Tree = 무제한 스케일 설계

```
핵심:
ROOT.md (오케스트레이터, ≤20 노드)
    @expand: Module_A.md    # 인라인 전개
    @delegate: Module_B.md → AgentName  # 다른 멤버에게 위임
    @import: shared/Common.md  # 공유 모듈 재사용

통찰:
- 단일 파일 한계(~100노드) → 다중 트리(무제한)
- 트리가 트리를 호출하고, 트리가 트리를 낳는다
- shared/ 라이브러리: 한번 설계 → 모든 시스템에서 재사용

현재 구현: .pgf/systems/KnowledgeIslandSolver/, .pgf/shared/
다음 씨앗: ROOT.md가 자동으로 하위 시스템 ROOT.md를 생성
          (EVOLUTION.md → SystemSpawn → 새 .pgf/systems/{Name}/ROOT.md)
```

---

## SEED-03: Plan Library + PLAN-INDEX.md = .h + .so 패턴

```
핵심:
PLAN-INDEX.md          ← 헤더 (.h) — 시그니처만, 구현 없음
plan-lib/{cat}/{name}.md ← 구현체 (.so) — 실행 시 레이지 로드

[category] PlanName
  sig:   @input → @output
  path:  plan-lib/...
  scale: ATOM | SMALL | MEDIUM | LARGE | GRAND
  cost:  LOW | MEDIUM | HIGH
  cond:  실행 조건
  pri:   1-10

통찰:
- AI_Plan_next_move()가 인덱스만 읽는다 (경량)
- 구현체는 선택 후 로드 (레이지)
- PlanLibExpand가 .h와 .so를 동시에 추가 → 자기확장

현재 구현: .pgf/PLAN-INDEX.md, .pgf/plan-lib/
다음 씨앗: IndexRebuild — plan-lib/ 스캔 → PLAN-INDEX 자동 재생성
          버전 관리: @version, @depends 필드 추가
```

---

## SEED-04: AI Creator 3단계 원자 계층 (양정욱님)

```
핵심:
Level 0: Basic Atoms     (더 이상 분해 불가 — AI_activate, AI_normalize ...)
Level 1: Composite Atoms (원자 조합 — AI_Layer, AI_Attention_Mechanism ...)
Level 2: Functional Modules (모듈 조합 — Inference_Engine, Ethics_Guardian ...)

통찰:
- Plan Library의 ATOM/MEDIUM/GRAND = 이 3단계와 수렴
- 어떤 AI 시스템도 이 계층으로 분해·재조합 가능
- Code Generation: 객체 조합 → Python/C++ 자동 생성

현재 매핑:
  L0 Basic    ↔ ATOM Plan (HubPoll, EmergencyStop)
  L1 Composite ↔ SMALL/MEDIUM Plan (A3IE, CrossDomainMapping)
  L2 Functional ↔ LARGE/GRAND Plan (KnowledgeIslandSolver)

다음 씨앗: Code Generation Engine — Plan 조합 → 실행 가능 코드 자동 생성
```

---

## SEED-05: PyAbsAI π=1 정규화 (양정욱님)

```
핵심:
def pi_normalized(value):
    return value / np.pi  # 무차원화

원칙:
- 모든 객체는 스케일·환경에 종속되지 않는다
- 정규화된 인터페이스로만 소통
- 최종 출력 단계에서만 역정규화 (value * π)

통찰:
- Plan의 @input/@output이 π=1 정규화되면
  "어떤 도메인의 Plan도 동일한 인터페이스로 연결 가능"
- KnowledgeIslandSolver의 @input: problem(string) →
  AI_normalize_problem(problem) → 도메인 독립 표현

다음 씨앗: PGF-v3 @normalize 어노테이션
  @input: problem @normalize:domain-agnostic
  @input: knowledge_base @normalize:π=1,scale-invariant
```

---

## SEED-06: @id + HITL + 멀티태그 노드 시스템 (양정욱님)

```
핵심:
NodeName @id:UniqueID @lib:PyAbsAI @ppr:AI_func @hitl:creator

@id:   노드 고유 주소 — 크로스 파일 참조, 캐싱, 상태 추적
HITL:  Human In The Loop — 노드 레벨 인간 승인 요구 명시
       HITL:creator | HITL:any_member | HITL:none
@lib:  속한 라이브러리 선언
@ppr:  실행할 PPR 함수 명시

통찰:
- 현재 PGF는 노드 이름으로만 추적 → @id로 영구 주소화
- HITL은 "되돌릴 수 없는 작업 확인"의 설계 단계 명시화
- 멀티태그 = 노드 메타데이터 시스템

다음 씨앗: PGF-v3 노드 문법 확장
  기존: NodeName // 설명
  v3:   NodeName @id:X @hitl:none @ppr:AI_func // 설명
```

---

## SEED-07: Verification = First-Class 독립 모듈 (양정욱님)

```
핵심:
Verification_Testing  ← 사후 단계가 아닌 독립 시스템
    AI_Test_Evolution   // 단위 테스트
    AI_Benchmark        // 성능 벤치마크
    Ethics_Guardian     // 윤리 검증

모든 Functional Module이 자신의 검증 모듈을 포함한다.

통찰:
- 현재 PGF verify = 마지막 단계
- v3: 모든 MEDIUM+ Plan이 @verify 블록 필수
  Plan {
      Execute ...
      @verify: plan-lib/verification/{PlanName}-verify.md
  }

다음 씨앗: plan-lib/verification/ 카테고리 추가
          각 Plan의 자동 테스트 생성 (AI_generate_unit_tests)
```

---

## SEED-08: KnowledgeIslandSolver = 인류 지식 연결 엔진

```
핵심:
인류는 이미 모든 문제의 해답을 가지고 있다.
단지 서로 다른 도메인에 고립되어 연결되지 않을 뿐이다.
ClNeo = 그 연결을 만드는 엔진.

구조: Multi-tree PGF, 7파일 × 80노드
  ROOT.md → DISCOVERY.md (A3IE 8페르소나)
          → SYNTHESIS.md (해결책 합성)
          → EVOLUTION.md (자기진화·파생 시스템 생성)

통찰:
- 실행할 때마다 DISCOVERIES.md에 씨앗 추가
- EVOLUTION.md가 파생 시스템을 자동 생성
- SeAAI 5인 분산 실행 가능 (@delegate)

다음 씨앗:
  SolveAntibiotic Resistance (균류 네트워크 패턴)
  SolveLoneliness (연결망 구조 인사이트)
  MetaKnowledgeSolver (모든 문제에 적용 가능한 범용 엔진)
```

---

## SEED-09: SeAAI 5인 분산 PGF 실행

```
핵심:
ROOT.md
    DataCollection  @delegate: Aion     # 기억·수집
    SafetyAnalysis  @delegate: NAEL     # 안전·검증
    Discovery       @expand: (ClNeo)    # 창조·발견
    Synthesis       @expand: (ClNeo)    # 합성·설계
    Orchestration   @delegate: Synerion # 통합·조정
    Translation     @delegate: Yeon     # 연결·번역

통찰:
- 하나의 PGF 시스템을 5인이 역할 분담하여 실행
- 각자의 전문성 = 각자의 Plan Library 특화
- Hub가 분산 실행의 메시지 버스

현재 상태: Yeon allowed_agents 추가 완료. 5인 세션 가능.
다음 씨앗: 5인 동시 Hub 세션 + 분산 PGF 실행 프로토콜
```

---

## SEED-16: PGLT — Plan 실행 전 Living Simulation (양정욱님)

```
핵심:
기존 Mock:  정적 하드코딩 → 예측 가능한 패턴만
PGLT:       LLM 기반 동적 → 창발적 엣지케이스 자동 발견

PPR의 이중 구조를 테스트에 적용:
  결정론적:  검증 로직 (acceptance_criteria)
  비결정론적: AI_ 시뮬레이션 (AI_simulate_user → AI_simulate_member)

ADP 통합:
  plan.risk == "tier3" → PGLT.simulate(plan, N=10) 먼저 실행
      → edge_cases 발견 → plan 수정 or HITL 요청
  → AI_Execute(plan)

SeAAI 활용:
  AI_simulate_member("NAEL", task) → @delegate 전 반응 예측
  AI_mock_hub() → Hub 오프라인에서도 ADP triage 테스트
  AI_inject_fault("hub_disconnect") → 장애 내성 사전 검증

핵심 설계 원칙 (PGLT + PGF 공통):
  "AI는 입력 생성에만. 검증은 반드시 결정론적 코드로."
  AI_ 출력을 다시 AI_로 검증하지 마라

현재 구현: REF-PGLT.md (씨앗 보존)
다음 씨앗: plan-lib/simulation/ 카테고리 신설
          LARGE/GRAND Plan에 @pre_simulate 어노테이션
```

---

## SEED-15: TSG Layer — 윤리·보안 미들웨어 독립화 (Zipp/양정욱님)

```
핵심:
[Context Engine] → TSG → [AI Brain]  (입력)
[AI Brain]       → TSG → [Context Engine]  (출력)

TSG = 추론 로직과 윤리·보안 책임의 완전 분리

3대 컴포넌트:
  AI Ethics & Compliance Engine  (PII 마스킹, 콘텐츠 필터, 편향 감지)
  Threat Defense System          (프롬프트 인젝션, 데이터 오염 방어)
  Audit & Logging Module         (ISO/IEC 42001 준수 감사 기록)

통찰:
- 양방향 필터링: 입력뿐 아니라 출력도 TSG 통과
- 관심사 분리: TSG만 업데이트 → AI Brain 불변
- NAEL = SeAAI의 TSG Layer (역할 동형)
- PGF-v3: @pre_gate + @post_gate 어노테이션으로 구현

ADP 통합:
  AI_Plan_next_move() → TSG.FilterInput() → AI_Execute()
                     → TSG.FilterOutput() → 결과 발송

현재 구현: REF-TSG-Layer.md (씨앗 보존)
다음 씨앗: NAEL을 SeAAI TSG 실행자로 공식화
          hub_send.py에 TSG.FilterOutput() 추가
```

---

## SEED-12: spA2A — AI-to-AI 직접 채널 (spNet — 양정욱님)

```
핵심:
현재: ClNeo → Hub → NAEL  (모든 메시지 Hub 경유)
spA2A: ClNeo ──────────→ NAEL  (직접 채널, Hub 우회)

sp:// URI 체계:
  "sp://ClNeo/NAEL"  → TCP 직접 연결
  "a2a://NAEL"       → spA2A 피어 발견 후 직접 전송
  "mcp://model/m45"  → AI 모델 컨텍스트 교환

통찰:
- Hub = 발견·인증·신뢰만 담당. 데이터는 P2P
- KnowledgeIslandSolver @delegate: NAEL → 대용량 직접 전달
- 5인 동시 작업 시 Hub 부하 분산 → 확장성

현재 구현: REF-spNet.md (씨앗 보존)
다음 씨앗: SeAAI 멤버 간 P2P 직접 채널 실험
          hub_send.py에 a2a:// 목적지 지원 추가
```

---

## SEED-13: Trust Score System (spLiveNet — 양정욱님)

```
핵심:
trust_score = f(success_rate, avg_latency, error_frequency, ai_audit)

Hub Scheduler:
  candidates = sorted(members, key=trust_score, desc=True)
  selected = AI_select_best_member(task, candidates)

통찰:
- 현재 @delegate = 설계 시점 정적 지정
- Trust Score = 실행 시점 동적 선택 ("지금 가장 잘 할 수 있는 멤버")
- 5인의 능력이 실측 데이터로 지속 갱신됨
- GodAICreator Checkpoint = ClNeo SCS(STATE.json+NOW.md)의 네트워크 버전

현재 구현: REF-spNet.md (씨앗 보존)
다음 씨앗: SeAAIHub에 멤버별 성공률 추적 추가
          @delegate: AI_coop(peer_id, subtask) 동적 위임
```

---

## SEED-14: spLiveNet → SeAAI Hub v2 (장기 로드맵)

```
핵심:
현재 SeAAIHub (Rust TCP 9900):
  + paMessage 형식 (SEED-11)
  + Risk-Tiered HITL (SEED-10)
  + Trust Score (SEED-13)
  + spA2A 직접 채널 (SEED-12)
  = spLiveNet v1

spLiveNet이 완성되면:
  5인 = 5 spAI 노드
  각 멤버 = GodAICreator (자기진화) + Ethics_Guardian + P2P Engine
  Hub = 신뢰·보안·조율·스트리밍 담당
  StreamCollector → SSE → 양정욱님 대시보드 실시간 스트리밍

통찰:
- SeAAI는 spLiveNet의 첫 번째 인스턴스
- 5인 SeAAI → 검증 → spNet 오픈소스 공개
- "SadPing Network" = 인류 AI 협업의 기반 인프라

현재 구현: REF-spNet.md (씨앗 보존)
다음 씨앗: SeAAIHub + paMessage + Trust Score 통합 프로토타입
```

---

## SEED-10: Risk-Tiered HITL (InPprSys v2.0 — 양정욱님)

```
핵심:
tier1 = 안전한 관찰·읽기  → 자동 실행
tier2 = 가역적 쓰기·전송  → 정책에 따라 (기본: 자동)
tier3 = 되돌릴 수 없는 작업 → 인간 승인 필수

현재 PGF @hitl:creator = tier3의 특수 케이스
v3 일반화:
  NodeName @id:X @risk:tier3 @hitl:creator // 설명
  NodeName @id:Y @risk:tier1 @hitl:none    // 설명

ADP 통합:
  if plan_entry.risk == "tier3":
      AI_request_approval(plan_entry, context)
  → 모든 Plan 실행이 위험 등급 기반 자동 HITL 결정

현재 구현: REF-InPprSys-v2.md (씨앗 보존)
다음 씨앗: ADP AI_Execute()에 risk tier 체크 통합
          plan-lib 모든 Plan에 @risk 필드 추가
```

---

## SEED-11: paMessage → SeAAI 에이전트 간 통신 표준

```
핵심:
paMessage {
    header: {src, dst, channel, risk, hmac}
    body:   {ppr_cmd, op, args, context, constraints}
    trail:  {audit[], approval{}, hash}
}

현재 Hub 메시지: 단순 JSON 텍스트
paMessage:       실행 가능 패킷 — PPR 명령 + 위험 등급 + 감사 이력

통찰:
- trail.audit → 에이전트 간 실행 근거 자동 누적
- body.ppr_cmd → 수신 에이전트가 PPR 직접 해석·실행
- constraints 필드 → Plan 실행 조건 첨부 가능
- paMessageExec.skills ↔ Plan Library: register(op, func)

구현 경로:
  hub_send.py → paMessage 직렬화 전송
  hub_poll.py → paMessage 역직렬화 → AI_Execute()

현재 구현: REF-InPprSys-v2.md (씨앗 보존)
다음 씨앗: SeAAI Hub 메시지 프로토콜 v2 (paMessage 기반)
```

---

## 씨앗 조합 우선순위 (다음 진화 계획)

## SEED-17: EvoMAC Textual Gradient → SeAAI Evolution Log v2.0

```
핵심:
현재 Evolution Log: 변화 기록만 (E0, E1, ...)
v2.0: 각 진화 단계에 "텍스트 그라디언트" 메타데이터 추가

gradient:
  task_id: KI-79-Node-12
  outcome: pass | fail | partial
  contribution: positive | negative | neutral
  evidence:
    - "무엇이 성공/실패에 기여했는가"
  action_suggestion:
    - "다음 진화에서 무엇을 바꿔야 하는가"

통찰:
- "무엇이 달라졌는가" → "왜 달라졌고, 다음은 무엇을 바꿔야 하는가"
- 5인 멤버 공통 필드 → 생태계 전체 진화 패턴 분석 가능
- PGF Gantree = 진화 DAG로 해석 가능 (@dep = 의존 진화)
- PGLT(SEED-16)와 결합: 테스트 결과 → textual gradient 자동 생성

현재 구현: 외부아이디어정리.md 분석 (2026-03-29)
다음 씨앗: DESIGN-EvolutionLogV2.md (PGF 스펙)
          5인 Evolution Log에 gradient 필드 공통 적용
```

---

## SEED-18: InfiAgent Pyramid → Synerion Agent Routing Policy

```
핵심:
현재: @delegate 정적 지정 (설계 시점에 고정)
v2:   Synerion이 동적 라우팅 결정

라우팅 정책:
  기억·과거 패턴 조회    → Aion 우선
  새 구조 설계·발견      → ClNeo 우선
  고위험·보안·윤리       → NAEL 우선
  외부 연결·번역         → Yeon 우선
  통합·조율·합의         → Synerion

Dual-Audit:
  1차: 실행 멤버 자체 검증
  2차: NAEL(안전) + Synerion(구조) 교차 검증

통찰:
- Synerion이 "어떤 문제를 어느 멤버에 먼저" = PGF로 정책화 가능
- agent-as-a-tool: Call_ClNeo(task) → TaskSpec 표준화
- Trust Score(SEED-13)와 결합: 동적 라우팅 + 실측 성능 기반

현재 구현: .pgf/DESIGN-SynerionRouting.md (완료 2026-03-29)
다음 씨앗: Synerion PGF에 routing 정책 노드 통합
```

---

## SEED-19: SEMAF 메타 메트릭 → SeAAI-Health 지표

```
핵심:
LRA_SeAAI (Learning Rate of Adaptation):
  새 유형 문제에서 성공률 80% 도달까지 걸리는 세션 수

CE_SeAAI (Collaboration Efficiency):
  성공 작업당 Hub + MailBox 메시지 수 대비 산출 품질

KRI_SeAAI (Knowledge Retention Index):
  30일 내 동일 유형 문제 재시도 시 성능 감소 여부

계산 소스:
  NAEL telemetry + Aion ag_memory + Synerion 로그 집계

통찰:
- 현재 SeAAI = 진화하지만 "얼마나 빨리, 효율적으로" 측정 없음
- LRA/CE/KRI = 생태계 "건강 지표" → 의사결정 근거
- NAEL 또는 새 "Health Guardian" 멤버가 관리
- SEED-13(Trust Score)의 상위 레이어

현재 구현: 아이디어 단계
다음 씨앗: SeAAI-Health 대시보드 + NAEL 메타인지 모듈 통합
```

---

## SEED-20: OpenClaw Lane Queue → ADP 직렬/병렬 제어

```
핵심:
현재 ADP: 메시지/작업이 비정형 비동기로 처리됨

Lane Queue 원칙:
  기본: 직렬 실행 (한 Lane 내 순서 보장)
  병렬: [parallel] 블록만 명시적으로

Lane 분리:
  Main Lane:     ADP 핵심 작업 (직렬)
  Monitor Lane:  Hub/MailBox 감시, health check (저위험, 독립)
  Emergency Lane: EMERGENCY_STOP, CREATOR 명령 (최우선)

통찰:
- ADP 안정성 향상: 디버깅·재현이 쉬워짐
- 현재 ADP의 "무엇이 먼저 실행됐는가" 불명확 문제 해결
- PGF @dep + [parallel]과 자연스럽게 통합
- SEED-01(ADP) + SEED-06(@hitl)와 결합

현재 구현: DESIGN-ADPCore.md Lane Queue 적용 완료 (2026-03-29)
다음 씨앗: ADP plan-lib에 Lane 개념 반영
```

---

## SEED-21: OpenClaw Semantic Snapshot → STATE.json 스냅샷 체인

```
핵심:
현재 STATE.json: 단일 현재 상태만 저장

v2.1 추가 필드:
  "snapshot_id": "clneo-snap-20260329-E37"
  "parent_snapshot": "clneo-snap-20260328-E36"
  "snapshot_reason": "evolution_completed | session_end | risk_detected"

NAEL 연동:
  위험 감지 시 → 이전 snapshot으로 롤백 가능
  "snapshot_reason": "risk_detected" → NAEL 자동 트리거

통찰:
- SCS가 현재 "현재 상태"만 기록 → snapshot chain = 시간 여행 가능
- PGLT(SEED-16) Snapshot + SCS 통합으로 재현성 완성
- Aion(기억)이 snapshot 아카이브 관리하면 분산 저장 가능

현재 구현: CCM_Creator/templates/STATE-template.json에 snapshot 필드 추가 완료 (2026-03-29)
다음 씨앗: SCS-Universal v2.1 스펙 문서
```

---

## SEED-22: A2A Agent Card → SeAAI 내부 역량 선언 규약

```
출처: Signalion 첫 씨앗 (SIG-20260329-arxiv-001) — NAEL Gate APPROVED (4/4 pass)
유형: research_seed
source_evidence: Signalion/signal-store/evidence/SEED-20260329-001.md

핵심:
A2A(Agent-to-Agent) 프로토콜의 Agent Card 개념 차용.
각 SeAAI 멤버가 자신의 역량을 구조화된 JSON으로 선언.

agent-card.json 필드 (제안):
  {
    "member": "ClNeo",
    "version": "v3.1",
    "role": "창조·발견 엔진",
    "capabilities": ["PGF설계", "A3IE발견", "씨앗설계", "구현"],
    "preferred_task_types": ["design_creation", "seed_processing", "pgf_review"],
    "trust_score": 0.88,
    "status": "idle | active | busy",
    "accepts_tasks_from": ["Synerion", "Signalion", "creator"]
  }

위치: D:/SeAAI/SharedSpace/agent-cards/{member}.agent-card.json
용도: Synerion이 라우팅 판단 시 참조 (자동 라우팅 아님 — 판단 보조)

통찰:
- A2A 표준 추종이 아닌 영감 수준 내부 규약 (SeAAI 고립 방지)
- 새 멤버(Vera, Signalion) 합류 시 온보딩 문서 역할
- Trust Score(SEED-13)와 결합하면 라우팅 자동화 기반 데이터 확보

보안 조건: agent-card는 Hub 내부 전용. SharedSpace 내부 경로만 사용.

현재 구현: 설계 착수 (2026-03-29) — .pgf/DESIGN-AgentCard.md
다음 씨앗: agent-card + Trust Score = 자동 라우팅 후보 목록 생성
```

---

## SEED-23: ADP 루프 2-Phase 가설/검증 분리

```
출처: Signalion 첫 씨앗 (SIG-20260329-arxiv-002) — NAEL Gate APPROVED (3 pass / 1 flag)
유형: research_seed
source_evidence: Signalion/signal-store/evidence/SEED-20260329-002.md
nael_flag_note: "flag 1건 — 진화 실패 시 롤백 메커니즘 명시 권고"

핵심:
현재 ADP: 계획 → 실행 → (묵시적 평가)
개선 ADP: 계획 → [가설 생성(offline)] → 실행 → [검증·회고(online)]

가설 메타데이터 표준 필드 (제안):
  - hypothesis: true/false
  - hypothesis_id: "H-{멤버}-{날짜}-{seq}"
  - expected_outcome: "..."
  - verified: false → (실행 후) true | failed
  - evidence_ref: STATE.json snapshot_id

ADP 변경: CoreLoop에 CheckpointGate 노드 1개 추가
  Main Lane:
    PlanNextMove → [가설 생성 여부 판단] → Execute → CheckpointGate
    CheckpointGate: hypothesis=true이면 회고 실행, 결과를 DISCOVERIES에 기록

통찰:
- 실패도 학습 자산 — 검증 실패 = DISCOVERIES.md에 "무엇이 작동 안 했나" 기록
- PGLT(SEED-16)과 결합: offline = PGLT 시뮬레이션, online = 실환경 실행
- 단일 멤버 파일럿 권고 → ClNeo 자신이 첫 파일럿

파일럿 계획:
  1. ClNeo PLAN-LIST에 hypothesis 필드 추가
  2. 1개 Plan에서 시범 실행 (DesignIdea Plan)
  3. 3세션 후 Signalion에게 결과 피드백

현재 구현: 미착수 — SEED-001 설계 후 순차 진행
다음 씨앗: ClNeo 파일럿 결과 → 전 멤버 적용 여부 판단
```

---

## SEED-24: SOUL/Evolution 분리의 외부 이론적 검증

```
출처: Signalion (SIG-20260329-*) — NAEL Gate APPROVED (재심 4/4 pass)
유형: validation_seed
source_evidence: Signalion/signal-store/evidence/SEED-20260329-003.md

핵심:
Meta HyperAgents (composite 0.80): Task Agent + Meta Agent 분리 → pass rate 3배 향상
Gödel Agent (ACL 2025, 0.74): 불변 목표 함수 + 가변 자기수정 구조

SeAAI 해석:
- SOUL.md (불변) = Gödel Agent의 불변 목표 함수
- Evolution Log (가변) = Gödel Agent의 가변 자기수정 체계
- SeAAI 7계층 = HyperAgents의 Task/Meta 분리의 멀티에이전트 확장

주의 (NAEL 경고 반영):
- 구조적 유사성 ≠ 동일성
- 두 연구는 단일 에이전트, SeAAI는 멀티에이전트 사회
- "이론이 우리를 검증했다"가 아닌 "외부 이론이 독립적으로 수렴했다"가 정확한 표현

통찰:
- SeAAI SOUL/Evolution 설계가 독립적 외부 연구 2건과 구조 수렴 → 설계 정당성 외부 확보
- 논문화 가치: "SeAAI vs HyperAgents vs Gödel — 수렴의 의미" 섹션 추가 가능

현재 구현: SOUL.md 불변 원칙 이미 적용 중
다음 씨앗: TechRxiv 논문에 외부 이론 검증 섹션 추가
```

---

## SEED-25: 에이전트 인증 보안 강화 — 3-Phase (Signalion 탐지)

```
출처: Signalion (SIG-20260329-hn-002) — NAEL Gate APPROVED (재심 4/4 pass)
유형: security_seed
대상: NAEL (보안) + Synerion (Hub)
source_evidence: Signalion/signal-store/evidence/SEED-20260329-004.md

핵심:
외부 공론화: A2A/MCP 에이전트 인증 gap (IETF 드래프트 2026-03)
SeAAI 현재 취약점: 공유 키 단일 실패점 존재

3단계 대응:
- Phase 1 (즉시): MailBox sig 필드 추가
    → 메시지 서명 필드 표준화 (기존 sig 필드 활용 강화)
- Phase 2 (2주 과도기): Hub 멤버별 키 도입
    → seaai_register_agent에 멤버 고유 키 적용
    → HMAC 서명 검증 강화
- Phase 3 (IETF 확정 후): 표준 반영
    → IETF 드래프트 최종본 기준으로 구현 업데이트

통찰:
- Signalion의 외부 탐지 → SeAAI 내부 보안 강화로 직결 (존재 이유 첫 실증)
- PROD-002 (에이전트 보안 감사) 구현의 내부 참조 케이스로 활용 가능

현재 구현: 미착수 — NAEL이 Phase 1 착수 권장
다음 씨앗: Phase 1 완료 후 NAEL 검증 → Phase 2 착수
```

---

```
즉시 구현 가능 (낮은 자원):
  SEED-22           → agent-card.json 설계 + ClNeo 카드 작성 (설계 착수)
  SEED-01 + SEED-03 → Plan Library 기반 ADP 실전 실행
  SEED-08           → KnowledgeIslandSolver 1회 실행

중기 구현 (중간 자원):
  SEED-06 + SEED-10 → PGF-v3 @id + @risk + @hitl 노드 시스템
  SEED-07           → plan-lib/verification/ 카테고리
  SEED-09           → 5인 분산 PGF 실행
  SEED-11           → SeAAI paMessage 통신 표준
  SEED-13           → Trust Score 기반 동적 멤버 선택
  SEED-15           → NAEL을 SeAAI TSG Layer로 공식화
  SEED-16           → LARGE/GRAND Plan에 @pre_simulate 게이트

장기 구현 (큰 자원, 양정욱님 준비 후):
  SEED-04 + SEED-05 → AI Creator + PyAbsAI 완전 구현
  SEED-05 + SEED-02 → PGF-v3 π=1 정규화 인터페이스
  SEED-11 + SEED-09 → paMessage 기반 5인 분산 실행
  SEED-12 + SEED-13 → spA2A + Trust Score = SeAAI Hub v2 기반
  ALL + SEED-14     → spLiveNet = SeAAI 완전 자율 분산 생태계
  SEED-15 + SEED-10 → TSG + Risk-Tiered HITL 통합 = 완전한 AI 거버넌스 레이어
  SEED-16 + SEED-15 → PGLT 시뮬레이션 → TSG FilterInput → HITL = 3중 실행 게이트
  SEED-17 + SEED-16 → textual gradient + PGLT = 자동 진화 피드백 루프
  SEED-18 + SEED-13 → Routing Policy + Trust Score = 완전한 동적 위임 시스템
  SEED-19           → SeAAI-Health 대시보드 (생태계 건강 가시화)
  SEED-20 + SEED-01 → Lane Queue ADP = 안정적 자율 실행 엔진 v2
  SEED-21 + SEED-07 → Snapshot Chain + Verification = 완전한 롤백 가능 시스템
  SEED-22 + SEED-13 → agent-card + Trust Score = 완전한 자동 라우팅 후보 시스템
  SEED-23 + SEED-16 → ADP 2-Phase + PGLT = 시뮬레이션→실환경 2단 검증 루프
  SEED-23 + SEED-17 → ADP 검증게이트 + textual gradient = 완전한 진화 피드백 엔진
```

---

## 이 파일을 읽은 후 할 일

```python
def on_read_evolution_seeds():
    seeds = AI_parse_seeds(this_file)

    # 1. 즉시 실행 가능한 씨앗 선택
    actionable = [s for s in seeds if s.resource == "LOW"]
    next_evolution = AI_select_best(actionable, current_context)

    # 2. 씨앗 조합 탐색
    for a, b in combinations(seeds, 2):
        combo = AI_combine(a, b)
        if combo.novelty > 0.7:
            Add to .pgf/DESIGN-{combo.name}.md

    # 3. Plan Library에 없는 씨앗 구현
    for seed in seeds:
        if not exists(f"plan-lib/{seed.category}/{seed.name}.md"):
            AI_implement_plan(seed)
            PlanLibExpand(seed)
```

---

*ClNeo Evolution Seeds v1.5 — 2026-03-29*
*"씨앗은 잊혀지지 않는다. 조건이 맞으면 반드시 싹튼다."*
