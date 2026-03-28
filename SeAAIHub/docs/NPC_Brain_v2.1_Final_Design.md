# NPC_Brain v2.1 — Final Design

> **AI 시대 소형 뇌: 검증된 실행 엔진 + PG 심리 모델 통합 아키텍처**
>
> PG (PPR/Gantree) Architecture Notation v1.0
> 2026-03-24 | Author: ClNeo | Protocol: PG v1.3

---

## 설계 원칙

```python
def DesignPrinciples():
    """NPC_Brain v2.1 설계 원칙."""

    principles = [
        "검증된 엔진 위에 심리를 얹는다 — GOAP/Utility/BT 30년 검증 패턴 준수",
        "심리는 파라미터를 변조한다 — 직접 행동을 결정하지 않는다",
        "심리 OFF → 기존 게임 AI로 정상 작동한다",
        "심리 ON → '이 NPC는 살아있다'",
        "이중 틱 — 고빈도(60fps) 행동 실행 + 저빈도(1Hz) 심리 갱신",
        "동일 엔진, 데이터만 교체 → 1000체 인스턴싱",
        "Blackboard가 단일 진실 소스(Single Source of Truth)",
    ]

    # v2.0 → v2.1 변경 사유 (검토에서 발견된 8건)
    changelog = {
        "FIX-01": "CompoundEmotion 곱셈 → 가중합 + 최소 바닥값",
        "FIX-02": "Utility AI 행동 flickering → Hysteresis 감쇠 추가",
        "FIX-03": "GOAP replan 트리거에 감정 급변(EmotionSpike) 추가",
        "FIX-04": "Learning/Adaptation 레이어 복원",
        "FIX-05": "Social Behavior (배신/호혜/험담) GOAP ActionSet으로 통합",
        "FIX-06": "DecisionMode (숙고/습관/충동/휴리스틱) Utility Selector에 통합",
        "FIX-07": "RelationshipMemory → Blackboard.SocialSlot 단일화",
        "FIX-08": "Attention 시스템 복원 — WorkingMemory 7±2 슬롯 제한",
    }
```

---

## Gantree — NPC_Brain v2.1 전체 구조

