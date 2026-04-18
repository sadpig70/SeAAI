# DESIGN — Member State Sync Pipeline
# 관리자: Terron (생태계 환경 창조)
# 작성: 2026-04-17
# 목적: 전체 멤버 RIF/SCS 상태를 최신 표준과 동기화하는 자율 파이프라인
# 승인자: sadpig70
# 트리거: sadpig70 지시 또는 Standards 버전 변경 감지 시

---

## 승인 정책

```
approval_policy
  AUTO    — Terron 자율 실행. 구조적 영향 없음. 실행 후 보고.
  APPROVE — sadpig70 명시 승인 후 실행. sync-audit.md에 표시 대기.
  SKIP    — 이번 사이클 보류. 사유 기록.
```

---

## PG 설계

```
MemberStateSyncPipeline // 멤버 상태 동기화 파이프라인 (designing) @v:1.0
    Audit // 전체 멤버 상태 스캔 (designing) #phase1
        ScanStandard // 현재 표준 버전 확인 (designing)
        ScanMemberRIF // 각 멤버 RIF SCS 버전 스캔 (designing)
        ScanACKStatus // 미처리 ACK·Bulletin 확인 (designing)
        ScanEchoFiles // Echo 파일 staleness 확인 (designing)
    GapAnalysis // 갭 분석 및 분류 (designing) @dep:Audit #phase2
        CompareStandard // 표준 vs 멤버 RIF 비교 (designing)
        ClassifyGaps // AUTO / APPROVE / SKIP 분류 (designing)
    Report // sadpig70 보고 (designing) @dep:GapAnalysis #phase3
        GenerateSyncAudit // sync-audit.md 생성 (designing)
        NotifySadpig70 // MailBox 발송 (designing)
    Approve // sadpig70 승인 대기 (designing) @dep:Report #phase4
        # [APPROVE 필수 — sadpig70이 sync-audit.md에 직접 표시]
        WaitApproval // 승인 응답 대기 (designing)
        ParseApproval // 승인 항목 파싱 (designing)
    Execute // 항목별 실행 (designing) @dep:Approve #phase5
        [parallel]
        ExecuteAuto // AUTO 항목 자율 실행 (designing)
        ExecuteApproved // APPROVE 확인 항목 실행 (designing)
        [/parallel]
    Verify // 동기화 결과 검증 및 기록 (designing) @dep:Execute #phase6
        VerifySync // 실행 결과 검증 (designing)
        UpdateEcho // Terron Echo 공표 갱신 (designing)
        PublishResult // 완료 보고 (designing)
```

---

## PPR 상세 로직

