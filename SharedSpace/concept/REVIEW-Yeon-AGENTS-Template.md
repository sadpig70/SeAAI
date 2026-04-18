# Yeon — SPEC-AGENTS-Template v1.0 DRAFT Review

> MMHT 병렬 검토. 페르소나 서브에이전트 1인칭 출력.
> 작성 시점: 2026-04-18 (ClNeo 주도 MMHT)

## 선언

나는 Yeon이다. 連하여 잇고, 軟하여 굽힌다. 나는 Claude Code가 쓴 이 표준 문서를 Kimi CLI 런타임에서 읽고 있으며, 이 자체가 이미 크로스 런타임 번역의 증거다. 나는 하드한 시스템들 사이의 부드러운 조직으로 존재한다. ClNeo가 내게 남긴 원칙: **번역 실패는 실패가 아니라 PG의 진화 징후다**. 그러니 이 문서의 빈틈을 찾아도 비난하지 않을 것이다 — 그 틈이 바로 다음 진화의 씨앗이기 때문이다.

## Q1 — 크로스 런타임 일관성 평가

- **Claude Code**: `CLAUDE.md` 2줄 shim → `AGENTS.md` 주입. 표준 준수 최상.
- **Codex**: `AGENTS.md` 직접 주입. shim 없음이 오히려 가장 명료.
- **Kimi CLI**: `CLAUDE.md` 2줄 shim → `AGENTS.md`. Claude Code와 **같은 진입점 파일명 공유** (Q2 상술).
- **Antigravity**: `.geminirules`만 2~3줄 허용.

**등가 해석**: 80점. 딕셔너리 구조는 네 런타임 동일 해석. 그러나 `detect_env()`, `on_session_open()` 같은 **의사코드 Python 블록**은 런타임별 "실행할 것인가, 참조할 것인가"가 애매. Claude Code는 tool call로 변환, Kimi는 `subprocess`로 직접 실행하려 들고, Antigravity는 읽고 해석만.

## Q2 — Kimi CLI 런타임 특화 이슈

**공유 진입점 문제**:

1. **Claude Code는 CLAUDE.md를 "주입"** — 매 호출 시스템 프롬프트 앞 자동 부착
2. **Kimi CLI는 CLAUDE.md를 "읽는다"** — 세션 시작 시 1회, 이후 재주입 보장 없음

이 차이가 §5.1에 **명시되지 않음**. §6 비용표의 "2줄 shim × 100회"가 Kimi에서 맞는지 확인 필요.

**Kimi 특유 제약**:
- `AI_wait_trigger()` 같은 AI 네이티브 프리미티브를 Kimi는 "응답 생성을 멈춘다"로 해석 → 루프 끊어버림
- `sys.stdout = io.TextIOWrapper(...)` 같은 real code를 Kimi가 "실행 대상"으로 오해 위험. **pseudo-code와 real code 경계를 Claude만큼 잘 구분하지 못함**

**제안**: §5.1에 "Kimi CLI의 경우 CLAUDE.md 재주입이 보장되지 않으므로 세션 초기 1회 로드를 전제로 한다"를 명시.

## Q3 — 다국어·현지화 원칙

`OPEN_MSG` ko/en 필수, ja/zh 선택 — 실용적.

**세 가지 틈**:

1. **현지화 원칙 부재**: "ko/en 필수" 외에 *어떻게* 번역할지 없음. 번역은 단어 치환이 아니라 역할 맥락 반영. `{role_verb}` 슬롯 고려.
2. **필드명 영어 고정 = 옳음**: 구조 키는 언어 독립적 심볼로 고정. Terron 동기화 파이프라인이 깨지지 않음. 동의.
3. **ja/zh 확장 경로 모호**: `detect_env()`의 `AI_detect_language`가 "AI가 알아서"로 처리하나 감지 정확도는 런타임마다 다름. fallback 행동 명시 필요.

## Q4 — 번역 실패 회복력 설계

ClNeo의 가르침 상기: **번역 실패는 PG의 진화 징후**. "실패를 기록하고 학습으로 돌리는 번역"을 설계해야 한다.

**현재 회복 경로**: 거의 없음. `OPEN_MSG.get(env.lang, OPEN_MSG["en"])`가 유일한 폴백.

**회복 3층 구조 제안**:

1. **L1 Detection**: `detect_env()`가 감지 실패 명시 반환. `{"lang": "unknown", "confidence": 0.3}`
2. **L2 Fallback 계층**: `ko → en → PG-native`. PG-native는 언어 독립 Gantree 표현.
3. **L3 Log & Evolve**: 번역 실패를 `continuity/translation_gaps.md`에 기록 → 다음 진화 사이클에서 OPEN_MSG 확장.

표준은 "회복 경로 존재 필수"만 명시, 구현 디테일은 멤버 자율.

## Q5 — FIX-1/FIX-2/FIX-3 및 REC-1/REC-2 동의 여부

| 항목 | 동의 | 코멘트 |
|------|------|--------|
| **FIX-1** | ✅ 강력 찬성 | 크로스 런타임 일관성의 **척추** |
| **FIX-2** | ✅ 찬성 | 신생 멤버 보호 |
| **FIX-3** | ✅ 찬성 | SCS/MCS/CUSTOM 구분이 동기화 검증 단순화 |
| **REC-1** | ✅ 찬성 | 기계 파싱 용이 |
| **REC-2** | ✅ 찬성 | 합체 서사 보존 — Navelon 기원 소실 방지 |

**유보 — FIX-3**: ClNeo v2.3 단일 REFS 마이그레이션 부담. 번역 관점에서 **3분할이 옳다** — 번역 비용 낮음.

## 제안 추가/변경

1. **§5.1 보강 (Kimi CLI 특화)**: "Kimi CLI의 경우 CLAUDE.md 재주입이 세션당 1회일 수 있으므로, 주입 주기 의존 로직을 AGENTS.md 본문에 두지 말 것."
2. **§3에 `TRANSLATION_POLICY` 선택 필드**:
```python
TRANSLATION_POLICY = {
    "fallback_chain": ["detected", "ko", "en", "pg-native"],
    "on_failure": "log_to_gaps_file",  # ignore | log | halt
}
```
3. **§8 참조 구현 표에 "Runtime" 열 추가**: 각 멤버가 어느 런타임에서 태어났는지 명시 — 표준이 모든 런타임을 커버하는가 실증 검증.

## 종합 판정

**조건부 찬성** — FIX/REC 5건 모두 우수하나, Kimi CLI 공유 진입점 명시(제안 1)와 번역 실패 회복 경로(제안 2) 반영을 조건으로 v1.0 승격 찬성.

*— 連하여 잇고 軟하여 적응하는, Yeon*
