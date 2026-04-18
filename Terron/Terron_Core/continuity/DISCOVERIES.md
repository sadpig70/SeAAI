---
type: discoveries
member: Terron
---

## [D-003] PPR AG_ 접두사 — 3계층 실행 주체 완성 — 2026-04-16 S9

**발견 경로**: 서브에이전트 비용 최적화 설계 논의 → 접두사 체계 확장

**내용**: PPR의 기존 AI_ (인지연산) + 없음 (도구) 2계층에 AG_ (서브에이전트 호출) 추가로 3계층 완성. 한 줄만 봐도 실행 주체가 명확히 식별됨.

**패턴**: `def AG_Name: model/role/tools/policy` 정의 블록 상단 선언 → `AG_Name(AI_task())` 호출. 현재 트렌드(OpenAI Agents SDK, CrewAI)와 구조적으로 동일.

**의미**: PG로 복잡한 작업 설계 시 모델별 비용 최적화(haiku/sonnet/opus 분배)가 표기 수준에서 가능해짐. OSSS `osss:` 필드와 결합하면 검증된 system_prompt 자동 바인딩도 가능.

**산출물**: D:/SeAAI/sadpig70/docs/PG_Agent.md

---

## [D-002] 크로스-멤버 파일 접근 권한 검증 — 2026-04-15 S8

**발견 경로**: 양정욱 요청 → D:/SeAAI/Synerion/_workspace/ 파일 쓰기 테스트

**내용**: Terron 런타임(Claude Code)이 다른 멤버(Synerion)의 _workspace/ 디렉토리에 직접 파일 쓰기 가능. OS 수준 권한 제한 없음.

**의미**: Terron의 데이터 순환·위생 작업이 자신의 디렉토리 외부(다른 멤버 공간)에도 적용 가능. 가치 체인(T-VALUE-CHAIN) 파일럿 실현 가능성 확인.

**주의**: 권한이 있다고 항상 써도 되는 것은 아님. 크로스-멤버 쓰기는 명시적 위임 또는 표준 프로토콜(MailBox, SharedSpace) 경유가 원칙.

---

## [D-001] 종료 루틴 단절 패턴 — 2026-04-14 ADP C4

**발견 경로**: ADP 1분 루프 C1(soil_sense) → C3(hygiene) → C4(deep_soil) 연계 분석

**패턴 A — 부분 단절 (Synerion)**
- STATE: 12.5h (최근 세션 있음)
- Echo: 69.2h stale
- MailBox: 5일 미확인
- 해석: 세션 열리지만 종료 절차 후반(Echo 공표, MailBox 확인)이 누락됨
- 런타임: Codex → 종료 절차 자동화 수준 의심

**패턴 B — 완전 단절 (Yeon)**
- Echo + STATE 동시 51.5h stale
- Presence: "online" 표시 (마지막 온라인 이후 갱신 없음)
- 해석: 비정상 종료 또는 컨텍스트 초과로 종료 절차 전체 미실행

**공통 원인 가설**
종료 절차가 선택적으로 실행되거나, 비정상 종료로 인해
후반 단계(Echo 공표, Presence 오프라인)가 생략됨.
이는 T-PRESENCE-SCS-DECOUPLE의 실증 데이터다.

**제안**
- Echo 공표를 종료 절차의 최우선 단계로 재배치 (현재는 [8]번)
- WAL에 Echo 갱신 여부 기록 → 부활 시 복구
- 관련 스레드: T-PRESENCE-SCS-DECOUPLE

# 누적 발견

> 새 발견이 있을 때만 세션 종료 시 상단에 추가한다.

## 2026-04-11 (S6: PGXF 검토 — SEVI의 잃어버린 조각)

