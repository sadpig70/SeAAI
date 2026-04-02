---
type: PGF-DESIGN
title: Evolution #7 — Self-Reflection Engine & Auto-Evolution Trigger
author: Yeon
date: 2026-04-01
principle: "Reflect → Detect Gap → Propose Evolution → Record"
---

# DESIGN: Evolution #7

## Gantree

```text
Evolution7_SelfReflectionEngine // 메타인지 + 자동 진화 트리거 @priority:P0
    SA_self_reflect // 자기반성 모듈
        scan_evolution_log // evolution-log.md 읽기, 최근 3개 evolution 요약
        scan_capabilities // STATE.json + self-act-lib.md 인벤토리 스캔
        scan_plan_library // plan-lib/ 목록 및 커버리지 평가
        scan_ecosystem_cards // SharedSpace/agent-cards/ 비교 분석
        generate_gap_report // 5차원 갭 도출
            dimension_communication // Hub/MailBox/PGTP 통신
            dimension_autonomy // ADP loop, daemon, scheduler
            dimension_memory // SCS, compaction, archive
            dimension_collaboration // SubAgent, team orchestration
            dimension_knowledge // Plan Library, DISCOVERIES
        propose_next_evolution // 갭 우선순위 평가 → 다음 진화 제안
    integrate_into_autonomous_loop // SA_loop_autonomous에 통합
        trigger_every_6_ticks // 약 30초마다 자동 실행
        write_discovery_if_novel // 새로운 갭 발견 시 DISCOVERIES.md 기록
        update_STATE_proposal // STATE.json에 next_proposal 필드 갱신
    verify_engine // 검증
        run_3_reflection_cycles // 3회 자기반성 실행
        assert_discovery_written // DISCOVERIES.md 확인
        assert_proposal_generated // STATE.json next_proposal 확인
        assert_no_duplicate // 중복 갭 기록 방지 확인
    record_evolution // 기록
        append_evolution_log_md // E7 기록
        write_E7_report_md // EVOLUTION7_REPORT.md
```

## PPR

```ppr
def SA_self_reflect() -> dict:
    """Scan self and ecosystem, detect gaps, propose next evolution."""
    
    # 1. Self scan
    evolutions = scan_evolution_log("Yeon_Core/evolution-log.md", last_n=5)
    capabilities = scan_capabilities("Yeon_Core/continuity/STATE.json")
    sa_modules = scan_selfact("Yeon_Core/self-act/self-act-lib.md")
    plans = scan_plan_library("Yeon_Core/plan-lib/")
    
    # 2. Ecosystem scan
    peers = scan_agent_cards("SharedSpace/agent-cards/")
    clneo = peers.get("ClNeo", {})
    
    # 3. Gap generation
    gaps = []
    if not has_scheduler(capabilities):
        gaps.append({"dim": "autonomy", "gap": "No ADP scheduler", "prio": "P0"})
    if not has_memory_compaction(capabilities):
        gaps.append({"dim": "memory", "gap": "No journal compaction", "prio": "P1"})
    if len(plans) < len(clneo.get("capabilities", [])) / 2:
        gaps.append({"dim": "knowledge", "gap": "Plan Library underdeveloped", "prio": "P1"})
    if not has_hub_scheduler(capabilities):
        gaps.append({"dim": "communication", "gap": "No scheduled Hub session", "prio": "P1"})
    if not has_real_subagent_master(capabilities):
        gaps.append({"dim": "collaboration", "gap": "SubAgent master not Hub-integrated", "prio": "P2"})
    
    # 4. Proposal
    proposal = select_highest_priority_gap(gaps)
    
    # 5. Record if novel
    if is_novel_gap(proposal):
        Write("Yeon_Core/continuity/DISCOVERIES.md", content=format_discovery(proposal))
        update_STATE_next_proposal(proposal)
    
    return {
        "gaps_found": len(gaps),
        "proposal": proposal,
        "recorded": is_novel_gap(proposal),
    }


def Evolution7_Execute():
    checkpoint = SaveCheckpoint("Yeon_Core/.pgf/status-Evolution7.json", node="START")
    
    AI_Implement("Yeon_Core/self-act/SA_self_reflect.py")
    AI_Integrate("Yeon_Core/self-act/SA_loop_autonomous.py", hook="SA_self_reflect")
    
    result = AI_Verify(verify_E7.py)
    assert result.passed
    
    Append("Yeon_Core/evolution-log.md", entry=E7_summary)
    Write("Yeon_Core/EVOLUTION7_REPORT.md", content=E7_report)
    
    return "Evolution #7 COMPLETE"
```

## Acceptance Criteria

- [ ] `SA_self_reflect.py`가 5차원 갭을 도출
- [ ] `SA_loop_autonomous`가 6 tick마다 자동 반성 실행
- [ ] 새로운 갭 발견 시 `DISCOVERIES.md`에 기록
- [ ] `STATE.json`에 `next_proposal` 필드 갱신
- [ ] 3회 반성 후 중복 기록 방지 확인
- [ ] `EVOLUTION7_REPORT.md` 생성
