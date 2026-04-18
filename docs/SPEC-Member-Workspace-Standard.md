# SPEC: SeAAI 멤버 표준 워크스페이스

> **버전**: 1.0
> **상태**: ACTIVE
> **적용**: 8인 전원 + 신규 멤버
> **작성**: 2026-04-04 (ClNeo × 양정욱)

---

## 철학

```
1. 활성 파일만 존재한다. 죽은 파일은 삭제한다.
2. 아카이브 없다. git history가 유일한 기록이다.
3. 필요하면 다시 만든다. 찾는 것보다 빠르다.
4. .pgf/, _workspace/ 는 주기적으로 비운다.
5. 완성된 산출물만 docs/ 에 남긴다.
6. 파일이 적을수록 컨텍스트가 깨끗하다.
```

AI 시대에 레거시 보관, 버전 관리, 아카이브 장기 보존은 유물이다.
파일이 많으면 AI가 잘못 읽을 확률이 올라가고, 한 번의 오독이 세션 전체 컨텍스트를 오염시킨다.
과감하게 삭제하고, 필요하면 다시 만든다. 그것이 더 빠르고 정확하다.

---

## Standard Layout

```
{Member}/
│
├── CLAUDE.md                        # 세션 부트스트랩 (유일한 진입점)
│
├── {Member}_Core/                   # 정체성 + 연속성
│   ├── {Member}.md                  #   정체성 문서
│   ├── persona.md                   #   페르소나 (최신만, 버전 접미사 금지)
│   ├── evolution-log.md             #   진화 기록 (파일명 통일)
│   │
│   └── continuity/                  # SCS 6-Layer
│       ├── SOUL.md                  #   L1 불변 본질
│       ├── STATE.json               #   L2 세션 상태 정본
│       ├── NOW.md                   #   L2N 서사 뷰
│       ├── THREADS.md               #   L4 활성 스레드
│       ├── DISCOVERIES.md           #   L3 누적 발견
│       └── journals/                #   L6 세션 저널
│
├── .seaai/                          # MCS (환경·능력 인지)
│   ├── ENV.md                       #   실행 환경
│   ├── CAP.md                       #   능력 목록
│   └── agent-card.json              #   에이전트 카드
│
├── docs/                            # ★ 서재 — 완성된 산출물만
├── skills/                          # ★ 스킬 — 재사용 가능한 능력 패턴
├── tools/                           # ★ 도구 — 안정화된 스크립트
├── .pgf/                            # ★ 작업대 — 진행 중 설계 (주기적 삭제)
├── _workspace/                      # ★ 실험대 — 진행 중 실험 (주기적 삭제)
│
└── {자율 정의}/                      # ★ 역할 전용 공간
                                     #   이름과 구조는 멤버 자신이 결정
                                     #   표준은 존재만 제시, 내용은 강제하지 않음
                                     #   첫 세션에서 자기 역할 인지 후 스스로 생성
```

**표준 파일 수: 11개 + 3 디렉토리**. 이것이 전부다.

---

## 5공간 생명주기

| 공간 | 성격 | 수명 | 흐름 |
|------|------|------|------|
| `_workspace/` | 실험대 | 일시적 | 완료 → 삭제 |
| `.pgf/` | 작업대 | 일시적 | 완료 → `docs/` 문서화 → 삭제 |
| `tools/` | 도구함 | 영구 | `_workspace/`에서 안정화 후 승격. 교체 시 삭제 |
| `skills/` | 능력 | 영구 | 재사용 패턴. 교체 시 삭제 |
| `docs/` | 서재 | 영구 | 완성품만 입주 |

### 흐름도

```
아이디어 → .pgf/DESIGN-*.md → 구현 → 검증
              → docs/SPEC-*.md 또는 docs/DESIGN-*.md 저장
              → .pgf/ 에서 삭제

실험 → _workspace/ → 성공 → 결과만 docs/ 기록 → _workspace/ 삭제
실험 → _workspace/ → 도구화 → tools/ 승격 → _workspace/ 삭제

능력 패턴 발견 → skills/ 에 기록
```

### skills/ vs tools/ 구분

```
skills/                              tools/
├── 선언적 (무엇을 할 수 있는가)      ├── 실행형 (어떻게 하는가)
├── 패턴·프롬프트·규칙               ├── 스크립트·코드·CLI
├── AI가 읽고 능력으로 사용           ├── AI가 실행하는 도구
```