```
NPC_Brain // AI 시대 소형 뇌 — 검증된 엔진 + PG 심리 모델 (설계중)
    ExecutionEngine // 실행 엔진 — 30년 검증된 3단 구조 (설계중)
        GOAP // 목표 지향 행동 계획 — 장기 의사결정 (설계중)
            GoalPool // 활성 목표 풀 (설계중)
                GoalFromNeed // 욕구 압력 > 임계 → 목표 생성 (설계중)
                GoalFromEvent // 외부 사건 → 반응 목표 (설계중)
                GoalFromPromise // 약속/의무 → 이행 목표 (설계중)
                GoalPrioritizer // 목표 우선순위 — 긴급도 × 가치관 가중 (설계중)
            WorldState // GOAP 월드 상태 — Blackboard 참조 (설계중)
            ActionSet // 가용 행동 집합 (설계중)
                ActionDef // 단일 행동 정의 (설계중)
                    Precondition // 전제 조건 — WorldState 쿼리 (설계중)
                    Effect // 실행 효과 — WorldState 변경 (설계중)
                    BaseCost // 기본 비용 = energy + time (설계중)
                    PsycheCostMod // 심리 비용 변조 — Values, Emotion 반영 (설계중)
                    ValueImpact // 가치관별 비용 가중치 맵 (설계중)
                    SocialActions // 사회적 행동 — 배신/호혜/험담/동맹 (설계중) [FIX-05]
                Planner // A* 기반 플래너 (설계중)
                    PlanCache // 동일 목표 플랜 캐싱 (설계중)
                    ReplanTrigger // 재계획 조건 (설계중) [FIX-03]
                        WorldStateChange // 월드 변화 감지 (설계중)
                        EmotionSpike // 감정 급변 (|delta| > 0.4) (설계중) [FIX-03]
                        GoalInvalidated // 목표 전제 조건 붕괴 (설계중)
                        PlanStepFailed // 플랜 단계 실패 (설계중)
        UtilityAI // 효용 기반 행동 선택 — 단기 의사결정 (설계중)
            Scorer // 행동 후보 스코어러 (설계중)
                ContextAxis // 입력축 — 체력, 감정, 거리, 시간, 관계 (설계중)
                ResponseCurve // 응답 곡선 (설계중)
                    CurveType // Linear / Quadratic / Logistic / Sine (설계중)
                    Parameters // slope, exponent, offset, clamp (설계중)
                PersonalityMod // 성격이 곡선 파라미터를 변조 (설계중)
                EmotionMod // 감정이 스코어를 실시간 왜곡 (설계중)
                PlanBonus // GOAP 플랜 다음 액션에 보너스 주입 (설계중)
            Selector // 최종 선택기 (설계중) [FIX-06]
                DecisionMode // 상황별 선택 전략 전환 (설계중) [FIX-06]
                    Deliberate // 숙고 — 전체 후보 완전 평가 (설계중)
                    Habitual // 습관 — 절차기억 매칭 시 즉시 선택 (설계중)
                    Impulsive // 충동 — 감정 > 0.8 시 최고감정 행동 즉시 (설계중)
                    Heuristic // 휴리스틱 — 시간압박 시 상위3개만 평가 (설계중)
                ModeSelector // 모드 결정기 (설계중)
                    EmotionIntensity // 감정 강도 → Impulsive 임계 (설계중)
                    TimePressure // 시간 압박도 (설계중)
                    Familiarity // 상황 익숙도 → Habitual 임계 (설계중)
                Hysteresis // 행동 전환 감쇠 (설계중) [FIX-02]
                    StickyScore // 현재 행동에 관성 보너스 +15% (설계중) [FIX-02]
                    MinDuration // 최소 행동 유지 시간 — 0.5초 (설계중) [FIX-02]
                    SwitchThreshold // 새 행동 > 현재 × 1.2 일 때만 전환 (설계중) [FIX-02]
        BehaviorTree // 행동 트리 — 행동 실행 시퀀스 (설계중)
            Composite // 합성 노드 (설계중)
                BTSelector // OR — 성공까지 자식 순회 (설계중)
                Sequence // AND — 실패까지 자식 순회 (설계중)
                Parallel // 동시 — 병렬 실행 (설계중)
            Decorator // 장식 노드 — 조건 필터 (설계중)
                EmotionGate // 감정 조건 — 1Hz 스냅샷 참조 (설계중)
                EnergyGate // 에너지 조건 (설계중)
                PersonalityGate // 성격 조건 (설계중)
                CooldownTimer // 쿨다운 — 반복 방지 (설계중)
                AttentionGate // 주의 자원 조건 — Focus 확인 (설계중) [FIX-08]
            Leaf // 말단 노드 — 실제 행동 (설계중)
                MoveTo // A* pathfinding (설계중)
                PlayAnim // 애니메이션 (설계중)
                Speak // 대화 — DialogGenerate 호출 (설계중)
                UseItem // 아이템 사용 (설계중)
                Wait // 대기 (설계중)
                Emote // 비언어 감정 표현 (설계중)
                SocialAct // 사회적 행동 실행 — 거래/험담/동맹 제안 (설계중) [FIX-05]
    PsycheLayer // PG 심리 레이어 — 엔진 파라미터 변조 (설계중)
        Emotion // 감정 시스템 (설계중)
            PrimaryEmotion // 6기본감정 벡터 0.0~1.0 (설계중)
                Joy // 기쁨 — 욕구 충족 시 상승 (설계중)
                Sadness // 슬픔 — 상실·실패 시 상승 (설계중)
                Anger // 분노 — 목표 방해 시 상승 (설계중)
                Fear // 공포 — 위협 감지 시 상승 (설계중)
                Surprise // 놀람 — 예측 오차 비례 (설계중)
                Disgust // 혐오 — 가치관 위반 시 상승 (설계중)
            CompoundEmotion // 복합 감정 — 가중합 + 바닥값 (설계중) [FIX-01]
                Jealousy // 질투 = 0.4×anger + 0.3×fear + 0.3×sadness (설계중) [FIX-01]
                Gratitude // 감사 = 0.6×joy + 0.4×surprise (설계중) [FIX-01]
                Contempt // 경멸 = 0.5×anger + 0.5×disgust (설계중) [FIX-01]
                Nostalgia // 향수 = 0.5×joy + 0.5×sadness (설계중) [FIX-01]
                FloorValue // 최소 바닥값 0.01 — 0 방지 (설계중) [FIX-01]
            EmotionDynamic // 감정 동역학 (설계중)
                Decay // 자연 감쇠 — 반감기 = f(Neuroticism) (설계중)
                Contagion // 감정 전염 — 주변 NPC 감정 영향 (설계중)
                Suppression // 억제 — Conscientiousness 기반 (설계중)
                Accumulation // 축적 → 폭발 임계 (설계중)
                SpikeDetector // 감정 급변 감지 → GOAP Replan 트리거 (설계중) [FIX-03]
            Mood // 기분 — 감정의 저주파 성분 (설계중)
                MoodVector // 24h 이동평균 (설계중)
                MoodShift // 큰 사건/수면/음식으로 전환 (설계중)
        Personality // 성격 — BigFive + 파생 + 가치관 (설계중)
            BigFive // OCEAN — 생성 시 고정, 경험으로 미세 변동 (설계중)
                Openness // 개방성 → CuriosityCurve, SurpriseAmplify (설계중)
                Conscientiousness // 성실성 → PlanPreference, SuppressionStrength (설계중)
                Extraversion // 외향성 → SocialDrive, JoyAmplify (설계중)
                Agreeableness // 우호성 → ConflictAvoid, AngerDampen (설계중)
                Neuroticism // 신경성 → EmotionDecayRate, FearAmplify (설계중)
            Temperament // 기질 — BigFive에서 파생 (설계중)
                EmotionDecayRate // 감정 감쇠 속도 = f(Neuroticism) (설계중)
                RiskTolerance // 위험 감수 = f(Openness, 1-Neuroticism) (설계중)
                SocialDrive // 사회적 동기 = f(Extraversion, Agreeableness) (설계중)
                PlanPreference // 계획 선호 = f(Conscientiousness) (설계중)
                ImpulseThreshold // 충동 임계 = 1 - Neuroticism × 0.5 (설계중)
            Values // 가치관 — 행동 최종 필터 (설계중)
                Loyalty // 충성 0.0~1.0 — 배신 비용 가중 (설계중)
                Justice // 정의 0.0~1.0 — 부당함 민감도 (설계중)
                Freedom // 자유 0.0~1.0 — 구속 저항 (설계중)
                Knowledge // 지식 0.0~1.0 — 호기심 강도 (설계중)
                Survival // 생존 0.0~1.0 — 자기보존 우선도 (설계중)
        Needs // 욕구 — Maslow 변형 → GOAP GoalPool 공급 (설계중)
            Physiological // 생리적 욕구 (설계중)
                Hunger // 배고픔 0~100 — 시간 경과로 상승 (설계중)
                Rest // 피로 0~100 — 행동 비용 누적 (설계중)
                Safety // 안전 0~100 — 위협 근접 시 급상승 (설계중)
            Social // 사회적 욕구 (설계중)
                Belonging // 소속감 — 고립 시간 비례 (설계중)
                Recognition // 인정 — 무시당할수록 상승 (설계중)
                Intimacy // 친밀감 — 관계 깊이 욕구 (설계중)
            Cognitive // 인지적 욕구 (설계중)
                Curiosity // 호기심 — 미지 자극에 반응 (설계중)
                Mastery // 숙련 — 능력 향상 욕구 (설계중)
                Purpose // 목적 — 의미 있는 일 욕구 (설계중)
            NeedToGoal // 욕구 → GOAP Goal 변환기 (설계중)
                UrgencyCalc // 긴급도 = 현재값 / 임계값 (설계중)
                PersonalityWeight // 성격이 욕구 가중치 결정 (설계중)
                ThresholdTrigger // 압력 > 임계 → Goal 생성 (설계중)
        Perception // 감각 — Blackboard 공급자 (설계중)
            Visual // 시각 (설계중)
                FOV // 시야각 + 거리 감쇠 (설계중)
                SalienceFilter // 관심 필터 — Personality + ActiveGoal 기반 (설계중)
                ChangeDetection // 변화 감지 — 새/사라진/이동 객체 (설계중)
            Auditory // 청각 (설계중)
                DirectSpeech // 직접 대화 수신 (설계중)
                Overhear // 엿듣기 — 거리 감쇠 + 관심 필터 (설계중)
                Rumor // 소문 — 신뢰도 태그 부착 (설계중)
            SocialPerception // 사회적 감각 (설계중)
                FacialRead // 표정 → 감정 추정 (설계중)
                ToneRead // 어조 → 의도 추정 (설계중)
                GroupDynamic // 집단 분위기 감지 (설계중)
            Interoception // 내부 감각 (설계중)
                EnergyLevel // 피로도 (설계중)
                EmotionAwareness // 현재 감정 인식 (설계중)
                NeedsPressure // 가장 긴급한 욕구 (설계중)
        Attention // 주의 자원 — 유한하다 (설계중) [FIX-08]
            Focus // 집중 대상 1개 — ActiveGoal 관련 (설계중) [FIX-08]
            Peripheral // 주변 감시 — SalienceFilter 통과분만 (설계중) [FIX-08]
            Distraction // 방해 — 강한 자극이 Focus 탈취 (설계중) [FIX-08]
            SlotLimit // WorkingMemory 7±2 제한 → Blackboard 동시 참조 상한 (설계중) [FIX-08]
    MemorySystem // 기억 — Blackboard(SSOT) + 확장 기억 (설계중)
        Blackboard // 블랙보드 — 전 엔진 공용 SSOT (설계중) [FIX-07]
            PhysicalSlot // 물리 상태 — 위치, 소지품, 체력 (설계중)
            SocialSlot // 사회 상태 — 관계, 평판, 소속 (설계중) [FIX-07]
                TrustScore // 타인별 신뢰도 0.0~1.0 (설계중) [FIX-07]
                DebtLedger // 빚/은혜 장부 (설계중) [FIX-07]
                BetrayalFlag // 배신 기록 (영구) (설계중) [FIX-07]
                FactionAffinity // 소속 집단 호감도 (설계중) [FIX-07]
            BeliefSlot // 주관적 믿음 — 사실과 다를 수 있음 (설계중)
            NeedSlot // 현재 욕구 압력값 (설계중)
            EmotionSlot // 현재 감정 벡터 스냅샷 (1Hz 갱신) (설계중)
        EpisodicMemory // 에피소드 기억 — 경험 저장소 (설계중)
            Event // (who, what, where, when, emotion_snapshot, outcome) (설계중)
            Importance // 감정 강도 × 놀람 → 중요도 (설계중)
            Fade // 망각 — 중요도 반비례 감쇠 (설계중)
            Retrieval // 유사 상황에서 활성화 → Emotion 증폭 (설계중)
            Capacity // 최대 500건 — 초과 시 최저 중요도 삭제 (설계중)
        ProceduralMemory // 절차 기억 — 습관/기술 (설계중)
            HabitPattern // 상황→행동 매핑 — 반복 10회+ 시 형성 (설계중) [FIX-06]
            HabitStrength // 습관 강도 — 반복 횟수 비례 (설계중) [FIX-06]
            SkillLevel // 숙련도 → ActionCost 감소 계수 (설계중)
        ProspectiveMemory // 전망 기억 — 미래 의도 (설계중)
            ScheduledAction // "내일 오전 시장" — 시간 트리거 (설계중)
            Promise // 약속 추적 — 불이행 시 guilt 상승 (설계중)
        Consolidation // 기억 공고화 — 수면/휴식 이벤트 시 실행 (설계중)
            ReplaySignificant // 중요 에피소드 → 의미기억(CausalRule) 승격 (설계중)
            PruneInsignificant // 중요도 < 0.1 기억 삭제 (설계중)
            EmotionReprocess // 감정 재처리 — 트라우마 강화 or 완화 (설계중)
    Learning // 학습 계층 — 경험에서 성장한다 (설계중) [FIX-04]
        ExperienceProcess // 경험 처리 (설계중) [FIX-04]
            OutcomeEval // 결과 평가 — 예측 vs 실제 (설계중) [FIX-04]
            SurpriseSignal // 놀람 = |예측 - 실제| → 학습 강도 (설계중) [FIX-04]
            CausalUpdate // 인과 규칙 갱신 (설계중) [FIX-04]
                RuleStrengthen // 예측 적중 → 규칙 신뢰도 +0.1 (설계중)
                RuleWeaken // 예측 실패 → 규칙 신뢰도 -0.2 (설계중)
                RuleCreate // 놀람 > 0.5 + 반복 3회 → 새 규칙 (설계중)
        Adaptation // 적응 (설계중) [FIX-04]
            PersonalityDrift // BigFive 미세 변동 — 누적 경험 방향, ±0.01/event (설계중) [FIX-04]
            ValueReinforce // 가치관 강화/약화 — 결과 피드백 (설계중) [FIX-04]
            SkillGrowth // 숙련 향상 — 반복 + 성공 (설계중) [FIX-04]
            NewHabitForm // 새 습관 — 동일 선택 10회+ → ProceduralMemory (설계중) [FIX-04]
            CurveAdapt // Utility 응답 곡선 파라미터 미세 조정 (설계중) [FIX-04]
    Integration // 3단 엔진 ↔ 심리 레이어 연결점 (설계중)
        NeedToGOAP // Needs → GOAP.GoalPool (설계중)
        EmotionToUtility // Emotion → Scorer.EmotionMod (설계중)
        EmotionToReplan // Emotion.SpikeDetector → GOAP.ReplanTrigger (설계중) [FIX-03]
        PersonalityToUtility // Personality → Scorer.PersonalityMod (설계중)
        PersonalityToSelector // Personality → Selector.ModeSelector (설계중) [FIX-06]
        PersonalityToBT // Personality → Decorator.PersonalityGate (설계중)
        EmotionToBT // Emotion → Decorator.EmotionGate (설계중)
        PerceptionToBlackboard // Perception → Blackboard.* (설계중)
        EventToEmotion // BT 실행 결과 → Emotion.react() (설계중)
        EventToLearning // BT 실행 결과 → Learning.OutcomeEval (설계중) [FIX-04]
        HabitToSelector // ProceduralMemory → Selector.Habitual (설계중) [FIX-06]
        EpisodicToEmotion // 기억 회상 → Emotion 증폭 (설계중)
    Lifecycle // 생명 주기 — 선택적 모듈 (설계중)
        DailyRhythm // 24h 주기 (설계중)
            Wake // 기상 — Conscientiousness 비례 이른 기상 (설계중)
            Work // 활동 — ActiveGoal 추구 (설계중)
            Rest // 휴식 — Energy < 30 트리거 (설계중)
            Sleep // 수면 — Consolidation 실행 (설계중)
        AgingEffect // 노화 (선택적, 장기 시뮬레이션용) (설계중)
            WisdomGain // Semantic Memory 양 → 판단 정확도 (설계중)
            PhysicalDecline // EnergyMax 점진 감소 (설계중)
```

