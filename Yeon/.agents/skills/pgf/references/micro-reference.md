# Micro Reference

≤10노드 경량 실행. 파일 오버헤드 최소화.

## 사용 조건

| 항목 | 기준 |
|-----|------|
| 노드 수 | ≤ 10개 |
| 깊이 | ≤ 3레벨 |
| 외부 의존성 | 없음 (또는 매우 단순) |
| 예상 시간 | ≤ 30분 |
| 복잡도 | 단순 작업, 문서 작성, 소규모 리팩터링 |

## 특징

| 항목 | Full PGF | Micro |
|-----|---------|-------|
| DESIGN 파일 | 생성 | 인메모리 |
| WORKPLAN 파일 | 생성 | 인메모리 |
| status.json | 파일로 저장 | 변수로 관리 |
| POLICY | 상세 설정 | 기본값 사용 |
| 검증 | 3관점 | 경량 검증 |

## 실행 흐름

```python
def micro_execute(task_description):
    """경량 실행"""
    
    # 1. 빠른 분해 (Level 2 기준)
    nodes = AI_quick_decompose(task_description, max_nodes=10)
    
    if len(nodes) > 10:
        # 자동 승격: Full PGF로 전환
        return promote_to_full_pgf(task_description)
    
    # 2. 인메모리 상태 관리
    status = {node: "designing" for node in nodes}
    
    # 3. 순차 실행
    for node in nodes:
        status[node] = "in-progress"
        result = execute_node_inline(node)
        
        # 경량 검증
        if quick_verify(result):
            status[node] = "done"
        else:
            # 간단한 재시도
            result = execute_node_inline(node)
            status[node] = "done" if result.ok else "blocked"
    
    # 4. 결과 보고 (파일 없음)
    return generate_summary(status)
```

## 자동 승격

실행 중 조건 초과 시 Full PGF로 전환:

```python
def check_promotion():
    """승격 조건 확인"""
    if len(nodes) > 10:
        return True
    if depth > 3:
        return True
    if has_complex_dependencies():
        return True
    if estimated_time > 30:  # 분
        return True
    return False

# 승격 시
if check_promotion():
    save_current_progress()  # 필요 시
    return "복잡도 초과 → Full PGF로 전환합니다"
```

## 사용법

```
User: "이 함수 리팩터링해줘"
Kimi: [micro 모드] 인라인 분해 → 실행 → 완료

User: "이 코드에 에러 처리 추가해"
Kimi: [micro 모드] 3-4개 노드 분해 → 순차 실행 → 완료

User: "대규모 시스템 설계해"  (10+ 노드 예상)
Kimi: [자동 승격] "복잡한 작업입니다. Full PGF로 설계하겠습니다"
      → DESIGN 파일 생성 → WORKPLAN 생성 → 실행
```

## 상태 표현

파일 없이 간단한 텍스트로 표현:

```
[Micro PGF] TaskName
[1/5] NodeA .................... done
[2/5] NodeB .................... in-progress
[3/5] NodeC .................... designing
```

## 한계

- 세션 종료 시 상태 소멸
- 복잡한 롤백/복구 불가
- 병렬 실행 제한적
- 검증 간소화

## 권장 사용 사례

✅ **적합**:
- 함수 단위 리팩터링
- 간단한 문서 작성
- 설정 파일 수정
- 단일 파일 수정
- 버그 픽스 (단순)

❌ **부적합**:
- 아키텍처 설계
- 다중 파일 리팩터링
- 테스트 작성
- 복잡한 로직 구현
- 여러 모듈 변경