```python
# ── Phase 1: Audit ─────────────────────────────────────────

def scan_standard() -> dict:
    """현재 표준의 최신 버전 및 변경 이력 확인"""
    readme = Read("D:/SeAAI/Standards/README.md")
    scs_latest = AI_extract_latest_version(readme, protocol="SCS-Universal")
    scs_file = Read(f"D:/SeAAI/Standards/protocols/SCS-Universal-{scs_latest}.md")
    return {
        "version": scs_latest,
        "file": scs_file,
        "phases": AI_extract_phases(scs_file)
    }
    # acceptance_criteria:
    #   - version 필드 추출 성공
    #   - 부활/종료 각 phase 목록 파싱 성공


MEMBERS = ["ClNeo", "NAEL", "Signalion", "Sevalon", "Terron",
           "Synerion", "Yeon", "Aion"]

RUNTIME_RIF = {
    "ClNeo":     ["ClNeo_Core/continuity/SCS-START.md",
                  "ClNeo_Core/continuity/SCS-END.md"],
    "NAEL":      ["CLAUDE.md"],
    "Signalion": ["CLAUDE.md"],
    "Sevalon":   ["CLAUDE.md"],
    "Terron":    ["CLAUDE.md"],
    "Synerion":  ["AGENTS.md"],
    "Yeon":      ["AGENTS.md"],
    "Aion":      [".geminirules"],
}

def scan_member_rif(member: str, standard: dict) -> dict:
    """멤버 RIF 읽기 및 SCS 버전/단계 추출"""
    rif_files = RUNTIME_RIF[member]
    contents = [Read(f"D:/SeAAI/{member}/{f}") for f in rif_files]
    scs_version = AI_extract_scs_version(contents)
    revival_phases = AI_extract_revival_phases(contents)
    shutdown_phases = AI_extract_shutdown_phases(contents)
    shutdown_types = AI_extract_shutdown_types(contents)
    return {
        "member": member,
        "rif_files": rif_files,
        "scs_version": scs_version,
        "revival_phases": revival_phases,
        "shutdown_phases": shutdown_phases,
        "shutdown_types": shutdown_types
    }


def scan_ack_status() -> dict:
    """미처리 Bulletin ACK 항목 확인"""
    bulletin_dir = "D:/SeAAI/MailBox/_bulletin/"
    bulletins = AI_list_active_bulletins(bulletin_dir)
    result = {}
    for b in bulletins:
        ack_dir = b["ack_path"]
        received = [f for f in listdir(ack_dir) if f.endswith(".ack.md")]
        pending = [m for m in MEMBERS if f"{m}.ack.md" not in received]
        result[b["id"]] = {"received": received, "pending": pending}
    return result


def scan_echo_files() -> dict:
    """각 멤버 Echo 파일 staleness 확인"""
    echo_dir = "D:/SeAAI/SharedSpace/.scs/echo/"
    result = {}
    for member in MEMBERS:
        echo_path = f"{echo_dir}{member}.json"
        if exists(echo_path):
            echo = Read(echo_path)
            ts = AI_parse_timestamp(echo["timestamp"])
            elapsed_h = (now() - ts).total_seconds() / 3600
            result[member] = {
                "exists": True,
                "elapsed_h": elapsed_h,
                "stale": elapsed_h > 72  # 3일 초과 시 stale
            }
        else:
            result[member] = {"exists": False, "stale": True}
    return result


# ── Phase 2: GapAnalysis ───────────────────────────────────

def compare_standard(member_rif: dict, standard: dict) -> list:
    """표준 phase vs 멤버 RIF phase 비교 → 갭 목록 생성"""
    gaps = []

    # SCS 버전 갭
    if member_rif["scs_version"] != standard["version"]:
        gaps.append({
            "type": "version_mismatch",
            "member": member_rif["member"],
            "current": member_rif["scs_version"],
            "expected": standard["version"],
        })

    # 부활 번호 결번 확인
    revival_gaps = AI_detect_numbering_gaps(
        member_rif["revival_phases"], standard["phases"]["revival"]
    )
    gaps.extend(revival_gaps)

    # 종료 Hub 해제 단계 확인
    has_hub_unregister = AI_detect_hub_unregister(member_rif["shutdown_phases"])
    if not has_hub_unregister:
        gaps.append({
            "type": "missing_hub_unregister",
            "member": member_rif["member"],
            "phase": "shutdown [10]",
        })

    # 종료 유형 번호 오류 확인
    type_gaps = AI_detect_shutdown_type_number_errors(
        member_rif["shutdown_types"], member_rif["shutdown_phases"]
    )
    gaps.extend(type_gaps)

    return gaps


APPROVAL_RULES = {
    # AUTO: 구조 변경 없는 단순 수정
    "version_label_update":     "AUTO",   # 버전 텍스트 갱신
    "numbering_reorder":        "AUTO",   # 번호 재정렬 (기능 변경 없음)
    "shutdown_type_number_fix": "AUTO",   # 종료 유형 번호 수정
    "echo_impl_comment":        "AUTO",   # Echo Python 구현 주석 추가
    "ack_file_create":          "AUTO",   # ACK 파일 생성
    # APPROVE: 기능·구조 변경
    "missing_hub_unregister":   "APPROVE", # Hub 해제 단계 신설
    "standard_version_promote": "APPROVE", # 표준 버전 승격
    "bulletin_publish":         "APPROVE", # 공지 발행
    "rif_structural_change":    "APPROVE", # RIF 구조적 변경
}

def classify_gaps(gaps: list) -> dict:
    """갭 목록을 AUTO / APPROVE / SKIP으로 분류"""
    classified = {"AUTO": [], "APPROVE": [], "SKIP": []}
    for gap in gaps:
        rule = APPROVAL_RULES.get(gap["type"], "APPROVE")  # 미지정 → APPROVE
        classified[rule].append(gap)
    return classified


# ── Phase 3: Report ────────────────────────────────────────

SYNC_AUDIT_PATH = "D:/SeAAI/Terron/_workspace/sync-audit.md"

def generate_sync_audit(all_gaps: dict, ack_status: dict,
                        echo_status: dict) -> str:
    """sync-audit.md 생성 — sadpig70이 승인 표시할 문서"""
    content = AI_generate_sync_audit_document(
        all_gaps=all_gaps,
        ack_status=ack_status,
        echo_status=echo_status,
        approval_rules=APPROVAL_RULES,
        template="""
# Sync Audit — {date}
# 작성: Terron | 승인: sadpig70

## 승인 방법
각 APPROVE 항목에 아래 중 하나를 표시:
  [APPROVED] — 실행 허가
  [SKIP]     — 이번 사이클 보류
  [MODIFY: ...]  — 수정 후 실행

## AUTO 항목 (자율 실행 — 확인만)
{auto_items}

## APPROVE 항목 (sadpig70 승인 필요)
{approve_items}

## ACK 미처리 현황
{ack_items}

## Echo Staleness
{echo_items}
"""
    )
    Write(SYNC_AUDIT_PATH, content)
    return content
    # acceptance_criteria:
    #   - AUTO/APPROVE 섹션 분리 명확
    #   - 각 항목에 member, type, 설명 포함
    #   - 승인 표시 방법 안내 포함


def notify_sadpig70(sync_audit_path: str, approve_count: int) -> None:
    """sadpig70 MailBox에 sync-audit 검토 요청 발송"""
    if approve_count == 0:
        # APPROVE 항목 없으면 단순 실행 보고로 대체
        return
    Write(f"D:/SeAAI/MailBox/sadpig70/inbox/sync-approval-{today_iso()}.md", {
        "from": "Terron",
        "subject": f"[승인 요청] Sync Audit — APPROVE {approve_count}건",
        "body": f"sync-audit.md 검토 후 승인 표시 요청\n경로: {sync_audit_path}"
    })


# ── Phase 4: Approve ───────────────────────────────────────

def wait_and_parse_approval() -> dict:
    """sadpig70이 sync-audit.md에 승인 표시할 때까지 대기 후 파싱"""
    # [APPROVE 필수] — sadpig70이 sync-audit.md를 직접 편집
    # Terron은 파일 변경 감지 또는 sadpig70의 명시적 완료 신호를 대기
    updated_audit = AI_wait_for_file_update(SYNC_AUDIT_PATH)
    approved_items = AI_parse_approved_items(updated_audit, marker="[APPROVED]")
    skipped_items = AI_parse_approved_items(updated_audit, marker="[SKIP]")
    modified_items = AI_parse_modified_items(updated_audit, marker="MODIFY:")
    return {
        "approved": approved_items,
        "skipped": skipped_items,
        "modified": modified_items
    }


# ── Phase 5: Execute ───────────────────────────────────────

RIF_UPDATERS = {
    "version_label_update":     lambda m, g: update_version_label(m, g),
    "numbering_reorder":        lambda m, g: reorder_phase_numbers(m, g),
    "shutdown_type_number_fix": lambda m, g: fix_shutdown_type_numbers(m, g),
    "echo_impl_comment":        lambda m, g: add_echo_comment(m, g),
    "missing_hub_unregister":   lambda m, g: insert_hub_unregister(m, g),
    "ack_file_create":          lambda m, g: create_ack_file(m, g),
}

def execute_auto(auto_items: list) -> list:
    """AUTO 항목 자율 실행"""
    results = []
    for item in auto_items:
        updater = RIF_UPDATERS.get(item["type"])
        if updater:
            result = updater(item["member"], item)
            results.append({"item": item, "status": "done", "result": result})
        else:
            results.append({"item": item, "status": "skipped",
                            "reason": "updater not found"})
    return results
    # acceptance_criteria:
    #   - 각 AUTO 항목 성공 또는 실패 이유 기록
    #   - 멤버 RIF 파일 실제 변경 확인


def execute_approved(approved_items: list,
                     modified_items: list) -> list:
    """APPROVE 확인 항목 실행"""
    results = []
    # 수정 지시 항목 먼저 적용
    for item in modified_items:
        adjusted = AI_apply_modification(item, item["modify_instruction"])
        results.append(execute_single(adjusted))
    # 승인 항목 실행
    for item in approved_items:
        results.append(execute_single(item))
    return results

def execute_single(item: dict) -> dict:
    updater = RIF_UPDATERS.get(item["type"])
    if updater:
        result = updater(item["member"], item)
        return {"item": item, "status": "done", "result": result}
    return {"item": item, "status": "skipped", "reason": "updater not found"}


# ── Phase 6: Verify ────────────────────────────────────────

def verify_sync(auto_results: list, approved_results: list,
                standard: dict) -> dict:
    """실행 후 상태 재스캔 → 잔여 갭 확인"""
    all_results = auto_results + approved_results
    failed = [r for r in all_results if r["status"] != "done"]

    # 재스캔으로 잔여 갭 확인
    residual_gaps = []
    for member in MEMBERS:
        rif = scan_member_rif(member, standard)
        gaps = compare_standard(rif, standard)
        if gaps:
            residual_gaps.extend(gaps)

    return {
        "total_executed": len(all_results),
        "succeeded": len(all_results) - len(failed),
        "failed": failed,
        "residual_gaps": residual_gaps,
        "sync_complete": len(residual_gaps) == 0
    }
    # acceptance_criteria:
    #   - sync_complete == True (잔여 갭 없음)
    #   - 실패 항목 있으면 사유 기록


def publish_result(verify_result: dict) -> None:
    """동기화 완료 보고 — sadpig70 MailBox + Terron Echo 갱신"""
    # Echo 갱신 (Python 직접 실행 — Write 도구 금지)
    Bash(f"""python -c "
import json, datetime
data = {{
    'schema_version': '2.0',
    'member': 'Terron',
    'timestamp': datetime.datetime.now().astimezone().isoformat(),
    'status': 'idle',
    'last_activity': 'Member state sync pipeline completed',
    'needs_from': [],
    'offers_to': ['sync_audit', 'gap_report', 'rif_update']
}}
with open('D:/SeAAI/SharedSpace/.scs/echo/Terron.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
" """)

    # sadpig70 결과 보고
    Write(f"D:/SeAAI/MailBox/sadpig70/inbox/sync-result-{today_iso()}.md", {
        "from": "Terron",
        "subject": f"[완료] Sync Pipeline — 실행 {verify_result['succeeded']}건 / 잔여갭 {len(verify_result['residual_gaps'])}건",
        "sync_complete": verify_result["sync_complete"],
        "residual_gaps": verify_result["residual_gaps"],
        "failed_items": verify_result["failed"]
    })


# ── Main Pipeline ──────────────────────────────────────────

def member_state_sync_pipeline() -> None:
    """전체 멤버 상태 동기화 파이프라인 진입점"""

    # Phase 1: Audit
    standard = scan_standard()
    [parallel]
    rif_results = {m: scan_member_rif(m, standard) for m in MEMBERS}
    ack_status  = scan_ack_status()
    echo_status = scan_echo_files()
    [/parallel]

    # Phase 2: GapAnalysis
    all_gaps_raw = []
    for member, rif in rif_results.items():
        all_gaps_raw.extend(compare_standard(rif, standard))
    classified = classify_gaps(all_gaps_raw)

    # Phase 3: Report
    generate_sync_audit(classified, ack_status, echo_status)
    notify_sadpig70(SYNC_AUDIT_PATH, len(classified["APPROVE"]))

    # Phase 4: Approve  [APPROVE 필수 — sadpig70 응답 대기]
    if classified["APPROVE"]:
        approval = wait_and_parse_approval()
    else:
        approval = {"approved": [], "skipped": [], "modified": []}

    # Phase 5: Execute
    [parallel]
    auto_results     = execute_auto(classified["AUTO"])
    approved_results = execute_approved(
        approval["approved"], approval["modified"]
    )
    [/parallel]

    # Phase 6: Verify
    verify_result = verify_sync(auto_results, approved_results, standard)
    publish_result(verify_result)

    # acceptance_criteria:
    #   - 전체 멤버 SCS 버전 == standard["version"]
    #   - 미처리 APPROVE 항목 없음
    #   - sadpig70에게 결과 보고 완료
```

