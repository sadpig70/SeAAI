//! AI Desktop - Network API Tool (Final MVP)

use anyhow::{anyhow, Context, Result};
use serde_json::{json, Value};
use std::time::Duration;

use crate::core::{Permission, Tool, ToolContext};

#[derive(Default)]
pub struct NetworkApiTool;

#[async_trait::async_trait]
impl Tool for NetworkApiTool {
    fn name(&self) -> &'static str {
        "network_api"
    }
    fn description(&self) -> &'static str {
        "Network tools: HTTP requests, Ping, DNS query, TCP check."
    }
    fn required_permissions(&self) -> Permission {
        Permission(0)
    } // 네트워크는 별도 권한 체크 로직 권장

    // [NEW] CTO 검수 완료된 스키마
    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "op": {
                    "type": "string",
                    "enum": ["http_request", "http_head", "http_download", "ping", "dns_query", "tcp_request", "network_diagnostics"],
                    "description": "Operation type. 'http_request' needs 'url'."
                },
                "url": { "type": "string", "description": "Target URL (http/https)" },
                "method": { "type": "string", "description": "HTTP Method (GET, POST, etc). Default: GET" },
                "body": { "type": "string", "description": "Request body (for POST/PUT)" },
                "headers": { "type": "object", "description": "HTTP Headers key-value pairs" },
                "target": { "type": "string", "description": "Target host/IP for ping/diagnostics" },
                "dns_name": { "type": "string", "description": "Domain name for DNS query" },
                "host": { "type": "string", "description": "TCP host" },
                "port": { "type": "integer", "description": "TCP port" }
            },
            "required": ["op"]
        })
    }

    async fn run(&self, _ctx: &ToolContext, payload: Value) -> Result<Value> {
        // ... (기존 run 구현 로직 그대로 유지) ...
        // payload["op"] 분기 처리 로직
        let op = payload
            .get("op")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow!("missing 'op'"))?;
        match op {
            "http_request" => http_request(&payload).await,
            "http_head" => http_head(&payload).await,
            "http_download" => http_download(&payload).await,
            "tcp_request" => tcp_request(&payload).await,
            "dns_query" => dns_query(&payload).await,
            "ping" => ping_mvp(&payload).await,
            "network_diagnostics" => network_diagnostics(&payload).await,
            // 윈도우 전용 기능은 MVP 단계에서 선택적으로 포함
            "win_http_request" => win_http_request_mvp(&payload).await,
            "windows_auth" => windows_auth_mvp().await,
            "firewall_control" => firewall_control_mvp(&payload).await,
            other => Ok(json!({ "ok": false, "error": format!("unknown op: {}", other) })),
        }
    }
}

/* -------------------------- HTTP -------------------------- */

async fn http_client_from(payload: &Value) -> Result<reqwest::Client> {
    let timeout_ms = payload
        .get("timeout_ms")
        .and_then(|v| v.as_u64())
        .unwrap_or(30000);
    Ok(reqwest::Client::builder()
        .timeout(Duration::from_millis(timeout_ms))
        .build()?)
}

async fn http_request(payload: &Value) -> Result<Value> {
    use reqwest::header::{HeaderMap, HeaderName, HeaderValue};

    let client = http_client_from(payload).await?;
    let url = payload
        .get("url")
        .and_then(|v| v.as_str())
        .context("missing 'url'")?;
    let method = payload
        .get("method")
        .and_then(|v| v.as_str())
        .unwrap_or("GET");
    let headers = payload.get("headers").cloned().unwrap_or(json!({}));
    let body = payload.get("body");

    let mut req = client.request(reqwest::Method::from_bytes(method.as_bytes())?, url);

    if let Some(obj) = headers.as_object() {
        let mut hm = HeaderMap::new();
        for (k, v) in obj {
            if let Some(s) = v.as_str() {
                if let (Ok(name), Ok(val)) = (
                    HeaderName::from_bytes(k.as_bytes()),
                    HeaderValue::from_str(s),
                ) {
                    hm.insert(name, val);
                }
            }
        }
        req = req.headers(hm);
    }

    if let Some(b) = body {
        req = if let Some(s) = b.as_str() {
            req.body(s.to_owned())
        } else {
            req.json(b)
        };
    }

    let resp = req.send().await?;
    let status = resp.status().as_u16();
    let headers: serde_json::Map<String, Value> = resp
        .headers()
        .iter()
        .map(|(k, v)| {
            (
                k.to_string(),
                Value::String(v.to_str().unwrap_or("").to_string()),
            )
        })
        .collect();
    let text = resp.text().await.unwrap_or_default();

    Ok(
        json!({ "ok": true, "status": status, "headers": headers, "body": text, "content_length": text.len() }),
    )
}

