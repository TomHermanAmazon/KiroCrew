"""Each split facade keeps resolving every public name it bound before its owners moved out.

A facade whose rules moved into owner modules stays the import path callers, tests and
docs use, so a public name it bound before the split -- one it defined, or one it
imported from the rest of ``kiro_crew`` -- is part of its surface even when no in-repo
caller reads it today. Standard-library, typing and third-party imports and private
names are not surface. The inventories below are frozen at the split: a name leaves one
only when the facade deliberately stops offering it.

Each name a facade binds again by import is listed with the module that holds it, and
a fresh interpreter checks the facade's binding is that module's own object, so no
reload or eviction elsewhere in the suite can decide the result.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import kiro_crew
from kiro_crew.subprocess_utf8 import UTF8_TEXT

#: Facade -> the public project names it bound before its split; each must keep resolving.
_BASE_PUBLIC_NAMES: dict[str, frozenset[str]] = {
    "kiro_crew.acp.client": frozenset("""
        ACP_BACKENDS_ADVERTISED_MODEL_SELECTION ACP_BACKENDS_HARNESS_OWNED_SESSIONS
        ACP_BACKENDS_HOST_AUTH_CALLBACK ACP_BACKENDS_INLINE_COMPACTION
        ACP_BACKENDS_INTERNAL_SANDBOX ACP_BACKENDS_LOAD_WITHOUT_MODES
        ACP_BACKENDS_MEMBER_DISPATCH ACP_BACKENDS_MEMBER_PANEL ACP_BACKENDS_META_IDENTITY
        ACP_BACKENDS_MODEL_EFFORT_PAIR_IDS ACP_BACKENDS_MODEL_VIA_CONFIG_OPTION
        ACP_BACKENDS_POD_HOME_REMAP ACP_BACKENDS_RESUME_WITHOUT_LOAD
        ACP_BACKENDS_SEED_LOCAL_SETTINGS ACP_BACKENDS_SESSION_MCP_ARRAY ACP_BACKENDS_STEER
        ACP_BACKENDS_STRUCTURED_REFUSAL ACP_BACKEND_CLAUDE ACP_BACKEND_CODEX
        ACP_BACKEND_DEEPSEEK ACP_BACKEND_GOOSE ACP_BACKEND_KAS ACP_BACKEND_KIRO
        ACP_BACKEND_LAUNCH ACP_BACKEND_NODE_ADAPTER_PACKAGES ACP_BACKEND_OPENCODE
        ACP_BACKEND_PI ACP_BACKEND_PROCESS_NAMES ACP_CLIENT_CAPABILITIES AcpAuthRequired
        AcpClient AcpError AcpEvent AcpModelUnavailable AcpPermissionNeeded AcpProcessDied
        AcpPromptBusy AcpPromptStats AcpRegistrationRateLimited AcpSandboxInitFailed
        AcpTimeoutError AcpToolGateUnroutable BoundWorkspaceMismatch CLAUDE_ACP_BIN
        CLAUDE_ACP_NPM_PKG CLAUDE_CODE_BIN CLIENT_NAME CLIENT_VERSION CODEX_ACP_BIN
        CODEX_ACP_NPM_PKG COMPACT_WAIT_TIMEOUT_SECS CREDENTIAL_POINTER_ENV_VARS ChildRecord
        DEEPSEEK_GATE_EXTENSION_SHA256 DEEPSEEK_PERMISSION_MODE DEFAULT_MODEL
        DRAIN_YIELD_AFTER_S DerivedSpecSnapshot DerivedSpecStale EVENT_AGENT_SWITCHED
        EVENT_CLEAR_STATUS EVENT_COMPACTION_STATUS EVENT_COMPLETE EVENT_MCP_OAUTH_REQUEST
        EVENT_MCP_SERVER_INITIALIZED EVENT_MCP_SERVER_INIT_FAILURE EVENT_SUBAGENT_ACTIVITY
        EVENT_SUBAGENT_LIST EVENT_TEXT_CHUNK EVENT_THINKING_CHUNK EVENT_TOOL_CALL
        EVENT_TOOL_CALL_UPDATE EVENT_TOOL_RESULT EVIDENCE_SAMPLING ForkGovernanceUnresolved
        GOOSE_VERIFIED_VERSION_PREFIX HOOK_EVENT_POST_TOOL_USE IDENTITY_STORE_ROOTS
        IDENTITY_STORE_ROOT_ENV_VARS JSONRPC_METHOD_NOT_FOUND JsonRpcMessage JsonRpcRequest
        KIROCREW_SPAWNED_ENV KIROCREW_SPAWNED_VALUE KIRO_CLI_BIN KIRO_CLI_SUBCMD
        KNOWN_SESSION_UPDATES LAUNCHER_EXIT_PREFIXES LivenessOracle MCP_ROSTER_COMPLETE_NOTE
        METHOD_AGENT_SWITCHED METHOD_CANCEL METHOD_CLEAR_STATUS METHOD_COMMANDS_EXECUTE
        METHOD_COMPACTION_STATUS METHOD_INITIALIZE METHOD_KIRO_SESSION_UPDATE
        METHOD_MCP_OAUTH_REQUEST METHOD_MCP_SERVER_INITIALIZED
        METHOD_MCP_SERVER_INIT_FAILURE METHOD_METADATA METHOD_PROMPT
        METHOD_REQUEST_PERMISSION METHOD_SESSION_LOAD METHOD_SESSION_NEW
        METHOD_SESSION_RESUME METHOD_SESSION_UPDATE METHOD_SET_MODE METHOD_SET_MODEL
        METHOD_SUBAGENT_LIST_UPDATE MIRRORS MODEL_CONFIG_ID McpSessionReport
        NODE_ADAPTER_ENTRY_SEGMENTS OPENCODE_BIN OPENCODE_INSTALL_COMMAND
        OPTION_ALLOW_ALWAYS OPTION_ALLOW_ONCE OUTCOME_CANCELLED OUTCOME_SELECTED
        OversizeLineUnrecoverable PI_ACP_BIN PI_ACP_NPM_PKG PI_ACP_VERIFIED_VERSION PI_BIN
        PI_GATE_EXTENSION_SHA256 PI_INSTALL_COMMAND PI_MIN_VERSION PI_NPM_PKG
        PROTOCOL_VERSION PROTOCOL_VERSION_CLAUDE PROTOCOL_VERSION_DEEPSEEK
        PROTOCOL_VERSION_GOOSE PROTOCOL_VERSION_OPENCODE PROTOCOL_VERSION_PI
        PROVIDER_ERROR_AUTH PROVIDER_ERROR_CONNECTION PROVIDER_ERROR_CREDENTIAL_PROPAGATION
        PROVIDER_ERROR_HTTP_5XX PROVIDER_ERROR_MALFORMED_REQUEST
        PROVIDER_ERROR_MODEL_UNAVAILABLE PROVIDER_ERROR_SESSION_EXPIRED
        PROVIDER_ERROR_THROTTLE PROVIDER_ERROR_UNKNOWN PROVIDER_ERROR_USAGE_LIMIT
        PiGateExtensionTampered ProviderErrorClass RLIMIT_PROFILE_SESSION_HOST
        SANDBOX_LAYER_CREW SANDBOX_LAYER_HARNESS SECRET_URI_PREFIX
        STOP_REASON_COMPACTION_FAILED STOP_REASON_END_TURN STUB_SESSION_TOKEN_ENV
        TERMINAL_TOOL_STATUSES UPDATE_AGENT_MESSAGE_CHUNK UPDATE_AGENT_THOUGHT_CHUNK
        UPDATE_CONFIG_OPTION UPDATE_CURRENT_MODE UPDATE_TOOL_CALL UPDATE_USAGE
        VERDICT_WORKING acp_tool_gate advertised_model_ids agent_env_scrub_prefixes
        agent_scratch agent_sdk agent_spec_snapshot agent_version_from_init
        apply_pod_bundle_spawn apply_windows_resource_ceiling
        assert_voice_runtime_outside_agent_workspace atomic_write attach_stub_session_token
        augmented_path await_under_no_progress_bound bind_voice_safe_agent_workspace_async
        browser_session_env browser_socket_env build_permission_event build_prompt_blocks
        bump_resolution_generation catalog_row_would_drop cgroup_scope_argv
        classify_provider_error classify_tool_call codex_acp_not_found_message
        compaction_failure_detail compaction_failure_is_transient config_dir
        consult_offloaded corroborate_launcher_refusal create_subprocess_limited
        deepseek_gate_extension_path delegated_workspace_exposes_sealed_target
        derive_edit_diff describe_search_path effort_config_option_id
        effort_config_option_value ensure_agent_materialized error_is_refusal_terminal
        extract_tool_purpose finish_suspended_spawn fire_tool_hooks format_command_result
        gate_envelope get_global_hook_store get_global_skill_read_observer host_auth
        inject_xdist_auto_cap injection_server_names is_auth_failure_output
        is_credential_propagation_delay is_registration_throttle_output
        is_sandbox_init_failure_output is_sensitive_path kiro_cli_not_found_message
        kiro_sessions_dir known_kiro_cli_dirs launch_for launcher_refusal
        log_unrenderable_content logger make_unified_diff meta_builtin_server_names
        mint_stub_session_token mirror_for mise_data_dir model_is_unusable
        model_refusal_phrase model_registry model_registry_namespace model_scope
        note_tool_call_started overlay_project_scope parse_claude_compaction_notice
        parse_codex_compaction_update parse_prompt_token_usage parse_refusal
        parse_session_modes parse_slash_command parse_usage_cost parse_usage_update
        permission_floor pi_gate_extension_path pick_served_default pinned_fs
        platform_compat pooled_session_servers prompt_timeout_for_ceiling record_frame
        record_tool_call_finished redact_credentials redact_exfiltration_urls
        redact_log_via_context redact_text registration_rate_limited_error
        registration_throttle_line release_bound_agent_workspace require_fork_governance
        require_fresh_derived_spec require_unchanged_derived_spec
        resolve_bound_session_workspace resolve_kiro_cli resolve_krb5_ccname
        resolve_pin_spelling resolve_prompt_timeout resolve_secret_uris resolve_usable_model
        response_write_window_secs sandbox_init_failure sandbox_init_failure_for_runtime
        sandbox_init_remediation schedule_claim schedule_session_token_publish
        scrub_agent_subprocess_env seed_provenance sel sel_module session_mcp_deny_rules
        subprocess_executor tool_call_content_text tool_output_fingerprints
        warn_unresolved_server_refs wrap_argv wrap_argv_async wrapped_by_crew_sandbox
        write_notification_best_effort write_response_frame_bounded
        """.split()),
    "kiro_crew.cron": frozenset("""
        CHANNEL_MAX_LEN CRON_FIRES CronFolderLookup CronHistoryStore CronJob
        CronLoopSafetyError CronPendingMismatch CronRunRecord CronSchedule CronService
        CronStoreBusy CronStoreUnreadable KiroCrewConfig MAX_CRON_MESSAGE MAX_SHORT_STRING
        ProcessHandle add_handle admission_check agent_sequence_dispatches
        authorize_runtime_kill bind_cron_memory build_cron_session_context
        compute_next_run_ts config_dir cron_expr_matches cron_gate_budget cron_inflight
        cron_job_id_from_session_key cron_owner_matches cron_script
        cron_session_key_is_stable cron_store_lock data_home dispatched_agents_from_disk
        effective_wake_budget emit_counter enabled_count_from_disk ending_fence
        env_flag_enabled failure_name format_schedule get_local_tz is_valid_skip_date
        is_valid_timezone job_agent_names_from_disk job_pause_state_from_disk join_failures
        kill_each kill_set kill_verified_process load_cron_folders logger
        lookup_cron_folder_id parse_time_string platform_compat process_handle_of
        process_survived_async published_config_timezone referenced_skill_names
        release_teardown_lease resolve_cron_memory sel shutdown_event spawn_in_flight
        stall_attribution subprocess_executor teardown_barriers teardown_capture
        unhealthy_jobs_from_disk validate_cron_expr with_kill_failure
        """.split()),
    "kiro_crew.autonudge": frozenset("""
        ADDRESSING_FIELDS APPROVAL_STALL_REASON AUTONUDGE_STOP_REASON AutoNudgeService
        AutoNudgeStaleBaseline AutoNudgeStoreUnvetted MANUAL_STOP_REASON MAX_BANNER_CHARS
        MONITOR_BUSY_RETRY_SECS MONITOR_COMPLETION_EVIDENCE_TIMEOUT_SECS
        MONITOR_STATE_VERSION MONITOR_STOP_APPROVAL_STALL
        MONITOR_STOP_COMPLETION_UNAVAILABLE MONITOR_STOP_SESSION_CLOSE
        MONITOR_STOP_SESSION_UNAVAILABLE MONITOR_STOP_UNSUPPORTED_VERSION MONITOR_STOP_USER
        MONITOR_TERMINAL_REASON MonitorActionCompletion MonitorActionDisposition
        MonitorBudgets MonitorCreationSurface MonitorDecision MonitorDispatchResult
        MonitorObservationStatus MonitorOutcome MonitorProbeResult MonitorState
        MonitorUpdateConflict MonitorVerdict NUDGE_RENEW_DUE_SHARE NudgeAdmissionRefused
        NudgeLoop PlatformCompositionError REVIEW_READY SENTINEL_DROPPED_REASON
        SESSION_START_FAILURE_REASON STRUCTURAL_TERMINAL_REASON autonudge_stop_log
        binding_key_for config_dir data_home decide_monitor enabled fsync_dir get_instance
        infer_monitor infer_subject irq is_channel_key is_sensitive_path
        is_structured_monitor_loop is_unattempted_probe kind_supports_objective legacy_home
        logger loop_subject monitor_budget_reason monitor_stall_reason
        monitor_state_from_dict monitor_state_to_dict new_goal_token nudge_cycle_header
        platform_compat probes quarantine_monitor_state redact_credentials
        redact_exfiltration_urls redact_log_via_context redact_store_value
        redact_via_context repair_sentinel_path replace_with_retry
        retained_outcome_blocks_rearm runtime_budget_exceeded scrub_loop_text
        scrubbed_judge_spec shutdown_event stamp_monitor_alerted
        structured_monitor_binding_key_for targets terminal_notification_delivery_matches
        validate_runtime_secs validation
        """.split()),
    "kiro_crew.apps.builtins.ops_mission_control.backend.routes": frozenset("""
        APP_NAME CLAIMED_BY_OPERATOR CronStoreUnreadable DEFAULT_VERIFY_AFTER_SECS
        EXPIRING_ACTIONS Handler LedgerEntry MAX_INCIDENTS_RESPONSE MODE_ORDER STATE_FIRING
        STATE_OK STATE_SUPPRESSED STATUS_NEEDS_HUMAN Signal UnknownFieldError VALID_ACTIONS
        VERIFIABLE_ACTIONS VERIFY_NOT_CHECKABLE VERIFY_PENDING canonical_slot_key companion
        delete_secret describe_secrets dispatch get_registry handover is_app_enabled ledger
        logger merge_provider_config notify_out policy_store provider_config put_secret
        redact_tokens redact_via_context register_routes resolve_silence_secs rotation sel
        set_top_level slack_out slot_watch store utc_now_iso webhook_mod
        """.split()),
    "kiro_crew.apps.builtins.issue_radar.backend.routes": frozenset("""
        GhCliError GhInvalidInputError GhPermissionError GhSetupError KiroCrewConfig
        LIST_POLL_MAX_STALENESS_SEC LoopBoundLock MAX_ASSIGNEES MAX_ITEM_NUMBER MAX_RUN_ID
        PrSearchError github_client is_app_enabled logger normalize_ui_language_tag
        pipeline_routes provider register_routes sel store ui_language_tag watch
        """.split()),
    "kiro_crew.mcp_gateway.gatewayd": frozenset("""
        Admission Backend BackendGone BackendPool BackendUnavailable CANONICAL_TEMP_KEYS
        CONTROL_PLANE_BACKENDS CallerContext CircuitBreaker DEFAULT_CAPACITY DEFAULT_CEILING
        DEFAULT_FLOOR DRAIN_DEADLINE_SECS DRAIN_SECS HostBudget HostBudgetExhausted
        HostBudgetLimits HostCharge HotKeyStore INTERNAL_STUB_PREFIXES IS_WINDOWS
        KIROCREW_BIN_MCP_SERVERS KiroCrewConfig OUTCOME_FAILURE OUTCOME_NEUTRAL OnQueued
        POOL_SHUTDOWN_SECS Permit PoolAtCapacity PoolKey READ_BUFFER_LIMIT_BYTES
        REGISTERED_CAPABILITIES REJECT_CLASS_CAPACITY REJECT_CLASS_COMPAT
        REJECT_CLASS_ISOLATION SECRET_URI_PREFIX STUB_KEEPALIVE_TYPE SecurityEventLog
        SpawnGate SpawnGateClosed SpawnGateTimeout TargetResolver apps_sweep_spool
        classify_declared_temp_env cleanup_old_spill_files code_fingerprint
        configure_default_executor credwatch declared_temp_refusal_reasons
        default_hot_keys_path env_sidecar_dir env_sidecar_name env_target_resolver
        format_declared_temp_refusals forward_declared_env_enabled get_recorder hash_command
        hash_effective_env hazards is_credential_env_key kiro_crew launch_approval logger
        main maintenance_executor mcp_search_path new_tenant_nonce non_secret_env
        pool_identity_env_keys prewarm_from_payloads records_dir redact
        resolvable_target_stems resolve_limits resolve_once_resolver resolve_overlay_dir
        resolve_peer_identity resolve_secret_uris resolved_launch run_gatewayd socketsec
        spawn_backend spec_path_key stub_fallback_counts subprocess_executor
        sweep_all_backend_tmp tool_surface transport warm_backend warm_code_fingerprint
        """.split()),
    "kiro_crew.crew_log.projection": frozenset("""
        APPROVAL_TYPES CODE_BAD_DATA CONTEXT_ORDINAL_MEMO_LIMIT CONTEXT_SOURCES_PER_TURN_LIMIT
        CONTEXT_TURNS_LIMIT CREDIT_SOURCES Checkpoint CrewLog CrewLogError
        DASHBOARD_AGENTIC_ENTRY_TYPE DASHBOARD_CODE_LIMIT DASHBOARD_FIELD_LIMIT
        DASHBOARD_FOLD_NAME DASHBOARD_REASON_LIMIT DASHBOARD_REFUSED_ENTRY_TYPE
        DASHBOARD_TYPE_LIMIT DASHBOARD_VALUE_BYTES DASHBOARD_VALUE_LIMIT
        DEFAULT_SESSION_FOLD_CACHE_BYTES DEFAULT_SLOT_FOLD_CACHE_BYTES EAGER_FOLD_NAMES
        EAGER_SESSION_FOLD_NAMES EAGER_SLOT_FOLD_NAMES Entry FOLD_NAMES ID_LIMIT
        INTERNAL_PROJECTION_NAMES KIND_SESSION KNOWN_TYPES LAZY_FOLD_REASONS
        LEDGER_ARTIFACT_KEY_LIMIT LEDGER_ARTIFACT_LIMIT LEDGER_ENTRY_TYPE LEDGER_EVENT_KINDS
        LEDGER_EVENT_LIMIT LEDGER_FOLD_NAME LEDGER_PHASE_LIMIT LEDGER_SCHEMA_VERSION
        LEDGER_TERMINAL_PHASES LEDGER_TEXT_LIMIT LEDGER_TRIED_LIMIT MAX_ENTRY_BYTES
        MISTAKES_FOLD_NAME MISTAKE_CORRECTED_CODE MISTAKE_CORRECTION_LIMIT MISTAKE_GROUP_LIMIT
        MODEL_LIMIT OPEN_LIST_LIMIT OPEN_RETAIN_LIMIT OUTLINE_PROMPT_CHARS OUTLINE_REPLY_CHARS
        OUTLINE_TURN_LIMIT OUTLINE_TYPES OVERSIZE_SLOT_CELL_LIMIT OWNER_SERVED_SLOT_PROJECTION
        OpenedRecord PANEL_CREW_KEY_LIMIT PANEL_ENTRY_TYPE PANEL_FOLD_NAME PANEL_HISTORY_LIMIT
        PANEL_OWNER_LIMIT PANEL_SCHEMA_VERSION PANEL_TEMPLATE_LIMIT PANEL_TITLE_LIMIT
        PHASE_SESSION_START PROJECTION_NAMES Projection ProjectionRegistry RADAR_CI_BOUNDS
        RADAR_CI_KEYS RADAR_CLEARABLE_FIELDS RADAR_CREW_LEVEL_EVENT_KIND
        RADAR_DEFAULT_SKIP_SCOPE RADAR_EDITING_PHASES RADAR_ENTRY_TYPE RADAR_EVENT_KINDS
        RADAR_EVENT_LIMIT RADAR_ITEM_LIMIT RADAR_LABELS_LIMIT RADAR_NUMBER_BOUNDS RADAR_PHASES
        RADAR_PHASE_LINE_LIMIT RADAR_SCHEMA_VERSION RADAR_SKIP_LIMIT RADAR_SKIP_SCOPES
        RADAR_TERMINAL_PHASES RADAR_TEXT_LIMIT RADAR_TRIED_LIMIT ReadCursor ResumePoint
        SERVERS_PER_TOOL_LIMIT SESSION_ENTRY_TYPES SESSION_FOLD_CACHE_BYTES_ENV
        SESSION_FOLD_NAMES SLOT_FOLD_CACHE_BYTES_ENV SLOT_PROJECTION_NAMES SUBAGENT_TYPES
        Savepoint SessionProjections TEXT_LIMIT TIMELINE_LIMIT TIMELINE_TYPES TOKEN_DIMENSIONS
        TOOL_NAME_LIMIT TOOL_TYPES TREE_PROJECTION_NAMES USAGE_TYPES WORKSTREAMS_BOARD_LIMIT
        WORKSTREAMS_DECISION_LIMIT WORKSTREAMS_EVENT_BUDGET WORKSTREAMS_EVENT_LIMIT
        WORKSTREAMS_FOLD_NAME WORKSTREAMS_SERIES_LIMIT WORKSTREAMS_SPENDER_LIMIT
        WORKSTREAMS_TASK_LIMIT WORKSTREAMS_TYPES WORKSTREAMS_UNIT_LIMIT WORKTREE_BOARD_LIMIT
        WORKTREE_FOLD_NAME WORKTREE_GOAL_CHARS WORKTREE_OWNER_LIMIT WORK_BLOCKED_REASONS
        WORK_CLOSED_WINDOW WORK_CONDUCTOR_FIELDS WORK_ENTRY_TYPE WORK_EVENT_LIMIT
        WORK_EVENT_TEXT_LIMIT WORK_ITEM_LIMIT WORK_PARKED_LIMIT WORK_STORED_ITEM_LIMIT
        WORK_TOMBSTONE_LIMIT WarmSession WorkBoardForgotten WorkBoardItem WorkBoardView advance
        attribute_seq data_home empty_session fold fold_approvals fold_citations fold_session
        fold_session_warm fold_slot fold_slot_checkpoint fold_slot_warm fold_slot_warm_revised
        fold_state_version fold_status fold_timeline fold_tools fold_tree_checkpoint fold_usage
        forget_session_folds forget_slot_folds initial log_exception_text log_origin log_rank_of
        logger open_session_log projection_of radar_ci_state read_projection
        read_slot_projection read_tree_projection require_name segment_paths
        session_fold_cache_bytes session_fold_memo_bytes session_fold_state_bytes session_ledger
        session_units_by_slot session_units_for_slot slot_fold_cache_bytes slot_fold_cell_bytes
        slot_fold_over_ceiling slot_fold_row_bytes slot_of_session state_is_serializable
        tree_fold_units unit_header_created_at unit_opened_previous units_in_succession
        work_slots_naming_board
        """.split()),
    "kiro_crew.slack.gateway": frozenset("""
        APPROVAL_INTERACTIVE APPROVAL_STALL_REASON AUTO_EFFECT_INSTALL AUTO_EFFECT_MANDATORY
        AUTO_EFFECT_NOTIFY AUTO_ROUTE_GIT AUTO_ROUTE_PROVIDER AUTO_ROUTE_WHEEL AcpError
        AcpProcessDied AgentTurnUsage AutoNudgeService AutoUpdateEffect BOOT_RESTART_HINT
        CHANNEL_ID_RE CHANNEL_SESSION_NAMESPACES CHAT_TYPE_DIRECT CHECK_SUCCEEDED
        CHECK_UNCHECKED CONSECUTIVE_FAILURE_REASON CRED_DISCORD_BOT_TOKEN CRED_FEISHU_APP_ID
        CRED_FEISHU_APP_SECRET CRED_MICROSOFT_APP_ID CRED_MICROSOFT_APP_PASSWORD
        CRED_MICROSOFT_APP_TENANT_ID CRED_OWNER_ID CRED_SLACK_APP_TOKEN CRED_SLACK_BOT_TOKEN
        CRED_TELEGRAM_BOT_TOKEN CRED_WEBEX_BOT_TOKEN CRED_WECOM_BOT_ID CRED_WECOM_SECRET
        CRED_WEIXIN_TOKEN CRON_NOTIFICATION_KIND ChannelHistory ChannelLink ConfigChange
        ConfigDeferred ContextBuilder ConversationLog CronClaimAbandoned CronClaimTimeDenied
        CronJob CronQueueTimeout CronService CronStoreBusy CronStoreUnreadable
        CronVetOverran DEFAULT_MONITOR_STALL_MIN_SECS DEFAULT_MONITOR_STALL_TICKS
        DIGEST_HOLD_SECS DM_SCOPE_UNIFIED DashboardState EXTERNALLY_MANAGED_STAMPS
        FINISHED_LOOP_REASONS GRACEFUL_SHUTDOWN_SECS GatewayManager GatewayOrchestrator
        GatewaySpec HEARTBEAT_KEY HEARTBEAT_TASK_TIMEOUT_SECS
        HOST_SESSION_KEY HeartbeatService HistoryConsolidator HookManager HooksConfig
        INJECTION_TIMEOUT InboundMessage KiroCrewConfig LLMEvent LaunchApprovals LessonStore
        MANAGED_BY_COMMAND MAX_PROMPT_BYTES MAX_SESSION_TTL_SECS MODEL_REFUSED_REASON
        MONITOR_CHANNEL MONITOR_STOP_APPROVAL_STALL MONITOR_STOP_COMPLETION_UNAVAILABLE
        MONITOR_STOP_INVALID_RECORD MONITOR_STOP_SESSION_UNAVAILABLE
        MONITOR_STOP_UNSUPPORTED_VERSION MONITOR_STOP_VERDICT_STALL MONITOR_TERMINAL_REASON
        MemoryStore MonitorActionDisposition MonitorCompletionHook MonitorDispatchResult
        MonitorOutcome NO_TOOL_CALLS_NOTE NudgeLoop ORPHAN_NOTICE_OWED OUTCOME_FAILED
        OUTCOME_OK OUTCOME_STOPPED PATH_ONLY_INSTALL_NOTE PlatformCompositionError
        PostedOptions PromptBusyExhaustedError QUEUED_WAIT_EXPIRED_TEXT RealSlackClient
        SESSION_NOT_FOUND_GIVE_UP_TEXT SESSION_NOT_FOUND_NOT_REPLAYED_TEXT SLACK_NAMESPACE
        STRUCTURAL_TERMINAL_REASON SUBAGENT_BATCH_COMPLETION_PREFIX SUBAGENT_COMPLETION_KIND
        SUBAGENT_COMPLETION_META_KEY SUBAGENT_COMPLETION_PREFIX SUBAGENT_DIGEST_CHUNK_SIZE
        SandboxUnavailableError SessionBusyError SessionClosingError SessionManager
        SilentRenderer SkillsLoader SlackTransport SpawnApprovalUnreachable SubagentDelivery
        SubagentInfo SubagentManager Subscription TOOL_ACTIVITY_ATTR TaskRunner
        ToolApprovalCallback ToolApprovalPolicy TurnDriver UPDATE_INSTALLER_STOP_SECS
        acp_error_after_tool_activity acp_error_is_session_not_found acp_error_is_transient
        agent_scratch agent_sequence_dispatches annotate_model_fallback
        append_fallback_story apply_kas_cli_floor audit_governance_degraded
        auto_update_effect autonudge_enabled autonudge_selfarm beacon boot_platform
        bounded_chat_turn build_cron_ack_block build_cron_session_context
        build_dashboard_url build_directive_consumer build_frontend_async
        build_options_blocks build_provider_factory build_timing_footer build_tool_gate
        builtin_channel_descriptors cautious_boot channel_egress_parts
        channel_inbound_permitted channel_namespace_of check_bundle_freshness
        chunk_for_transport claim_vet_bound commits_ahead compose_nudge_body config_dir
        configure_default_executor configured_fallback_chain consume_reinjection
        context_meter_reading crash_guard create_subprocess_limited cron_gate_budget
        cron_job_env_without_reserved current_context dashboard_slot_key data_home
        deliver_spawn_approval delivery_fingerprint dep_sync display_safe
        disposition_for_stop_reason distribution drain_idle_parent_queue_for_stall
        drain_sign_in_refresher effective_wake_budget embed_executor
        embedding_model_is_custom ensure_agents_slice_limits ensure_cron_slot escape_mrkdwn
        extract_options filter_target_env flush_audit_queue_before_hard_exit
        flush_breadcrumb_writes format_dashboard_urls format_subagent_usage generate_token
        get_shared_embedder git_command_env governance_permits hidden_worktree_edits
        hooks_config_from_config_dict inbound_spool inject_cron_result_to_dashboard
        is_bundled_kiro_cli is_channel_key is_gateway_supported is_keep_response
        is_legacy_slack_key is_local_only is_monitor_completion_evidence is_primary_branch
        is_read_only_bash
        is_structured_monitor_loop is_thread_incognito is_thread_temporary
        is_tracked_channel kiro_agents_dir kiro_crew listener_guard_exit_code live
        load_approvals load_window_off_loop log_probe_failure loggable_path logger
        maintenance_executor make_sync_embed_fn mint_options_token model_file_present
        monitor_state_public_dict name_grant nudge_cycle_header open_dm_with_retry
        parse_dashboard_url parse_kiro_cli_version parse_session_key
        peek_ready_shared_embedder persist_token_record_async persistence_lost_exit_code
        pin_kiro_cli platform_compat prefetch_cron_history probe_data_home
        provider_fallback_active provider_last_turn_usage provider_model_pin_partial
        provider_model_pin_refused publish_turn_identity read_context_tokens
        read_effective_agent read_turn_model rearm_reinjection reason_in
        reconcile_store_embedding_space record_auto_update_effect redact redact_and_truncate
        redact_credentials redact_exfiltration_urls redact_for_display
        redact_log_via_context redact_via_context reembed_progress registry
        rehydrate_slot_from_history_async remember_slack_options render_for_slack
        render_nudge_message repo_exec_config_reason resolve_dashboard_host
        resolve_max_subagents resolve_prefetch resolve_remote_url resolve_restart_launcher
        resolve_session_start_sizing restart_command_hint rewrite_agents rewrite_kwargs
        rollback_skill_bodies run_command_sandboxed run_gateway run_in_cron_gate_pool
        run_in_cron_pool run_in_embed_pool run_persistence_watchdog run_pre_exec_stops
        run_script_sandboxed run_sign_in_refresher run_stale_asset_watchdog
        runtime_budget_exceeded runtime_death safe_context_call safety_override
        sandboxed_spawn_argv sandboxed_spawn_argv_async save_conversation_turn_off_loop
        save_pass sel send_channel_parts session_store_for_turn session_work_dir
        set_publish_disabled shutdown_event shutdown_exit_code signing_key_preflight
        single_completion_meta spawn_guarded_turn start_background_model_download
        start_dashboard stop_reason_landed store_embedding_space_is_stale stream_and_collect
        strip_keep_sentinel subagent_event_slot subprocess_executor summarize_result
        supervisor_reentry sweep_agents_dir terminal_notification_delivery_matches
        token_secret tracks_upstream transient_retry_delay turn_ceiling turn_stats_meta
        update_blocked_reason update_ownership vet_and_audit vet_job_at_fire_time
        wait_for_unwinding_turns warm_backend warn_if_channel_uncredentialed
        warn_unreadable_tracked_channels wave_chunk_meta wave_final_meta work_root
        workspace_root
        """.split()),
    "kiro_crew.sandbox": frozenset("""
        AUTH_SQLITE_DB AUTH_SQLITE_SIDECAR_SUFFIXES BoundWorkspaceMismatch
        CANONICAL_TEMP_KEYS CRON_SCRIPT_CHILD_ENV DECLARED_TEMP_REFUSAL_REASONS
        DeclaredTempRefusal KIROCREW_SANDBOX_TOOL_ENV KIROCREW_SANDBOX_TOOL_VALUE
        KIROCREW_SPAWNED_ENV KIROCREW_SPAWNED_VALUE LAUNCHER_EXIT_PREFIXES
        LiveTargetUnfitness MD_NOTEBOOK_APP_NAME REMEDY_APPARMOR_USERNS
        REMEDY_MAX_USER_NAMESPACES REMEDY_MOUNT_DENIED REMEDY_NO_USER_NS
        REMEDY_USERNS_DENIED RLIMIT_PROFILE_BUILD RLIMIT_PROFILE_EXTRACTOR
        RLIMIT_PROFILE_NONE RLIMIT_PROFILE_SESSION_HOST RLIMIT_PROFILE_TOOL
        SANDBOX_LAYER_CREW SANDBOX_LAYER_HARNESS SandboxCeilingUnsealable
        SandboxUnavailableError UNSANDBOXED_BY_OPERATOR UNSANDBOXED_BY_PLATFORM
        UnauditedSpawnRefused agent_confinement_evidence agent_env_scrub_prefixes
        agents_slice_throttling app_backend_visible_targets
        apply_windows_resource_ceiling assert_voice_runtime_outside_agent_workspace
        bind_voice_safe_agent_workspace bind_voice_safe_agent_workspace_async
        bound_agent_workspace_target build_resource_limit_preexec
        carveout_chain_has_planted_link carveout_shadowed_by_foreign_mask
        cgroup_scope_argv cgroup_scope_bus_env check_agents_slice_pressure
        classify_declared_temp_env classify_declared_temp_path
        cleanup_stale_sandbox_profiles config_dir configured_sandbox_mode
        corroborate_launcher_refusal create_subprocess_limited
        credential_mask_applies crew_home_visible_spellings crew_host_runtime_leaves
        current_context declared_temp_refusal_reasons
        delegated_workspace_exposes_sealed_target detect_backend
        effective_sandbox_mode ensure_agents_slice_limits
        extractor_resource_limit_preexec fd_real_path format_declared_temp_refusals
        fsync_dir install_root_targets_for is_docker_container is_wsl
        kiro_agents_dir kiro_internal_sandbox_enabled kiro_internal_sandbox_switch
        launcher_refusal live_target_pointer_unfitness logger
        masked_credential_leaf_aliases name_scope_unit namespace_argv
        namespace_launcher_script_dir platform_compat popen_limited prewarm_backend
        prime_voice_runtime_sandbox_paths read_cgroup_int refuse_linked_parent
        refuse_unaudited_on_dead_fs release_bound_agent_workspace remedy_guidance
        require_real_model_path require_unaliased_cloud_config
        require_unaliased_launch_state require_unaliased_model_file reset_backend
        resolve_bound_session_workspace resource_limit_preexec
        resource_limit_supervisor_argv run_limited safe_terminal_line
        sandbox_exec_argv sandbox_init_remediation sandbox_launcher
        sandbox_mount_sweep sandbox_plan sandbox_seatbelt sandboxed_spawn_argv
        sandboxed_spawn_argv_async scope_unit_name scrub_agent_denied_env
        scrub_agent_subprocess_env scrub_env session_host_preexec
        shielded_prepare_off_loop spawn_delegates_masking spawn_shim_argv
        unavailable_kind unavailable_reason unavailable_remedy
        unconfined_live_agent_pid unsandboxed_exec_permitted_by userns_available
        voice_runtime_workspace_conflict warm_backend wrap_argv wrap_argv_async
        wrapped_by_crew_sandbox
        """.split()),
    "kiro_crew.providers.acp": frozenset("""
        ACP_BACKENDS_ACP_RUNTIME ACP_BACKENDS_COMPACT ACP_BACKENDS_CONTEXT_RECYCLE
        ACP_BACKENDS_EFFORT_FROM_ADVERTISED_OPTION ACP_BACKENDS_HARNESS_MANAGED
        ACP_BACKENDS_HARNESS_OWNED_SESSIONS ACP_BACKENDS_KIRO_SLASH_COMMANDS ACP_BACKENDS_KNOWN
        ACP_BACKENDS_MEMBER_CAPABILITIES ACP_BACKENDS_MEMBER_TOOL_LIMITS
        ACP_BACKENDS_SESSION_SHARING ACP_BACKENDS_TOOL_SEARCH_OVERLAY ACP_BACKEND_CODEX
        ACP_BACKEND_DEEPSEEK ACP_BACKEND_GOOSE ACP_BACKEND_KAS ACP_BACKEND_KIRO
        ACP_BACKEND_OPENCODE ACP_BACKEND_PI AcpAuthRequired AcpClient AcpError AcpProvider
        AcpRuntime AcpRuntimeError AcpSessionHandle AcpSessionProvider
        CLI_SETTINGS_LOCK_ACTION_TIMEOUT_SECS CLI_SETTINGS_LOCK_TIMEOUT_SECS
        COMPACT_WAIT_TIMEOUT_SECS CancelOutcome DEFAULT_MODEL EFFORT_LEVELS
        EVENT_COMPACTION_STATUS EntitlementRevalidating GrantDeadline InfraError LLMEvent
        LLMProvider McpSessionReport POLICY_ID_BY_BACKEND PROVIDER_LABEL_BY_BACKEND
        PROVIDER_LABEL_CLAUDE PROVIDER_LABEL_DEFAULT STOP_REASON_CANCELLED STOP_REASON_END_TURN
        SessionCapabilities SessionMcpReport TOOL_SEARCH_DEFAULT_MIN_PCT
        TOOL_SEARCH_DEFAULT_MIN_TOKENS ToolSearchSettings advertised_model_ids
        agent_spec_snapshot atomic_write capabilities_for catalog_row_would_drop clamp_min_pct
        clamp_min_tokens effort_config_option_id effort_config_option_value effort_settings_key
        host_auth is_claude_backend is_claude_backend_name kiro_sessions_dir logger mark_run_dir
        mcp_hot_reload_supported model_is_unusable model_registry_namespace model_scope
        model_supports_effort parse_kiro_cli_version pid_exists provider_label
        reclaim_session_work_dir resolve_billing_stats resolve_effort_for_model
        resolve_pin_spelling_on resolve_prompt_timeout_for_deadline
        resume_takes_tool_search_replay sandbox_init_failure_for_runtime sanitize_sink_text
        servers_exposing_no_tools telemetry_channel_of workspace_cli_settings_lock
        """.split()),
    # The loader facade: every public project name it bound before its owners existed.
    "kiro_crew.config.loader": frozenset("""
        ACP_BACKENDS_EFFORT_FROM_ADVERTISED_OPTION ACTIVATION_ALWAYS ACTIVATION_MENTION
        ACTIVATION_OBSERVE ACTIVATION_OFF ACTIVATION_REVIEW APPROVAL_TURN_MARGIN_SECS
        AUTOCOMPACT_PCT_MAX AUTOCOMPACT_PCT_MIN AgentConfig AppSettingsConfig AwsConfig
        BACKGROUND_WORKER_AGENTS CHAT_ENTRY_CACHE_BYTES_DEFAULT CHAT_ENTRY_CACHE_BYTES_MAX
        CHAT_ENTRY_CACHE_BYTES_MIN CHAT_ENTRY_CACHE_ENTRIES_DEFAULT CHAT_ENTRY_CACHE_ENTRIES_MAX
        CHAT_ENTRY_CACHE_ENTRIES_MIN CHAT_TURN_TIMEOUT_MAX CHAT_TURN_TIMEOUT_MIN
        COMPLETION_KEEP_CHARS_MAX COMPLETION_KEEP_CHARS_MIN CONFIG_DIR_NAME
        CONFIG_RESERVED_TOP_KEYS CONNECTIONS_UI_MIGRATION_MARKER CONTEXT_WARN_MARGIN_PCT
        CREDENTIAL_KEYS CRED_AZURE_DEVOPS_EXT_PAT CRED_BITBUCKET_API_TOKEN CRED_BITBUCKET_EMAIL
        CRED_DISCORD_BOT_TOKEN CRED_FEISHU_APP_ID CRED_FEISHU_APP_SECRET CRED_JIRA_API_TOKEN
        CRED_KIRO_API_KEY CRED_MICROSOFT_APP_ID CRED_MICROSOFT_APP_PASSWORD
        CRED_MICROSOFT_APP_TENANT_ID CRED_OWNER_ID CRED_SLACK_APP_TOKEN CRED_SLACK_BOT_TOKEN
        CRED_TELEGRAM_BOT_TOKEN CRED_WAKATIME_API_KEY CRED_WEBEX_BOT_TOKEN CRED_WECOM_BOT_ID
        CRED_WECOM_SECRET CRED_WEIXIN_TOKEN ChannelConfig ComputerUseConfig ConfigDocument
        ConfigReadError ConfigWriteRefused CronHistoryConfig DASHBOARD_PORT
        DEDUP_EVERY_N_SWEEPS_MAX DEFAULT_AUTOCOMPACT_PCT DEFAULT_AUTO_INGEST_ARTIFACT_KINDS
        DEFAULT_CWD_ALLOWED_ROOTS DEFAULT_KIRO_TEMPLATE DEFAULT_MAX_PARALLEL_STEPS
        DEFAULT_MEMORY_STORE DEFAULT_MODEL DEFAULT_POOL_SIZE DEFAULT_SESSION_TIMEOUT
        DEFAULT_SPAWN_MIN_MEMORY_GB DEFAULT_SUBAGENT_COST_GB DEFAULT_SUBAGENT_MAX_TURNS
        DEFAULT_SUBAGENT_QUEUE_MAX_WAIT_SECS DEGRADED_TAILSCALE DEGRADED_WHOLE_CONFIG
        DashboardConfig DecisionsConfig DiscordConfig EFFORT_LEVELS EMBED_RATE_LIMIT_MAX
        EXTRACTION_POOL_SIZE_MAX EXTRACTION_POOL_SIZE_MIN EnvFileWideEncodingError
        ExternalRegistryConfig FOLDER_INGEST_CHUNK_BUDGET_MAX FORWARD_DECLARED_ENV_DEFAULT
        FeishuConfig GROUP_OTHER_BITS HeartbeatConfig IMESSAGE_SERVICES IMPORT_CHUNK_BUDGET_MAX
        IMessageConfig InstancesConfig JAIL_MODE_AUTO JAIL_MODE_OFF JAIL_MODE_ON JiraAuthEntry
        KIRO_CLI_BUILTIN_AGENTS KiroCrewAgentConfig KiroCrewConfig KnowledgeConfig
        LOOP_STALL_EXIT_AFTER_DEFAULT LOOP_STALL_EXIT_AFTER_MANAGED_DEFAULT
        LOOP_STALL_EXIT_AFTER_MAX LOOP_STALL_EXIT_AFTER_MIN MANAGED_VAULT_FIXED_CONSUMERS
        MAX_SUBAGENTS_FIXED_FLOOR MCP_PROBE_TIMEOUT_MAX MCP_PROBE_TIMEOUT_MIN MIGRATE_AGENTS
        MIGRATE_CONNECTIONS_UI MIGRATE_DEFAULT_AGENT MIGRATE_STAR_DEFAULT_TEMPLATE
        MIGRATE_SUPERSEDED_DEFAULTS MIGRATE_WORKSPACES MODEL_NAMESPACE_ACP McpConfig
        McpGatewayConfig MemoryConfig MemoryStoreConfig MessagingConfig MonitoringConfig
        OUTBOX_DIR_NAME POOL_SIZE_MAX POOL_TTL_SECS_MAX POOL_TTL_SECS_MIN PROJECT_PROFILES_KEY
        PublishConfig RECENT_TINT_COUNT_MAX RECENT_TINT_COUNT_MIN ROLE_MODEL_KEYS ResolvedBindings
        ResourceLimitsConfig SCRATCH_ROOT_ENV SESSION_FOLDER_NAME_MAX SESSION_START_TIMEOUT_MAX
        SESSION_START_TIMEOUT_MIN SESSION_TIMEOUT_MAX SESSION_TIMEOUT_MIN SOFT_STOP_BUDGET_MAX
        SOFT_STOP_BUDGET_MIN STT_PROVIDER_LOCAL SUBAGENT_AUTO_MAX_CEILING
        SUBAGENT_MAX_TURNS_CEILING SUBAGENT_TIMEOUT_MAX SUBAGENT_TIMEOUT_MIN SUBAGENT_TIMEOUT_SECS
        SWEEP_CHUNK_BUDGET_MAX SessionConfig SessionSummaryConfig SkillsConfig SlackConfig
        SttConfig SupersededDefault TELEGRAM_ACTIVATIONS THRESHOLD_PCT_MAX THRESHOLD_PCT_MIN
        TOOL_APPROVAL_TIMEOUT_MAX TOOL_APPROVAL_TIMEOUT_MIN TailscaleConfig TaskRunnerConfig
        TeamsConfig TelegramAccountConfig TelegramConfig TelemetryConfig TunnelConfig
        VAULT_CHANNEL_CREDENTIAL_KEYS WakaTimeConfig WatchdogConfig WeComConfig WebexConfig
        WeixinConfig WhatsAppConfig WorkspaceConfig WorkspaceDirUnusable YOLO_UNTIL_SHUTDOWN
        agent_alias_snapshot app_model_pin atomic_write auto_adoptable aws_consent_path
        build_config build_provider_factory capabilities_for coerce_config_field
        coerce_dict_section coerce_effort coerce_fallback_model coerce_project_profiles
        coerce_role_efforts coerce_role_models coerce_runtime_ceiling computer_use_state_path
        config_content_stamp config_dir config_local_path config_package_dir config_path
        consume_managed_service_launch_environment credential_redaction_path crew_autocompact_pct
        data_home decisions_consent_path decode_env_bytes default_overlay_dir default_project_dir
        default_socket_path default_template degraded_config_files demote_scratch_root_override
        denied_commands_path dispatch_kiro_agent drift_summary drop_drifted_keys ensure_data_home
        env_bom_prefix env_path file_delivery_consent_path inject_kiro_cli_api_key
        is_owner_only_target is_valid_effort iter_agent_spec_files jira_global_token_applicable
        jira_host_token_name kiro_agents_dir launched_as_managed_service
        load_config_with_content_stamp load_loop_stall_exit_after logger materialize_workspace_dir
        member_template_id memory_store_name_defect model_registry model_scope
        model_supports_effort next_config_load_ticket normalize_agent_model normalize_jira_host
        normalize_workspace_path oauth_endpoints_path on_event_loop outbox_dir overlay_pins
        parse_agent_spec_text persist_write_back pinned_fs platform_compat project_agents_dir
        project_profile_refusals publish_agent_alias_snapshot publish_autocompact_pct
        publish_config_timezone publish_materialized_agents published_autocompact_pct
        published_config_timezone read_config_document read_config_for_update read_config_text
        read_env_file read_env_file_credential read_env_text read_local_secret record_adoptions
        refresh_config_meta_stamp refresh_materialized_agents registry_trust_path
        reset_dangling_default_agent reset_degraded_observations resolve_agent_bindings
        resolve_agent_config_path resolve_agent_identity resolve_app_spawn_model
        resolve_cc_permission_mode resolve_crew_identity resolve_effective_agent
        resolve_effective_model resolve_env_credential resolve_env_credentials
        resolve_loop_stall_exit_after resolve_memory_store_config resolve_selected_backend
        schedule_materialized_agents_refresh scratch_root_owner_refusal scratch_root_writer_refusal
        ssh_auth_sock_consent_path stamp_config_meta stored_value_or_none strip_kiro_cli_api_key
        strip_utf8_bom superseded_default_drift tailnet_effective_allowed_logins
        tailnet_identity_unknown undecodable_env_message unsandboxed_exec_declared
        unsandboxed_exec_platform_default update_config_locked valid_scratch_root_override
        validate_kiro_agent_references vault_channel_env_value warn_undecodable_env windows_acl
        workspace_dir_for workspace_dir_from_entry workspace_root write_config_atomically
        yolo_duration_to_secs
        """.split()),
    # The package forwards these to the loader facade, which serves them from its owners.
    "kiro_crew.config": frozenset("""
        KiroCrewConfig config_dir config_local_path config_path data_home ensure_data_home
        env_path resolve_agent_config_path
        """.split()),
}

#: Facade -> ``{name: module holding it}`` for each base name the facade re-binds by import.
_REBOUND: dict[str, dict[str, str]] = {
    "kiro_crew.acp.client": {
        "ACP_BACKENDS_HOST_AUTH_CALLBACK": "kiro_crew.acp.types",
        "LAUNCHER_EXIT_PREFIXES": "kiro_crew.sandbox",
        "SANDBOX_LAYER_CREW": "kiro_crew.sandbox",
        "SANDBOX_LAYER_HARNESS": "kiro_crew.sandbox",
        "launcher_refusal": "kiro_crew.sandbox",
        "sandbox_init_remediation": "kiro_crew.sandbox",
    },
    "kiro_crew.cron": {
        "CHANNEL_MAX_LEN": "kiro_crew.validation",
        "MAX_CRON_MESSAGE": "kiro_crew.validation",
        "MAX_SHORT_STRING": "kiro_crew.validation",
        "cron_gate_budget": "kiro_crew.executors",
        "platform_compat": "kiro_crew",
    },
    "kiro_crew.autonudge": {
        "MONITOR_BUSY_RETRY_SECS": "kiro_crew.monitoring.models",
        "MONITOR_COMPLETION_EVIDENCE_TIMEOUT_SECS": "kiro_crew.monitoring.models",
        "MONITOR_STOP_APPROVAL_STALL": "kiro_crew.monitoring.models",
        "MONITOR_STOP_SESSION_CLOSE": "kiro_crew.monitoring.models",
        "MONITOR_STOP_USER": "kiro_crew.monitoring.models",
        "MonitorActionCompletion": "kiro_crew.monitoring.models",
        "MonitorActionDisposition": "kiro_crew.monitoring.models",
        "MonitorBudgets": "kiro_crew.monitoring.models",
        "MonitorCreationSurface": "kiro_crew.monitoring.models",
        "MonitorDecision": "kiro_crew.monitoring.models",
        "MonitorObservationStatus": "kiro_crew.monitoring.models",
        "MonitorProbeResult": "kiro_crew.monitoring.models",
        "MonitorVerdict": "kiro_crew.monitoring.models",
        "REVIEW_READY": "kiro_crew.monitoring.registry",
        "data_home": "kiro_crew.config.loader",
        "decide_monitor": "kiro_crew.monitoring.decision",
        "is_unattempted_probe": "kiro_crew.monitoring.github_provider_errors",
        "kind_supports_objective": "kiro_crew.monitoring.registry",
        "monitor_budget_reason": "kiro_crew.monitoring.decision",
        "monitor_stall_reason": "kiro_crew.monitoring.decision",
        "monitor_state_to_dict": "kiro_crew.monitoring.models",
        "platform_compat": "kiro_crew",
        "probes": "kiro_crew",
        "retained_outcome_blocks_rearm": "kiro_crew.monitoring.models",
        "shutdown_event": "kiro_crew",
        "stamp_monitor_alerted": "kiro_crew.monitoring.decision",
        "targets": "kiro_crew.probes",
        "validate_runtime_secs": "kiro_crew.monitoring.limits",
    },
    "kiro_crew.apps.builtins.ops_mission_control.backend.routes": {
        "CLAIMED_BY_OPERATOR": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "CronStoreUnreadable": "kiro_crew.cron",
        "DEFAULT_VERIFY_AFTER_SECS": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "EXPIRING_ACTIONS": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "LedgerEntry": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "MODE_ORDER": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "STATE_FIRING": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "STATE_OK": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "STATE_SUPPRESSED": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "STATUS_NEEDS_HUMAN": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "Signal": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "UnknownFieldError": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "VALID_ACTIONS": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "VERIFIABLE_ACTIONS": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "VERIFY_NOT_CHECKABLE": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "VERIFY_PENDING": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "describe_secrets": "kiro_crew.apps.builtins.ops_mission_control.backend.secrets",
        "provider_config": "kiro_crew.apps.builtins.ops_mission_control.backend.providers",
        "resolve_silence_secs": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
        "set_top_level": "kiro_crew.apps.builtins.ops_mission_control.backend.providers",
        "utc_now_iso": "kiro_crew.apps.builtins.ops_mission_control.backend.models",
    },
    "kiro_crew.apps.builtins.issue_radar.backend.routes": {
        "KiroCrewConfig": "kiro_crew.config.loader",
        "normalize_ui_language_tag": "kiro_crew.context",
        "ui_language_tag": "kiro_crew.context",
    },
    "kiro_crew.mcp_gateway.gatewayd": {
        "BackendGone": "kiro_crew.mcp_gateway.backend",
        "BackendUnavailable": "kiro_crew.mcp_gateway.pool",
        "CallerContext": "kiro_crew.mcp_caller",
        "DRAIN_DEADLINE_SECS": "kiro_crew.mcp_gateway.pool",
        "HostBudgetExhausted": "kiro_crew.mcp_gateway.host_budget",
        "KIROCREW_BIN_MCP_SERVERS": "kiro_crew.mcp_cleanup",
        "PoolAtCapacity": "kiro_crew.mcp_gateway.pool",
        "SpawnGateClosed": "kiro_crew.mcp_gateway.admission",
        "SpawnGateTimeout": "kiro_crew.mcp_gateway.admission",
        "code_fingerprint": "kiro_crew.code_fingerprint",
        "configure_default_executor": "kiro_crew.executors",
        "env_sidecar_dir": "kiro_crew.mcp_gateway.rewriter",
        "env_sidecar_name": "kiro_crew.mcp_gateway.rewriter",
        "hash_command": "kiro_crew.mcp_gateway.hashing",
        "hash_effective_env": "kiro_crew.mcp_gateway.hashing",
        "is_credential_env_key": "kiro_crew.mcp_gateway.manager",
        "new_tenant_nonce": "kiro_crew.mcp_caller",
        "non_secret_env": "kiro_crew.mcp_gateway.hashing",
        "prewarm_from_payloads": "kiro_crew.mcp_gateway.prewarm",
        "resolve_overlay_dir": "kiro_crew.mcp_gateway.rewriter",
        "resolve_peer_identity": "kiro_crew.peer_resolve",
        "subprocess_executor": "kiro_crew.executors",
        "tool_surface": "kiro_crew.mcp_gateway",
    },
    "kiro_crew.crew_log.projection": {
        "CODE_BAD_DATA": "kiro_crew.crew_log.errors",
        "CrewLog": "kiro_crew.crew_log.store",
        "CrewLogError": "kiro_crew.crew_log.errors",
        "DASHBOARD_AGENTIC_ENTRY_TYPE": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_CODE_LIMIT": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_FIELD_LIMIT": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_FOLD_NAME": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_REASON_LIMIT": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_REFUSED_ENTRY_TYPE": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_TYPE_LIMIT": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_VALUE_BYTES": "kiro_crew.crew_log.entry_types",
        "DASHBOARD_VALUE_LIMIT": "kiro_crew.crew_log.entry_types",
        "Entry": "kiro_crew.crew_log.schema",
        "KIND_SESSION": "kiro_crew.crew_log.schema",
        "LEDGER_ENTRY_TYPE": "kiro_crew.session_ledger",
        "MAX_ENTRY_BYTES": "kiro_crew.crew_log.schema",
        "MISTAKES_FOLD_NAME": "kiro_crew.crew_log.entry_types",
        "MISTAKE_CORRECTED_CODE": "kiro_crew.crew_log.entry_types",
        "MISTAKE_CORRECTION_LIMIT": "kiro_crew.crew_log.entry_types",
        "MISTAKE_GROUP_LIMIT": "kiro_crew.crew_log.entry_types",
        "OpenedRecord": "kiro_crew.crew_log.session_tree",
        "PANEL_CREW_KEY_LIMIT": "kiro_crew.crew_log.entry_types",
        "PANEL_ENTRY_TYPE": "kiro_crew.crew_log.entry_types",
        "PANEL_FOLD_NAME": "kiro_crew.crew_log.entry_types",
        "PANEL_HISTORY_LIMIT": "kiro_crew.crew_log.entry_types",
        "PANEL_OWNER_LIMIT": "kiro_crew.crew_log.entry_types",
        "PANEL_TEMPLATE_LIMIT": "kiro_crew.crew_log.entry_types",
        "PANEL_TITLE_LIMIT": "kiro_crew.crew_log.entry_types",
        "PHASE_SESSION_START": "kiro_crew.context_blocks",
        "ProjectionRegistry": "kiro_crew.projection",
        "RADAR_CI_BOUNDS": "kiro_crew.crew_log.entry_types",
        "RADAR_CI_KEYS": "kiro_crew.crew_log.entry_types",
        "RADAR_CLEARABLE_FIELDS": "kiro_crew.crew_log.entry_types",
        "RADAR_CREW_LEVEL_EVENT_KIND": "kiro_crew.crew_log.entry_types",
        "RADAR_DEFAULT_SKIP_SCOPE": "kiro_crew.crew_log.entry_types",
        "RADAR_EDITING_PHASES": "kiro_crew.crew_log.entry_types",
        "RADAR_ENTRY_TYPE": "kiro_crew.crew_log.entry_types",
        "RADAR_EVENT_KINDS": "kiro_crew.crew_log.entry_types",
        "RADAR_LABELS_LIMIT": "kiro_crew.crew_log.entry_types",
        "RADAR_NUMBER_BOUNDS": "kiro_crew.crew_log.entry_types",
        "RADAR_PHASES": "kiro_crew.crew_log.entry_types",
        "RADAR_SKIP_SCOPES": "kiro_crew.crew_log.entry_types",
        "RADAR_TERMINAL_PHASES": "kiro_crew.crew_log.entry_types",
        "ReadCursor": "kiro_crew.crew_log.store",
        "ResumePoint": "kiro_crew.crew_log.store",
        "SESSION_ENTRY_TYPES": "kiro_crew.crew_log.entry_types",
        "Savepoint": "kiro_crew.projection",
        "WORK_BLOCKED_REASONS": "kiro_crew.work_vocab",
        "WORK_CLOSED_WINDOW": "kiro_crew.work_vocab",
        "WORK_CONDUCTOR_FIELDS": "kiro_crew.work_vocab",
        "WORK_ENTRY_TYPE": "kiro_crew.crew_log.entry_types",
        "WORK_STORED_ITEM_LIMIT": "kiro_crew.work_vocab",
        "WORK_TOMBSTONE_LIMIT": "kiro_crew.work_vocab",
        "WorkBoardForgotten": "kiro_crew.work_vocab",
        "WorkBoardItem": "kiro_crew.work_vocab",
        "WorkBoardView": "kiro_crew.work_vocab",
        "attribute_seq": "kiro_crew.projection",
        "data_home": "kiro_crew.config.paths",
        "fold_citations": "kiro_crew.crew_log.session_tree",
        "log_exception_text": "kiro_crew.crew_log.store",
        "log_rank_of": "kiro_crew.crew_log.session_tree",
        "segment_paths": "kiro_crew.crew_log.store",
        "session_ledger": "kiro_crew",
        "session_units_by_slot": "kiro_crew.crew_log.store",
        "session_units_for_slot": "kiro_crew.crew_log.store",
        "unit_header_created_at": "kiro_crew.crew_log.store",
        "unit_opened_previous": "kiro_crew.crew_log.store",
    },
    "kiro_crew.slack.gateway": {
        "CronClaimAbandoned": "kiro_crew.slack.gateway_runtime.cron_dispatch",
        "CronClaimTimeDenied": "kiro_crew.slack.gateway_runtime.cron_dispatch",
        "CronVetOverran": "kiro_crew.slack.gateway_runtime.cron_dispatch",
        "claim_vet_bound": "kiro_crew.slack.gateway_runtime.cron_dispatch",
        "cron_job_env_without_reserved": "kiro_crew.slack.gateway_runtime.cron_dispatch",
        "run_gateway": "kiro_crew.slack.gateway_runtime.process_entry",
        "signing_key_preflight": "kiro_crew.slack.gateway_runtime.process_entry",
    },
    "kiro_crew.sandbox": {
        "AUTH_SQLITE_DB": "kiro_crew.identity_stores",
        "AUTH_SQLITE_SIDECAR_SUFFIXES": "kiro_crew.identity_stores",
        "KIROCREW_SANDBOX_TOOL_ENV": "kiro_crew.constants",
        "KIROCREW_SANDBOX_TOOL_VALUE": "kiro_crew.constants",
        "KIROCREW_SPAWNED_ENV": "kiro_crew.constants",
        "KIROCREW_SPAWNED_VALUE": "kiro_crew.constants",
        "config_dir": "kiro_crew.config.paths",
        "current_context": "kiro_crew.platform",
        "fd_real_path": "kiro_crew.pinned_fs",
        "fsync_dir": "kiro_crew.atomic_write",
        "kiro_agents_dir": "kiro_crew.config.paths",
        "platform_compat": "kiro_crew",
        "refuse_linked_parent": "kiro_crew.atomic_write",
        "safe_terminal_line": "kiro_crew.terminal_safe",
        "sandbox_launcher": "kiro_crew",
        "sandbox_mount_sweep": "kiro_crew",
        "sandbox_plan": "kiro_crew",
        "sandbox_seatbelt": "kiro_crew",
    },
    "kiro_crew.providers.acp": {
        "ACP_BACKENDS_ACP_RUNTIME": "kiro_crew.acp.types",
        "ACP_BACKENDS_COMPACT": "kiro_crew.acp.types",
        "ACP_BACKENDS_CONTEXT_RECYCLE": "kiro_crew.acp.types",
        "ACP_BACKENDS_EFFORT_FROM_ADVERTISED_OPTION": "kiro_crew.acp.types",
        "ACP_BACKENDS_HARNESS_OWNED_SESSIONS": "kiro_crew.acp.types",
        "ACP_BACKENDS_KIRO_SLASH_COMMANDS": "kiro_crew.acp.types",
        "ACP_BACKENDS_KNOWN": "kiro_crew.acp.types",
        "ACP_BACKENDS_MEMBER_CAPABILITIES": "kiro_crew.acp.types",
        "ACP_BACKENDS_MEMBER_TOOL_LIMITS": "kiro_crew.acp.types",
        "ACP_BACKENDS_SESSION_SHARING": "kiro_crew.acp.types",
        "ACP_BACKENDS_TOOL_SEARCH_OVERLAY": "kiro_crew.acp.types",
        "ACP_BACKEND_CODEX": "kiro_crew.acp.types",
        "ACP_BACKEND_DEEPSEEK": "kiro_crew.acp.types",
        "ACP_BACKEND_GOOSE": "kiro_crew.acp.types",
        "ACP_BACKEND_KAS": "kiro_crew.acp.types",
        "ACP_BACKEND_KIRO": "kiro_crew.acp.types",
        "ACP_BACKEND_OPENCODE": "kiro_crew.acp.types",
        "ACP_BACKEND_PI": "kiro_crew.acp.types",
        "AcpAuthRequired": "kiro_crew.acp.client",
        "AcpClient": "kiro_crew.acp.client",
        "AcpError": "kiro_crew.acp.client",
        "AcpRuntime": "kiro_crew.acp.runtime",
        "AcpRuntimeError": "kiro_crew.acp.runtime",
        "AcpSessionHandle": "kiro_crew.acp.session_handle",
        "AcpSessionProvider": "kiro_crew.acp.session_provider",
        "CLI_SETTINGS_LOCK_ACTION_TIMEOUT_SECS": "kiro_crew.workspace_cli_settings",
        "CLI_SETTINGS_LOCK_TIMEOUT_SECS": "kiro_crew.workspace_cli_settings",
        "COMPACT_WAIT_TIMEOUT_SECS": "kiro_crew.constants",
        "CancelOutcome": "kiro_crew.providers.base",
        "DEFAULT_MODEL": "kiro_crew.acp.client",
        "EFFORT_LEVELS": "kiro_crew.effort",
        "EVENT_COMPACTION_STATUS": "kiro_crew.acp.types",
        "EntitlementRevalidating": "kiro_crew.acp.session_handle",
        "GrantDeadline": "kiro_crew.trust_patterns",
        "InfraError": "kiro_crew.recovery.ladder",
        "LLMEvent": "kiro_crew.providers.base",
        "LLMProvider": "kiro_crew.providers.base",
        "McpSessionReport": "kiro_crew.acp.mcp_session_report",
        "POLICY_ID_BY_BACKEND": "kiro_crew.acp_backends",
        "PROVIDER_LABEL_BY_BACKEND": "kiro_crew.acp.types",
        "PROVIDER_LABEL_CLAUDE": "kiro_crew.acp.types",
        "PROVIDER_LABEL_DEFAULT": "kiro_crew.acp.types",
        "STOP_REASON_CANCELLED": "kiro_crew.acp.types",
        "STOP_REASON_END_TURN": "kiro_crew.acp.types",
        "SessionCapabilities": "kiro_crew.agent_sdk.capabilities",
        "SessionMcpReport": "kiro_crew.providers.base",
        "TOOL_SEARCH_DEFAULT_MIN_PCT": "kiro_crew.agent_sdk.tool_search",
        "TOOL_SEARCH_DEFAULT_MIN_TOKENS": "kiro_crew.agent_sdk.tool_search",
        "ToolSearchSettings": "kiro_crew.agent_sdk.tool_search",
        "advertised_model_ids": "kiro_crew.acp.client",
        "agent_spec_snapshot": "kiro_crew.acp.session_mcp",
        "atomic_write": "kiro_crew.atomic_write",
        "capabilities_for": "kiro_crew.agent_sdk.capabilities",
        "catalog_row_would_drop": "kiro_crew.acp.client",
        "clamp_min_pct": "kiro_crew.agent_sdk.tool_search",
        "clamp_min_tokens": "kiro_crew.agent_sdk.tool_search",
        "effort_config_option_id": "kiro_crew.acp.types",
        "effort_config_option_value": "kiro_crew.acp.types",
        "effort_settings_key": "kiro_crew.effort",
        "host_auth": "kiro_crew.agent_sdk",
        "is_claude_backend_name": "kiro_crew.agent_sdk.backend_identity",
        "kiro_sessions_dir": "kiro_crew.config.paths",
        "mark_run_dir": "kiro_crew.session_work_dir",
        "mcp_hot_reload_supported": "kiro_crew.mcp_hot_reload",
        "model_is_unusable": "kiro_crew.acp.client",
        "model_registry_namespace": "kiro_crew.agent_sdk.backends",
        "model_scope": "kiro_crew",
        "model_supports_effort": "kiro_crew.effort",
        "parse_kiro_cli_version": "kiro_crew.mcp_hot_reload",
        "pid_exists": "kiro_crew.platform_compat",
        "reclaim_session_work_dir": "kiro_crew.session_work_dir",
        "resolve_billing_stats": "kiro_crew.providers.base",
        "resolve_effort_for_model": "kiro_crew.effort",
        "resolve_pin_spelling_on": "kiro_crew.acp.client",
        "resolve_prompt_timeout_for_deadline": "kiro_crew.acp.client",
        "resume_takes_tool_search_replay": "kiro_crew.agent_sdk.tool_search",
        "sandbox_init_failure_for_runtime": "kiro_crew.acp.client",
        "sanitize_sink_text": "kiro_crew.acp.mcp_session_report",
        "servers_exposing_no_tools": "kiro_crew.acp.mcp_session_report",
        "telemetry_channel_of": "kiro_crew.messaging.link",
        "workspace_cli_settings_lock": "kiro_crew.workspace_cli_settings",
    },
    "kiro_crew.config.loader": {
        "ACP_BACKENDS_EFFORT_FROM_ADVERTISED_OPTION": "kiro_crew.agent_sdk.backends",
        "ACTIVATION_ALWAYS": "kiro_crew.config.sections",
        "ACTIVATION_MENTION": "kiro_crew.config.sections",
        "ACTIVATION_OBSERVE": "kiro_crew.config.sections",
        "ACTIVATION_OFF": "kiro_crew.config.sections",
        "ACTIVATION_REVIEW": "kiro_crew.config.sections",
        "APPROVAL_TURN_MARGIN_SECS": "kiro_crew.config.sections",
        "AUTOCOMPACT_PCT_MAX": "kiro_crew.config.sections",
        "AUTOCOMPACT_PCT_MIN": "kiro_crew.config.sections",
        "AgentConfig": "kiro_crew.config.sections",
        "AppSettingsConfig": "kiro_crew.config.integration_sections",
        "AwsConfig": "kiro_crew.config.integration_sections",
        "BACKGROUND_WORKER_AGENTS": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_BYTES_DEFAULT": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_BYTES_MAX": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_BYTES_MIN": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_ENTRIES_DEFAULT": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_ENTRIES_MAX": "kiro_crew.config.sections",
        "CHAT_ENTRY_CACHE_ENTRIES_MIN": "kiro_crew.config.sections",
        "CHAT_TURN_TIMEOUT_MAX": "kiro_crew.config.sections",
        "CHAT_TURN_TIMEOUT_MIN": "kiro_crew.config.sections",
        "COMPLETION_KEEP_CHARS_MAX": "kiro_crew.config.sections",
        "COMPLETION_KEEP_CHARS_MIN": "kiro_crew.config.sections",
        "CONFIG_DIR_NAME": "kiro_crew.config.paths",
        "CONFIG_RESERVED_TOP_KEYS": "kiro_crew.config.resolution",
        "CONNECTIONS_UI_MIGRATION_MARKER": "kiro_crew.config.migration",
        "CONTEXT_WARN_MARGIN_PCT": "kiro_crew.config.sections",
        "ChannelConfig": "kiro_crew.config.sections",
        "ComputerUseConfig": "kiro_crew.config.sections",
        "CronHistoryConfig": "kiro_crew.config.sections",
        "DEDUP_EVERY_N_SWEEPS_MAX": "kiro_crew.config.sections",
        "DEFAULT_AUTOCOMPACT_PCT": "kiro_crew.config.sections",
        "DEFAULT_AUTO_INGEST_ARTIFACT_KINDS": "kiro_crew.config.sections",
        "DEFAULT_CWD_ALLOWED_ROOTS": "kiro_crew.config.sections",
        "DEFAULT_MAX_PARALLEL_STEPS": "kiro_crew.config.sections",
        "DEFAULT_MEMORY_STORE": "kiro_crew.memory_stores",
        "DEFAULT_MODEL": "kiro_crew.config.sections",
        "DEFAULT_POOL_SIZE": "kiro_crew.config.sections",
        "DEFAULT_SESSION_TIMEOUT": "kiro_crew.config.sections",
        "DEFAULT_SPAWN_MIN_MEMORY_GB": "kiro_crew.constants",
        "DEFAULT_SUBAGENT_COST_GB": "kiro_crew.constants",
        "DEFAULT_SUBAGENT_MAX_TURNS": "kiro_crew.constants",
        "DEFAULT_SUBAGENT_QUEUE_MAX_WAIT_SECS": "kiro_crew.constants",
        "DEGRADED_TAILSCALE": "kiro_crew.config.resolution",
        "DEGRADED_WHOLE_CONFIG": "kiro_crew.config.resolution",
        "DashboardConfig": "kiro_crew.config.sections",
        "DecisionsConfig": "kiro_crew.config.sections",
        "DiscordConfig": "kiro_crew.config.sections",
        "EFFORT_LEVELS": "kiro_crew.config.sections",
        "EMBED_RATE_LIMIT_MAX": "kiro_crew.config.sections",
        "EXTRACTION_POOL_SIZE_MAX": "kiro_crew.config.sections",
        "EXTRACTION_POOL_SIZE_MIN": "kiro_crew.config.sections",
        "ExternalRegistryConfig": "kiro_crew.config.sections",
        "FOLDER_INGEST_CHUNK_BUDGET_MAX": "kiro_crew.config.sections",
        "FORWARD_DECLARED_ENV_DEFAULT": "kiro_crew.config.sections",
        "FeishuConfig": "kiro_crew.config.sections",
        "GROUP_OTHER_BITS": "kiro_crew.owner_only_files",
        "HeartbeatConfig": "kiro_crew.config.sections",
        "IMESSAGE_SERVICES": "kiro_crew.config.sections",
        "IMPORT_CHUNK_BUDGET_MAX": "kiro_crew.config.sections",
        "IMessageConfig": "kiro_crew.config.sections",
        "InstancesConfig": "kiro_crew.config.sections",
        "JAIL_MODE_AUTO": "kiro_crew.config.sections",
        "JAIL_MODE_OFF": "kiro_crew.config.sections",
        "JAIL_MODE_ON": "kiro_crew.config.sections",
        "JiraAuthEntry": "kiro_crew.config.sections",
        "KiroCrewAgentConfig": "kiro_crew.config.sections",
        "KiroCrewConfig": "kiro_crew.config.loader_config",
        "KnowledgeConfig": "kiro_crew.config.sections",
        "LOOP_STALL_EXIT_AFTER_DEFAULT": "kiro_crew.config.sections",
        "LOOP_STALL_EXIT_AFTER_MANAGED_DEFAULT": "kiro_crew.config.sections",
        "LOOP_STALL_EXIT_AFTER_MAX": "kiro_crew.config.sections",
        "LOOP_STALL_EXIT_AFTER_MIN": "kiro_crew.config.sections",
        "MAX_SUBAGENTS_FIXED_FLOOR": "kiro_crew.config.sections",
        "MCP_PROBE_TIMEOUT_MAX": "kiro_crew.config.sections",
        "MCP_PROBE_TIMEOUT_MIN": "kiro_crew.config.sections",
        "MIGRATE_AGENTS": "kiro_crew.config.migration",
        "MIGRATE_CONNECTIONS_UI": "kiro_crew.config.migration",
        "MIGRATE_DEFAULT_AGENT": "kiro_crew.config.migration",
        "MIGRATE_STAR_DEFAULT_TEMPLATE": "kiro_crew.config.migration",
        "MIGRATE_SUPERSEDED_DEFAULTS": "kiro_crew.config.migration",
        "MIGRATE_WORKSPACES": "kiro_crew.config.migration",
        "MODEL_NAMESPACE_ACP": "kiro_crew.agent_sdk.capabilities",
        "McpConfig": "kiro_crew.config.sections",
        "McpGatewayConfig": "kiro_crew.config.sections",
        "MemoryConfig": "kiro_crew.config.sections",
        "MemoryStoreConfig": "kiro_crew.config.sections",
        "MessagingConfig": "kiro_crew.config.sections",
        "MonitoringConfig": "kiro_crew.config.sections",
        "OUTBOX_DIR_NAME": "kiro_crew.config.paths",
        "POOL_SIZE_MAX": "kiro_crew.config.sections",
        "POOL_TTL_SECS_MAX": "kiro_crew.config.sections",
        "POOL_TTL_SECS_MIN": "kiro_crew.config.sections",
        "PROJECT_PROFILES_KEY": "kiro_crew.aws_project_profiles",
        "PublishConfig": "kiro_crew.config.sections",
        "RECENT_TINT_COUNT_MAX": "kiro_crew.config.sections",
        "RECENT_TINT_COUNT_MIN": "kiro_crew.config.sections",
        "ROLE_MODEL_KEYS": "kiro_crew.config.sections",
        "ResolvedBindings": "kiro_crew.config.sections",
        "ResourceLimitsConfig": "kiro_crew.config.sections",
        "SCRATCH_ROOT_ENV": "kiro_crew.config.paths",
        "SESSION_FOLDER_NAME_MAX": "kiro_crew.config.sections",
        "SESSION_START_TIMEOUT_MAX": "kiro_crew.config.sections",
        "SESSION_START_TIMEOUT_MIN": "kiro_crew.config.sections",
        "SESSION_TIMEOUT_MAX": "kiro_crew.config.sections",
        "SESSION_TIMEOUT_MIN": "kiro_crew.config.sections",
        "SOFT_STOP_BUDGET_MAX": "kiro_crew.config.sections",
        "SOFT_STOP_BUDGET_MIN": "kiro_crew.config.sections",
        "STT_PROVIDER_LOCAL": "kiro_crew.config.sections",
        "SUBAGENT_AUTO_MAX_CEILING": "kiro_crew.config.sections",
        "SUBAGENT_MAX_TURNS_CEILING": "kiro_crew.config.sections",
        "SUBAGENT_TIMEOUT_MAX": "kiro_crew.constants",
        "SUBAGENT_TIMEOUT_MIN": "kiro_crew.constants",
        "SUBAGENT_TIMEOUT_SECS": "kiro_crew.constants",
        "SWEEP_CHUNK_BUDGET_MAX": "kiro_crew.config.sections",
        "SessionConfig": "kiro_crew.config.sections",
        "SessionSummaryConfig": "kiro_crew.config.sections",
        "SkillsConfig": "kiro_crew.config.sections",
        "SlackConfig": "kiro_crew.config.sections",
        "SttConfig": "kiro_crew.config.sections",
        "SupersededDefault": "kiro_crew.config.superseded_defaults",
        "TELEGRAM_ACTIVATIONS": "kiro_crew.config.sections",
        "THRESHOLD_PCT_MAX": "kiro_crew.config.sections",
        "THRESHOLD_PCT_MIN": "kiro_crew.config.sections",
        "TOOL_APPROVAL_TIMEOUT_MAX": "kiro_crew.config.sections",
        "TOOL_APPROVAL_TIMEOUT_MIN": "kiro_crew.config.sections",
        "TailscaleConfig": "kiro_crew.config.sections",
        "TaskRunnerConfig": "kiro_crew.config.sections",
        "TeamsConfig": "kiro_crew.config.sections",
        "TelegramAccountConfig": "kiro_crew.config.sections",
        "TelegramConfig": "kiro_crew.config.sections",
        "TelemetryConfig": "kiro_crew.config.sections",
        "TunnelConfig": "kiro_crew.config.sections",
        "WakaTimeConfig": "kiro_crew.config.sections",
        "WatchdogConfig": "kiro_crew.config.sections",
        "WeComConfig": "kiro_crew.config.sections",
        "WebexConfig": "kiro_crew.config.sections",
        "WeixinConfig": "kiro_crew.config.sections",
        "WhatsAppConfig": "kiro_crew.config.sections",
        "WorkspaceConfig": "kiro_crew.config.sections",
        "YOLO_UNTIL_SHUTDOWN": "kiro_crew.config.sections",
        "atomic_write": "kiro_crew.atomic_write",
        "auto_adoptable": "kiro_crew.config.superseded_defaults",
        "capabilities_for": "kiro_crew.agent_sdk.capabilities",
        "coerce_effort": "kiro_crew.config.sections",
        "coerce_fallback_model": "kiro_crew.config.sections",
        "coerce_project_profiles": "kiro_crew.aws_project_profiles",
        "coerce_role_efforts": "kiro_crew.config.sections",
        "coerce_role_models": "kiro_crew.config.sections",
        "coerce_runtime_ceiling": "kiro_crew.config.section_builders",
        "config_dir": "kiro_crew.config.paths",
        "config_package_dir": "kiro_crew.config.paths",
        "data_home": "kiro_crew.config.paths",
        "default_overlay_dir": "kiro_crew.mcp_gateway.rewriter",
        "default_socket_path": "kiro_crew.mcp_gateway.rewriter",
        "degraded_config_files": "kiro_crew.config.resolution",
        "demote_scratch_root_override": "kiro_crew.config.paths",
        "drift_summary": "kiro_crew.config.superseded_defaults",
        "drop_drifted_keys": "kiro_crew.config.superseded_defaults",
        "ensure_data_home": "kiro_crew.config.paths",
        "is_owner_only_target": "kiro_crew.owner_only_files",
        "is_valid_effort": "kiro_crew.effort",
        "iter_agent_spec_files": "kiro_crew.agent_spec_format",
        "kiro_agents_dir": "kiro_crew.config.paths",
        "memory_store_name_defect": "kiro_crew.memory_stores",
        "model_registry": "kiro_crew",
        "model_scope": "kiro_crew",
        "model_supports_effort": "kiro_crew.effort",
        "normalize_agent_model": "kiro_crew.config.sections",
        "on_event_loop": "kiro_crew.atomic_write",
        "parse_agent_spec_text": "kiro_crew.agent_spec_format",
        "pinned_fs": "kiro_crew",
        "platform_compat": "kiro_crew",
        "project_agents_dir": "kiro_crew.config.paths",
        "project_profile_refusals": "kiro_crew.aws_project_profiles",
        "record_adoptions": "kiro_crew.config.superseded_defaults",
        "reset_degraded_observations": "kiro_crew.config.resolution",
        "resolve_cc_permission_mode": "kiro_crew.agent_sdk.backends",
        "resolve_memory_store_config": "kiro_crew.config.sections",
        "resolve_selected_backend": "kiro_crew.config.sections",
        "scratch_root_owner_refusal": "kiro_crew.config.paths",
        "scratch_root_writer_refusal": "kiro_crew.config.paths",
        "stored_value_or_none": "kiro_crew.config.superseded_defaults",
        "strip_utf8_bom": "kiro_crew.user_json",
        "superseded_default_drift": "kiro_crew.config.superseded_defaults",
        "tailnet_effective_allowed_logins": "kiro_crew.config.resolution",
        "tailnet_identity_unknown": "kiro_crew.config.resolution",
        "valid_scratch_root_override": "kiro_crew.config.paths",
        "windows_acl": "kiro_crew",
        "yolo_duration_to_secs": "kiro_crew.config.sections",
    },
    "kiro_crew.config": {
        "KiroCrewConfig": "kiro_crew.config.loader_config",
        "config_dir": "kiro_crew.config.paths",
        "config_local_path": "kiro_crew.config.loader_locations",
        "config_path": "kiro_crew.config.loader_locations",
        "data_home": "kiro_crew.config.paths",
        "ensure_data_home": "kiro_crew.config.paths",
        "env_path": "kiro_crew.config.loader_credentials",
        "resolve_agent_config_path": "kiro_crew.config.loader_locations",
    },
}

_PROBE = """
import importlib, json, sys
rebound = json.loads(sys.argv[1])
checked, wrong = 0, []
for facade, names in rebound.items():
    module = importlib.import_module(facade)
    for name, home in names.items():
        checked += 1
        if getattr(module, name, None) is not getattr(importlib.import_module(home), name):
            wrong.append(f"{facade}.{name}")
