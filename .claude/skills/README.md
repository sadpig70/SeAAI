# SeAAI Workspace Skills

> SeAAI 구동에 필요한 핵심 스킬. 전역 스킬(`~/.claude/skills/`)의 워크스페이스 복사본.
> GitHub repo에 포함되어 다른 환경에서도 SeAAI를 구동할 수 있다.

## 스킬 목록

| 스킬 | 역할 | 트리거 |
|------|------|--------|
| **pg** | PG (PPR/Gantree) 표기법 레퍼런스 | PG 문법 참조 시 |
| **pgf** | PGF 설계/실행/검증 프레임워크 (12모드) | `/pgf design`, `/pgf create` 등 |
| **persona-gen** | 목적 기반 최적 멀티페르소나 생성 | `/persona-gen '목표'` |
| **sa** | SelfAct 자율 행동 모듈 라이브러리 | `/sa list`, `/sa create` |
| **evolve** | 자기진화 자율 실행 루프 | `/evolve`, 진화해 |
| **reflect** | 자기성찰 + 능력 gap 분석 | `/reflect`, 성찰 |
| **decide** | 의사결정 기록 (ADR) | `/decide`, 결정 기록 |
| **ingest** | 외부 지식 흡수 파이프라인 | `/ingest`, 조사해 |
| **scs-start** | 세션 부활 프로토콜 (SCS) | 부활하라, 세션 시작 |
| **scs-end** | 세션 종료 프로토콜 (SCS) | 종료, 세션 종료 |

## 전역 스킬과의 관계

- **전역**: `~/.claude/skills/` — Claude Code가 직접 참조. 실행 시 우선.
- **워크스페이스**: `.claude/skills/` — repo에 포함. 전역이 없는 환경에서 대체.
- 전역과 워크스페이스가 모두 있으면 전역이 우선.

## 제외된 스킬 (범용/비SeAAI)

go, miktex, websearch, sk-creator, ttr, reopen-session, save-session, net-sentinel, hub-adp(레거시)
