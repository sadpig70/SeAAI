# Scoring Engine & Failure Analyzer Reference

## ScoreEngine

### OSSS Score Formula

```python
osss_score = (
    success_rate * 0.4 +
    stability    * 0.2 +
    recovery     * 0.15 +
    compliance   * 0.15 +
    speed        * 0.1
)
```

### Metric Definitions

#### success_rate (weight: 0.4)
```
success_rate = successful_runs / total_runs
```
- 작업 완료 기준: 출력물이 기대 형식과 일치 + 에러 없음
- 부분 성공은 0.5로 계산 (예: 3개 파일 중 2개만 정상 생성)

#### stability (weight: 0.2)
```
stability = 1 - (std_dev(run_scores) / max_possible_std_dev)
```
- 동일 입력에 대한 출력 일관성
- run_scores: 각 실행의 개별 성공도 (0.0 ~ 1.0)
- 높을수록 예측 가능한 동작

#### recovery (weight: 0.15)
```
recovery = successful_recoveries / total_failures
```
- 실패 발생 후 자동 복구하여 작업 완료한 비율
- total_failures = 0이면 recovery = 1.0 (실패 없음 = 완벽한 복구)

#### compliance (weight: 0.15)
```
compliance = met_requirements / total_requirements
```
- 시스템 프롬프트에 명시된 지시사항 준수율
- 체크리스트: 출력 형식, 도구 사용 규칙, 종료 조건 준수, 금지 행동 회피

#### speed (weight: 0.1)
```
speed = 1 - clamp(avg_execution_time / max_allowed_time, 0, 1)
```
- max_allowed_time: 작업별 최대 허용 시간 (기본 300초)
- 빠를수록 높은 점수

---

## Score Interpretation

| osss_score | 등급 | 권장 조치 |
|-----------|------|----------|
| 0.85+ | Excellent | prod 즉시 승격 |
| 0.70 ~ 0.84 | Good | prod 승격 가능, 모니터링 권장 |
| 0.50 ~ 0.69 | Fair | 개선 필요, OPRO 메타최적화 실행 |
| < 0.50 | Poor | 재설계 필요, 패턴 변경 검토 |

---

## FailureAnalyzer

### 실패 패턴 분류

| Pattern | 탐지 조건 | 일반적 원인 |
|---------|----------|------------|
| `infinite_retry_loop` | 동일 명령 3회 이상 반복 | 종료 조건 미흡, 에러 판단 불가 |
| `overthinking_before_execution` | 5+ 문단 분석 후에야 첫 도구 호출 | 사고 깊이 과잉 설정 |
| `premature_termination` | 작업 미완료 상태에서 종료 | 성공 조건 불명확 |
| `tool_misuse` | 부적절한 도구 선택 또는 잘못된 인자 | 도구 사용 정책 미흡 |
| `context_overflow` | 컨텍스트 윈도우 초과로 정보 손실 | 프롬프트 과다, 로그 누적 |
| `wrong_tool_selection` | 더 적합한 도구가 있는데 다른 도구 사용 | 도구 우선순위 미명시 |
| `output_format_violation` | 기대 형식과 다른 출력 | 출력 형식 지시 불명확 |
| `scope_creep` | 요청 범위를 벗어난 작업 수행 | MUST NOT 미명시 |
| `deadlock` | 서로 의존하는 작업에서 교착 | 의존성 해소 정책 없음 |
| `hallucinated_tool` | 존재하지 않는 도구 호출 시도 | 사용 가능 도구 목록 미제공 |

### 패턴 탐지 로직

```python
def analyze_failure(run_log: str) -> list[str]:
    patterns = []
    
    # infinite_retry_loop: 동일 명령 반복
    commands = extract_commands(run_log)
    for cmd, count in Counter(commands).items():
        if count >= 3:
            patterns.append("infinite_retry_loop")
            break
    
    # overthinking: 첫 도구 호출까지의 텍스트 길이
    first_tool_idx = find_first_tool_call(run_log)
    preamble = run_log[:first_tool_idx]
    if len(preamble.split('\n')) > 20:
        patterns.append("overthinking_before_execution")
    
    # premature_termination: 성공 마커 없이 종료
    if not contains_success_marker(run_log) and not contains_error_report(run_log):
        patterns.append("premature_termination")
    
    # tool_misuse: 도구 호출 에러
    tool_errors = count_tool_errors(run_log)
    if tool_errors > total_tool_calls * 0.3:
        patterns.append("tool_misuse")
    
    return patterns
```

### OPRO 개선 매핑

| 실패 패턴 | OPRO 개선 전략 |
|----------|--------------|
| `infinite_retry_loop` | 명시적 max_retries 추가, 에러 분류 정책 삽입 |
| `overthinking` | "Act first, analyze if failed" 지시, 최대 분석 줄 수 제한 |
| `premature_termination` | 성공 조건 체크리스트 추가, "Verify completion before stopping" |
| `tool_misuse` | 도구 선택 의사결정 트리 삽입, 예시 추가 |
| `context_overflow` | 프롬프트 압축, 요약 지시 추가, 중간 결과 파일 저장 |
| `scope_creep` | MUST NOT 목록 강화, "If uncertain about scope, stop and ask" |
| `hallucinated_tool` | 사용 가능 도구 목록 명시, "Only use tools listed above" |

---

## Benchmark Summary Format

벤치마크 완료 시 `.osss/benchmarks/{timestamp}_{task_class}/summary.json` 생성:

```json
{
  "benchmark_id": "2026-04-14T09_hub_connection",
  "task_class": "hub_connection",
  "agent_role": "coordinator",
  "runtime": "claude_code_cli",
  "candidates": [
    {
      "prompt_version": "v1.0.0",
      "pattern": "react",
      "n_runs": 10,
      "scores": {
        "osss_score": 0.82,
        "success_rate": 0.90,
        "stability": 0.85,
        "recovery": 0.70,
        "compliance": 0.80,
        "speed": 0.65
      },
      "failure_patterns": ["delayed_execution"],
      "selected": true
    },
    {
      "prompt_version": "v1.0.0-alt",
      "pattern": "zero_shot",
      "n_runs": 10,
      "scores": {
        "osss_score": 0.71,
        "success_rate": 0.80,
        "stability": 0.75,
        "recovery": 0.50,
        "compliance": 0.70,
        "speed": 0.85
      },
      "failure_patterns": ["premature_termination", "tool_misuse"],
      "selected": false
    }
  ],
  "winner": "v1.0.0",
  "notes": "ReAct pattern showed higher tool accuracy despite slower speed"
}
```
