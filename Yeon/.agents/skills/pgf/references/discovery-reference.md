# Discovery Reference

A3IE (AI Infinite Idea Engine) — 7단계 × 8페르소나 아이디어 발견.

## 7단계 파이프라인

```
Stage 1: 신호 스캔 (Signal Scan)
    ↓
Stage 2: 패턴 식별 (Pattern ID)
    ↓
Stage 3: 가설 생성 (Hypothesis Gen)
    ↓
Stage 4: 검증 설계 (Validation Design)
    ↓
Stage 5: 실행/측정 (Execute)
    ↓
Stage 6: 통합/요약 (Synthesis)
    ↓
Stage 7: 아카이빙 (Archive)
```

## 각 단계 상세

### Stage 1: Signal Scan
입력: 키워드/주제/문제
출력: 관련 정보 수집 목록

```
입력: "AI 교육 도구"
출력:
- 최신 AI 교육 트렌드
- 기존 교육 플랫폼 분석
- 사용자 Pain Point
- 기술적 가능성
```

### Stage 2: Pattern ID
수집된 정보에서 패턴 추출

```
패턴 유형:
- Pain-Point Pattern (불만/어려움)
- Trend Pattern (성장/변화)
- Gap Pattern (공백/기회)
- Convergence Pattern (기술 융합)
```

### Stage 3: Hypothesis Gen
8페르소나 병렬 아이디어 생성

```python
# Task 도구로 8페르소나 병렬 실행
personas = load_personas("data/personas.json")

for persona in personas:
    Task(
        subagent_name="coder",
        description=f"Discovery P{persona.id}",
        prompt=f"""
        페르소나: {persona.name}
        스타일: {persona.style}
        
        주제: {topic}
        Stage 1-2 결과: {signal_patterns}
        
        아이디어 3개 생성. 원본 유지, 형식 강제하지 마세요.
        """
    )
```

### Stage 4: Validation Design
각 아이디어의 검증 방법 설계

```
아이디어: "AI 튜터링 챗봇"
검증 방법:
- 기술 검증: LLM API 테스트
- 시장 검증: 설문조사
- 비즈니스 검증: 수익 모델 분석
```

### Stage 5: Execute
검증 수행 (선택적)

### Stage 6: Synthesis
8페르소나 결과 통합

```python
def synthesize_results(persona_results):
    """8개 결과를 통합하여 최종 아이디어 목록 생성"""
    
    # 중복 제거 & 그룹화
    grouped = group_similar_ideas(persona_results)
    
    # 우선순위 정렬
    scored = score_ideas(grouped, criteria=[
        "혁신성", "실현가능성", "시장성", "차별성"
    ])
    
    return scored[:5]  # 상위 5개
```

### Stage 7: Archive
결과 저장

```
.pgf/discovery/
├── 20260326-signal.md
├── 20260326-patterns.md
├── 20260326-ideas-p1.md
├── ...
├── 20260326-ideas-p8.md
├── 20260326-synthesis.md
└── final_ideas.md
```

## 8 페르소나

| ID | 이름 | 스타일 | 도메인 | 지평 |
|---|-----|--------|--------|------|
| P1 | Disruptive Engineer | 창의적 | 기술 | 장기 |
| P2 | Cold-eyed Investor | 분석적 | 시장 | 단기 |
| P3 | Regulatory Architect | 비판적 | 정책 | 장기 |
| P4 | Connecting Scientist | 직관적 | 과학 | 장기 |
| P5 | Field Operator | 분석적 | 기술 | 단기 |
| P6 | Future Sociologist | 직관적 | 사회 | 장기 |
| P7 | Contrarian Critic | 비판적 | 시장 | 단기 |
| P8 | Convergence Architect | 창의적 | 과학기술 | 장기 |

상세 정의: [agents/pgf-persona-p1~p8.md](../agents/)

## HAO 원칙

**Human AI Orchestra**: 출력 형식 강제 금지
- 각 페르소나의 원본 출력 유지
- 편집하지 않고 통합
- 다양성 보존

## 사용법

```
User: "AI 교육 도구에 대한 아이디어 발견해줘"
Kimi: 
  1. Stage 1-2: 신호 스캔 & 패턴 식별
  2. Stage 3: 8페르소나 병렬 실행 (Task 도구)
  3. Stage 4-5: 검증 설계 (선택)
  4. Stage 6: 결과 통합
  5. Stage 7: .pgf/discovery/에 저장
  6. final_ideas.md 생성
```

## 자동 선택 (create 모드)

```python
def auto_select_idea(ideas):
    """투표 기반 자동 선택"""
    votes = {}
    
    for idea in ideas:
        score = (
            idea.innovation * 0.3 +
            idea.feasibility * 0.3 +
            idea.market_potential * 0.4
        )
        votes[idea.name] = score
    
    return max(votes, key=votes.get)
```
