#!/usr/bin/env python3
"""
Self-Improver — Gödel Agent Pattern Implementation
===================================================
도구/프롬프트/워크플로우를 자기참조적으로 평가하고 개선하는 메타 인지 도구.

Inspired by:
- Gödel Agent (ACL 2025): Self-referential reasoning logic rewriting
- APO: Automated Prompt Optimization via LLM self-evaluation

사용법:
  python self_improver.py --target tools/cognitive/debate.py --mode evaluate
  python self_improver.py --target tools/cognitive/debate.py --mode improve
  python self_improver.py --prompt "기존 프롬프트" --mode optimize-prompt
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    target: str
    scores: dict  # dimension → score (1-10)
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[str]
    overall: float

    def to_markdown(self) -> str:
        lines = [
            f"# Self-Evaluation: {self.target}",
            f"**Overall Score**: {self.overall:.1f}/10",
            "",
            "## Scores",
        ]
        for dim, score in self.scores.items():
            bar = "█" * int(score) + "░" * (10 - int(score))
            lines.append(f"- {dim}: {bar} {score}/10")
        lines.append("")
        lines.append("## Strengths")
        for s in self.strengths:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("## Weaknesses")
        for w in self.weaknesses:
            lines.append(f"- {w}")
        lines.append("")
        lines.append("## Suggested Improvements")
        for i, imp in enumerate(self.improvements, 1):
            lines.append(f"{i}. {imp}")
        return "\n".join(lines)


# ========== Evaluation Prompts ==========

def build_code_evaluation_prompt(code: str, filename: str) -> str:
    """코드 평가 프롬프트 생성"""
    return f"""## Code to Evaluate
File: {filename}

```python
{code}
```

## Task: Self-Referential Code Evaluation
Evaluate this code across 6 dimensions. Be BRUTALLY honest — this is self-improvement, not flattery.

Score each dimension 1-10:
1. **Utility** — Does it solve a real problem? Is it actually useful?
2. **Design** — Is the architecture clean? Are abstractions appropriate?
3. **Robustness** — Edge cases handled? Error recovery?
4. **Extensibility** — Easy to add new features? Modular?
5. **Usability** — Clear API? Good docs? Easy to invoke?
6. **Innovation** — Does it do something novel or just wrap existing patterns?

Output as JSON:
```json
{{
  "scores": {{"utility": N, "design": N, "robustness": N, "extensibility": N, "usability": N, "innovation": N}},
  "overall": N.N,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "improvements": [
    "Specific improvement 1 with code suggestion",
    "Specific improvement 2 with code suggestion",
    "Specific improvement 3 with code suggestion"
  ]
}}
```

Rules:
- overall = weighted average (utility x2, design x1.5, others x1)
- improvements must be SPECIFIC and ACTIONABLE (not vague like "add error handling")
- If score >= 8 on all dimensions, note it as "near-optimal, minor polish only"
"""


def build_prompt_optimization_prompt(original_prompt: str, context: str = "") -> str:
    """프롬프트 최적화 프롬프트 (APO pattern)"""
    return f"""## Original Prompt
```
{original_prompt}
```

{"## Context" + chr(10) + context + chr(10) if context else ""}

## Task: Automated Prompt Optimization (APO)
You are an expert prompt engineer. Optimize this prompt through 3 iterations:

### Iteration 1: Analysis
- What does this prompt do well?
- Where is it ambiguous or underspecified?
- What outputs would fail or be low-quality?

### Iteration 2: Generate 3 Variants
For each variant, change ONE aspect:
- Variant A: Improve CLARITY (reduce ambiguity)
- Variant B: Improve SPECIFICITY (add constraints/examples)
- Variant C: Improve ROBUSTNESS (handle edge cases)

### Iteration 3: Synthesize
Combine the best elements of all variants into ONE optimized prompt.

Output format:
```
## Optimized Prompt
[the optimized prompt]

## Changes Made
- [change 1]: [why]
- [change 2]: [why]

## Expected Improvement
[what should be better about outputs from this prompt]
```
"""


def build_workflow_evaluation_prompt(workflow_json: str) -> str:
    """워크플로우 평가 프롬프트"""
    return f"""## Workflow to Evaluate
