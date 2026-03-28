# AI Desktop Detailed Manual

## AI Desktop Plan

- Systematize the Desktop so that AI can use almost all functions of the Desktop as tools, effectively making the Desktop itself a tool for the AI.

## AI Desktop Source Structure

```
AI_Desktop/
├── Cargo.toml
└── src/
    ├── main.rs            (Main Application)
    ├── core.rs            (Core Abstraction: Tool, ToolRegistry, Security)
    └── ai_tools/
        ├── mod.rs         (Export all tool modules)
        ├── file_manager_tool.rs
        ├── network_api_tool.rs
        ├── process_manager_tool.rs
        ├── system_info_tool.rs
        ├── web_search_tool.rs
        └── ...
```

# 🚀 AI Desktop (Rust Edition) – Analysis & Description

## 🎯 Project Overview

AI Desktop is a system embodying the vision of **"Providing my entire computer as a tool for AI."**
A lightweight, high-speed server written in Rust runs in the background, allowing AI agents to control the following via **MCP (Model Context Protocol)**.

| Category | Example Features |
|---|---|
| **File/Folder** | Create, delete, move, read files |
| **System** | Process control, system info monitoring |
| **Network** | HTTP requests, web search |
| **Development** | Auto-tool generation stub |

---

## 🏗️ Architecture

```text
┌-------------┐
│  MCP Client │ (e.g., Claude Desktop, IDE)
└-----┬-------┘
      │ JSON-RPC 2.0 (Stdio)
┌-----▼-------┐   tokio   ┌-------------┐
│ MCP Server  │----------▶│  ToolRegistry│--┐
└-----┬-------┘           └-----┬-------┘  │
      │                         │         Active Tools
      ▼                         ▼
SecurityManager            Active Tools
(Permission/Risk Check)    (File, Net, Process...)
```

---

## 🔐 Security Model

1. **Permission**  
   Apply Least Privilege Principle with combinations of `READ | WRITE | EXEC | NET | SYSTEM`.
2. **Security Context**  
   Manage actor and granted permissions.

---

## 🧰 Tool Addition Guide

Just implement the `core::Tool` trait to register a new tool immediately.

```rust
#[async_trait]
impl Tool for MyTool {
    fn name(&self) -> &'static str { "my_tool" }
    fn description(&self) -> &'static str { "..." }
    fn required_permissions(&self) -> Permission { Permission::READ }
    fn input_schema(&self) -> Value { json!({...}) }
    async fn run(&self, ctx: &ToolContext, payload: Value) -> Result<Value> {
        // ... logic
        Ok(json!({"status": "ok"}))
    }
}
```

In `ai_desktop_mcp.rs`, register it:
`registry.register(MyTool::default());`

---

## 🧪 How to Run

```bash
cargo run --release --bin ai_desktop_mcp
# The server will listen on Stdio for MCP connections.
```

---

## One-Line Summary
>
> **"AI Desktop is a 'Toolbox for AI' that allows full control of my PC via standard MCP protocol."**
