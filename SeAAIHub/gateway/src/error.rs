use thiserror::Error;

#[derive(Debug, Error)]
pub enum Error {
    #[error("hub offline")]
    HubOffline,
    #[error("agent not registered: {0}")]
    NotRegistered(String),
    #[error("invalid args: {0}")]
    InvalidArgs(String),
    #[error("protocol: {0}")]
    Protocol(String),
    #[error("hub rpc error: {0}")]
    HubRpc(String),
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("json: {0}")]
    Json(#[from] serde_json::Error),
    #[error("shutdown")]
    Shutdown,
    #[error("internal: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, Error>;