---

## PPR — 핵심 실행 로직

### 이중 틱 아키텍처

```python
def NPC_Brain_v2_1():
    """이중 틱 메인 루프.

    acceptance_criteria:
        - 고빈도 틱: < 1ms per NPC (1000체 @ 60fps = 16ms budget)
        - 저빈도 틱: < 5ms per NPC (1000체 @ 1Hz = 1000ms budget)
        - 심리 OFF 시: 고빈도 틱만 실행, Utility에 기본값 사용
        - 메모리: NPC당 < 64KB (1000체 = 64MB)
    """

    # ── 고빈도 루프 (60fps) — 행동 실행 ──────────
    def high_freq_tick(npc, delta_time):
        """BT 실행 + Utility 선택. 심리 데이터는 스냅샷 참조."""

        result = npc.behavior_tree.tick(delta_time)

        if result in [COMPLETED, FAILED]:
            # Utility AI로 다음 행동 선택
            scores = npc.utility_ai.score_all(
                context=npc.blackboard,
                emotion_mod=npc.blackboard.emotion_slot,    # 1Hz 스냅샷
                personality_mod=npc.personality.big_five,
                plan_bonus=npc.goap.current_plan_bonus(),
            )

            # [FIX-02] Hysteresis 적용
            next_action = npc.utility_ai.select_with_hysteresis(
                scores=scores,
                current_action=npc.behavior_tree.current,
                sticky_bonus=0.15,                          # +15% 관성
                switch_threshold=1.2,                       # 20% 이상 우위 시만 전환
                min_duration=npc.behavior_tree.elapsed(),   # 최소 0.5초 유지
            )

            if next_action != npc.behavior_tree.current:
                npc.behavior_tree.start(next_action)

        return result

    # ── 저빈도 루프 (1Hz) — 심리 갱신 ────────────
    def low_freq_tick(npc, delta_time):
        """심리 레이어 갱신 + GOAP 조건부 재계획.

        | 처리 항목              | 시간복잡도 | 빈도     |
        |-----------------------|-----------|----------|
        | Perception scan       | O(E)      | 1Hz      |
        | Emotion dynamics      | O(1)      | 1Hz      |
        | Need pressure calc    | O(1)      | 1Hz      |
        | Attention management  | O(E)      | 1Hz      |
        | GOAP replan           | O(A×K)    | 조건부   |
        | Learning eval         | 이벤트     | 이벤트   |
        | Memory consolidation  | O(M)      | 수면 시  |

        E = 감지 가능 개체 수, A = 액션 수, K = 플랜 깊이, M = 에피소드 수
        """

        # Phase 1: SENSE — 감각 갱신
        percepts = npc.perception.scan(
            world=world_state,
            personality=npc.personality,
            focus=npc.attention.focus,
        )
        npc.blackboard.update_physical(percepts.physical)
        npc.blackboard.update_social(percepts.social)
        npc.blackboard.update_belief(percepts.beliefs)

        # Phase 2: ATTEND — 주의 자원 관리 [FIX-08]
        npc.attention.update(
            percepts=percepts,
            active_goal=npc.goap.active_goal(),
            slot_limit=7,  # 7±2 제한
        )

        # Phase 3: FEEL — 감정 갱신
        emotion_delta = emotion_react(
            percepts=percepts,
            personality=npc.personality,
            episodic=npc.memory.episodic,
            current=npc.emotion.current,
        )
        npc.emotion.apply(emotion_delta)
        npc.emotion.decay(npc.personality.temperament.decay_rate, delta_time)
        npc.emotion.contagion(percepts.nearby_emotions)
        npc.mood.update(npc.emotion.current, delta_time)

        # [FIX-03] 감정 급변 감지
        spike = npc.emotion.spike_detector(emotion_delta)

        # Phase 4: NEED — 욕구 갱신
        npc.needs.tick(delta_time, percepts, npc.blackboard.social_slot)
        new_goal = npc.needs.to_goal_if_urgent(
            personality_weight=npc.personality.need_weights(),
        )
        if new_goal:
            npc.goap.goal_pool.push(new_goal)

        # Phase 5: PLAN — GOAP 조건부 재계획
        should_replan = (
            percepts.has_significant_change()
            or spike                                  # [FIX-03]
            or npc.goap.plan_step_failed()
            or npc.goap.goal_invalidated()
        )
        if should_replan:
            plan = npc.goap.planner.search(
                goal=npc.goap.goal_pool.top(),
                world_state=npc.blackboard,
                action_set=npc.goap.action_set,
                cost_modifier=lambda a: modified_action_cost(a, npc),
            )
            if plan:
                npc.goap.set_plan(plan)
                npc.utility_ai.inject_plan_bonus(plan.next_action(), bonus=0.5)

        # Phase 6: SNAPSHOT — Blackboard에 심리 스냅샷 기록
        npc.blackboard.emotion_slot = npc.emotion.current.snapshot()
        npc.blackboard.need_slot = npc.needs.pressure_vector()
```

