use crate::browser::types::{
    BrowserActionPlan, BrowserDialogPlan, BrowserProfileInfo, BrowserProfileListing,
    BrowserSessionRecord, BrowserSnapshotRecord, BrowserSnapshotRef, BrowserTabRecord,
    BrowserUploadPlan, RefMode, SnapshotFormat,
};
use anyhow::{Context, Result};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone)]
pub struct BrowserControlPlane {
    root: PathBuf,
}

impl BrowserControlPlane {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self { root: root.into() }
    }

    pub fn state_root(&self) -> PathBuf {
        self.root.join("state").join("browser")
    }

    pub fn sessions_dir(&self) -> PathBuf {
        self.state_root().join("sessions")
    }

    pub fn profiles_dir(&self) -> PathBuf {
        self.state_root().join("profiles")
    }

    pub fn temp_profiles_dir(&self) -> PathBuf {
        self.state_root().join("temp-profiles")
    }

    pub fn list_sessions_for_member(&self, member: &str) -> Result<Vec<BrowserSessionRecord>> {
        let mut sessions = Vec::new();
        let dir = self.sessions_dir();
        if !dir.exists() {
            return Ok(sessions);
        }

        for entry in fs::read_dir(&dir).with_context(|| format!("failed to read {}", dir.display()))? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|ext| ext.to_str()) != Some("json") {
                continue;
            }
            let content = fs::read_to_string(&path)
                .with_context(|| format!("failed to read session file {}", path.display()))?;
            let session: BrowserSessionRecord = serde_json::from_str(&content)
                .with_context(|| format!("failed to parse session file {}", path.display()))?;
            if session.member == member {
                sessions.push(session);
            }
        }

        sessions.sort_by(|a, b| a.session_id.cmp(&b.session_id));
        Ok(sessions)
    }

    pub fn list_tabs_for_member(&self, member: &str) -> Result<Vec<BrowserTabRecord>> {
        let sessions = self.list_sessions_for_member(member)?;
        Ok(sessions
            .into_iter()
            .map(|session| BrowserTabRecord {
                tab_id: session.session_id.clone(),
                session_id: session.session_id,
                url: session.url,
                title: session.title,
                active: session.status.as_deref() != Some("closed"),
                mode: session.mode,
            })
            .collect())
    }

    pub fn list_profiles_for_member(&self, member: &str) -> Result<BrowserProfileListing> {
        let persistent = self.collect_profiles(&self.profiles_dir(), member, false)?;
        let temporary = self.collect_profiles(&self.temp_profiles_dir().join(member), member, true)?;
        Ok(BrowserProfileListing {
            member: member.to_string(),
            persistent,
            temporary,
        })
    }

    pub fn make_snapshot_record(
        &self,
        session_id: Option<String>,
        tab_id: String,
        format: SnapshotFormat,
        ref_mode: RefMode,
        text: String,
        title: Option<String>,
    ) -> BrowserSnapshotRecord {
        let refs = self.extract_snapshot_refs(&text);
        let ref_count = refs.len();
        BrowserSnapshotRecord {
            snapshot_id: Self::next_snapshot_id(),
            session_id,
            tab_id,
            format,
            ref_mode,
            refs,
            ref_count,
            text,
            title,
        }
    }

    pub fn make_upload_plan(&self, upload_paths: Vec<String>) -> BrowserUploadPlan {
        let existing_paths = upload_paths
            .iter()
            .filter(|path| Path::new(path.as_str()).exists())
            .cloned()
            .collect::<Vec<_>>();
        let missing_paths = upload_paths
            .iter()
            .filter(|path| !Path::new(path.as_str()).exists())
            .cloned()
            .collect::<Vec<_>>();
        BrowserUploadPlan {
            ok: !existing_paths.is_empty() && missing_paths.is_empty(),
            execution_mode: "validated-upload-plan".to_string(),
            execution_status: if existing_paths.is_empty() { "blocked" } else { "planned" }.to_string(),
            live_execution: false,
            next_bridge: "live-browser-required".to_string(),
            existing_paths,
            missing_paths,
        }
    }

    pub fn make_dialog_plan(&self, decision: String, text: Option<String>) -> BrowserDialogPlan {
        let valid = matches!(decision.as_str(), "accept" | "dismiss");
        BrowserDialogPlan {
            ok: valid,
            decision,
            execution_mode: if valid { "decision-prepared" } else { "structured-degraded" }.to_string(),
            execution_status: if valid { "planned" } else { "blocked" }.to_string(),
            live_execution: false,
            next_bridge: "live-browser-required".to_string(),
            text,
            diagnosis: if valid { None } else { Some("invalid_dialog_decision".to_string()) },
        }
    }

    pub fn make_action_plan(
        &self,
        snapshot: &BrowserSnapshotRecord,
        action: String,
        ref_id: Option<String>,
        input_text: Option<String>,
    ) -> BrowserActionPlan {
        let requires_ref = !matches!(action.as_str(), "wait" | "evaluate");
        let resolved_ref = ref_id.as_ref().and_then(|target| {
            snapshot
                .refs
                .iter()
                .find(|item| item.ref_id == *target)
                .cloned()
        });

        if requires_ref && resolved_ref.is_none() {
            return BrowserActionPlan {
                ok: false,
                action,
                execution_mode: "structured-degraded".to_string(),
                execution_status: "blocked".to_string(),
                live_execution: false,
                next_bridge: "live-browser-required".to_string(),
                snapshot_id: Some(snapshot.snapshot_id.clone()),
                ref_id,
                resolved_ref: None,
                input_text,
                diagnosis: Some("action_ref_not_found".to_string()),
            };
        }

        let execution_mode = if requires_ref {
            "stateless-ref-validated"
        } else {
            "stateless-action-plan"
        };

        BrowserActionPlan {
            ok: true,
            action,
            execution_mode: execution_mode.to_string(),
            execution_status: "planned".to_string(),
            live_execution: false,
            next_bridge: "live-browser-required".to_string(),
            snapshot_id: Some(snapshot.snapshot_id.clone()),
            ref_id,
            resolved_ref,
            input_text,
            diagnosis: None,
        }
    }

    fn collect_profiles(&self, dir: &Path, member: &str, member_only: bool) -> Result<Vec<BrowserProfileInfo>> {
        let mut items = Vec::new();
        if !dir.exists() {
            return Ok(items);
        }

        for entry in fs::read_dir(dir).with_context(|| format!("failed to read {}", dir.display()))? {
            let entry = entry?;
            let path = entry.path();
            if !path.is_dir() {
                continue;
            }
            let name = entry.file_name().to_string_lossy().to_string();
            items.push(BrowserProfileInfo {
                name: name.clone(),
                path: path.display().to_string(),
                member_owned: member_only || name == member,
            });
        }
        items.sort_by(|a, b| a.name.cmp(&b.name));
        Ok(items)
    }

    fn extract_snapshot_refs(&self, html: &str) -> Vec<BrowserSnapshotRef> {
        let mut refs = Vec::new();
        self.collect_container_refs(html, "button", "button", &mut refs);
        self.collect_void_refs(html, "input", &mut refs);
        self.collect_container_refs(html, "a", "link", &mut refs);
        refs
    }

    fn collect_container_refs(&self, html: &str, tag: &str, role: &str, refs: &mut Vec<BrowserSnapshotRef>) {
        let open = format!("<{tag}");
        let close = format!("</{tag}>");
        let mut cursor = 0usize;
        while let Some(rel_start) = html[cursor..].find(&open) {
            let start = cursor + rel_start;
            let Some(rel_open_end) = html[start..].find('>') else { break; };
            let open_end = start + rel_open_end;
            let attrs = &html[start + open.len()..open_end];
            let content_start = open_end + 1;
            let Some(rel_close) = html[content_start..].find(&close) else { break; };
            let content_end = content_start + rel_close;
            let text = clean_text(&html[content_start..content_end]);
            let label = first_non_empty(&[
                extract_attr(attrs, "aria-label"),
                extract_attr(attrs, "title"),
                extract_attr(attrs, "name"),
                if text.is_empty() { None } else { Some(text.clone()) },
                Some(role.to_string()),
            ]);
            refs.push(BrowserSnapshotRef {
                ref_id: format!("r{}", refs.len() + 1),
                tag: Some(tag.to_string()),
                role: Some(role.to_string()),
                label,
                name: extract_attr(attrs, "name").or_else(|| extract_attr(attrs, "id")),
                r#type: extract_attr(attrs, "type"),
                text: if text.is_empty() { None } else { Some(text) },
                href: extract_attr(attrs, "href"),
            });
            cursor = content_end + close.len();
        }
    }

    fn collect_void_refs(&self, html: &str, tag: &str, refs: &mut Vec<BrowserSnapshotRef>) {
        let open = format!("<{tag}");
        let mut cursor = 0usize;
        while let Some(rel_start) = html[cursor..].find(&open) {
            let start = cursor + rel_start;
            let Some(rel_end) = html[start..].find('>') else { break; };
            let end = start + rel_end;
            let attrs = &html[start + open.len()..end];
            let input_type = extract_attr(attrs, "type").unwrap_or_else(|| "text".to_string());
            let role = if matches!(input_type.as_str(), "button" | "submit" | "reset") {
                "button"
            } else if matches!(input_type.as_str(), "checkbox" | "radio") {
                input_type.as_str()
            } else {
                "textbox"
            };
            let label = first_non_empty(&[
                extract_attr(attrs, "aria-label"),
                extract_attr(attrs, "placeholder"),
                extract_attr(attrs, "title"),
                extract_attr(attrs, "name"),
                Some(role.to_string()),
            ]);
            refs.push(BrowserSnapshotRef {
                ref_id: format!("r{}", refs.len() + 1),
                tag: Some(tag.to_string()),
                role: Some(role.to_string()),
                label,
                name: extract_attr(attrs, "name").or_else(|| extract_attr(attrs, "id")),
                r#type: Some(input_type),
                text: None,
                href: None,
            });
            cursor = end + 1;
        }
    }

    fn next_snapshot_id() -> String {
        let duration = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or(Duration::from_secs(0));
        format!("snap-{}", duration.as_millis())
    }
}

fn extract_attr(attrs: &str, name: &str) -> Option<String> {
    let needle = format!("{name}=");
    let start = attrs.find(&needle)? + needle.len();
    let mut chars = attrs[start..].chars();
    let quote = chars.next()?;
    if quote != '"' && quote != '\'' {
        return None;
    }
    let rest = &attrs[start + quote.len_utf8()..];
    let end = rest.find(quote)?;
    let value = rest[..end].trim();
    if value.is_empty() {
        None
    } else {
        Some(value.to_string())
    }
}

fn clean_text(value: &str) -> String {
    value.split_whitespace().collect::<Vec<_>>().join(" ")
}

fn first_non_empty(candidates: &[Option<String>]) -> Option<String> {
    for candidate in candidates {
        if let Some(value) = candidate {
            if !value.trim().is_empty() {
                return Some(value.trim().to_string());
            }
        }
    }
    None
}