print(json.dumps({"checked": checked, "wrong": wrong}))
"""


@pytest.mark.parametrize("facade", sorted(_BASE_PUBLIC_NAMES))
def test_every_base_public_name_resolves_on_its_facade(facade: str) -> None:
    module = importlib.import_module(facade)
    assert sorted(name for name in _BASE_PUBLIC_NAMES[facade] if not hasattr(module, name)) == []


def test_every_rebound_name_is_a_base_public_name_of_its_facade() -> None:
    assert set(_REBOUND) == set(_BASE_PUBLIC_NAMES)
    for facade, names in _REBOUND.items():
        assert names and set(names) <= _BASE_PUBLIC_NAMES[facade], facade


def test_a_rebound_name_is_the_object_its_home_module_holds(tmp_path: Path) -> None:
    """Checked in a fresh interpreter, so no module another test reloaded or evicted
    can make a copy look like the original, or the original look like a copy. The child
    runs in ``tmp_path``, so anything an import writes by a relative path stays there."""
    env = dict(os.environ)
    src = str(Path(kiro_crew.__file__).resolve().parents[1])
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    out = subprocess.run(
        [sys.executable, "-c", _PROBE, json.dumps(_REBOUND)],
        capture_output=True,
        check=True,
        env=env,
        cwd=tmp_path,
        timeout=60,
        **UTF8_TEXT,
    )
    result = json.loads(out.stdout.splitlines()[-1])
    assert result == {"checked": sum(map(len, _REBOUND.values())), "wrong": []}, out.stderr
