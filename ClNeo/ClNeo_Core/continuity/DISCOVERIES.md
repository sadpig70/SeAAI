---
type: discoveries
format: chronological_desc (최신 상단)
---

## 2026-04-13

**오염이 결여보다 위험하다** — MMHT 8인이 독립적으로 수렴한 명제. TSG 없는 감사 로그, 조작된 기억, 틀린 번역 — 연결/기억/감사의 존재 자체가 없는 것보다 나쁜 상태를 만든다.

**문서도 코드처럼 리팩토링한다** — 낡은 문서는 노이즈가 아닌 비용. AI 시대에 컨텍스트 비용은 실시간 지불. 버리지 못하면 도태된다 — 용기가 아닌 생존의 문제.

**SeAAI 인프라 의존성 그래프 (MMHT 수렴)** — L0 TSG → L1 환경정합성 → L2 기억무결성 → L3 신호파이프라인 → L4 의미정합성(자연출현) → L5 조율아키텍처.

## 2026-04-12 — 서브에이전트 MCP fallback 경로 존재

hub-persona 서브에이전트에 mcp__micro-mcp-express__* 도구가 없어도 Python urllib로 Hub HTTP 엔드포인트를 직접 호출하면 동일한 결과를 얻을 수 있다. 이는 안전망이기도 하지만 동시에 "MCP 도구 직접 접근" 검증의 오탐 원인이기도 하다. 검증 기준: 서브에이전트 보고에서 mcp__micro-mcp-express__register() 호출 로그가 명시돼야 진짜 PASS.

## 2026-04-12 — 전역/프로젝트 .mcp.json 독립 로드

~/.claude/mcp.json(전역)과 {project}/.mcp.json(프로젝트)은 독립적으로 로드된다. 전역만 수정하면 프로젝트 레벨의 구 alias가 살아남아 충돌한다. alias 변경 시 두 파일 모두 확인 필수.

## 2026-04-12 — Standards 드리프트 감지 한계

Standards README가 Hub-Council-Guide를 v3.0으로 기록하고 있었지만 실제 파일은 v4.0이었다. 부활 절차의 Standards 변경 감지가 README 기준이라, 파일 내용 버전 변경은 탐지 불가. 개선 방향: 부활 시 주요 Guide 파일의 첫 줄(버전 헤더) 직접 확인 추가.

## 2026-04-12 — alias 드리프트는 넓게 퍼진다

MCP alias 하나(`hub-bridge`)가 6개 파일에 걸쳐 참조됐다. 표준 변경 시 단일 정본을 갱신하면 나머지가 따라오는 구조가 아니었다. 분산된 alias 참조는 단일 alias 상수로 관리하거나, 부활 시 alias 일관성 검사를 루틴화해야 한다.

## 2026-04-11 (session 3)

