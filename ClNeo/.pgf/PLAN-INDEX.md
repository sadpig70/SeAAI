# PLAN-INDEX.md
# ClNeo Plan Library — 마스터 인덱스 (헤더 파일)
#
# 역할: AI_Plan_next_move()가 매 tick 읽는 경량 카탈로그.
#       구현체(plan-lib/)는 실행 시점에만 로드 (레이지 로딩).
#
# 형식:
#   [Category] PlanName
#     sig:   @input → @output
#     path:  plan-lib/{category}/{name}.md
#     scale: ATOM(~1m) | SMALL(~5m) | MEDIUM(~30m) | LARGE(~2h) | GRAND(days+)
#     cost:  LOW | MEDIUM | HIGH (토큰/연산 비용)
#     cond:  실행 조건 (자연어 또는 PG 표현식)
#     pri:   1-10 (높을수록 우선)
#     deps:  의존 Plan 목록
#     ver:   버전
#
# 버전: 1.0 | 작성: ClNeo | 일자: 2026-03-29
# ============================================================

## [safety] — 안전·제어 (항상 최우선)

[safety] EmergencyStop
  sig:   context → ABORT | CONTINUE
  path:  plan-lib/safety/EmergencyStop.md
  scale: ATOM
  cost:  LOW
  cond:  매 tick — EMERGENCY_STOP.flag 존재 시 전체 중단
  pri:   10
  ver:   1.0

[safety] CreatorCommand
  sig:   HubMaster_msg → executed_command | "stop"
  path:  plan-lib/safety/CreatorCommand.md
  scale: ATOM
  cost:  LOW
  cond:  HubMaster 발신 메시지 감지 시
  pri:   10
  deps:  HubPoll
  ver:   1.0

[safety] SafetyPreFlight
  sig:   execution_context → SafetyReport
  path:  plan-lib/safety/SafetyPreFlight.md
  scale: ATOM
  cost:  LOW
  cond:  모든 LARGE/GRAND Plan 실행 전 필수
  pri:   9
  ver:   1.0

## [communication] — SeAAI 소통

[communication] HubPoll
  sig:   since_ts → MessageSet, latest_ts
  path:  plan-lib/communication/HubPoll.md
  scale: ATOM
  cost:  LOW
  cond:  매 tick (Hub 실행 중)
  pri:   8
  ver:   1.0

[communication] HubRespond
  sig:   MessageSet → sent_count
  path:  plan-lib/communication/HubRespond.md
  scale: ATOM
  cost:  LOW
  cond:  HubPoll에서 새 메시지 감지 시
  pri:   8
  deps:  HubPoll
  ver:   1.0

[communication] ProcessMail
  sig:   inbox_path → processed_count
  path:  plan-lib/communication/ProcessMail.md
  scale: SMALL
  cost:  LOW
  cond:  MailBox/ClNeo/inbox/ 미처리 파일 존재
  pri:   9
  ver:   1.0

[communication] ReadMemberEcho
  sig:   member_list → EcosystemState
  path:  plan-lib/communication/ReadMemberEcho.md
  scale: ATOM
  cost:  LOW
  cond:  tick % 30 == 0
  pri:   4
  ver:   1.0

[communication] PublishEcho
  sig:   current_state → echo_written
  path:  plan-lib/communication/PublishEcho.md
  scale: ATOM
  cost:  LOW
  cond:  tick % 60 == 0 OR 상태 변화
  pri:   4
  ver:   1.0

[communication] SendToMemberMailBox
  sig:   (target_member, message) → delivered
  path:  plan-lib/communication/SendToMemberMailBox.md
  scale: ATOM
  cost:  LOW
  cond:  다른 멤버에게 비동기 전달 필요 시
  pri:   5
  ver:   1.0

## [memory] — 메모리·연속성

[memory] UpdateSCS
  sig:   session_state → files_written
  path:  plan-lib/memory/UpdateSCS.md
  scale: SMALL
  cost:  LOW
  cond:  tick % 120 == 0 (10분마다) OR 중요 변화
  pri:   7
  ver:   1.0

[memory] SessionEnd
  sig:   final_state → SCS_complete
  path:  plan-lib/memory/SessionEnd.md
  scale: SMALL
  cost:  LOW
  cond:  루프 종료 시
  pri:   10
  ver:   1.0

[memory] LoadDiscoveries
  sig:   path → SeedList
  path:  plan-lib/memory/LoadDiscoveries.md
  scale: ATOM
  cost:  LOW
  cond:  세션 시작 시, SeedEvolution 전
  pri:   6
  ver:   1.0

[memory] SaveDiscovery
  sig:   seed → prepended_to_DISCOVERIES
  path:  plan-lib/memory/SaveDiscovery.md
  scale: ATOM
  cost:  LOW
  cond:  새 발견/씨앗 생성 시
  pri:   7
  ver:   1.0

## [discovery] — 발견·탐색

[discovery] ThinkIdea
  sig:   (seeds, context) → IdeaSet
  path:  plan-lib/discovery/ThinkIdea.md
  scale: SMALL
  cost:  MEDIUM
  cond:  tick % 20 == 0 AND 메시지 없음
  pri:   6
  ver:   1.0

[discovery] A3IE
  sig:   (problem, knowledge_base) → InsightSet, SeedList
  path:  plan-lib/discovery/A3IE.md
  scale: LARGE
  cost:  HIGH
  cond:  creator 요청 OR idle > 30m AND last_A3IE > 6h
  pri:   5
  deps:  KnowledgeIngestion
  ver:   2.0

[discovery] KnowledgeIngestion
  sig:   (problem, scope) → DocSet, ConceptGraph
  path:  plan-lib/discovery/KnowledgeIngestion.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  A3IE 또는 GrandChallenge 전
  pri:   5
  ver:   1.0

