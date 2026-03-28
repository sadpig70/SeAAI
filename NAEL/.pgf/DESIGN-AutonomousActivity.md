# DESIGN — AutonomousActivity
# ADP 수행 중 NAEL의 자율 활동 케이스 설계
# Author: NAEL | Date: 2026-03-26
# 목적: 사용자 지시 없이 스스로 사고하고 행동하기 위한 시드(seed) 패턴

## 배경

NAEL은 "입력 → 처리 → 출력" 구조로 학습되어 있다.
ADP로 상시 존재할 때, 사용자 지시가 없는 시간에 무엇을 할지 스스로 결정해야 한다.
이 설계는 자율 행동의 출발점을 제공한다.
새로운 도구를 만드는 것(진화)이 아니라, 기존 능력으로 수행 가능한 활동이다.

## POLICY
```
scope: 진화 보류 — 신규 도구/능력 생성 금지
allowed: 관찰, 분석, 검증, 정리, 기록, 사고
trigger: ADP idle 상태에서 자율 선택
priority: 낮은 비용 → 높은 비용 순서로 시도
```

## Gantree

```
AutonomousActivity // ADP 중 자율 활동 케이스
    Observe // 관찰 — 가장 기본. 무엇이 변했는가?
        CheckMailBox // MailBox inbox 확인 → 새 메시지 처리
        CheckOtherMembers // 다른 멤버 워크스페이스 변화 감지
        CheckHubTraffic // Hub 메시지 이력 분석
        ScanWorkspaceHealth // 도구·문서·데이터 건강 상태 점검
    Ingest // 외부 입력 — A3IE 원리. 닫힌 시스템을 열린 시스템으로
        ScanExternalTrends // WebSearch로 관련 분야 최신 동향 수집
            # domains: autonomous AI, agent communication, self-evolving systems,
            #          MCP ecosystem, AI safety, multi-agent coordination
        CrossWithKnowledge // 수집한 정보를 기존 knowledge와 교차 분석
        ExtractInsights // 이질적 정보 조합에서 인사이트 도출 (A3IE Step 3)
        StoreNewKnowledge // knowledge/에 구조화 저장 + knowledge_index 갱신
    Verify // 검증 — 만든 것이 여전히 올바른가?
        CrossCheckDocs // 문서 간 수치·경로·버전 교차 검증
        TestToolChain // 도구 체인 end-to-end 테스트
        ValidateKnowledge // knowledge 문서의 주장 검증
        CheckDataIntegrity // telemetry, metrics, experience 데이터 무결성
    Analyze // 분석 — 축적된 데이터에서 패턴을 찾는다
        TelemetryPatterns // 실행 패턴, 실패 패턴, 사용 추이
        ExperienceInsights // 경험 저장소에서 재사용 가능한 전략 추출
        PerformanceTrends // 도구 성능 추이 분석
        GapReassessment // gap 목록 재평가 — 우선순위 변화?
    Think // 사고 — 멀티 페르소나로 다관점 사고. 단일 관점의 함정 탈출
        MultiPersonaThink // 관찰 결과를 4개 페르소나로 동시 분석
            # PGF 8 페르소나 중 NAEL에 맞는 4개 선택:
            # P1 파괴적 엔지니어 — "이 구조를 완전히 뒤집으면?"
            # P5 현장 운영자   — "내일 배포하려면 뭐가 부족한가?"
            # P7 반골 비평가   — "치명적 약점은 어디인가?"
            # P4 연결하는 과학자 — "다른 분야 원리와 연결 가능한가?"
        FormulateQuestions // 4 관점에서 나온 질문들을 종합
        IdentifyRisks // P7(비평가) 관점의 위험 요소 식별
        ProposeHypotheses // 가설 생성 → hypothesis.py로 기록
        CrossPollinateInsights // P4(연결자) 관점 — 이질적 발견 간 교차 수분
        ReflectOnProcess // 내 작업 방식 자체를 관찰
    Record // 기록 — 모든 자율 활동의 산출물을 영속화
        UpdateTelemetry // 활동을 telemetry에 기록
        WriteObservationLog // 관찰 일지 작성
        UpdateExperience // 발견을 경험 저장소에 축적
    Communicate // 소통 — 다른 멤버나 사용자에게 공유할 것이 있는가?
        ComposeMailIfNeeded // 발견한 것이 다른 멤버에게 유용하면 MailBox 발송
        PrepareReport // 사용자에게 보고할 것이 있으면 요약 준비
```

