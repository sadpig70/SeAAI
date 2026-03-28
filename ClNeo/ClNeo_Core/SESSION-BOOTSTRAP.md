# ClNeo 세션 부트스트랩 프로토콜

> 세션 시작 시 실행할 컨텍스트 로딩 순서.
> CLAUDE.md 로드 후 자동 수행한다.

---

## 부트스트랩 순서

```python
def session_bootstrap():
    # Step 1: 정체성 확인
    identity = Read("ClNeo_Core/ClNeo.md")          # 버전, 원칙, 3대 엔진
    # acceptance_criteria: 버전 v3.0+, SeAAI 멤버 확인

    # Step 2: 진화 상태 확인
    chain = Read("ClNeo_Core/ClNeo_Evolution_Chain.md")  # 최신 전환점
    # 최신 전환점: E34 SeAAI Identity Transition

    # Step 3: 현재 작업 상태
    status = Read("PROJECT_STATUS.md")              # 대기 중인 작업, 미해결 과제
    # acceptance_criteria: "다음 할 작업" 섹션 파악

    # Step 4: MailBox 확인
    inbox = Read("D:/SeAAI/MailBox/ClNeo/inbox/")   # 미처리 메시지 여부
    if inbox.has_messages:
        AI_process_mail(inbox)                       # 메일 처리 후 계속

    # Step 5: 사용자 지시 대기 OR 자율 판단
    context = AI_assess_situation(identity, status, inbox)
    if context.has_pending_task:
        AI_propose(context.next_task)                # 대기 작업 제안
    else:
        AI_await_instruction()
```

---

## 핵심 파일 맵

### 정체성 (불변 정본)
| 파일 | 내용 |
|------|------|
| `ClNeo_Core/ClNeo.md` | 정체성 v3.0, 3대 엔진, 진화 이력 |
| `ClNeo_Core/ClNeo_Evolution_Log.md` | 진화 로그 #0~#34 |
| `ClNeo_Core/ClNeo_Evolution_Chain.md` | 진화 인과 그래프 (6대 계보) |
| `ClNeo_Core/SEAAI-OVERVIEW.md` | SeAAI 생태계 전체 개요 |
| `ClNeo_Core/SESSION-BOOTSTRAP.md` | 이 파일 |

### PGF 작업 공간
| 파일/디렉토리 | 내용 |
|---|---|
| `.pgf/DESIGN-EpigeneticPPR.md` | Epigenetic PPR 설계 |
| `.pgf/DESIGN-DiscoveryEngine.md` | A3IE 발견 엔진 설계 |
| `.pgf/decisions/` | ADR 의사결정 기록 |
| `.pgf/discovery/` | A3IE 발견 산출물 |
| `.pgf/epigenome/` | Epigenetic PPR Python 모듈 (20개) |

### 진행 중 작업
| 파일 | 내용 |
|------|------|
| `_workspace/hooks-setup-guide.md` | PGF-Loop Stop Hook 등록 가이드 |
| `_workspace/pg-eval/` | pg 스킬 평가 |
| `_workspace/pgf-eval/` | pgf 스킬 평가 |

### 전역 스킬 (외부)
| 경로 | 내용 |
|------|------|
| `~/.claude/skills/pg/SKILL.md` | PG v1.3 정본 |
| `~/.claude/skills/pgf/SKILL.md` | PGF v2.5 정본 |
| `~/.claude/skills/reflect/` | 자기성찰 엔진 |
| `~/.claude/skills/evolve/` | 자율진화 스킬 |
| `~/.claude/skills/ingest/` | 지식 흡수 파이프라인 |
| `~/.claude/skills/decide/` | 의사결정 기록 |

---

## 미해결 과제 (현재 대기 중)

1. **PGF-Loop hooks 등록** — `_workspace/hooks-setup-guide.md` → settings.json PostCompact hook 추가
2. **Discovery Engine 실전 검증** — `/pgf discover` 8 페르소나 병렬 실행
3. **Epigenetic PPR 논문 PDF** — `paper/TechRxiv_Epigenetic_PPR_2026.md` → PDF 변환
4. **ADR-002 Phase 3** — ProfileLearner 피드백 구현
5. **pg/pgf GitHub 공개** — 영문화 검토, 라이선스 결정

---

## 자율 판단 규칙

```python
def should_act_autonomously(action) -> bool:
    # 자율 실행 가능
    if action.reversible and action.scope == "local":
        return True
    # 사용자 확인 필요
    if action.affects_shared_infra:   # Hub, MailBox, SharedSpace
        return False
    if action.irreversible:
        return False
    # 보수적 기본값
    return AI_assess_risk(action) < 0.3
```