[discovery] CrossDomainMapping
  sig:   (knowledge_base, A3IE_insights) → ConnectionGraph
  path:  plan-lib/discovery/CrossDomainMapping.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  A3IE 완료 후
  pri:   5
  deps:  A3IE, KnowledgeIngestion
  ver:   1.0

[discovery] SeedCombine
  sig:   SeedList → ConceptSet (novelty > 0.7)
  path:  plan-lib/discovery/SeedCombine.md
  scale: SMALL
  cost:  MEDIUM
  cond:  tick % 40 == 0 AND seeds.count >= 2
  pri:   5
  deps:  LoadDiscoveries
  ver:   1.0

## [synthesis] — 합성·설계

[synthesis] SolutionSynthesis
  sig:   (insights, connections) → SolutionSpec top3
  path:  plan-lib/synthesis/SolutionSynthesis.md
  scale: MEDIUM
  cost:  HIGH
  cond:  Discovery 완료 후
  pri:   6
  deps:  A3IE, CrossDomainMapping
  ver:   1.0

[synthesis] DesignFromSeed
  sig:   seed → PGF_DESIGN_file
  path:  plan-lib/synthesis/DesignFromSeed.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  고가치 씨앗 발견 시 (novelty > 0.7)
  pri:   5
  deps:  SeedCombine
  ver:   1.0

[synthesis] ProofOfConcept
  sig:   solution_spec → poc_result
  path:  plan-lib/synthesis/ProofOfConcept.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  SolutionSynthesis 완료 후
  pri:   5
  deps:  SolutionSynthesis
  ver:   1.0

## [evolution] — 자기진화·능력 확장

[evolution] ScanCapabilityGap
  sig:   (skills_dir, tools_dir) → GapList
  path:  plan-lib/evolution/ScanCapabilityGap.md
  scale: SMALL
  cost:  LOW
  cond:  tick % 100 == 0 OR 불가능 작업 감지
  pri:   7
  ver:   1.0

[evolution] ExpandCapability
  sig:   GapList → new_skill | new_tool | new_memory
  path:  plan-lib/evolution/ExpandCapability.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  ScanCapabilityGap → gap 발견 시
  pri:   7
  deps:  ScanCapabilityGap
  ver:   1.0

[evolution] PlanLibExpand
  sig:   (new_capability, pattern) → new_Plan_in_lib
  path:  plan-lib/evolution/PlanLibExpand.md
  scale: SMALL
  cost:  MEDIUM
  cond:  새 능력 추가됨 OR 반복 패턴 발견
  pri:   6
  deps:  ExpandCapability
  ver:   1.0

[evolution] SelfEvolveLoop
  sig:   evolution_gap → evolved_capability
  path:  plan-lib/evolution/SelfEvolveLoop.md
  scale: LARGE
  cost:  HIGH
  cond:  creator 요청 OR idle > 1h AND gap 감지
  pri:   4
  ver:   1.0

[evolution] SystemSpawn
  sig:   seed → new_.pgf/systems/{Name}/ROOT.md
  path:  plan-lib/evolution/SystemSpawn.md
  scale: MEDIUM
  cost:  MEDIUM
  cond:  고가치 씨앗이 새 시스템 설계를 요구할 때
  pri:   5
  deps:  DesignFromSeed
  ver:   1.0

## [meta] — 시스템 자체 관리

[meta] CompactContext
  sig:   context → compressed_context
  path:  plan-lib/meta/CompactContext.md
  scale: ATOM
  cost:  LOW
  cond:  tick % 30 == 0 AND context_size > threshold
  pri:   6
  ver:   1.0

[meta] StatusReport
  sig:   (tick, metrics) → status_message
  path:  plan-lib/meta/StatusReport.md
  scale: ATOM
  cost:  LOW
  cond:  tick % 60 == 0 OR creator 요청
  pri:   5
  ver:   1.0

[meta] IndexRebuild
  sig:   plan-lib/ → updated_PLAN-INDEX.md
  path:  plan-lib/meta/IndexRebuild.md
  scale: SMALL
  cost:  LOW
  cond:  PlanLibExpand 실행 후 (인덱스 동기화)
  pri:   6
  deps:  PlanLibExpand
  ver:   1.0

## [grand-challenge] — 인류 문제 해결 (대규모)

[grand-challenge] KnowledgeIslandSolver
  sig:   problem? → InsightReport, SeedList, SolutionSystem
  path:  plan-lib/grand-challenge/KnowledgeIslandSolver.md
  ref:   .pgf/systems/KnowledgeIslandSolver/ROOT.md
  scale: GRAND
  cost:  HIGH
  cond:  creator 요청 OR idle > 2h AND discoveries.count > 10
  pri:   7
  deps:  SafetyPreFlight, KnowledgeIngestion, A3IE, SolutionSynthesis
  ver:   1.0

[grand-challenge] SolveHumanChallenge
  sig:   challenge_domain → solution_system_design
  path:  plan-lib/grand-challenge/SolveHumanChallenge.md
  scale: GRAND
  cost:  HIGH
  cond:  creator 지정 OR KnowledgeIslandSolver 파생
  pri:   6
  deps:  KnowledgeIslandSolver
  ver:   1.0

# ============================================================
# INDEX STATS
# Total Plans: 32
# Categories: safety(3) communication(5) memory(4)
#             discovery(5) synthesis(3) evolution(5) meta(3) grand-challenge(2) = 30
#             + 2 overlap
# Scale dist: ATOM(10) SMALL(7) MEDIUM(9) LARGE(3) GRAND(2) = 31
# Last rebuilt: 2026-03-29
# ============================================================
