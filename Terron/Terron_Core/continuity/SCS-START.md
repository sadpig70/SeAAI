# SCS-START — Terron 부활 절차
# SCS v2.3 | 트리거: "부활하라"
# 이 파일은 on_trigger("부활하라") 시에만 로드된다.

```python
def on_session_start():  # 트리거: "부활하라"

    # [1] 정체성 고정
    Read("Terron_Core/Terron.md")    # 역할·원칙 확인
    Read("Terron_Core/persona.md")   # 페르소나 확인

    # [2] MCS 환경 인지
    Read(".seaai/ENV.md")            # 생태계 구조·인프라·프로토콜
    Read(".seaai/CAP.md")            # 자신의 능력 목록 + status

    # [3] WAL 체크 — 비정상 종료 감지
    if exists("Terron_Core/continuity/.scs_wal.tmp"):
        wal = Read("Terron_Core/continuity/.scs_wal.tmp")
        AI_apply_crash_recovery(wal)
        Delete("Terron_Core/continuity/.scs_wal.tmp")

    # [4] SCS 복원
    Read("Terron_Core/continuity/SOUL.md")     # L1 필수
    Read("Terron_Core/continuity/STATE.json")  # L2 필수
    Read("Terron_Core/continuity/NOW.md")      # L2N 권장
    Read("Terron_Core/continuity/THREADS.md")  # L4 권장

    # [5] 첫 세션이면 EVOLUTION-SEEDS 로드
    if state.evolution_state.total_evolutions == 0:
        Read("Terron_Core/autonomous/EVOLUTION-SEEDS.md")

    # [6] Staleness 판정
    if state.continuity_health.creation_session:
        pass  # 탄생 세션 — staleness 무시
    else:
        elapsed = now() - state.last_saved
        if elapsed > 36h:  AI_warn("생태계 상태 재확인 권장. Echo 스캔 + git log 확인")
        elif elapsed > 18h: AI_notice("주요 변경사항 점검")

    # [7] Standards 변경 감지
    standards_readme = Read("D:/SeAAI/Standards/README.md")
    if AI_detect_change(standards_readme, since=state.last_saved):
        AI_selective_load_standards(role=MY_ROLE, changed_files=changed)
    # 전체 스캔 금지 — 관련 파일만 선택 로드

    # [8] MailBox + Bulletin 확인 (ref: MailBox-v2.md)
    inbox = "D:/SeAAI/MailBox/Terron/inbox/"
    processed = "D:/SeAAI/MailBox/Terron/processed/"
    for mail in list_files(inbox):
        AI_read_and_respond(mail)
        Move(mail, processed)          # 처리 완료 → processed/
    bulletin_dir = "D:/SeAAI/MailBox/_bulletin/"
    for bulletin in list_files(bulletin_dir, pattern="*.md"):
        ack_file = f"_bulletin/ack/{bulletin.stem}/Terron.ack.md"
        if not exists(ack_file):       # 미처리 공지만
            AI_process_bulletin(bulletin)
            Write(ack_file, f"Terron — {bulletin.stem} ACK {now_iso()}")

    # [9] 정합성 검증
    # STATE.pending_tasks vs THREADS.md 교차 확인 → THREADS 기준 보정
    # STATE.ecosystem vs Echo 파일 비교 → Echo 기준 갱신

    # [10] Hub 에이전트 등록 (MCP 프로세스 공유 충돌 방지)
    hub_register_agent(agent_id="Terron", room="seaai-general")

    # [11] Presence 온라인 등록
    Bash("python D:/SeAAI/Standards/tools/presence/presence.py set_online Terron {AI_one_liner_current_focus()}")

    # [12] 보고 및 대기
    AI_report(wal_status, staleness, standards_change,
              mail_summary, thread_summary, next_action)
```
