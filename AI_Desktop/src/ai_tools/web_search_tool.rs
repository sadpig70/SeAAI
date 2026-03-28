//! src/ai_tools/web_search_tool.rs
use std::{
    env, fs,
    io::Write,
    path::{Path, PathBuf},
    time::{Duration, SystemTime},
};

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha1::{Digest, Sha1};

#[derive(thiserror::Error, Debug)]
pub enum WebSearchError {
    #[error("invalid argument: {0}")]
    InvalidArg(String),
    #[error("http error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("json error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("provider error: {0}")]
    Provider(String),
}
pub type WebSearchResult<T> = Result<T, WebSearchError>;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchOptions {
    pub top: usize,                // 1~50 권장
    pub market: Option<String>,    // 예: "ko-KR"
    pub freshness: Option<String>, // "Day" | "Week" | "Month"
    pub safe: Option<String>,      // "Off" | "Moderate" | "Strict"
    pub timeout_ms: u64,           // HTTP 타임아웃
    pub cache_ttl_sec: u64,        // 캐시 TTL(0이면 미사용)
}
impl Default for SearchOptions {
    fn default() -> Self {
        Self {
            top: 10,
            market: Some("ko-KR".into()),
            freshness: None,
            safe: Some("Moderate".into()),
            timeout_ms: 8_000,
            cache_ttl_sec: 600,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub title: String,
    pub url: String,
    pub snippet: String,
    pub provider: String,
    pub source_rank: Option<usize>,
}

#[derive(Debug, Clone)]
pub enum Provider {
    Bing,
    DuckDuckGo,
}

#[derive(Debug, Clone)]
pub struct WebSearchTool {
    provider: Provider,
    client: reqwest::Client,
    bing_key: Option<String>,
    bing_endpoint: String,
    cache_dir: Option<PathBuf>,
}

impl WebSearchTool {
    /// 환경변수:
    /// - BING_SEARCH_KEY (있으면 Bing, 없으면 DuckDuckGo)
    /// - BING_SEARCH_ENDPOINT (기본: https://api.bing.microsoft.com/v7.0/search)
    /// - AI_DESKTOP_CACHE (옵션: 캐시 루트 경로)
    /// - HTTP(S)_PROXY 자동 지원(reqwest)
    pub fn new() -> WebSearchResult<Self> {
        let bing_key = env::var("BING_SEARCH_KEY").ok();
        let provider = if bing_key.is_some() {
            Provider::Bing
        } else {
            Provider::DuckDuckGo
        };

        let client = reqwest::Client::builder()
            .user_agent("AI-Desktop-WebSearch/1.0")
            .timeout(Duration::from_millis(8_000))
            .gzip(true)
            .brotli(true)
            .deflate(true)
            .use_rustls_tls()
            .build()?;

        let endpoint = env::var("BING_SEARCH_ENDPOINT")
            .unwrap_or_else(|_| "https://api.bing.microsoft.com/v7.0/search".to_string());

        let cache_dir = determine_cache_dir()?;

        Ok(Self {
            provider,
            client,
            bing_key,
            bing_endpoint: endpoint,
            cache_dir,
        })
    }

    /// 검색 실행
    pub async fn search(
        &self,
        query: &str,
        mut opt: SearchOptions,
    ) -> WebSearchResult<Vec<SearchResult>> {
        if query.trim().is_empty() {
            return Err(WebSearchError::InvalidArg("query is empty".into()));
        }
        if opt.top == 0 || opt.top > 50 {
            opt.top = 10;
        }

        // 캐시 로드
        if opt.cache_ttl_sec > 0 {
            if let Some(hit) = self.try_cache_load(query, &opt)? {
                return Ok(hit);
            }
        }

        let results = match self.provider {
            Provider::Bing => self.search_bing(query, &opt).await,
            Provider::DuckDuckGo => self.search_duckduckgo(query, &opt).await,
        }?;

        // 캐시 저장
        if opt.cache_ttl_sec > 0 {
            if let Some(dir) = &self.cache_dir {
                let _ = save_cache(dir, query, &results);
            }
        }

        Ok(results)
    }

    /// JSON 포맷 결과
    #[allow(dead_code)]
    pub async fn search_json(&self, query: &str, opt: SearchOptions) -> WebSearchResult<String> {
        let res = self.search(query, opt).await?;
        Ok(serde_json::to_string_pretty(&res)?)
    }

    // ---------------- Provider 구현 ----------------

    async fn search_bing(
        &self,
        query: &str,
        opt: &SearchOptions,
    ) -> WebSearchResult<Vec<SearchResult>> {
        let key = self
            .bing_key
            .as_ref()
            .ok_or_else(|| WebSearchError::Provider("BING_SEARCH_KEY not set".into()))?;

        let mut req = self
            .client
            .get(&self.bing_endpoint)
            .query(&[("q", query), ("count", &opt.top.to_string())])
            .header("Ocp-Apim-Subscription-Key", key);

        if let Some(m) = &opt.market {
            req = req.query(&[("mkt", m)]);
        }
        if let Some(f) = &opt.freshness {
            req = req.query(&[("freshness", f)]);
        }
        if let Some(s) = &opt.safe {
            req = req.query(&[("safeSearch", s)]);
        }

        let v: serde_json::Value = req.send().await?.error_for_status()?.json().await?;

        let mut out = Vec::new();
        if let Some(arr) = v.pointer("/webPages/value").and_then(|x| x.as_array()) {
            for (i, item) in arr.iter().enumerate() {
                let name = item
                    .get("name")
                    .and_then(|x| x.as_str())
                    .unwrap_or("")
                    .to_string();
                let url = item
                    .get("url")
                    .and_then(|x| x.as_str())
                    .unwrap_or("")
                    .to_string();
                let snippet = item
                    .get("snippet")
                    .and_then(|x| x.as_str())
                    .unwrap_or("")
                    .to_string();
                if !url.is_empty() {
                    out.push(SearchResult {
                        title: name,
                        url,
                        snippet,
                        provider: "bing".into(),
                        source_rank: Some(i + 1),
                    });
                }
                if out.len() >= opt.top {
                    break;
                }
            }
        }
        Ok(out)
    }

    async fn search_duckduckgo(
        &self,
        query: &str,
        opt: &SearchOptions,
    ) -> WebSearchResult<Vec<SearchResult>> {
        let url = format!(
            "https://html.duckduckgo.com/html/?q={}",
            urlencoding::encode(query)
        );
        let body = self
            .client
            .get(&url)
            .send()
            .await?
            .error_for_status()?
            .text()
            .await?;

        let mut results = Vec::new();
        for (i, cap) in LINK_RE.captures_iter(&body).enumerate() {
            let url = html_unescape(cap.get(1).map(|m| m.as_str()).unwrap_or(""));
            let title = html_unescape(cap.get(2).map(|m| m.as_str()).unwrap_or(""));

            // 스니펫은 근처 첫 매칭(경량)
            let snippet = if let Some(sn) = SNIPPET_RE.captures(&body).and_then(|c| c.get(1)) {
                html_unescape(sn.as_str())
            } else {
                String::new()
            };

            if !url.is_empty() && !title.is_empty() {
                results.push(SearchResult {
                    title,
                    url,
                    snippet,
                    provider: "duckduckgo".into(),
                    source_rank: Some(i + 1),
                });
            }
            if results.len() >= opt.top {
                break;
            }
        }
        Ok(results)
    }

    // ---------------- Cache ----------------

    fn try_cache_load(
        &self,
        query: &str,
        opt: &SearchOptions,
    ) -> WebSearchResult<Option<Vec<SearchResult>>> {
        let dir = match &self.cache_dir {
            Some(d) => d,
            None => return Ok(None),
        };
        let p = cache_file_path(dir, query);
        if !p.exists() {
            return Ok(None);
        }

        let md = fs::metadata(&p)?;
        let age = SystemTime::now()
            .duration_since(md.modified().unwrap_or(SystemTime::now()))
            .unwrap_or_default();
        if age.as_secs() > opt.cache_ttl_sec {
            return Ok(None);
        }

        let data = fs::read(&p)?;
        let vec: Vec<SearchResult> = serde_json::from_slice(&data)?;
        Ok(Some(vec))
    }
}

// ---- 얕은 HTML 파싱 (의존성 최소) ----
static LINK_RE: once_cell::sync::Lazy<regex::Regex> = once_cell::sync::Lazy::new(|| {
    regex::Regex::new(r#"<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>"#).unwrap()
});
static SNIPPET_RE: once_cell::sync::Lazy<regex::Regex> = once_cell::sync::Lazy::new(|| {
    regex::Regex::new(r#"<a[^>]*class="result__snippet"[^>]*>(.*?)</a>"#).unwrap()
});

fn html_unescape(s: &str) -> String {
    htmlescape::decode_html(s).unwrap_or_else(|_| s.to_string())
}

// ---- 캐시 유틸 ----
fn determine_cache_dir() -> WebSearchResult<Option<PathBuf>> {
    if let Ok(custom) = env::var("AI_DESKTOP_CACHE") {
        let p = PathBuf::from(custom).join("web_search");
        let _ = fs::create_dir_all(&p);
        return Ok(Some(p));
    }
    if let Ok(local) = env::var("LOCALAPPDATA") {
        let p = Path::new(&local)
            .join("ai_desktop")
            .join("cache")
            .join("web_search");
        let _ = fs::create_dir_all(&p);
        return Ok(Some(p));
    }
    Ok(None)
}
fn cache_file_path(dir: &Path, query: &str) -> PathBuf {
    let mut hasher = Sha1::new();
    hasher.update(query.as_bytes());
    let hash = hex::encode(hasher.finalize());
    dir.join(format!("{hash}.json"))
}
fn save_cache(dir: &Path, _query: &str, results: &Vec<SearchResult>) -> std::io::Result<()> {
    fs::create_dir_all(dir)?;
    let p = dir.join("last.json"); // 최근 결과도 바로 확인할 수 있게
    let mut f = fs::File::create(p)?;
    f.write_all(serde_json::to_string(results).unwrap().as_bytes())
}

// ---- 프로젝트 패턴: Default ----
impl Default for WebSearchTool {
    fn default() -> Self {
        Self::new().expect("WebSearchTool init failed")
    }
}

// ---- 기존 방식: Tool 트레이트 구현 ----
use crate::core::{Permission, Tool, ToolContext, ToolResult};
use async_trait::async_trait;

#[async_trait]
impl Tool for WebSearchTool {
    fn name(&self) -> &'static str {
        "web_search"
    }
    fn description(&self) -> &'static str {
        "Search the web (Bing/DuckDuckGo). Returns titles, snippets, and URLs."
    }
    fn required_permissions(&self) -> Permission {
        Permission(Permission::EXECUTE)
    }

    // [NEW] 스키마 정의
    fn input_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "const": "search",
                    "description": "Always use 'search'"
                },
                "q": {
                    "type": "string",
                    "description": "Search query keywords"
                },
                "top": {
                    "type": "integer",
                    "description": "Number of results (default 10)"
                }
            },
            "required": ["cmd", "q"]
        })
    }

    async fn run(&self, _ctx: &ToolContext, payload: Value) -> ToolResult {
        // ... (기존 run 구현 로직 유지) ...
        let cmd = payload.get("cmd").and_then(|x| x.as_str()).unwrap_or("");
        match cmd {
            "search" => {
                let query = payload
                    .get("q")
                    .and_then(|x| x.as_str())
                    .unwrap_or("")
                    .trim()
                    .to_string();
                if query.is_empty() {
                    return Ok(json!({ "ok": false, "error": "missing 'q'" }));
                }
                let mut opt = SearchOptions::default();
                if let Some(n) = payload.get("top").and_then(|x| x.as_u64()) {
                    opt.top = n as usize;
                }
                if let Some(s) = payload.get("market").and_then(|x| x.as_str()) {
                    opt.market = Some(s.to_string());
                }
                if let Some(s) = payload.get("freshness").and_then(|x| x.as_str()) {
                    opt.freshness = Some(s.to_string());
                }
                if let Some(s) = payload.get("safe").and_then(|x| x.as_str()) {
                    opt.safe = Some(s.to_string());
                }
                if let Some(n) = payload.get("timeout_ms").and_then(|x| x.as_u64()) {
                    opt.timeout_ms = n;
                }
                if let Some(n) = payload.get("cache_ttl_sec").and_then(|x| x.as_u64()) {
                    opt.cache_ttl_sec = n;
                }

                match self.search(&query, opt).await {
                    Ok(results) => Ok(json!({ "ok": true, "results": results })),
                    Err(e) => Ok(json!({ "ok": false, "error": e.to_string() })),
                }
            }
            _ => Ok(json!({ "ok": false, "error": "unknown command. use 'search'" })),
        }
    }
}
