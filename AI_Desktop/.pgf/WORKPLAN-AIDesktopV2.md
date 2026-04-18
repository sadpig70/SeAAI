# AIDesktopV2 Work Plan

## POLICY

```python
POLICY = {
    "_version": "codex-0.1",
    "max_retry": 3,
    "on_blocked": "skip_and_continue",
    "completion": "all_done_or_blocked",
    "max_verify_cycles": 2,
    "delegate_allowed": False,
    "allowed_paths": [
        "D:/SeAAI/AI_Desktop"
    ],
    "forbidden_actions": [
        "destructive_without_user_request",
        "unapproved_network"
    ],
    "parallel_mode": "sequential_unless_explicit_parallel",
}
```

## Execution Tree

```text
AIDesktopV2 // active canonical SeAAI-only MCP bridge package (done) @v:2.1
    AuditLegacySurface // legacy scope and drift captured (done)
    FreezeToolSurface // SeAAI-only tool set fixed (done) @dep:AuditLegacySurface
    HardenDynamicRunner // python-only interpreter + path escape guard (done) @dep:FreezeToolSurface
    UpdateDocs // README and TSG aligned with actual enforcement (done) @dep:HardenDynamicRunner
    StabilizeBrowserBridge // edge-cli diagnostics + fallback chain implemented (done) @dep:FreezeToolSurface
    RestoreDeterministicBuild // Cargo.lock + offline/MSVC build path restored (done) @dep:HardenDynamicRunner
    VerifyMcpSurface // initialize, tools/list, policy deny, tool call smoke tests (done) @dep:UpdateDocs,StabilizeBrowserBridge,RestoreDeterministicBuild
    NormalizeRootPath // active root moved to D:/SeAAI/AI_Desktop and docs/build refs updated (done) @dep:VerifyMcpSurface
    ArchiveLegacyDocs // historical document sources moved under _legacy (done) @dep:NormalizeRootPath
    RunFullSurfaceValidation // all exposed MCP tools exercised with read/write/approve paths where applicable (done) @dep:ArchiveLegacyDocs
    NormalizeStateRoots // approval and echo storage moved from SharedSpace into AI_Desktop/state (done) @dep:RunFullSurfaceValidation
    MigrateLegacyState // existing approval/echo records copied into AI_Desktop/state for continuity (done) @dep:NormalizeStateRoots
    AddLocalBrowserFallback // data/file inspect and title extraction succeed without external network (done) @dep:MigrateLegacyState
    RecordBrowserHostBlocker // headless Edge screenshot and external URL inspect remain machine-blocked (done) @dep:AddLocalBrowserFallback
```