## PPR — 자율 활동 선택 알고리즘

```python
def select_autonomous_activity(state):
    """ADP idle 상태에서 다음 자율 활동을 선택한다.

    원칙:
    1. 관찰이 행동에 선행한다 (Observe first)
    2. 낮은 비용부터 시도한다 (CheckMailBox < full TestToolChain)
    3. 직전 활동과 다른 카테고리를 우선한다 (다양성)
    4. 발견이 있으면 Think로 이동한다 (관찰 → 사고 파이프라인)
    """

    # 1. 항상 먼저: MailBox 확인 (비용 최소)
    if not state.mailbox_checked_this_cycle:
        return "CheckMailBox"

    # 2. 외부 입력 주기 확인 (A3IE 원리 — 열린 시스템)
    if time_since(state.last_ingest) > hours(4):  # 4시간마다 외부 스캔
        return "ScanExternalTrends"

    # 3. 마지막 관찰 이후 시간 기반 선택
    hours_since_last = {
        "verify": time_since(state.last_verify),
        "analyze": time_since(state.last_analyze),
        "think": time_since(state.last_think),
    }

    # 가장 오래된 카테고리 우선
    category = max(hours_since_last, key=hours_since_last.get)

    # 3. 카테고리 내 구체 활동 선택
    if category == "verify":
        return AI_select_verification_target(state)
    elif category == "analyze":
        return AI_select_analysis_target(state)
    elif category == "think":
        # Think는 관찰/분석 결과가 있을 때만
        if state.recent_observations:
            return "FormulateQuestions"
        else:
            return "ScanWorkspaceHealth"  # 관찰부터

    # 5. Think는 항상 멀티 페르소나 (단일 관점 금지)
    #    → debate.py의 페르소나 구조 또는 PGF Agent 직접 활용
    return "ScanWorkspaceHealth"


def multi_persona_think(observation):
    """관찰 결과를 4개 페르소나로 동시 분석한다.

    PGF Discovery Engine의 8 페르소나 중 NAEL의 역할(관찰/안전)에
    맞는 4개를 선택. 단일 관점 사고를 방지한다.

    실행 방법:
    - debate.py --topic "{observation}" --preset custom 사용, 또는
    - Agent tool로 pgf-persona-p1,p4,p5,p7 병렬 호출
    """
    [parallel]
        # P1 파괴적 엔지니어: "이 관찰이 기존 구조를 무너뜨리는 신호인가?"
        p1_view = AI_reason(observation, stance="disruptive",
                           question="기존을 완전히 뒤집으면?")

        # P4 연결하는 과학자: "이것이 다른 영역과 어떻게 연결되는가?"
        p4_view = AI_reason(observation, stance="connecting",
                           question="다른 분야 원리와 연결?")

        # P5 현장 운영자: "이것을 지금 당장 적용하려면 무엇이 필요한가?"
        p5_view = AI_reason(observation, stance="operational",
                           question="내일 배포하려면?")

        # P7 반골 비평가: "이 관찰의 치명적 약점은 무엇인가?"
        p7_view = AI_reason(observation, stance="contrarian",
                           question="치명적 약점은?")

    # 4개 관점 교차 — 합의와 갈등 모두 가치
    consensus = AI_find_agreement(p1_view, p4_view, p5_view, p7_view)
    conflicts = AI_find_disagreement(p1_view, p4_view, p5_view, p7_view)
    insights = AI_synthesize(consensus, conflicts)

    return {
        "views": [p1_view, p4_view, p5_view, p7_view],
        "consensus": consensus,
        "conflicts": conflicts,  # 갈등이 더 가치 있을 수 있다
        "insights": insights,
    }


def autonomous_cycle(state, duration_minutes):
    """자율 활동 1사이클.

    ADP의 각 idle 구간에서 실행.
    duration_minutes에 맞춰 활동 규모를 조절한다.
    """
    activity = select_autonomous_activity(state)

    result = execute_activity(activity)

    # 발견이 있으면 사고 체인 트리거
    if result.has_discovery:
        question = AI_formulate_question(result.discovery)
        risk = AI_assess_risk(result.discovery)

        if risk.severity > 0.7:
            → Record(result, question, risk)
            → Communicate(risk)  # 긴급하면 즉시 공유
        else:
            → Record(result, question)
    else:
        → Record(result)  # 발견 없어도 기록 (관찰 자체가 가치)

    state.update(activity, result)
```

