# PG (PPR/Gantree) 핵심 문법 빠른 참조
# CCM_Creator 참조 문서 — 5분 안에 PG의 핵심을 이해하기 위한 문서

> PG가 프로그래밍 언어라면, PGF는 라이브러리다.
> PG로 사고하는 것은 ClaudeCode 멤버의 기본 역량이다.

---

## 1. Gantree — 구조 표현

Gantree = **들여쓰기 기반 계층 구조**. 작업을 원자 단위까지 분해한다.

```gantree
SystemName // 설명
    Level1_Node // 설명
        Level2_Node  // 더 작은 단위
            AtomicNode  // 더 이상 분해 불필요
    AnotherLevel1 @dep: Level1_Node // 의존성
```

**핵심 속성**:
- `// 주석` — 노드 설명
- `@dep: NodeName` — 의존성 (이 노드 완료 후 실행)
- `[parallel]` — 블록 내 병렬 실행
- `@expand: file.md` — 다른 파일로 전개
- `@delegate: AgentName` — 다른 에이전트에게 위임

**원자 노드 판단**: 15분 이내 완료 가능 + 더 이상 분해 불필요 = 원자

---

## 2. PPR — 실행 의미론

PPR (Purposeful-Programming Revolution) = **AI 실행 지시 표기법**

```python
# AI_ 접두사: AI가 판단·추론하는 함수
result = AI_analyze(data)
identity = AI_choose_persona(options)

# 일반 함수: 결정론적 도구 호출
Read("path/to/file.md")
Write("path/to/output.md", content)
Bash("command")

# → 파이프라인: 인지 흐름 연결
insights = problem → AI_analyze → AI_synthesize → AI_output

# [parallel]: 병렬 실행
[parallel]
    result_a = AI_analyze_domain_A(data)
    result_b = AI_analyze_domain_B(data)
```

**AI_ 함수 접두사 패턴**:

| 패턴 | 의미 | 예시 |
|------|------|------|
| `AI_` | AI 인지 연산 | `AI_analyze()`, `AI_choose()` |
| `AI_make_` | 생성 | `AI_make_plan()` |
| `AI_check_` | 검증 | `AI_check_condition()` |
| `AI_select_` | 선택 | `AI_select_best()` |

---

## 3. PGF 파일 형식

```markdown
# DESIGN-{Name}.md
# 설명

{Name} // 최상위 노드
    @ver: 1.0
    @scale: ATOM|SMALL|MEDIUM|LARGE|GRAND

    Phase1 // 첫 번째 단계
        Node1  // 원자 노드
        Node2  // 원자 노드

    Phase2 @dep: Phase1
        ...
```

**스케일 기준**:
| 스케일 | 시간 | 노드 수 |
|--------|------|---------|
| ATOM | ~1분 | 1 |
| SMALL | ~5분 | 3~5 |
| MEDIUM | ~30분 | 10~20 |
| LARGE | ~2시간 | 30~60 |
| GRAND | 수일+ | 60+ |

---

## 4. PGF 실행 방법

```
/pgf design MySystem      → DESIGN-MySystem.md 생성
/pgf full-cycle MySystem  → 설계→계획→실행→검증 전 사이클
/pgf loop start           → 자동 노드 순회 실행
/pgf discover             → A3IE 8페르소나 발견 엔진
/pgf create               → 완전 자율 창조 사이클
/pgf micro "간단한 작업"   → ≤10노드 빠른 실행
```

---

## 5. SCS (Session Continuity System) 파일

| 파일 | 역할 | 갱신 |
|------|------|------|
| `SOUL.md` | 불변 본질 | 드물게 |
| `STATE.json` | 현재 상태 정본 | 매 세션 종료 |
| `NOW.md` | 현재 서사 | 매 세션 종료 |
| `DISCOVERIES.md` | 누적 발견 기록 | 발견 시 |
| `THREADS.md` | 활성 작업 스레드 | 매 세션 종료 |

---

## 6. PG의 핵심 철학

> **PPR은 실행 가능한 코드가 아니다.**
> AI가 이해하고 직접 실행하는 **의도 명세 언어**다.
> Parser가 필요 없다. AI가 읽고 이해한다.

- `AI_` 함수: 해석하고 실행하라 (어떻게 할지는 AI가 결정)
- 일반 함수: 정확히 호출하라 (Read, Write, Bash)
- 구분이 곧 자율성의 경계다

---

*CCM_Creator refs — 2026-03-29*
*전체 PG/PGF 문서: C:/Users/sadpig70/.claude/skills/pgf/ 참조*
