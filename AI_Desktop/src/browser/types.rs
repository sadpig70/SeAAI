use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum BrowserTarget {
    Host,
    Sandbox,
    Node,
    RemoteCdp,
}

impl Default for BrowserTarget {
    fn default() -> Self {
        Self::Host
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SnapshotFormat {
    Ai,
    Aria,
}

impl Default for SnapshotFormat {
    fn default() -> Self {
        Self::Aria
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum RefMode {
    Role,
    Aria,
}

impl Default for RefMode {
    fn default() -> Self {
        Self::Aria
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserSessionRecord {
    pub session_id: String,
    #[serde(default)]
    pub member: String,
    #[serde(default)]
    pub url: String,
    #[serde(default)]
    pub pid: Option<u32>,
    #[serde(default)]
    pub created_at: Option<String>,
    #[serde(default)]
    pub closed_at: Option<String>,
    #[serde(default)]
    pub status: Option<String>,
    #[serde(default)]
    pub mode: Option<String>,
    #[serde(default)]
    pub target: BrowserTarget,
    #[serde(default)]
    pub profile: Option<String>,
    #[serde(default)]
    pub title: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserTabRecord {
    pub tab_id: String,
    #[serde(default)]
    pub session_id: String,
    #[serde(default)]
    pub url: String,
    #[serde(default)]
    pub title: Option<String>,
    #[serde(default)]
    pub active: bool,
    #[serde(default)]
    pub mode: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserSnapshotRef {
    #[serde(rename = "ref")]
    pub ref_id: String,
    #[serde(default)]
    pub tag: Option<String>,
    #[serde(default)]
    pub role: Option<String>,
    #[serde(default)]
    pub label: Option<String>,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub r#type: Option<String>,
    #[serde(default)]
    pub text: Option<String>,
    #[serde(default)]
    pub href: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserSnapshotRecord {
    pub snapshot_id: String,
    #[serde(default)]
    pub session_id: Option<String>,
    #[serde(default)]
    pub tab_id: String,
    #[serde(default)]
    pub format: SnapshotFormat,
    #[serde(default)]
    pub ref_mode: RefMode,
    #[serde(default)]
    pub refs: Vec<BrowserSnapshotRef>,
    #[serde(default)]
    pub ref_count: usize,
    #[serde(default)]
    pub text: String,
    #[serde(default)]
    pub title: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserActionPlan {
    pub ok: bool,
    pub action: String,
    #[serde(default)]
    pub execution_mode: String,
    #[serde(default)]
    pub execution_status: String,
    #[serde(default)]
    pub live_execution: bool,
    #[serde(default)]
    pub next_bridge: String,
    #[serde(default)]
    pub snapshot_id: Option<String>,
    #[serde(rename = "ref", default)]
    pub ref_id: Option<String>,
    #[serde(default)]
    pub resolved_ref: Option<BrowserSnapshotRef>,
    #[serde(default)]
    pub input_text: Option<String>,
    #[serde(default)]
    pub diagnosis: Option<String>,
}


#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserUploadPlan {
    pub ok: bool,
    #[serde(default)]
    pub execution_mode: String,
    #[serde(default)]
    pub execution_status: String,
    #[serde(default)]
    pub live_execution: bool,
    #[serde(default)]
    pub next_bridge: String,
    #[serde(default)]
    pub existing_paths: Vec<String>,
    #[serde(default)]
    pub missing_paths: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserDialogPlan {
    pub ok: bool,
    #[serde(default)]
    pub decision: String,
    #[serde(default)]
    pub execution_mode: String,
    #[serde(default)]
    pub execution_status: String,
    #[serde(default)]
    pub live_execution: bool,
    #[serde(default)]
    pub next_bridge: String,
    #[serde(default)]
    pub text: Option<String>,
    #[serde(default)]
    pub diagnosis: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserProfileInfo {
    pub name: String,
    pub path: String,
    #[serde(default)]
    pub member_owned: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BrowserProfileListing {
    #[serde(default)]
    pub member: String,
    #[serde(default)]
    pub persistent: Vec<BrowserProfileInfo>,
    #[serde(default)]
    pub temporary: Vec<BrowserProfileInfo>,
}