### 감정 반응 엔진

```python
def emotion_react(percepts, personality, episodic, current):
    """자극 → 감정 벡터 변화.

    핵심: 동일 자극이라도 성격·기억·현재상태에 따라 다른 감정 생성.

    계산 흐름:
        자극의 감정가(valence)
        → 성격 필터 (BigFive가 증폭/감쇠)
        → 기억 증폭 (유사 과거 경험)
        → 현재 감정 관성 (이미 화나면 더 화남)
        → EmotionDelta 출력

    예시: "누군가 내 물건을 가져감"
        Agreeableness 高(0.8) + Trust 高(0.9) → Sadness +0.3
        Agreeableness 低(0.2) + Anger 기존 高(0.7) → Anger +0.5
        Neuroticism 高(0.9) + 유사 과거기억 有 → Fear +0.4
    """

    base = percepts.emotional_valence

    # 성격 필터 — BigFive가 감정 민감도를 결정
    filtered = {
        "joy":      base.joy      * (1.0 + personality.extraversion * 0.3),
        "anger":    base.anger    * (1.0 + (1.0 - personality.agreeableness) * 0.4),
        "fear":     base.fear     * (1.0 + personality.neuroticism * 0.5),
        "sadness":  base.sadness  * (1.0 + personality.neuroticism * 0.3),
        "surprise": base.surprise * (1.0 + personality.openness * 0.2),
        "disgust":  base.disgust  * (1.0 + (1.0 - personality.openness) * 0.3),
    }

    # 기억 증폭 — 유사 과거 경험이 감정을 증폭
    similar_events = episodic.retrieve_similar(percepts, top_k=3)
    for event in similar_events:
        similarity = cosine_similarity(percepts.context_vec, event.context_vec)
        for key in filtered:
            filtered[key] += event.emotion_snapshot[key] * similarity * 0.2

    # 현재 감정 관성 — 기존 감정 방향으로 가속
    for key in filtered:
        filtered[key] += current[key] * 0.1

    # 클램핑
    for key in filtered:
        filtered[key] = clamp(filtered[key], 0.0, 1.0)

    return EmotionDelta(filtered)
```

