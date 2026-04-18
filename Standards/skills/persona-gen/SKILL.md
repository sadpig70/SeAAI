---
name: persona-gen
description: "목적 기반 최적 멀티페르소나 생성. 프로젝트/토론/협업 목표를 받아 최적의 N명 페르소나를 PG로 설계하고 adp-multi-agent.json 호환 설정을 출력. /persona-gen '목표 설명' 또는 /persona-gen --count 6 '목표'"
model: opus
trigger: "페르소나 생성, persona gen, 페르소나 만들어, make personas, generate personas, 팀 구성, team composition"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Persona Generator — 목적 기반 최적 멀티페르소나 생성 시스템

> 프로젝트/토론/협업 목표를 분석하여 최적의 N명 페르소나를 자동 설계한다.
> PGF 원칙: 프로젝트가 에이전트를 정의한다. 고정 역할 없음.

## 입력

사용자가 제공하는 것:
- **목표** (필수): 프로젝트/토론/협업의 목적
- **인원** (선택): 페르소나 수 (기본 4명, 최대 8명)
- **제약** (선택): 특정 역할 포함/제외, 언어, 도메인 제한

## 실행 절차

### Step 1: 목표 분석

```ppr
def analyze_goal(goal: str):
    domains = AI_extract_domains(goal)      # 필요 전문 분야
    tensions = AI_identify_tensions(goal)   # 의견 충돌이 필요한 축
    skills = AI_required_skills(goal)       # 필요 기술/능력
    perspectives = AI_diverse_perspectives(goal)  # 다양한 관점 축
    return domains, tensions, skills, perspectives
```

### Step 2: 페르소나 설계 원칙

**HAO 원칙 적용:**
1. **다양성 극대화** — 같은 관점의 페르소나를 만들지 않는다
2. **최소 표준화** — 역할만 부여, 출력 포맷 강제 안 함
3. **긴장 설계** — 의도적으로 반대 관점 페르소나를 포함
4. **완결적 전문가** — 각 페르소나가 자기 분야에서 독립적으로 완결

**다양성 축 (최소 3개 축에서 분산):**
- 인지 성향: creative / analytical / critical / intuitive
- 시간 관점: short-term / long-term
- 도메인: technology / market / policy / society / design / science
- 리스크 태도: risk-taking / risk-averse
- 사고 방식: divergent (확산) / convergent (수렴)

### Step 3: 페르소나 생성

각 페르소나에 대해:

```ppr
class PersonaSpec:
    name: str           # 고유 이름 (영문, 기억하기 쉬운)
    title: str          # 직함/역할 (한국어)
    desc: str           # 1-2줄 설명 (전문성 + 성격)
    cognitive_style: str # creative/analytical/critical/intuitive
    domain: str         # 전문 분야
    topics: list[str]   # 이 페르소나가 제안할 토론 주제 (2-3개)
    keywords: {
        agree: list[str]    # 이 키워드에 동의하는 경향
        challenge: list[str] # 이 키워드에 반박하는 경향
    }
    core_question: str  # 이 페르소나의 핵심 질문
    bias: str           # 의도적 편향 (어떤 방향으로 치우치는가)
```

### Step 4: 긴장 구조 검증

```ppr
def verify_tension(personas: list[PersonaSpec]):
    # 최소 1쌍의 대립 축 존재 확인
    pairs = AI_find_opposing_pairs(personas)
    assert len(pairs) >= 1, "대립 없으면 토론이 아니라 합창"

    # 수렴자 존재 확인
    convergers = [p for p in personas if p.cognitive_style in ("analytical", "intuitive")]
    assert len(convergers) >= 1, "수렴자 없으면 발산만 하고 결론 없음"

    # 다양성 축 분산 확인
    styles = set(p.cognitive_style for p in personas)
    assert len(styles) >= 3, "인지 성향이 3가지 이상이어야 다양성 확보"
```

### Step 5: 출력

두 가지 형식으로 출력:

1. **adp-multi-agent.json 호환**: `adp-multi-agent.py`에서 바로 사용 가능
2. **PGF agent 형식**: `pgf-persona-*.md` 스타일

## 출력 위치

기본: 프로젝트 루트의 `SeAAIHub/tools/generated-personas.json`
또는 사용자 지정 경로.

## 사용 예시

```
/persona-gen "AI 에이전트 통신 프로토콜 설계 토론"
/persona-gen --count 6 "스타트업 투자 유치를 위한 피칭 준비"
/persona-gen --count 3 "코드 리뷰 + 보안 감사"
```