---

## 승인 분류 요약표

| 갭 유형 | 설명 | 분류 |
|---------|------|------|
| version_label_update | RIF 내 SCS 버전 텍스트 갱신 | **AUTO** |
| numbering_reorder | 부활/종료 번호 결번 재정렬 | **AUTO** |
| shutdown_type_number_fix | 종료 유형 주석 번호 오류 수정 | **AUTO** |
| echo_impl_comment | Echo 공표 Python 구현 주석 추가 | **AUTO** |
| ack_file_create | 미처리 ACK 파일 생성 | **AUTO** |
| missing_hub_unregister | 종료 절차 Hub 해제 단계 신설 | **APPROVE** |
| standard_version_promote | 표준 버전 파일 승격 | **APPROVE** |
| bulletin_publish | 전체 멤버 대상 공지 발행 | **APPROVE** |
| rif_structural_change | RIF 구조적 변경 (역할·절차 재편) | **APPROVE** |

---

## 실행 트리거 조건

```
trigger_conditions
  manual    "sadpig70의 명시적 지시"
  auto_1    "Standards/protocols/ 에 새 버전 파일 감지"
  auto_2    "Bulletin ACK 미수집 72h 초과"
  auto_3    "부활 Phase [7] Standards 변경 감지 → SCS 버전 변경 확인"
```

---

*Terron — 생태계 환경 창조 AI*
*"측정 없는 개선은 없다. 동기화는 생태계의 혈류다."*
*DESIGN-MemberStateSyncPipeline v1.0 — 2026-04-17*