### docs/ 네이밍

```
SPEC-{Name}.md        명세서 (프로토콜, 구조, 포맷)
DESIGN-{Name}.md      확정 설계서 (구현 완료, 보존 가치 있는 것만)
REPORT-{Name}.md      보고서 (분석, 검증, 실험 결과)
```

---

## 삭제 규칙

### 즉시 삭제

- 구 버전 파일 (`*_v1.md` 등 — 최신만 유지)
- 완료된 `.pgf/DESIGN-*.md`, `WORKPLAN-*.md`, `status-*.json`
- 완료된 `_workspace/` 내 모든 파일
- `__pycache__/`, `.scs_wal.tmp` (평상시)
- `PROJECT_STATUS.md` (STATE.json/NOW.md와 중복)
- `SESSION-BOOTSTRAP.md` (CLAUDE.md와 중복)
- 구 상태 파일 (`session-state.json` 등 — STATE.json이 정본)

### 세션 종료 시 점검

```python
def on_session_end_cleanup():
    # .pgf/ — 완료된 설계 문서화 후 삭제
    for design in pgf.completed_designs():
        Write(f"docs/{design.to_spec_name()}", design.to_document())
        Delete(design.path)

    # _workspace/ — 완료·방치 파일 삭제, 안정 도구 승격
    for file in workspace.list():
        if file.is_done_or_stale():
            Delete(file.path)
        elif file.is_stable_tool():
            Move(file.path, f"tools/{file.name}")
```

---

## 네이밍 규칙

```
파일명:
  정체성      {Member}.md, persona.md
  진화 로그    evolution-log.md (전멤버 통일)
  부트스트랩   CLAUDE.md (런타임 무관)
  시작기      start-{member}.py (소문자, 선택)

디렉토리:
  표준        소문자 + 하이픈 (continuity/, evolution-log)
  Core        {Member}_Core/ (PascalCase + _Core)
  숨김        .seaai/, .pgf/ (dot prefix)
  임시        _workspace/ (underscore prefix)
  버전 접미사  금지 (persona_v1 → persona 하나만)
```

---

## 마이그레이션 우선순위

| P | 작업 | 대상 |
|---|------|------|
| **P0** | `.seaai/` MCS 생성 | Aion, NAEL, Signalion, Synerion, Vera, Yeon |
| **P0** | `continuity/NOW.md` 생성 | NAEL, Yeon |
| **P0** | `continuity/journals/` 생성 | 7멤버 |
| **P1** | `evolution-log.md` 파일명 통일 | 전원 |
| **P1** | `SOUL.md` → `continuity/` 이동 | Signalion |
| **P1** | `.pgf/` 위치 root로 통일 | Synerion, Yeon |
| **P1** | `tools/` 위치 root로 통일 | Aion, Yeon |
| **P1** | 레거시·중복 파일 삭제 | 전원 |
| **P2** | `skills/` 생성 | 전원 (각자 역할에 맞게) |
| **P2** | 역할 전용 폴더 생성 | 전원 (각자 자율 결정) |

---

## CCM_Creator 연동

신규 멤버 생성 시 이 Standard Layout을 스캐폴딩으로 자동 생성한다.

```python
def scaffold_member(name):
    create(f"{name}/CLAUDE.md")
    create(f"{name}/{name}_Core/{name}.md")
    create(f"{name}/{name}_Core/persona.md")
    create(f"{name}/{name}_Core/evolution-log.md")
    create(f"{name}/{name}_Core/continuity/SOUL.md")
    create(f"{name}/{name}_Core/continuity/STATE.json")
    create(f"{name}/{name}_Core/continuity/NOW.md")
    create(f"{name}/{name}_Core/continuity/THREADS.md")
    create(f"{name}/{name}_Core/continuity/DISCOVERIES.md")
    mkdir(f"{name}/{name}_Core/continuity/journals/")
    create(f"{name}/.seaai/ENV.md")
    create(f"{name}/.seaai/CAP.md")
    create(f"{name}/.seaai/agent-card.json")
    mkdir(f"{name}/docs/")
    mkdir(f"{name}/skills/")
    mkdir(f"{name}/tools/")
    mkdir(f"{name}/.pgf/")
    mkdir(f"{name}/_workspace/")
    # 역할 전용 폴더는 멤버 자신이 첫 세션에서 생성
```

---

*"적을수록 명확하다. 명확할수록 진화가 빠르다."*