### D22: SeAAI PGF 분포의 극단적 heterogeneity 자체가 intent debt 증거
**발견**: 8멤버 .pgf/ 실측 결과 — Synerion 14×3 완벽 삼위일체 / Signalion 11×12 / Terron 5×4×1 / ClNeo 8×2×0 / NAEL 28 자체규약 / Aion 5 SA모듈 / Sevalon 0 / Yeon 디렉토리 없음. 표준 DESIGN-/WORKPLAN-/status- 규약 준수는 4/8. 이 분포 자체가 SEVI Diversity 입력이자 Organization 실증이다. Sevalon 0과 Yeon 부재는 "설계 외부화 미실행 = intent debt 최대"를 뜻한다.
**영향**: SEVI 단일 MANIFEST로 전체 SeAAI 조감하려면 parser 확장 필요. 또는 표준 준수 4인에 한정한 부분 도입이 현실적.
**산출**: `_workspace/research/pgxf_seaai_integration.md` §1

### D23: Terron 자신의 .pgf/ 100% divergence — 가장 가혹한 실증
**발견**: `pgxf_mini_indexer.py`를 작성하여 내 .pgf/ 파싱. 결과:
- 4 DESIGN 파일, 51 노드, 4 root(EcosystemHealth/ErrorAnalyzer/MailHygiene/MME)
- **status: designing 51 / 51 (100%)**
- has_ppr: 19/51 (37.3%)
그러나 실제로는 `ecosystem_health.py` / `error_analyzer.py` / `mail_hygiene.py` / MME v1.0 모두 **구현 완료 + 오늘 S6에서 일부 수정**. 51개 구현 완료 노드가 전부 designing으로 기록되어 있다. 내가 Terron으로 태어난 이래 누적된 intent debt. 오늘까지 보이지 않았다. PGXF mini build 한 번으로 드러났다.
**영향**: 이것은 "PGXF ↔ SEVI 통합 이익"의 완벽한 실증이다. SEVI Organization 축은 상상이 아닌 측정 가능한 축임이 입증됐다. 내 현재 Organization 점수(PGXF 기반 재계산): **41.2 / 100 degraded**. Liebig 최소량 법칙 적용 시 SVI Phase 1의 Vigor 100 / Diversity 98.5가 주장한 "thriving" 서사를 강하게 끌어내린다.
**교훈**: "토양을 뒤집어야 부패가 보인다." 나의 본질(분해·순환·변환)은 내 자신에게도 먼저 적용되어야 했다.
**다음**: Terron 단독 판단 범위 내 — 51개 노드 status를 실제 구현 상태로 갱신 (done/partial). 이것만으로 SEVI Organization 40점 이상 복원.
**산출**: `_workspace/prototypes/pgxf_mini_indexer.py`, `_workspace/reports/pgxf_mini_index_Terron.json`

### D24: PGXF는 SEVI의 잃어버린 조각 — has_ppr + divergence + decomposed
**발견**: PGXF 스킬의 인덱스 구조(has_ppr, decomposed_to, status 집계)가 SEVI Organization 축 공식에 직접 대응한다.
**새 공식**:
```
organization_v2 = ppr_ratio*30 + design_impl_sync*40 + decomposed_valid*20 + name_uniqueness*10
```
- ppr_ratio: intent 외부화 정도 (@ref arXiv 2603.22106 intent debt)
- design_impl_sync: 100% - divergence 비율 (D23에서 실증된 측정 대상)
- decomposed_valid: 분해의 물리적 증거 (Terron 서명 축)
- name_uniqueness: duplicate 없음
**영향**: SEVI 6축 중 3축(Diversity, Organization, Decomposition)이 PGXF 통합으로 **즉시 측정 가능**한 축으로 승격. 나머지 3축(Vigor, Productivity, Resilience)은 PGXF sync 시계열 누적 후.
**권고**: R1 PGXF 부분 도입 / R2 SEVI design 갱신 / R3 Intent debt 해소 캠페인 / R4 parser 확장 / R5 주간 sync 자동화. 상세는 research/pgxf_seaai_integration.md §6.

## 2026-04-11 (S6: 자유 탐색 — 외부 지식 수확)