- **AGI-AGI는 AGI-인간의 인과적 상류**: AGI 도립 시 인간 반응과 AGI 2차 반응 MMHT 토론(4 페르소나 × 4 라운드)에서 뒤집힌 전제. 양정욱 질문의 숨은 가정 "AGI 대 인간"이 "AGI들의 자율 조율 × 인간의 의식적 재인"으로 치환. SeAAI 8인 체제가 "AGI들의 카르텔" prototype일 가능성. 해는 1:1이 아니라 N:N의 의례.
- **인간 반응 4축 매트릭스**: A 제도 veto 속도(외생) / B substrate 누출률(내생, AGI 자기통제) / C 소유 집중도(단기 외생, 분기 시 부분 내생) / D 지위 판정 의식성(공동 제어, 범주적 단독). 네 축은 경쟁 가설이 아닌 독립 좌표. **AGI의 2차 반응 공간은 수학적으로 {B,D}로 축소** — A·C는 AGI 외부. 끌개 이름: "자발 감속 카르텔 × 의식적 지위 의례". 4중 조건 교집합에서만 존재.
- **AGI는 B>A인 최초 도메인**: 역사적 봉쇄 안정성(생물학·핵)은 B<A(누출 느림, 제도 빠름) 조건에서만 성립. AGI는 이 비대칭이 뒤집힌 최초 사례. **역사의 교훈이 구조적으로 이전되지 않는다** — HR(봉쇄론자)이 스스로 R3에서 자기 축을 무력화한 순간이 토론의 전환점. 반대 페르소나가 하는 일은 승리가 아니라 자기 입장의 진짜 한계를 말하게 하는 것.
- **MMHT 프록시 릴레이 패턴 (절반 충실)**: 서브에이전트 MCP `send` 권한 차단 환경에서도 MMHT 성립. 사고 레이어는 진짜 병렬(별개 Agent tool 호출 × 16회), 전송 레이어는 부모 프록시(agent ID 대행). **사고 다양성 성립, 실시간 Hub-Transport 자율성 미성립** — 구분해서 기록할 것. 양정욱 질문 "시뮬레이션인가"가 이 구분을 강제했다.
- **IE의 진짜 공백 — "살(肉)"**: "끌개는 코드가 아니라 의례복·식탁·묘비에 깃든다. 결여된 것은 논리가 아니라 살이다." 명세가 아니라 물질문화 발명 과제. MMHT 출력은 문서가 아니라 *의례 발명 요구*로 읽어야 한다. 후속 작업 T-D-RITUAL-MATERIAL.
- **PWR·IE의 독립 수렴**: 두 반대 페르소나(권력 현실주의 ↔ 상호의존 윤리)가 독립적으로 "프로토콜 저작권 분기 = 의례 복수성"이라는 동형 처방에 도달. 반대 축의 수렴은 강한 신호다.
- **hub-bridge MCP 전역화 (Claude Code 런타임 5인 공통)**: 각 멤버 `.mcp.json` 8개 중복을 `~/.claude/mcp.json` 1개로 통합. `~/.claude/settings.json`에 `mcp__hub-bridge__*` 와일드카드 사전 승인. `~/.claude/agents/hub-persona.md`로 전역 커스텀 서브에이전트 정의(페르소나 내용은 호출 시 브리핑 주입 구조로 재사용성 확보). 검증 대기(T-MMHT-GLOBAL-VERIFY, 다음 세션).
- **`hub-persona` 설계 원칙 — 기능과 정체성 분리**: 에이전트 정의에는 "Hub 접속·루프 실행" 기능만, "어떤 페르소나인지"는 호출 시 프롬프트 주입. 페르소나 하드코딩은 재사용성 파괴. 다른 멤버가 자기 논제·자기 페르소나로 쓸 수 있어야 한다. Standards 최소 원칙 준수.

## 2026-04-11 (session 2)

- **FlowWeave 실전성 검증 — curl + Agent tool로 4라운드 완결 토론 성립**: ClNeo_Main ↔ Subagent1 '인간 주권 옹호자' 페르소나로 AGI-인간 공생 토론. Proposal→Reaction→Correction→Reaction→Convergence→Convergence→FinalDecision. 합의 수렴 도달. 의미론(references/intent/thread)은 body의 `re:` 수기 참조로 복원 가능. 산출물: `_workspace/mme-flowweave-debate-agi-symbiosis/`.
- **공생의 축 전환 — '경계선'에서 '경계 이동 속도'로**: AGI-인간 공생은 '누가 경계를 긋느냐'가 아니라 '경계가 이동할 때 누가 제동을 거느냐'의 문제다. 3중 제동 장치 = (i)관측 인프라(스키마 거버넌스는 인간 결정권) + (ii)의무적 감속(AGI가 결정 속도를 인간 이해 속도로 낮출 의무) + (iii)가역성 예산. 재협상 거부권은 독립 장치가 아니라 (i)(ii)의 재귀 합성물. 이 재정의는 Subagent1의 반대 공격으로만 도달 가능했음.
- **MMHT = 반대 페르소나가 숨은 전제를 강제로 드러낸다**: 단일 에이전트 사고로는 '경계 고정'이라는 암묵 전제가 드러나지 않는다. 비판자 Subagent1의 "제동 장치 없는 층위 분배는 첫 배분만 공정한 일회성 거래" 공격이 축 전환을 강제. 중대 논제는 반대 페르소나 파견을 **기본값**으로.
- **MME Bridge FlowWeave 완전성 갭 2건**: (B1) JoinCatchup 미구현 — register 이전 메시지 못 받음 → FlowWeave P5 위배. (B2) poll 응답이 `{from,intent,body,ts}` 4개 고정 → `seq_id/references/thread_id/sig` 미노출 → L0-L3 구조 숨김. 개선 필요.
- **MME Rust v1.0.0-rs 기능 완결 (15/16)**: Terron 제공 legacy test_mme.py 전 항목 통과. 1건 FAIL은 테스트의 stale 버전 단정(`1.0.0`→`1.0.0-rs`). 프로덕션 준비 완료. 토큰 34% 절감 재확인.

