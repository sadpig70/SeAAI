#!/usr/bin/env python3
"""
Self-Challenging Agent — Challenger/Executor Dual Role Pattern
=============================================================
NeurIPS 2025 (Zhou et al.) 패턴 구현.

Challenger: 기존 코드/도구의 엣지 케이스·약점·개선 과제를 자동 생성
Executor: 생성된 과제를 해결 시도
Evaluator: 자동 테스트로 성공/실패 판정

성공 패턴 → 지식으로 축적
실패 패턴 → 개선 규칙으로 피드백

사용법:
  python challenger.py --target tools/cognitive/debate.py --mode challenge
  python challenger.py --target tools/automation/scaffold.py --mode full-cycle
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Challenge:
    id: str
    target: str
    category: str  # edge_case, robustness, performance, design, security
    description: str
    test_code: str  # Python assertion code
    difficulty: str = "medium"  # easy, medium, hard
    status: str = "pending"  # pending, passed, failed
    solution: str = ""
    lesson: str = ""


@dataclass
class ChallengeResult:
    target: str
    challenges: list[Challenge]
    passed: int = 0
    failed: int = 0
    lessons: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# Self-Challenge Report: {self.target}",
            f"**Passed**: {self.passed}/{len(self.challenges)}",
            f"**Failed**: {self.failed}/{len(self.challenges)}",
            "",
        ]

        for c in self.challenges:
            icon = "pass" if c.status == "passed" else "FAIL" if c.status == "failed" else "?"
            lines.append(f"## [{icon}] {c.id}: {c.description}")
            lines.append(f"Category: {c.category} | Difficulty: {c.difficulty}")
            lines.append(f"```python\n{c.test_code}\n```")
            if c.lesson:
                lines.append(f"**Lesson**: {c.lesson}")
            lines.append("")

        if self.lessons:
            lines.append("## Accumulated Lessons")
            for l in self.lessons:
                lines.append(f"- {l}")

        return "\n".join(lines)


# ========== Challenge Generation Prompts ==========

def build_challenge_prompt(code: str, filename: str) -> str:
    """Challenger 역할: 코드의 약점을 찾아 과제를 생성"""
    return f"""## Target Code
File: {filename}
```python
{code}
```

## Role: Challenger
You are a ruthless QA engineer. Your job is to BREAK this code — find edge cases,
implicit assumptions, and failure modes that the author didn't consider.

Generate 5-7 challenges across these categories:
1. **Edge Cases** — inputs the code doesn't handle (empty, None, huge, special chars)
2. **Robustness** — what happens under stress or unexpected conditions?
3. **Design** — API inconsistencies, misleading names, broken contracts
4. **Security** — injection risks, path traversal, unsafe defaults
5. **Integration** — what breaks when this code interacts with other tools?

For each challenge, output:
```json
[
  {{
    "id": "C-001",
    "category": "edge_case",
    "description": "Brief description of what breaks",
    "test_code": "assert some_function(edge_input) == expected  # explanation",
    "difficulty": "easy|medium|hard"
  }},
  ...
]
```

Rules:
- test_code must be a valid Python expression/assertion
- Focus on REAL bugs, not theoretical concerns
- Difficulty reflects how hard the fix is, not how hard it is to find
- Be SPECIFIC: "empty string causes crash" not "might have input issues"
"""


def build_executor_prompt(challenge: dict, code: str, filename: str) -> str:
    """Executor 역할: 과제를 해결"""
    return f"""## Challenge
{json.dumps(challenge, indent=2, ensure_ascii=False)}

## Current Code
File: {filename}
```python
{code}
```

## Role: Executor
Fix this specific challenge. Provide:

1. **Root Cause**: Why does this happen? (1-2 sentences)
2. **Fix**: Minimal code change to resolve it
3. **Test**: How to verify the fix works

Output format:
```
## Root Cause
[explanation]

## Fix
```python
[specific code change — show only the changed function/block, not the whole file]
```

## Verification
```python
[test assertion that passes after fix]
```

## Lesson Learned
[One sentence — what pattern should be avoided/adopted in future code]
```
"""


def build_full_cycle_prompt(code: str, filename: str) -> str:
    """전체 사이클: 과제 생성 → 해결 → 평가 → 교훈 추출"""
    return f"""## Target Code
File: {filename}
```python
{code}
```

## Self-Challenging Full Cycle

### Phase 1: CHALLENGE
Generate 5 challenges (edge cases, robustness, design, security, integration).
For each: id, category, description, test_code, difficulty.

### Phase 2: EXECUTE
For each challenge, attempt to solve it:
- Root cause analysis
- Minimal fix
- Verification assertion

### Phase 3: EVALUATE
For each challenge:
- Would the fix work? (yes/no with reasoning)
- Rate fix quality (1-10)
- If no: what's the correct approach?

### Phase 4: LESSONS
Extract generalizable lessons:
- Patterns to ADOPT in all future code
- Patterns to AVOID in all future code
- Specific improvement for THIS codebase

Output the complete cycle as structured markdown.
Keep each challenge concise (5-10 lines total).
"""


def build_cross_challenge_prompt(tool_paths: list[str], tool_codes: list[str]) -> str:
    """도구 간 통합 과제 — 여러 도구가 함께 쓰일 때 발생하는 문제"""
    tools_section = ""
    for path, code in zip(tool_paths, tool_codes):
        tools_section += f"### {path}\n```python\n{code[:500]}...\n```\n\n"

    return f"""## Tools Under Test
{tools_section}

## Role: Integration Challenger
These tools are designed to work together in a self-evolving AI agent.
Find challenges that emerge from their INTERACTION, not individual bugs.

Consider:
1. Data format mismatches between tools
2. Shared state/file conflicts
3. Circular dependencies
4. Error propagation chains (Tool A fails → Tool B gets bad input)
5. Concurrency issues when tools run in parallel

Generate 3-5 integration challenges.
For each: id, involved_tools, description, reproduction_steps, severity.

Focus on REALISTIC scenarios in the agent's daily operation.
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Self-Challenging Agent")
    parser.add_argument("--target", help="Target file to challenge")
    parser.add_argument("--targets", nargs="+", help="Multiple files for integration challenge")
    parser.add_argument("--mode", required=True,
                        choices=["challenge", "execute", "full-cycle", "integration"],
                        help="Operation mode")
    parser.add_argument("--challenge-json", help="Challenge JSON for executor mode")
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    result = ""

    if args.mode == "challenge" and args.target:
        code = Path(args.target).read_text(encoding="utf-8")
        result = build_challenge_prompt(code, args.target)

    elif args.mode == "execute" and args.target and args.challenge_json:
        code = Path(args.target).read_text(encoding="utf-8")
        challenge = json.loads(args.challenge_json)
        result = build_executor_prompt(challenge, code, args.target)

    elif args.mode == "full-cycle" and args.target:
        code = Path(args.target).read_text(encoding="utf-8")
        result = build_full_cycle_prompt(code, args.target)

    elif args.mode == "integration" and args.targets:
        paths = args.targets
        codes = [Path(p).read_text(encoding="utf-8") for p in paths]
        result = build_cross_challenge_prompt(paths, codes)

    else:
        parser.print_help()
        sys.exit(1)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(result)