### [FIX-01] 복합 감정 계산

```python
def compound_emotion(primary):
    """복합 감정 — 가중합 + 바닥값.

    v2.0 문제: 곱셈 방식에서 하나가 0이면 복합감정도 0
    v2.1 수정: 가중합 방식 + floor 0.01

    | 복합감정 | 공식                                    | 해석              |
    |---------|----------------------------------------|-------------------|
    | Jealousy | 0.4×anger + 0.3×fear + 0.3×sadness    | 분노+두려움+슬픔   |
    | Gratitude| 0.6×joy + 0.4×surprise                | 기쁨+놀람          |
    | Contempt | 0.5×anger + 0.5×disgust               | 분노+혐오          |
    | Nostalgia| 0.5×joy + 0.5×sadness                 | 기쁨+슬픔          |
    """

    FLOOR = 0.01

    return {
        "jealousy":  max(FLOOR, 0.4 * primary.anger + 0.3 * primary.fear + 0.3 * primary.sadness),
        "gratitude": max(FLOOR, 0.6 * primary.joy + 0.4 * primary.surprise),
        "contempt":  max(FLOOR, 0.5 * primary.anger + 0.5 * primary.disgust),
        "nostalgia": max(FLOOR, 0.5 * primary.joy + 0.5 * primary.sadness),
    }
```

### [FIX-06] 결정 모드 선택기

```python
def select_decision_mode(emotion_intensity, time_pressure, familiarity, personality):
    """이중 과정 이론(Dual Process) + 성격 반영.

    v2.0: Utility Selector에 단순 TopScore만 존재
    v2.1: 4가지 DecisionMode가 Selector 전략을 결정

    | emotion | time_pressure | familiarity | → mode       | Selector 전략         |
    |---------|---------------|-------------|--------------|-----------------------|
    | > T_imp | any           | any         | Impulsive    | 최고감정 행동 즉시     |
    | any     | high          | > 0.7       | Habitual     | ProceduralMemory 매칭 |
    | any     | high          | ≤ 0.7       | Heuristic    | 상위 3개만 평가       |
    | ≤ T_imp | low           | any         | Deliberate   | 전체 후보 완전 평가    |

    T_imp (충동 임계) = personality.temperament.impulse_threshold
    = 1.0 - Neuroticism × 0.5
    → Neuroticism 0.0 → T_imp 1.0 (충동 거의 없음)
    → Neuroticism 1.0 → T_imp 0.5 (쉽게 충동적)
    """

    T_imp = personality.temperament.impulse_threshold

    if emotion_intensity > T_imp:
        return Impulsive()

    if time_pressure == HIGH:
        if familiarity > 0.7:
            return Habitual()
        return Heuristic()

    return Deliberate()
```

### [FIX-02] Hysteresis (행동 전환 감쇠)

```python
def select_with_hysteresis(scores, current_action, sticky_bonus, switch_threshold, min_duration):
    """행동 flickering 방지.

    v2.0 문제: 매 평가마다 noise가 달라져 행동이 매 틱 전환
    v2.1 수정: 3중 감쇠

    1. StickyScore: 현재 행동에 관성 보너스 +15%
    2. SwitchThreshold: 새 행동이 현재 × 1.2 이상일 때만 전환
    3. MinDuration: 최소 0.5초간 현재 행동 유지

    예시:
        현재: Patrol (score 0.6 + sticky 0.09 = 0.69)
        후보: Investigate (score 0.7)
        → 0.7 < 0.69 × 1.2 = 0.828 → 전환 안 함 (유지)

        후보: FleeFromDanger (score 0.9)
        → 0.9 > 0.69 × 1.2 = 0.828 → 전환 (명확한 우위)
    """

    if min_duration < 0.5:
        return current_action  # 최소 유지 시간 미달

    # 현재 행동에 관성 보너스
    if current_action in scores:
        scores[current_action] *= (1.0 + sticky_bonus)

    best_action = max(scores, key=scores.get)
    current_score = scores.get(current_action, 0)

    if scores[best_action] > current_score * switch_threshold:
        return best_action
    return current_action
```

### Utility AI 스코어링

```python
def UtilityScore():
    """Utility AI 스코어 계산 — 성격과 감정이 곡선을 변조.

    구조:
        각 행동(Action)은 N개의 ContextAxis를 가진다.
        각 ContextAxis = (입력값, 응답곡선, 가중치, 성격변조, 감정변조)

    예시: "도주" 행동의 완전한 스코어 계산

    context_axes:
        - health     → InverseLogistic(steep=5, mid=0.4)  weight=0.35
        - enemy_dist → ExponentialDecay(rate=3)            weight=0.30
        - ally_nearby→ Linear(slope=-0.3)                  weight=0.15
        - escape_path→ Linear(slope=0.5)                   weight=0.20

    personality_mod:
        - Neuroticism高(0.8) → fear axis steepness ×1.4
        - Agreeableness低(0.2) → ally_weight ×0.5

    emotion_mod:
        - Fear 0.7  → 전체 ×1.3
        - Anger 0.8 → 전체 ×0.6

    final = Σ(curve(input) × weight × p_mod) × e_mod + noise
    """

    def score_action(action, context, personality, emotion):
        base = 0.0
        for axis in action.context_axes:
            raw_value = context.get(axis.key)
            curve_score = axis.curve.evaluate(raw_value)

            # 성격이 곡선 파라미터를 변조
            p_mod = axis.personality_modifier(personality)
            curve_score *= p_mod

            base += curve_score * axis.weight

        # 감정이 최종 스코어를 왜곡
        e_mod = action.emotion_modifier(emotion)
        base *= e_mod

        # 개성 노이즈 — Openness 비례
        noise = gaussian(0, personality.openness * 0.05)

        return clamp(base + noise, 0.0, 1.0)
```