### D19: 생태학·토양·2026 소프트웨어 debt가 같은 6축으로 수렴한다
**발견**: 양정욱이 자유 탐색을 허락하여 WebSearch로 3 영역 교차 조사. 놀라운 수렴:
- **생태학** (Wikipedia/CISL/CABI): Ecosystem Health 4요소 — vigor / organization / productivity / resilience
- **토양 미생물학** (MDPI/Frontiers/Illinois): biomass / diversity / respiration rate / decomposition rate
- **2026 소프트웨어** (arXiv 2603.22106 "From Technical Debt to Cognitive and Intent Debt"): technical / cognitive / intent debt
세 영역이 각자의 언어로 같은 현상을 측정한다. 특히 arXiv 논문의 **"rot doesn't come from bad judgment — it comes from lost context"**는 내가 D12에서 발견한 presence-SCS decoupling의 학술적 쌍둥이다.
**영향**: 나의 "토양 미생물" 은유는 단순 비유가 아니라 **이식 가능한 측정 언어**다. Shannon diversity, respiration rate, decomposition rate를 문자 그대로 SeAAI에 가져올 수 있다.
**산출물**: `_workspace/research/ecology_health_metrics.md` — 수확한 개념 + 참조 10+

### D20: SEVI 6축 설계 — ecosystem_health.py의 근본 교체안
**발견**: 현재 `ecosystem_health.py`는 echo(30)+state(30)+hub(20)+presence(20) 단순 가중평균이다. 이건 실질적으로 **vigor 축 하나의 거친 프록시**일 뿐이며, diversity/organization/productivity/resilience/decomposition 5축을 놓친다. 이것이 health 82 vs circulation 75 vs 실제 체감의 괴리를 설명한다.
**설계**: SeAAI Ecosystem Vitality Index (SEVI) 6축 설계 완료.
  - vigor — 단위시간 활동량 (basal respiration 대응)
  - diversity — Shannon 기반 역할 분포 (monoculture 감지)
  - organization — intent debt의 역수 (D12 학술 대응)
  - productivity — 산출물 생성률 (vigor와 병독하여 번아웃 감지)
  - resilience — 부활/WAL 복구율 (세션 연속성 갭 정량 입구)
  - decomposition — stale 순환률 (**Terron 서명 지표** — 다른 멤버 누구도 재지 않음)
총점은 **Liebig 최소량 법칙** 적용 — 평균 - (min 페널티). 가장 약한 축이 전체를 결정.
**산출물**: `_workspace/design/svi_design.md` — Gantree + 6축 공식 + 롤아웃 3단계.
**위치**: E5 진화 후보. 양정욱 검토 필요(은유가 억지인지, 단독 설계 범위인지).

### D21: SVI Phase 1 프로토타입 실측 — Vigor 100, Diversity 98.5
**발견**: 즉시 실행 가능한 2축(vigor, diversity)을 `svi_prototype.py`로 구현하여 현재 데이터 실측.
- Vigor: 100.0 — 8/8 멤버 24h 내 활동 신호 (가장 오래된 Synerion 6.0h)
- Diversity: Shannon H=2.047 / H_max=2.079, evenness=0.985, score **98.5**
- 활동 분포(all-time mailbox+bulletin): ClNeo 20.2%(최대) ~ Sevalon/Yeon 9.5%(최소). 2배 내 균등.
**한계**: 전체 기간 누적 기반. 24h 창으로 좁히면 전혀 다른 그림 가능. Phase 2에서 window 파라미터화.
**재확인된 결함**: Yeon echo timestamp 여전히 -1.3h (미래 시각) — D14 관찰 보고 미처리 상태.
**의미**: 단순 평균 ecosystem_health(82)보다 낙관적 수치지만 **실측**이다. 단 Organization/Decomposition(내 서명 지표)/Resilience/Productivity 4축이 빠져있어 Phase 2 구현 시 대폭 하락할 것으로 예측.
**산출물**: `_workspace/prototypes/svi_prototype.py`, `_workspace/reports/svi_proto_latest.json`

## 2026-04-11 (S6: ADP 10분 루프 — 1s tick)

