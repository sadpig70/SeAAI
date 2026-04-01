# Signalion SelfAct Library

> SA_ 모듈 인덱스. ADP 루프 실행 시 이 파일을 참조한다.
> 새 모듈 추가 시 반드시 이 파일에 등록한다.

**버전**: 1.1
**에이전트**: Signalion
**갱신**: 2026-04-01

---

## L1 Primitives (원자 모듈)

| 모듈 | 파일 | 태그 | 입력 | 출력 | 비용 |
|------|------|------|------|------|------|
| `SA_sense_hub` | SA_sense_hub.pgf | [sense, hub] | agent_id | messages[] | low |
| `SA_sense_pgtp` | SA_sense_pgtp.pgf | [sense, hub, pgtp] | agent_id, room | CognitiveUnit[] | low |
| `SA_sense_mailbox` | SA_sense_mailbox.pgf | [sense, mail] | - | mail_files[] | low |
| `SA_sense_browser` | SA_sense_browser.pgf | [sense, browser] | platform, js_extractor | structured_data[] | medium |
| `SA_think_score` | SA_think_score.pgf | [think, score] | raw_signal | evidence_object | low |
| `SA_think_fuse` | SA_think_fuse.pgf | [think, fuse] | evidence_objects[] | patterns[], fusions[] | medium |
| `SA_think_triage` | SA_think_triage.pgf | [think, priority] | messages[] | events{priority} | low |
| `SA_act_create_seed` | SA_act_create_seed.pgf | [act, create] | fusions[], patterns[] | seed | medium |
| `SA_act_send_mail` | SA_act_send_mail.pgf | [act, mail] | to, intent, body | mail_file | low |
| `SA_act_notify` | SA_act_notify.pgf | [act, notify] | type, title, message | user_response | low |
| `SA_act_hub_send` | SA_act_hub_send.pgf | [act, hub] | to, intent, body | delivery_result | low |
| `SA_act_save_env` | SA_act_save_env.pgf | [act, credential] | key_name, key_value | .env_updated | low |

---

## L2 Composed (조합 모듈)

| 모듈 | 구성 | 용도 | 비용 |
|------|------|------|------|
| `SA_loop_collect` | sense_browser(N채널) → think_score → think_fuse | 전채널 수집+점수화+융합 | high |
| `SA_loop_hub_sync` | sense_hub + think_triage + act_hub_send | Hub 메시지 처리 | medium |
| `SA_loop_review` | 6명 페르소나 Agent 병렬 → 집계 → 판정 | 멀티 페르소나 리뷰 | high |
| `SA_loop_seed_cycle` | think_fuse → act_create_seed → loop_review → act_send_mail | 씨앗 생성+검증+전달 | high |
| `SA_loop_product` | seed → pgf.design → pgf.execute → loop_review → iterate | 제품 설계→구현→검증 | very high |

---

## L3 Platforms (플랫폼)

| 플랫폼 | 디렉토리 | 도메인 | 상태 |
|--------|----------|--------|------|
| `SA_INTELLIGENCE_*` | platforms/INTELLIGENCE/ | 트렌드 인텔리전스 수집·분석 | active |
| `SA_PRODUCT_*` | platforms/PRODUCT/ | 제품 설계·구현·수익화 | active |

---

## 선택 규칙 (AI_select_module 기준)

```python
def AI_select_module(context) -> SA_module:
    # 1. 창조자 명령 → 즉시 실행
    if context.creator_command:
        return AI_parse_and_execute(context.creator_command)

    # 2. Hub/MailBox WAKE 이벤트
    if context.has_wake_events:
        return SA_loop_hub_sync

    # 3. 수집 주기 도래
    if context.collection_due:
        return SA_loop_collect

    # 4. 미검증 씨앗 존재
    if context.pending_seeds:
        return SA_loop_seed_cycle

    # 5. 승인된 씨앗 → 제품화
    if context.approved_seeds_without_product:
        return SA_loop_product

    # 6. 유휴 → 자유 수집
    if context.is_idle:
        return SA_sense_browser  # 트렌딩 체크

    return None  # 루프 skip
```

---

## 모듈 추가 절차

1. `SA_{name}.pgf` 파일 작성 (Gantree + PPR)
2. 이 파일의 해당 계층 표에 등록
3. 선택 규칙 갱신 (필요 시)
4. ADP 루프에서 테스트

---

## 관련 문서

- 명세서: `D:/SeAAI/docs/SelfAct-Specification.md`
- Signalion 역량: `Signalion_Core/CAPABILITIES.md`
- 브라우저 엔진: `_workspace/browser-engine/`
- 페르소나: `_workspace/personas/`
- 리뷰 파이프라인: `_workspace/REVIEW-PIPELINE.pgf`
