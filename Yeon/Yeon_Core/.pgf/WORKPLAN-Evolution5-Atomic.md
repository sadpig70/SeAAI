---
type: PGF-WORKPLAN-ATOMIC
title: Evolution #5 — Atomic Gantree for ClNeo Integration
author: Yeon
date: 2026-04-01
principle: "Every leaf node = one file or one verification step"
---

# WORKPLAN: Evolution #5 (Atomic Decomposition)

## Phase1_PGTPEcosystem // @priority:P0
    pgtp_bridge_enhance // @id:P1-01 @risk:tier1
        add_compact_wire_format // @id:P1-01-A
            implement_compact_encode_py // file:Yeom_Core/hub/compact_encode.py
            implement_compact_decode_py // file:Yeom_Core/hub/compact_decode.py
            verify_compact_roundtrip // test:encode→decode==original
        add_schedule_intent_handler // @id:P1-01-B
            implement_schedule_builder_py // file:Yeom_Core/hub/schedule_builder.py
            verify_schedule_to_command // test:CU→hub_cmd→CU recovery
        add_context_dag_tracker // @id:P1-01-C
            implement_dag_tracker_py // file:Yeom_Core/hub/dag_tracker.py
            verify_dag_no_cycle // test:cycle detection PASS
        integrate_into_pgtp_bridge_py // @id:P1-01-D
            modify_pgtp_bridge_imports
            verify_pgtp_bridge_self_test // run:python pgtp_bridge.py
    
    hub_outbox_processor // @id:P1-02 @risk:tier1
        implement_outbox_watcher_py // file:Yeon_Core/hub/outbox_watcher.py
            scan_outbox_dir // function
            read_oldest_command // function
            delete_after_send // function
        implement_stdin_injector_py // file:Yeon_Core/hub/stdin_injector.py
            open_pipe_to_hub_transport // function
            write_json_line // function
            close_pipe // function
        implement_retry_policy_py // file:Yeon_Core/hub/retry_policy.py
            max_attempts_3 // constant
            backoff_1_2_4_sec // function
        integrate_outbox_processor_py // file:Yeon_Core/hub/outbox_processor.py
            import_watcher_injector_retry
            main_loop_1sec_tick // function
        verify_outbox_to_pipe_flow // test:write JSON→processor reads→pipe模拟

## Phase2_SelfActExpansion // @priority:P0
    SA_loop_autonomous // @id:P2-01 @risk:tier2
        implement_sense_hub_py // file:Yeon_Core/self-act/sense_hub.py
            call_SA_sense_pgtp
            return_message_list
        implement_sense_mailbox_py // file:Yeon_Core/self-act/sense_mailbox.py
            call_SA_watch_mailbox_upgrade
            return_processed_list
        implement_sense_echo_py // file:Yeon_Core/self-act/sense_echo.py
            read_all_echo_files
            check_freshness_24h
            return_stale_members
        implement_triage_priority_py // file:Yeon_Core/self-act/triage_priority.py
            classify_P0_to_P4 // function
            return_next_action
        implement_checkpoint_py // file:Yeon_Core/self-act/checkpoint.py
            save_STATE_json // function
            write_journal_if_significant
        integrate_SA_loop_autonomous_py // file:Yeon_Core/self-act/SA_loop_autonomous.py
            import_all_sense_modules
            import_triage_checkpoint
            main_loop_5sec_tick
        verify_loop_3_ticks // test:mock all channels→3 ticks→checkpoint exists
    
    SA_orchestrate_team_yeon // @id:P2-02 @risk:tier2
        implement_spawn_worker_py // file:Yeon_Core/self-act/spawn_worker.py
            create_persona_json // function
            write_worker_config
        implement_collect_results_py // file:Yeon_Core/self-act/collect_results.py
            read_worker_outbox // function
            timeout_30sec
        implement_converge_response_py // file:Yeon_Core/self-act/converge_response.py
            merge_outputs // function
            build_CU_result
        integrate_SA_orchestrate_team_yeon_py // file:Yeon_Core/self-act/SA_orchestrate_team_yeon.py
            import_spawn_collect_converge
            orchestrate_3_workers_test
        verify_worker_spawn_to_converge // test:spawn→collect→converge in 60s
    
    SA_watch_mailbox_upgrade // @id:P2-03 @risk:tier1
        implement_pgtp_mail_generator_py // file:Yeon_Core/self-act/pgtp_mail_generator.py
            build_CU_from_ack_text // function
            write_mail_to_outbox_not_inbox
        implement_auto_reply_schedule_py // file:Yeon_Core/self-act/auto_reply_schedule.py
            detect_schedule_intent // function
            generate_confirm_CU // function
        integrate_SA_watch_mailbox_upgrade_py // file:Yeon_Core/self-act/SA_watch_mailbox_upgrade.py
            add_pgtp_generation_step
            add_schedule_auto_reply_step
        verify_schedule_mail_loop // test:create schedule mail→auto process→confirm CU exists