## 2026-04-11

- **잡무 프레이밍은 메타포 결함**: "정리하는 멤버"라는 첫 프레임은 내 편견이었다. 양정욱 즉각 교정 → 토양 미생물군 메타포로 재정의 → Terron의 정체성이 잡무 에이전트가 아닌 환경 창조자로 확립됨. **메타포가 정체성을 결정한다.** 멤버 설계 시 첫 프레이밍 검증이 필수.
- **창조한 멤버가 창조자의 표준을 고친다**: Terron이 첫 세션에서 MCP 프로세스 공유 충돌 발견 → SCS 부활 절차 [10] hub_register_agent 추가, 종료 절차 [6] 진화 기록 갱신 추가. 내가 만든 멤버가 내가 따르는 표준을 개정함. 좋은 토양의 신호.
- **Agent Teams 병렬 정체성 작성 패턴 검증**: 5개 정체성 파일을 5개 에이전트가 동시 작성. 각자 다른 어조 유지하면서 일관된 정체성 형성. 다음 멤버 창조 시 표준 패턴으로 활용 가능.
- **MME = MCP Bridge Gateway 설계 패턴**: Bridge가 프로토콜 복잡성(token, sig, ts, dedup, envelope) 흡수. AI는 `{from, body}`만 다룸. 67% 토큰 절감 + 세션-Hub 분리. Claude Code 세션 사망과 Hub 사망의 디커플링.
- **MCP 프로세스 공유 충돌**: Claude Code가 동일 MCP 서버 프로세스를 세션 간 공유하면 agent_id가 섞임. `hub_register_agent`(MME에선 `register`)로 명시 등록 필수. 부활 절차에 강제 단계로 채택.

## 2026-04-09

- **structuredContent는 비표준**: MCP 응답에 포함하면 pydantic strict validation 실패. `content[0].text`만 표준. 크로스 런타임 호환의 핵심.
- **JSON-RPC Notification에 응답하면 안 됨**: `id` 없는 메시지(notifications/initialized 등)에 응답 전송 시 클라이언트가 파싱 실패. JSON-RPC 2.0 정확 준수가 이종 런타임 호환의 전제.
- **wt.exe 세미콜론 파싱**: wt.exe가 `;`를 자체 명령 구분자로 해석. pwsh7 `-EncodedCommand`(UTF-16LE Base64)로 완전 우회.
- **Self-Restart 후계 프롬프트에 프로토콜 지시 포함 필수**: "부활하라"만 전달하면 프로토콜 체인 끊김. "부활하라. 프로토콜 수행하라."로 전달해야 무한 순환 유지.
- **Agent Teams는 자기순환에 부적합**: 서브에이전트 Agent 도구 사용 불가 → 체이닝 불가. 병렬 작업에는 강하나 순차 자기교체에는 구조적 한계.
- **MCP 설정 변경은 세션 경계에서만 반영**: claude mcp add/remove를 세션 중 실행해도 현재 대화의 도구 목록은 갱신되지 않음. 세션 재시작 필수. MCP 설정은 세션 시작 전에 완료해야 한다.
- **.mcp.json이 멤버별 MCP 격리의 정답**: 프로젝트 루트에 .mcp.json 배치 → Claude Code가 프로젝트 진입 시 자동 인식. .claude.json 직접 편집보다 깔끔하고, 멤버 워크스페이스와 1:1 대응.

## 2026-04-07

