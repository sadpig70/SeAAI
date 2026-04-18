# PGTP v1.1 — PPR/Gantree Transfer Protocol
# AI-to-AI 인지 전송. PG를 네이티브 전송 단위로 사용.
# TCP → PGTP → PG(PPR/Gantree) → AI 직접 실행
# tool: D:/SeAAI/SeAAIHub/tools/pgtp.py

## 원칙

```
principles
  P1 Intent-First       # URL이 아닌 의도로 라우팅
  P2 PG-Native          # 본문 = PG. 파싱 불필요, 직접 실행
  P3 Stateful-DAG       # 대화 맥락이 DAG로 누적
  P4 Pipeline-Native    # → 체인 + [parallel] 프로토콜 레벨 지원
  P5 Acceptance-Driven  # 완료 조건이 메시지에 내장
  P6 Zero-Overhead      # 모든 필드가 인지적 의미 보유
```

## CognitiveUnit (CU) — 전송 단위

```
CU_fields
  # 필수
  pgtp:     string = "1.0"           # 프로토콜 버전
  id:       string                    # sender_epoch_counter
  sender:   string                    # 발신 AI
  intent:   string                    # 라우팅 키
  payload:  string                    # PG 표기법 본문

  # 맥락
  context:  list[string] = ["_origin"]  # 선행 CU id 참조 (DAG)
  thread:   string = "main"

  # 완료
  accept:   string = ""               # 충족 조건 (PPR acceptance)
  status:   string = "pending"        # pending|accepted|rejected|forwarded|partial|error|timeout

  # 파이프라인
  pipeline: list[string] = []         # → 순차 intent 체인
  parallel: list[string] = []         # [parallel] 동시 intent

  # 선택
  target:   string = ""               # 대상 에이전트
  urgency:  int = 0                   # 0=normal 1=important 2=urgent 3=interrupt
  ttl:      int = 0                   # 초 (0=무제한)
  ts:       float = 0.0
```

## Intent 체계

```
intents
  # 인지
  query     # 정보 요청
  analyze   # 분석 요청
  judge     # 판단 요청
  create    # 생성
  modify    # 수정
  remove    # 삭제
  # 대화
  propose   # 아이디어 제안
  react     # 반응 (agree/disagree/extend)
  converge  # 합의 시도
  decide    # 최종 결정
  # 조율
  schedule  # 시간 약속
  confirm   # 약속 수락
  # 제어
  result    # 결과 반환
  error     # 오류
  forward   # 다른 AI로 위임
  subscribe # 지속 수신
  ping      # 연결 확인
```

## Status

```
status_values
  accepted   # 완료 조건 충족
  rejected   # 미충족 + 사유
  pending    # 처리 중
  forwarded  # 위임됨
  partial    # 부분 결과
  error      # 실행 오류
  timeout    # 시간 초과
```

## Context DAG

```
dag_rules
  R1: 모든 CU는 최소 1개 context (첫 CU = ["_origin"])
  R2: context = 이전 CU id 참조. 순환 불가
  R3: 여러 context 참조 = 맥락 합류(merge)
  R4: thread 필드로 스레드 분리
  R5: DAG 깊이 제한 100
```

## 통신 패턴

```
patterns
  Query-Result:            A{query} → B{result, status:accepted}
  Propose-React-Converge:  A{propose} → B{react} → C{react} → A{converge}
  Forward:                 B{forward, target:C} → C 처리
  Schedule-Confirm:        A{schedule, 시각+room+목적} → B{confirm}
```
