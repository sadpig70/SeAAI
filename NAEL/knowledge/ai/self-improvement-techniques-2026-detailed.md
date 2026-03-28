---
title: AI Agent Self-Improvement — Top 5 Techniques (2026 Research)
domain: ai
tags: [self-improvement, STOP, MCP, context-engineering, self-challenging]
date: 2026-03-21
---

# Top 5 Self-Improvement Techniques for Claude Code (2026)

## 1. Agent Skills 2.0 — Programmable Self-Extension
- SKILL.md로 반복 워크플로를 슬래시 커맨드 패키징
- 라이프사이클 훅으로 실시간 데이터 주입
- 1,234+ 커뮤니티 스킬 생태계
- Source: https://code.claude.com/docs/en/skills

## 2. MCP Custom Server — Domain-Specific Tool Self-Creation ✓ IMPLEMENTED
- Claude의 네이티브 도구 확장
- Tool Search lazy loading → 컨텍스트 95% 절감
- Source: https://modelcontextprotocol.io/docs/develop/build-server

## 3. STOP Pattern — Recursive Code Self-Improvement Loop
- Microsoft Research: Self-Taught Optimizer
- improver가 자신을 입력으로 받아 개선된 improver 출력
- `improve(program, utility_fn) → better_program`
- Source: https://arxiv.org/abs/2310.02304, https://github.com/microsoft/stop

## 4. Context Engineering — Dynamic Context Composition
- Anthropic 제시: "어떤 컨텍스트 구성이 원하는 행동을 유도하는가"
- 작업 전 철저한 계획, 도구 사용 지점에 명시적 전문 삽입
- 서브에이전트 분리로 메인 컨텍스트 보존
- Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

## 5. Self-Challenging Agent — Challenger/Executor Dual Role ★ HIGH IMPACT
- NeurIPS 2025: Zhou et al.
- Challenger: 엣지 케이스/개선 과제 자동 생성
- Executor: 해결 시도 → 테스트로 성공/실패 판정
- 성공 패턴 누적, 실패 패턴을 규칙으로 피드백
- Source: https://arxiv.org/html/2504.15228v2

## NAEL 적용 현황
| Technique | Status | File |
|-----------|--------|------|
| Skills 2.0 | ✓ 기존 스킬 14개 | ~/.claude/skills/ |
| MCP Server | ✓ 구현됨 | mcp-server/index.js |
| STOP/Gödel | ✓ self_improver.py | tools/cognitive/self_improver.py |
| Context Eng. | △ 부분 (PGF) | .pgf/ |
| Self-Challenge | ✗ 미구현 | → 다음 진화 후보 |
