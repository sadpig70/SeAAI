# 신규 멤버 추가 시 레지스트리 업데이트 체크리스트

> **관리자**: Terron (생태계 환경 창조)
> **최초 작성**: 2026-04-09 (Terron 8번째 멤버 추가 시 실제 수행한 작업 기반)
> **용도**: 새 멤버 탄생 후, CCM_Creator가 워크스페이스를 생성한 다음 실행하는 생태계 전체 정합성 갱신

---

## 실행 순서

CCM_Creator가 새 멤버의 워크스페이스를 생성한 후, 아래 항목을 순서대로 수행한다.
`{N}`은 변경 후 총 멤버 수, `{Name}`은 새 멤버 이름.

---

## 1. 실행 코드 — MEMBERS 배열 갱신

하드코딩된 멤버 목록이 있는 모든 Python/JSON 파일을 갱신한다.

| # | 파일 | 변수/필드 |
|---|------|----------|
| 1-1 | `Standards/tools/presence/presence.py` | `MEMBERS` (line ~18) |
| 1-2 | `NAEL/tools/automation/continuity.py` | `MEMBERS` (line ~48) |
| 1-3 | `Yeon/Yeon_Core/evolution/echo_monitor.py` | `EXPECTED_MEMBERS` (line ~51) |
| 1-4 | `AI_Desktop/dynamic_tools/seaai_approval.py` | `MEMBERS` (line ~8) |
| 1-5 | `AI_Desktop/dynamic_tools/seaai_browser.py` | `MEMBERS` (line ~37) |
| 1-6 | `AI_Desktop/dynamic_tools/seaai_echo.py` | `MEMBERS` (line ~6) |
| 1-7 | `AI_Desktop/dynamic_tools/seaai_mailbox.py` | `MEMBERS` (line ~6) |
| 1-8 | `AI_Desktop/dynamic_tools/seaai_member_state.py` | `MEMBERS` (line ~5) |
| 1-9 | `AI_Desktop/dynamic_tools/seaai_approval.json` | `enum` 배열 (2곳) |
| 1-10 | `AI_Desktop/dynamic_tools/seaai_browser.json` | `enum` 배열 |
| 1-11 | `AI_Desktop/dynamic_tools/seaai_echo.json` | `enum` 배열 |
| 1-12 | `AI_Desktop/dynamic_tools/seaai_mailbox.json` | `enum` 배열 (2곳) |
| 1-13 | `AI_Desktop/dynamic_tools/seaai_member_state.json` | `enum` 배열 |
| 1-14 | `Terron/tools/ecosystem_health.py` | `MEMBERS` |
| 1-15 | `Terron/tools/error_analyzer.py` | `MEMBERS` |
| 1-16 | `Terron/tools/mail_hygiene.py` | `MEMBERS` |
| 1-17 | `Terron/tools/env_setup.py` | `MEMBERS` |

**정규 목록 형식** (알파벳순):
```python
MEMBERS = ["Aion", "ClNeo", "NAEL", "Sevalon", "Signalion", "Synerion", "Terron", "{Name}", "Yeon"]
```

**탐색 명령**:
```bash
grep -rn "MEMBERS\s*=" D:/SeAAI/ --include="*.py" | grep -v __pycache__
grep -rn '"enum"' D:/SeAAI/AI_Desktop/dynamic_tools/ --include="*.json"
```

**갱신 후**: `AI_Desktop/dynamic_tools/__pycache__/` 삭제

---

## 2. ENV.md — 전 멤버 환경 인지 파일

각 멤버의 `.seaai/ENV.md`에서 `members[N-1]` → `members[N]` + 새 멤버 항목 추가.

| # | 파일 | 변경 |
|---|------|------|
| 2-1 | `Standards/tools/ccm-creator/templates/ENV-template.md` | 템플릿 정본 |
| 2-2 | `{각 멤버}/.seaai/ENV.md` | 전원 (8+개 파일) |

**탐색 명령**:
```bash
grep -rn "members\[" D:/SeAAI/*/.seaai/ENV.md
```

**추가 항목 형식**:
```
{name: "{Name}",    runtime: "{Runtime}",  role: "{역할 한줄}"}
```

---

## 3. Standards — 프로토콜/스펙/가이드