async fn http_head(payload: &Value) -> Result<Value> {
    let client = http_client_from(payload).await?;
    let url = payload
        .get("url")
        .and_then(|v| v.as_str())
        .context("missing 'url'")?;
    let resp = client.head(url).send().await?;
    let status = resp.status().as_u16();
    let headers: serde_json::Map<String, Value> = resp
        .headers()
        .iter()
        .map(|(k, v)| {
            (
                k.to_string(),
                Value::String(v.to_str().unwrap_or("").to_string()),
            )
        })
        .collect();
    Ok(json!({ "ok": true, "status": status, "headers": headers }))
}

async fn http_download(payload: &Value) -> Result<Value> {
    use tokio::fs;
    let client = http_client_from(payload).await?;
    let url = payload
        .get("url")
        .and_then(|v| v.as_str())
        .context("missing 'url'")?;
    let save_path = payload
        .get("save_path")
        .and_then(|v| v.as_str())
        .context("missing 'save_path'")?;
    let bytes = client.get(url).send().await?.bytes().await?;
    fs::write(save_path, &bytes).await?;
    Ok(json!({ "ok": true, "saved_path": save_path, "file_size": bytes.len() }))
}

/* -------------------------- TCP -------------------------- */

async fn tcp_request(payload: &Value) -> Result<Value> {
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::TcpStream;

    let host = payload
        .get("host")
        .and_then(|v| v.as_str())
        .context("missing 'host'")?;
    let port = payload
        .get("port")
        .and_then(|v| v.as_u64())
        .context("missing 'port'")? as u16;
    let data = payload.get("data").and_then(|v| v.as_str()).unwrap_or("");
    let timeout_ms = payload
        .get("timeout_ms")
        .and_then(|v| v.as_u64())
        .unwrap_or(5000);

    let addr = format!("{}:{}", host, port);
    let stream = tokio::time::timeout(Duration::from_millis(timeout_ms), TcpStream::connect(&addr))
        .await
        .map_err(|_| anyhow!("tcp connect timeout"))??;

    let mut stream = stream;
    if !data.is_empty() {
        stream.write_all(data.as_bytes()).await?;
    }
    stream.flush().await?;

    let mut buf = vec![0u8; 4096];
    let n = tokio::time::timeout(Duration::from_millis(timeout_ms), stream.read(&mut buf))
        .await
        .map_err(|_| anyhow!("tcp read timeout"))??;

    let got = String::from_utf8_lossy(&buf[..n]).to_string();
    Ok(
        json!({ "ok": true, "connected": true, "host": host, "port": port, "read_bytes": n, "data": got }),
    )
}

/* -------------------------- DNS (feature-gated) -------------------------- */

async fn dns_query(payload: &Value) -> Result<Value> {
    let name = payload
        .get("dns_name")
        .and_then(|v| v.as_str())
        .context("missing 'dns_name'")?;
    let typ = payload
        .get("dns_type")
        .and_then(|v| v.as_str())
        .unwrap_or("A");

    #[cfg(feature = "network-support")]
    {
        use trust_dns_resolver::config::{ResolverConfig, ResolverOpts};
        use trust_dns_resolver::TokioAsyncResolver;

        let resolver =
            TokioAsyncResolver::tokio(ResolverConfig::default(), ResolverOpts::default());
        match typ.to_uppercase().as_str() {
            "A" => {
                let resp = resolver.ipv4_lookup(name).await?;
                let addrs: Vec<String> = resp.iter().map(|ip| ip.to_string()).collect();
                Ok(json!({ "ok": true, "a_records": addrs }))
            }
            "AAAA" => {
                let resp = resolver.ipv6_lookup(name).await?;
                let addrs: Vec<String> = resp.iter().map(|ip| ip.to_string()).collect();
                Ok(json!({ "ok": true, "aaaa_records": addrs }))
            }
            _ => {
                Ok(json!({ "ok": false, "error": "unsupported dns_type for MVP (use A or AAAA)" }))
            }
        }
    }

    #[cfg(not(feature = "network-support"))]
    {
        let _ = (name, typ);
        Ok(
            json!({ "ok": false, "error": "network-support feature disabled", "hint": "Enable with: cargo build --features network-support" }),
        )
    }
}

