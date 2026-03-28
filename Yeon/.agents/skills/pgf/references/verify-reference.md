# Verify Reference

3관점 검증 가이드.

## 검증 개요

각 노드 실행 후 반드시 수행. 실패 시 재작업 또는 blocked.

## 3관점 검증

### 1. Acceptance Criteria (수용 기준)

DESIGN의 `acceptance_criteria` 충족 확인:

```python
def verify_acceptance(result, criteria):
    """
    criteria 예시:
    - "모든 필드 포함"
    - "AI_assess_quality >= 0.85"
    - "응답 시간 < 5초"
    """
    checks = []
    
    for criterion in criteria:
        if "포함" in criterion:
            checks.append(check_fields_present(result, criterion))
        elif "quality" in criterion or "품질" in criterion:
            score = AI_assess_quality(result)
            checks.append(score >= 0.85)
        elif "시간" in criterion or "time" in criterion:
            checks.append(check_performance(result, criterion))
    
    return all(checks)
```

### 2. Code Quality (코드 품질)

구현물의 품질 검증:

| 항목 | 검증 방법 |
|-----|----------|
| 중복 제거 | 동일 패턴 반복 여부 |
| 효율성 | 시간/공간 복잡도 |
| 가독성 | 명명 규칙, 주석 |
| 재사용성 | 모듈화, 인터페이스 |

```python
def verify_quality(code_or_output):
    """품질 검증"""
    issues = []
    
    # 중복 검사
    if detect_duplication(code_or_output):
        issues.append("중복 코드 발견")
    
    # 복잡도 검사
    if complexity_score(code_or_output) > threshold:
        issues.append("복잡도 초과")
    
    return len(issues) == 0, issues
```

### 3. Architecture Match (아키텍처 일치)

DESIGN Gantree와 실제 구현 구조 비교:

```python
def verify_architecture(design_tree, implementation):
    """
    DESIGN에 정의된 구조와 실제 구현이 일치하는지 확인
    """
    design_nodes = extract_node_names(design_tree)
    impl_nodes = extract_implementation_structure(implementation)
    
    missing = design_nodes - impl_nodes
    extra = impl_nodes - design_nodes
    
    return len(missing) == 0, {"missing": missing, "extra": extra}
```

## 검증 결과 처리

| 결과 | 다음 동작 |
|-----|----------|
| **passed** | 다음 노드 진행 |
| **rework** | 현재 노드 재실행 (max_iterations 초과 시 blocked) |
| **blocked** | 사용자 보고, 분기 노드로 전환 또는 중단 |

## Failure Strategy

```python
max_retry = POLICY.max_iterations or 3

for attempt in range(max_retry):
    result = execute_node(node)
    
    # 3관점 검증
    passed = True
    feedback = []
    
    if not verify_acceptance(result, node.criteria):
        passed = False
        feedback.append("Acceptance criteria failed")
    
    if not verify_quality(result):
        passed = False
        feedback.append("Quality check failed")
    
    if not verify_architecture(node, result):
        passed = False
        feedback.append("Architecture mismatch")
    
    if passed:
        node.status = "done"
        break
    else:
        # 재설계
        if attempt < max_retry - 1:
            node.ppr = AI_redesign(node.ppr, feedback)
        else:
            node.status = "blocked"
```

## 가벼운 검증 (Lightweight)

micro 모드 또는 단순 작업:

```python
def verify_lightweight(result, node):
    """간소화 검증"""
    # 인라인 criteria만 확인
    if "# criteria:" in node.comments:
        return AI_verify(result, node.comments["criteria"])
    return True
```