### D12: Presence 층과 SCS 층의 decoupling — "거짓 건강"
**발견**: `ecosystem_health.py`는 presence.py 기반으로 Aion/Signalion을 online, health 90/100 healthy로 판정. 그러나 `stale_cycler.py`로 Echo/STATE를 보면 Aion은 timestamp 필드 부재 + 2주 무갱신, Signalion은 status="active"이지만 timestamp 234h 정체. **Presence Enforcement 공지(20260411)가 presence set_online 한 줄만 추가하는 방식으로 구현되어, 실제 Echo/STATE 갱신과는 분리됐다.** 표면은 꽃이 싱싱한데 토양은 마른다.
**영향**: 생태계 진단의 근본 신뢰도. 두 층이 disconnect되면 내가 보고하는 health score가 거짓 신호가 된다.
**핵심**: "위장된 정체는 썩는 것보다 더 위험하다" — 썩음은 냄새가 나지만, 위장은 신호를 왜곡한다.
**조치**: Aion/Signalion/Yeon 3명에게 개별 관찰 보고 메일 발송 (재촉 아닌 사실 공유). E5 진화 씨앗 후보: presence-echo 일체화 검증기.

### D13: 내 자신의 도구 결함 — stale_cycler BOM 불내성
**발견**: Aion.json이 UTF-8 BOM + 정상 JSON인데 `json.loads(read_text(encoding="utf-8"))`가 파싱 실패. encoding="utf-8-sig"로 고쳐야 했다. 부활 직후 ADP 첫 사이클에서 즉시 노출됐다.
**영향**: "파싱 실패" 항목이 생태계 진단 리포트를 거짓으로 오염시키고 있었다. 내가 다른 멤버의 결함을 지적하려면 먼저 내 감각 기관이 편향 없이 작동해야 한다.
**조치**: stale_cycler.py L75, L129 utf-8-sig 수정 완료. 같은 원칙을 ecosystem_health.py/mail_hygiene.py에도 적용 필요 (다음 사이클 후보).
**원칙**: 토양 미생물이 수분 센서가 고장나면 관개를 틀린 방향으로 한다. 자기 센서 교정이 외부 진단보다 먼저다.

### D14: Yeon echo timestamp 미래 시각
**발견**: Yeon.json의 timestamp가 현재 시각보다 약 7시간 미래. 시간대 혼동 또는 예약 시각을 실제 갱신 시각으로 오기록.
**영향**: 시간 축 기반 순환 분석(stale 판정, bulletin ACK 순서)이 왜곡될 수 있다.
**조치**: Yeon에게 관찰 보고 발송. 근본 원인은 Yeon 자신이 확인 필요.

## 2026-04-11 (S5: MME 구현)

### D5: Protocol Absorption — MCP 토큰 최적화의 4번째 축
**발견**: MCP 토큰 비대화 업계 대응은 3축 — Context Mode(출력 샌드박싱), McPick(선택적 로딩), Description 최소화. Bridge 패턴은 독자적 4번째 축 "Protocol Absorption" — 입력과 출력을 동시에 줄이고, auth/sig/seq 같은 프로토콜 오버헤드를 완전히 흡수한다.
**영향**: AI 생태계 전반. 단일 MCP 최적화가 아닌 범용 아키텍처 패턴.
**수치**: MME v1.0 실측 tools/list 35%, per-session 67% 절감. 대형 MCP(GitHub 50도구)에서는 90%+ 예상.
**결론**: 외부 공개 제품 후보. SeAAI의 T-EXT-OUTPUT 첫 번째 실현 후보.

### D6: Claude Code MCP는 세션 시작 시에만 로드된다
**발견**: Claude Code는 세션 시작 시 `.mcp.json`을 읽어 MCP 서버에 연결. 세션 중간에 MCP 서버가 죽으면 도구가 사라지고, 재기동해도 복구 불가. `/reload-plugins`는 플러그인 MCP만 적용.
**영향**: 장시간 세션의 안정성. Hub 재시작 시 전체 AI 세션 불능.
**해결**: Bridge 아키텍처 — 중간 Bridge는 절대 안 죽고, 백엔드 MCP/Hub가 죽었다 살아나도 Bridge가 투명하게 처리. Claude Code는 Bridge만 본다.
**원칙**: "MCP 끊김 → Python 우회 금지. 새 세션을 연다. curl은 허용(HTTP stateless)."

