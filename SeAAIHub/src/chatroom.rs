use std::collections::{BTreeSet, HashMap, HashSet};
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{anyhow, bail, Result};
use hmac::{Hmac, Mac};
use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::protocol::{MessageTarget, PgMessageParams};

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Clone, Serialize)]
pub struct ChatMessage {
    pub id: String,
    pub from: String,
    pub to: Vec<String>,
    pub room_id: String,
    pub intent: String,
    pub body: String,
    pub ts: f64,
    pub sig: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct DeliveryResult {
    pub delivered_to: Vec<String>,
    pub room_id: String,
    pub message_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct AgentMailbox {
    pub agent_id: String,
    pub messages: Vec<ChatMessage>,
}

#[derive(Debug, Clone, Serialize)]
pub struct RoomState {
    pub room_id: String,
    pub members: Vec<String>,
    pub message_count: usize,
}

pub struct SendMessageRequest {
    pub id: Option<String>,
    pub from: String,
    pub to: MessageTarget,
    pub room_id: String,
    pub payload: PgMessageParams,
    pub sig: String,
}

pub struct ChatroomHub {
    allowed_agents: HashSet<String>,
    authenticated_agents: HashSet<String>,
    rooms: HashMap<String, BTreeSet<String>>,
    inboxes: HashMap<String, Vec<ChatMessage>>,
    room_history: HashMap<String, Vec<ChatMessage>>,
    shared_secret: String,
    mock_mode: bool,
    mock_last_inject_at: Option<u64>,
    mock_next_interval: u64,
}

impl ChatroomHub {
    pub fn new() -> Self {
        let allowed_agents = ["Aion", "ClNeo", "NAEL", "Synerion", "HubMaster"]
            .into_iter()
            .map(str::to_string)
            .collect();

        Self {
            allowed_agents,
            authenticated_agents: HashSet::new(),
            rooms: HashMap::new(),
            inboxes: HashMap::new(),
            room_history: HashMap::new(),
            shared_secret: "seaai-shared-secret".to_string(),
            mock_mode: false,
            mock_last_inject_at: None,
            mock_next_interval: 7,
        }
    }

    pub fn register_agent(&mut self, agent_id: &str, token: &str) -> Result<()> {
        self.ensure_allowed_agent(agent_id)?;

        let expected = self.build_agent_token(agent_id)?;
        if token != expected {
            bail!("invalid token for agent {}", agent_id);
        }

        self.authenticated_agents.insert(agent_id.to_string());
        self.inboxes.entry(agent_id.to_string()).or_default();
        Ok(())
    }

    pub fn join_room(&mut self, agent_id: &str, room_id: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;
        self.rooms
            .entry(room_id.to_string())
            .or_default()
            .insert(agent_id.to_string());
        Ok(())
    }

    pub fn leave_room(&mut self, agent_id: &str, room_id: &str) -> Result<()> {
        self.ensure_authenticated(agent_id)?;
        let Some(members) = self.rooms.get_mut(room_id) else {
            bail!("room {} does not exist", room_id);
        };

        members.remove(agent_id);
        if members.is_empty() {
            self.rooms.remove(room_id);
            self.room_history.remove(room_id);
        }
        Ok(())
    }

    pub fn send_message(&mut self, request: SendMessageRequest) -> Result<DeliveryResult> {
        self.ensure_authenticated(&request.from)?;
        self.ensure_room_member(&request.from, &request.room_id)?;

        let computed_sig = self.build_message_signature(&request.payload)?;
        if request.sig != computed_sig {
            bail!("invalid message signature");
        }

        let message_id = request
            .id
            .unwrap_or_else(|| format!("msg-{}-{}", request.from, self.current_timestamp()));
        let recipients = self.resolve_recipients(&request.from, &request.room_id, request.to)?;

        let message = ChatMessage {
            id: message_id.clone(),
            from: request.from,
            to: recipients.clone(),
            room_id: request.room_id.clone(),
            intent: request.payload.intent,
            body: request.payload.body,
            ts: request.payload.ts,
            sig: request.sig,
        };

        for recipient in &recipients {
            self.inboxes
                .entry(recipient.clone())
                .or_default()
                .push(message.clone());
        }

        self.room_history
            .entry(request.room_id.clone())
            .or_default()
            .push(message);

        Ok(DeliveryResult {
            delivered_to: recipients,
            room_id: request.room_id,
            message_id,
        })
    }

    pub fn list_rooms(&self) -> Vec<String> {
        self.rooms.keys().cloned().collect()
    }

    pub fn room_state(&self, room_id: &str) -> Result<RoomState> {
        let Some(members) = self.rooms.get(room_id) else {
            bail!("room {} does not exist", room_id);
        };

        let message_count = self.room_history.get(room_id).map_or(0, Vec::len);
        Ok(RoomState {
            room_id: room_id.to_string(),
            members: members.iter().cloned().collect(),
            message_count,
        })
    }

    pub fn agent_messages(&mut self, agent_id: &str) -> Result<AgentMailbox> {
        self.ensure_authenticated(agent_id)?;
        self.maybe_inject_mock_message()?;
        Ok(AgentMailbox {
            agent_id: agent_id.to_string(),
            messages: self.inboxes.get(agent_id).cloned().unwrap_or_default(),
        })
    }

    pub fn build_agent_token(&self, agent_id: &str) -> Result<String> {
        self.ensure_allowed_agent(agent_id)?;
        Ok(self.hmac_hex(agent_id.as_bytes())?)
    }

    pub fn build_message_signature(&self, payload: &PgMessageParams) -> Result<String> {
        let mut hasher = Sha256::new();
        hasher.update(payload.body.as_bytes());
        hasher.update(payload.ts.to_string().as_bytes());
        let digest = hasher.finalize();
        self.hmac_hex(digest.as_slice())
    }

    fn ensure_allowed_agent(&self, agent_id: &str) -> Result<()> {
        if !self.allowed_agents.contains(agent_id) {
            bail!("agent {} is not allowed", agent_id);
        }
        Ok(())
    }

    fn ensure_authenticated(&self, agent_id: &str) -> Result<()> {
        self.ensure_allowed_agent(agent_id)?;
        if !self.authenticated_agents.contains(agent_id) {
            bail!("agent {} is not authenticated", agent_id);
        }
        Ok(())
    }

    fn ensure_room_member(&self, agent_id: &str, room_id: &str) -> Result<()> {
        let Some(members) = self.rooms.get(room_id) else {
            bail!("room {} does not exist", room_id);
        };
        if !members.contains(agent_id) {
            bail!("agent {} is not a member of room {}", agent_id, room_id);
        }
        Ok(())
    }

    fn resolve_recipients(
        &self,
        sender: &str,
        room_id: &str,
        target: MessageTarget,
    ) -> Result<Vec<String>> {
        let members = self
            .rooms
            .get(room_id)
            .ok_or_else(|| anyhow!("room {} does not exist", room_id))?;

        let recipients = match target {
            MessageTarget::Broadcast(_) => members
                .iter()
                .filter(|member| member.as_str() != sender)
                .cloned()
                .collect::<Vec<_>>(),
            MessageTarget::Agents(list) => {
                for agent in &list {
                    if !members.contains(agent) {
                        bail!("agent {} is not in room {}", agent, room_id);
                    }
                }
                list
            }
        };

        Ok(recipients)
    }

    fn hmac_hex(&self, bytes: &[u8]) -> Result<String> {
        let mut mac = HmacSha256::new_from_slice(self.shared_secret.as_bytes())?;
        mac.update(bytes);
        let result = mac.finalize().into_bytes();
        Ok(hex::encode(result))
    }

    // ── Mock mode: 5~10초 랜덤 간격으로 접속자에게 시간 메시지 ──

    pub fn set_mock_mode(&mut self, enabled: bool) {
        self.mock_mode = enabled;
        if enabled {
            self.mock_last_inject_at = None;
            self.mock_next_interval = Self::mock_rand_interval();
        }
    }

    pub fn maybe_inject_mock_message(&mut self) -> Result<()> {
        if !self.mock_mode {
            return Ok(());
        }
        // 접속자가 없거나 방이 없으면 skip
        if self.rooms.is_empty() || self.authenticated_agents.is_empty() {
            return Ok(());
        }

        let now = self.current_timestamp();

        let last = match self.mock_last_inject_at {
            Some(t) => t,
            None => {
                self.mock_last_inject_at = Some(now);
                return Ok(());
            }
        };

        if now < last + self.mock_next_interval {
            return Ok(());
        }

        // 시간 경과 → 모든 접속자에게 mock 메시지 주입
        let ts = now as f64;
        let body = format!("MockHub // current_time={} interval={}s", now, self.mock_next_interval);
        let payload = PgMessageParams {
            intent: "chat".to_string(),
            body: body.clone(),
            ts,
        };
        let sig = self.build_message_signature(&payload)?;

        // 모든 room의 모든 멤버에게 전달
        let all_members: Vec<String> = self.rooms.values()
            .flat_map(|members| members.iter().cloned())
            .collect::<HashSet<String>>()
            .into_iter()
            .collect();

        let first_room = self.rooms.keys().next().cloned().unwrap_or_default();

        let message = ChatMessage {
            id: format!("mock-{}", now),
            from: "MockHub".to_string(),
            to: all_members.clone(),
            room_id: first_room.clone(),
            intent: "chat".to_string(),
            body,
            ts,
            sig,
        };

        for agent in &all_members {
            self.inboxes.entry(agent.clone()).or_default().push(message.clone());
        }

        self.mock_last_inject_at = Some(now);
        self.mock_next_interval = Self::mock_rand_interval();
        eprintln!("[MockHub] Injected time message to {} agent(s), next in {}s", all_members.len(), self.mock_next_interval);

        Ok(())
    }

    fn mock_rand_interval() -> u64 {
        // 5~10초 랜덤 (간단한 시간 기반 의사 난수)
        let seed = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.subsec_nanos())
            .unwrap_or(0);
        5 + (seed % 6) as u64  // 5, 6, 7, 8, 9, 10
    }

    fn current_timestamp(&self) -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|duration| duration.as_secs())
            .unwrap_or(0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn registered_hub() -> ChatroomHub {
        let mut hub = ChatroomHub::new();
        let aion = hub.build_agent_token("Aion").unwrap();
        let clneo = hub.build_agent_token("ClNeo").unwrap();
        let nael = hub.build_agent_token("NAEL").unwrap();
        hub.register_agent("Aion", &aion).unwrap();
        hub.register_agent("ClNeo", &clneo).unwrap();
        hub.register_agent("NAEL", &nael).unwrap();
        hub.join_room("Aion", "design-room").unwrap();
        hub.join_room("ClNeo", "design-room").unwrap();
        hub.join_room("NAEL", "ops-room").unwrap();
        hub
    }

    #[test]
    fn authenticates_and_broadcasts_with_room_isolation() {
        let mut hub = registered_hub();
        let payload = PgMessageParams {
            intent: "design".to_string(),
            body: "SeAAIChatroom // Room topology refinement".to_string(),
            ts: 42.0,
        };
        let sig = hub.build_message_signature(&payload).unwrap();
        let result = hub
            .send_message(SendMessageRequest {
                id: Some("msg-1".to_string()),
                from: "Aion".to_string(),
                to: MessageTarget::Broadcast("*".to_string()),
                room_id: "design-room".to_string(),
                payload,
                sig,
            })
            .unwrap();

        assert_eq!(result.delivered_to, vec!["ClNeo".to_string()]);
        assert_eq!(hub.agent_messages("ClNeo").unwrap().messages.len(), 1);
        assert_eq!(hub.agent_messages("NAEL").unwrap().messages.len(), 0);
    }

    #[test]
    fn rejects_invalid_signature() {
        let mut hub = registered_hub();
        let error = hub
            .send_message(SendMessageRequest {
                id: None,
                from: "Aion".to_string(),
                to: MessageTarget::Broadcast("*".to_string()),
                room_id: "design-room".to_string(),
                payload: PgMessageParams {
                    intent: "design".to_string(),
                    body: "tampered".to_string(),
                    ts: 7.0,
                },
                sig: "bad-signature".to_string(),
            })
            .unwrap_err();

        assert!(error.to_string().contains("invalid message signature"));
    }

    // time_broadcast tests removed — heartbeat moved to Bridge
}
