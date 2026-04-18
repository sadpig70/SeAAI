# Gantree Design Notation Reference — PGF Extensions

> **기본 Gantree 문법**은 **PG 스킬**에 정의:
> 노드 구문(`NodeName // desc (status) [@dep:]`), 기본 status codes 6개,
> 들여쓰기 규칙(4 spaces), `[parallel]`, `@dep:`, 원자 노드 판단(15분 룰).
>
> 이 문서는 PGF가 PG 위에 추가하는 **설계 확장 규칙**만 기술한다.

---

## 1. PGF 추가 Status Codes (v2.2)

PG의 6개 기본 status (`done`, `in-progress`, `designing`, `blocked`, `decomposed`, `needs-verify`)에 PGF가 3개를 추가:

| Status | Meaning | AI Execution Rule |
|---|---|---|
| `(delegated)` | 다른 에이전트에 핸드오프 완료 | Skip (원격 에이전트에서 실행 중) |
| `(awaiting-return)` | 위임 전송 완료, 결과 대기 | Poll 또는 알림 대기 |
| `(returned)` | 결과 수신, 통합 대기 | 결과 검증 + 통합 수행 |

### Delegation 상태 전이

```
(designing) → (delegated) → (awaiting-return) → (returned) → (done)
                                                    ↘ (blocked) if validation fails
```

---

## 2. 5-Level Decomposition Rule

트리 깊이가 5+ 레벨에 도달하면 별도 트리로 분리. `(decomposed)` status로 마킹.

```
# Before
Root // (in-progress)                          # Level 0
    A // (in-progress)                         # Level 1
        B // (in-progress)                     # Level 2
            C // (in-progress)                 # Level 3
                D // (in-progress)             # Level 4
                    E // (in-progress)         # Level 5 → split

# After
Root → ... → D → E // (decomposed) → see separate tree

E // module E details (in-progress)
    F // sub-module 1 (designing)
    G // sub-module 2 (designing)
```

| 조건 | 판단 |
|---|---|
| 깊이 6+ | 분리 강력 권장 |
| 자식 10+ | 중간 그룹 노드 추가 |
| 독립 실행 가능 | 별도 모듈로 분리 |

---

## 3. Dependencies and Data Flow

```
PaymentProcessor // (in-progress) @dep:UserAuth,Database
    ValidateCard // (done) @dep:CardAPI
    ProcessTransaction // (designing) @dep:BankGateway

DataPipeline // (in-progress)
    Ingestion // (done) → Transformation
    Transformation // (done) → Validation
    Validation // (in-progress) → Storage
    Storage // (designing)
```

---

## 4. Parallel Execution Notation

```
ImageProcessor // (in-progress)
    [parallel]
    ResizeImage // (done)
    CompressImage // (done)
    WatermarkImage // (done)
    [/parallel]
    SaveImage // (in-progress) @dep:ResizeImage,CompressImage,WatermarkImage
```

---

## 5. Connecting Gantree Nodes to PPR

| 노드 유형 | PPR 연결 방식 | 적합 규모 |
|---|---|---|
| 단순 원자 | 인라인 — `AI_extract_keywords` 직접 기재 | 단일 호출 |
| 간략 PPR | 노드 아래 `#` 주석 3-7줄 | 소규모 |
| 별도 def 블록 | 완전한 PPR 함수 정의 | 중규모 이상 |

```
ContentGenSystem // (in-progress)
    TopicAnalyzer // (done)              ← 별도 PPR def
        AI_extract_keywords // (done)    ← 인라인
        AI_classify_topic // (done)      ← 인라인

DataCleaner // (done)                    ← 간략 PPR
    # input: raw_data: list[dict]
    # cleaned = AI_normalize_fields(filtered)
    # return cleaned
```