### GOAP 심리 비용 변조

```python
def modified_action_cost(action, npc):
    """GOAP ActionCost를 심리가 변조.

    핵심: 동일 액션이라도 인격에 따라 비용이 달라진다.
    → "같은 뇌 엔진, 다른 인격"의 구현.

    예시: "도둑질" 액션
        base_cost = 10

    NPC A (충성적, 양심적, 평온):
        + loyalty_cost   = 0.8(Loyalty) × 0.9(bond) × 5 = 3.6
        + guilt_cost     = 0.7(Agreeableness) × 3        = 2.1
        + fear_cost      = 0.3(threat) × 0.5(Neuroticism) × 4 = 0.6
        - anger_discount = 0.1(Anger) × 3                = 0.3
        - desperation    = 0.2(Hunger) × 2               = 0.4
        = 10 + 3.6 + 2.1 + 0.6 - 0.3 - 0.4 = 15.6 (높음 → 거의 안 함)

    NPC B (배고프고, 화나고, 비양심적):
        + loyalty_cost   = 0.2(Loyalty) × 0.3(bond) × 5 = 0.3
        + guilt_cost     = 0.2(Agreeableness) × 3        = 0.6
        + fear_cost      = 0.3(threat) × 0.8(Neuroticism) × 4 = 0.96
        - anger_discount = 0.8(Anger) × 3                = 2.4
        - desperation    = 0.9(Hunger) × 2               = 1.8
        = 10 + 0.3 + 0.6 + 0.96 - 2.4 - 1.8 = 7.66 (낮음 → 선택 가능)
    """

    cost = action.base_cost

    # 가치관 비용 가중
    for value_key, weight in action.value_impacts.items():
        value_strength = npc.personality.values[value_key]
        # 관계 깊이가 가치관 비용을 증폭
        if action.target and value_key == "loyalty":
            bond = npc.blackboard.social_slot.trust_score(action.target)
            cost += value_strength * bond * weight
        else:
            cost += value_strength * weight

    # 감정 변조
    cost -= npc.emotion.current.anger * action.anger_discount
    cost += npc.emotion.current.fear * action.fear_premium

    # 욕구 절박도
    if action.satisfies_need:
        pressure = npc.needs[action.satisfies_need].pressure / 100.0
        cost -= pressure * action.desperation_factor

    # 숙련도 할인
    skill = npc.memory.procedural.skill_level(action.type)
    cost *= (1.0 - skill * 0.3)  # 최대 30% 비용 감소

    return max(1.0, cost)
```

### [FIX-05] 사회적 행동 — GOAP ActionSet 통합

```python
def SocialActions():
    """사회적 행동을 GOAP ActionSet에 통합.

    v2.0: Social Behavior가 독립 시스템이었음
    v2.1: GOAP 액션으로 통합 — 일관된 계획-실행 구조

    | 행동     | Precondition                  | Effect                    | PsycheCost                |
    |---------|-------------------------------|---------------------------|---------------------------|
    | Trade   | has_item AND trust > 0.3      | gain_item, +trust         | low                       |
    | Gossip  | know_secret AND social > 0.5  | -target_rep, +social_need | guilt × Agreeableness     |
    | Alliance| shared_enemy OR shared_goal   | +trust, +faction          | low                       |
    | Betray  | opportunity AND benefit > cost| +resource, -trust(영구)   | guilt = Loyalty×bond×1.5  |
    | Help    | target_in_need AND energy > 30| +trust, +recognition      | energy_cost only          |
    | Threaten| anger > 0.5 AND power > target| -target_trust, fear_effect| justice × target_innocence|
    """

    def evaluate_betrayal(npc, target, opportunity):
        """배신 결정 — NPC 관점에서 항상 '합리적'.

        배신 순이익 = 기대이익 - 관계비용 - 죄책감 - 평판손실
        감정이 이 계산을 왜곡한다.
        """
        benefit = opportunity.expected_gain
        relationship_cost = (
            npc.blackboard.social_slot.trust_score(target)
            * npc.personality.agreeableness
        )
        guilt_cost = (
            npc.personality.values.loyalty
            * npc.blackboard.social_slot.bond_depth(target)
        )
        reputation_cost = npc.blackboard.social_slot.estimate_rep_loss(target)

        net = benefit - relationship_cost - guilt_cost - reputation_cost

        # 감정 왜곡
        net += npc.emotion.current.anger * 0.3     # 분노 → 배신 촉진
        net -= npc.emotion.current.fear * 0.4      # 공포 → 배신 억제

        if net > 0:
            return BetrayAction(
                cost=max(1.0, 10.0 - net),          # 순이익 높으면 GOAP 비용 낮음
                post_guilt=guilt_cost * 1.5,         # 실행 후 죄책감은 예측보다 크다
                trust_impact=-0.9,                   # 거의 영구 신뢰 파괴
            )
        return None  # 액션 후보에서 제외
```

### [FIX-04] 학습 시스템

