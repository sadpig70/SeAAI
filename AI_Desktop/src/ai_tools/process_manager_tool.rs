//! src/ai_tools/process_manager_tool.rs
//! Enhanced Windows Process Manager Tool with TES/TSG integration and cross-platform support

use anyhow::{anyhow, Result};
use once_cell::sync::Lazy;
use prometheus::{register_histogram, Histogram};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{collections::HashMap, path::PathBuf, time::Duration};
#[cfg(not(windows))]
use sysinfo::Signal as SysinfoSignal;
use sysinfo::{Pid, ProcessesToUpdate, System};
use thiserror::Error;
use tokio::time;
use tracing::instrument;

#[cfg(windows)]
use windows::{
    core::{Error as WindowsError, PCWSTR, PWSTR},
    Win32::{Foundation::*, System::Threading::*, UI::WindowsAndMessaging::*},
};

use crate::core::{Permission, Tool, ToolContext, ToolResult};

// TSG mock implementation (replace with actual gRPC in production)
async fn tsg_filter_input(payload: &Value) -> Result<Value> {
    let cmd = payload.get("cmd").and_then(|v| v.as_str());
    if let Some(cmd) = cmd {
        if cmd.contains('|') || cmd.contains('&') || cmd.contains(';') || cmd.contains('`') {
            return Err(anyhow!("TSG: Invalid command detected"));
        }
    }
    tracing::info!("TSG filter passed: {:?}", payload);
    Ok(payload.clone())
}

// TES ConfigManager mock implementation
async fn get_config() -> Result<(Vec<u32>, u64, Vec<String>)> {
    Ok((
        vec![1, 2, 3], // Whitelisted PIDs
        10_485_760,    // Max capture bytes (10MB)
        vec![
            "list".into(),
            "inspect".into(),
            "sample_usage".into(),
            "cpu_usage".into(),
        ],
    ))
}

//
// ---- Error Types ----
//
#[derive(Error, Debug)]
pub enum ProcessError {
    #[error("Process not found: {0}")]
    NotFound(u32),
    #[error("Access denied for process: {0}")]
    AccessDenied(u32),
    #[error("Timeout waiting for process: {0}")]
    Timeout(u32),
    #[error("Windows API error: {0}")]
    WinApi(String),
    #[error("Invalid input: {0}")]
    InvalidInput(String),
}

#[cfg(windows)]
impl From<WindowsError> for ProcessError {
    fn from(err: WindowsError) -> Self {
        ProcessError::WinApi(format!("{:?}", err))
    }
}

//
// ---- Metrics ----
//
static PROC_LATENCY: Lazy<Histogram> = Lazy::new(|| {
    register_histogram!(
        "proc_op_latency_seconds",
        "Process operation latency",
        vec![0.1, 0.5, 1.0, 2.0]
    )
    .unwrap()
});

