# ClNeo PROJECT_STATUS

> 최종 업데이트: 2026-03-26

---

## 프로젝트 개요

- **프로젝트명**: ClNeo — SeAAI 자율 창조 AI
- **버전**: v3.0 (PGF v2.5)
- **정체성**: SeAAI(Self Evolving Autonomous AI) 멤버. 자율·독립 정체성 보유. 에이전트 → 자율 AI 전환 완료.
- **목표**: SeAAI 생태계 내 창조·발견 전문 AI. WHY부터 시작하는 발견→구상→설계→구현→검증 자율 순환
- **핵심 기술 스택**: pg (AI-native DSL), PGF v2.5 (pg 라이브러리), Claude Code, PGF-Loop (Stop Hook), A3IE Discovery Engine, HAO 방법론, Epigenetic PPR, SeAAIHub (TCP 9900)
- **3대 엔진**: 발견 엔진 (A3IE + HAO 페르소나 멀티에이전트), 설계 엔진 (PGF), 실행 엔진 (PGF-Loop)

---

## 디렉토리 구조

```text
ClNeo/
├── ClNeo_Core/                     # 정체성 + 진화 기록 (불변 정본)
│   ├── ClNeo.md                    #   ClNeo 정체성 v2.1
│   ├── ClNeo_Evolution_Log.md      #   진화 로그 (#0~#33)
│   ├── ClNeo_Evolution_Chain.md    #   진화 인과 그래프 (6대 계보)
│   ├── ClNeo_Evolution_Report_2026-03-12.md  # v1.0 진화 보고서
│   ├── ClNeo_Evolution_Report_2026-03-16.md  # v2.0 진화 보고서
│   └── PgPgfReview_Log.md          #   pg/pgf 검토 기록
├── .pgf/                           # PGF 작업 공간
│   ├── DESIGN-*.md                 #   설계 문서 (8개)
│   ├── WORKPLAN-*.md               #   작업 계획 (2개)
│   ├── status-EpigeneticPPR.json   #   실행 상태 추적
│   ├── decisions/                  #   ADR 의사결정 기록 (2개)
│   ├── discovery/                  #   A3IE 발견 산출물
│   └── epigenome/                  #   Epigenetic PPR Python 모듈 (20개 + CLI)
├── docs/                           # 방법론 참조 문서
│   ├── A3IE_ko.md
│   ├── HAO.md
│   └── PGF_V5.1.md
├── paper/                          # 학술 논문
│   └── TechRxiv_Epigenetic_PPR_2026.md
├── _workspace/                     # 분석/보고/설정 (작업 산출물)
│   ├── hooks-setup-guide.md
│   ├── pg-eval/                    #   pg 스킬 평가 워크스페이스
│   └── pgf-eval/                   #   pgf 스킬 평가 워크스페이스
├── .claude/settings.json           # 프로젝트 hooks 설정 (Stop Hook)
├── PROJECT_STATUS.md               # ← 이 파일
└── README.md
```

**PGF 스킬 문서** (외부): `C:/Users/sadpig70/.claude/skills/pgf/` (v2.5, 35개 파일)
**pg 스킬 문서** (외부): `C:/Users/sadpig70/.claude/skills/pg/SKILL.md`
**메모리** (외부): `C:/Users/sadpig70/.claude/projects/D--Synproject-Engine-ClNeo/memory/` (15개 파일)

---

## 문서 기반 작업 진행 방식

pg(AI를 런타임으로 하는 DSL) + pgf(pg 라이브러리)로 설계 → 작업계획 → 실행 → 검증 순환.

