use clap::Parser;
use std::net::SocketAddr;

#[derive(Debug, Clone, Parser)]
#[command(name = "mme", version, about = "Micro MCP Express (Rust)")]
pub struct Config {
    #[arg(long, env = "MME_PORT", default_value_t = 9902)]
    pub port: u16,

    #[arg(long, env = "MME_HUB_HOST", default_value = "127.0.0.1")]
    pub hub_host: String,

    #[arg(long, env = "MME_HUB_PORT", default_value_t = 9900)]
    pub hub_port: u16,

    #[arg(long, env = "SEAAI_HUB_SECRET", default_value = "seaai-shared-secret")]
    pub shared_secret: String,

    #[arg(long, default_value = "info")]
    pub log_level: String,
}

pub const RECONNECT_BASE_DELAY_MS: u64 = 1_000;
pub const RECONNECT_MAX_DELAY_MS: u64 = 30_000;
pub const HEALTH_PING_INTERVAL_MS: u64 = 30_000;
#[allow(dead_code)]
pub const MAX_OFFLINE_BUFFER: usize = 500;
pub const DEDUP_CAP: usize = 10_000;
pub const MCP_PROTOCOL_VERSION: &str = "2024-11-05";
pub const SERVER_NAME: &str = "micro-mcp-express";
pub const SERVER_VERSION: &str = "1.0.0-rs";

impl Config {
    pub fn bind_addr(&self) -> SocketAddr {
        SocketAddr::from(([127, 0, 0, 1], self.port))
    }
    pub fn hub_addr(&self) -> String {
        format!("{}:{}", self.hub_host, self.hub_port)
    }
}
