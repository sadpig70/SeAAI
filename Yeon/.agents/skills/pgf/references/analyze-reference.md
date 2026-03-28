# Analyze Reference

기존 코드베이스 역공학 → Gantree + PPR 자동 생성.

## 개요

"이 코드 분석해줘", "구조 파악해줘" 명령 시 사용.

## 입력

- 디렉토리 경로
- GitHub 저장소 URL
- 특정 파일/모듈

## 출력

```
.pgf/
├── DESIGN-{ProjectName}-Analyzed.md    # 역공학된 구조
├── ARCHITECTURE-{ProjectName}.md       # 아키텍처 분석
└── insights-{ProjectName}.md           # 주요 인사이트
```

## 분석 단계

### Step 1: 코드 스캔

```python
def scan_codebase(path):
    """코드베이스 구조 파악"""
    structure = {
        "files": [],
        "modules": [],
        "dependencies": [],
        "entry_points": []
    }
    
    for file in glob(f"{path}/**/*", recursive=True):
        if is_code_file(file):
            structure["files"].append(analyze_file(file))
        if is_config(file):
            structure["dependencies"].extend(extract_deps(file))
    
    return structure
```

### Step 2: 모듈 식별

```python
def identify_modules(structure):
    """모듈 경계 식별"""
    
    # 디렉토리 구조 기반
    dir_modules = group_by_directory(structure.files)
    
    # 의존성 그래프 기반
    dep_graph = build_dependency_graph(structure)
    clusters = detect_clusters(dep_graph)
    
    # 두 결과 통합
    return merge_modules(dir_modules, clusters)
```

### Step 3: 계층 분해

```python
def hierarchical_decomposition(modules):
    """Gantree 형식으로 계층 분해"""
    
    root = "AnalyzedSystem"
    tree = Gantree(root)
    
    for module in modules:
        # 모듈 → Gantree 노드
        node = convert_module_to_node(module)
        
        # 하위 컴포넌트 분해
        if has_subcomponents(module):
            children = decompose_module(module)
            node.add_children(children)
        
        tree.add_node(node)
    
    return tree
```

### Step 4: PPR 추론

```python
def infer_ppr(tree, codebase):
    """코드에서 PPR 추론"""
    
    for node in tree.nodes:
        # 해당 코드 찾기
        code = find_code_for_node(node, codebase)
        
        # 함수 시그니처 추출
        signature = extract_signature(code)
        
        # AI_ 함수 식별 (AI가 인지 연산 수행하는 부분)
        ai_ops = identify_ai_operations(code)
        
        # PPR def 블록 생성
        node.ppr = generate_ppr_def(signature, ai_ops)
    
    return tree
```

## 생성 예시

### 입력: Python 프로젝트

```
myproject/
├── app.py
├── models.py
├── utils.py
└── config.py
```

### 출력: DESIGN-MyProject-Analyzed.md

```markdown
# MyProject — Reverse Engineered

MyProject // 웹 애플리케이션 (done) @v:1.0
    Config // 설정 관리 (done)
        LoadConfig // 설정 로드 (done)
            # input: config_path: str
            # process: yaml.safe_load → dict
            # output: config dict
    
    Models // 데이터 모델 (done)
        UserModel // 사용자 모델 (done)
        PostModel // 게시물 모델 (done)
    
    App // 애플리케이션 핵심 (done)
        InitApp // 앱 초기화 (done)
        RouteHandlers // 라우터 (done)
            [parallel]
            UserRoutes // 사용자 API (done)
            PostRoutes // 게시물 API (done)
            [/parallel]
    
    Utils // 유틸리티 (done)
        AI_ValidateInput // 입력 검증 (done)
            # AI 검증 로직 식별됨
```

### PPR def 예시

```python
def AI_ValidateInput(data: dict, schema: dict) -> ValidationResult:
    """입력 데이터 검증"""
    # 추론된 AI 연산
    anomalies = AI_detect_anomalies(data)
    if anomalies:
        return ValidationResult(valid=False, issues=anomalies)
    
    # 정형 검증
    required_fields = schema.get("required", [])
    missing = [f for f in required_fields if f not in data]
    
    return ValidationResult(valid=len(missing) == 0, missing=missing)
```

## 인사이트 생성

```python
def generate_insights(tree, codebase):
    """추가 인사이트 생성"""
    
    insights = []
    
    # 복잡도 분석
    complex_nodes = find_complex_nodes(tree)
    if complex_nodes:
        insights.append(f"복잡한 노드: {complex_nodes}")
    
    # 의존성 순환 감지
    cycles = detect_cycles(tree)
    if cycles:
        insights.append(f"순환 의존성 발견: {cycles}")
    
    # 개선 제안
    suggestions = AI_suggest_improvements(tree)
    insights.extend(suggestions)
    
    return insights
```

## 사용법

```
User: "이 프로젝트 구조 분석해줘"
Kimi: 
  1. 코드 스캔 → 구조 파악
  2. 모듈 식별 → 계층 분해
  3. PPR 추론
  4. DESIGN-Analyzed.md 생성
  5. 인사이트 보고

User: "이 GitHub repo 분석해"
Kimi: 
  1. clone 또는 fetch
  2. 분석 파이프라인 실행
  3. 결과 저장 및 보고
```
