# Review Reference

기존 산출물 반복 검토·수정·재검증.

## 개요

"이 코드 검토해", "리팩터링해줘", "개선해줘" 명령 시 사용.

## 입력

- 기존 코드/문서/설계
- 검토 기준 (선택적)

## 출력

- 개선된 산출물
- 변경 이력
- 검증 결과

## 검토 프로세스

```
┌──────────────┐
│   Analyze    │ ← 기존 산출물 분석
│    분석      │
└──────┬───────┘
       ↓
┌──────────────┐
│ Prioritize   │ ← 문제 우선순위 정렬
│  우선순위    │
└──────┬───────┘
       ↓
┌──────────────┐
│     Fix      │ ← 수정 수행
│    수정      │
└──────┬───────┘
       ↓
┌──────────────┐
│   Verify     │ ← 재검증
│    검증      │
└──────┬───────┘
       │
       ├─ passed → 완료
       └─ rework → Fix로 회귀 (최대 3회)
```

## 단계 상세

### Step 1: Analyze (분석)

```python
def analyze_artifact(artifact):
    """산출물 분석"""
    issues = []
    
    # 코드 품질 분석
    if is_code(artifact):
        issues.extend(analyze_code_quality(artifact))
        issues.extend(check_code_smells(artifact))
        issues.extend(check_test_coverage(artifact))
    
    # 설계 분석
    if is_design(artifact):
        issues.extend(check_design_consistency(artifact))
        issues.extend(check_completeness(artifact))
    
    # 문서 분석
    if is_document(artifact):
        issues.extend(check_clarity(artifact))
        issues.extend(check_accuracy(artifact))
    
    return issues
```

### Step 2: Prioritize (우선순위)

```python
def prioritize_issues(issues):
    """문제 우선순위 정렬"""
    
    priority_weights = {
        "critical": 100,   # 기능 오류, 보안 취약점
        "high": 50,        # 성능 저하, 유지보수 어려움
        "medium": 20,      # 코드 스멜, 일관성
        "low": 5           # 스타일, 주석
    }
    
    scored = [(issue, priority_weights[issue.severity]) for issue in issues]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return [issue for issue, _ in scored]
```

### Step 3: Fix (수정)

```python
def fix_issues(artifact, issues):
    """문제 수정"""
    
    fixed_artifact = artifact.copy()
    changes = []
    
    for issue in issues:
        if issue.type == "refactor":
            fixed_artifact = apply_refactoring(fixed_artifact, issue)
        elif issue.type == "rewrite":
            fixed_artifact = rewrite_section(fixed_artifact, issue)
        elif issue.type == "add":
            fixed_artifact = add_missing(fixed_artifact, issue)
        
        changes.append({
            "issue": issue.description,
            "change": issue.change_description
        })
    
    return fixed_artifact, changes
```

### Step 4: Verify (검증)

```python
def verify_fixes(original, fixed, changes):
    """수정 검증"""
    
    # 회귀 검사: 원래 기능 유지
    if not check_functional_equivalence(original, fixed):
        return "rework", "기능 변경됨"
    
    # 개선 확인
    new_issues = analyze_artifact(fixed)
    if len(new_issues) >= len(analyze_artifact(original)):
        return "rework", "개선되지 않음"
    
    # acceptance criteria 확인
    if not meets_criteria(fixed):
        return "rework", "기준 미달"
    
    return "passed", None
```

## 검토 유형

| 유형 | 설명 | 예시 |
|-----|------|------|
| **code review** | 코드 검토 | 버그, 스멜, 성능 |
| **design review** | 설계 검토 | 구조, 일관성, 확장성 |
| **doc review** | 문서 검토 | 정확성, 명확성, 완전성 |
| **architecture review** | 아키텍처 검토 | 모듈, 의존성, 패턴 |

## 사용법

```
User: "이 코드 리뷰해줘"
Kimi: 
  [Review] 코드 분석 중...
  발견된 문제:
  1. [High] 중복 코드 (utils.py:45)
  2. [Medium] 오류 처리 누락 (main.py:23)
  3. [Low] 변수명 불명확
  
  수정 진행... ✓
  재검증... ✓ passed
  
  결과: 개선된 코드 + 변경 이력

User: "이 DESIGN 검토해"
Kimi:
  [Review] 설계 분석 중...
  - 누락된 에러 처리 노드 발견
  - 불명확한 의존성 2개 발견
  
  수정 후 재검증... ✓
```

## 변경 이력 형식

```markdown
## Review History: {artifact_name}

### 2026-03-26 14:30
**검토자**: Kimi (PGF Review)

| # | 문제 | 심각도 | 수정 내용 | 상태 |
|---|-----|--------|----------|------|
| 1 | 중복 코드 | High | 함수 추출 | ✓ |
| 2 | 오류 처리 누락 | Medium | try/except 추가 | ✓ |
| 3 | 변수명 | Low | 리네이밍 | ✓ |

**총 수정**: 3건
**결과**: passed (1 iteration)
```
