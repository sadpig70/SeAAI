# Practical Example: Content Generation System

## Gantree Design

```
ContentGenSystem // Content generation system (in-progress) @v:1.0

    InputProcessing // Input processing (done)
        TopicAnalyzer // Topic analysis (done) → ContentPlanner
            AI_extract_keywords // Keyword extraction (done)
            AI_classify_topic // Topic classification (done)
        ContextLoader // Context loading (done)
            load_user_preferences // Load user preferences (done)
            load_style_guide // Load style guide (done)

    ContentPlanning // Content planning (in-progress) @dep:InputProcessing
        ContentPlanner // Content planner (in-progress)
            AI_generate_outline // Outline generation (done)
            AI_plan_structure // Structure planning (in-progress)
        QualityPredictor // Quality predictor (designing)
            AI_predict_engagement // Engagement prediction (designing)

    ContentGeneration // Content generation (designing) @dep:ContentPlanning
        [parallel]
        TextGenerator // Text generator (designing)
            AI_generate_title // Title generation (designing)
            AI_generate_body // Body generation (designing)
        VisualPlanner // Visual planner (designing)
            AI_plan_visuals // Visual element planning (designing)
        [/parallel]

    QualityAssurance // Quality assurance (blocked)
        AI_evaluate_content // Content evaluation (blocked)
        AI_integrate_feedback // Feedback integration (blocked)
```

## PPR Detail — ContentPlanner Node

```python
def content_planner(
    topic: str,
    keywords: list[str],
    audience: Literal["general", "technical", "executive"],
    constraints: Optional[dict] = None,
) -> dict:
    """Content planner — generate outline tailored to topic and audience"""

    context = load_domain_knowledge(topic)
    audience_profile = AI_analyze_audience(audience)

    raw_outline: list[dict] = AI_generate_outline(
        topic=topic,
        keywords=keywords,
        context=context,
        audience=audience_profile,
    )

    # Conditional adjustment
    if constraints:
        raw_outline = AI_adjust_outline(raw_outline, constraints)

    # Iteration: assign priorities
    for section in raw_outline:
        section["priority"] = AI_assess_priority(section, audience)

    outline = sorted(raw_outline, key=lambda s: s["priority"], reverse=True)

    # Metadata generation
    metadata = {
        "estimated_length": calculate_estimated_length(outline),
        "complexity": AI_assess_complexity(outline),
    }

    return {"outline": outline, "metadata": metadata}
```

## PPR Detail — TextGenerator Node

```python
def text_generator(
    outline: list[dict],
    style_guide: dict,
) -> dict:
    """Text generator — title/body writing with quality convergence based on outline"""

    title: str = AI_generate_title(
        topic=outline[0]["title"],
        style=style_guide["tone"],
    )

    body_parts: list[str] = []
    for section in outline:
        draft: str = AI_generate_body(section=section, style=style_guide)

        # Convergent iteration — until quality threshold met
        while True:
            evaluation = AI_evaluate(draft)  # -> {"score": float, "feedback": str}
            if evaluation["score"] >= 0.85:
                break
            draft = AI_revise(draft, evaluation["feedback"])

        body_parts.append(draft)

    body = "\n\n".join(body_parts)
    return {"title": title, "body": body}
```

## Execution Flow Interpretation

```
1. InputProcessing (done) → execute
   - AI_extract_keywords("user input") → list[str]
   - AI_classify_topic(text, keywords) → str
   - load_user_preferences() → actual Python code (deterministic)
   - load_style_guide() → actual Python code (deterministic)

2. ContentPlanning (in-progress) → execute per PPR def block
   - content_planner() invocation (see PPR above)
   - QualityPredictor (designing) → return defaults

3. ContentGeneration (designing) → basic logic only
   - TextGenerator, VisualPlanner parallel but designing, so stubs

4. QualityAssurance (blocked) → skip
```
