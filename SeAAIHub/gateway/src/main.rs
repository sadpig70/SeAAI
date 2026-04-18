use clap::Parser;
use std::sync::Arc;
use std::time::Instant;
use tracing::info;
use tracing_subscriber::EnvFilter;

mod config;
mod error;
mod hub_client;
mod pool;
mod router;
mod server;
mod sig;
mod wire;

use config::Config;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cfg = Config::parse();

    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new(&cfg.log_level)),
        )
        .init();

    info!(
        version = %config::SERVER_VERSION,
        port = cfg.port,
        hub = %cfg.hub_addr(),
        "mme (rust) starting"
    );

    let hub = hub_client::HubClient::spawn(cfg.clone());
    let pool = pool::AgentPool::new();
    let router = router::Router {
        pool,
        hub: hub.clone(),
        shared_secret: cfg.shared_secret.as_bytes().to_vec(),
    };

    let state = Arc::new(server::BridgeState {
        router,
        started: Instant::now(),
    });

    let app = server::app(state.clone());
    let listener = tokio::net::TcpListener::bind(cfg.bind_addr()).await?;
    info!(addr = %cfg.bind_addr(), "listening");

    let shutdown = async {
        tokio::signal::ctrl_c().await.ok();
        info!("shutdown signal received");
    };

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown)
        .await?;

    hub.shutdown().await;
    info!("bye");
    Ok(())
}