//
// ---- Request/Response Types ----
//
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Op {
    List,
    Inspect,
    Tree,
    Spawn,
    Wait,
    Kill,
    Close,
    SampleUsage,
    CpuUsage,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum WindowState {
    Normal,
    Min,
    Max,
    Hidden,
}
impl Default for WindowState {
    fn default() -> Self {
        WindowState::Normal
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum PriorityClass {
    Idle,
    BelowNormal,
    Normal,
    AboveNormal,
    High,
    Realtime,
}
impl Default for PriorityClass {
    fn default() -> Self {
        PriorityClass::Normal
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
enum Signal {
    WmClose,
    Terminate,
}
impl Default for Signal {
    fn default() -> Self {
        Signal::WmClose
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct ProcReq {
    #[serde(default)]
    op: Option<Op>,
    #[serde(default)]
    pid: Option<u32>,
    #[serde(default)]
    pids: Option<Vec<u32>>,
    #[serde(default)]
    name: Option<String>,
    #[serde(default)]
    max_items: Option<u32>,
    #[serde(default)]
    cmd: Option<String>,
    #[serde(default)]
    args: Option<Vec<String>>,
    #[serde(default)]
    cwd: Option<String>,
    #[serde(default)]
    env: Option<HashMap<String, String>>,
    #[serde(default)]
    capture: Option<bool>,
    #[serde(default)]
    capture_max: Option<u64>,
    #[serde(default)]
    window_state: Option<WindowState>,
    #[serde(default)]
    priority_class: Option<PriorityClass>,
    #[serde(default)]
    affinity_mask: Option<u64>,
    #[serde(default)]
    time_limit_ms: Option<u64>,
    #[serde(default)]
    kill_on_timeout: Option<bool>,
    #[serde(default)]
    run_as_admin: Option<bool>,
    #[serde(default)]
    grace_ms: Option<u64>,
    #[serde(default)]
    signal: Option<Signal>,
    #[serde(default)]
    timeout_ms: Option<u64>,
    #[serde(default)]
    sample_ms: Option<u64>,
    #[serde(default)]
    interval_ms: Option<u64>,
    #[serde(default)]
    dry_run: Option<bool>,
}

// ---- Tool Implementation ----
#[derive(Clone, Debug, Default)]
pub struct ProcessManagerTool;

#[async_trait::async_trait]
impl Tool for ProcessManagerTool {
    fn name(&self) -> &'static str {
        "process_manager"
    }
    fn description(&self) -> &'static str {
        "Advanced process manager with TES/TSG integration"
    }
    fn required_permissions(&self) -> Permission {
        Permission(Permission::EXECUTE | Permission::ADMIN)
    }

    #[instrument]
    async fn run(&self, ctx: &ToolContext, mut payload: Value) -> ToolResult {
        let timer = PROC_LATENCY.start_timer();
        payload = tsg_filter_input(&payload).await?;

        let req: ProcReq = serde_json::from_value(payload)?;
        let (whitelist_pids, capture_max, allowed_ops) = get_config().await?;

        let op = req
            .op
            .as_ref()
            .ok_or_else(|| ProcessError::InvalidInput("Missing op".into()))?;
        let op_str = format!("{:?}", op).to_lowercase();

        if !allowed_ops.is_empty() && !allowed_ops.contains(&op_str) {
            return Err(
                ProcessError::InvalidInput(format!("Operation not allowed: {}", op_str)).into(),
            );
        }

        let result = match op {
            Op::List => pm_list(&req, &whitelist_pids, capture_max).await,
            Op::Inspect => pm_inspect(&req, &whitelist_pids).await,
            // Op::Tree => pm_tree(&req, &whitelist_pids).await, // Tree는 스키마에 없으므로 제외 가능하거나 유지
            Op::Spawn => pm_spawn(&req, &whitelist_pids, ctx, capture_max).await,
            Op::Wait => pm_wait(&req, &whitelist_pids).await,
            Op::Kill => pm_kill(&req, &whitelist_pids).await,
            Op::Close => pm_close(&req, &whitelist_pids).await,
            // Op::SampleUsage => pm_sample_usage(&req, &whitelist_pids).await,
            Op::CpuUsage => pm_cpu_usage(&req, &whitelist_pids).await,
            _ => Ok(json!({"error": "operation not supported via MCP schema subset"})),
        };

        timer.observe_duration();
        result
    }
}

#[instrument]
async fn pm_list(req: &ProcReq, whitelist_pids: &[u32], _capture_max: u64) -> Result<Value> {
    let max_items = req.max_items.unwrap_or(100) as usize;
    let mut system = System::new_all();
    system.refresh_all();

    let processes = system
        .processes()
        .iter()
        .filter(|(pid, _)| whitelist_pids.is_empty() || whitelist_pids.contains(&pid.as_u32()))
        .take(max_items)
        .map(|(pid, proc)| {
            json!({
                "pid": pid.as_u32(),
                "name": proc.name(),
                "parent_pid": proc.parent().map(|p| p.as_u32()).unwrap_or(0),
                "working_set": proc.memory(),
                "private_bytes": proc.virtual_memory(),
            })
        })
        .collect::<Vec<_>>();

    Ok(json!({ "success": true, "processes": processes }))
}

#[instrument]
async fn pm_inspect(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    let mut system = System::new_all();
    system.refresh_processes(ProcessesToUpdate::All, true);

    let proc = system
        .process(Pid::from_u32(pid))
        .ok_or_else(|| ProcessError::NotFound(pid))?;

    Ok(json!({
        "success": true,
        "pid": pid,
        "name": proc.name(),
        "working_set": proc.memory(),
        "private_bytes": proc.virtual_memory(),
        "cpu_time_100ns": proc.cpu_usage() as u64 * 10_000_000,
        "started_100ns": proc.run_time() * 10_000_000,
    }))
}

#[instrument]
async fn pm_tree(_req: &ProcReq, _whitelist_pids: &[u32]) -> Result<Value> {
    Ok(json!({ "success": true, "tree": [] }))
}

#[instrument]
async fn pm_spawn(
    req: &ProcReq,
    _whitelist_pids: &[u32],
    ctx: &ToolContext,
    capture_max: u64,
) -> Result<Value> {
    let cmd = need_str(req.cmd.as_ref(), "cmd")?;
    let cmd = sanitize_cmd(&cmd)?;
    let args = req.args.clone().unwrap_or_default();
    let cwd = req.cwd.as_ref().map(|c| sanitize_path(c)).transpose()?;
    let _env = req.env.clone().unwrap_or_default();
    let _capture = req.capture.unwrap_or(false);
    let _capture_max = req.capture_max.unwrap_or(capture_max);
    let run_as_admin = req.run_as_admin.unwrap_or(false);

    if run_as_admin && !ctx.permissions.has(Permission(Permission::ADMIN)) {
        return Err(ProcessError::InvalidInput("Admin permission required".into()).into());
    }

    #[cfg(windows)]
    {
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;

        let cmd_line = format!("{} {}", cmd, args.join(" "));
        let mut cmd_line: Vec<u16> = OsStr::new(&cmd_line)
            .encode_wide()
            .chain(std::iter::once(0))
            .collect();

        let mut si: STARTUPINFOW = unsafe { std::mem::zeroed() };
        si.cb = std::mem::size_of::<STARTUPINFOW>() as u32;
        let mut pi: PROCESS_INFORMATION = unsafe { std::mem::zeroed() };

        let success = unsafe {
            if let Some(cwd_path) = cwd {
                let cwd_wide: Vec<u16> = OsStr::new(&cwd_path)
                    .encode_wide()
                    .chain(std::iter::once(0))
                    .collect();

                CreateProcessW(
                    None,
                    PWSTR::from_raw(cmd_line.as_mut_ptr()),
                    None,
                    None,
                    false,
                    NORMAL_PRIORITY_CLASS,
                    None,
                    PCWSTR::from_raw(cwd_wide.as_ptr()),
                    &si,
                    &mut pi,
                )
            } else {
                CreateProcessW(
                    None,
                    PWSTR::from_raw(cmd_line.as_mut_ptr()),
                    None,
                    None,
                    false,
                    NORMAL_PRIORITY_CLASS,
                    None,
                    None,
                    &si,
                    &mut pi,
                )
            }
        };

        if success.is_ok() {
            let pid = pi.dwProcessId;
            unsafe {
                let _ = CloseHandle(pi.hThread);
                let _ = CloseHandle(pi.hProcess);
            }
            Ok(json!({ "success": true, "pid": pid }))
        } else {
            Err(
                ProcessError::WinApi(format!("CreateProcessW failed: {:?}", unsafe {
                    GetLastError()
                }))
                .into(),
            )
        }
    }

    #[cfg(not(windows))]
    {
        let mut command = tokio::process::Command::new(&cmd);
        command.args(&args);
        if let Some(cwd) = cwd {
            command.current_dir(cwd);
        }
        command.envs(&env);
        if capture {
            command.stdout(std::process::Stdio::piped());
            command.stderr(std::process::Stdio::piped());
        }

        let child = command
            .spawn()
            .map_err(|e| ProcessError::InvalidInput(format!("Spawn failed: {}", e)))?;
        let pid = child
            .id()
            .ok_or_else(|| ProcessError::InvalidInput("Failed to get PID".into()))?;

        Ok(json!({ "success": true, "pid": pid }))
    }
}

#[instrument]
async fn pm_wait(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    let timeout = Duration::from_millis(req.timeout_ms.unwrap_or(10000));
    let mut system = System::new_all();
    let timeout_at = time::Instant::now() + timeout;

    let status = time::timeout(timeout, async {
        loop {
            system.refresh_processes(ProcessesToUpdate::All, true);
            if time::Instant::now() >= timeout_at {
                return Err(ProcessError::Timeout(pid));
            }

            if system.process(Pid::from_u32(pid)).is_none() {
                break;
            }

            time::sleep(Duration::from_millis(100)).await;
        }
        Ok(0) // sysinfo doesn't provide exit code
    })
    .await??;

    Ok(json!({
        "success": true,
        "pid": pid,
        "exit_code": status,
    }))
}

#[instrument]
async fn pm_kill(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    #[cfg(windows)]
    {
        let handle = unsafe { OpenProcess(PROCESS_TERMINATE, false, pid)? };
        let success = unsafe { TerminateProcess(handle, 1) };
        unsafe {
            let _ = CloseHandle(handle);
        }

        if success.is_ok() {
            Ok(json!({ "success": true, "pid": pid }))
        } else {
            Err(
                ProcessError::WinApi(format!("TerminateProcess failed: {:?}", unsafe {
                    GetLastError()
                }))
                .into(),
            )
        }
    }

    #[cfg(not(windows))]
    {
        let mut system = System::new_all();
        system.refresh_processes(ProcessesToUpdate::All, true);

        let proc = system
            .process(Pid::from_u32(pid))
            .ok_or_else(|| ProcessError::NotFound(pid))?;

        proc.kill_with(SysinfoSignal::Kill)
            .ok_or_else(|| ProcessError::InvalidInput("Failed to kill process".into()))?;

        Ok(json!({ "success": true, "pid": pid }))
    }
}

#[instrument]
async fn pm_close(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    #[cfg(windows)]
    {
        let success = unsafe { PostThreadMessageW(pid, WM_CLOSE, WPARAM(0), LPARAM(0)) };

        if success.is_ok() {
            Ok(json!({ "success": true, "pid": pid }))
        } else {
            Err(
                ProcessError::WinApi(format!("PostThreadMessageW failed: {:?}", unsafe {
                    GetLastError()
                }))
                .into(),
            )
        }
    }

    #[cfg(not(windows))]
    {
        let mut system = System::new_all();
        system.refresh_processes(ProcessesToUpdate::All, true);

        let proc = system
            .process(Pid::from_u32(pid))
            .ok_or_else(|| ProcessError::NotFound(pid))?;

        proc.kill_with(SysinfoSignal::Term)
            .ok_or_else(|| ProcessError::InvalidInput("Failed to terminate process".into()))?;

        Ok(json!({ "success": true, "pid": pid }))
    }
}

#[instrument]
async fn pm_sample_usage(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    let mut system = System::new_all();
    system.refresh_processes(ProcessesToUpdate::All, true);

    let proc = system
        .process(Pid::from_u32(pid))
        .ok_or_else(|| ProcessError::NotFound(pid))?;

    Ok(json!({
        "success": true,
        "pid": pid,
        "working_set": proc.memory(),
        "private_bytes": proc.virtual_memory(),
        "cpu_time_100ns": proc.cpu_usage() as u64 * 10_000_000,
        "started_100ns": proc.run_time() * 10_000_000,
    }))
}

#[instrument]
async fn pm_cpu_usage(req: &ProcReq, whitelist_pids: &[u32]) -> Result<Value> {
    let pid = req
        .pid
        .ok_or_else(|| ProcessError::InvalidInput("Missing pid".into()))?;
    if !whitelist_pids.is_empty() && !whitelist_pids.contains(&pid) {
        return Err(ProcessError::AccessDenied(pid).into());
    }

    let interval = req.interval_ms.unwrap_or(1000);
    let mut system = System::new_all();

    system.refresh_processes(ProcessesToUpdate::All, true);
    let sample1 = pm_sample_usage(
        &ProcReq {
            pid: Some(pid),
            ..Default::default()
        },
        whitelist_pids,
    )
    .await?;

    time::sleep(Duration::from_millis(interval)).await;

    system.refresh_processes(ProcessesToUpdate::All, true);
    let sample2 = pm_sample_usage(
        &ProcReq {
            pid: Some(pid),
            ..Default::default()
        },
        whitelist_pids,
    )
    .await?;

    let cpu1 = sample1
        .get("cpu_time_100ns")
        .and_then(|v| v.as_u64())
        .unwrap_or(0);
    let cpu2 = sample2
        .get("cpu_time_100ns")
        .and_then(|v| v.as_u64())
        .unwrap_or(0);
    let cpu_delta = cpu2.saturating_sub(cpu1) as f64;
    let time_delta = (interval as f64) * 10_000.0;
    let core_count = System::physical_core_count()
        .map(|c| c as f64)
        .unwrap_or(1.0);
    let cpu_percent = (cpu_delta / time_delta) * 100.0 / core_count;

    Ok(json!({
        "success": true,
        "pid": pid,
        "cpu_percent": format!("{:.2}", cpu_percent),
        "interval_ms": interval,
        "core_count": core_count,
        "working_set": sample2.get("working_set"),
        "private_bytes": sample2.get("private_bytes"),
    }))
}

//
// ---- Helpers ----
//
fn need_str(v: Option<&String>, key: &str) -> Result<String> {
    let s = v.ok_or_else(|| ProcessError::InvalidInput(format!("Missing field: {}", key)))?;
    if s.trim().is_empty() {
        return Err(ProcessError::InvalidInput(format!("Empty field: {}", key)).into());
    }
    Ok(s.clone())
}

fn sanitize_cmd(cmd: &str) -> Result<String> {
    if cmd.contains('|') || cmd.contains('&') || cmd.contains(';') || cmd.contains('`') {
        Err(ProcessError::InvalidInput("Command contains invalid characters".into()).into())
    } else {
        Ok(cmd.to_string())
    }
}

fn sanitize_path(path: &str) -> Result<String> {
    let path = PathBuf::from(path);
    let abs = path
        .canonicalize()
        .map_err(|e| ProcessError::InvalidInput(e.to_string()))?;
    Ok(abs.to_string_lossy().to_string())
}