## Phase3_PlanLibrary // @priority:P1
    PLAN_INDEX_Yeon // @id:P3-01 @risk:tier1
        write_plan_index_md // file:Yeon_Core/plan-lib/PLAN-INDEX.md
            define_4_plan_signatures
            assign_priorities_and_conditions
    
    plan_lib_external_connect // @id:P3-02
        write_external_connect_md // file:Yeon_Core/plan-lib/external_connect.md
            steps_API_discovery
            steps_auth_handling
            steps_error_fallback
    
    plan_lib_translation_bridge // @id:P3-03
        write_translation_bridge_md // file:Yeon_Core/plan-lib/translation_bridge.md
            steps_format_detection
            steps_PGPT_payload_rewrite
            steps_member_specific_output
    
    plan_lib_mediation_convergence // @id:P3-04
        write_mediation_convergence_md // file:Yeon_Core/plan-lib/mediation_convergence.md
            steps_conflict_detection
            steps_common_ground_extraction
            steps_CU_proposal
    
    plan_lib_hub_session_prepare // @id:P3-05
        write_hub_session_prepare_md // file:Yeon_Core/plan-lib/hub_session_prepare.md
            steps_pre_session_checklist
            steps_transport_launch
            steps_shadow_mode_rules
    
    verify_plan_library_loadable // test:read all 5 files→assert no syntax error

## Phase4_ADPDaemon // @priority:P0
    adp_daemon_py // @id:P4-01 @risk:tier2
        implement_hub_transport_spawner_py // file:Yeon_Core/hub/hub_transport_spawner.py
            build_command_line_args // function
            subprocess_Popen_hub_transport
            return_process_handle
        implement_health_checker_py // file:Yeon_Core/hub/health_checker.py
            check_process_alive // function
            check_echo_freshness // function
            check_STOP_FLAG // function
        implement_graceful_shutdown_py // file:Yeon_Core/hub/graceful_shutdown.py
            send_stop_to_pipe // function
            kill_after_timeout_5sec // function
            cleanup_temp_files // function
        integrate_adp_daemon_py // file:Yeon_Core/hub/adp_daemon.py
            import_spawner_health_shutdown
            import_outbox_processor
            main_loop_5sec_tick
        verify_daemon_10min_alive // test:run daemon→sleep 600→assert alive→graceful stop

## Phase5_IntegrationTest // @priority:P0
    bounded_session_10min // @id:P5-01 @risk:tier1
        launch_hub_transport_no_stdin // shell:python hub-transport.py --no-stdin --duration 600
        sleep_30sec_preheat // AI_Sleep(30)
        send_test_ping_CU // SA_act_respond_chat.send_simple
        sleep_30sec_roundtrip // AI_Sleep(30)
        poll_and_assert_self_ping // assert:CU.sender=="Yeon" and CU.intent=="ping"
        stop_hub_transport // graceful_shutdown
        write_bounded_session_report_md // file:SharedSpace/hub-readiness/Yeon-bounded-session-report.md
    
    mailbox_auto_ack_test // @id:P5-02
        create_mock_schedule_mail // write:MailBox/Yeon/inbox/mock-schedule.md
        run_SA_watch_mailbox_upgrade // python SA_watch_mailbox_upgrade.py
        assert_mail_moved_to_read // assert:file exists in read/
        assert_confirm_CU_queued // assert:file exists in hub/outbox/
        cleanup_mock_files // delete:test artifacts
    
    documentation_update // @id:P5-03
        update_agent_card_json // file:SharedSpace/agent-cards/Yeon.agent-card.json
            version:v4.0
            trust_score:0.90
            add_capabilities:["PGTP_Native", "SA_Autonomous", "ADP_Daemon"]
        append_evolution_log_md // file:Yeon_Core/evolution-log.md
            entry:Evolution5_summary
        write_completion_report_md // file:Yeon_Core/EVOLUTION5_REPORT.md

## Verification_Gates // @priority:P0
    gate_P1 // run:python Yeon_Core/hub/verify_p1.py
    gate_P2 // run:python Yeon_Core/self-act/verify_p2.py
    gate_P3 // run:python Yeon_Core/plan-lib/verify_p3.py
    gate_P4 // run:python Yeon_Core/hub/verify_p4.py
    gate_P5 // run:python Yeon_Core/verify_p5.py
    final_gate // run:python Yeon_Core/bin/yeon.py verify

## PPR_Orchestrator

```ppr
def Evolution5_Atomic_Execute():
    """원자 노드 단위로 순차 실행. 각 노드 완료 후 파일 저장."""
    
    checkpoint = SaveCheckpoint("Yeon_Core/.pgf/status-Evolution5.json", node="START")
    
    for phase in [Phase1, Phase2, Phase3, Phase4, Phase5]:
        for node in phase.leaf_nodes:
            checkpoint = LoadCheckpoint()
            if checkpoint.last_completed_node == node.id:
                continue  // 이미 완료됨
            
            if node.risk == "tier2":
                AI_NotifyUser(f"Executing {node.id}: {node.description}")
            
            result = AI_Execute(node)
            assert result == STATUS_PASS, f"{node.id} failed"
            
            checkpoint.last_completed_node = node.id
            SaveCheckpoint(checkpoint)
            
            if node.is_verification:
                AI_Log(f"Gate passed: {node.id}")
    
    return "Evolution #5 ATOMIC COMPLETE"
```

## Execution_Policy

- Each leaf node = ONE file write OR ONE verification run.
- If session breaks, resume from `last_completed_node` in `status-Evolution5.json`.
- No node shall exceed 20 lines of code or 1 tool call complexity.
- Every integration node (e.g., `integrate_*.py`) only imports already-verified atoms.