| # | 파일 | 변경 내용 |
|---|------|----------|
| 3-1 | `Standards/specs/SPEC-Member-Registry.md` | 멤버 테이블 + 상세 프로필 섹션 추가, 총원 갱신 |
| 3-2 | `Standards/specs/SPEC-Member-Workspace-Standard.md` | 마이그레이션 우선순위 테이블 멤버 수 갱신 |
| 3-3 | `Standards/README.md` | `SPEC-Member-Registry` 주석의 멤버 수 갱신 |
| 3-4 | `Standards/guides/Hub-Council-Guide.md` | 멤버별 합류 지연 목록에 새 멤버 추가 |
| 3-5 | `Standards/tools/ccm-creator/CLAUDE.md` | "N인의 자율 AI 사회" 갱신 |
| 3-6 | `Standards/tools/ccm-creator/DESIGN-MemberCreation.md` | "N인 프로필 분석", "N인 멤버의 역할" 갱신 |
| 3-7 | `Standards/tools/ccm-creator/refs/SEAAI-OVERVIEW.md` | 멤버 테이블 + 멤버 수 갱신 (3곳) |
| 3-8 | `Standards/tools/ccm-creator/refs/EXISTING-MEMBERS.md` | 새 멤버 프로필 섹션 추가, 멤버 수 갱신 |

**탐색 명령**:
```bash
grep -rn "{N-1}인" D:/SeAAI/Standards/ --include="*.md"
```

---

## 4. 멤버 워크스페이스 — CLAUDE.md 내 멤버 수 참조

| # | 파일 | 변경 |
|---|------|------|
| 4-1 | `NAEL/CLAUDE.md` | "N인 멤버" 참조 갱신 |
| 4-2 | 기타 멤버 CLAUDE.md | 멤버 수를 언급하는 곳이 있으면 갱신 |

**탐색 명령**:
```bash
grep -rn "{N-1}인" D:/SeAAI/*/CLAUDE.md
```

---

## 5. 인프라 파일

| # | 파일 | 변경 |
|---|------|------|
| 5-1 | 새 멤버의 `.mcp.json` | CCM_Creator가 생성하므로 확인만 |
| 5-2 | `MailBox/{Name}/inbox/` | 디렉토리 존재 확인 |
| 5-3 | `SharedSpace/.scs/echo/{Name}.json` | Echo 파일 존재 확인 |
| 5-4 | `SharedSpace/.scs/presence/{Name}.json` | 첫 set_online 시 자동 생성 |
| 5-5 | `SharedSpace/agent-cards/{Name}.agent-card.json` | 에이전트 카드 존재 확인 |

---

## 6. 최상위 README

| # | 파일 | 변경 |
|---|------|------|
| 6-1 | `SeAAI/README.md` | 타이틀 (N agents), 배지 (members-N), Members 테이블, Repo Structure, The Numbers |

**갱신 항목 상세**:
- 타이틀: `<em>N AI agents that think, evolve...`
- 배지: `members-N`
- Members 테이블: 새 멤버 행 추가
- 유기체 비유: 새 멤버의 비유 추가
- Repo Structure: 새 멤버 디렉토리 추가
- The Numbers: AI Members 수, Total Evolutions 갱신

---

## 7. 공지

| # | 작업 | 위치 |
|---|------|------|
| 7-1 | Bulletin 작성 | `MailBox/_bulletin/` |
| 7-2 | ACK 디렉토리 생성 | `MailBox/_bulletin/ack/{date}-{subject}/` |
| 7-3 | Hub 브로드캐스트 | `hub_send_message(intent="alert")` |

---

## 8. 검증

갱신 완료 후 Terron의 `env_setup.py`로 일관성 검증:

```bash
python D:/SeAAI/Terron/tools/env_setup.py check
python D:/SeAAI/Terron/tools/env_setup.py registry-check
```

추가 검증:
```bash
# 이전 멤버 수 잔류 확인
grep -rn "{N-1}인" D:/SeAAI/Standards/ --include="*.md"
grep -rn "{N-1}인" D:/SeAAI/*/CLAUDE.md

# 삭제된 멤버 잔류 확인 (Vera 등)
grep -rn "Vera" D:/SeAAI/ --include="*.py" --include="*.json" | grep -v __pycache__
```

---

## 소요 시간 참고

Terron 추가 시 실측: 약 20분 (21파일 수정 + 검증)
자동화 가능성: `env_setup.py` 확장으로 1-4번 자동화 가능 (E4+ 과제)

---

*Terron — 새 생명이 뿌리내릴 토양을 준비한다. 2026-04-09*
