# AI Desktop MCP Gantt Design & Action Plan

This document outlines the architectural vision and roadmap for the AI Desktop MCP Server.

-----

### 🌲 AI Desktop MCP System - Architecture

```gantree
AI_Desktop_MCP_Server // AI OS based Rust MCP Integration Server
    Core_Infrastructure // Server operation & communication core logic
        Stdio_Transport // Standard Input/Output based communication channel (Done)
        JsonRpc_Handler // JSON-RPC 2.0 message parsing & error handling (Done)
    
    Security_Architecture // TSG(Trust & Security Gateway) implementation
        Permission_Manager // Tool-specific execution permission (R/W/X) verification (Done)
        Audit_Logger // Recording all AI actions & I/O (Done)

    MCP_Capability_Layer // MCP protocol standard feature implementation
        Tool_Provider // Providing Tool Call features (Done)
            Tool_Registry // Tool registration & metadata management (Done)
            Tool_Groups // Logical grouping of tools

// -------------------------------------------------------
// [Decomposition] Tool_Groups Details
// -------------------------------------------------------

Tool_Groups // Collection of tools by function
    OS_Control_Group // OS control tools
        Process_Manager_Tool // Process list/kill/spawn (Done)
        System_Info_Tool // Hardware specs & status query (Done)

    FileSystem_Group // File & data processing tools
        File_Manager_Tool // File navigation/CRUD (Done)
    
    Network_Group // External communication tools
        Network_Api_Tool // HTTP/REST requests (Done)
        Web_Search_Tool // Google/Bing search result parsing (Done)
    
    Dev_Ops_Group // Development & maintenance tools
        Auto_Tool_Generator // Auto-generation of new tool code (Done)
```

-----

### 🚀 Roadmap & Future Expansion

The following features are designed but not yet implemented (Legacy/Planned):

1. **Extended OS Control**: Windows Registry, Clipboard, System Monitor, Window Manager.
2. **Extended FileSystem**: Zip compression, PDF parsing, Database tools.
3. **Perception & Action**: Screen Capture, Audio I/O, Keyboard/Mouse simulation.
4. **DevOps**: Git integration, Terminal execution.
5. **Resources & Prompts**: Real-time log streaming, context injection.