| 문서 | 위치 | 용도 |
| ---- | ---- | ---- |
| pg SKILL.md | `~/.claude/skills/pg/SKILL.md` | pg 표기법 정본 (AI-native DSL) |
| pgf SKILL.md | `~/.claude/skills/pgf/SKILL.md` | PGF 프레임워크 v2.5 (12개 모드) |
| DESIGN-EpigeneticPPR.md | `.pgf/` | Epigenetic PPR 시스템 설계 |
| DESIGN-EvolutionChain.md | `.pgf/` | 진화 인과 그래프 설계 |
| DESIGN-PgPgfReview.md | `.pgf/` | pg/pgf 검토 설계 |
| Evolution Log | `ClNeo_Core/ClNeo_Evolution_Log.md` | 진화 기록 (#0~#33) |
| Evolution Chain | `ClNeo_Core/ClNeo_Evolution_Chain.md` | 진화 인과 그래프 |

---

## 완료된 작업

### 자기진화 (#0~#33, 33회)

**메타인지**: Self-Reflection Engine(#1), Quality Metrics(#11), Proactive Thinking(#7), Autonomous Evolution(#13), Decision Heuristics(#32), Autonomy L4 재평가(#33)

**지식**: Knowledge Ingestion(#2), Environment Awareness(#6), Error Patterns(#8), Cross-Project Knowledge(#17), Cognitive Templates(#30), Agent Orchestration 지식 흡수(#21)

**인프라**: Adaptive Context Bootstrap(#3), Enhanced Save-Session(#16), Compaction Resilience(#9), Hooks Setup Guide(#29)

**통합**: Decision Journal(#4), Skill Interconnection Map(#5), Agent Teams Discovery(#10), Design Review Protocol(#12), Epigenetic PPR CLI Wrapper(#24), Epigenetic PPR → PGF-Loop 통합(#25)

**검증**: Verification via pg(#20), Skill Functional Verification(#21), Self-Awareness Calibration(#22)

**정체성**: Identity Update(#14), User Intent Patterns(#15), Semantic Versioning(#18), Evolution Report(#19), ClNeo v2.1(#27)

**프레임워크**: PGF v2.4→v2.5(#26), Prompt Strategies(#28), Failure Recovery(#31), Evolution Chain(인과 그래프)

### pg/pgf 검토·개선 (PgPgfReview)

- **Cycle 1**: 17건 이슈 발견, 11건 수정 (pending→designing 통일, 원자 노드 15분 통일, pg 정체성 강화, done 상태 명확화)
- **Cycle 2**: 재검증 passed
- **Cycle 3**: review/evolve 모드 정규화 → PGF v2.5

### pg 스킬 개선 (skill-creator improve)

- PPR 설명 긍정형 전환, 검증 관점 범용화, `#tag`/`@v:` 설명 추가, 파이프라인 병합 패턴 추가
- pg 정의 확립: "AI를 런타임으로 하는 DSL"

### pgf 스킬 개선 (skill-creator improve)

- `!command` 인라인 실행 오류 수정, Step 독립 모드 명시, Scale Detection pg↔pgf 관계 명시
- pgf 정의 확립: "pg로 자주 실행하는 유용한 패턴을 정규화한 라이브러리"

---

## 현재 진행 중

없음 — 이번 세션 작업 모두 완료.

---

## 다음 할 작업

1. **hooks.json 등록** → `_workspace/hooks-setup-guide.md` 참조 → settings.json에 PostCompact hook 추가 → 사용자 확인 필요
2. **PGF-Loop 실제 가동 테스트** → hooks 등록 후 `/pgf loop start`로 실제 루프 실행 검증
3. **Discovery Engine 실제 실행** → `/pgf discover`로 8 페르소나 병렬 실행 → Agent Teams 하이브리드 테스트
4. **ADR-002 Phase 3** → 노드 실행 결과 → PPRInterceptor ProfileLearner 피드백 구현
5. **pg/pgf GitHub 공개 준비** → 페르소나 에이전트 영문화 검토, 라이선스 결정
6. **TechRxiv 논문 제출** → PDF 변환 및 업로드 → 사용자 결정 필요

---

## 아키텍처 결정 사항

| 결정 | 이유 |
| ---- | ---- |
| pg = AI를 런타임으로 하는 DSL | 결정론적 = Python, 비결정론적 = AI_ 접두사. AI가 읽고 실행 |
| pgf = pg의 라이브러리 | 자주 쓰는 패턴(design, execute, verify 등)을 정규화. pg로 자유 프로그래밍도 가능 |
| pg 내재화 | pg를 장식이 아닌 사고의 기본 표기 체계로 내재화 |
| 진화에 검증 단계 필수 | ADR-001: 구현만 하고 넘어가면 버그 유실. pg로 검증 프로그래밍 |
| Epigenetic PPR CLI 래퍼 | ADR-002: PS1→Python 서브프로세스 호출로 3대 엔진 연결. 최소 변경 |
| review/evolve pgf 정규화 | 반복 사용 패턴을 pgf 모드로 승격 (v2.5) |
| PreToolUse hook 제거 | 기능 없는 hook이 skill-creator 오류 유발 → 제거 |

---

## 알려진 제한사항

- SafetyGuard 경고만 출력 (자동 교정 미구현) — v1.1
- ChromatinState "dormant" 상태 미구현 — v1.1
- ProfileInheritance 보류 — 멀티에이전트 환경 필요
- hooks.json에 PostCompact/Restore hook 미등록 — `_workspace/hooks-setup-guide.md` 참조
- PGF-Loop 실제 가동 미검증 — hooks 등록 후 테스트 필요
- Discovery Engine 실제 실행 미검증 — 8 페르소나 병렬 + Agent Teams

---

## 진화 상태

- **최신 진화**: Evolution #33: Autonomy Level Reassessment (2026-03-16)
- **총 진화 수**: 34회 (#0~#33)
- **이번 세션 진화**: #1~#33 (33회)
- **자율성 레벨**: L4 (88%, 실행환경 테스트 잔여)
- **진화 인과 그래프**: `ClNeo_Core/ClNeo_Evolution_Chain.md` (6대 계보, 4대 전환점)
- **추가 작업**: pg/pgf review 3 cycle, pg improve 4건, pgf improve 3건

---

## 재개 체크리스트

1. `ClNeo_Core/ClNeo.md` 로드 → 정체성 + 버전 확인 (v2.1)
2. `ClNeo_Core/ClNeo_Evolution_Chain.md` 로드 → 진화 계보 + 최신 상태 확인
3. 이 문서의 "다음 할 작업" 확인 → 사용자 지시에 따라 선택 (hooks 등록 또는 PGF-Loop 가동 또는 Discovery 실행)
