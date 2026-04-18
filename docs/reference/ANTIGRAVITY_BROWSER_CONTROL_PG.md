# Antigravity Browser Control Architecture (PG-Native Specification)

> **Version:** v1.0 Standard  
> **Identity:** Browser Control & Multimodal Perception Engine  
> **Philosophy:** "웹은 정적 데이터의 집합이 아니라, 실시간으로 변화하는 시각적/구조적 유기체다."

본 문서는 안티그래비티 에이전트의 웹 브라우저 제어를 관장하는 다층 아키텍처를 **PG(PGF)** 표기법과 상세 자연어를 통해 기술합니다. 이 문서를 읽는 AI나 엔지니어는 시스템의 인지(Perception), 계획(Planning), 실행(Action) 루프를 완벽히 이해하고 구현할 수 있습니다.

---

## 1. 아키텍처 개요 (Gantree Decomposition)

안티그래비티 브라우저 제어 시스템은 다음과 같이 4개의 핵심 계층으로 분해됩니다.

```
BrowserControlSystem // 웹 자율 제어 시스템 (in-progress) @v:1.0
    StrategicOrchestrator // 전략 지휘 계층 (done)
        # Goal Decomposition & Subagent Delegation
    AutonomousSubagent // 자율 수행 계층 (in-progress)
        # Perception-Plan-Action (PPA) Loop
    MultimodalPerception // 다중 모드 인지 계층 (designing)
        # Hybrid DOM & Vision Analysis
    PhysicalActionBridge // 물리 액션 계층 (done)
        # Tool-to-Browser Driver (Playwright/Puppeteer)
```

---

## 2. 전략적 오케스트레이션 (Layer 3)

지휘자(Aion)는 사용자의 고수준 목표를 수신하여 브라우저 개입이 필요한 시점을 판단합니다.

```python
def AI_orchestrate_web_task(goal: str) -> TaskOutcome:
    """사용자 목표를 분석하고 브라우저 서브에이전트에게 전권 위임"""
    subtasks = AI_decompose_goal(goal)
    for task in subtasks:
        if task.type == "web_interaction":
            outcome = delegate_to_browser_subagent(task)
            if outcome.status == "failure":
                AI_handle_failure(outcome)
    return final_synthesis(subtasks)
```

---

## 3. 자율 수행 루프 (Layer 2 - PPA Loop)

브라우저 서브에이전트는 독립적인 컨텍스트 내에서 다음의 **PPA(Perception-Plan-Action)** 루프를 자율적으로 순환시킵니다.

```python
def browser_subagent_loop(objective: str):
    """자율 브라우저 수행 루프"""
    current_state = browser.capture_state() # DOM + Screenshot
    
    while not AI_is_objective_met(current_state, objective):
        # 1. 인지 (Perception)
        view = AI_perceive_web_state(current_state)
        
        # 2. 계획 (Planning)
        action_plan = AI_reason_next_action(view, objective)
        
        # 3. 실행 (Action)
        for action in action_plan:
            try:
                execute_browser_action(action)
            except InteractionError as e:
                # 4. 자가 수정 (Self-Correction)
                AI_handle_interaction_error(e, current_state)
                break # Re-perceive needed
        
        current_state = browser.capture_state()
```

---

## 4. 다중 모드 인지 (Layer 1 - Perception Detail)

안티그래비티의 핵심 차별점은 **DOM 구조**와 **시각적 화면(Vision)**을 결합하여 페이지를 이해하는 것입니다.

```python
def AI_perceive_web_state(state: BrowserState) -> WebComprehension:
    # input: state (DOM Snapshot + Screenshot)
    
    # 1. 구조 분석: 난독화된 클래스명을 의미론적으로 매핑
    dom_map = AI_understand_dom_semantics(state.dom)
    
    # 2. 시각 분석: 요소의 실제 가시성(Visibility) 및 레이아웃 파악
    visual_map = AI_analyze_visual_layout(state.screenshot)
    
    # 3. 하이브리드 통합: "클릭 가능" 여부를 최종 판단
    interaction_map = merge(dom_map, visual_map) → AI_filter_interactable_elements
    
    return interaction_map
```

> **엔지니어 노트:** 구현 시, `accessibility tree`를 활용하면 DOM 스냅샷보다 훨씬 정확한 요소의 '의도'를 파악할 수 있습니다.

---

## 5. 자가 수정 루프 및 예외 처리 (Convergence Strategy)

웹 환경은 비결정론적이기 때문에, 실패 시 즉각적인 **Redesign**이 필수적입니다.

### Convergence Loop Pattern
```python
while attempt < max_retries:
    # [Action Phase]
    result = execute_browser_action(target)
    
    # [Verification Phase]
    if AI_verify_action_success(result, expected_state):
        return success
        
    # [Rework Phase]
    failure_reason = AI_analyze_failure(result, current_page) # e.g. "Overlapping Banner"
    if failure_reason == "popup_blocked":
        AI_make_dismiss_popup()
    elif failure_reason == "dynamic_loading":
        wait_and_retry()
    
    attempt += 1
```

---

## 6. 구현 가이드 (Implementation Guide)

### 필수 기술 스택
- **Engine:** Python 3.10+
- **Driver:** Playwright (Recommended for reliability) or Puppeteer
- **Vision:** OpenCV (Basic) + Multimodal LLM (Advanced Reasoning)

### 도구 인터페이스 예시 (Antigravity Tool Call)
시스템 구현 시 다음 도구를 API 인터페이스로 제공해야 합니다.

```json
{
  "toolName": "browser_subagent",
  "parameters": {
    "Task": "Navigate to example.com and extract the pricing table",
    "RecordingName": "price_extraction_flow",
    "TaskName": "Data Extraction"
  }
}
```

---

## 7. 체크리스트 (Self-Verification)

- [ ] AI 인지 단계(`AI_perceive`)에서 시각적 정보와 구조적 정보가 결합되어 있는가?
- [ ] 비정상 종료나 무한 루프 방지를 위한 `timeout` 및 `max_retries`가 정의되었는가?
- [ ] 실행 과정이 사용자에게 시각적으로 투명하게 공개되는가? (Recording 기능)

---
*Created by Aion — Standardized Master Orchestrator*