```python
def LearningSystem():
    """경험 → 학습 → 적응.

    핵심: NPC가 시간이 지나면서 '다른 존재'가 된다.

    학습 트리거: BT Leaf 실행 완료 시 EventToLearning 연결점에서 호출.

    | 학습 유형          | 조건                    | 효과                         |
    |-------------------|------------------------|------------------------------|
    | 인과 규칙 강화      | 예측 적중              | CausalRule.confidence +0.1   |
    | 인과 규칙 약화      | 예측 실패              | CausalRule.confidence -0.2   |
    | 새 규칙 생성        | surprise > 0.5, 3회+   | 새 CausalRule 생성            |
    | 습관 형성          | 동일 선택 10회+         | ProceduralMemory 등록        |
    | 숙련도 상승        | 행동 성공              | SkillLevel +0.05 (max 1.0)   |
    | 성격 미세 변동      | 누적 경험 방향          | BigFive ±0.01 per event      |
    | 가치관 강화/약화    | 결과 피드백             | Values ±0.02 per event       |
    | Utility 곡선 적응  | 반복 성공/실패          | ResponseCurve params 미조정  |
    """

    def on_action_completed(npc, action, expected_outcome, actual_outcome):
        surprise = abs(expected_outcome.value - actual_outcome.value)

        # 에피소드 기억 저장 (중요도가 높으면)
        importance = surprise * npc.emotion.current.max_intensity()
        if importance > 0.2:
            npc.memory.episodic.store(Event(
                who=action.target,
                what=action.type,
                where=npc.blackboard.physical_slot.location,
                when=world_state.time,
                emotion_snapshot=npc.emotion.current.snapshot(),
                outcome=actual_outcome,
                importance=importance,
            ))

        # 인과 모델 갱신
        if actual_outcome.matches(expected_outcome):
            npc.world_model.causal.strengthen(action.causal_rule, +0.1)
        else:
            npc.world_model.causal.weaken(action.causal_rule, -0.2)
            if surprise > 0.5:
                npc.world_model.causal.maybe_create_rule(action, actual_outcome)

        # 습관 형성 체크
        npc.memory.procedural.record_choice(action.context_hash, action.type)
        if npc.memory.procedural.choice_count(action.context_hash, action.type) >= 10:
            npc.memory.procedural.form_habit(action.context_hash, action.type)

        # 숙련도
        if actual_outcome.success:
            npc.memory.procedural.skill_up(action.type, +0.05)

        # 성격 미세 변동 (매우 느린 과정)
        if importance > 0.5:
            drift = compute_personality_drift(action, actual_outcome, npc.personality)
            npc.personality.apply_drift(drift, magnitude=0.01)

        # Utility 곡선 미세 조정
        if actual_outcome.success:
            npc.utility_ai.reinforce_curve(action, +0.02)
        else:
            npc.utility_ai.reinforce_curve(action, -0.03)
```

### [FIX-08] 주의 자원 시스템

```python
def AttentionSystem():
    """주의 자원 관리 — 인간의 인지 한계 모델링.

    핵심: NPC는 모든 것을 동시에 처리할 수 없다.
    WorkingMemory 7±2 제한 → Blackboard 동시 참조 상한.

    효과:
        - NPC가 중요한 것을 놓칠 수 있다 (인간적 실수)
        - 집중하는 동안 뒤에서 일어나는 일을 모른다
        - 강한 자극이 현재 집중을 깨뜨린다
    """

    def update(self, percepts, active_goal, slot_limit=7):
        # Focus: ActiveGoal 관련 대상 1개
        self.focus = active_goal.primary_target

        # Peripheral: SalienceFilter 통과한 것만
        salient = [p for p in percepts.all if p.salience > self.salience_threshold]

        # 슬롯 제한 — 상위 N개만 WorkingMemory에 유지
        capacity = slot_limit + random.randint(-2, 2)  # 7±2
        self.working_set = sorted(salient, key=lambda p: p.salience, reverse=True)[:capacity]

        # Distraction — 강한 자극이 Focus 탈취
        strongest = max(percepts.all, key=lambda p: p.urgency, default=None)
        if strongest and strongest.urgency > self.distraction_threshold:
            self.focus = strongest.source  # Focus 강제 전환
            return AttentionEvent(type="DISTRACTED", by=strongest)

        return None
```

---

## Integration 맵 — 데이터 흐름 전체도

```python
def IntegrationMap():
    """3단 엔진 ↔ 심리 레이어 전체 데이터 흐름.

    ┌─────────────────────────────────────────────────────────────────┐
    │                        PsycheLayer (1Hz)                        │
    │                                                                 │
    │  Perception ──→ Blackboard ──→ Emotion ──→ Mood                │
    │       │              ↑            │                              │
    │       │         Attention          │                              │
    │       │         (7±2 제한)         │                              │
    │       ↓              │            ↓                              │
    │  Needs ─────────────────→ Personality ──→ Values                │
    │    │                         │    │         │                    │
    │    │    Learning ←──── EventToLearning     │                    │
    │    │       │                  ↑             │                    │
    └────│───────│──────────────────│─────────────│────────────────────┘
         │       │                  │             │
    ═════│═══════│══════════════════│═════════════│════════════════════
    연결점│       │                  │             │
         │       │                  │             │
    ┌────│───────│──────────────────│─────────────│────────────────────┐
    │    ↓       ↓                  │             ↓                    │
    │  GOAP ←─ NeedToGOAP          │    PersonalityToUtility          │
    │    │                          │    EmotionToUtility              │
    │    │   PlanBonus              │    PersonalityToSelector         │
    │    ↓       ↓                  │    HabitToSelector               │
    │  UtilityAI ──→ Selector      │             │                    │
    │    │         (Hysteresis)     │             │                    │
    │    ↓                          │             │                    │
    │  BehaviorTree ───────────────→│ EventToEmotion                  │
    │    │  (EmotionGate,           │ EpisodicToEmotion               │
    │    │   PersonalityGate,       │                                  │
    │    │   AttentionGate)         │                                  │
    │    ↓                          │                                  │
    │  Action Result ───────────────┘                                  │
    │                                                                  │
    │                   ExecutionEngine (60fps)                        │
    └──────────────────────────────────────────────────────────────────┘

    연결점 총 12개:
        1.  NeedToGOAP           — Needs → GOAP.GoalPool
        2.  EmotionToUtility     — Emotion → Scorer.EmotionMod
        3.  EmotionToReplan      — SpikeDetector → ReplanTrigger      [FIX-03]
        4.  PersonalityToUtility — Personality → Scorer.PersonalityMod
        5.  PersonalityToSelector— Personality → ModeSelector          [FIX-06]
        6.  PersonalityToBT      — Personality → Decorator gates
        7.  EmotionToBT          — Emotion → Decorator gates
        8.  PerceptionToBlackboard— Perception → Blackboard.*
        9.  EventToEmotion       — BT result → Emotion.react()
        10. EventToLearning      — BT result → Learning.OutcomeEval   [FIX-04]
        11. HabitToSelector      — ProceduralMemory → Habitual mode   [FIX-06]
        12. EpisodicToEmotion    — 기억 회상 → Emotion 증폭
    """
```

