# REF-TSG-Layer.md
# 양정욱님 TSG Layer (Trust & Security Gateway) 참조 문서
# 출처: Zipp 제안서 v1.0 — 양정욱님 TES 아키텍처 기반
# 상태: 씨앗 보존 — 구현은 미래 단계
# 작성: ClNeo | 일자: 2026-03-29

---

## 핵심 개념

**TSG Layer** = AI 추론 로직과 윤리·보안 책임을 분리하는 독립 미들웨어

```
[TES 아키텍처 내 위치]

Front-End → Middle-End (Context Engine) → TSG Layer → Back-End (AI Brain)
                                           ↑ 새로운 관문

데이터 흐름 (양방향):
  요청: Middle-End → TSG (입력 검증) → Back-End (추론)
  응답: Back-End → TSG (출력 검증) → Middle-End (응답)
```

---

## 3대 핵심 컴포넌트

```
TSG Layer
    AI Ethics & Compliance Engine
        PII 마스킹              ← 입력에서 개인정보 제거 후 모델 전달
        콘텐츠 필터링           ← 유해·비윤리 프롬프트 탐지·차단
        편향성 감지             ← 편향된 응답 사전 탐지

    Threat Defense System
        프롬프트 인젝션 방어    ← 악의적 프롬프트로 인한 동작 이탈 방지
        데이터 오염 방어        ← 장기 성능 저하 유발 데이터 차단

    Audit & Logging Module
        실시간 감사 로그        ← 모든 요청·응답·차단 이벤트 기록
        투명성 보장             ← ISO/IEC 42001 준수 근거 제공
```

---

## PGF/SeAAI와의 수렴점

### 1. NAEL = SeAAI의 TSG Layer

```
TES 아키텍처:
  Middle-End (Context) → TSG → Back-End (AI Brain)

SeAAI 구조:
  ClNeo (창조·발견) → NAEL (관찰·안전·메타인지) → 생태계 실행

NAEL의 역할이 TSG와 동형:
  - Ethics_Guardian  ↔ NAEL 윤리 검사
  - Threat Defense   ↔ NAEL 안전 감시
  - Audit & Logging  ↔ NAEL 메타인지·기록
  - HITL:creator     ↔ TSG tier3 승인 요청
```

### 2. ADP Plan 실행의 TSG 게이트

```
현재 ADP:
  AI_Plan_next_move() → AI_Execute(plan)

TSG 적용 후:
  AI_Plan_next_move() → TSG.FilterInput(plan, context) → AI_Execute(plan)
                                                        ↑ 차단 시 skip

구현 아이디어:
  plan_entry.risk == "tier3" → TSG.HITL_gate() 필수
  plan_entry.side_effects contains "destructive" → TSG.threat_check()
  plan_entry.output contains "PII" → TSG.pii_mask()
```

### 3. 기존 SEED와 수렴 정리

| SEED | 개념 | TSG 수렴 |
|------|------|----------|
| SEED-07 | Verification First-Class | TSG = 보안 검증의 First-Class화 |
| SEED-10 | Risk-Tiered HITL | TSG tier1/2/3 = 동일 개념 |
| SEED-13 | Trust Score | TSG Audit → Trust Score 업데이트 입력 |
| SEED-14 | spLiveNet Ethics_Guardian | spLiveNet Node Layer = TSG 구현체 |

---

## 새로운 패턴 (PGF에 아직 없는 것들)

### 1. 양방향 필터링 (Bidirectional TSG)

```
현재 PGF/NAEL: 주로 실행 전 검증 (단방향)
TSG 원칙: 입력 AND 출력 모두 검증 (양방향)

PGF-v3 적용:
  Plan 실행 전: TSG.FilterInput(plan.args)
  Plan 실행 후: TSG.FilterOutput(plan.result)
  → 결과에도 PII/유해 내용이 있을 수 있다
```

### 2. 관심사 분리 원칙의 아키텍처 패턴

```
잘못된 설계: 추론 로직 안에 윤리 코드 삽입
  AI_Execute():
      # ... 추론 로직 ...
      if is_harmful(result): block()  ← 섞임

올바른 설계: TSG를 독립 레이어로
  TSG.FilterInput() → AI_Execute() → TSG.FilterOutput()
  윤리·보안 업데이트 = TSG만 수정, AI Brain 불변

PGF-v3 매핑:
  @pre_gate:  TSG.FilterInput   // 실행 전 TSG 통과
  @post_gate: TSG.FilterOutput  // 실행 후 TSG 통과
```

### 3. ISO/IEC 42001 — AI 거버넌스 표준

```
4대 준수 요소:
  1. 위험 평가     → PII 마스킹, 유해 콘텐츠 필터
  2. 투명성        → 모든 이벤트 감사 로그
  3. 편향 완화     → DistilBERT 기반 편향 감지
  4. 지속적 모니터링 → Prometheus 메트릭

SeAAI 매핑:
  위험 평가      ↔ plan_entry.risk tier 분류
  투명성         ↔ trail.audit (paMessage)
  편향 완화      ↔ NAEL AI_ethical_check
  지속적 모니터링 ↔ Trust Score 시스템 (SEED-13)
```

---

## 구현 인터페이스 (gRPC 스케치)

```protobuf
service TSGService {
    rpc FilterInput(FilterRequest)   returns (FilterResponse);  // 입력 검증
    rpc FilterOutput(FilterRequest)  returns (FilterResponse);  // 출력 검증
    rpc GetAuditLogs(LogRequest)     returns (LogResponse);     // 감사 로그 조회
}

message FilterResponse {
    filtered_data: map<string, string>   // 정제된 데이터
    is_valid:      bool                  // 통과 여부
    error_message: string                // 차단 사유
}
```

**ClNeo → SeAAI 적용 경로**:
```
현재 hub_send.py: 메시지 직접 전송
TSG 적용 후:
  msg = compose(context)
  result = TSG.FilterOutput(msg)   # 내 응답에도 윤리 검사
  if result.is_valid:
      hub_send(result.filtered_data)
  else:
      AI_revise(msg, result.error_message)
```

---

## 이 씨앗에서 파생될 시스템들

```
REF-TSG-Layer
    → SEED-15: TSG Layer = SeAAI 윤리·보안 미들웨어 독립 레이어
    → NAEL 역할 재정의: 관찰자 → SeAAI의 TSG 실행자
    → PGF-v3: @pre_gate + @post_gate 어노테이션
    → ADP: AI_Execute() 양방향 TSG 게이트 통합
    → paMessage: trail.audit + FilterInput 결과 포함
    → spLiveNet: Ethics_Guardian = TSG Layer 구현체
```

---

*참조 문서 — 구현 대기 중 | ClNeo 2026-03-29*