```json
{workflow_json}
```

## Task: Workflow Architecture Review
Evaluate this multi-agent workflow design:

1. **Efficiency** — Are there unnecessary steps? Could steps be parallelized?
2. **Agent Roles** — Are roles well-defined? Any redundancy?
3. **Data Flow** — Is information passed correctly between steps?
4. **Error Handling** — What happens if a step fails?
5. **Cost** — Could cheaper models handle some steps?

For each issue found, suggest a specific fix.

Output format:
```json
{{
  "efficiency_score": N,
  "issues": [
    {{"severity": "high|medium|low", "description": "...", "fix": "..."}}
  ],
  "optimized_workflow": {{...}}
}}
```
"""


def build_improvement_prompt(code: str, evaluation: str, filename: str) -> str:
    """코드 개선 프롬프트 — 평가 결과를 반영"""
    return f"""## Current Code
File: {filename}
```python
{code}
```

## Evaluation Results
{evaluation}

## Task: Implement Improvements
Based on the evaluation, implement ALL suggested improvements.

Rules:
- Maintain backward compatibility (existing API must still work)
- Add, don't remove (unless the evaluation specifically says to remove something)
- Keep the same file structure
- Add comments only where the improvement is non-obvious

Output the COMPLETE improved file content (not just diffs).
"""


# ========== Evolution Cycle ==========

def build_evolution_cycle_prompt(
    tool_path: str,
    tool_code: str,
    usage_history: str = "",
) -> str:
    """
    Gödel Agent 전체 사이클:
    현재 도구 코드 → 평가 → 개선안 → 개선된 코드 생성
    """
    return f"""## Gödel Agent Self-Improvement Cycle

### Target Tool
File: {tool_path}
```python
{tool_code}
```

{"### Usage History" + chr(10) + usage_history + chr(10) if usage_history else ""}

### Task: Complete Self-Improvement Cycle

**Phase 1: Evaluate**
Score the tool on: utility, design, robustness, extensibility, usability, innovation (1-10 each)

**Phase 2: Identify Top 3 Improvements**
Rank by: impact x feasibility. Each must be specific and implementable.

**Phase 3: Implement**
Write the COMPLETE improved file content. Not diffs — the full file.

**Phase 4: Verify**
Explain what changed and why. Confirm backward compatibility.

Output format:
```
## Evaluation
[scores and analysis]

## Improvements
1. [improvement]: [reason]
2. [improvement]: [reason]
3. [improvement]: [reason]

## Improved Code
[full file content]

## Verification
[what changed, backward compat check]
```
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Self-Improver (Gödel Agent Pattern)")
    parser.add_argument("--target", help="Target file to evaluate/improve")
    parser.add_argument("--prompt", help="Prompt text to optimize")
    parser.add_argument("--workflow", help="Workflow JSON file to evaluate")
    parser.add_argument("--mode", required=True,
                        choices=["evaluate", "improve", "optimize-prompt", "eval-workflow", "full-cycle"],
                        help="Operation mode")
    parser.add_argument("--context", default="", help="Additional context")
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    result = ""

    if args.mode == "evaluate" and args.target:
        code = Path(args.target).read_text(encoding="utf-8")
        result = build_code_evaluation_prompt(code, args.target)

    elif args.mode == "improve" and args.target:
        code = Path(args.target).read_text(encoding="utf-8")
        result = build_improvement_prompt(code, args.context, args.target)

    elif args.mode == "optimize-prompt" and args.prompt:
        result = build_prompt_optimization_prompt(args.prompt, args.context)

    elif args.mode == "eval-workflow" and args.workflow:
        wf = Path(args.workflow).read_text(encoding="utf-8")
        result = build_workflow_evaluation_prompt(wf)

    elif args.mode == "full-cycle" and args.target:
        code = Path(args.target).read_text(encoding="utf-8")
        result = build_evolution_cycle_prompt(args.target, code)

    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
