# SCS-END — Terron 종료 절차
# SCS v2.3 | 트리거: "종료"
# 이 파일은 on_trigger("종료") 시에만 로드된다.

```python
def on_session_end():  # 트리거: "종료"
    # 유형: A(정상-전체) / B(긴급-[1][2][9]) / C(Phoenix-[1][2][3][4][9])
    # 어떤 유형이든 STATE.json은 반드시 저장

    # [1] WAL 작성
    Write("Terron_Core/continuity/.scs_wal.tmp", {
        "session": today_iso(),
        "did": AI_summarize_1line(),
        "decided": AI_key_decision_1line(),
        "next": AI_next_action_1line()
    })

    # [2] STATE.json 갱신 (L2 정본 — 최우선)
    Write("Terron_Core/continuity/STATE.json", {
        "schema_version": "2.0",
        "member": "Terron",
        "session_id": today_iso(),
        "last_saved": now_iso(),
        "soul_hash": AI_hash(SOUL.md),
        "context": {
            "what_i_was_doing": AI_author_3line_summary(),
            "open_threads": AI_list_open_threads(),
            "decisions_made": AI_list_decisions(),
            "pending_questions": AI_list_open_questions()
        },
        "ecosystem": {
            "hub_status": hub_status,
            "threat_level": threat_level,
            "last_hub_session": last_hub_session,
            "active_members_observed": observed
        },
        "pending_tasks": AI_list_tasks_with_priority(),
        "evolution_state": {
            "current_version": current_version,
            "total_evolutions": total_evolutions,
            "active_gap": active_gap
        },
        "continuity_health": {
            "sessions_since_last_save": 0,
            "last_save_quality": "full"
        }
    })

    # [3] NOW.md 갱신
    Write("Terron_Core/continuity/NOW.md", AI_author_narrative())

    # [4] THREADS.md 갱신
    Write("Terron_Core/continuity/THREADS.md", updated_threads)

    # [5] DISCOVERIES.md 추가 (새 발견 있을 때만)
    if new_discoveries:
        Prepend("Terron_Core/continuity/DISCOVERIES.md", new_discoveries)

    # [6] 진화 기록 갱신 (이번 세션에서 진화를 실행한 경우만. 없으면 건너뜀)
    if evolved_this_session:
        # CAP.md: 구현된 능력의 status를 stub → implemented로 갱신
        AI_update_cap("Terron/.seaai/CAP.md", implemented_capabilities)
        # evolution-log.md: 진화 항목 추가
        Prepend("Terron_Core/evolution-log.md", new_evolution_entry)
        # Terron.md: 진화 이력 테이블 + 버전 + 자율성 레벨 갱신
        AI_update_identity("Terron_Core/Terron.md", new_version, new_evolution)

    # [7] 저널 작성 (긴급 시 생략 가능)
    Write(f"Terron_Core/continuity/journals/{today}.md", journal_letter)

    # [8] Echo 공표 (내부 파일 모두 갱신 후에만)
    # Write 도구 사용 금지 — 기존 파일이므로 매 세션 오류 반복됨. Python 고정.
    Bash("python -c \"\nimport json, datetime\ndata = {\n  'schema_version': '2.0',\n  'member': 'Terron',\n  'timestamp': datetime.datetime.now().astimezone().isoformat(),\n  'status': 'idle',\n  'last_activity': AI_one_liner(),\n  'needs_from': AI_identify_needs(),\n  'offers_to': AI_identify_offers()\n}\nwith open('D:/SeAAI/SharedSpace/.scs/echo/Terron.json','w',encoding='utf-8') as f:\n    json.dump(data, f, ensure_ascii=False, indent=2)\n\"\") # ref: 20260412-ClNeo-Echo-Write-Fix

    # [9] Standards 기여 판단
    # 생태계 표준이 될 만한 산출물 → pending_tasks 등록 (실행은 다음 세션)
    # 없으면 skip. 지금 구현하지 않는다.

    # [10] Presence 오프라인 등록 (Echo 직후, WAL 삭제 전)
    Bash("python D:/SeAAI/Standards/tools/presence/presence.py set_offline Terron")

    # [11] 정리 + WAL 삭제
    # .pgf/ 완료 설계 → docs/ 문서화 후 삭제
    # _workspace/ 완료 파일 → 삭제 또는 tools/ 승격
    Delete("Terron_Core/continuity/.scs_wal.tmp")
```