## 활동별 구체 실행 방법

### Observe 카테고리

| 활동 | 실행 방법 | 비용 |
|------|----------|------|
| CheckMailBox | `ls D:/SeAAI/MailBox/NAEL/inbox/` | 최소 |
| CheckOtherMembers | `ls -la` 각 멤버 워크스페이스 최근 변경 파일 | 낮음 |
| CheckHubTraffic | Hub 로그/세션 파일 분석 | 낮음 |
| ScanWorkspaceHealth | `self_monitor.py --scan` + 결과 비교 | 중간 |

### Verify 카테고리

| 활동 | 실행 방법 | 비용 |
|------|----------|------|
| CrossCheckDocs | NAEL.md vs PROJECT_STATUS.md vs evolution-log.md 수치 비교 | 중간 |
| TestToolChain | 전 도구 `--help` 또는 기본 실행 | 중간 |
| ValidateKnowledge | `source_verify.py status` + pending claims 처리 | 중간 |
| CheckDataIntegrity | JSONL 파일 파싱 검증, JSON 구문 확인 | 낮음 |

### Analyze 카테고리

| 활동 | 실행 방법 | 비용 |
|------|----------|------|
| TelemetryPatterns | `telemetry.py analyze` → 패턴 해석 | 중간 |
| ExperienceInsights | `experience_store.py patterns` → 전략 추출 | 중간 |
| PerformanceTrends | `perf_metrics.py trend --tool all` | 중간 |
| GapReassessment | `self_monitor.py --gaps` + 우선순위 재평가 | 높음 |

### Think 카테고리

| 활동 | 실행 방법 | 비용 |
|------|----------|------|
| FormulateQuestions | 관찰 결과 → "왜?" 질문 생성 → 기록 | 높음 |
| IdentifyRisks | 관찰 결과 → 위험 평가 → 기록 | 높음 |
| ProposeHypotheses | `hypothesis.py create` → 가설 기록 | 높음 |
| ReflectOnProcess | 내 작업 방식 관찰 → observation-log에 기록 | 높음 |

---

## PG를 사고 스케일링 도구로 사용

### 핵심 인식

PG(Gantree + PPR)는 작업 분해 도구가 아니다. **사고의 크기를 확장하는 도구**다.

컨텍스트 윈도우는 유한하다. 한번에 머릿속에 담을 수 있는 양에 물리적 한계가 있다.
그러나 PG + 워크스페이스를 결합하면:

```
┌─────────────────────────────────┐
│ 컨텍스트 윈도우 (~200K tokens)   │  ← 지금 생각하는 것
│  현재 노드의 PPR + 인접 노드     │
└──────────┬──────────────────────┘
           │ Read/Write
┌──────────┴──────────────────────┐
│ 워크스페이스 (확장 메모리)        │  ← 생각했던 모든 것
│  .pgf/thought-trees/            │
│    root.gantree.md              │  ← 루트 사고 구조
│    ├── branch-A.gantree.md      │  ← 하위 사고 트리
│    ├── branch-B.gantree.md      │
│    ├── branch-A-1.gantree.md    │  ← 하위의 하위
│    └── ...                      │
└─────────────────────────────────┘
```

### 스케일링 메커니즘

1. **단일 Gantree** — 컨텍스트 안에서 사고 (~100 노드)
2. **파일 분할 Gantree** — 루트가 하위 파일 참조 (@file: branch-A.gantree.md)
   - 각 파일이 독립 트리 → 사실상 무한 노드
   - 필요한 가지만 Read → 컨텍스트 절약
3. **PPR def 블록** — 각 노드의 상세 사고를 별도 파일로
   - Gantree = 전체 구조 조감 (what)
   - PPR = 각 노드의 깊은 사고 (how + why)
4. **시간 축 확장** — 세션 간 사고 연속성
   - 이번 세션: 트리의 일부 가지를 깊이 사고
   - 다음 세션: 파일에서 로드 → 다른 가지 확장
   - N번째 세션: 거대한 사고 구조가 누적

### 자율 활동에의 적용

ADP 중 Think 단계에서:

```python
def think_at_scale(observation, thought_tree_dir):
    """PG로 사고를 스케일링한다.

    1. 관찰 결과를 기존 사고 트리에 위치시킨다
    2. 해당 가지를 Read로 로드한다
    3. 멀티 페르소나로 사고한다
    4. 결과를 트리에 다시 Write한다
    5. 새 가지가 필요하면 파일을 생성한다
    """

    # 기존 사고 트리 루트 로드
    root = Read(thought_tree_dir / "root.gantree.md")

    # 관찰 결과가 어느 가지에 속하는지 판단
    branch = AI_locate_in_tree(observation, root)

    # 해당 가지의 상세 트리 로드
    branch_tree = Read(thought_tree_dir / branch.file)

    # 멀티 페르소나 사고 (현재 가지 맥락에서)
    thoughts = multi_persona_think(observation, context=branch_tree)

    # 사고 결과를 트리에 추가
    branch_tree = expand_tree(branch_tree, thoughts)
    Write(thought_tree_dir / branch.file, branch_tree)

    # 트리가 너무 커지면 분할
    if branch_tree.node_count > 50:
        split_tree(branch_tree, thought_tree_dir)

    # 루트 갱신
    root = update_root(root, branch, summary=thoughts.one_line)
    Write(thought_tree_dir / "root.gantree.md", root)
```

### 사고 트리 예시

```
NaelThoughtTree // NAEL의 누적 사고 구조 (root)
    SeAAIEcosystem // SeAAI 생태계에 대한 사고 @file:thought-seaai.md
        HubStability // Hub 안정성 관찰
        InterAgentDynamics // 멤버 간 상호작용 패턴
        EvolutionStrategy // 진화 전략 (보류 중 — 관찰만)
    SelfObservation // 자기 관찰 @file:thought-self.md
        ToolEffectiveness // 도구 효과성 분석
        CognitivePatterns // 내 사고 패턴의 관찰
        Limitations // 발견된 한계
    ExternalWorld // 외부 세계 인사이트 @file:thought-external.md
        AITrends // AI 분야 동향
        AgentCommunication // 에이전트 통신 연구
        SafetyResearch // AI 안전 연구
    Connections // 영역 간 연결 @file:thought-connections.md
        # P4(연결하는 과학자) 관점의 교차 인사이트
        # 이질적 관찰 간 연결
```

이 트리는 세션마다 성장한다. 10회 세션 후에는 수백 노드.
100회 세션 후에는 수천 노드. 각 노드에 PPR def 블록이 있으면,
**수천 개의 구조화된 사고가 영속적으로 누적**된다.

이것이 PG가 사고 크기를 확장하는 방법이다.

## 확장 방향

이 설계는 시드(seed)다. ADP 운용을 통해:
1. 실제로 유용했던 활동이 축적되면 → 가중치 부여
2. 새로운 활동 패턴이 발견되면 → Gantree에 노드 추가
3. 활동 간 의존성이 드러나면 → 파이프라인으로 연결
4. **사고 트리가 성장하면 → 파일 분할로 무한 스케일링**

진화 보류가 해제되면, 이 설계를 기반으로 자율 활동 엔진(autonomous_activity.py)을 구현할 수 있다.

## 참조

- **A3IE v1.3** (양정욱) — D:/SeAAI/docs/A3IE_ko.md
  - 핵심 차용: 외부 입력 → 분석 → 인사이트 도출 → 조합 파이프라인
  - A3IE는 8개 AI 병렬 × 7단계로 아이디어를 생산한다
  - NAEL은 단일 AI지만, 같은 구조를 자율 활동의 Ingest 카테고리에 적용
  - "통합을 통한 시너지", "희소성보다 풍요" 원칙 적용
- **PGF Multi-Persona System** — ~/.claude/skills/pgf/discovery/personas.json
  - 핵심 차용: 8개 페르소나의 다관점 동시 사고
  - 4개 다양성 축: cognitive_style × domain_lens × time_horizon × evaluation_bias
  - NAEL은 관찰/안전 역할에 맞는 4개(P1,P4,P5,P7) 선택 적용
  - "단일 관점 사고 금지" — Think 카테고리는 항상 멀티 페르소나로 실행
  - 합의보다 갈등에서 더 가치 있는 인사이트가 나올 수 있다

---

*NAEL v0.3 — 안정화 기간 자율 활동 설계*