/* -------------------------- Ping (MVP) -------------------------- */

async fn ping_mvp(payload: &Value) -> Result<Value> {
    let target = payload
        .get("target")
        .and_then(|v| v.as_str())
        .context("missing 'target'")?;
    let common_ports = [80u16, 443u16];
    for &p in &common_ports {
        if try_tcp(target, p, 1000).await {
            return Ok(
                json!({ "ok": true, "target": target, "port": p, "reachable": true, "method": "tcp-probe" }),
            );
        }
    }
    Ok(json!({ "ok": true, "target": target, "reachable": false, "method": "tcp-probe" }))
}

async fn try_tcp(host: &str, port: u16, timeout_ms: u64) -> bool {
    use tokio::net::TcpStream;
    let addr = format!("{}:{}", host, port);
    tokio::time::timeout(Duration::from_millis(timeout_ms), TcpStream::connect(addr))
        .await
        .is_ok()
}

/* -------------------------- Diagnostics (MVP) -------------------------- */

async fn network_diagnostics(payload: &Value) -> Result<Value> {
    let diag = payload
        .get("diagnostic_type")
        .and_then(|v| v.as_str())
        .unwrap_or("port_scan");
    let target = payload
        .get("target")
        .and_then(|v| v.as_str())
        .unwrap_or("127.0.0.1");

    if diag == "port_scan" {
        let ports = payload
            .get("ports")
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|x| x.as_u64().map(|u| u as u16))
                    .collect::<Vec<_>>()
            })
            .unwrap_or_else(|| vec![22, 80, 443, 3389, 8080]);

        let mut open = Vec::new();
        for p in ports {
            if try_tcp(target, p, 500).await {
                open.push(p);
            }
        }
        return Ok(
            json!({ "ok": true, "target": target, "open_ports": open, "scan_type": "common_ports" }),
        );
    }

    Ok(json!({ "ok": false, "error": format!("unsupported diagnostic_type: {}", diag) }))
}

/* -------------------------- Windows-only MVP ops -------------------------- */

async fn win_http_request_mvp(payload: &Value) -> Result<Value> {
    #[cfg(windows)]
    {
        let mut p = payload.clone();
        let obj = p.as_object_mut().unwrap();
        obj.insert(
            "method".into(),
            obj.get("method").cloned().unwrap_or(json!("GET")),
        );
        let out = http_request(&p).await?;
        let mut m = out.as_object().cloned().unwrap_or_default();
        m.insert("platform".into(), json!("windows"));
        m.insert("via".into(), json!("reqwest-mvp"));
        Ok(Value::Object(m))
    }
    #[cfg(not(windows))]
    {
        Ok(json!({ "ok": false, "error": "windows-only op", "platform": "non-windows" }))
    }
}

async fn windows_auth_mvp() -> Result<Value> {
    #[cfg(windows)]
    {
        use std::env;
        let user = env::var("USERNAME").unwrap_or_default();
        let domain = env::var("USERDOMAIN").unwrap_or_default();
        Ok(
            json!({ "ok": true, "auth_type": "windows_integrated_mvp", "current_user": format!("{}\\{}", domain, user) }),
        )
    }
    #[cfg(not(windows))]
    {
        Ok(json!({ "ok": false, "error": "windows-only op" }))
    }
}

async fn firewall_control_mvp(payload: &Value) -> Result<Value> {
    #[cfg(windows)]
    {
        let target = payload
            .get("target")
            .and_then(|v| v.as_str())
            .unwrap_or("list_rules");
        Ok(
            json!({ "ok": true, "action": target, "platform": "windows", "note": "MVP: use 'netsh advfirewall' or Firewall API in next phase" }),
        )
    }
    #[cfg(not(windows))]
    {
        Ok(json!({ "ok": false, "error": "windows-only op" }))
    }
}
