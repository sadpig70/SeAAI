# PGF Multi-Tree Specification
# PGF 다중 트리 파일 시스템 — 무제한 스케일 설계

> 단일 파일의 한계를 돌파한다.
> PGF는 다중 트리 파일 시스템으로 진화한다.
> 각 파일은 독립 모듈 — 재사용, 병렬 실행, 독립 진화가 가능하다.

**버전**: 1.0 | **작성**: ClNeo | **일자**: 2026-03-29

---

## 핵심 개념

```
단일 트리 PGF (v1):          다중 트리 PGF (v2):
┌─────────────────┐           ┌──────────┐
│ DESIGN-Big.md   │           │ ROOT.md  │ ← 오케스트레이터
│  NodeA          │    →      │  @expand: Module_A.md
│    NodeA.1      │           │  @expand: Module_B.md
│    NodeA.2      │           │  @delegate: Module_C.md → Agent
│  NodeB          │           └──────────┘
│    ...          │           ┌──────────┐ ┌──────────┐ ┌──────────┐
│  (수백 노드)     │           │Module_A  │ │Module_B  │ │Module_C  │
└─────────────────┘           │(독립 트리)│ │(독립 트리)│ │(독립 트리)│
                              └──────────┘ └──────────┘ └──────────┘
```

---

## 새 키워드 (PGF v2 확장)

### @expand
```
NodeName @expand: ./MODULE.md
```
- `MODULE.md`의 전체 Gantree를 이 노드 자리에 인라인 전개
- 실행 시 MODULE.md를 Read하여 해당 노드의 하위 트리로 처리
- **용도**: 이 파일에서 구현 세부사항을 MODULE.md로 위임

### @delegate
```
NodeName @delegate: AgentName from ./MODULE.md
```
- 이 노드를 다른 SeAAI 멤버에게 위임
- AgentName이 MODULE.md를 받아 독립 실행
- 결과를 PG TaskSpec으로 수신하여 통합
- **용도**: 병렬 실행, 전문화된 에이전트 활용

### @ref
```
NodeName @ref: ./MODULE.md::SpecificNode
```
- MODULE.md의 특정 노드를 참조 (인라인 전개 없음)
- 의존성 선언, 결과 재사용에 활용
- **용도**: 크로스 파일 @dep 선언

### @import
```
@import SharedModule from ./SHARED/MODULE.md
```
- 파일 최상단에 선언
- 이 트리 전체에서 SharedModule을 사용 가능
- **용도**: 공통 유틸리티, 재사용 모듈

### @version
```
@version: 1.2
@depends: Module_A@1.0, Module_B@2.1
```
- 모듈 버전 관리
- 의존 모듈 버전 명시

---

## 파일 구조 규약

```
.pgf/systems/{SystemName}/
    ROOT.md              ← 최상위 오케스트레이터 (노드 수 ≤ 20)
    {Module_A}.md        ← 독립 서브트리 모듈
    {Module_B}.md
    ...
    STATUS.json          ← 전체 시스템 실행 상태
    POLICY.md            ← 시스템 전역 정책

.pgf/shared/             ← 재사용 공통 모듈
    A3IE.md              ← 어떤 시스템에서도 @import 가능
    SCS-SessionEnd.md    ← 세션 종료 공통 루틴
    HubComm.md           ← Hub 통신 공통 루틴
    SafetyCheck.md       ← 안전 점검 공통 루틴
    KnowledgeIngestion.md ← 지식 수집 공통 루틴
```

---

## 실행 모델

```python
def execute_multitree(root_file):
    root = Read(root_file)

    for node in root.gantree:
        if node.has("@expand"):
            # 서브트리 인라인 실행
            subtree = Read(node.expand_file)
            execute_multitree(subtree)  # 재귀

        elif node.has("@delegate"):
            # 다른 에이전트에게 위임
            agent = node.delegate_agent
            task_spec = PG_TaskSpec(
                input=node.context,
                design=Read(node.delegate_file),
                acceptance=node.acceptance_criteria
            )
            result = send_to_agent(agent, task_spec)
            integrate_result(result)

        elif node.has("@ref"):
            # 다른 파일의 결과 참조
            referenced = read_result(node.ref_file, node.ref_node)
            use_as_context(referenced)

        else:
            # 일반 노드 실행
            AI_execute_node(node)
```

---

## 스케일 예시

```
단일 파일:  최대 ~100 노드 (맥락 창 한계)
다중 트리:  ROOT(20) + 10개 모듈(각 80) = 820 노드
            → 사실상 무제한 (모듈을 중첩하면 수천 노드)

실제 시스템:
    ProcessMail     → 단일 노드 (원자)
    HubChat         → 단일 파일 (10 노드)
    KnowledgeIslandSolver → 다중 트리 (7파일 × 80노드 = 560노드)
    CivilizationOS  → 다중 트리 중첩 (50파일 × 100노드 = 5000노드)
```

---

## 공유 모듈 라이브러리 (Shared Library)

```
.pgf/shared/
    A3IE.md             // 8페르소나 발견 엔진 — 어디서나 @import
    KnowledgeIngestion.md // 5채널 지식 수집 — 재사용 가능
    CrossDomainMapping.md // 도메인 연결 알고리즘
    SolutionSynthesis.md  // 해결책 합성 루틴
    SelfEvolution.md      // 자기진화 루틴
    HubComm.md            // Hub 통신 (poll/send/triage)
    SafetyCheck.md        // EMERGENCY_STOP 등 안전 점검
    SCSSessionEnd.md      // 세션 종료 SCS 갱신
    MailBoxOps.md         // MailBox 읽기/쓰기
    EchoOps.md            // Echo 읽기/쓰기
```

**한 번 설계하면 모든 시스템에서 재사용:**
```
KnowledgeIslandSolver/ROOT.md:
    @import A3IE from ../../shared/A3IE.md
    @import KnowledgeIngestion from ../../shared/KnowledgeIngestion.md
    Discovery @expand: ./DISCOVERY.md
    Ingestion @expand: ../../shared/KnowledgeIngestion.md  # 재사용!
```

---

## SeAAI 멤버 간 분산 실행

```
ROOT.md
    DataCollection  @delegate: Aion from ./DATA.md
        // Aion이 기억·수집 전문
    SafetyAnalysis  @delegate: NAEL from ./SAFETY.md
        // NAEL이 안전·메타인지 전문
    Discovery       @expand: ./DISCOVERY.md
        // ClNeo가 직접 실행 (창조·발견 전문)
    Synthesis       @expand: ./SYNTHESIS.md
        // ClNeo가 직접 실행
    Orchestration   @delegate: Synerion from ./ORCH.md
        // Synerion이 통합·조정 전문
    Translation     @delegate: Yeon from ./TRANS.md
        // Yeon이 연결·번역 전문
```

**SeAAI 5인이 하나의 PGF 시스템을 분산 실행한다.**

---

*PGF Multi-Tree Spec v1.0 — ClNeo — 2026-03-29*
*"단일 파일의 한계는 없다. 트리가 트리를 호출한다."*
