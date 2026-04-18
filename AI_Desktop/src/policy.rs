use crate::core::{PermissionSet, ToolContext};
use anyhow::{bail, Result};
use serde_json::Value;
use std::collections::HashMap;

const MEMBERS: &[&str] = &[
    "Aion",
    "ClNeo",
    "NAEL",
    "Signalion",
    "Synerion",
    "Vera",
    "Yeon",
    "Sevalon",
];

#[derive(Clone, Default)]
pub struct PolicyEngine {
    allowed_actions: HashMap<&'static str, &'static [&'static str]>,
}

impl PolicyEngine {
    pub fn new() -> Self {
        let mut allowed_actions = HashMap::new();
        allowed_actions.insert("seaai_mailbox", &["read_inbox", "send", "mark_read", "list_read"][..]);
        allowed_actions.insert("seaai_echo", &["read", "publish", "list"][..]);
        allowed_actions.insert("seaai_member_state", &["read_state", "list_members", "discover"][..]);
        allowed_actions.insert("seaai_hub", &["status", "read_log", "read_protocol"][..]);
        allowed_actions.insert("seaai_approval", &["request", "list", "get", "respond"][..]);
        allowed_actions.insert("seaai_audit_query", &["list_recent", "by_actor", "by_tool"][..]);
        allowed_actions.insert("seaai_browser", &["doctor", "inspect", "extract_title", "screenshot", "launch", "list_sessions", "close_session", "status", "start", "stop", "profiles", "tabs", "open", "focus", "navigate", "snapshot", "act", "upload", "dialog"][..]);
        Self { allowed_actions }
    }

    pub fn authorize(
        &self,
        tool_name: &str,
        required: PermissionSet,
        ctx: &ToolContext,
        args: &Value,
    ) -> Result<()> {
        if !ctx.permissions.has_all(required) {
            bail!("permission denied for tool {}", tool_name);
        }

        let allowed = self
            .allowed_actions
            .get(tool_name)
            .ok_or_else(|| anyhow::anyhow!("unknown tool blocked: {}", tool_name))?;

        let action = args
            .get("action")
            .and_then(Value::as_str)
            .ok_or_else(|| anyhow::anyhow!("action is required"))?;

        if !allowed.contains(&action) {
            bail!("action blocked: {}.{}", tool_name, action);
        }

        self.validate_member_fields(args)?;
        self.validate_payload(tool_name, action, args, ctx)?;
        Ok(())
    }

    fn validate_member_fields(&self, args: &Value) -> Result<()> {
        for field in ["member", "to", "from", "requester", "responder"] {
            if let Some(value) = args.get(field).and_then(Value::as_str) {
                if !MEMBERS.contains(&value) {
                    bail!("unknown member in field {}: {}", field, value);
                }
            }
        }
        Ok(())
    }

    fn validate_payload(&self, tool_name: &str, action: &str, args: &Value, ctx: &ToolContext) -> Result<()> {
        if tool_name == "seaai_mailbox" && action == "send" {
            if !ctx.permissions.has_all(PermissionSet(PermissionSet::WRITE)) {
                bail!("mailbox send requires write permission");
            }
            let content = args.get("content").and_then(Value::as_str).unwrap_or("");
            if content.trim().is_empty() {
                bail!("mailbox send requires content");
            }
            if content.len() > 12000 {
                bail!("mailbox content too large");
            }
        }

        if tool_name == "seaai_echo" && action == "publish" {
            if !ctx.permissions.has_all(PermissionSet(PermissionSet::WRITE)) {
                bail!("echo publish requires write permission");
            }
            let message = args.get("message").and_then(Value::as_str).unwrap_or("");
            if message.trim().is_empty() {
                bail!("echo publish requires message");
            }
        }

        if tool_name == "seaai_approval" && action == "request" {
            if !ctx.permissions.has_all(PermissionSet(PermissionSet::WRITE | PermissionSet::APPROVE)) {
                bail!("approval request requires write+approve permission");
            }
        }

        if tool_name == "seaai_approval" && action == "respond" {
            if !ctx.permissions.has_all(PermissionSet(PermissionSet::APPROVE)) {
                bail!("approval response requires approve permission");
            }
            if ctx.approval_token.is_none() {
                bail!("approval response requires approval_token");
            }
        }

        if tool_name == "seaai_browser" {
            let url = args.get("url").and_then(Value::as_str).unwrap_or("");
            if matches!(action, "inspect" | "extract_title" | "screenshot" | "launch" | "open" | "navigate" | "snapshot") && url.trim().is_empty() {
                bail!("browser action requires url");
            }
            if matches!(action, "close_session" | "stop" | "focus")
                && args.get("session_id").and_then(Value::as_str).unwrap_or("").trim().is_empty()
            {
                bail!("browser action {} requires session_id", action);
            }
            if matches!(action, "screenshot" | "launch" | "close_session" | "start" | "stop" | "open" | "focus" | "navigate" | "act" | "upload" | "dialog")
                && !ctx.permissions.has_all(PermissionSet(PermissionSet::WRITE))
            {
                bail!("browser action {} requires write permission", action);
            }
        }

        Ok(())
    }
}