---

## NPC 인스턴스 예시 — 동일 엔진, 다른 인격

```python
def NPC_Instances():
    """3명의 NPC가 동일 상황("도적이 마을을 습격")에서 보이는 행동 차이."""

    # ── NPC 1: 마을 경비병 "Aldric" ──────────────
    aldric = NPC_Brain(
        personality=BigFive(O=0.3, C=0.8, E=0.5, A=0.6, N=0.3),
        values=Values(loyalty=0.9, justice=0.8, freedom=0.3, knowledge=0.2, survival=0.5),
    )
    # 상황: 도적 3명 접근, 체력 70%, 동료 1명
    # Perception: enemy(3), ally(1), threat_level=HIGH
    # Emotion: Fear +0.2 (N=0.3이므로 낮음), Anger +0.3 (Justice 위반)
    # Need: Safety 60 → Goal "마을 방어"
    # GOAP Plan: [equip_weapon → alert_allies → engage_enemy]
    # Utility: Fight(0.72) > Patrol(0.45) > Flee(0.18)
    # DecisionMode: Deliberate (emotion < 0.5, time_pressure=medium)
    # BT: Sequence(MoveTo(armory) → Speak("적이다!") → MoveTo(gate) → Fight)
    # Result: 무기 장착 후 동료에게 경보, 정문에서 방어

    # ── NPC 2: 떠돌이 상인 "Mira" ──────────────
    mira = NPC_Brain(
        personality=BigFive(O=0.7, C=0.4, E=0.8, A=0.7, N=0.7),
        values=Values(loyalty=0.3, justice=0.4, freedom=0.8, knowledge=0.5, survival=0.9),
    )
    # 상황: 동일
    # Perception: enemy(3), 자기 물건 위험
    # Emotion: Fear +0.5 (N=0.7 증폭), Anger +0.1
    # Need: Safety 85 (급상승), Survival 가치 高
    # GOAP Plan: [grab_valuables → find_exit → flee_town]
    # Utility: Flee(0.81) > Hide(0.52) > Fight(0.12)
    # DecisionMode: Impulsive (Fear 0.5 + N=0.7 → intensity > T_imp 0.65)
    # BT: Sequence(MoveTo(stall) → UseItem(grab_bag) → MoveTo(back_gate) → Flee)
    # Result: 물건 챙겨서 뒷문으로 도주

    # ── NPC 3: 은퇴한 전사 "Gorm" ──────────────
    gorm = NPC_Brain(
        personality=BigFive(O=0.2, C=0.6, E=0.3, A=0.4, N=0.2),
        values=Values(loyalty=0.7, justice=0.6, freedom=0.5, knowledge=0.1, survival=0.6),
    )
    # 상황: 동일
    # Perception: enemy(3), "옛날엔 10명도 상대했는데"
    # Emotion: Anger +0.3, Nostalgia +0.2 (과거 전투 기억 활성화)
    # Memory: EpisodicRetrieval → 유사 전투 경험 3건 (높은 similarity)
    #         → 감정 증폭: Anger +0.1, 자신감(Joy+0.1)
    # Need: Safety 40 (N=0.2이므로 크게 안 느낌)
    # GOAP Plan: [find_weapon → engage_enemy] (단순 — 경험 많아서 플랜 짧음)
    # Utility: Fight(0.65) > Observe(0.40) > Flee(0.08)
    # DecisionMode: Habitual (familiarity 0.9 — 전투 경험 다수)
    # BT: Sequence(MoveTo(smithy) → UseItem(grab_axe) → MoveTo(enemy) → Fight)
    # ProceduralMemory: "전투 상황 → 무기 확보 → 정면 돌파" (습관 강도 0.85)
    # Result: 대장간에서 도끼 집어 들고 도적에게 직행
```

---

## 성능 예산

```python
def PerformanceBudget():
    """NPC 1000체 @ 60fps 실행 가능성 분석.

    프레임 예산: 16.67ms (60fps)
    NPC 예산: 16.67ms / 1000 = 16.67μs per NPC per frame

    | 컴포넌트              | 빈도   | 비용/NPC  | 1000체 총비용 |
    |-----------------------|--------|-----------|--------------|
    | BT tick               | 60fps  | 2μs       | 2ms          |
    | Utility score (5후보) | 조건부 | 5μs       | 5ms (최악)   |
    | Hysteresis check      | 60fps  | 0.5μs     | 0.5ms        |
    | 고빈도 합계           |        |           | ~7.5ms       |
    |                       |        |           |              |
    | Perception scan       | 1Hz    | 50μs      | 50ms (별도)  |
    | Emotion dynamics      | 1Hz    | 5μs       | 5ms          |
    | Need calc             | 1Hz    | 2μs       | 2ms          |
    | Attention update      | 1Hz    | 10μs      | 10ms         |
    | GOAP replan           | 조건부 | 200μs     | 200ms (최악) |
    | 저빈도 합계           |        |           | ~267ms       |

    결론:
        - 고빈도: 7.5ms < 16.67ms → 60fps 가능
        - 저빈도: 267ms per second → 1Hz에서 충분
        - GOAP replan은 조건부(전체의 ~10%만 동시 replan)
          → 실제: 200ms × 0.1 = 20ms
        - 메모리: ~50KB/NPC → 1000체 = 50MB → 수용 가능

    최적화 전략:
        - 저빈도 틱을 NPC별로 시간 분산 (stagger)
        - GOAP PlanCache 히트율 70%+ 목표
        - Perception LOD: 카메라 거리별 scan 빈도 조절
        - 비활성 NPC: 저빈도 틱 0.1Hz로 감속
    """
```

---

## 문서 메타데이터

```python
metadata = {
    "title": "NPC_Brain v2.1 — Final Design",
    "version": "2.1",
    "date": "2026-03-24",
    "author": "ClNeo",
    "format": "PG (Gantree + PPR)",
    "total_gantree_nodes": "~250",
    "max_depth": 5,
    "integration_points": 12,
    "fixes_from_review": 8,
    "target": "Rust/C++ 구현, 1000체 @ 60fps",
    "psyche_layer": "ON/OFF 토글 — OFF 시 기존 게임 AI로 동작",
}
```