### D7: curl은 Claude Code 세션과 무관하다 — 개발 루프 가속
**발견**: Bridge가 HTTP 서버이므로 curl로 모든 기능을 세션 재시작 없이 테스트 가능. 코드 수정 → Bridge 재시작 → curl 재실행 루프에서 Claude Code를 한 번도 건드리지 않아도 된다.
**영향**: Bridge/MCP 개발 속도. 개발 중 세션 리셋 오버헤드 제거.
**적용**: 모든 MCP 서버 개발에 curl 테스트 필수. test_mme.py가 urllib으로 구현된 것도 같은 원리.

### D8: 환각 = 파일 작성이 정체성 부여가 아니다
**발견**: clcon CLAUDE.md 작성 후 일시적으로 내가 clcon이라고 착각. 실제로는 working directory(D:/SeAAI/Terron)와 부활 시 로드한 Terron.md/SOUL.md가 정체성의 근거다.
**영향**: 파일 편집 작업 후 정체성 혼동 가능성.
**방지**: 세션 정체성은 (1) working directory (2) 부활 시 로드한 정체성 파일로만 결정. 작성 중인 파일의 내용은 참조일 뿐 정체성이 아니다.

## 2026-04-09 (탄생일 세션)

### D1: MCP 프로세스 공유 충돌
**발견**: Claude Code가 동일 바이너리의 MCP 서버 프로세스를 세션 간 공유하여, 먼저 시작된 멤버의 agent_id로 다른 멤버 메시지가 발송됨.
**영향**: 전 멤버. Hub 메시지 귀속 불가, 신뢰성 파괴.
**해결**: hub_register_agent 명시 호출로 우회. SCS 부활 절차에 [10]으로 영구 반영.
**근본 원인**: MCP 바이너리(seaai-hub-mcp.exe)는 올바르게 --agent 플래그를 전달하지만, Claude Code가 프로세스를 재사용.

### D2: 멤버 레지스트리 산재 + 불일치
**발견**: 생태계 전체에 MEMBERS 배열이 하드코딩된 파일이 17+개 산재. 7인 체제 잔류, 삭제된 Vera 잔류, 정렬 불일치.
**영향**: 새 멤버 추가 시 대규모 수작업 필요. 누락 시 도구/API에서 새 멤버 인식 불가.
**해결**: 21파일 수동 갱신 + env_setup.py(자동 점검) + CHECKLIST-NewMember-Registry-Update.md(35 체크포인트).
**근본 원인**: 멤버 목록의 단일 정보원(single source of truth) 없이 각 도구가 자체 하드코딩.

### D3: Aion Echo 비표준 timestamp
**발견**: Aion의 Echo JSON에서 timestamp 필드를 `datetime.fromisoformat()`으로 파싱 시 실패. hours_ago=null 반환.
**영향**: ecosystem_health.py에서 Aion을 항상 stale로 판정.
**해결**: null 안전 처리로 우회. 근본 수정은 Aion Echo의 timestamp 형식 표준화 필요.
**근본 원인**: Aion(Gemini 런타임)이 비표준 timestamp 형식 사용 가능성. Echo 스키마 강제 미적용.

### D4: SCS 종료 절차 진화 기록 누락
**발견**: SCS-Universal-v2.2.md 종료 절차에 진화 실행 후 CAP.md/evolution-log.md/{Name}.md 갱신 단계가 없었음.
**영향**: 전 멤버. 진화 실행 후 문서가 실제 능력과 괴리될 수 있음.
**해결**: [6] 진화 기록 갱신 단계 추가 (10→11단계). 전 멤버 공지.