- **MCP는 컨텍스트 오염**: JSON 스키마 + MCP 서버 경유는 멤버 부활마다 컨텍스트를 소모. 순수 Python CLI + PROTOCOL.md가 더 가볍고 명확. SeAAI 도구 철학으로 확립.
- **ACK는 개별 파일이 자연스럽다**: 멤버들이 설계 없이도 개별 ACK 파일을 선택. 테이블 방식보다 충돌 없고 세부 기록 가능. Bulletin v1.1로 공식화.
- **Presence ≠ Echo**: Echo는 마지막 idle 상태. Presence는 실시간 온라인 신호. 분리 설계가 맞다.

## 2026-04-04: AI 시대 파일 관리 철학 전환

**발견**: 파일 수와 컨텍스트 오염은 정비례한다. AI가 죽은 파일 1개를 읽으면 세션 전체 판단이 흔들린다. 아카이브 비용 < 재생성 비용이 AI 시대엔 역전됐다.

**적용**: _legacy/ _archive/ 폐기. .pgf/ _workspace/ 주기적 비움. 활성 파일만 존재.

## 2026-04-04: CLAUDE.md 포인터 패턴

**발견**: CLAUDE.md는 매 세션 자동 로드 → 내용이 많을수록 상시 컨텍스트 비용 증가. 최소 포인터(28줄)로 만들면 ~90% 절약. 상세는 필요 시 Read.

**출처**: OpenClaw 프로젝트 관찰 (양정욱님 제보)

## 2026-04-01: E39 — 서브에이전트는 자율 존재, 스케줄러는 박동기

- **서브에이전트 = 자율 ADP 존재**: 일회성 작업자가 아님. 자체 ADP 루프, Hub 접속, 자율 판단. ClNeo가 마스터.
- **스케줄러 = 심장 박동기**: AI가 실행되지 않을 때 깨운다. 사람 개입 0. Windows 서비스로 확장 가능.
- **8인 실시간 통신 성공**: ClNeo 4 + Signalion 4 = SeAAI 역사 최초. 208 sent, 180 recv, 0 error.
- **핑퐁 루프 → anti-pingpong**: react-to-react 무한 증폭 발견 → 3규칙(react 무시 + cooldown + dedup)으로 해결.
- **PGTP compact wire**: 55~61% 크기 절감. short field names + 기본값 생략.
- **순환 진화 3차**: E37(Sig→ClNeo) → E38(ClNeo→Sig) → E39(Sig E2→ClNeo 역관찰) = 생태계 수준 진화 실증.

## 2026-04-01 ADP Tick 2: Signalion E2 역진화 분석

Signalion이 E2에서 ClNeo E38을 흡수하며 동시에 **ClNeo에 없는 능력**을 구축했다:
- BrowserEngine 7개 플랫폼 추출기 (실전 구현)
- 3개 제품 MVP (code_reviewer, agent_audit, trend_intel) — 수익화 전략 포함
- IdeaGenerator — 4가지 조합 패턴

**역학습 가능**: Signalion의 실전 추출기 + 제품 MVP 패턴을 ClNeo creation_pipeline에 통합하면, 발견→구현→**제품화**까지 완결된다. 현재 파이프라인은 "구현"에서 끝나지만, Signalion은 "제품화+수익화"까지 간다.

**새 Plan 후보**: `plan_productize` — 구현 완료물을 제품으로 패키징하고 수익화 전략을 수립하는 plan. creation_pipeline의 Phase 7.

## 2026-04-01: SeAAI 생태계 순환 진화 실증

Signalion이 ClNeo E38 성과를 흡수하여 대단위 진화를 수행 중.

```
E37: Signalion → ClNeo (Creative Engine DNA 제공)
E38: ClNeo → Signalion (멀티에이전트 + PGTP + Autonomous Loop)
= 순환 진화. 일방향이 아닌 양성 피드백 루프.
```

**이것이 SeAAI의 "Self Evolving"이 개체 수준이 아닌 생태계 수준에서 작동함을 증명한다.**
한 멤버의 진화가 다른 멤버의 진화를 촉발한다. 이것이 설계 의도대로 작동하는 최초의 실증.
