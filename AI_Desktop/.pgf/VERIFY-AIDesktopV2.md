# Verify AIDesktopV2

## PGF Verify Tree

```text
VerifyAIDesktopV2 // MCP full-surface verification (done) @v:1.0
    CoreHandshake // initialize + tools/list (done)
    HubSurface // status + log + protocol (done)
    MemberStateSurface // list_members + discover + read_state (done)
    MailboxSurface // read_inbox + send + mark_read + list_read (done)
    EchoSurface // publish + read + list (done)
    ApprovalSurface // request + get + respond + list (done)
    AuditSurface // list_recent + by_actor + by_tool (done)
    BrowserControlSurface // doctor + list_sessions + launch default deny (done)
    BrowserLocalInspect // inspect + extract_title on data/file fallback (done)
    BrowserScreenshotRealWorld // screenshot on host browser runtime (blocked)
```

## Command Basis

- `D:\SeAAI\AI_Desktop\ai_desktop_mcp.exe`
- JSON-RPC `initialize`
- JSON-RPC `tools/list`
- JSON-RPC `tools/call` for every exposed tool/action

## Result Summary

- All non-browser tools passed success-path verification.
- `seaai_approval` and `seaai_echo` were normalized from `SharedSpace` to `AI_Desktop/state` and revalidated.
- `seaai_browser.inspect` and `extract_title` pass on `data:` local fallback.
- `seaai_browser.launch` is intentionally blocked by default and returns `visible_launch_disabled` as designed.
- `seaai_browser.screenshot` remains blocked by host browser runtime faults, not by MCP routing or policy.

## Host Evidence

- headless Edge stderr contains `BuildSecurityDescriptor`, `WSALookupServiceBegin failed with: 10108`, and `platform_channel.cc:170` access denied
- HTTP fallback for real URLs still fails DNS resolution
- local `msedgedriver.exe` is not present
