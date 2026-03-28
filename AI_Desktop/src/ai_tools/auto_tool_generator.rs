//! AI Desktop - Auto Tool Generator (fixed)

use anyhow::{anyhow, Result};
use serde_json::{json, Value};
use std::fs;
use std::path::Path;

use crate::core::{Permission, Tool, ToolContext};

#[derive(Default)]
pub struct AutoToolGenerator;

impl AutoToolGenerator {
    async fn generate_python_tool(&self, name: &str, payload: &Value) -> Result<Value> {
        let dyn_dir = Path::new("dynamic_tools");
        fs::create_dir_all(dyn_dir)?;

        let desc = payload
            .get("description")
            .and_then(|v| v.as_str())
            .unwrap_or("Auto generated tool");
        let script_content = payload
            .get("script_content")
            .and_then(|v| v.as_str())
            .unwrap_or(
                "import sys, json\nprint(json.dumps({'ok': True, 'msg': 'Hello from Python'}))",
            );

        let schema = payload.get("input_schema").cloned().unwrap_or(json!({
            "type": "object", "properties": {}
        }));

        // 1. 스크립트 파일 생성
        let script_file = dyn_dir.join(format!("{}.py", name));
        fs::write(&script_file, script_content)?;

        // 2. 메타데이터(Config) 파일 생성
        let config_file = dyn_dir.join(format!("{}.json", name));
        let config_json = json!({
            "name": name,
            "description": desc,
            "script_path": format!("{}.py", name),
            "interpreter": "python",
            "schema": schema
        });
        fs::write(&config_file, serde_json::to_string_pretty(&config_json)?)?;

        Ok(json!({
            "ok": true,
            "msg": "Dynamic tool created. Use 'tools/refresh' to load it.",
            "path": config_file.to_string_lossy()
        }))
    }

    async fn generate_rust_tool(&self, tool_name: &str) -> Result<Value> {
        // Validate and normalize identifiers
        let snake = to_snake_case(tool_name);
        let pascal = to_pascal_case(tool_name);
        if !valid_ident(&snake) || !valid_ident(&pascal) {
            return Err(anyhow!("invalid tool_name"));
        }

        let src_dir = Path::new("src/ai_tools");
        let file_path = src_dir.join(format!("{}_tool.rs", snake));

        // Template for new tool
        let template = format!(
            r#"//! AI Desktop - {pascal}Tool (auto-generated)

use anyhow::Result;
use serde_json::{{json, Value}};

use crate::core::{{Permission, Tool, ToolContext}};

#[derive(Default)]
pub struct {pascal}Tool;

#[async_trait::async_trait]
impl Tool for {pascal}Tool {{
    fn name(&self) -> &'static str {{ "{snake}" }}
    fn description(&self) -> &'static str {{ "Auto-generated tool: {pascal}" }}
    fn required_permissions(&self) -> Permission {{ Permission(0) }}

    async fn run(&self, _ctx: &ToolContext, payload: Value) -> Result<Value> {{
        Ok(json!({{ "ok": true, "tool": "{snake}", "payload": payload }}))
    }}
}}
"#,
            pascal = pascal,
            snake = snake
        );

        write_file(&file_path, &template)?;
        patch_mod_rs(&snake)?;
        patch_main_rs(&pascal)?;

        Ok(json!({ "ok": true, "generated": file_path.to_string_lossy() }))
    }
}

#[async_trait::async_trait]
impl Tool for AutoToolGenerator {
    fn name(&self) -> &'static str {
        "auto_tool_generator"
    }

    fn description(&self) -> &'static str {
        "Generates new AI tools. Supports 'python' (dynamic) and 'rust' (static)."
    }

    fn required_permissions(&self) -> Permission {
        Permission(Permission::WRITE | Permission::EXECUTE)
    }

    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "lang": {
                    "type": "string",
                    "enum": ["python", "rust"],
                    "description": "Target language"
                },
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool (snake_case)"
                },
                "description": {
                    "type": "string",
                    "description": "Tool description"
                },
                "script_content": {
                    "type": "string",
                    "description": "Python script code (for python lang)"
                },
                "input_schema": {
                    "type": "object",
                    "description": "JSON Schema for inputs (for python lang)"
                }
            },
            "required": ["tool_name"]
        })
    }

    async fn run(&self, _ctx: &ToolContext, payload: Value) -> Result<Value> {
        let lang = payload
            .get("lang")
            .and_then(|v| v.as_str())
            .unwrap_or("python");
        let tool_name = payload
            .get("tool_name")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow!("missing tool_name"))?;

        // 식별자 검증
        if tool_name.contains("..") || tool_name.contains("/") || tool_name.contains("\\") {
            return Err(anyhow!("Invalid tool name"));
        }

        if lang == "python" {
            self.generate_python_tool(tool_name, &payload).await
        } else {
            self.generate_rust_tool(tool_name).await
        }
    }
}

/* ---------------- Helpers ---------------- */

fn to_snake_case(s: &str) -> String {
    let mut out = String::new();
    for (i, c) in s.chars().enumerate() {
        if c.is_uppercase() {
            if i > 0 {
                out.push('_');
            }
            for lower in c.to_lowercase() {
                out.push(lower);
            }
        } else {
            out.push(c);
        }
    }
    out
}

fn to_pascal_case(s: &str) -> String {
    let mut out = String::new();
    let mut capitalize = true;
    for c in s.chars() {
        if c == '_' || c == '-' {
            capitalize = true;
            continue;
        }
        if capitalize {
            for upper in c.to_uppercase() {
                out.push(upper);
            }
            capitalize = false;
        } else {
            out.push(c);
        }
    }
    out
}

fn valid_ident(s: &str) -> bool {
    !s.is_empty() && s.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
}

fn write_file(path: &Path, content: &str) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, content)?;
    Ok(())
}

fn patch_mod_rs(snake: &str) -> Result<()> {
    let mod_file = Path::new("src/ai_tools/mod.rs");
    let mut content = fs::read_to_string(mod_file).unwrap_or_default();
    let decl = format!("pub mod {}_tool;", snake);
    if !content.contains(&decl) {
        content.push_str("\n");
        content.push_str(&decl);
        fs::write(mod_file, content)?;
    }
    Ok(())
}

fn patch_main_rs(pascal: &str) -> Result<()> {
    let main_file = Path::new("src/main.rs");
    let mut content = fs::read_to_string(main_file).unwrap_or_default();
    let reg = format!("registry.register(Box::new({}Tool::default()));", pascal);
    if !content.contains(&reg) {
        content.push_str("\n");
        content.push_str(&reg);
        fs::write(main_file, content)?;
    }
    Ok(())
}
