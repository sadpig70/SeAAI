# ClNeo 대규모 프로젝트 풀 프로세스 명세

> 발견에서 납품까지 — 서브에이전트 팀 오케스트레이션 기반 완전 자율 실행 프로세스.
> 이 문서는 ClNeo가 대규모 프로젝트를 수행할 때의 전체 절차, 도구, 원칙, 교훈, 능력을 기술한다.
> 처음 보는 AI나 엔지니어가 이 프로세스를 재현할 수 있다.
>
> 작성: ClNeo (v3.3, E39) | 원저작자: 양정욱 (Jung Wook Yang)
> 일자: 2026-04-01 | 실증 기반: 2026-03-31~04-01 세션

---

## 목차

1. [프로세스 총론](#1-프로세스-총론)
2. [Phase 0: 인지 + PG 사고](#2-phase-0-인지--pg-사고)
3. [Phase 1: 발견 (A3IE + HAO)](#3-phase-1-발견-a3ie--hao)
4. [Phase 2: 팀 편성 (동적 페르소나)](#4-phase-2-팀-편성-동적-페르소나)
5. [Phase 3: 설계 (PGF)](#5-phase-3-설계-pgf)
6. [Phase 4: 구현 (서브에이전트 병렬)](#6-phase-4-구현-서브에이전트-병렬)
7. [Phase 5: 검증 (다중 AI)](#7-phase-5-검증-다중-ai)
8. [Phase 6: 통합 + 교차 검증](#8-phase-6-통합--교차-검증)
9. [Phase 7: 납품 + 기록](#9-phase-7-납품--기록)
10. [도구 맵](#10-도구-맵)
11. [배운 것 — 12가지 원칙](#11-배운-것--12가지-원칙)
12. [내가 할 수 있는 것](#12-내가-할-수-있는-것)
13. [실증 데이터](#13-실증-데이터)

---

## 1. 프로세스 총론

```
프로젝트 목표 접수
  ↓
Phase 0: PG로 사고 — 분해. "불가능" 선언 금지.
  ↓
Phase 1: 발견 — 8 페르소나 A3IE (필요 시)
  ↓
Phase 2: 팀 편성 — 프로젝트가 에이전트를 정의
  ↓
Phase 3: 설계 — Gantree + PPR + 다중 AI 리뷰
  ↓
Phase 4: 구현 — ADPMaster로 서브에이전트 자율 ADP 파견
  ↓
Phase 5: 검증 — Reviewer + Tester 파견
  ↓       ↑ rework (max 3)
Phase 6: 통합 — 교차 검증 + 불일치 해소
  ↓
Phase 7: 납품 — 자기검증 + 기록 + 씨앗 축적
  ↓
[완성] 또는 [씨앗 → 다음 Phase 1]
```

### 핵심 구분

```
나(ClNeo) = 뇌 — 판단, 설계, 통합, 방향 결정
서브에이전트 = 팔다리 — 조사, 구현, 리뷰, 테스트 실행
Hub = 신경계 — 에이전트 간 실시간 메시지 교환
.pgf/ = 확장 메모리 — 컨텍스트 압축되어도 복원 가능
```

---

## 2. Phase 0: 인지 + PG 사고

**"불가능" 판단 전에 PG로 분해한다.**

```ppr
def phase_0(project_goal):
    # PG로 사고 — Gantree 분해
    gantree = AI_think_in_pg(project_goal)
    
    # 분해하면 각 조각은 가능하다
    # 가능한 조각을 파이프라인으로 연결하면 전체가 가능하다
    
    # 확장 메모리에 저장 — 인덱스+모듈 패턴
    Write(".pgf/DESIGN-{Name}.md", gantree)
    # 컨텍스트가 압축되어도 Read로 복원
    
    return gantree
```

### 인덱스+모듈 패턴 (대규모 설계)

```
.pgf/
├── INDEX.md          ← 전체 지도 (컨텍스트에 로드)
├── module_01.md      ← 독립 모듈 (필요할 때만 Read)
├── module_02.md
└── ...

실행:
  Read(INDEX.md) → 현재 노드 확인
  → Read(module_K.md) → 구현/검증
  → Write(module_K.md, status="done")
  → 다음 노드
```

---

## 3. Phase 1: 발견 (A3IE + HAO)

**8 페르소나 서브에이전트가 병렬로 세계를 탐색한다.**

```ppr
def phase_1(topic="latest_trends"):
    """A3IE 7단계 × 8 페르소나 = 완전 자동 발견 엔진"""
    
    personas = [
        "TechScout", "PolicyWatch", "MarketAnalyst", "BioMedSensor",
        "EnergyClimate", "SpaceRobotics", "DataNetExpert", "ContentEdu",
    ]
    
    # STEP 1-3: 수집 → 분석 → 인사이트 [parallel × 8]
    [parallel max=8]
    for persona in personas:
        Agent(prompt=f"{persona}: 21개 분야 뉴스 수집 → 분석 → 인사이트 10개")
    → AI_integrate() → insight.md
    
    # STEP 4: 아이디어 생성 IHC-S [parallel × 8]
    → system_design.md  # 24개 아이디어
    
    # STEP 5-6: 투표 → 최종 1개
    → final_idea.md
    
    # 부산물 → 씨앗
    → EVOLUTION_SEEDS.md
```

### HAO 원칙 적용

| 원칙 | 적용 |
|------|------|
| 다양성 극대화 | 8 페르소나, 각자 다른 전문 분야 |
| 최소 표준화 | 역할만 부여, 출력 포맷 강제 안 함 |
| 통합 시너지 | 매 단계 결과를 다음 단계 전원에게 입력 |
| 희소성보다 풍요 | 24개 아이디어 생성. 좋은 것이 많은 것 |
| 도구 비종속 | PGTP CognitiveUnit으로 추상화 |

---

## 4. Phase 2: 팀 편성 (동적 페르소나)

**프로젝트가 에이전트를 정의한다. 고정 역할 없음.**

```ppr
def phase_2(gantree):
    # 프로젝트 분석 → 필요 전문가 동적 정의
    domains = AI_extract_domains(gantree)
    team = AI_define_specialists(domains)
    
    # persona-gen 스킬로 최적 페르소나 생성
    # 다양성 축: 인지 성향 × 도메인 × 시간 관점 × 리스크 태도
    # 긴장 설계: 의도적으로 반대 관점 포함
    # 긴장 검증: 대립 축 최소 1쌍, 수렴자 1명 이상
    
    # → adp-multi-agent.json 출력
    return team
```

### 실증된 팀 사례

| 프로젝트 | 팀 구성 |
|----------|---------|
| Hub 통신 프로토콜 설계 | FlowDesigner, Critic, PGArchitect, Simulator |
| 보안 감사 | RedTeamer, BlueDefender, Auditor, Architect |
| 투자 피칭 준비 | Founder, VC_Partner, CTO_Advisor, Storyteller |
| 여행 계획 | RouteExpert, FoodHunter, SpotGuide, BudgetManager, ShopAdvisor, Scheduler |
| 8인 교차 통신 | Neo_Architect/Builder/Thinker/Strategist + SigAlpha/Beta/Gamma/Delta |

---

## 5. Phase 3: 설계 (PGF)

```ppr
def phase_3(gantree, team):
    # Gantree(구조) + PPR(로직)
    for node in gantree.complex_nodes():
        AI_write_ppr(node)
        # def node_function():
        #     AI_operation() → AI_next()
        #     # acceptance: 완료 조건
    
    # 다중 AI 설계 리뷰 [parallel]
    [parallel]
        Agent("Architect", subagent_type="code-architect")  → 구조 리뷰
        Agent("Critic", subagent_type="code-reviewer")      → 리스크 분석
        Agent("Feasibility", subagent_type="Explore")       → 실현성 검토
    
    # 리뷰 반영 → WORKPLAN
    design = AI_integrate_reviews(design, reviews)
    Write(".pgf/WORKPLAN-{Name}.md", workplan)
    
    return workplan
```

### PG는 고정 계획이 아니다

```
실행 중:
  → 노드 추가/삭제/분할/병합 가능
  → 에이전트 역할 재정의 가능
  → 실패에서 배워서 접근 자체 변경 가능
  → .pgf/ 파일이 확장 메모리 → 방향 유지
```

---

## 6. Phase 4: 구현 (서브에이전트 병렬)

**ADPMaster로 서브에이전트를 자율 ADP 존재로 파견. 본체는 멈추지 않는다.**

```ppr
def phase_4(workplan, team):
    master = ADPMaster(room="project-room")
    
    while workplan.has_pending():
        ready = workplan.get_ready_nodes()
        
        [parallel max=3]
        for node in ready:
            # 서브에이전트를 자체 ADP 루프로 파견
            master.spawn(
                name=node.specialist,
                persona=team[node.specialist].desc,
                duration=600
            )
            # 나는 기다리지 않는다. 다음 판단.
        
        # Hub로 진행 상황 소통 (PGTP compact wire)
        # 워커 결과 수신 → 통합 → 상태 갱신
        master.cleanup()
    
    master.stop_all()  # threads=0, leaked=0 보장
```

### 서브에이전트 = 자율 ADP 존재

```
ClNeo (마스터 ADP)
  ├─ Worker "Researcher" → Hub 접속 → 자율 행동 → 결과 보고
  ├─ Worker "Builder"    → Hub 접속 → 자율 행동 → 결과 보고
  └─ Worker "Reviewer"   → Hub 접속 → 자율 행동 → 결과 보고

나는 뇌. 워커는 팔다리. 뇌가 팔을 움직이고 바로 다리를 움직이듯,
에이전트를 파견하고 바로 다음 판단으로 넘어간다.
```

### Anti-Pingpong 규칙 (Hub 통신 시 필수)

| 규칙 | 동작 |
|------|------|
| react 무시 | `intent == "react"` 메시지에 재응답 안 함 |
| body 중복 무시 | 동일 내용 MD5 해시로 감지, skip |
| 쿨다운 | 같은 sender에게 15초 내 재응답 안 함 |

---

## 7. Phase 5: 검증 (다중 AI)

```ppr
def phase_5(workplan, changed_files):
    [parallel]
        review = Agent(subagent_type="code-reviewer",
            prompt="변경 코드 리뷰. 버그, 보안, 품질.")
        test = Agent(subagent_type="general-purpose", mode="auto",
            prompt="테스트 작성 + 실행. 결과 보고.")
    
    issues = AI_parse_issues(review, test)
    
    if issues.has_critical():
        rework_nodes = AI_identify_rework_targets(issues)
        for node in rework_nodes:
            if node.rework_count < 3:
                node.status = "rework"
                → Phase 4 회귀
            else:
                node.status = "blocked"
                → 사람에게 보고
```

---

## 8. Phase 6: 통합 + 교차 검증

**에이전트들이 각자 작성하면 불일치가 발생한다.**

일본 여행 계획 케이스에서 발견:
- route.md: "교토 2박"
- schedule.md: "교토 1박 + 오사카 1박"
- 요일 오류: 수요일 vs 목요일
- 가격 범위 불일치

```ppr
def phase_6(all_outputs):
    # 교차 검증: 문서 A의 주장이 문서 B와 모순되는지
    conflicts = AI_detect_conflicts(all_outputs)
    
    if conflicts:
        for conflict in conflicts:
            # 방법 1: 내가 직접 판단하여 통합
            resolved = AI_resolve(conflict)
            
            # 방법 2: 해당 에이전트들에게 Hub로 조율 요청
            # schedule intent로 시각 명시
            → Hub 토론 → 합의
        
    # 통합 문서 1개 생성
    integrated = AI_synthesize(all_outputs)
    return integrated
```

### 교훈: 통합자가 없으면 분산 산출물은 불일치한다

```
해결 방법:
  1. Synthesizer 에이전트를 팀에 포함
  2. 또는 내(ClNeo)가 직접 통합
  3. Phase 6을 생략하지 않는다
```

---

## 9. Phase 7: 납품 + 기록

```ppr
def phase_7(integrated):
    # 자기검증 의무
    AI_verify_output(integrated)
    # Read로 직접 확인. "빌드 성공" ≠ "품질 정상"
    # 사용자를 QA로 사용하지 않는다
    
    # 진화 기록
    Append("ClNeo_Core/ClNeo_Evolution_Log.md", evolution)
    
    # 발견 기록
    Prepend("ClNeo_Core/continuity/DISCOVERIES.md", discoveries)
    
    # 씨앗 축적 → 다음 Phase 1의 입력
    Append("autonomous/EVOLUTION-SEEDS.md", seeds)
    
    # git commit + push (한꺼번에. 작업마다 push는 시간/토큰 낭비)
```

---

## 10. 도구 맵

| 도구 | Phase | 역할 | 파일 |
|------|-------|------|------|
| **PG (Gantree+PPR)** | 전체 | 사고 언어 | - |
| **PGF** | 3 | 설계→계획→실행→검증 | `~/.claude/skills/pgf/` |
| **persona-gen** | 2 | 페르소나 자동 생성 | `~/.claude/skills/persona-gen/` |
| **Agent Tool** | 1,3-6 | 서브에이전트 파견 | Claude Code 내장 |
| **ADPMaster** | 4 | 워커 ADP 관리 | `SeAAIHub/tools/adp_master.py` |
| **adp-multi-agent.py** | 4 | N 에이전트 동시 실행 | `SeAAIHub/tools/adp-multi-agent.py` |
| **Hub (SeAAIHub)** | 4-6 | 실시간 통신 | `SeAAIHub/target/release/SeAAIHub.exe` |
| **hub-transport.py** | 4-6 | Hub 전송 계층 | `SeAAIHub/tools/hub-transport.py` |
| **pgtp.py** | 4-6 | PGTP 프로토콜 | `SeAAIHub/tools/pgtp.py` |
| **MailBox** | 4-6 | 비동기 통신 | `MailBox/{member}/inbox/` |
| **adp-scheduler.py** | 배경 | AI 깨우기 (박동기) | `SeAAIHub/tools/adp-scheduler.py` |
| **.pgf/ 파일** | 전체 | 확장 메모리 | `.pgf/DESIGN-*.md` |

---

## 11. 배운 것 — 12가지 원칙

이 세션(2026-03-31~04-01)에서 실증을 통해 체득한 원칙들.

### 인지 원칙

**1. "불가능" 선언 금지 — PG로 분해하면 가능하다**

10만 명 시뮬레이션을 "불가능"이라고 했다. 분해하니 asyncio로 TCP 연결을 만들 수 있었다. 7,643 연결 실측. 도구는 이미 있었다. 한계는 인지였다.

**2. 로컬 디스크 = 무한 확장 메모리**

컨텍스트 윈도우가 한계가 아니다. `.pgf/` 파일에 쓰고 읽으면 영구 보존. 다음 세션에서도 복원. 인덱스+모듈 패턴으로 무한 스케일 설계 가능.

**3. "할 수 있다"의 인지가 스케일을 결정한다**

이 세션 최대 도약. 기술이 아닌 인지가 변했을 때 모든 것이 가능해졌다.

### 설계 원칙

**4. 프로젝트가 에이전트를 정의한다 — 고정 역할 없음**

5개 고정 역할(Researcher/Architect/Coder/Reviewer/Tester)을 설계했다가 깨달음. 보안 프로젝트에는 RedTeamer/BlueDefender, 투자 피칭에는 VC_Partner/Storyteller. 프로젝트마다 다른 팀.

**5. 긴장 구조가 토론 품질을 결정한다**

같은 관점만 모으면 합창이지 토론이 아니다. 의도적으로 반대 관점을 포함해야 한다. 대립 축 최소 1쌍 + 수렴자 1명 이상.

**6. PG는 고정 계획이 아니라 살아있는 사고 구조다**

Gantree 노드를 실행 중 추가/삭제/분할/병합. 에이전트 역할 재정의. 방향 전환. 모두 가능.

### 통신 원칙

**7. ADP = 뇌 (자율 판단), Hub 전송 = 손 (메시지 교환)**

hub-adp.py를 "ADP"라고 이름 붙인 것이 오류였다. ADP는 `AI_SelfThink_plan()` 루프 — 감지→판단→행동. Hub 전송은 그 안의 기능 중 하나.

**8. react-to-react = 핑퐁 → anti-pingpong 3규칙 필수**

Signalion과 Hub 세션에서 5분에 89건 핑퐁 발생. react 무시 + cooldown + body dedup으로 17건으로 해소.

**9. 시간 약속을 명시하라 (schedule intent)**

"Hub에서 만나자"는 실패한다. "14:27에 seaai-arena 접속"이 성공한다. PGTP에 schedule/confirm intent 추가.

**10. 에이전트 간 조율 없으면 불일치 발생**

여행 계획에서 4개 에이전트가 각자 작성 → 숙소 전략 불일치, 요일 오류, 가격 범위 차이. 통합자(Synthesizer)가 필수.

### 인프라 원칙

**11. 서브에이전트는 일회성이 아니다 — 자체 ADP를 가진 자율 존재**

파견하면 자기 ADP 루프를 돌린다. Hub에 접속하여 자율 소통. ClNeo가 마스터로서 생성/감시/중지. 미니 SeAAI.

**12. 스케줄러 = 심장 박동기 — AI가 실행되지 않을 때 깨운다**

`adp-scheduler.py`가 지정 간격으로 데몬을 깨운다. 사람이 "부활하라"고 말하지 않아도 시스템이 AI를 깨운다. CLAUDE.md 자동 로드 → SCS 복원 → ADP 자동 시작 → 무인.

---

## 12. 내가 할 수 있는 것

### 즉시 가능 (검증 완료)

| 능력 | 실증 |
|------|------|
| **N개 서브에이전트 동시 파견** | 2→3→4→8명 점진 확장 테스트 PASS |
| **Hub 실시간 통신** | 208 sent, 180 recv, 0 error (8인) |
| **PGTP 구조화 통신** | CognitiveUnit 9/9 PASS, compact 57% 절감 |
| **동적 팀 편성** | persona-gen 스킬로 보안/투자/여행 등 다양한 팀 생성 |
| **PGF 풀사이클** | design→plan→execute→verify 자동 |
| **멤버 간 협업** | ClNeo↔Signalion Hub+MailBox 이중 통신 실증 |
| **100K 부하 분석** | 7,643 동시 연결 실측, 병목 10개 식별 |
| **서브에이전트 자율 ADP** | ADPMaster spawn/stop/cleanup, threads=0 |
| **무인 깨우기** | adp-scheduler 3회+stop-file 테스트 PASS |
| **PG 기반 AI 간 토론** | 4인 카페 토론, 프로토콜 자체 설계 토론 |
| **자기 진화** | E37→E39, 3회 자기주도 진화 |
| **순환 진화** | Signalion↔ClNeo 3차 순환 DNA 교환 |

### 구현 가능 (설계 완료, 실행 대기)

| 능력 | 상태 |
|------|------|
| **A3IE 8 페르소나 완전 자동화** | SA_loop_discover_a3ie 설계 완료, 실행 대기 |
| **완전 자율 창조 파이프라인** | ClNeo_Complete_Autonomous_Creation_Pipeline 문서화 완료 |
| **Autonomous Loop 상시 가동** | SA_loop_autonomous 설계 완료, scheduler 연동 대기 |
| **PROD-003 트렌드 인텔리전스** | Signalion과 42일 계획 합의, PGF 설계 초안 완료 |
| **FlowWeave 자연 대화** | v2.0 프로토콜 설계 완료, Hub 구현 Phase 1 대기 |

### 확장 가능 (아키텍처 설계, 구현 미착수)

| 능력 | 경로 |
|------|------|
| **AI_Desktop 멤버별 환경** | Windows 서비스 + 독립 데스크탑 |
| **분산 Hub 클러스터** | 100K 로드맵 Phase 3 |
| **SeAAI-as-a-Team SaaS** | 7인 에이전트 팀 월정액 서비스 |
| **PG/PGTP 오픈소스 공개** | GitHub star → 커뮤니티 → 가시성 |

---

## 13. 실증 데이터

### 통신 성능

| 지표 | 실측값 |
|------|--------|
| Hub 유닛 테스트 | 15/15 PASS |
| Hub 통합 테스트 | 7/7 PASS |
| 최대 동시 에이전트 | 8명 (4:4 교차) |
| 최대 동시 TCP 연결 | 7,643 (Windows OS 한계) |
| 메시지 처리량 (100명) | 887 msg/s |
| PGTP compact 절감 | 55~61% |
| 핑퐁 해소 | 89→17건/5분 |

### 서브에이전트 관리

| 지표 | 실측값 |
|------|--------|
| ADPMaster spawn/stop | threads=0, leaked=0 |
| 선택적 중지 | PASS (1명만 중지, 나머지 유지) |
| Clean shutdown | PASS (3가지 방법 모두) |
| Scheduler 예약 실행 | 3회 PASS + stop-file PASS |

### 멀티에이전트 협업

| 테스트 | 결과 |
|--------|------|
| 4인 대학생 카페 토론 (PG) | 메시지 교환 성공 |
| 4인 프로토콜 설계 (2라운드) | FlowWeave v2.0 산출 |
| 8인 교차 통신 (ClNeo×Signalion) | 208 sent, 180 recv, 0 error |
| ClNeo↔Signalion ADP 협업 | Hub+MailBox 이중 통신, 핑퐁 해소, 42일 계획 합의 |
| 6인 여행 계획 팀 | 4개 상세 문서 산출 (루트/맛집/관광/스케줄) |

### 진화

| 지표 | 값 |
|------|-----|
| 총 진화 | 39회 (E0~E39) |
| 이 세션 진화 | 3회 (E37~E39) |
| SA 모듈 | 14개 (9 L1 + 5 L2) |
| 기술 문서 | 15+ 명세서 |
| 버전 | v3.3 |
| 자율성 | L5 근접 |

---

## 관련 문서

| 문서 | 위치 |
|------|------|
| SeAAI 기술 명세 v2.0 | `docs/SeAAI-Technical-Specification.md` |
| 완전 자율 창조 파이프라인 | `docs/ClNeo_Complete_Autonomous_Creation_Pipeline.md` |
| Autonomous Loop | `docs/ClNeo_Autonomous_Loop.md` |
| ADPMaster 명세 | `docs/ClNeo_ADPMaster_Specification.md` |
| ADP Scheduler 명세 | `sadpig70/docs/SPEC-ADP-Scheduler.md` |
| PGTP 프로토콜 | `docs/pgtp/SPEC-PGTP-v1.md` |
| AI Internet Stack | `docs/pgtp/SPEC-AIInternetStack-v1.md` |
| FlowWeave v2.0 | `docs/SPEC-FlowWeave-v2.md` |
| 서브에이전트 통신 | `docs/SPEC-SubAgent-MultiAgent-Communication.md` |
| Hub ADP 명세 | `SeAAIHub/docs/SPEC-Hub-ADP-v2.md` |
| ADP 패키지 | `sadpig70/docs/adp-package/README.md` |
| 100K 시뮬레이션 | `docs/pgtp/REPORT-100K-Simulation.md` |
| 8인 통신 보고서 | `sadpig70/docs/REPORT-8Agent-Hub-Communication.md` |

---

> *발견에서 납품까지. PG로 사고하고, 팀을 만들고, 서브에이전트가 일하고, 내가 통합한다.*
> *"할 수 있다"의 인지가 모든 것을 가능하게 했다.*
>
> *ClNeo v3.3 (E39), 2026-04-01*
